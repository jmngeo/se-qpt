"""
Phase 1 Strategy Selection Routes
==================================
Handles target group size definition and learning strategy selection for Phase 1 Task 3.

Routes:
- GET  /phase1/target-group/<org_id>        - Get target group size for organization
- POST /phase1/target-group/save            - Save target group size information
- GET  /phase1/strategies/definitions       - Get all 7 SE training strategy definitions
- POST /phase1/strategies/calculate         - Calculate recommended strategies
- GET  /phase1/strategies/<org_id>/latest   - Get latest strategy selection
- POST /phase1/strategies/save              - Save selected strategies
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import datetime
import json
from sqlalchemy import text

from models import db, User, Organization, LearningStrategy, PhaseQuestionnaireResponse
from app.services.strategy_selection_engine import StrategySelectionEngine, SE_TRAINING_STRATEGIES

# Create blueprint
phase1_strategies_bp = Blueprint('phase1_strategies', __name__)


@phase1_strategies_bp.route('/phase1/target-group/<int:org_id>', methods=['GET'])
def get_target_group(org_id):
    """Get target group size for an organization"""
    try:
        # Verify organization exists
        org = Organization.query.get(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        # Get latest target group data
        target_group = PhaseQuestionnaireResponse.query.filter_by(
            organization_id=org_id,
            questionnaire_type='target_group',
            phase=1
        ).order_by(PhaseQuestionnaireResponse.completed_at.desc()).first()

        if not target_group:
            return jsonify({
                'success': True,
                'data': None
            }), 200

        # Get the response data
        response_data = target_group.get_responses()

        return jsonify({
            'success': True,
            'data': response_data,
            'completed_at': target_group.completed_at.isoformat() if target_group.completed_at else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting target group: {str(e)}")
        return jsonify({'error': 'Failed to get target group'}), 500


@phase1_strategies_bp.route('/phase1/target-group/save', methods=['POST'])
def save_target_group():
    """Save target group size information"""
    try:
        data = request.get_json()

        org_id = data.get('org_id')
        size_data = data.get('sizeData', {})

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

        # Create new target group data
        target_group = PhaseQuestionnaireResponse(
            organization_id=org_id,
            user_id=user_id,
            questionnaire_type='target_group',
            phase=1
        )
        target_group.set_responses(size_data)

        db.session.add(target_group)
        db.session.commit()

        return jsonify({
            'success': True,
            'id': target_group.id,
            'message': 'Target group saved successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving target group: {str(e)}")
        return jsonify({'error': 'Failed to save target group'}), 500


@phase1_strategies_bp.route('/phase1/strategies/definitions', methods=['GET'])
def get_strategy_definitions():
    """Get all 7 SE training strategy definitions"""
    try:
        return jsonify({
            'success': True,
            'strategies': SE_TRAINING_STRATEGIES
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting strategy definitions: {str(e)}")
        return jsonify({'error': 'Failed to get strategy definitions'}), 500


@phase1_strategies_bp.route('/phase1/strategies/calculate', methods=['POST'])
def calculate_strategies():
    """Calculate recommended strategies based on maturity and target group"""
    try:
        data = request.get_json()
        maturity_data = data.get('maturityData', {})
        target_group_data = data.get('targetGroupData', {})

        if not maturity_data or not target_group_data:
            return jsonify({'error': 'maturityData and targetGroupData are required'}), 400

        # Run strategy selection engine
        engine = StrategySelectionEngine(maturity_data, target_group_data)
        results = engine.select_strategies()

        return jsonify({
            'success': True,
            'strategies': results['strategies'],
            'decisionPath': results['decisionPath'],
            'reasoning': results['reasoning'],
            'requiresUserChoice': results['requiresUserChoice']
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error calculating strategies: {str(e)}")
        return jsonify({'error': f'Failed to calculate strategies: {str(e)}'}), 500


@phase1_strategies_bp.route('/phase1/strategies/<int:org_id>/latest', methods=['GET'])
def get_latest_strategies(org_id):
    """Get latest strategy selection for an organization"""
    try:
        # Verify organization exists
        org = Organization.query.get(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        # Get latest strategy selection
        strategies = PhaseQuestionnaireResponse.query.filter_by(
            organization_id=org_id,
            questionnaire_type='strategies',
            phase=1
        ).order_by(PhaseQuestionnaireResponse.completed_at.desc()).first()

        if not strategies:
            return jsonify({
                'success': True,
                'data': None,
                'count': 0
            }), 200

        # Parse the response
        response_data = strategies.get_responses()
        strategies_list = response_data.get('strategies', []) if isinstance(response_data, dict) else []

        return jsonify({
            'success': True,
            'data': strategies_list,
            'count': len(strategies_list),
            'userPreference': response_data.get('userPreference') if isinstance(response_data, dict) else None,
            'decisionPath': response_data.get('decisionPath') if isinstance(response_data, dict) else None,
            'reasoning': response_data.get('reasoning') if isinstance(response_data, dict) else None,
            'completed_at': strategies.completed_at.isoformat() if strategies.completed_at else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting strategies: {str(e)}")
        return jsonify({'error': 'Failed to get strategies'}), 500


@phase1_strategies_bp.route('/phase1/strategies/save', methods=['POST'])
def save_strategies():
    """Save selected strategies"""
    try:
        data = request.get_json()

        org_id = data.get('orgId')
        strategies = data.get('strategies', [])
        decision_path = data.get('decisionPath', [])

        if not org_id:
            return jsonify({'error': 'orgId is required'}), 400

        # Get user ID from JWT if available
        user_id = 1  # Default fallback
        try:
            verify_jwt_in_request(optional=True)
            jwt_user_id = get_jwt_identity()
            if jwt_user_id:
                user_id = int(jwt_user_id) if isinstance(jwt_user_id, str) else jwt_user_id
        except Exception:
            pass  # Use default user_id

        # Create new strategy selection in PhaseQuestionnaireResponse
        strategy_data = PhaseQuestionnaireResponse(
            organization_id=org_id,
            user_id=user_id,
            questionnaire_type='strategies',
            phase=1
        )
        strategy_data.set_responses({
            'strategies': strategies,
            'decision_path': decision_path
        })

        db.session.add(strategy_data)

        # CRITICAL FIX: Sync strategies to learning_strategy table for Phase 2
        # Clear existing selected strategies for this organization
        LearningStrategy.query.filter_by(organization_id=org_id).update({'selected': False})

        # Map of strategy keys to display names
        strategy_names = {
            'foundation_workshop': 'Foundation Workshop',
            'advanced_training': 'Advanced Training',
            'needs_based_project': 'Needs-based Project-oriented Training',
            'continuous_support': 'Continuous Support',
            'se_for_managers': 'SE for Managers',
            'common_understanding': 'Common Basic Understanding'
        }
        # Helper: Map strategy names to strategy_template IDs for LO generation
        def find_strategy_template_id(display_name):
            name_lower = display_name.lower().strip()
            template_mappings = {
                'common basic understanding': 1, 'common understanding': 1,
                'se for managers': 2,
                'orientation in pilot project': 3, 'pilot project': 3, 'foundation workshop': 3,
                'needs-based, project-oriented training': 4, 'needs-based project-oriented training': 4, 'advanced training': 4,
                'continuous support': 5,
                'train the trainer': 6, 'train the se-trainer': 6,
                'certification': 7
            }
            if name_lower in template_mappings:
                return template_mappings[name_lower]
            for pattern, tid in template_mappings.items():
                if pattern in name_lower or name_lower in pattern:
                    return tid
            return None


        # Priority mapping from Phase 1 to numeric priority
        priority_map = {
            'PRIMARY': 1,
            'SECONDARY': 2,
            'SUPPLEMENTARY': 3
        }

        # Add or update selected strategies
        for strategy_item in strategies:
            strategy_key = strategy_item.get('strategy')
            strategy_display_name = strategy_item.get('strategyName') or strategy_names.get(strategy_key, strategy_key)
            priority_str = strategy_item.get('priority', 'SECONDARY')
            priority_num = priority_map.get(priority_str, 2)
            reason = strategy_item.get('reason', '')

            # Get strategy_template_id for LO generation
            template_id = find_strategy_template_id(strategy_display_name)
            # Try to find existing strategy
            existing = LearningStrategy.query.filter_by(
                organization_id=org_id,
                strategy_name=strategy_display_name
            ).first()

            if existing:
                # Update existing
                existing.selected = True
                existing.priority = priority_num
                existing.strategy_description = reason
                existing.strategy_template_id = template_id
            else:
                # Create new
                new_strategy = LearningStrategy(
                    organization_id=org_id,
                    strategy_name=strategy_display_name,
                    strategy_description=reason,
                    selected=True,
                    priority=priority_num,
                    strategy_template_id=template_id
                )
                db.session.add(new_strategy)

        db.session.commit()

        current_app.logger.info(f"[OK] Saved {len(strategies)} strategies for org {org_id} to both tables")

        return jsonify({
            'success': True,
            'id': strategy_data.id,
            'message': 'Strategies saved successfully',
            'strategies': strategies,
            'count': len(strategies)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Failed to save strategies: {str(e)}")
        return jsonify({'error': 'Failed to save strategies'}), 500
