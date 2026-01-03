"""
Phase 3: Macro Planning Routes Blueprint

API endpoints for Phase 3 "Macro Planning":
- Task 1: Training Structure Selection
- Task 2: Learning Format Selection with 3-Factor Suitability
- Task 3: LLM-Generated Timeline Planning

Based on Phase3_Macro_Planning_Specification_v3.2.md
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback

from models import db

# Create blueprint
phase3_planning_bp = Blueprint('phase3_planning', __name__)


# ==============================================================================
# HELPER: Get Service Instance
# ==============================================================================

def _get_service():
    """Get Phase 3 Planning Service instance"""
    from app.services.phase3_planning_service import Phase3PlanningService
    return Phase3PlanningService(db.session)


# ==============================================================================
# TASK 1: Training Structure Selection
# ==============================================================================

@phase3_planning_bp.route('/phase3/config/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_phase3_config(organization_id):
    """
    Get Phase 3 configuration for an organization.

    Returns config including selected view, progress, and scaling info.
    """
    try:
        service = _get_service()

        config = service.get_phase3_config(organization_id)
        available_views = service.get_available_views(organization_id)

        return jsonify({
            'success': True,
            'config': config,
            'available_views': available_views
        })

    except Exception as e:
        current_app.logger.error(f"Error getting Phase 3 config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/training-structure/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_training_structure(organization_id):
    """
    Get training structure options for Task 1.

    Returns available views based on organization maturity and current selection.
    """
    try:
        service = _get_service()

        config = service.get_phase3_config(organization_id)
        available_views = service.get_available_views(organization_id)

        return jsonify({
            'success': True,
            'selected_view': config.get('selected_view'),
            'task_completed': config.get('task1_completed', False),
            **available_views
        })

    except Exception as e:
        current_app.logger.error(f"Error getting training structure: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/training-structure/<int:organization_id>', methods=['POST'])
@jwt_required()
def set_training_structure(organization_id):
    """
    Set training structure view for Task 1.

    Request Body:
        {"selected_view": "competency_level" | "role_clustered"}
    """
    try:
        data = request.get_json()
        selected_view = data.get('selected_view')

        if not selected_view:
            return jsonify({
                'success': False,
                'error': 'selected_view is required'
            }), 400

        service = _get_service()
        result = service.set_training_structure(organization_id, selected_view)

        return jsonify(result)

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error setting training structure: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# TASK 2: Learning Format Selection
# ==============================================================================

@phase3_planning_bp.route('/phase3/learning-formats', methods=['GET'])
@jwt_required()
def get_learning_formats():
    """
    Get all 10 learning formats with their properties.

    Returns complete format definitions including participant ranges,
    max achievable levels, and effort ratings.
    """
    try:
        service = _get_service()
        formats = service.get_learning_formats()

        return jsonify({
            'success': True,
            'formats': formats,
            'total': len(formats)
        })

    except Exception as e:
        current_app.logger.error(f"Error getting learning formats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/training-modules/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_training_modules(organization_id):
    """
    Get training modules from Phase 2 Learning Objectives.

    Returns modules with gap data, participant estimates, and existing selections.
    """
    try:
        service = _get_service()
        result = service.get_training_modules(organization_id)

        if result.get('error'):
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400

        return jsonify({
            'success': True,
            **result
        })

    except Exception as e:
        current_app.logger.error(f"Error getting training modules: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/evaluate-format', methods=['POST'])
@jwt_required()
def evaluate_format():
    """
    Evaluate a learning format's suitability for a training module.

    Request Body:
        {
            "organization_id": 28,
            "competency_id": 14,
            "target_level": 2,
            "format_id": 1,
            "participant_count": 45
        }

    Returns 3-factor suitability feedback (green/yellow/red for each).
    """
    try:
        data = request.get_json()

        required = ['organization_id', 'competency_id', 'target_level', 'format_id', 'participant_count']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {missing}"
            }), 400

        service = _get_service()
        result = service.evaluate_format_suitability(
            organization_id=data['organization_id'],
            competency_id=data['competency_id'],
            target_level=data['target_level'],
            format_id=data['format_id'],
            participant_count=data['participant_count']
        )

        return jsonify({
            'success': True,
            **result
        })

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error evaluating format: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/select-format', methods=['POST'])
@jwt_required()
def select_format():
    """
    Save format selection for a training module.

    Request Body:
        {
            "organization_id": 28,
            "competency_id": 14,
            "target_level": 2,
            "pmt_type": "combined" | "method" | "tool",
            "format_id": 1,
            "estimated_participants": 45,
            "confirmed": true
        }
    """
    try:
        data = request.get_json()

        required = ['organization_id', 'competency_id', 'target_level', 'pmt_type', 'format_id']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {missing}"
            }), 400

        service = _get_service()

        # First evaluate suitability
        suitability = service.evaluate_format_suitability(
            organization_id=data['organization_id'],
            competency_id=data['competency_id'],
            target_level=data['target_level'],
            format_id=data['format_id'],
            participant_count=data.get('estimated_participants', 0)
        )

        # Save selection
        result = service.save_format_selection(
            organization_id=data['organization_id'],
            competency_id=data['competency_id'],
            target_level=data['target_level'],
            pmt_type=data['pmt_type'],
            format_id=data['format_id'],
            suitability=suitability,
            estimated_participants=data.get('estimated_participants', 0),
            confirmed=data.get('confirmed', False)
        )

        return jsonify({
            'success': True,
            'suitability': suitability
        })

    except Exception as e:
        current_app.logger.error(f"Error saving format selection: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# TASK 3: Timeline Planning
# ==============================================================================

@phase3_planning_bp.route('/phase3/generate-timeline', methods=['POST'])
@jwt_required()
def generate_timeline():
    """
    Generate timeline milestones using LLM.

    Request Body:
        {"organization_id": 28}

    Returns 5 milestones with estimated dates.
    """
    try:
        data = request.get_json()
        organization_id = data.get('organization_id')

        if not organization_id:
            return jsonify({
                'success': False,
                'error': 'organization_id is required'
            }), 400

        service = _get_service()
        result = service.generate_timeline(organization_id)

        if not result.get('success'):
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Error generating timeline: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/timeline/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_timeline(organization_id):
    """
    Get stored timeline milestones for an organization.
    """
    try:
        service = _get_service()
        result = service.get_timeline(organization_id)

        return jsonify({
            'success': True,
            **result
        })

    except Exception as e:
        current_app.logger.error(f"Error getting timeline: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# Phase 3 Output/Summary
# ==============================================================================

@phase3_planning_bp.route('/phase3/output/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_phase3_output(organization_id):
    """
    Get complete Phase 3 output summary.

    Returns all Phase 3 data including config, modules, timeline, and summary stats.
    """
    try:
        service = _get_service()
        result = service.get_phase3_output(organization_id)

        return jsonify({
            'success': True,
            **result
        })

    except Exception as e:
        current_app.logger.error(f"Error getting Phase 3 output: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==============================================================================
# Training Program Clusters (for Role-Clustered View)
# ==============================================================================

@phase3_planning_bp.route('/phase3/training-clusters', methods=['GET'])
@jwt_required()
def get_training_clusters():
    """
    Get all 6 Training Program Clusters.

    Used for Role-Clustered training view.
    """
    try:
        result = db.session.execute(
            db.text("""
                SELECT id, cluster_key, cluster_name, training_program_name,
                       description, typical_org_roles
                FROM training_program_cluster
                ORDER BY display_order
            """)
        )

        clusters = []
        for row in result:
            clusters.append({
                'id': row.id,
                'cluster_key': row.cluster_key,
                'cluster_name': row.cluster_name,
                'training_program_name': row.training_program_name,
                'description': row.description,
                'typical_org_roles': row.typical_org_roles
            })

        return jsonify({
            'success': True,
            'clusters': clusters,
            'total': len(clusters)
        })

    except Exception as e:
        current_app.logger.error(f"Error getting training clusters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@phase3_planning_bp.route('/phase3/training-clusters/<int:organization_id>/distribution', methods=['GET'])
@jwt_required()
def get_training_cluster_distribution(organization_id):
    """
    Get distribution of organization roles across Training Program Clusters.

    Used for Role-Clustered training view.
    Note: Uses organization_roles table (not organization_role_mappings)
    """
    try:
        result = db.session.execute(
            db.text("""
                SELECT tpc.id, tpc.cluster_name, tpc.training_program_name,
                       COUNT(orr.id) as role_count,
                       ARRAY_AGG(orr.role_name) as role_titles
                FROM training_program_cluster tpc
                LEFT JOIN organization_roles orr
                    ON orr.training_program_cluster_id = tpc.id
                    AND orr.organization_id = :org_id
                GROUP BY tpc.id, tpc.cluster_name, tpc.training_program_name
                ORDER BY tpc.display_order
            """),
            {'org_id': organization_id}
        )

        distribution = []
        for row in result:
            distribution.append({
                'cluster_id': row.id,
                'cluster_name': row.cluster_name,
                'training_program_name': row.training_program_name,
                'role_count': row.role_count,
                'role_titles': [r for r in row.role_titles if r] if row.role_titles else []
            })

        return jsonify({
            'success': True,
            'distribution': distribution
        })

    except Exception as e:
        current_app.logger.error(f"Error getting cluster distribution: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
