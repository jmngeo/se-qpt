"""
Phase 4: Micro Planning - AVIVA & RFP Routes Blueprint

API endpoints for Phase 4 "Micro Planning":
- Task 1: AVIVA Didactics Planning
- Task 2: RFP Document Export

Based on Phase4_Micro_Planning_Specification_v1.1.md
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
from datetime import datetime

from models import db

# Create blueprint
phase4_aviva_bp = Blueprint('phase4_aviva', __name__)


# ==============================================================================
# HELPER: Get Service Instance
# ==============================================================================

def _get_service():
    """Get Phase 4 AVIVA Service instance"""
    from app.services.phase4_aviva_service import Phase4AvivaService
    return Phase4AvivaService(db.session)


# ==============================================================================
# PHASE 4 CONFIGURATION
# ==============================================================================

@phase4_aviva_bp.route('/phase4/config/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_phase4_config(organization_id):
    """
    Get Phase 4 configuration for an organization.

    Returns config including task statuses and generation method.
    """
    try:
        service = _get_service()
        config = service.get_phase4_config(organization_id)

        return jsonify({
            'success': True,
            'config': config
        })

    except Exception as e:
        current_app.logger.error(f"Error getting Phase 4 config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/config/<int:organization_id>', methods=['PUT'])
@jwt_required()
def update_phase4_config(organization_id):
    """
    Update Phase 4 configuration.

    Request body can include:
    - task1_status: 'not_started', 'in_progress', 'completed'
    - task2_status: 'not_started', 'in_progress', 'completed'
    - aviva_generation_method: 'template' or 'genai'
    """
    try:
        service = _get_service()
        data = request.get_json()

        config = service.update_phase4_config(organization_id, data)

        return jsonify({
            'success': True,
            'config': config
        })

    except Exception as e:
        current_app.logger.error(f"Error updating Phase 4 config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# TASK 1: AVIVA DIDACTICS PLANNING
# ==============================================================================

@phase4_aviva_bp.route('/phase4/aviva/modules/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_aviva_modules(organization_id):
    """
    Get list of training modules ready for AVIVA planning.

    Returns modules from Phase 3 that are confirmed and have Method/Tool PMT type.
    Respects the Phase 3 view type selection (competency_level or role_clustered).
    Excludes Process-only modules.

    Returns:
    - modules: List of confirmed training modules with AVIVA status
    - view_type: 'competency_level' or 'role_clustered'
    - scaling_info: Participant scaling information from Phase 3
    - statistics: Summary statistics
    """
    try:
        service = _get_service()
        result = service.get_modules_for_aviva(organization_id)

        if result.get('error'):
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400

        modules = result.get('modules', [])
        view_type = result.get('view_type', 'competency_level')
        scaling_info = result.get('scaling_info', {})

        # Calculate statistics
        total_modules = len(modules)
        total_duration = sum(m.get('estimated_duration_hours', 0) for m in modules)
        modules_with_aviva = sum(1 for m in modules if m.get('has_aviva_plan'))

        # For role_clustered view, also calculate per-cluster stats
        cluster_stats = {}
        if view_type == 'role_clustered':
            for m in modules:
                cluster_id = m.get('cluster_id') or 0
                cluster_name = m.get('cluster_name') or 'Uncategorized'
                if cluster_id not in cluster_stats:
                    cluster_stats[cluster_id] = {
                        'cluster_id': cluster_id,
                        'cluster_name': cluster_name,
                        'total_modules': 0,
                        'modules_with_aviva': 0,
                        'common_count': 0,
                        'pathway_count': 0
                    }
                cluster_stats[cluster_id]['total_modules'] += 1
                if m.get('has_aviva_plan'):
                    cluster_stats[cluster_id]['modules_with_aviva'] += 1
                if m.get('subcluster') == 'common':
                    cluster_stats[cluster_id]['common_count'] += 1
                elif m.get('subcluster') == 'pathway':
                    cluster_stats[cluster_id]['pathway_count'] += 1

        return jsonify({
            'success': True,
            'modules': modules,
            'view_type': view_type,
            'scaling_info': scaling_info,
            'statistics': {
                'total_modules': total_modules,
                'total_duration_hours': total_duration,
                'modules_with_aviva': modules_with_aviva,
                'modules_pending': total_modules - modules_with_aviva
            },
            'cluster_stats': list(cluster_stats.values()) if cluster_stats else None
        })

    except Exception as e:
        current_app.logger.error(f"Error getting AVIVA modules: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/aviva/module/<int:module_id>/preview', methods=['GET'])
@jwt_required()
def get_module_preview(module_id):
    """
    Get detailed preview for a single module.

    Returns learning objectives, content topics, and suggested AVIVA sequence.
    """
    try:
        service = _get_service()
        preview = service.get_module_preview(module_id)

        if not preview:
            return jsonify({
                'success': False,
                'error': f'Module {module_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'module': preview
        })

    except Exception as e:
        current_app.logger.error(f"Error getting module preview: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/aviva/generate', methods=['POST'])
@jwt_required()
def generate_aviva_plans():
    """
    Generate AVIVA plans for selected modules.

    Request body:
    {
        "organization_id": 1,
        "module_ids": [1, 2, 3],
        "generation_method": "template" | "genai",
        "options": {
            "start_time_hour": 9,
            "save_to_db": true
        }
    }

    Returns generated AVIVA plans.
    """
    try:
        service = _get_service()
        data = request.get_json()

        organization_id = data.get('organization_id')
        module_ids = data.get('module_ids', [])
        generation_method = data.get('generation_method', 'template')
        options = data.get('options', {})

        start_time_hour = options.get('start_time_hour', 9)
        save_to_db = options.get('save_to_db', True)

        if not module_ids:
            return jsonify({
                'success': False,
                'error': 'No module IDs provided'
            }), 400

        plans = []
        errors = []

        for module_id in module_ids:
            try:
                plan = service.generate_aviva_plan(
                    module_id=module_id,
                    generation_method=generation_method,
                    start_time_hour=start_time_hour
                )

                if save_to_db and organization_id:
                    service.save_aviva_plan(organization_id, module_id, plan)

                plans.append(plan)

            except Exception as e:
                current_app.logger.error(f"Error generating AVIVA for module {module_id}: {e}")
                errors.append({
                    'module_id': module_id,
                    'error': str(e)
                })

        # Update Phase 4 config
        if organization_id and plans:
            service.update_phase4_config(organization_id, {
                'task1_status': 'in_progress',
                'aviva_generation_method': generation_method
            })

        return jsonify({
            'success': True,
            'plans': plans,
            'errors': errors,
            'summary': {
                'generated': len(plans),
                'failed': len(errors)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error generating AVIVA plans: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/aviva/module/<int:module_id>', methods=['GET'])
@jwt_required()
def get_aviva_plan(module_id):
    """
    Get saved AVIVA plan for a module.
    """
    try:
        service = _get_service()
        plan = service.get_aviva_plan(module_id)

        if not plan:
            return jsonify({
                'success': False,
                'error': f'No AVIVA plan found for module {module_id}'
            }), 404

        return jsonify({
            'success': True,
            'plan': plan
        })

    except Exception as e:
        current_app.logger.error(f"Error getting AVIVA plan: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/aviva/export', methods=['POST'])
@jwt_required()
def export_aviva_excel():
    """
    Export AVIVA plans to Excel file.

    Request body:
    {
        "organization_id": 1,
        "module_ids": [1, 2, 3] (optional, defaults to all)
    }

    Returns Excel file download.
    """
    try:
        service = _get_service()
        data = request.get_json()

        organization_id = data.get('organization_id')
        module_ids = data.get('module_ids')

        # Get all modules (includes subcluster info from Phase 3)
        result = service.get_modules_for_aviva(organization_id)
        modules = result.get('modules', [])

        # Build lookup for subcluster info by module_id
        module_info_lookup = {m['id']: m for m in modules if m.get('id')}

        if not module_ids:
            module_ids = [m['id'] for m in modules if m.get('has_aviva_plan')]

        if not module_ids:
            return jsonify({
                'success': False,
                'error': 'No modules with AVIVA plans to export'
            }), 400

        # Get AVIVA plans and merge subcluster info
        plans = []
        for module_id in module_ids:
            plan = service.get_aviva_plan(module_id)
            if plan:
                # Merge subcluster and other info from Phase 3 modules data
                if module_id in module_info_lookup:
                    module_info = module_info_lookup[module_id]
                    plan['subcluster'] = module_info.get('subcluster')
                    plan['estimated_participants'] = module_info.get('estimated_participants', 0)
                    plan['roles_needing_training'] = module_info.get('roles_needing_training', [])
                    if not plan.get('cluster_name'):
                        plan['cluster_name'] = module_info.get('cluster_name')
                    if not plan.get('cluster_id'):
                        plan['cluster_id'] = module_info.get('cluster_id')
                plans.append(plan)

        if not plans:
            return jsonify({
                'success': False,
                'error': 'No AVIVA plans found for the specified modules'
            }), 404

        # Generate Excel with organization data
        excel_buffer = service.export_aviva_to_excel(plans, organization_id=organization_id)

        # Get organization name for filename
        org_result = db.session.execute(
            db.text("SELECT organization_name FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()
        safe_org_name = ''
        if org_result:
            safe_org_name = ''.join(c for c in org_result.organization_name if c.isalnum() or c in ' -_')[:20]
            safe_org_name = f"_{safe_org_name}"

        # Generate filename
        filename = f"Phase4_AVIVA_Plans{safe_org_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting AVIVA to Excel: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/aviva/export-fresh', methods=['POST'])
@jwt_required()
def export_fresh_aviva_excel():
    """
    Generate fresh AVIVA plans and export to Excel (no database save).

    Request body:
    {
        "organization_id": 1,
        "module_ids": [1, 2, 3],
        "generation_method": "template" | "genai"
    }

    Returns Excel file download.
    """
    try:
        service = _get_service()
        data = request.get_json()

        organization_id = data.get('organization_id')
        module_ids = data.get('module_ids')
        generation_method = data.get('generation_method', 'template')

        # Get all confirmed modules (includes subcluster info from Phase 3)
        result = service.get_modules_for_aviva(organization_id)
        modules = result.get('modules', [])

        # Build lookup for subcluster info by module_id
        module_info_lookup = {m['id']: m for m in modules if m.get('id')}

        if not module_ids:
            module_ids = [m['id'] for m in modules if m.get('id')]

        if not module_ids:
            return jsonify({
                'success': False,
                'error': 'No modules available for AVIVA generation'
            }), 400

        # Generate plans - use parallel processing for GenAI to speed up
        plans = []

        if generation_method == 'genai' and len(module_ids) > 1:
            # Parallel processing for GenAI (much faster)
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from app.services.phase4_aviva_service import Phase4AvivaService
            from sqlalchemy.orm import scoped_session, sessionmaker

            # Create a thread-safe session factory
            engine = db.engine
            session_factory = sessionmaker(bind=engine)
            Session = scoped_session(session_factory)

            def generate_single_plan(mid):
                # Each thread gets its own session
                thread_session = Session()
                try:
                    thread_service = Phase4AvivaService(thread_session)
                    plan = thread_service.generate_aviva_plan(
                        module_id=mid,
                        generation_method=generation_method
                    )
                    return mid, plan, None
                except Exception as e:
                    import traceback
                    return mid, None, traceback.format_exc()
                finally:
                    thread_session.close()
                    Session.remove()

            current_app.logger.info(f"[Phase4 GenAI] Starting parallel generation for {len(module_ids)} modules")

            # Use up to 5 parallel workers (conservative for OpenAI rate limits)
            max_workers = min(5, len(module_ids))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(generate_single_plan, mid): mid for mid in module_ids}

                for future in as_completed(futures):
                    mid, plan, error = future.result()
                    if plan:
                        # Merge subcluster and other info
                        if mid in module_info_lookup:
                            module_info = module_info_lookup[mid]
                            plan['subcluster'] = module_info.get('subcluster')
                            plan['estimated_participants'] = module_info.get('estimated_participants', 0)
                            plan['roles_needing_training'] = module_info.get('roles_needing_training', [])
                            if not plan.get('cluster_name'):
                                plan['cluster_name'] = module_info.get('cluster_name')
                            if not plan.get('cluster_id'):
                                plan['cluster_id'] = module_info.get('cluster_id')
                        plans.append(plan)
                    else:
                        current_app.logger.warning(f"Skipping module {mid}: {error}")

            current_app.logger.info(f"[Phase4 GenAI] Completed {len(plans)} of {len(module_ids)} modules")
        else:
            # Sequential processing for template (fast enough)
            for module_id in module_ids:
                try:
                    plan = service.generate_aviva_plan(
                        module_id=module_id,
                        generation_method=generation_method
                    )
                    # Merge subcluster and other info from Phase 3 modules data
                    if module_id in module_info_lookup:
                        module_info = module_info_lookup[module_id]
                        plan['subcluster'] = module_info.get('subcluster')
                        plan['estimated_participants'] = module_info.get('estimated_participants', 0)
                        plan['roles_needing_training'] = module_info.get('roles_needing_training', [])
                        if not plan.get('cluster_name'):
                            plan['cluster_name'] = module_info.get('cluster_name')
                        if not plan.get('cluster_id'):
                            plan['cluster_id'] = module_info.get('cluster_id')
                    plans.append(plan)
                except Exception as e:
                    current_app.logger.warning(f"Skipping module {module_id}: {e}")

        if not plans:
            return jsonify({
                'success': False,
                'error': 'Failed to generate any AVIVA plans'
            }), 500

        # Generate Excel with organization data
        excel_buffer = service.export_aviva_to_excel(plans, organization_id=organization_id)

        # Get organization name for filename
        org_result = db.session.execute(
            db.text("SELECT organization_name FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()
        safe_org_name = ''
        if org_result:
            safe_org_name = ''.join(c for c in org_result.organization_name if c.isalnum() or c in ' -_')[:20]
            safe_org_name = f"_{safe_org_name}"

        # Generate filename
        method_suffix = 'GenAI' if generation_method == 'genai' else 'Template'
        filename = f"Phase4_AVIVA_Plans_{method_suffix}{safe_org_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting fresh AVIVA to Excel: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# CONTENT BASELINE
# ==============================================================================

@phase4_aviva_bp.route('/phase4/content-baseline/<int:competency_id>', methods=['GET'])
@jwt_required()
def get_content_baseline(competency_id):
    """
    Get content topics baseline for a competency.
    """
    try:
        result = db.session.execute(
            db.text("""
                SELECT c.competency_name, ccb.content_topics
                FROM competency_content_baseline ccb
                JOIN competency c ON ccb.competency_id = c.id
                WHERE ccb.competency_id = :comp_id
            """),
            {'comp_id': competency_id}
        ).fetchone()

        if not result:
            return jsonify({
                'success': False,
                'error': f'No content baseline for competency {competency_id}'
            }), 404

        return jsonify({
            'success': True,
            'competency_id': competency_id,
            'competency_name': result.competency_name,
            'content_topics': result.content_topics
        })

    except Exception as e:
        current_app.logger.error(f"Error getting content baseline: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/content-baseline', methods=['GET'])
@jwt_required()
def get_all_content_baselines():
    """
    Get content topics baseline for all competencies.
    """
    try:
        results = db.session.execute(
            db.text("""
                SELECT c.id, c.competency_name, ccb.content_topics
                FROM competency_content_baseline ccb
                JOIN competency c ON ccb.competency_id = c.id
                ORDER BY c.id
            """)
        ).fetchall()

        baselines = [
            {
                'competency_id': r.id,
                'competency_name': r.competency_name,
                'content_topics': r.content_topics
            }
            for r in results
        ]

        return jsonify({
            'success': True,
            'baselines': baselines,
            'count': len(baselines)
        })

    except Exception as e:
        current_app.logger.error(f"Error getting content baselines: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# TASK 2: RFP DOCUMENT EXPORT
# ==============================================================================

def _get_rfp_service():
    """Get Phase 4 RFP Service instance"""
    from app.services.phase4_rfp_service import Phase4RFPService
    return Phase4RFPService(db.session)


@phase4_aviva_bp.route('/phase4/rfp/preview/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_rfp_preview(organization_id):
    """
    Get RFP data preview/summary for an organization.

    Returns aggregated data from all phases that will be included in the RFP export.
    """
    try:
        service = _get_rfp_service()

        # Get summary data (without full AVIVA plans for preview)
        org_profile = service.get_organization_profile(organization_id)
        maturity = service.get_maturity_assessment(organization_id)
        target_group = service.get_target_group_size(organization_id)
        strategies = service.get_strategies(organization_id)
        roles = service.get_organization_roles(organization_id)
        gaps = service.get_competency_gaps(organization_id)
        existing_trainings = service.get_existing_trainings(organization_id)
        pmt_context = service.get_pmt_context(organization_id)
        phase3_data = service.get_phase3_data(organization_id)

        # Get AVIVA plan count
        aviva_service = _get_service()
        aviva_result = aviva_service.get_modules_for_aviva(organization_id)
        aviva_modules = aviva_result.get('modules', [])
        modules_with_aviva = sum(1 for m in aviva_modules if m.get('has_aviva_plan'))

        phase3_summary = phase3_data.get('summary', {})

        return jsonify({
            'success': True,
            'preview': {
                'organization': {
                    'name': org_profile.get('name'),
                    'maturity_score': org_profile.get('maturity_score'),
                    'maturity_level': org_profile.get('maturity_level'),
                    'assessment_pathway': maturity.get('assessment_pathway')
                },
                'strategies': {
                    'primary': strategies[0].get('name') if strategies else 'Not Selected',
                    'all': [s.get('name') for s in strategies],
                    'count': len(strategies)
                },
                'scope': {
                    'target_group_size': target_group.get('size', 0),
                    'target_group_range': target_group.get('range_label'),
                    'roles_count': len(roles),
                    'participating_roles': sum(1 for r in roles if r.get('participating')),
                    'total_modules': phase3_summary.get('total_modules', 0),
                    'confirmed_modules': phase3_summary.get('confirmed_modules', 0),
                    'total_gaps': gaps.get('total_gaps', 0),
                    'modules_with_aviva': modules_with_aviva,
                    'existing_trainings_count': len(existing_trainings)
                },
                'pmt_context': {
                    'has_tools': bool(pmt_context.get('tools')),
                    'has_methods': bool(pmt_context.get('methods')),
                    'has_processes': bool(pmt_context.get('processes')),
                    'industry': pmt_context.get('industry')
                },
                'format_distribution': phase3_summary.get('format_distribution', {}),
                'phases_complete': {
                    'phase1': org_profile.get('phase1_completed', False),
                    'phase2': org_profile.get('phase2_completed', False),
                    'phase3': org_profile.get('phase3_completed', False),
                    'has_aviva': modules_with_aviva > 0
                }
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting RFP preview: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/rfp/export', methods=['POST'])
@jwt_required()
def export_rfp():
    """
    Export RFP document to Excel.

    Request body:
    {
        "organization_id": 1,
        "include_aviva": true,
        "save_record": true
    }

    Returns Excel file download.
    """
    try:
        service = _get_rfp_service()
        data = request.get_json()

        organization_id = data.get('organization_id')
        include_aviva = data.get('include_aviva', True)
        save_record = data.get('save_record', True)

        if not organization_id:
            return jsonify({
                'success': False,
                'error': 'organization_id is required'
            }), 400

        current_app.logger.info(f"[RFP] Starting export for org {organization_id}, include_aviva={include_aviva}")

        # Generate Excel
        excel_buffer = service.export_rfp_to_excel(organization_id, include_aviva=include_aviva)

        # Save export record
        if save_record:
            service.save_export_record(
                organization_id=organization_id,
                export_format='excel',
                include_aviva=include_aviva
            )

        # Get organization name for filename
        org_result = db.session.execute(
            db.text("SELECT organization_name FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()

        safe_org_name = ''
        if org_result:
            safe_org_name = ''.join(c for c in org_result.organization_name if c.isalnum() or c in ' -_')[:20]
            safe_org_name = f"_{safe_org_name}"

        filename = f"SE_QPT_RFP{safe_org_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        current_app.logger.info(f"[RFP] Export completed: {filename}")

        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting RFP: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/rfp/data/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_rfp_data(organization_id):
    """
    Get complete RFP data as JSON (for debugging/preview).

    Query params:
    - include_aviva: true/false (default: true)
    """
    try:
        service = _get_rfp_service()

        include_aviva = request.args.get('include_aviva', 'true').lower() == 'true'

        data = service.get_rfp_data(organization_id, include_aviva=include_aviva)

        return jsonify({
            'success': True,
            'data': data
        })

    except Exception as e:
        current_app.logger.error(f"Error getting RFP data: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/rfp/history/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_rfp_history(organization_id):
    """
    Get RFP export history for an organization.
    """
    try:
        service = _get_rfp_service()
        history = service.get_export_history(organization_id)

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        current_app.logger.error(f"Error getting RFP history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase4_aviva_bp.route('/phase4/rfp/export-word', methods=['POST'])
@jwt_required()
def export_rfp_word():
    """
    Export RFP document to Word format with LLM-generated content.

    Request body:
    {
        "organization_id": 1,
        "include_llm": true  (optional, default true)
    }

    Returns Word document (.docx) download.
    Note: This endpoint may take 2-5 minutes for LLM generation.
    """
    try:
        service = _get_rfp_service()
        data = request.get_json()

        organization_id = data.get('organization_id')
        include_llm = data.get('include_llm', True)

        if not organization_id:
            return jsonify({
                'success': False,
                'error': 'organization_id is required'
            }), 400

        current_app.logger.info(f"[RFP] Starting Word export for org {organization_id}, include_llm={include_llm}")

        # Generate Word document (may take time for LLM)
        word_buffer = service.export_rfp_to_word(organization_id, include_llm=include_llm)

        # Save export record
        service.save_export_record(
            organization_id=organization_id,
            export_format='word',
            include_aviva=False
        )

        # Get organization name for filename
        org_result = db.session.execute(
            db.text("SELECT organization_name FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()

        safe_org_name = ''
        if org_result:
            safe_org_name = ''.join(c for c in org_result.organization_name if c.isalnum() or c in ' -_')[:20]
            safe_org_name = f"_{safe_org_name}"

        filename = f"SE_QPT_RFP{safe_org_name}_{datetime.now().strftime('%Y%m%d')}.docx"

        current_app.logger.info(f"[RFP] Word export completed: {filename}")

        return send_file(
            word_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting RFP to Word: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


