"""
Organization routes blueprint
Handles organization setup, verification, dashboard, and archetype management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import datetime
import sys
import json

from models import db, User, Organization, CompetencyAssessment

# Create blueprint
org_bp = Blueprint('organization', __name__)


def get_maturity_level_from_score(score):
    """Convert maturity score to level name"""
    if score >= 4.0:
        return 'Optimizing'
    elif score >= 3.0:
        return 'Defined'
    elif score >= 2.0:
        return 'Managed'
    elif score >= 1.0:
        return 'Performed'
    else:
        return 'Initial'


@org_bp.route('/organization/setup', methods=['POST'])
@jwt_required()
def organization_setup():
    """Update organization details (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)
        organization = Organization.query.get(user.organization_id)

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        data = request.get_json()

        # Update organization details (using Derik's field names)
        if 'name' in data:
            organization.organization_name = data['name']
        if 'size' in data:
            organization.size = data['size']

        db.session.commit()

        return jsonify({'organization': organization.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Organization setup error: {str(e)}")
        return jsonify({'error': 'Organization setup failed'}), 500


@org_bp.route('/organization/verify-code/<code>', methods=['GET'])
def verify_organization_code(code):
    """Verify organization code for employee registration"""
    try:
        organization = Organization.query.filter_by(organization_public_key=code.upper()).first()

        if organization:
            return jsonify({
                'valid': True,
                'organization_name': organization.organization_name
            }), 200
        else:
            return jsonify({
                'valid': False,
                'organization_name': None
            }), 200

    except Exception as e:
        current_app.logger.error(f"Organization verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500


@org_bp.route('/organization/dashboard', methods=['GET'])
def organization_dashboard():
    """Get organization dashboard data - supports both JWT and query param authentication"""
    print("=" * 80)
    print("ORGANIZATION DASHBOARD ENDPOINT HIT!")
    print("=" * 80)
    sys.stdout.flush()
    try:
        # Try to get user from JWT token
        auth_header = request.headers.get('Authorization')
        user_id = None
        user = None
        organization = None

        print(f"DEBUG: Authorization header: {auth_header}")
        sys.stdout.flush()

        if auth_header and auth_header.startswith('Bearer '):
            # Try JWT authentication
            try:
                from flask_jwt_extended import verify_jwt_in_request
                verify_jwt_in_request(optional=True)
                user_id = int(get_jwt_identity())
                if user_id:
                    claims = get_jwt()
                    print(f"DEBUG: User ID from JWT: {user_id}, Role: {claims.get('role')}")
                    current_app.logger.info(f"DEBUG: Organization dashboard requested by user {user_id}, role: {claims.get('role')}")
                    user = User.query.get(user_id)
                    if user:
                        organization = Organization.query.get(user.organization_id)
            except Exception as jwt_error:
                print(f"DEBUG: JWT verification failed: {jwt_error}")
                # Continue to query param fallback

        # If no JWT or JWT failed, try query parameters
        if not organization:
            org_code = request.args.get('code')
            org_id = request.args.get('id')

            print(f"DEBUG: Using query params - code: {org_code}, id: {org_id}")
            sys.stdout.flush()

            if org_code:
                organization = Organization.query.filter_by(organization_public_key=org_code).first()
            elif org_id:
                organization = Organization.query.get(int(org_id))

        current_app.logger.info(f"DEBUG: Found user: {user.username if user else 'None'}")
        current_app.logger.info(f"DEBUG: Organization ID: {user.organization_id if user else 'None'}")
        current_app.logger.info(f"DEBUG: Organization: {organization.organization_name if organization else 'None'}")

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        # Get organization statistics
        total_users = User.query.filter_by(organization_id=organization.id).count()

        # Get completed assessments - use proper join with select_from
        try:
            completed_assessments = db.session.query(CompetencyAssessment).select_from(User).join(
                CompetencyAssessment, User.id == CompetencyAssessment.user_id
            ).filter(
                User.organization_id == organization.id
            ).count()
        except Exception as e:
            print(f"DEBUG: Completed assessments query failed: {e}")
            completed_assessments = 0

        # REMOVED Phase 2A: MaturityAssessment model deleted - data now comes from questionnaire system
        # maturity_assessment = MaturityAssessment.query.filter_by(organization_id=organization.id).first()

        # BRIDGE: Check questionnaire system for Phase 1 assessment data
        questionnaire_maturity_data = None
        selected_archetype = organization.selected_archetype  # Default fallback

        try:
            # Import questionnaire models to check for completed assessments
            from models import QuestionnaireResponse, Questionnaire

            current_app.logger.info(f"DEBUG: Starting bridge check for organization {organization.id}")

            # Find admin users in this organization who completed Phase 1
            admin_users = User.query.filter_by(
                organization_id=organization.id,
                role='admin'
            ).all()

            current_app.logger.info(f"DEBUG: Found {len(admin_users)} admin users in organization")

            for admin_user in admin_users:
                current_app.logger.info(f"DEBUG: Checking admin user {admin_user.id} ({admin_user.username})")

                # Check for completed maturity assessment (questionnaire ID 1)
                # ORDER BY completed_at DESC to get the LATEST assessment
                maturity_response = QuestionnaireResponse.query.filter_by(
                    user_id=str(admin_user.id),
                    questionnaire_id=1,
                    status='completed'
                ).order_by(QuestionnaireResponse.completed_at.desc()).first()

                current_app.logger.info(f"DEBUG: Maturity response found: {maturity_response is not None}")
                if maturity_response:
                    current_app.logger.info(f"DEBUG: Maturity score: {maturity_response.total_score}/{maturity_response.max_possible_score} (completed: {maturity_response.completed_at})")

                # Check for completed archetype selection (questionnaire ID 2)
                # ORDER BY completed_at DESC to get the LATEST archetype selection
                archetype_response = QuestionnaireResponse.query.filter_by(
                    user_id=str(admin_user.id),
                    questionnaire_id=2,
                    status='completed'
                ).order_by(QuestionnaireResponse.completed_at.desc()).first()

                current_app.logger.info(f"DEBUG: Archetype response found: {archetype_response is not None}")

                if maturity_response and archetype_response:
                    current_app.logger.info(f"DEBUG: Found both responses! Creating bridge data...")

                    # CRITICAL: Extract computed archetype from questionnaire response (including secondary)
                    secondary_archetype = None
                    if archetype_response.computed_archetype:
                        try:
                            import json
                            computed_data = json.loads(archetype_response.computed_archetype)
                            selected_archetype = computed_data.get('name', selected_archetype)
                            secondary_archetype = computed_data.get('secondary')  # Extract secondary archetype
                            current_app.logger.info(f"DEBUG: Extracted archetype from computed data: {selected_archetype}, secondary: {secondary_archetype}")
                        except json.JSONDecodeError as e:
                            current_app.logger.error(f"DEBUG: Failed to parse computed_archetype JSON: {e}")
                    else:
                        current_app.logger.warning(f"DEBUG: No computed_archetype data found in archetype response")

                    # Create maturity assessment data from questionnaire responses
                    # Use archetype_response.completed_at for accurate timestamp
                    questionnaire_maturity_data = {
                        'id': maturity_response.uuid,
                        'organization_id': organization.id,
                        'overall_score': maturity_response.total_score / maturity_response.max_possible_score * 5.0 if maturity_response.max_possible_score > 0 else 0,
                        'scope_score': 2.5,  # Default - could be calculated from specific questions
                        'process_score': 2.5,  # Default - could be calculated from specific questions
                        'overall_maturity': get_maturity_level_from_score(maturity_response.total_score / maturity_response.max_possible_score * 5.0 if maturity_response.max_possible_score > 0 else 0),
                        'completed_at': archetype_response.completed_at.isoformat() if archetype_response.completed_at else None,  # Use archetype completion time
                        'responses': None,
                        'secondary_archetype': secondary_archetype  # Include secondary archetype
                    }
                    current_app.logger.info(f"DEBUG: Bridge data created with score: {questionnaire_maturity_data['overall_score']}, archetype: {selected_archetype}, secondary: {secondary_archetype}")
                    break  # Use first completed assessment found

        except ImportError as e:
            current_app.logger.warning(f"Could not import questionnaire models: {e}")
        except Exception as e:
            current_app.logger.error(f"Error checking questionnaire system: {e}")
            import traceback
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")

        # Use questionnaire data (MaturityAssessment model was removed in Phase 2A)
        final_maturity_assessment = questionnaire_maturity_data

        # Extract secondary archetype from questionnaire data if available
        final_secondary_archetype = questionnaire_maturity_data.get('secondary_archetype') if questionnaire_maturity_data else None

        # Log the timestamps being sent
        if final_maturity_assessment:
            current_app.logger.info(f"DEBUG: Sending completion timestamp: {final_maturity_assessment.get('completed_at')}")

        dashboard_data = {
            'organization': {
                **organization.to_dict(),
                'selected_archetype': selected_archetype,
                'secondary_archetype': final_secondary_archetype  # Include secondary archetype
            },
            'statistics': {
                'total_users': total_users,
                'completed_assessments': completed_assessments,
                'maturity_completed': final_maturity_assessment is not None
            },
            'maturity_assessment': final_maturity_assessment
        }

        return jsonify(dashboard_data), 200

    except Exception as e:
        current_app.logger.error(f"Organization dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to load dashboard'}), 500


@org_bp.route('/organization/archetype', methods=['PUT'])
@jwt_required()
def update_organization_archetype():
    """Update organization's selected archetype (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)
        organization = Organization.query.get(user.organization_id)

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        data = request.get_json()
        archetype = data.get('selected_archetype')

        if not archetype:
            return jsonify({'error': 'selected_archetype is required'}), 400

        organization.selected_archetype = archetype
        db.session.commit()

        return jsonify({'organization': organization.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update archetype error: {str(e)}")
        return jsonify({'error': 'Failed to update archetype'}), 500


@org_bp.route('/organization/phase1-complete', methods=['PUT'])
@jwt_required()
def complete_phase1():
    """Mark Phase 1 as complete for organization (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)
        organization = Organization.query.get(user.organization_id)

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        data = request.get_json()
        maturity_score = data.get('maturity_score')
        selected_archetype = data.get('selected_archetype')

        # Update organization with Phase 1 completion data
        if maturity_score is not None:
            organization.maturity_score = maturity_score
        if selected_archetype:
            organization.selected_archetype = selected_archetype

        organization.phase1_completed = True
        db.session.commit()

        current_app.logger.info(f"Phase 1 completed for organization {organization.id}")
        return jsonify({'organization': organization.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Phase 1 completion error: {str(e)}")
        return jsonify({'error': 'Failed to mark Phase 1 as complete'}), 500


@org_bp.route('/organization/phase2-complete', methods=['PUT'])
@jwt_required()
def complete_phase2():
    """Mark Phase 2 as complete for organization (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)
        organization = Organization.query.get(user.organization_id)

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        organization.phase2_completed = True
        db.session.commit()

        current_app.logger.info(f"Phase 2 completed for organization {organization.id}")
        return jsonify({'organization': organization.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Phase 2 completion error: {str(e)}")
        return jsonify({'error': 'Failed to mark Phase 2 as complete'}), 500


@org_bp.route('/organization/phase3-complete', methods=['PUT'])
@jwt_required()
def complete_phase3():
    """Mark Phase 3 as complete for organization (Admin only)"""
    try:
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        user = User.query.get(user_id)
        organization = Organization.query.get(user.organization_id)

        if not organization:
            return jsonify({'error': 'Organization not found'}), 404

        organization.phase3_completed = True
        db.session.commit()

        current_app.logger.info(f"Phase 3 completed for organization {organization.id}")
        return jsonify({'organization': organization.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Phase 3 completion error: {str(e)}")
        return jsonify({'error': 'Failed to mark Phase 3 as complete'}), 500
