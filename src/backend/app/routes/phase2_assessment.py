"""
Phase 2 Assessment Routes Blueprint
Handles competency assessment, survey submission, and results retrieval
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import traceback
from sqlalchemy import func
from collections import defaultdict

from models import (
    db,
    User,
    CompetencyAssessment,
    Competency,
    CompetencyIndicator,
    RoleCompetencyMatrix,
    UnknownRoleCompetencyMatrix,
    UserCompetencySurveyResults,
    UserRoleCluster,
    UserCompetencySurveyFeedback,
    UserAssessment,
    OrganizationRoles
)

# Import LLM feedback generation
from app.services.generate_survey_feedback import generate_feedback_with_llm

# Create blueprint
phase2_assessment_bp = Blueprint('phase2_assessment', __name__)


# =============================================================================
# LEGACY ASSESSMENT ENDPOINTS (3 endpoints)
# =============================================================================

@phase2_assessment_bp.route('/assessments/competency', methods=['POST'])
@jwt_required()
def submit_competency_assessment():
    """Submit individual competency assessment (All users)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Validate competency scores
        competency_scores = data.get('competency_scores')
        if not competency_scores:
            return jsonify({'error': 'competency_scores required'}), 400

        # Create competency assessment record
        assessment = CompetencyAssessment(
            user_id=user_id,
            role_cluster=data.get('role_cluster', 'Unknown')
        )
        assessment.set_competency_scores(competency_scores)
        db.session.add(assessment)
        db.session.commit()

        return jsonify({'assessment': assessment.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Competency assessment error: {str(e)}")
        return jsonify({'error': 'Failed to submit assessment'}), 500


@phase2_assessment_bp.route('/assessments/results/<user_id>', methods=['GET'])
@jwt_required()
def get_user_assessment_results_legacy(user_id):
    """Get assessment results for a user (legacy endpoint)"""
    try:
        current_user_id = int(get_jwt_identity())
        claims = get_jwt()

        # Users can only see their own results, admins can see all
        if user_id != current_user_id and claims.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        # Get competency assessment
        competency_assessment = CompetencyAssessment.query.filter_by(
            user_id=user_id
        ).first()

        # Note: RoleMapping and LearningPlan models removed
        # This legacy endpoint returns limited data
        results = {
            'competency_assessment': competency_assessment.to_dict() if competency_assessment else None,
            'role_mapping': None,
            'learning_plan': None
        }

        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Get assessment results error: {str(e)}")
        return jsonify({'error': 'Failed to get results'}), 500


@phase2_assessment_bp.route('/assessments/organization-summary', methods=['GET'])
@jwt_required()
def get_organization_assessment_summary():
    """Get organization-wide assessment summary (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)

        # Get all users in organization
        org_users = User.query.filter_by(organization_id=user.organization_id).all()

        # Get completion statistics
        total_users = len(org_users)
        completed_competency = CompetencyAssessment.query.join(User).filter(
            User.organization_id == user.organization_id
        ).count()

        summary = {
            'total_users': total_users,
            'completed_competency_assessments': completed_competency,
            'completion_rate': (completed_competency / total_users * 100) if total_users > 0 else 0,
            'maturity_assessment': None  # MaturityAssessment removed - use dashboard endpoint for full data
        }

        return jsonify(summary), 200

    except Exception as e:
        current_app.logger.error(f"Organization summary error: {str(e)}")
        return jsonify({'error': 'Failed to get summary'}), 500


# =============================================================================
# LEARNING PLAN ENDPOINTS (2 endpoints - DEPRECATED)
# Note: LearningPlan model has been removed from the system
# These endpoints are kept for backwards compatibility but return errors
# =============================================================================

@phase2_assessment_bp.route('/learning-plan/<user_id>', methods=['GET'])
@jwt_required()
def get_learning_plan(user_id):
    """Get learning plan for a user (DEPRECATED)"""
    return jsonify({
        'error': 'Learning plan endpoint deprecated',
        'message': 'Use Phase 2 Task 3 learning objectives generation instead'
    }), 410


@phase2_assessment_bp.route('/learning-plan/generate', methods=['POST'])
@jwt_required()
def generate_learning_plan():
    """Generate learning plan for current user (DEPRECATED)"""
    return jsonify({
        'error': 'Learning plan endpoint deprecated',
        'message': 'Use Phase 2 Task 3 learning objectives generation instead'
    }), 410


# =============================================================================
# QUESTIONNAIRE COMPATIBILITY ENDPOINTS
# =============================================================================

@phase2_assessment_bp.route('/public/users/<string:user_id>/responses', methods=['GET'])
def get_user_questionnaire_responses_uuid(user_id):
    """Public endpoint for questionnaire responses using UUID user IDs (compatibility)"""
    try:
        # Import the models from models.py to avoid circular imports
        from models import QuestionnaireResponse, Questionnaire

        print(f"DEBUG: MVP public endpoint accessed for user UUID {user_id}")

        # CRITICAL: The questionnaire system uses integer User IDs, not UUIDs
        # We need to find the User by UUID first, then query responses by integer ID
        user = User.query.filter_by(uuid=user_id).first()

        if not user:
            print(f"DEBUG: No user found with UUID {user_id}")
            return jsonify({
                'success': True,
                'responses': [],
                'total_count': 0
            }), 200

        print(f"DEBUG: Found user ID {user.id} for UUID {user_id}")

        # Query responses using the integer user ID
        responses = QuestionnaireResponse.query.filter_by(user_id=user.id).order_by(QuestionnaireResponse.started_at.desc()).all()

        print(f"DEBUG: Found {len(responses)} responses for user ID {user.id}")

        responses_data = []
        for response in responses:
            questionnaire_name = 'Unknown Questionnaire'
            questionnaire_type = 'unknown'

            if response.questionnaire_id:
                questionnaire = Questionnaire.query.get(response.questionnaire_id)
                if questionnaire:
                    questionnaire_name = questionnaire.name
                    questionnaire_type = questionnaire.questionnaire_type

            responses_data.append({
                'id': response.id,
                'questionnaire_id': response.questionnaire_id,
                'questionnaire_name': questionnaire_name,
                'questionnaire_type': questionnaire_type,
                'status': response.status,
                'started_at': response.started_at.isoformat() if response.started_at else None,
                'completed_at': response.completed_at.isoformat() if response.completed_at else None
            })

        return jsonify({
            'success': True,
            'responses': responses_data,
            'total_count': len(responses_data)
        }), 200

    except Exception as e:
        print(f"DEBUG: Error in get_user_questionnaire_responses_uuid: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'responses': [],
            'total_count': 0
        }), 500


# =============================================================================
# QUESTIONNAIRE ENDPOINTS
# =============================================================================

@phase2_assessment_bp.route('/questionnaires/<int:questionnaire_id>', methods=['GET'])
def get_questionnaire_definition(questionnaire_id):
    """Get questionnaire definition (stub for now)"""
    try:
        # Stub implementation - return empty questionnaire structure
        # This can be expanded later with actual questionnaire data
        return jsonify({
            'id': questionnaire_id,
            'name': f'Questionnaire {questionnaire_id}',
            'questions': [],
            'description': 'Questionnaire definition'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting questionnaire: {str(e)}")
        return jsonify({'error': 'Failed to get questionnaire'}), 500


# =============================================================================
# DERIK'S COMPETENCY ASSESSMENT ENDPOINTS
# Legacy endpoints for competency assessment bridge compatibility
# =============================================================================

@phase2_assessment_bp.route('/get_required_competencies_for_roles', methods=['POST'])
def get_required_competencies_for_roles():
    """Fetch distinct competencies and the maximum competency value for selected roles and organization."""
    data = request.json
    role_ids = data.get('role_ids')
    organization_id = data.get('organization_id')
    user_name = data.get('user_name')
    survey_type = data.get('survey_type')

    print(f"[get_required_competencies_for_roles] Role IDs: {role_ids}")
    print(f"[get_required_competencies_for_roles] Organization ID: {organization_id}")
    print(f"[get_required_competencies_for_roles] Survey type: {survey_type}")

    if survey_type == 'known_roles':
        if role_ids is None or organization_id is None:
            return jsonify({"error": "role_ids and organization_id are required"}), 400

        try:
            # Query with JOIN to get full competency details
            competencies = (
                db.session.query(
                    RoleCompetencyMatrix.competency_id,
                    Competency.competency_name,
                    Competency.description,
                    Competency.competency_area,
                    func.max(RoleCompetencyMatrix.role_competency_value).label('max_value')
                )
                .join(Competency, RoleCompetencyMatrix.competency_id == Competency.id)
                .filter(
                    RoleCompetencyMatrix.role_cluster_id.in_(role_ids),
                    RoleCompetencyMatrix.organization_id == organization_id
                )
                .group_by(
                    RoleCompetencyMatrix.competency_id,
                    Competency.competency_name,
                    Competency.description,
                    Competency.competency_area
                )
                .having(func.max(RoleCompetencyMatrix.role_competency_value) > 0)  # Filter out zero-level competencies
                .order_by(RoleCompetencyMatrix.competency_id)
                .all()
            )

            competencies_data = [
                {
                    'competency_id': competency.competency_id,
                    'competency_name': competency.competency_name,
                    'description': competency.description,
                    'category': competency.competency_area,  # Map to 'category' for frontend compatibility
                    'max_value': competency.max_value
                }
                for competency in competencies
            ]

            print(f"[get_required_competencies_for_roles] Filtered {len(competencies_data)} competencies with required level > 0")
            return jsonify({
                "success": True,
                "competencies": competencies_data,
                "count": len(competencies_data)
            }), 200

        except Exception as e:
            print(f"[get_required_competencies_for_roles] Error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    elif survey_type == 'unknown_roles':
        if user_name is None or organization_id is None:
            return jsonify({"error": "user_name and organization_id are required"}), 400

        try:
            # Query with JOIN to get full competency details (same as known_roles fix)
            competencies = (
                db.session.query(
                    UnknownRoleCompetencyMatrix.competency_id,
                    Competency.competency_name,
                    Competency.description,
                    Competency.competency_area,
                    UnknownRoleCompetencyMatrix.role_competency_value.label('max_value')
                )
                .join(Competency, UnknownRoleCompetencyMatrix.competency_id == Competency.id)
                .filter(
                    UnknownRoleCompetencyMatrix.user_name == user_name,
                    UnknownRoleCompetencyMatrix.organization_id == organization_id,
                    UnknownRoleCompetencyMatrix.role_competency_value > 0  # Filter out zero-level competencies
                )
                .order_by(UnknownRoleCompetencyMatrix.competency_id)
                .all()
            )

            competencies_data = [
                {
                    'competency_id': competency.competency_id,
                    'competency_name': competency.competency_name,
                    'description': competency.description,
                    'category': competency.competency_area,  # Map to 'category' for frontend compatibility
                    'max_value': competency.max_value
                }
                for competency in competencies
            ]

            print(f"[get_required_competencies_for_roles] Task-based: Filtered {len(competencies_data)} competencies with required level > 0")
            return jsonify({"competencies": competencies_data}), 200

        except Exception as e:
            print(f"[get_required_competencies_for_roles] Error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    elif survey_type == "all_roles":
        print("[get_required_competencies_for_roles] Fetching competencies for all roles")
        if organization_id is None:
            return jsonify({"error": "organization_id is required"}), 400

        try:
            competencies = (
                db.session.query(
                    RoleCompetencyMatrix.competency_id,
                    func.round(func.avg(RoleCompetencyMatrix.role_competency_value)).label('max_value')
                )
                .filter(
                    RoleCompetencyMatrix.organization_id == organization_id
                )
                .group_by(RoleCompetencyMatrix.competency_id)
                .having(func.round(func.avg(RoleCompetencyMatrix.role_competency_value)) > 0)  # Filter out zero-level competencies
                .order_by(RoleCompetencyMatrix.competency_id)
                .all()
            )

            competencies_data = [
                {
                    'competency_id': competency.competency_id,
                    'max_value': competency.max_value
                }
                for competency in competencies
            ]

            print(f"[get_required_competencies_for_roles] Filtered {len(competencies_data)} competencies with required level > 0")
            return jsonify({
                "success": True,
                "competencies": competencies_data,
                "count": len(competencies_data)
            }), 200

        except Exception as e:
            print(f"[get_required_competencies_for_roles] Error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid survey_type"}), 400


# =============================================================================
# DERIK'S COMPETENCY ASSESSMENT ENDPOINTS (Phase 2 Integration)
# =============================================================================

@phase2_assessment_bp.route('/get_competency_indicators_for_competency/<int:competency_id>', methods=['GET'])
def get_competency_indicators_for_competency(competency_id):
    """
    Fetch all indicators associated with the specified competency, grouped by level.
    Used by Phase 2 competency assessment to display indicators for each competency.
    """
    try:
        # Query to fetch indicators by competency ID
        indicators = CompetencyIndicator.query.filter_by(competency_id=competency_id).all()

        # Group indicators by their level
        indicators_by_level = {}
        for indicator in indicators:
            if indicator.level not in indicators_by_level:
                indicators_by_level[indicator.level] = []
            indicators_by_level[indicator.level].append({
                "indicator_en": indicator.indicator_en,
                "indicator_de": indicator.indicator_de
            })

        # Structure response with indicators grouped by level
        response_data = [
            {
                "level": level,
                "indicators": indicators
            }
            for level, indicators in indicators_by_level.items()
        ]

        return jsonify(response_data), 200

    except Exception as e:
        print(f"[get_competency_indicators] Error: {str(e)}")
        return jsonify({"error": "An error occurred while fetching competency indicators"}), 500


# =============================================================================
# NEW AUTHENTICATED ASSESSMENT ENDPOINTS (Replaces anonymous survey system)
# =============================================================================

@phase2_assessment_bp.route('/assessment/start', methods=['POST'])
def start_assessment():
    """
    Start a new assessment for an authenticated user
    Replaces /new_survey_user endpoint - uses real authenticated user instead of anonymous username
    """
    data = request.get_json()
    try:
        user_id = data.get('user_id')
        organization_id = data.get('organization_id')
        assessment_type = data.get('assessment_type')  # 'role_based', 'task_based', 'full_competency'

        if not user_id or not organization_id or not assessment_type:
            return jsonify({"error": "user_id, organization_id, and assessment_type are required"}), 400

        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Determine survey_type based on assessment_type
        survey_type_map = {
            'role_based': 'known_roles',
            'task_based': 'unknown_roles',
            'full_competency': 'all_roles'
        }
        survey_type = survey_type_map.get(assessment_type, 'known_roles')

        # Create new assessment record
        assessment = UserAssessment(
            user_id=user_id,
            organization_id=organization_id,
            assessment_type=assessment_type,
            survey_type=survey_type
        )

        db.session.add(assessment)
        db.session.commit()
        db.session.refresh(assessment)

        print(f"[start_assessment] Created assessment {assessment.id} for user {user.username}")

        return jsonify({
            "message": "Assessment started successfully",
            "assessment_id": assessment.id,
            "username": user.username,  # Return for compatibility
            "user_id": user.id,
            "assessment": assessment.to_dict()
        }), 201

    except Exception as e:
        print(f"[start_assessment] Error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@phase2_assessment_bp.route('/phase2/start-assessment', methods=['POST'])
def start_phase2_assessment():
    """
    Start a new Phase 2 assessment (task-based or role-based pathway)

    Expected payload:
    - org_id: Organization ID
    - admin_user_id: ID of user taking assessment
    - employee_name: Name of employee (optional)
    - role_ids: Array of selected role IDs (empty for task-based)
    - competencies: Array of necessary competencies
    - assessment_type: 'phase2_employee' or other
    - task_based_username: Username for task-based pathway (optional)
    """
    data = request.get_json()
    try:
        org_id = data.get('org_id')
        admin_user_id = data.get('admin_user_id')
        employee_name = data.get('employee_name')
        role_ids = data.get('role_ids', [])
        competencies = data.get('competencies', [])
        assessment_type = data.get('assessment_type', 'phase2_employee')
        task_based_username = data.get('task_based_username')

        if not org_id or not admin_user_id:
            return jsonify({"error": "org_id and admin_user_id are required"}), 400

        # Verify user exists
        user = User.query.get(admin_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Determine survey_type based on pathway
        survey_type = 'unknown_roles' if task_based_username else 'known_roles'

        # Prepare tasks_responsibilities JSON for task-based pathway
        tasks_data = None
        if task_based_username:
            tasks_data = {
                'username': task_based_username,
                'competencies': competencies
            }

        # Create new assessment record
        assessment = UserAssessment(
            user_id=admin_user_id,
            organization_id=org_id,
            assessment_type=assessment_type,
            survey_type=survey_type,
            selected_roles=role_ids if role_ids else None,
            tasks_responsibilities=tasks_data
        )

        db.session.add(assessment)
        db.session.commit()
        db.session.refresh(assessment)

        print(f"[start_phase2_assessment] Created assessment {assessment.id} for user {user.username}")
        print(f"[start_phase2_assessment] Survey type: {survey_type}, Task-based username: {task_based_username}")

        return jsonify({
            "success": True,
            "message": "Assessment started successfully",
            "assessment_id": assessment.id,
            "username": user.username,
            "survey_type": survey_type,
            "task_based_username": task_based_username
        }), 201

    except Exception as e:
        print(f"[start_phase2_assessment] Error: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": "An error occurred", "details": str(e)}), 500


@phase2_assessment_bp.route('/phase2/submit-assessment', methods=['POST'])
def submit_phase2_assessment():
    """
    Submit Phase 2 competency assessment answers

    Expected payload:
    - assessment_id: Assessment ID
    - answers: Array of {competency_id, selected_groups, current_level}

    Returns:
    - Success status and assessment ID
    """
    data = request.get_json()
    try:
        assessment_id = data.get('assessment_id')
        answers = data.get('answers', [])

        if not assessment_id:
            return jsonify({"success": False, "error": "assessment_id is required"}), 400

        # Fetch the assessment
        assessment = UserAssessment.query.get(assessment_id)
        if not assessment:
            return jsonify({"success": False, "error": "Assessment not found"}), 404

        print(f"[submit_phase2_assessment] Submitting {len(answers)} answers for assessment {assessment_id}")

        # Delete existing survey results for this assessment
        UserCompetencySurveyResults.query.filter_by(
            user_id=assessment.user_id,
            assessment_id=assessment_id
        ).delete()

        # Insert new survey results
        for answer in answers:
            competency_id = answer.get('competency_id')
            current_level = answer.get('current_level', 0)

            if competency_id is None:
                continue

            survey_result = UserCompetencySurveyResults(
                user_id=assessment.user_id,
                organization_id=assessment.organization_id,
                competency_id=competency_id,
                score=current_level,
                assessment_id=assessment_id
            )
            db.session.add(survey_result)
            print(f"[submit_phase2_assessment] Added result: competency {competency_id}, score {current_level}")

        # Mark assessment as completed
        assessment.completed_at = datetime.utcnow()

        # Populate user_role_cluster table for role-based pathway
        # This is required for learning objectives to detect high-maturity organizations
        if assessment.survey_type == 'known_roles' and assessment.selected_roles:
            # Delete existing role assignments for this assessment
            UserRoleCluster.query.filter_by(assessment_id=assessment_id).delete()

            # Insert new role assignments
            for role_id in assessment.selected_roles:
                role_entry = UserRoleCluster(
                    user_id=assessment.user_id,
                    role_cluster_id=role_id,
                    assessment_id=assessment_id
                )
                db.session.add(role_entry)
                print(f"[submit_phase2_assessment] Added role {role_id} to user_role_cluster for user {assessment.user_id}")

        db.session.commit()

        print(f"[submit_phase2_assessment] Assessment {assessment_id} completed successfully")

        # After saving, fetch results with gap analysis using existing get_assessment_results logic
        # This provides immediate feedback to the user and enables caching for future visits
        try:
            # Fetch user competencies
            print(f"[submit_phase2_assessment] Fetching competencies for assessment_id={assessment_id}")
            user_competencies = UserCompetencySurveyResults.query.filter_by(
                assessment_id=assessment_id
            ).order_by(UserCompetencySurveyResults.competency_id).all()

            print(f"[submit_phase2_assessment] Found {len(user_competencies)} user competencies")

            competencies = Competency.query.filter(
                Competency.id.in_([u.competency_id for u in user_competencies])
            ).order_by(Competency.id).all()

            competency_info_map = {comp.id: {'name': comp.competency_name, 'area': comp.competency_area} for comp in competencies}

            user_scores = [
                {
                    'competency_id': u.competency_id,
                    'score': u.score,
                    'competency_name': competency_info_map[u.competency_id]['name'],
                    'competency_area': competency_info_map[u.competency_id]['area']
                }
                for u in user_competencies
            ]

            # Fetch required scores based on survey type
            if assessment.survey_type == 'known_roles':
                # Use selected_roles from assessment (not UserRoleCluster)
                role_cluster_ids = assessment.selected_roles or []

                if not role_cluster_ids:
                    print(f"[submit_phase2_assessment] WARNING: No role IDs found in assessment.selected_roles")
                    max_scores = []
                else:
                    print(f"[submit_phase2_assessment] Role-based pathway: role_ids={role_cluster_ids}, org_id={assessment.organization_id}")
                    max_scores = db.session.query(
                        RoleCompetencyMatrix.competency_id,
                        db.func.max(RoleCompetencyMatrix.role_competency_value).label('max_score')
                    ).filter(
                        RoleCompetencyMatrix.organization_id == assessment.organization_id,
                        RoleCompetencyMatrix.role_cluster_id.in_(role_cluster_ids)
                    ).group_by(RoleCompetencyMatrix.competency_id).having(
                        db.func.max(RoleCompetencyMatrix.role_competency_value) > 0
                    ).order_by(RoleCompetencyMatrix.competency_id).all()
                    print(f"[submit_phase2_assessment] Found {len(max_scores)} required competencies from role_competency_matrix")

            elif assessment.survey_type == 'unknown_roles':
                # For task-based pathway - get username from tasks_responsibilities JSON
                task_based_username = assessment.tasks_responsibilities.get('username') if assessment.tasks_responsibilities else None

                if not task_based_username:
                    print(f"[submit_phase2_assessment] ERROR: No task-based username found in assessment {assessment_id}")
                    raise Exception("Task-based username not found in assessment")

                print(f"[submit_phase2_assessment] Task-based pathway: task_username={task_based_username}, org_id={assessment.organization_id}")
                max_scores = db.session.query(
                    UnknownRoleCompetencyMatrix.competency_id,
                    UnknownRoleCompetencyMatrix.role_competency_value.label('max_score')
                ).filter(
                    UnknownRoleCompetencyMatrix.organization_id == assessment.organization_id,
                    UnknownRoleCompetencyMatrix.user_name == task_based_username,
                    UnknownRoleCompetencyMatrix.role_competency_value > 0
                ).all()
                print(f"[submit_phase2_assessment] Found {len(max_scores)} required competencies from unknown_role_competency_matrix")
            else:
                max_scores = []

            max_scores_dict = [{'competency_id': m.competency_id, 'max_score': float(m.max_score)} for m in max_scores]

            # Filter user_scores to only include competencies with required level > 0
            required_competency_ids = {m['competency_id'] for m in max_scores_dict}
            print(f"[submit_phase2_assessment] Required competency IDs: {required_competency_ids}")
            user_scores = [score for score in user_scores if score['competency_id'] in required_competency_ids]
            print(f"[submit_phase2_assessment] Filtered user_scores to {len(user_scores)} competencies")

            # Calculate summary statistics
            total_competencies = len(user_scores)
            proficient = 0
            needs_improvement = 0

            for score in user_scores:
                comp_id = score['competency_id']
                current_level = score['score']
                required_level = next((m['max_score'] for m in max_scores_dict if m['competency_id'] == comp_id), 0)

                if current_level >= required_level:
                    proficient += 1
                else:
                    needs_improvement += 1

            print(f"[submit_phase2_assessment] Gap analysis: {proficient}/{total_competencies} proficient, {needs_improvement} need improvement")

            return jsonify({
                "success": True,
                "message": "Assessment submitted successfully",
                "assessment_id": assessment_id,
                "results": {
                    "assessment_id": assessment_id,  # Add for CompetencyResults compatibility
                    "assessment": assessment.to_dict(),
                    "user_scores": user_scores,
                    "max_scores": max_scores_dict,
                    "feedback_list": []  # Will be generated on first results page visit
                },
                "summary": {
                    "total": total_competencies,
                    "proficient": proficient,
                    "needs_improvement": needs_improvement
                }
            }), 200

        except Exception as results_error:
            print(f"[submit_phase2_assessment] Error generating results: {str(results_error)}")
            traceback.print_exc()
            # Still return success for submission, but without results
            return jsonify({
                "success": True,
                "message": "Assessment submitted successfully, but results generation failed",
                "assessment_id": assessment_id
            }), 200

    except Exception as e:
        print(f"[submit_phase2_assessment] Error: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"success": False, "error": "An error occurred", "details": str(e)}), 500


@phase2_assessment_bp.route('/phase2/role-based-pathway/<int:organization_id>', methods=['GET'])
def get_role_based_pathway_analysis(organization_id):
    """
    Run complete role-based pathway analysis (8-step algorithm)

    This endpoint executes the complete algorithm including:
    - Steps 1-4: Data retrieval, analysis, aggregation, best-fit selection
    - Steps 5-8: Validation, strategic decisions, objectives, output

    Args:
        organization_id: Organization ID to analyze

    Returns:
        Complete analysis with:
        - Cross-strategy coverage
        - Strategy validation
        - Strategic decisions and recommendations
        - Learning objectives per strategy
    """
    try:
        from app.services.role_based_pathway_fixed import run_role_based_pathway_analysis_fixed

        print(f"[role-based-pathway] Starting analysis for organization {organization_id}")

        # Run the complete 8-step algorithm
        result = run_role_based_pathway_analysis_fixed(organization_id)

        # Check for errors
        if 'error' in result:
            print(f"[role-based-pathway] Error: {result['error']}")
            return jsonify({"success": False, "error": result['error']}), 400

        print(f"[role-based-pathway] Analysis complete for organization {organization_id}")
        print(f"[role-based-pathway] Validation status: {result['strategy_validation']['status']}")
        print(f"[role-based-pathway] Recommendation: {result['strategic_decisions']['overall_action']}")

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        print(f"[role-based-pathway] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "An error occurred", "details": str(e)}), 500


@phase2_assessment_bp.route('/assessment/<int:assessment_id>/submit', methods=['POST'])
def submit_assessment(assessment_id):
    """
    Submit competency scores for an assessment
    Replaces /submit_survey endpoint - uses assessment_id instead of username
    """
    data = request.get_json()
    try:
        # Fetch the assessment
        assessment = UserAssessment.query.get(assessment_id)
        if not assessment:
            return jsonify({"error": "Assessment not found"}), 404

        # Extract data
        selected_roles = data.get('selected_roles', [])
        competency_scores = data.get('competency_scores', [])
        tasks_responsibilities = data.get('tasks_responsibilities')

        # Update assessment with submitted data
        assessment.selected_roles = selected_roles
        assessment.tasks_responsibilities = tasks_responsibilities
        assessment.completed_at = datetime.utcnow()

        # Delete existing roles for this assessment if any
        UserRoleCluster.query.filter_by(assessment_id=assessment_id).delete()

        # Insert new roles with assessment_id
        # After migration 003: role_cluster_id now references organization_roles.id directly
        # Supports both standard-derived AND custom roles
        for role in selected_roles:
            org_role_id = role.get('role_id') or role.get('id')

            role_entry = UserRoleCluster(
                user_id=assessment.user_id,
                role_cluster_id=org_role_id,  # Now directly uses organization_roles.id
                assessment_id=assessment_id
            )
            db.session.add(role_entry)
            print(f"[submit_assessment] Added role {org_role_id} for assessment {assessment_id}")

        # Delete existing survey results for this assessment
        UserCompetencySurveyResults.query.filter_by(
            user_id=assessment.user_id,
            assessment_id=assessment_id
        ).delete()

        # Define valid competency scores (aligned with learning objectives templates)
        VALID_SCORES = [0, 1, 2, 4, 6]

        # Insert survey results with assessment_id
        for competency in competency_scores:
            # Extract score with proper fallback to 0 for None values
            score = competency.get('user_score') if competency.get('user_score') is not None else competency.get('score')
            if score is None:
                score = 0  # Default to 0 if no score provided

            # Validate score is one of the allowed values
            if score not in VALID_SCORES:
                return jsonify({
                    "error": f"Invalid competency score: {score}. Valid scores are {VALID_SCORES}.",
                    "competency_id": competency.get('competency_id') or competency.get('competencyId'),
                    "invalid_score": score
                }), 400

            survey = UserCompetencySurveyResults(
                user_id=assessment.user_id,
                organization_id=assessment.organization_id,
                competency_id=competency.get('competency_id') or competency.get('competencyId'),
                score=score,
                assessment_id=assessment_id
            )
            db.session.add(survey)

        db.session.commit()

        print(f"[submit_assessment] Assessment {assessment_id} completed for user {assessment.user_id}")

        return jsonify({
            'message': 'Assessment submitted successfully',
            'assessment_id': assessment_id,
            'assessment': assessment.to_dict()
        }), 200

    except Exception as e:
        print(f"[submit_assessment] Error: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@phase2_assessment_bp.route('/assessment/<int:assessment_id>/results', methods=['GET'])
def get_assessment_results(assessment_id):
    """
    Get results for a specific assessment
    Replaces /get_user_competency_results endpoint - uses assessment_id instead of username
    """
    try:
        # Fetch the assessment
        assessment = UserAssessment.query.get(assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404

        # Fetch competency survey results for this assessment
        user_competencies = UserCompetencySurveyResults.query.filter_by(
            assessment_id=assessment_id
        ).order_by(UserCompetencySurveyResults.competency_id).all()

        if not user_competencies:
            return jsonify({'error': 'No results found for this assessment'}), 404

        competencies = Competency.query.filter(
            Competency.id.in_([u.competency_id for u in user_competencies])
        ).order_by(Competency.id).all()

        competency_info_map = {comp.id: {'name': comp.competency_name, 'area': comp.competency_area} for comp in competencies}

        user_scores = [
            {
                'competency_id': u.competency_id,
                'score': u.score,
                'competency_name': competency_info_map[u.competency_id]['name'],
                'competency_area': competency_info_map[u.competency_id]['area']
            }
            for u in user_competencies
        ]

        # Fetch required competency scores based on survey type
        if assessment.survey_type == 'known_roles':
            # Use selected_roles from assessment (not UserRoleCluster)
            role_cluster_ids = assessment.selected_roles or []

            if not role_cluster_ids:
                print(f"[get_assessment_results] WARNING: No role IDs found in assessment.selected_roles")
                max_scores = []
            else:
                print(f"[get_assessment_results] Role-based pathway: role_ids={role_cluster_ids}, org_id={assessment.organization_id}")
                max_scores = db.session.query(
                    RoleCompetencyMatrix.competency_id,
                    db.func.max(RoleCompetencyMatrix.role_competency_value).label('max_score')
                ).filter(
                    RoleCompetencyMatrix.organization_id == assessment.organization_id,
                    RoleCompetencyMatrix.role_cluster_id.in_(role_cluster_ids)
                ).group_by(RoleCompetencyMatrix.competency_id).having(
                    db.func.max(RoleCompetencyMatrix.role_competency_value) > 0
                ).order_by(RoleCompetencyMatrix.competency_id).all()
                print(f"[get_assessment_results] Found {len(max_scores)} required competencies from role_competency_matrix")

        elif assessment.survey_type == 'unknown_roles':
            # For task-based, fetch from UnknownRoleCompetencyMatrix using task-based username
            task_based_username = assessment.tasks_responsibilities.get('username') if assessment.tasks_responsibilities else None

            if not task_based_username:
                print(f"[get_assessment_results] ERROR: No task-based username found for assessment {assessment_id}")
                return jsonify({'error': 'Task-based username not found'}), 500

            max_scores = db.session.query(
                UnknownRoleCompetencyMatrix.competency_id,
                UnknownRoleCompetencyMatrix.role_competency_value.label('max_score')
            ).filter(
                UnknownRoleCompetencyMatrix.organization_id == assessment.organization_id,
                UnknownRoleCompetencyMatrix.user_name == task_based_username,
                UnknownRoleCompetencyMatrix.role_competency_value > 0
            ).all()

        elif assessment.survey_type == 'all_roles':
            max_scores = db.session.query(
                RoleCompetencyMatrix.competency_id,
                db.func.avg(RoleCompetencyMatrix.role_competency_value).label('max_score')
            ).filter(
                RoleCompetencyMatrix.organization_id == assessment.organization_id
            ).group_by(RoleCompetencyMatrix.competency_id).having(
                db.func.avg(RoleCompetencyMatrix.role_competency_value) > 0
            ).order_by(RoleCompetencyMatrix.competency_id).all()
        else:
            max_scores = []

        max_scores_dict = [{'competency_id': m.competency_id, 'max_score': float(m.max_score)} for m in max_scores]

        # Filter user_scores to only include competencies with required level > 0
        required_competency_ids = {m['competency_id'] for m in max_scores_dict}
        user_scores = [score for score in user_scores if score['competency_id'] in required_competency_ids]

        # Check if feedback already exists for this assessment
        existing_feedbacks = UserCompetencySurveyFeedback.query.filter_by(
            assessment_id=assessment_id
        ).all()

        if existing_feedbacks:
            # Since feedback is stored as a JSONB array in a single row, extract it directly
            # The feedback column contains the complete feedback_list, not individual items
            if len(existing_feedbacks) == 1:
                feedback_list = existing_feedbacks[0].feedback
            else:
                # Fallback: flatten if multiple rows (shouldn't happen with current schema)
                feedback_list = []
                for fb in existing_feedbacks:
                    if isinstance(fb.feedback, list):
                        feedback_list.extend(fb.feedback)
                    else:
                        feedback_list.append(fb.feedback)
            print(f"[get_assessment_results] Using cached feedback for assessment {assessment_id}")
        else:
            # Generate feedback using LLM
            print(f"[get_assessment_results] No cached feedback found for assessment {assessment_id}, generating...")
            feedback_list = []

            try:
                # Helper function to map score to level
                def score_to_level(score):
                    score_map = {
                        0: '0',  # unwissend (unaware)
                        1: '1',  # kennen (know)
                        2: '2',  # verstehen (understand)
                        4: '3',  # anwenden (apply)
                        6: '4'   # beherrschen (master)
                    }
                    return score_map.get(score, '0')

                # Helper function to get level name
                def get_level_name(level):
                    level_names = {
                        '0': 'unwissend (unaware)',
                        '1': 'kennen (know)',
                        '2': 'verstehen (understand)',
                        '3': 'anwenden (apply)',
                        '4': 'beherrschen (master)'
                    }
                    return level_names.get(level, 'unknown')

                # Helper function to get indicators for a competency at a specific level
                def get_indicators_for_level(competency_id, level):
                    if level == '0':
                        return 'You are unaware or lack knowledge in this competency area'

                    indicators = CompetencyIndicator.query.filter_by(
                        competency_id=competency_id,
                        level=level
                    ).all()

                    if not indicators:
                        return f'No specific indicators available for level {level} ({get_level_name(level)})'

                    return '. '.join([ind.indicator_en for ind in indicators if ind.indicator_en])

                # Build max_scores_map for easy lookup
                max_scores_map = {m['competency_id']: m['max_score'] for m in max_scores_dict}

                # Build detailed competency results
                aggregated_results = defaultdict(list)

                for user_comp in user_competencies:
                    competency_id = user_comp.competency_id
                    user_score = user_comp.score

                    # Get competency info
                    competency_obj = Competency.query.get(competency_id)
                    if not competency_obj:
                        continue

                    competency_name = competency_obj.competency_name
                    competency_area = competency_obj.competency_area

                    # Map user score to level
                    user_level = score_to_level(user_score)
                    user_indicators = get_indicators_for_level(competency_id, user_level)

                    # Get required score and map to level
                    required_score = max_scores_map.get(competency_id, 0)

                    # Skip competencies with required level = 0
                    if required_score == 0:
                        continue

                    required_level = score_to_level(int(required_score)) if required_score else 'unwissend'
                    required_indicators = get_indicators_for_level(competency_id, required_level)

                    # Add to aggregated results
                    aggregated_results[competency_area].append({
                        "competency_name": competency_name,
                        "user_level": user_level,
                        "user_indicator": user_indicators,
                        "required_level": required_level,
                        "required_indicator": required_indicators
                    })

                print(f"[get_assessment_results] Aggregated {len(aggregated_results)} areas for feedback generation")

                # Generate feedback using LLM for each competency area
                for competency_area, competencies in aggregated_results.items():
                    print(f"[get_assessment_results] Generating feedback for {competency_area} with {len(competencies)} competencies")
                    feedback_json = generate_feedback_with_llm(competency_area, competencies)
                    feedback_list.append(feedback_json)

                # Save feedback to database with assessment_id
                new_feedback = UserCompetencySurveyFeedback(
                    user_id=assessment.user_id,
                    organization_id=assessment.organization_id,
                    feedback=feedback_list,
                    assessment_id=assessment_id
                )
                db.session.add(new_feedback)
                db.session.commit()
                print(f"[get_assessment_results] Generated and saved {len(feedback_list)} feedback items for assessment {assessment_id}")

            except Exception as e:
                db.session.rollback()
                print(f"[get_assessment_results] LLM feedback generation error: {str(e)}")
                traceback.print_exc()
                feedback_list = []  # Return empty feedback on error

        # Get full role objects for selected roles (for display in results)
        selected_roles_data = []
        if assessment.selected_roles and assessment.survey_type == 'known_roles':
            roles = OrganizationRoles.query.filter(
                OrganizationRoles.id.in_(assessment.selected_roles)
            ).all()
            selected_roles_data = [role.to_dict() for role in roles]
            print(f"[get_assessment_results] Fetched {len(selected_roles_data)} role objects for display")

        return jsonify({
            'assessment': assessment.to_dict(),
            'user_scores': user_scores,
            'max_scores': max_scores_dict,
            'feedback_list': feedback_list,
            'selected_roles_data': selected_roles_data  # Full role objects for frontend display
        }), 200

    except Exception as e:
        print(f"[get_assessment_results] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


@phase2_assessment_bp.route('/user/<int:user_id>/assessments', methods=['GET'])
def get_user_assessment_history(user_id):
    """
    Get all assessments for a user (assessment history)
    NEW endpoint - enables users to see their assessment history
    """
    try:
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Fetch all assessments for this user
        assessments = UserAssessment.query.filter_by(user_id=user_id).order_by(
            UserAssessment.created_at.desc()
        ).all()

        assessments_list = [assessment.to_dict() for assessment in assessments]

        print(f"[get_user_assessment_history] Found {len(assessments_list)} assessments for user {user.username}")

        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'assessment_count': len(assessments_list),
            'assessments': assessments_list
        }), 200

    except Exception as e:
        print(f"[get_user_assessment_history] Error: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


@phase2_assessment_bp.route('/latest_competency_overview', methods=['GET'])
@jwt_required()
def get_latest_competency_overview():
    """
    Get top 5 competencies from user's latest Phase 2 assessment,
    sorted by required level (importance) from role-competency matrix.

    Returns competencies with highest required levels to show users
    what's most critical for their SE role.
    """
    try:
        user_id = int(get_jwt_identity())

        # Get user's latest completed Phase 2 assessment
        latest_assessment = UserAssessment.query.filter_by(
            user_id=user_id
        ).order_by(UserAssessment.created_at.desc()).first()

        if not latest_assessment:
            return jsonify({
                'competencies': [],
                'message': 'No Phase 2 assessment completed yet'
            }), 200

        # Get user's competency scores for this assessment
        user_competencies = UserCompetencySurveyResults.query.filter_by(
            assessment_id=latest_assessment.id
        ).all()

        print(f"[latest_competency_overview] Assessment {latest_assessment.id}: survey_type={latest_assessment.survey_type}, user_competencies={len(user_competencies)}")

        if not user_competencies:
            return jsonify({
                'competencies': [],
                'message': 'No competency data found'
            }), 200

        # Get competency info
        competency_ids = [uc.competency_id for uc in user_competencies]
        competencies = Competency.query.filter(
            Competency.id.in_(competency_ids)
        ).all()

        competency_info_map = {
            comp.id: {
                'name': comp.competency_name,
                'area': comp.competency_area
            }
            for comp in competencies
        }

        # Get required competency levels based on survey type
        if latest_assessment.survey_type == 'known_roles':
            # Use selected_roles from assessment (not UserRoleCluster)
            role_cluster_ids = latest_assessment.selected_roles or []

            if not role_cluster_ids:
                print(f"[latest_competency_overview] WARNING: No role IDs in assessment.selected_roles")
                max_scores = []
            else:
                print(f"[latest_competency_overview] Role-based: role_ids={role_cluster_ids}")
                # Get max required level across all user's roles
                max_scores = db.session.query(
                    RoleCompetencyMatrix.competency_id,
                    db.func.max(RoleCompetencyMatrix.role_competency_value).label('required_level')
                ).filter(
                    RoleCompetencyMatrix.organization_id == latest_assessment.organization_id,
                    RoleCompetencyMatrix.role_cluster_id.in_(role_cluster_ids)
                ).group_by(RoleCompetencyMatrix.competency_id).having(
                    db.func.max(RoleCompetencyMatrix.role_competency_value) > 0
                ).all()

        elif latest_assessment.survey_type == 'unknown_roles':
            # Get from task-based role mapping - use task_based_username from tasks_responsibilities JSON
            task_based_username = latest_assessment.tasks_responsibilities.get('username') if latest_assessment.tasks_responsibilities else None

            if not task_based_username:
                print(f"[latest_competency_overview] ERROR: No task-based username found in assessment {latest_assessment.id}")
                max_scores = []
            else:
                print(f"[latest_competency_overview] Task-based: task_username={task_based_username}, org_id={latest_assessment.organization_id}")
                max_scores = db.session.query(
                    UnknownRoleCompetencyMatrix.competency_id,
                    UnknownRoleCompetencyMatrix.role_competency_value.label('required_level')
                ).filter(
                    UnknownRoleCompetencyMatrix.organization_id == latest_assessment.organization_id,
                    UnknownRoleCompetencyMatrix.user_name == task_based_username,
                    UnknownRoleCompetencyMatrix.role_competency_value > 0
                ).all()
                print(f"[latest_competency_overview] Found {len(max_scores)} required competencies from unknown_role_competency_matrix")

        elif latest_assessment.survey_type == 'all_roles':
            # Average across all roles
            max_scores = db.session.query(
                RoleCompetencyMatrix.competency_id,
                db.func.avg(RoleCompetencyMatrix.role_competency_value).label('required_level')
            ).filter(
                RoleCompetencyMatrix.organization_id == latest_assessment.organization_id
            ).group_by(RoleCompetencyMatrix.competency_id).having(
                db.func.avg(RoleCompetencyMatrix.role_competency_value) > 0
            ).all()
        else:
            max_scores = []

        # Build map of required levels
        required_level_map = {m.competency_id: float(m.required_level) for m in max_scores}

        # Build combined data: user score + required level + competency info
        combined_data = []
        for uc in user_competencies:
            competency_id = uc.competency_id

            # Only include competencies with required level > 0
            if competency_id not in required_level_map:
                continue

            if competency_id not in competency_info_map:
                continue

            combined_data.append({
                'competency_id': competency_id,
                'competency_name': competency_info_map[competency_id]['name'],
                'competency_area': competency_info_map[competency_id]['area'],
                'current_score': uc.score,
                'required_score': required_level_map[competency_id],
                'gap': required_level_map[competency_id] - uc.score
            })

        # Sort by required level (importance) descending, then by gap descending
        combined_data.sort(key=lambda x: (-x['required_score'], -x['gap']))

        # Take top 5
        top_5_competencies = combined_data[:5]

        print(f"[get_latest_competency_overview] Returning {len(top_5_competencies)} competencies for user {user_id}")

        return jsonify({
            'competencies': top_5_competencies,
            'assessment_id': latest_assessment.id,
            'completed_at': latest_assessment.created_at.isoformat() if latest_assessment.created_at else None,
            'total_competencies': len(combined_data)
        }), 200

    except Exception as e:
        print(f"[get_latest_competency_overview] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
