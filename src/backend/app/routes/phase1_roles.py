"""
Phase 1 Role Management Routes Blueprint

This blueprint handles all Phase 1 role-related endpoints including:
- Role identification and saving (STANDARD and CUSTOM roles)
- Role-process matrix initialization with smart-merge support
- Task-based process identification using AI/LLM
- AI-powered role suggestion from process involvement
- AI role mapping (document extraction and cluster mapping)
- Organization structure analysis
- Matrix CRUD operations (role-process and process-competency)
- Organization-specific role queries

Extracted from routes.py on 2025-12-03
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
import os
import traceback
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict

# Import models
from models import (
    db,
    User,
    Organization,
    RoleCluster,
    OrganizationRoles,
    OrganizationRoleMapping,
    IsoProcesses,
    IsoSystemLifeCycleProcesses,
    Competency,
    RoleProcessMatrix,
    ProcessCompetencyMatrix,
    RoleCompetencyMatrix,
    UnknownRoleProcessMatrix,
    UnknownRoleCompetencyMatrix,
    PhaseQuestionnaireResponse
)

# Import AI services
from app.services.role_cluster_mapping_service import RoleClusterMappingService
from app.services.custom_role_matrix_generator import CustomRoleMatrixGenerator

# Import helper functions
from app.most_similar_role import find_most_similar_role_cluster

# Create blueprint
phase1_roles_bp = Blueprint('phase1_roles', __name__)

# Initialize AI services
role_mapping_service = RoleClusterMappingService()
custom_role_matrix_generator = CustomRoleMatrixGenerator()


# =============================================================================
# ROLE IDENTIFICATION AND MANAGEMENT
# =============================================================================

@phase1_roles_bp.route('/phase1/roles/<int:org_id>/latest', methods=['GET'])
def get_latest_roles(org_id):
    """
    Get latest role identification for an organization.
    Returns roles directly from organization_roles table with database IDs.

    Refactored: 2025-10-30 - Now uses ORM instead of raw SQL
    """
    try:
        # Verify organization exists
        org = Organization.query.get(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        # Fetch roles using ORM (with eager loading of standard_cluster relationship)
        roles = OrganizationRoles.query.filter_by(organization_id=org_id).order_by(OrganizationRoles.id).all()

        if not roles:
            return jsonify({
                'success': True,
                'exists': False,
                'data': None,
                'count': 0
            }), 200

        # Use built-in to_dict() method and add has_competencies flag
        roles_list = []
        for role in roles:
            role_dict = role.to_dict()

            # Check if role has any non-zero competencies
            # Query role_competency_matrix for this role
            has_competencies = db.session.query(RoleCompetencyMatrix).filter(
                RoleCompetencyMatrix.organization_id == org_id,
                RoleCompetencyMatrix.role_cluster_id == role.id,
                RoleCompetencyMatrix.role_competency_value > 0
            ).count() > 0

            role_dict['has_competencies'] = has_competencies
            roles_list.append(role_dict)

        return jsonify({
            'success': True,
            'exists': True,
            'data': roles_list,
            'count': len(roles_list),
            'organizationName': org.organization_name
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting roles: {str(e)}")
        return jsonify({'error': 'Failed to get roles'}), 500


@phase1_roles_bp.route('/phase1/roles/save', methods=['POST'])
def save_roles():
    """
    Save identified SE roles for an organization to organization_roles table.
    Each role can be:
    - STANDARD: Maps to one of 14 standard role clusters
    - CUSTOM: User-defined role not mapped to any cluster

    Smart-merge feature (2025-10-30):
    - Detects pathway changes (Task 1 retake affecting seProcesses threshold)
    - Preserves matrix data for unchanged roles
    - Only resets matrix when pathway changes or user explicitly changes roles

    Refactored: 2025-10-30 - Now uses ORM instead of raw SQL
    """
    try:
        from flask_jwt_extended import verify_jwt_in_request

        data = request.get_json()

        org_id = data.get('org_id')
        maturity_id = data.get('maturity_id')  # NEW: needed to detect pathway changes
        roles = data.get('roles', [])
        identification_method = data.get('identification_method', 'STANDARD')

        if not org_id:
            return jsonify({'error': 'org_id is required'}), 400

        # Get user ID from JWT if available
        user_id = 1  # Default fallback
        try:
            verify_jwt_in_request(optional=True)
            jwt_user_id = get_jwt_identity()
            if jwt_user_id:
                user_id = int(jwt_user_id) if isinstance(jwt_user_id, str) else jwt_user_id
        except Exception:
            pass  # Use default user_id

        # SMART-MERGE STEP 1: Detect pathway changes (Task 1 retake)
        MATURITY_THRESHOLD = 3  # "Defined and Established"
        pathway_changed = False
        old_pathway = None
        new_pathway = None

        if maturity_id:
            # Get the new maturity data
            new_maturity = PhaseQuestionnaireResponse.query.filter_by(
                id=maturity_id,
                organization_id=org_id,
                questionnaire_type='maturity'
            ).first()

            if new_maturity:
                new_results = new_maturity.get_computed_scores()
                new_se_processes = new_results.get('strategyInputs', {}).get('seProcessesValue', 0)
                new_pathway = 'STANDARD' if new_se_processes >= MATURITY_THRESHOLD else 'TASK_BASED'

                # Get the previous maturity (if exists)
                previous_maturity = PhaseQuestionnaireResponse.query.filter(
                    PhaseQuestionnaireResponse.organization_id == org_id,
                    PhaseQuestionnaireResponse.questionnaire_type == 'maturity',
                    PhaseQuestionnaireResponse.id != maturity_id
                ).order_by(PhaseQuestionnaireResponse.completed_at.desc()).first()

                if previous_maturity:
                    old_results = previous_maturity.get_computed_scores()
                    old_se_processes = old_results.get('strategyInputs', {}).get('seProcessesValue', 0)
                    old_pathway = 'STANDARD' if old_se_processes >= MATURITY_THRESHOLD else 'TASK_BASED'

                    # Pathway changed if crossing the threshold
                    if old_pathway != new_pathway:
                        pathway_changed = True
                        current_app.logger.warning(
                            f"[ROLE SAVE] Pathway changed for org {org_id}: {old_pathway} -> {new_pathway} "
                            f"(seProcesses: {old_se_processes} -> {new_se_processes})"
                        )

        # SMART-MERGE STEP 2: Check if organization already has roles using ORM
        existing_roles_objs = OrganizationRoles.query.filter_by(organization_id=org_id).all()

        # Convert to simple dicts for comparison
        existing_roles = [{
            'id': role.id,
            'name': role.role_name,
            'cluster': role.standard_role_cluster_id,
            'method': role.identification_method
        } for role in existing_roles_objs]

        # SMART-MERGE STEP 3: Compare submitted roles with existing roles to detect changes
        submitted_role_signatures = set()
        submitted_role_map = {}  # sig -> role data
        for role in roles:
            sig = f"{role.get('orgRoleName')}|{role.get('standardRoleId')}|{role.get('identificationMethod', 'STANDARD')}"
            submitted_role_signatures.add(sig)
            submitted_role_map[sig] = role

        existing_role_signatures = set()
        existing_role_map = {}  # sig -> role id
        for role in existing_roles:
            sig = f"{role['name']}|{role['cluster']}|{role['method']}"
            existing_role_signatures.add(sig)
            existing_role_map[sig] = role['id']

        is_new = len(existing_roles) == 0
        roles_changed = submitted_role_signatures != existing_role_signatures if not is_new else True

        # SMART-MERGE STEP 4: Build detailed change info
        unchanged_roles = submitted_role_signatures & existing_role_signatures
        added_roles = submitted_role_signatures - existing_role_signatures
        removed_roles = existing_role_signatures - submitted_role_signatures

        current_app.logger.info(
            f"[ROLE SAVE] Change analysis for org {org_id}: "
            f"unchanged={len(unchanged_roles)}, added={len(added_roles)}, removed={len(removed_roles)}, "
            f"pathway_changed={pathway_changed}"
        )

        if not is_new and not roles_changed:
            # CASE 1: Roles haven't changed - return existing roles (preserves matrix)
            current_app.logger.info(f"[ROLE SAVE] No role changes detected for org {org_id} - preserving matrix")

            # Use to_dict() for consistent output
            saved_roles = [role.to_dict() for role in existing_roles_objs]

            return jsonify({
                'success': True,
                'message': f'Using existing {len(saved_roles)} roles (no changes detected)',
                'roles': saved_roles,
                'count': len(saved_roles),
                'is_update': True,
                'roles_changed': False,
                'pathway_changed': False,
                'smart_merge_enabled': False
            }), 200

        elif not is_new and roles_changed:
            # CASE 2: Roles have changed
            if pathway_changed:
                # CASE 2a: Pathway changed (Task 1 retake) - FULL RESET
                current_app.logger.warning(
                    f"[ROLE SAVE] Pathway changed ({old_pathway} -> {new_pathway}) - FULL MATRIX RESET"
                )
                # Delete old roles using ORM (CASCADE will delete matrix)
                OrganizationRoles.query.filter_by(organization_id=org_id).delete()
                current_app.logger.warning(f"[ROLE SAVE] Deleted old roles and matrix (pathway change)")
                is_updating = True
                smart_merge_enabled = False

            else:
                # CASE 2b: Only roles changed (no pathway change) - SMART MERGE
                current_app.logger.info(
                    f"[ROLE SAVE] Roles changed but pathway stable - SMART MERGE: "
                    f"keep {len(unchanged_roles)}, add {len(added_roles)}, remove {len(removed_roles)}"
                )

                # Smart merge: Only delete removed roles
                if removed_roles:
                    removed_role_ids = [existing_role_map[sig] for sig in removed_roles]
                    OrganizationRoles.query.filter(
                        OrganizationRoles.organization_id == org_id,
                        OrganizationRoles.id.in_(removed_role_ids)
                    ).delete(synchronize_session=False)
                    current_app.logger.info(f"[ROLE SAVE] Deleted {len(removed_roles)} removed roles (matrix CASCADE)")

                is_updating = True
                smart_merge_enabled = True

        else:
            # CASE 3: New organization - first time setup
            current_app.logger.info(f"[ROLE SAVE] Creating new roles for org {org_id} (matrix will be initialized)")
            is_updating = False
            smart_merge_enabled = False

        # Insert/update roles into organization_roles table using ORM
        saved_roles = []
        roles_to_add = []  # Track which roles we're adding (for matrix initialization)

        # NOTE: Training Program Cluster assignment is done in Phase 2 (Learning Objectives)
        # based on competency gaps, NOT here in Phase 1 Task 2.

        for role in roles:
            # Extract role data
            role_name = role.get('orgRoleName')
            role_description = role.get('standard_role_description')
            standard_role_cluster_id = role.get('standardRoleId')  # NULL for custom roles
            role_identification_method = role.get('identificationMethod', 'STANDARD')
            participating = role.get('participatingInTraining', True)

            if not role_name:
                current_app.logger.warning(f"[ROLE SAVE] Skipping role with empty name for org {org_id}")
                continue

            # Build signature for this role
            sig = f"{role_name}|{standard_role_cluster_id}|{role_identification_method}"

            # SMART MERGE: Check if this role already exists (unchanged)
            if smart_merge_enabled and sig in unchanged_roles:
                # This role hasn't changed - reuse existing ID and preserve its matrix data
                existing_id = existing_role_map[sig]
                existing_obj = OrganizationRoles.query.get(existing_id)
                saved_roles.append(existing_obj.to_dict())
                current_app.logger.info(
                    f"[ROLE SAVE] Keeping unchanged role '{role_name}' (ID: {existing_id}) - matrix preserved"
                )
            else:
                # This is a new role (or full reset) - create it
                # NOTE: training_program_cluster_id is assigned in Phase 2, not here
                new_role = OrganizationRoles(
                    organization_id=org_id,
                    role_name=role_name,
                    role_description=role_description,
                    standard_role_cluster_id=standard_role_cluster_id,
                    identification_method=role_identification_method,
                    participating_in_training=participating
                )
                db.session.add(new_role)
                db.session.flush()  # Get the ID without committing

                # Use to_dict() for consistent output
                saved_role_dict = new_role.to_dict()
                saved_roles.append(saved_role_dict)
                roles_to_add.append(saved_role_dict)  # Track for matrix initialization

                current_app.logger.info(
                    f"[ROLE SAVE] {'Added' if smart_merge_enabled else 'Created'} role '{role_name}' (ID: {new_role.id}) "
                    f"for org {org_id} (SE cluster: {standard_role_cluster_id})"
                )

        # Also save to PhaseQuestionnaireResponse for backward compatibility
        role_data = PhaseQuestionnaireResponse(
            organization_id=org_id,
            user_id=user_id,
            questionnaire_type='roles',
            phase=1
        )
        role_data.set_responses({
            'roles': saved_roles,
            'identification_method': identification_method
        })
        db.session.add(role_data)

        db.session.commit()

        # Build response message
        if smart_merge_enabled:
            message = (
                f"Smart merge: preserved {len(unchanged_roles)}, "
                f"added {len(added_roles)}, removed {len(removed_roles)} roles"
            )
        elif pathway_changed:
            message = f"Pathway changed - rebuilt {len(saved_roles)} roles (matrix reset)"
        else:
            message = f'{"Updated" if is_updating else "Created"} {len(saved_roles)} roles successfully'

        return jsonify({
            'success': True,
            'id': role_data.id,
            'message': message,
            'roles': saved_roles,
            'count': len(saved_roles),
            'is_update': is_updating,
            'roles_changed': roles_changed,
            'pathway_changed': pathway_changed,
            'smart_merge_enabled': smart_merge_enabled,
            'roles_to_add': roles_to_add,  # Only new roles that need matrix initialization
            'change_summary': {
                'unchanged': len(unchanged_roles),
                'added': len(added_roles),
                'removed': len(removed_roles)
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ROLE SAVE ERROR] {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to save roles: {str(e)}'}), 500


@phase1_roles_bp.route('/phase1/roles/initialize-matrix', methods=['POST'])
def initialize_role_process_matrix():
    """
    Initialize role-process matrix for newly saved roles.

    For STANDARD roles (mapped to clusters):
        - Copy 30 process values from organization 1's reference matrix

    For CUSTOM roles (not mapped to clusters):
        - Initialize all 30 processes with value 0 (user must define)

    Smart-merge feature (2025-10-30):
        - If smart_merge=True: Only initialize matrix for new roles (preserves existing)
        - If smart_merge=False: Full reset (delete all and rebuild)

    This endpoint should be called after roles are saved to organization_roles.

    Refactored: 2025-10-30 - Now uses ORM instead of raw SQL
    """
    try:
        data = request.get_json()
        org_id = data.get('organization_id')
        roles = data.get('roles', [])  # Roles with database IDs
        smart_merge = data.get('smart_merge', False)  # NEW: smart merge flag

        if not org_id:
            return jsonify({'error': 'organization_id is required'}), 400

        if not roles:
            return jsonify({'error': 'roles array is required'}), 400

        # Smart merge: Only delete matrix for removed roles (already done by CASCADE)
        # Full reset: Delete all matrix entries
        if not smart_merge:
            # Full reset - delete existing matrix entries for this organization using ORM
            RoleProcessMatrix.query.filter_by(organization_id=org_id).delete()
            current_app.logger.info(f"[MATRIX INIT] Full reset - deleted existing matrix for org {org_id}")
        else:
            current_app.logger.info(f"[MATRIX INIT] Smart merge - preserving matrix for unchanged roles")

        # Get all process IDs using ORM
        all_processes = IsoProcesses.query.order_by(IsoProcesses.id).all()
        all_process_ids = [p.id for p in all_processes]

        if len(all_process_ids) != 30:
            current_app.logger.warning(f"[MATRIX INIT] Expected 30 processes, found {len(all_process_ids)}")

        entries_created = 0
        roles_skipped = 0

        for role in roles:
            role_id = role.get('id')
            role_name = role.get('orgRoleName')
            standard_cluster_id = role.get('standardRoleId')
            identification_method = role.get('identificationMethod', 'STANDARD')

            if not role_id:
                current_app.logger.warning(f"[MATRIX INIT] Skipping role without ID: {role_name}")
                continue

            # SMART MERGE: Skip roles that already have matrix data (unchanged roles)
            if smart_merge:
                existing_matrix_count = RoleProcessMatrix.query.filter_by(
                    organization_id=org_id,
                    role_cluster_id=role_id
                ).count()

                if existing_matrix_count > 0:
                    roles_skipped += 1
                    current_app.logger.info(
                        f"[MATRIX INIT] Skipping role '{role_name}' (ID: {role_id}) - "
                        f"matrix already exists ({existing_matrix_count} entries)"
                    )
                    continue

            if identification_method == 'STANDARD' and standard_cluster_id:
                # Find reference role in organization 1 (template org) with same cluster ID
                # NOTE: Org 1 is the template organization with all 14 standard roles and baseline matrix
                reference_role = OrganizationRoles.query.filter_by(
                    organization_id=1,
                    standard_role_cluster_id=standard_cluster_id
                ).first()

                if reference_role:
                    # Get reference matrix entries using ORM
                    reference_entries = RoleProcessMatrix.query.filter_by(
                        organization_id=1,
                        role_cluster_id=reference_role.id
                    ).all()

                    reference_values = {entry.iso_process_id: entry.role_process_value for entry in reference_entries}
                else:
                    current_app.logger.warning(
                        f"[MATRIX INIT] No reference role found for cluster {standard_cluster_id}, using zeros"
                    )
                    reference_values = {pid: 0 for pid in all_process_ids}

                # Insert matrix entries for this role using ORM
                for process_id in all_process_ids:
                    value = reference_values.get(process_id, 0)
                    new_entry = RoleProcessMatrix(
                        organization_id=org_id,
                        role_cluster_id=role_id,
                        iso_process_id=process_id,
                        role_process_value=value
                    )
                    db.session.add(new_entry)
                    entries_created += 1

                current_app.logger.info(
                    f"[MATRIX INIT] Copied {len(reference_values)} values for STANDARD role "
                    f"'{role_name}' (cluster {standard_cluster_id})"
                )

            elif identification_method == 'CUSTOM':
                # Use AI to generate intelligent matrix values for custom roles
                current_app.logger.info(f"[MATRIX INIT] Generating AI-powered matrix for CUSTOM role '{role_name}'")

                try:
                    # Prepare process list for AI
                    processes_for_ai = [{'id': p.id, 'name': p.name, 'description': p.description or ''} for p in all_processes]

                    # Get role description from the role object
                    role_description = role.get('standard_role_description', '') or role.get('description', '')

                    # Get existing matrix context (to make AI-generation context-aware)
                    existing_matrix_entries = RoleProcessMatrix.query.filter_by(organization_id=org_id).all()
                    existing_matrix = {}
                    for entry in existing_matrix_entries:
                        if entry.iso_process_id not in existing_matrix:
                            existing_matrix[entry.iso_process_id] = {}
                        existing_matrix[entry.iso_process_id][entry.role_cluster_id] = entry.role_process_value

                    # Get existing roles for context
                    existing_roles_objs = OrganizationRoles.query.filter_by(organization_id=org_id).all()
                    existing_roles = []
                    for r in existing_roles_objs:
                        existing_roles.append({
                            'id': r.id,
                            'orgRoleName': r.role_name,
                            'standardRoleName': r.standard_cluster.role_cluster_name if r.standard_cluster else None
                        })

                    # Call AI to generate matrix
                    ai_result = custom_role_matrix_generator.generate_matrix_for_custom_role(
                        role_name=role_name,
                        role_description=role_description,
                        processes=processes_for_ai,
                        existing_matrix=existing_matrix if existing_matrix else None,
                        existing_roles=existing_roles if existing_roles else None
                    )

                    if ai_result['success']:
                        ai_matrix = ai_result['matrix']
                        current_app.logger.info(f"[MATRIX INIT] AI generated matrix for '{role_name}': {ai_result.get('reasoning', '')}")

                        # Insert AI-generated values
                        for process_id in all_process_ids:
                            value = ai_matrix.get(process_id, 0)
                            new_entry = RoleProcessMatrix(
                                organization_id=org_id,
                                role_cluster_id=role_id,
                                iso_process_id=process_id,
                                role_process_value=value
                            )
                            db.session.add(new_entry)
                            entries_created += 1

                        current_app.logger.info(f"[MATRIX INIT] AI-generated {len(all_process_ids)} values for CUSTOM role '{role_name}'")
                    else:
                        # Fallback to zeros if AI fails
                        current_app.logger.warning(f"[MATRIX INIT] AI generation failed for '{role_name}', using zeros: {ai_result.get('error', 'Unknown error')}")
                        for process_id in all_process_ids:
                            new_entry = RoleProcessMatrix(
                                organization_id=org_id,
                                role_cluster_id=role_id,
                                iso_process_id=process_id,
                                role_process_value=0
                            )
                            db.session.add(new_entry)
                            entries_created += 1

                except Exception as ai_error:
                    # Fallback to zeros if AI generation fails
                    current_app.logger.error(f"[MATRIX INIT] AI generation error for '{role_name}': {str(ai_error)}")
                    current_app.logger.error(traceback.format_exc())
                    current_app.logger.info(f"[MATRIX INIT] Falling back to zeros for CUSTOM role '{role_name}'")

                    for process_id in all_process_ids:
                        new_entry = RoleProcessMatrix(
                            organization_id=org_id,
                            role_cluster_id=role_id,
                            iso_process_id=process_id,
                            role_process_value=0
                        )
                        db.session.add(new_entry)
                        entries_created += 1
            else:
                current_app.logger.warning(
                    f"[MATRIX INIT] Unknown identification method '{identification_method}' for role '{role_name}'"
                )

        db.session.commit()

        # CRITICAL: Calculate role-competency matrix from role-process × process-competency
        # This is required for Phase 2 competency assessment to work!
        try:
            db.session.execute(
                text('CALL update_role_competency_matrix(:org_id);'),
                {'org_id': org_id}
            )
            db.session.commit()
            current_app.logger.info(f"[MATRIX INIT] Calculated role-competency matrix for org {org_id}")
        except Exception as calc_error:
            current_app.logger.error(f"[MATRIX INIT] Failed to calculate role-competency matrix: {calc_error}")
            # Don't fail the whole operation, but log the error
            current_app.logger.error(traceback.format_exc())

        # Build response message
        if smart_merge:
            message = f'Smart merge: initialized matrix for {len(roles) - roles_skipped} new roles, preserved {roles_skipped} unchanged roles'
        else:
            message = f'Initialized role-process matrix for {len(roles)} roles'

        return jsonify({
            'success': True,
            'message': message,
            'entries_created': entries_created,
            'roles_processed': len(roles),
            'roles_skipped': roles_skipped,
            'smart_merge': smart_merge,
            'processes_per_role': len(all_process_ids)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[MATRIX INIT ERROR] {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to initialize matrix: {str(e)}'}), 500


# =============================================================================
# TASK-BASED ROLE IDENTIFICATION (AI/LLM)
# =============================================================================

@phase1_roles_bp.route('/findProcesses', methods=['POST'])
def find_processes():
    """
    Map user tasks to ISO/IEC 15288 SE processes using AI
    Used in Phase 1 task-based role identification pathway
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input provided"}), 400

        # Extract required fields
        username = data.get('username')
        organization_id = data.get('organizationId')
        tasks = data.get('tasks', {})

        if not username or not organization_id:
            return jsonify({"error": "Username or Organization ID missing"}), 400

        # Extract task categories with defaults
        tasks_responsibilities = {
            "responsible_for": tasks.get("responsible_for", []),
            "supporting": tasks.get("supporting", []),
            "designing": tasks.get("designing", [])
        }

        print(f"[findProcesses] Processing tasks for user: {username}, org: {organization_id}")
        print(f"[findProcesses] Tasks: {tasks_responsibilities}")

        # Try to use LLM pipeline if available
        llm_success = False
        try:
            from app.services.llm_pipeline import llm_process_identification_pipeline
            pipeline = llm_process_identification_pipeline.create_pipeline()

            result = pipeline(tasks_responsibilities)

            print(f"[findProcesses] DEBUG: Pipeline returned result: {result}")
            print(f"[findProcesses] DEBUG: Result type: {type(result)}")
            print(f"[findProcesses] DEBUG: Result status: {result.get('status') if isinstance(result, dict) else 'NOT A DICT'}")

            # Handle invalid tasks case
            if result.get("status") == "invalid_tasks":
                return jsonify({
                    "status": "invalid_tasks",
                    "message": result.get("message", "Tasks are invalid or empty")
                }), 400

            # Handle success case
            elif result.get("status") == "success":
                print("[findProcesses] ============ LLM SUCCESS BLOCK ENTERED ============")
                # Extract process involvement from LLM result
                llm_result = result.get("result")
                processes_list = llm_result.processes if hasattr(llm_result, 'processes') else []

                # Format response for frontend
                processes = [
                    {
                        "process_name": process.process_name,
                        "involvement": process.involvement
                    }
                    for process in processes_list
                ]

                print(f"[findProcesses] Formatted {len(processes)} processes for response")
                llm_success = True

                # Extract LLM role suggestion if available
                llm_role_suggestion = result.get("llm_role_suggestion", None)

                # DERIK'S APPROACH: Store in UnknownRoleProcessMatrix for competency calculation
                try:
                    print(f"[findProcesses] Starting DB storage for username: {username}, org: {organization_id}")

                    # Fetch ALL ISO Processes from database
                    iso_processes = IsoProcesses.query.with_entities(IsoProcesses.id, IsoProcesses.name).all()
                    print(f"[findProcesses] Fetched {len(iso_processes)} ISO processes from DB")
                    iso_process_map = {
                        process.name.strip().lower(): process.id for process in iso_processes
                    }

                    # Create process involvement map from LLM result
                    # Strip " process" suffix from LLM output to match database format
                    llm_process_map = {}
                    for process in processes:
                        name = process.get('process_name', '').strip().lower()
                        # Remove " process" suffix if present
                        if name.endswith(' process'):
                            name = name[:-8]  # Remove last 8 characters (" process")
                        llm_process_map[name] = process.get('involvement', 'Not performing')

                    # Delete existing entries for this user to avoid duplicates
                    UnknownRoleProcessMatrix.query.filter_by(
                        user_name=username,
                        organization_id=organization_id
                    ).delete()

                    # Prepare rows to insert (one row per ISO process)
                    rows_to_insert = []
                    for process in iso_processes:
                        process_name = process.name.strip().lower()
                        iso_process_id = process.id

                        # Determine involvement from LLM output
                        involvement = llm_process_map.get(process_name, "Not performing")

                        # Map involvement to numeric value
                        # CRITICAL: These values multiply with process_competency_value (0,1,2)
                        # Valid results must match stored procedure CASE: {0,1,2,3,4,6}
                        # Designing(3) * Understand(2) = 6 -> beherrschen (master level)
                        involvement_values = {
                            "Responsible": 2,
                            "Supporting": 1,
                            "Designing": 3,  # Must be 3 to match Derik's implementation
                            "Not performing": 0
                        }
                        role_process_value = involvement_values.get(involvement, 0)

                        # Add row to insert
                        rows_to_insert.append(UnknownRoleProcessMatrix(
                            user_name=username,
                            iso_process_id=iso_process_id,
                            role_process_value=role_process_value,
                            organization_id=organization_id
                        ))

                    # Bulk insert
                    if rows_to_insert:
                        print(f"[findProcesses] Inserting {len(rows_to_insert)} process rows")
                        db.session.bulk_save_objects(rows_to_insert)
                        db.session.commit()
                        print(f"[findProcesses] Successfully inserted process data")
                    else:
                        print(f"[findProcesses] WARNING: No rows to insert!")

                    # Call stored procedure to calculate competency requirements from process involvement
                    try:
                        print(f"[findProcesses] Calling stored procedure update_unknown_role_competency_values")
                        db.session.execute(
                            text("CALL update_unknown_role_competency_values(:username, :organization_id);"),
                            {"username": username, "organization_id": organization_id}
                        )
                        db.session.commit()
                        print(f"[findProcesses] Stored procedure completed successfully")
                    except Exception as proc_error:
                        print(f"[findProcesses] ERROR in stored procedure: {str(proc_error)}")
                        print(traceback.format_exc())
                        db.session.rollback()
                        # Continue anyway - competency calculation can be done later

                except Exception as db_error:
                    print(f"[findProcesses] ERROR in DB operations: {str(db_error)}")
                    print(traceback.format_exc())
                    db.session.rollback()
                    # Continue anyway - return processes to frontend

                response_data = {
                    "status": "success",
                    "processes": processes
                }

                # Add LLM role suggestion if available
                if llm_role_suggestion:
                    response_data["llm_role_suggestion"] = llm_role_suggestion

                print("=" * 80)
                print("[SUCCESS] LLM pipeline used successfully for process identification")
                print(f"[SUCCESS] Identified {len(processes)} processes using AI-based analysis")
                print("=" * 80)
                return jsonify(response_data), 200

        except ImportError as import_err:
            print("=" * 80)
            print(f"[ERROR] LLM pipeline import failed: {str(import_err)}")
            print("[FALLBACK] Using keyword matching instead")
            print("=" * 80)
        except Exception as llm_err:
            print("=" * 80)
            print(f"[ERROR] LLM pipeline execution failed: {str(llm_err)}")
            print("[FALLBACK] Using keyword matching instead")
            print(traceback.format_exc())
            print("=" * 80)

        # Fallback: Simple keyword-based process identification
        if not llm_success:
            print("=" * 80)
            print("[WARNING] FALLBACK MODE ACTIVE: Using keyword-based process identification")
            print("[INFO] This is a simplified fallback mechanism with limited accuracy")
            print("[INFO] For better results, ensure LLM pipeline is properly configured")
            print("=" * 80)
            processes = []
            combined_tasks = ' '.join(
                tasks_responsibilities.get("responsible_for", []) +
                tasks_responsibilities.get("supporting", []) +
                tasks_responsibilities.get("designing", [])
            ).lower()

            # Map keywords to ISO 15288 processes
            process_keywords = {
                'Business or Mission Analysis': ['business', 'mission', 'strategy', 'goals', 'objectives'],
                'Stakeholder Needs and Requirements Definition': ['stakeholder', 'needs', 'requirements', 'gather', 'elicit'],
                'System Requirements Definition': ['system requirements', 'specification', 'define requirements'],
                'System Architecture Definition': ['architecture', 'design', 'structure', 'components', 'interfaces'],
                'Implementation': ['implement', 'code', 'develop', 'build', 'program'],
                'Integration': ['integrate', 'combine', 'merge', 'connect', 'assemble'],
                'Verification': ['verify', 'test', 'check', 'validate', 'inspect'],
                'Transition': ['deploy', 'release', 'transition', 'deliver', 'install'],
                'Validation': ['validate', 'acceptance', 'user testing', 'customer'],
                'Operation': ['operate', 'run', 'maintain', 'monitor', 'support'],
                'Maintenance': ['maintain', 'fix', 'update', 'patch', 'service'],
                'Disposal': ['dispose', 'retire', 'decommission', 'remove', 'shutdown']
            }

            for process_name, keywords in process_keywords.items():
                if any(keyword in combined_tasks for keyword in keywords):
                    # Determine involvement based on task category
                    if any(keyword in ' '.join(tasks_responsibilities.get("designing", [])).lower() for keyword in keywords):
                        involvement = "Designing"
                    elif any(keyword in ' '.join(tasks_responsibilities.get("responsible_for", [])).lower() for keyword in keywords):
                        involvement = "Responsible"
                    else:
                        involvement = "Supporting"

                    processes.append({
                        "process_name": process_name,
                        "involvement": involvement
                    })

            # Default processes if none found
            if not processes:
                processes = [
                    {"process_name": "System Architecture Definition", "involvement": "Responsible"},
                    {"process_name": "System Requirements Definition", "involvement": "Responsible"},
                    {"process_name": "Implementation", "involvement": "Responsible"}
                ]

            print(f"[findProcesses] Fallback identified {len(processes)} processes")

            # STORE FALLBACK RESULTS TO DATABASE (same as LLM path)
            try:
                print(f"[findProcesses] [FALLBACK] Starting DB storage for username: {username}, org: {organization_id}")

                # Fetch ALL ISO Processes from database
                iso_processes = IsoProcesses.query.with_entities(IsoProcesses.id, IsoProcesses.name).all()
                print(f"[findProcesses] [FALLBACK] Fetched {len(iso_processes)} ISO processes from DB")
                iso_process_map = {
                    process.name.strip().lower(): process.id for process in iso_processes
                }

                # Create process involvement map from fallback result
                fallback_process_map = {}
                for process in processes:
                    name = process.get('process_name', '').strip().lower()
                    # Remove " process" suffix if present
                    if name.endswith(' process'):
                        name = name[:-8]
                    fallback_process_map[name] = process.get('involvement', 'Not performing')

                # Delete existing entries for this user to avoid duplicates
                UnknownRoleProcessMatrix.query.filter_by(
                    user_name=username,
                    organization_id=organization_id
                ).delete()

                # Prepare rows to insert (one row per ISO process)
                rows_to_insert = []
                for process in iso_processes:
                    process_name = process.name.strip().lower()
                    iso_process_id = process.id

                    # Determine involvement from fallback output
                    involvement = fallback_process_map.get(process_name, "Not performing")

                    # Map involvement to numeric value
                    involvement_values = {
                        "Responsible": 2,
                        "Supporting": 1,
                        "Designing": 3,  # Must be 3 to match Derik's implementation
                        "Not performing": 0
                    }
                    role_process_value = involvement_values.get(involvement, 0)

                    # Add row to insert
                    rows_to_insert.append(UnknownRoleProcessMatrix(
                        user_name=username,
                        iso_process_id=iso_process_id,
                        role_process_value=role_process_value,
                        organization_id=organization_id
                    ))

                # Bulk insert
                if rows_to_insert:
                    print(f"[findProcesses] [FALLBACK] Inserting {len(rows_to_insert)} process rows")
                    db.session.bulk_save_objects(rows_to_insert)
                    db.session.commit()
                    print(f"[findProcesses] [FALLBACK] Successfully inserted process data")

                # Call stored procedure to calculate competency requirements
                try:
                    print(f"[findProcesses] [FALLBACK] Calling stored procedure update_unknown_role_competency_values")
                    db.session.execute(
                        text("CALL update_unknown_role_competency_values(:username, :organization_id);"),
                        {"username": username, "organization_id": organization_id}
                    )
                    db.session.commit()
                    print(f"[findProcesses] [FALLBACK] Stored procedure completed successfully")
                except Exception as proc_error:
                    print(f"[findProcesses] [FALLBACK] ERROR in stored procedure: {str(proc_error)}")
                    print(traceback.format_exc())
                    db.session.rollback()

            except Exception as db_error:
                print(f"[findProcesses] [FALLBACK] ERROR in DB operations: {str(db_error)}")
                print(traceback.format_exc())
                db.session.rollback()

            return jsonify({
                "status": "success",
                "processes": processes,
                "fallback": True
            }), 200

    except Exception as e:
        print(f"[findProcesses] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@phase1_roles_bp.route('/phase1/roles/suggest-from-processes', methods=['POST'])
def suggest_role_from_processes():
    """
    DERIK'S SIMPLE APPROACH: Pure competency-based distance matching
    - Uses Euclidean distance between user and role competency vectors
    - Returns role(s) with minimum distance
    - Confidence based on distance separation
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No input provided'}), 400

        username = data.get('username')
        organization_id = data.get('organizationId', 11)

        if not username:
            return jsonify({'error': 'Username required'}), 400

        print(f"[suggest-role-simple] Analyzing user: {username} (org: {organization_id})")

        # ====================
        # STEP 1: Get user's competency requirements
        # ====================
        competencies = UnknownRoleCompetencyMatrix.query.filter_by(
            user_name=username,
            organization_id=organization_id
        ).all()

        if not competencies:
            print(f"[suggest-role-simple] No competency data for user: {username}")
            return jsonify({
                'error': 'No competency data available. Please complete task analysis first.',
                'debug': {
                    'username': username,
                    'organization_id': organization_id,
                    'hint': 'Call /findProcesses endpoint first'
                }
            }), 400

        user_scores = [
            {'competency_id': c.competency_id, 'score': c.role_competency_value}
            for c in competencies
        ]

        print(f"[suggest-role-simple] User has {len(user_scores)} competency requirements")

        # ====================
        # STEP 2: Find most similar role using Euclidean distance
        # ====================
        result = find_most_similar_role_cluster(organization_id, user_scores)

        if not result or not result.get('role_ids'):
            print("[suggest-role-simple] No similar roles found")
            return jsonify({
                'error': 'No matching roles found',
                'debug': result
            }), 404

        # ====================
        # STEP 3: Calculate confidence based on distance separation
        # ====================
        best_role_id = result['role_ids'][0]
        distances = result['distances']['euclidean']
        metric_agreement = result.get('metric_agreement', 0)

        # Get all distances sorted
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])

        if len(sorted_distances) >= 2:
            best_distance = sorted_distances[0][1]
            second_best_distance = sorted_distances[1][1]

            # Calculate separation (how much better is #1 vs #2)
            if second_best_distance > 0:
                separation = (second_best_distance - best_distance) / second_best_distance
            else:
                separation = 1.0

            # Confidence based on:
            # 1. All 3 distance metrics agree (metric_agreement = 3): +0.15
            # 2. Good separation from second best: up to +0.30
            base_confidence = 0.55
            agreement_bonus = 0.15 if metric_agreement == 3 else (0.10 if metric_agreement == 2 else 0.05)
            separation_bonus = separation * 0.30

            confidence = min(base_confidence + agreement_bonus + separation_bonus, 0.95)
        else:
            # Only one role found
            confidence = 0.80 if metric_agreement == 3 else 0.70

        print(f"[suggest-role-simple] Best role ID: {best_role_id}")
        print(f"[suggest-role-simple] Euclidean distance: {distances[best_role_id]:.4f}")
        print(f"[suggest-role-simple] Metric agreement: {metric_agreement}/3")
        print(f"[suggest-role-simple] Confidence: {confidence:.0%}")

        # ====================
        # STEP 4: Build response
        # ====================
        best_role = RoleCluster.query.get(best_role_id)

        if not best_role:
            return jsonify({'error': 'Role not found in database'}), 500

        # Get alternative roles (next 2 best matches)
        alternative_roles = []
        for role_id, distance in sorted_distances[1:3]:
            role = RoleCluster.query.get(role_id)
            if role:
                alt_confidence = confidence * 0.75  # Lower confidence for alternatives
                alt_role_dict = role.to_dict()
                alt_role_dict['confidence'] = round(alt_confidence, 2)
                alt_role_dict['distance'] = round(distance, 4)
                alternative_roles.append(alt_role_dict)

        response_data = {
            'suggestedRole': best_role.to_dict(),
            'confidence': round(confidence, 2),
            'alternativeRoles': alternative_roles,
            'debug': {
                'method': 'COMPETENCY_DISTANCE (Euclidean)',
                'euclidean_distance': round(distances[best_role_id], 4),
                'metric_agreement': f"{metric_agreement}/3",
                'all_distances': {
                    RoleCluster.query.get(rid).role_cluster_name: round(dist, 4)
                    for rid, dist in sorted_distances[:5]
                    if RoleCluster.query.get(rid)
                }
            }
        }

        print(f"[suggest-role-simple] RESULT: {best_role.role_cluster_name} ({confidence:.0%} confidence)")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[suggest-role-simple] ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


# =============================================================================
# AI ROLE MAPPING (DOCUMENT EXTRACTION AND CLUSTER MAPPING)
# =============================================================================

@phase1_roles_bp.route('/phase1/role-clusters', methods=['GET'])
def get_role_clusters_for_mapping():
    """Get all 14 SE role clusters for AI mapping"""
    try:
        clusters = role_mapping_service.get_all_role_clusters()
        return jsonify({
            'success': True,
            'role_clusters': clusters,
            'total': len(clusters)
        })
    except Exception as e:
        current_app.logger.error(f"[ERROR] Failed to get role clusters: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/extract-roles-from-document', methods=['POST'])
def extract_roles_from_document():
    """
    Extract role information from uploaded documents (PDF, DOC, DOCX, TXT)
    Uses OpenAI to parse document text and extract structured role data
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        organization_id = request.form.get('organization_id')

        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not organization_id:
            return jsonify({'success': False, 'error': 'organization_id is required'}), 400

        # Get file extension
        filename = file.filename.lower()

        # Extract text based on file type
        extracted_text = None

        if filename.endswith('.txt'):
            extracted_text = file.read().decode('utf-8', errors='ignore')

        elif filename.endswith('.pdf'):
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
                extracted_text = '\n'.join(text_parts)
            except Exception as e:
                current_app.logger.error(f"[ERROR] PDF extraction failed: {str(e)}")
                return jsonify({'success': False, 'error': f'Failed to extract text from PDF: {str(e)}'}), 500

        elif filename.endswith('.docx'):
            try:
                import docx
                doc = docx.Document(file)
                text_parts = [para.text for para in doc.paragraphs]
                extracted_text = '\n'.join(text_parts)
            except Exception as e:
                current_app.logger.error(f"[ERROR] DOCX extraction failed: {str(e)}")
                return jsonify({'success': False, 'error': f'Failed to extract text from DOCX: {str(e)}'}), 500

        else:
            return jsonify({'success': False, 'error': 'Unsupported file format. Please upload PDF, DOCX, or TXT files.'}), 400

        if not extracted_text or len(extracted_text.strip()) < 50:
            return jsonify({'success': False, 'error': 'Document appears to be empty or too short'}), 400

        # Use OpenAI to extract role information
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        prompt = f"""You are an expert in analyzing organizational role descriptions.
Extract all roles mentioned in the following document and structure them as a JSON array.

For each role, extract:
- title: The job title or role name
- description: A brief description of the role
- responsibilities: An array of key responsibilities (at least 2-3 if mentioned)
- skills: An array of required skills/technologies (if mentioned)

If a role doesn't have explicit responsibilities or skills listed, infer them from the description.

Document text:
{extracted_text[:8000]}

Return ONLY a valid JSON array of roles, nothing else. Example format:
[
  {{
    "title": "Software Engineer",
    "description": "Develops and maintains software applications",
    "responsibilities": ["Write code", "Debug issues", "Review code"],
    "skills": ["Python", "JavaScript", "Git"]
  }}
]
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured role information from documents. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            ai_response = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1]
                if ai_response.startswith('json'):
                    ai_response = ai_response[4:]
                ai_response = ai_response.strip()

            # Parse JSON response
            roles = json.loads(ai_response)

            if not isinstance(roles, list):
                raise ValueError("Expected an array of roles")

            current_app.logger.info(f"[OK] Extracted {len(roles)} roles from document")

            return jsonify({
                'success': True,
                'roles': roles,
                'total': len(roles)
            })

        except json.JSONDecodeError as e:
            current_app.logger.error(f"[ERROR] Failed to parse AI response: {str(e)}")
            current_app.logger.error(f"[ERROR] AI response was: {ai_response}")
            return jsonify({'success': False, 'error': 'Failed to parse role information from document'}), 500

    except Exception as e:
        current_app.logger.error(f"[ERROR] Document extraction failed: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/map-roles', methods=['POST'])
def map_organization_roles():
    """
    Map organization roles to SE-QPT clusters using AI

    Request body:
    {
        "organization_id": 123,
        "roles": [
            {
                "title": "Senior Software Developer",
                "description": "Develops embedded software...",
                "responsibilities": ["Design software modules", ...],
                "skills": ["C++", "Python", ...]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        organization_id = data.get('organization_id')
        roles = data.get('roles', [])

        if not organization_id:
            return jsonify({'success': False, 'error': 'organization_id is required'}), 400

        if not roles:
            return jsonify({'success': False, 'error': 'roles array is required'}), 400

        # Perform AI mapping
        result = role_mapping_service.map_multiple_roles(roles)

        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 500

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        current_app.logger.error(f"[ERROR] Role mapping failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/role-mappings/<int:org_id>', methods=['GET'])
def get_role_mappings(org_id):
    """Get all role mappings for an organization"""
    try:
        mappings = OrganizationRoleMapping.query.filter_by(
            organization_id=org_id
        ).order_by(OrganizationRoleMapping.org_role_title).all()

        result = []
        for m in mappings:
            result.append({
                'id': m.id,
                'org_role_title': m.org_role_title,
                'org_role_description': m.org_role_description,
                'mapped_cluster': {
                    'id': m.mapped_cluster_id,
                    'name': m.role_cluster.role_cluster_name if m.role_cluster else None,
                    'description': m.role_cluster.role_cluster_description if m.role_cluster else None
                },
                'confidence_score': float(m.confidence_score) if m.confidence_score else None,
                'reasoning': m.mapping_reasoning,
                'matched_responsibilities': json.loads(m.matched_responsibilities) if m.matched_responsibilities else [],
                'user_confirmed': m.user_confirmed,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })

        return jsonify({
            'success': True,
            'mappings': result,
            'total': len(result)
        })

    except Exception as e:
        current_app.logger.error(f"[ERROR] Failed to get role mappings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/role-mappings/<int:mapping_id>', methods=['PUT'])
def update_role_mapping(mapping_id):
    """
    Update a role mapping (confirm, reject, or modify)

    Request body:
    {
        "user_confirmed": true,
        "confirmed_by": 456
    }
    """
    try:
        data = request.get_json()
        mapping = OrganizationRoleMapping.query.get(mapping_id)

        if not mapping:
            return jsonify({'success': False, 'error': 'Mapping not found'}), 404

        if 'user_confirmed' in data:
            mapping.user_confirmed = data['user_confirmed']
            mapping.confirmed_by = data.get('confirmed_by')
            if data['user_confirmed']:
                mapping.confirmed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Mapping updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Failed to update role mapping: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/role-mappings/<int:mapping_id>', methods=['DELETE'])
def delete_role_mapping(mapping_id):
    """Delete a role mapping"""
    try:
        mapping = OrganizationRoleMapping.query.get(mapping_id)

        if not mapping:
            return jsonify({'success': False, 'error': 'Mapping not found'}), 404

        db.session.delete(mapping)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Mapping deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Failed to delete role mapping: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@phase1_roles_bp.route('/phase1/organization-structure/<int:org_id>', methods=['GET'])
def get_organization_structure_analysis(org_id):
    """
    Get organization structure analysis showing which role clusters are present.
    This is DESCRIPTIVE only - does NOT warn about "missing" clusters.
    """
    try:
        # Get all clusters
        all_clusters = role_mapping_service.get_all_role_clusters()

        # Get confirmed mappings for this organization
        mappings = OrganizationRoleMapping.query.filter_by(
            organization_id=org_id,
            user_confirmed=True
        ).all()

        # Get unique cluster IDs that are covered
        covered_cluster_ids = set(m.mapped_cluster_id for m in mappings)

        covered_clusters = [c for c in all_clusters if c['id'] in covered_cluster_ids]
        present_count = len(covered_clusters)

        # Get organization roles that map to each cluster
        cluster_roles = defaultdict(list)
        for m in mappings:
            cluster_roles[m.mapped_cluster_id].append({
                'title': m.org_role_title,
                'confidence': float(m.confidence_score) if m.confidence_score else None
            })

        # Build analysis (DESCRIPTIVE only, no gap warnings)
        analysis = {
            'organization_id': org_id,
            'total_possible_clusters': len(all_clusters),
            'present_clusters_count': present_count,
            'present_clusters': [
                {
                    'id': c['id'],
                    'name': c['name'],
                    'description': c['description'],
                    'org_roles': cluster_roles.get(c['id'], [])
                }
                for c in covered_clusters
            ],
            'summary': f"Organization has roles in {present_count} of {len(all_clusters)} SE role clusters"
        }

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        current_app.logger.error(f"[ERROR] Failed to get organization structure: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# ORGANIZATION-SPECIFIC ROLE QUERIES
# =============================================================================

@phase1_roles_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_role_clusters():
    """
    Get organization-specific roles for competency assessment.

    Fixed: 2025-10-30 - Now returns user's organization roles instead of generic 14 clusters.
    This fixes:
    - "No competencies found" error in Phase 2 (role IDs now match role_competency_matrix)
    - Auto-selection bug when roles share same cluster (each org role now has unique ID)
    """
    print("[GET ROLES] Endpoint called")
    try:
        # Get authenticated user's organization_id
        print("[GET ROLES] Getting JWT identity...")
        user_id = int(get_jwt_identity())
        print(f"[GET ROLES] JWT user_id: {user_id}")

        user = User.query.get(user_id)
        print(f"[GET ROLES] Found user: {user.username if user else 'None'}")

        if not user:
            print("[GET ROLES ERROR] User not found")
            return jsonify({'error': 'User not found'}), 404

        organization_id = user.organization_id
        print(f"[GET ROLES] Organization ID: {organization_id}")

        if not organization_id:
            print("[GET ROLES ERROR] User has no organization")
            return jsonify({'error': 'User has no organization'}), 400

        # Return organization's actual roles (not generic clusters)
        roles = OrganizationRoles.query.filter_by(organization_id=organization_id).order_by(OrganizationRoles.id).all()
        print(f"[GET ROLES] Found {len(roles)} roles")

        # Use to_dict() for consistent output
        roles_list = [role.to_dict() for role in roles]

        current_app.logger.info(f"[GET ROLES] Returned {len(roles_list)} organization-specific roles for org {organization_id}")
        print(f"[GET ROLES] Returning {len(roles_list)} organization-specific roles for org {organization_id}")

        return jsonify(roles_list), 200

    except Exception as e:
        current_app.logger.error(f"[GET ROLES ERROR] {str(e)}")
        print(f"[GET ROLES ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch roles', 'details': str(e)}), 500


@phase1_roles_bp.route('/organization/<int:org_id>/roles', methods=['GET'])
def get_organization_roles(org_id):
    """
    Get roles for a specific organization from organization_roles table.

    Refactored: 2025-10-30 - Now uses ORM instead of raw SQL
    """
    try:
        # Verify organization exists
        org = Organization.query.get(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        # Fetch roles using ORM (relationships handle the JOIN automatically)
        roles = OrganizationRoles.query.filter_by(organization_id=org_id).order_by(OrganizationRoles.id).all()

        # Use to_dict() for consistent output
        roles_list = [role.to_dict() for role in roles]

        current_app.logger.info(f"[GET ORG ROLES] Fetched {len(roles_list)} roles for organization {org_id}")
        return jsonify(roles_list), 200

    except Exception as e:
        current_app.logger.error(f"[GET ORG ROLES] Error: {str(e)}")
        return jsonify({'error': 'Failed to get organization roles'}), 500


# =============================================================================
# MATRIX CRUD OPERATIONS (ADMIN)
# =============================================================================

@phase1_roles_bp.route('/roles-and-processes', methods=['GET'])
def get_roles_and_processes():
    """Get all roles and processes for admin matrix editing"""
    try:
        roles = RoleCluster.query.all()
        processes = IsoProcesses.query.all()

        return jsonify({
            'roles': [r.to_dict() for r in roles],
            'processes': [p.to_dict() for p in processes]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching roles and processes: {str(e)}")
        return jsonify({'error': 'Failed to fetch roles and processes'}), 500


@phase1_roles_bp.route('/role-process-matrix/<int:organization_id>/<int:role_id>', methods=['GET'])
def get_role_process_matrix(organization_id, role_id):
    """Get role-process matrix values for a specific role and organization"""
    try:
        matrix_entries = RoleProcessMatrix.query.filter_by(
            organization_id=organization_id,
            role_cluster_id=role_id
        ).all()

        return jsonify([entry.to_dict() for entry in matrix_entries]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching role-process matrix: {str(e)}")
        return jsonify({'error': 'Failed to fetch role-process matrix'}), 500


@phase1_roles_bp.route('/role-process-matrix/bulk', methods=['PUT'])
def bulk_update_role_process_matrix():
    """
    Bulk update role-process matrix and recalculate role-competency matrix
    Based on Derik's implementation (routes.py:250)
    """
    try:
        data = request.get_json()
        organization_id = data.get('organization_id')
        role_cluster_id = data.get('role_cluster_id')
        matrix = data.get('matrix')  # Dict: {process_id: value}

        if not all([organization_id, role_cluster_id, matrix]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Update or create matrix entries
        for process_id, value in matrix.items():
            process_id = int(process_id)

            # Find existing entry or create new one
            entry = RoleProcessMatrix.query.filter_by(
                organization_id=organization_id,
                role_cluster_id=role_cluster_id,
                iso_process_id=process_id
            ).first()

            if entry:
                entry.role_process_value = value
            else:
                entry = RoleProcessMatrix(
                    organization_id=organization_id,
                    role_cluster_id=role_cluster_id,
                    iso_process_id=process_id,
                    role_process_value=value
                )
                db.session.add(entry)

        db.session.commit()

        # Recalculate role-competency matrix for this organization
        # As per MATRIX_CALCULATION_PATTERN.md
        print(f"[ROLE-PROCESS MATRIX] Calling stored procedure to recalculate role-competency matrix for org {organization_id}")
        current_app.logger.info(f"[ROLE-PROCESS MATRIX] Calling stored procedure to recalculate role-competency matrix for org {organization_id}")
        db.session.execute(
            text('CALL update_role_competency_matrix(:org_id);'),
            {'org_id': organization_id}
        )
        db.session.commit()
        print(f"[ROLE-PROCESS MATRIX] Successfully recalculated role-competency matrix for org {organization_id}")
        current_app.logger.info(f"[ROLE-PROCESS MATRIX] Successfully recalculated role-competency matrix for org {organization_id}")

        return jsonify({
            'message': 'Role-process matrix updated successfully',
            'recalculated': True
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating role-process matrix: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to update role-process matrix'}), 500


@phase1_roles_bp.route('/competencies', methods=['GET'])
def get_competencies_for_matrix():
    """Get all competencies for admin matrix editing"""
    try:
        competencies = Competency.query.all()

        return jsonify([c.to_dict() for c in competencies]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching competencies: {str(e)}")
        return jsonify({'error': 'Failed to fetch competencies'}), 500


@phase1_roles_bp.route('/process-competency-matrix/<int:competency_id>', methods=['GET'])
def get_process_competency_matrix(competency_id):
    """Get process-competency matrix values for a specific competency"""
    try:
        # Get all processes
        processes = IsoProcesses.query.all()

        # Get matrix entries for this competency
        matrix_entries = ProcessCompetencyMatrix.query.filter_by(
            competency_id=competency_id
        ).all()

        return jsonify({
            'processes': [p.to_dict() for p in processes],
            'matrix': [entry.to_dict() for entry in matrix_entries]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching process-competency matrix: {str(e)}")
        return jsonify({'error': 'Failed to fetch process-competency matrix'}), 500


@phase1_roles_bp.route('/process-competency-matrix/bulk', methods=['PUT'])
def bulk_update_process_competency_matrix():
    """
    Bulk update process-competency matrix and recalculate for ALL organizations
    Based on Derik's implementation (routes.py:322-328)
    """
    try:
        data = request.get_json()
        competency_id = data.get('competency_id')
        matrix = data.get('matrix')  # Dict: {process_id: value}

        if not all([competency_id, matrix]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Update or create matrix entries
        for process_id, value in matrix.items():
            process_id = int(process_id)

            # Find existing entry or create new one
            entry = ProcessCompetencyMatrix.query.filter_by(
                iso_process_id=process_id,
                competency_id=competency_id
            ).first()

            if entry:
                entry.process_competency_value = value
            else:
                entry = ProcessCompetencyMatrix(
                    iso_process_id=process_id,
                    competency_id=competency_id,
                    process_competency_value=value
                )
                db.session.add(entry)

        db.session.commit()

        # Recalculate role-competency matrix for ALL organizations
        # As per MATRIX_CALCULATION_PATTERN.md
        organizations = Organization.query.all()
        for org in organizations:
            db.session.execute(
                text('CALL update_role_competency_matrix(:org_id);'),
                {'org_id': org.id}
            )
        db.session.commit()

        return jsonify({
            'message': 'Process-competency matrix updated successfully',
            'recalculated_for_orgs': len(organizations)
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating process-competency matrix: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to update process-competency matrix'}), 500


# =============================================================================
# ISO PROCESSES ENDPOINTS (for Process Selection Feature)
# =============================================================================

@phase1_roles_bp.route('/iso-processes', methods=['GET'])
def get_all_iso_processes():
    """
    Get all 30 ISO/IEC 15288 processes with their lifecycle groups.
    Used for the "Add More Processes" feature in Phase 2 task-based pathway.

    Returns:
        {
            "status": "success",
            "processes": [{id, name, description, lifecycle_id, lifecycle_name}, ...],
            "grouped": {"Agreement Processes": [...], ...},
            "total": 30
        }
    """
    try:
        # Fetch all processes with lifecycle info
        processes = db.session.query(
            IsoProcesses.id,
            IsoProcesses.name,
            IsoProcesses.description,
            IsoProcesses.life_cycle_process_id,
            IsoSystemLifeCycleProcesses.name.label('lifecycle_name')
        ).join(
            IsoSystemLifeCycleProcesses,
            IsoProcesses.life_cycle_process_id == IsoSystemLifeCycleProcesses.id
        ).order_by(
            IsoProcesses.life_cycle_process_id,
            IsoProcesses.id
        ).all()

        # Group by lifecycle for frontend convenience
        grouped = {}
        flat_list = []

        for p in processes:
            process_data = {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'lifecycle_id': p.life_cycle_process_id,
                'lifecycle_name': p.lifecycle_name
            }
            flat_list.append(process_data)

            if p.lifecycle_name not in grouped:
                grouped[p.lifecycle_name] = []
            grouped[p.lifecycle_name].append(process_data)

        current_app.logger.info(f"[get_all_iso_processes] Returning {len(flat_list)} ISO processes")

        return jsonify({
            'status': 'success',
            'processes': flat_list,
            'grouped': grouped,
            'total': len(flat_list)
        }), 200

    except Exception as e:
        current_app.logger.error(f"[get_all_iso_processes] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@phase1_roles_bp.route('/updateProcessSelection', methods=['POST'])
def update_process_selection():
    """
    Update user's process selection after manual modification.
    - Updates unknown_role_process_matrix with new selections
    - Re-runs stored procedure to recalculate competencies

    Used in Phase 2 task-based pathway when user modifies LLM-identified processes.

    Request body:
    {
        "username": "phase2_task_11_xxx",
        "organizationId": 11,
        "processes": [
            {"process_name": "Implementation", "involvement": "Responsible"},
            {"process_name": "Verification", "involvement": "Supporting"}
        ]
    }

    Response:
    {
        "status": "success",
        "processes": [...],
        "competencies_updated": true
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input provided"}), 400

        username = data.get('username')
        organization_id = data.get('organizationId')
        processes = data.get('processes', [])

        if not username or not organization_id:
            return jsonify({"error": "Username and organizationId required"}), 400

        if not processes:
            return jsonify({"error": "At least one process must be selected"}), 400

        current_app.logger.info(f"[updateProcessSelection] Updating for user: {username}, org: {organization_id}")
        current_app.logger.info(f"[updateProcessSelection] Processes to update: {len(processes)}")

        # Fetch all ISO processes for name-to-ID mapping
        iso_processes = IsoProcesses.query.with_entities(
            IsoProcesses.id,
            IsoProcesses.name
        ).all()
        iso_process_map = {
            process.name.strip().lower(): process.id
            for process in iso_processes
        }

        # Involvement value mapping
        involvement_values = {
            "Responsible": 2,
            "Supporting": 1,
            "Designing": 3,  # Must be 3 to match Derik's implementation
            "Not performing": 0
        }

        # Build map of selected processes
        selected_process_map = {}
        for process in processes:
            name = process.get('process_name', '').strip().lower()
            # Remove " process" suffix if present (for LLM output compatibility)
            if name.endswith(' process'):
                name = name[:-8]
            involvement = process.get('involvement', 'Not performing')
            selected_process_map[name] = involvement_values.get(involvement, 0)

        current_app.logger.info(f"[updateProcessSelection] Selected processes map: {list(selected_process_map.keys())}")

        # Delete existing entries for this user
        deleted_count = UnknownRoleProcessMatrix.query.filter_by(
            user_name=username,
            organization_id=organization_id
        ).delete()
        current_app.logger.info(f"[updateProcessSelection] Deleted {deleted_count} existing rows")

        # Insert ALL 30 processes (with 0 for unselected)
        rows_to_insert = []
        for iso_process in iso_processes:
            process_name = iso_process.name.strip().lower()

            # Check if this process is in selected list
            if process_name in selected_process_map:
                role_process_value = selected_process_map[process_name]
            else:
                role_process_value = 0  # Not performing

            rows_to_insert.append(UnknownRoleProcessMatrix(
                user_name=username,
                iso_process_id=iso_process.id,
                role_process_value=role_process_value,
                organization_id=organization_id
            ))

        if rows_to_insert:
            db.session.bulk_save_objects(rows_to_insert)
            db.session.commit()
            current_app.logger.info(f"[updateProcessSelection] Inserted {len(rows_to_insert)} process rows")

        # Re-run stored procedure to recalculate competencies
        competencies_updated = False
        try:
            current_app.logger.info(f"[updateProcessSelection] Calling stored procedure...")
            db.session.execute(
                text("CALL update_unknown_role_competency_values(:username, :organization_id);"),
                {"username": username, "organization_id": organization_id}
            )
            db.session.commit()
            current_app.logger.info(f"[updateProcessSelection] Stored procedure completed successfully")
            competencies_updated = True
        except Exception as proc_error:
            current_app.logger.error(f"[updateProcessSelection] Stored procedure error: {str(proc_error)}")
            traceback.print_exc()
            # Don't fail the whole request - user can still proceed

        # Return updated process list for frontend
        response_processes = [
            {
                "process_name": p.get('process_name'),
                "involvement": p.get('involvement')
            }
            for p in processes
        ]

        return jsonify({
            "status": "success",
            "processes": response_processes,
            "competencies_updated": competencies_updated,
            "message": "Process selection updated successfully"
        }), 200

    except Exception as e:
        current_app.logger.error(f"[updateProcessSelection] Error: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
