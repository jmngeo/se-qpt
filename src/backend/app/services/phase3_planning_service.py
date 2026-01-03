"""
Phase 3: Macro Planning Service

Handles all business logic for Phase 3 "Macro Planning":
- Task 1: Training Structure Selection (competency_level vs role_clustered)
- Task 2: Learning Format Selection with 3-Factor Suitability Feedback
- Task 3: LLM-Generated Timeline Planning

Based on Phase3_Macro_Planning_Specification_v3.2.md
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from sqlalchemy import text
from flask import current_app


class Phase3PlanningService:
    """Service for Phase 3 Macro Planning operations"""

    def __init__(self, db_session):
        """Initialize the service with database session"""
        self.db = db_session
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    # =========================================================================
    # TASK 1: Training Structure Selection
    # =========================================================================

    def get_phase3_config(self, organization_id: int) -> Dict[str, Any]:
        """
        Get Phase 3 configuration for an organization.
        Creates default config if not exists.
        """
        result = self.db.execute(
            text("""
                SELECT id, selected_view, actual_assessed_users, target_group_size,
                       scaling_factor, task1_completed, task2_completed, task3_completed
                FROM phase3_config
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
        ).fetchone()

        if result:
            return {
                'id': result.id,
                'selected_view': result.selected_view,
                'actual_assessed_users': result.actual_assessed_users,
                'target_group_size': result.target_group_size,
                'scaling_factor': float(result.scaling_factor) if result.scaling_factor else None,
                'task1_completed': result.task1_completed,
                'task2_completed': result.task2_completed,
                'task3_completed': result.task3_completed
            }

        # Create default config
        self.db.execute(
            text("""
                INSERT INTO phase3_config (organization_id, selected_view)
                VALUES (:org_id, 'competency_level')
                ON CONFLICT (organization_id) DO NOTHING
            """),
            {'org_id': organization_id}
        )
        self.db.commit()

        return {
            'id': None,
            'selected_view': 'competency_level',
            'actual_assessed_users': None,
            'target_group_size': None,
            'scaling_factor': None,
            'task1_completed': False,
            'task2_completed': False,
            'task3_completed': False
        }

    def get_available_views(self, organization_id: int) -> Dict[str, Any]:
        """
        Determine which training views are available based on organization maturity.

        Returns:
            {
                'available_views': ['competency_level'] or ['competency_level', 'role_clustered'],
                'default_view': 'competency_level',
                'show_view_selector': True/False,
                'maturity_level': 3,
                'has_roles': True/False
            }
        """
        # Get organization maturity
        org = self.db.execute(
            text("SELECT maturity_score FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()

        maturity = org.maturity_score if org else 1

        # Check if organization has defined roles with Training Program Cluster assignments
        roles_count = self.db.execute(
            text("""
                SELECT COUNT(*) FROM organization_roles
                WHERE organization_id = :org_id
                  AND training_program_cluster_id IS NOT NULL
            """),
            {'org_id': organization_id}
        ).scalar()

        has_roles = roles_count > 0

        # Low maturity or no roles: Only Competency-Level view
        if maturity <= 2 or not has_roles:
            return {
                'available_views': ['competency_level'],
                'default_view': 'competency_level',
                'show_view_selector': False,
                'maturity_level': maturity,
                'has_roles': has_roles
            }

        # High maturity with roles: Both views available
        return {
            'available_views': ['competency_level', 'role_clustered'],
            'default_view': 'competency_level',
            'show_view_selector': True,
            'maturity_level': maturity,
            'has_roles': has_roles
        }

    def set_training_structure(self, organization_id: int, selected_view: str) -> Dict[str, Any]:
        """Set the training structure view for Phase 3"""
        if selected_view not in ['competency_level', 'role_clustered']:
            raise ValueError(f"Invalid view: {selected_view}")

        self.db.execute(
            text("""
                INSERT INTO phase3_config (organization_id, selected_view, task1_completed)
                VALUES (:org_id, :view, true)
                ON CONFLICT (organization_id) DO UPDATE SET
                    selected_view = :view,
                    task1_completed = true,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {'org_id': organization_id, 'view': selected_view}
        )
        self.db.commit()

        return {'success': True, 'selected_view': selected_view}

    # =========================================================================
    # TASK 2: Learning Format Selection
    # =========================================================================

    def get_learning_formats(self) -> List[Dict[str, Any]]:
        """Get all 10 learning formats with their properties"""
        result = self.db.execute(
            text("""
                SELECT id, format_key, format_name, short_name, description, icon,
                       mode_of_delivery, communication_type, collaboration_type, learning_type,
                       participant_min, participant_max, max_level_achievable,
                       is_e_learning, is_passive, is_recommended,
                       effort_content_creation, effort_content_update, effort_per_training,
                       advantages, disadvantages, display_order
                FROM learning_format
                ORDER BY display_order
            """)
        )

        formats = []
        for row in result:
            formats.append({
                'id': row.id,
                'format_key': row.format_key,
                'format_name': row.format_name,
                'short_name': row.short_name,
                'description': row.description,
                'icon': row.icon,
                'mode_of_delivery': row.mode_of_delivery,
                'communication_type': row.communication_type,
                'collaboration_type': row.collaboration_type,
                'learning_type': row.learning_type,
                'participant_min': row.participant_min,
                'participant_max': row.participant_max,
                'max_level_achievable': row.max_level_achievable,
                'is_e_learning': row.is_e_learning,
                'is_passive': row.is_passive,
                'is_recommended': row.is_recommended,
                'effort_content_creation': row.effort_content_creation,
                'effort_content_update': row.effort_content_update,
                'effort_per_training': row.effort_per_training,
                'advantages': json.loads(row.advantages) if row.advantages else [],
                'disadvantages': json.loads(row.disadvantages) if row.disadvantages else []
            })

        return formats

    def get_training_modules(self, organization_id: int) -> Dict[str, Any]:
        """
        Get training modules from Phase 2 Learning Objectives.

        Returns modules with gap data, participant counts, and any existing format selections.
        """
        # Get organization info for scaling
        org_info = self._get_organization_scaling_info(organization_id)

        # Get learning objectives with gaps from Phase 2
        lo_result = self.db.execute(
            text("""
                SELECT objectives_data
                FROM generated_learning_objectives
                WHERE organization_id = :org_id
                ORDER BY generated_at DESC
                LIMIT 1
            """),
            {'org_id': organization_id}
        ).fetchone()

        if not lo_result or not lo_result.objectives_data:
            return {
                'modules': [],
                'scaling_info': org_info,
                'error': 'No learning objectives found. Complete Phase 2 first.'
            }

        objectives_data = lo_result.objectives_data
        if isinstance(objectives_data, str):
            objectives_data = json.loads(objectives_data)

        # Get existing format selections
        existing_selections = self._get_existing_selections(organization_id)

        # Extract modules from learning objectives
        modules = self._extract_modules_from_los(
            objectives_data,
            organization_id,
            org_info,
            existing_selections
        )

        return {
            'modules': modules,
            'scaling_info': org_info,
            'total_modules': len(modules),
            'configured_modules': sum(1 for m in modules if m.get('selected_format_id'))
        }

    def _get_organization_scaling_info(self, organization_id: int) -> Dict[str, Any]:
        """Get participant scaling information for an organization"""
        # Get target group size from Phase 1 questionnaire
        target_result = self.db.execute(
            text("""
                SELECT responses
                FROM phase_questionnaire_responses
                WHERE organization_id = :org_id
                  AND questionnaire_type = 'target_group'
                ORDER BY completed_at DESC
                LIMIT 1
            """),
            {'org_id': organization_id}
        ).fetchone()

        target_group_size = 100  # Default
        if target_result and target_result.responses:
            data = target_result.responses
            if isinstance(data, str):
                data = json.loads(data)
            target_group_size = data.get('value', 100)

        # Get actual assessed users count
        assessed_count = self.db.execute(
            text("""
                SELECT COUNT(DISTINCT user_id)
                FROM user_se_competency_survey_results
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
        ).scalar() or 1

        scaling_factor = target_group_size / max(assessed_count, 1)

        return {
            'target_group_size': target_group_size,
            'actual_assessed_users': assessed_count,
            'scaling_factor': round(scaling_factor, 2)
        }

    def _get_existing_selections(self, organization_id: int) -> Dict[str, Dict]:
        """Get existing format selections for an organization"""
        result = self.db.execute(
            text("""
                SELECT competency_id, target_level, pmt_type, selected_format_id,
                       estimated_participants, confirmed,
                       suitability_factor1_status, suitability_factor2_status, suitability_factor3_status
                FROM phase3_training_module
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
        )

        selections = {}
        for row in result:
            key = f"{row.competency_id}_{row.target_level}_{row.pmt_type}"
            selections[key] = {
                'selected_format_id': row.selected_format_id,
                'estimated_participants': row.estimated_participants,
                'confirmed': row.confirmed,
                'suitability': {
                    'factor1_status': row.suitability_factor1_status,
                    'factor2_status': row.suitability_factor2_status,
                    'factor3_status': row.suitability_factor3_status
                }
            }

        return selections

    def _extract_modules_from_los(
        self,
        objectives_data: Dict,
        organization_id: int,
        scaling_info: Dict,
        existing_selections: Dict
    ) -> List[Dict[str, Any]]:
        """Extract training modules from learning objectives data"""
        modules = []

        # Get data section
        data = objectives_data.get('data', objectives_data)
        main_pyramid = data.get('main_pyramid', {})
        levels = main_pyramid.get('levels', {})

        # Get competency lookup
        competencies = self._get_competency_lookup()

        for level_key, level_data in levels.items():
            target_level = int(level_key)
            comps = level_data.get('competencies', [])

            for comp in comps:
                # Skip if no gap
                if comp.get('status') != 'gap':
                    continue

                competency_id = comp.get('competency_id')
                competency_name = comp.get('competency_name', competencies.get(competency_id, 'Unknown'))

                # Check if PMT breakdown exists
                lo_data = comp.get('learning_objective', {})
                has_pmt = lo_data.get('has_pmt_breakdown', False)

                # Get users with gap (for participant estimation)
                gap_data = comp.get('gap_data', {})
                users_with_gap = gap_data.get('users_with_gap', 1)
                roles_needing = gap_data.get('roles_needing_training', [])

                # Calculate estimated participants
                estimated_participants = int(users_with_gap * scaling_info['scaling_factor'])

                if has_pmt:
                    # Create separate modules for Method and Tool
                    for pmt_type in ['method', 'tool']:
                        key = f"{competency_id}_{target_level}_{pmt_type}"
                        selection = existing_selections.get(key, {})

                        modules.append({
                            'competency_id': competency_id,
                            'competency_name': competency_name,
                            'target_level': target_level,
                            'pmt_type': pmt_type,
                            'module_name': f"{competency_name} - Level {target_level} - {pmt_type.title()}",
                            'users_with_gap': users_with_gap,
                            'estimated_participants': estimated_participants,
                            'roles_needing_training': roles_needing,
                            'selected_format_id': selection.get('selected_format_id'),
                            'confirmed': selection.get('confirmed', False),
                            'suitability': selection.get('suitability')
                        })
                else:
                    # Single combined module
                    key = f"{competency_id}_{target_level}_combined"
                    selection = existing_selections.get(key, {})

                    modules.append({
                        'competency_id': competency_id,
                        'competency_name': competency_name,
                        'target_level': target_level,
                        'pmt_type': 'combined',
                        'module_name': f"{competency_name} - Level {target_level}",
                        'users_with_gap': users_with_gap,
                        'estimated_participants': estimated_participants,
                        'roles_needing_training': roles_needing,
                        'selected_format_id': selection.get('selected_format_id'),
                        'confirmed': selection.get('confirmed', False),
                        'suitability': selection.get('suitability')
                    })

        return modules

    def _get_competency_lookup(self) -> Dict[int, str]:
        """Get competency ID to name mapping"""
        result = self.db.execute(
            text("SELECT id, competency_name FROM competency")
        )
        return {row.id: row.competency_name for row in result}

    def evaluate_format_suitability(
        self,
        organization_id: int,
        competency_id: int,
        target_level: int,
        format_id: int,
        participant_count: int
    ) -> Dict[str, Any]:
        """
        Evaluate a learning format's suitability for a training module.

        Returns 3-factor suitability feedback:
        - Factor 1: Participant count appropriateness
        - Factor 2: Level achievable by format
        - Factor 3: Strategy consistency

        Each factor has: status (green/yellow/red), message
        """
        # Get format info
        format_info = self.db.execute(
            text("""
                SELECT format_key, format_name, participant_min, participant_max, max_level_achievable
                FROM learning_format
                WHERE id = :fmt_id
            """),
            {'fmt_id': format_id}
        ).fetchone()

        if not format_info:
            raise ValueError(f"Format not found: {format_id}")

        # Get organization's selected strategy
        strategy = self.db.execute(
            text("""
                SELECT st.id, st.strategy_name
                FROM organization o
                JOIN strategy_template st ON st.strategy_name = o.selected_archetype
                WHERE o.id = :org_id
            """),
            {'org_id': organization_id}
        ).fetchone()

        strategy_id = strategy.id if strategy else 1

        # Factor 1: Participant Count
        factor1 = self._evaluate_participant_factor(
            participant_count,
            format_info.participant_min,
            format_info.participant_max,
            format_info.format_name
        )

        # Factor 2: Level Achievable
        factor2 = self._evaluate_level_factor(
            competency_id,
            target_level,
            format_id
        )

        # Factor 3: Strategy Consistency
        factor3 = self._evaluate_strategy_factor(
            strategy_id,
            format_id
        )

        return {
            'format_id': format_id,
            'format_name': format_info.format_name,
            'factors': {
                'factor1': factor1,
                'factor2': factor2,
                'factor3': factor3
            },
            'overall_status': self._get_overall_status([factor1, factor2, factor3])
        }

    def _evaluate_participant_factor(
        self,
        participant_count: int,
        min_participants: int,
        max_participants: Optional[int],
        format_name: str
    ) -> Dict[str, str]:
        """Evaluate Factor 1: Participant count appropriateness"""
        max_val = max_participants or float('inf')

        if min_participants <= participant_count <= max_val:
            return {
                'status': 'green',
                'message': f"Suitable for {participant_count} participants"
            }

        # Check 20% tolerance
        tolerance = 0.2
        if participant_count >= min_participants * (1 - tolerance) and \
           (max_participants is None or participant_count <= max_val * (1 + tolerance)):
            return {
                'status': 'yellow',
                'message': f"Manageable but not ideal for {participant_count} participants"
            }

        range_str = f"{min_participants}-{max_participants if max_participants else 'unlimited'}"
        return {
            'status': 'red',
            'message': f"Not suitable for {participant_count} participants (optimal: {range_str})"
        }

    def _evaluate_level_factor(
        self,
        competency_id: int,
        target_level: int,
        format_id: int
    ) -> Dict[str, str]:
        """Evaluate Factor 2: Level achievable by format"""
        result = self.db.execute(
            text("""
                SELECT max_achievable_level
                FROM competency_learning_format_matrix
                WHERE competency_id = :comp_id AND learning_format_id = :fmt_id
            """),
            {'comp_id': competency_id, 'fmt_id': format_id}
        ).fetchone()

        if not result:
            return {'status': 'yellow', 'message': 'No level data available'}

        achievable = result.max_achievable_level

        if achievable >= target_level:
            return {
                'status': 'green',
                'message': f"Can achieve Level {target_level}"
            }

        if achievable >= target_level - 2 and achievable > 0:
            return {
                'status': 'yellow',
                'message': f"Can only achieve Level {achievable} (target: Level {target_level})"
            }

        return {
            'status': 'red',
            'message': f"Cannot achieve Level {target_level} (max: Level {achievable})"
        }

    def _evaluate_strategy_factor(
        self,
        strategy_id: int,
        format_id: int
    ) -> Dict[str, str]:
        """Evaluate Factor 3: Strategy consistency"""
        result = self.db.execute(
            text("""
                SELECT consistency
                FROM strategy_learning_format_matrix
                WHERE strategy_template_id = :strat_id AND learning_format_id = :fmt_id
            """),
            {'strat_id': strategy_id, 'fmt_id': format_id}
        ).fetchone()

        if not result:
            return {'status': 'yellow', 'message': 'No strategy data available'}

        consistency = result.consistency

        if consistency == '++':
            return {'status': 'green', 'message': 'Highly recommended for your strategy'}
        elif consistency == '+':
            return {'status': 'yellow', 'message': 'Partly recommended for your strategy'}
        else:
            return {'status': 'red', 'message': 'Not consistent with your strategy'}

    def _get_overall_status(self, factors: List[Dict]) -> str:
        """Get overall status based on individual factors"""
        statuses = [f['status'] for f in factors]
        if 'red' in statuses:
            return 'warning'
        if 'yellow' in statuses:
            return 'caution'
        return 'good'

    def save_format_selection(
        self,
        organization_id: int,
        competency_id: int,
        target_level: int,
        pmt_type: str,
        format_id: int,
        suitability: Dict[str, Any],
        estimated_participants: int,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """Save a format selection for a training module"""
        self.db.execute(
            text("""
                INSERT INTO phase3_training_module (
                    organization_id, competency_id, target_level, pmt_type,
                    selected_format_id, estimated_participants, actual_users_with_gap,
                    suitability_factor1_status, suitability_factor1_message,
                    suitability_factor2_status, suitability_factor2_message,
                    suitability_factor3_status, suitability_factor3_message,
                    confirmed
                ) VALUES (
                    :org_id, :comp_id, :level, :pmt,
                    :fmt_id, :est_participants, :users_gap,
                    :f1_status, :f1_msg,
                    :f2_status, :f2_msg,
                    :f3_status, :f3_msg,
                    :confirmed
                )
                ON CONFLICT (organization_id, competency_id, target_level, pmt_type)
                DO UPDATE SET
                    selected_format_id = :fmt_id,
                    estimated_participants = :est_participants,
                    suitability_factor1_status = :f1_status,
                    suitability_factor1_message = :f1_msg,
                    suitability_factor2_status = :f2_status,
                    suitability_factor2_message = :f2_msg,
                    suitability_factor3_status = :f3_status,
                    suitability_factor3_message = :f3_msg,
                    confirmed = :confirmed,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                'org_id': organization_id,
                'comp_id': competency_id,
                'level': target_level,
                'pmt': pmt_type,
                'fmt_id': format_id,
                'est_participants': estimated_participants,
                'users_gap': 0,
                'f1_status': suitability['factors']['factor1']['status'],
                'f1_msg': suitability['factors']['factor1']['message'],
                'f2_status': suitability['factors']['factor2']['status'],
                'f2_msg': suitability['factors']['factor2']['message'],
                'f3_status': suitability['factors']['factor3']['status'],
                'f3_msg': suitability['factors']['factor3']['message'],
                'confirmed': confirmed
            }
        )
        self.db.commit()

        return {'success': True}

    # =========================================================================
    # TASK 3: Timeline Planning (LLM-Generated)
    # =========================================================================

    def generate_timeline(self, organization_id: int) -> Dict[str, Any]:
        """
        Generate timeline milestones using LLM based on training program context.

        Returns 5 milestones:
        1. Concept Development Start
        2. Concept Development End
        3. Pilot Start
        4. Rollout Start
        5. Rollout End
        """
        # Gather context
        context = self._build_timeline_context(organization_id)

        # Build prompt
        prompt = self._build_timeline_prompt(context)

        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in training program planning and implementation. Generate realistic timeline estimates based on the training program context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Save milestones
            self._save_timeline_milestones(organization_id, result)

            # Mark Task 3 as complete
            self.db.execute(
                text("""
                    UPDATE phase3_config
                    SET task3_completed = true, updated_at = CURRENT_TIMESTAMP
                    WHERE organization_id = :org_id
                """),
                {'org_id': organization_id}
            )
            self.db.commit()

            return {
                'success': True,
                'milestones': result.get('milestones', []),
                'reasoning': result.get('reasoning', ''),
                'generation_context': context
            }

        except Exception as e:
            current_app.logger.error(f"Timeline generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_timeline_context(self, organization_id: int) -> Dict[str, Any]:
        """Build context for timeline generation"""
        # Get organization info
        org = self.db.execute(
            text("""
                SELECT organization_name, maturity_score, selected_archetype
                FROM organization
                WHERE id = :org_id
            """),
            {'org_id': organization_id}
        ).fetchone()

        # Get training modules
        modules = self.get_training_modules(organization_id)
        module_list = modules.get('modules', [])

        # Calculate format distribution
        format_counts = {}
        for m in module_list:
            if m.get('selected_format_id'):
                fmt = self.db.execute(
                    text("SELECT short_name FROM learning_format WHERE id = :id"),
                    {'id': m['selected_format_id']}
                ).fetchone()
                if fmt:
                    format_counts[fmt.short_name] = format_counts.get(fmt.short_name, 0) + 1

        # Calculate totals
        total_participants = sum(m.get('estimated_participants', 0) for m in module_list)

        # Get competencies involved
        competencies = list(set(m.get('competency_name', '') for m in module_list))

        # Check for e-learning
        e_learning_formats = ['WBT', 'CBT', 'Self-Learning']
        has_elearning = any(f in format_counts for f in e_learning_formats)

        # Check for in-person
        in_person_formats = ['Seminar', 'Coaching', 'Conference', 'Game-Based']
        has_in_person = any(f in format_counts for f in in_person_formats)

        return {
            'organization_name': org.organization_name if org else 'Unknown',
            'maturity_level': org.maturity_score if org else 2,
            'selected_strategy': org.selected_archetype if org else 'Need-based training',
            'total_modules': len(module_list),
            'total_estimated_participants': total_participants,
            'competencies_included': competencies[:10],  # Limit to 10
            'format_distribution': format_counts,
            'has_elearning_components': has_elearning,
            'has_in_person_components': has_in_person,
            'current_date': datetime.now().isoformat()
        }

    def _build_timeline_prompt(self, context: Dict[str, Any]) -> str:
        """Build the LLM prompt for timeline generation"""
        return f"""You are an expert in training program planning and implementation. Based on the following SE training program context, generate realistic timeline estimates for 5 key milestones.

## Training Program Context
- Organization: {context['organization_name']}
- Organization Maturity Level: {context['maturity_level']}
- Selected Qualification Strategy: {context['selected_strategy']}
- Total Training Modules: {context['total_modules']}
- Total Estimated Participants: {context['total_estimated_participants']}
- Competencies: {', '.join(context['competencies_included'][:5])}
- Format Distribution: {json.dumps(context['format_distribution'])}
- Has E-Learning Components: {context['has_elearning_components']}
- Has In-Person Components: {context['has_in_person_components']}

## Reference Durations (from Training Lifecycle Research)
- Development Phase: 2-4 months
- Pilot Phase: 1-3 months
- Initial Implementation: 6-12 months

## Current Date
{context['current_date']}

## Task
Generate estimated dates for these 5 milestones:
1. Concept Development Start - When training material development should begin
2. Concept Development End - When training materials should be ready
3. Pilot Start - When pilot training with test group should begin
4. Rollout Start - When first full training session should occur
5. Rollout End - When last planned training session should complete

Consider:
- Larger participant counts require longer rollout periods
- E-learning content requires more upfront development time but enables parallel delivery
- In-person formats require sequential scheduling
- Higher maturity organizations may move faster
- More modules/competencies extend development time
- Complex format mixes (blended) require more coordination

Respond in JSON format:
{{
  "milestones": [
    {{"order": 1, "name": "Concept Development Start", "estimated_date": "YYYY-MM-DD", "quarter": "Q1 2026", "description": "Training material development begins"}},
    {{"order": 2, "name": "Concept Development End", "estimated_date": "YYYY-MM-DD", "quarter": "Q2 2026", "description": "Training materials ready for pilot"}},
    {{"order": 3, "name": "Pilot Start", "estimated_date": "YYYY-MM-DD", "quarter": "Q2 2026", "description": "Pilot training with test group begins"}},
    {{"order": 4, "name": "Rollout Start", "estimated_date": "YYYY-MM-DD", "quarter": "Q3 2026", "description": "First full training session"}},
    {{"order": 5, "name": "Rollout End", "estimated_date": "YYYY-MM-DD", "quarter": "Q4 2027", "description": "Last planned training session completes"}}
  ],
  "reasoning": "Brief explanation of timeline estimation logic based on the program context"
}}"""

    def _save_timeline_milestones(self, organization_id: int, result: Dict) -> None:
        """Save LLM-generated timeline milestones to database"""
        # Clear existing milestones
        self.db.execute(
            text("DELETE FROM phase3_timeline WHERE organization_id = :org_id"),
            {'org_id': organization_id}
        )

        # Insert new milestones
        for milestone in result.get('milestones', []):
            self.db.execute(
                text("""
                    INSERT INTO phase3_timeline (
                        organization_id, milestone_order, milestone_name,
                        milestone_description, estimated_date, quarter,
                        generation_reasoning
                    ) VALUES (
                        :org_id, :order, :name, :desc, :date, :quarter, :reasoning
                    )
                """),
                {
                    'org_id': organization_id,
                    'order': milestone.get('order'),
                    'name': milestone.get('name'),
                    'desc': milestone.get('description', ''),
                    'date': milestone.get('estimated_date'),
                    'quarter': milestone.get('quarter'),
                    'reasoning': result.get('reasoning', '')
                }
            )

        self.db.commit()

    def get_timeline(self, organization_id: int) -> Dict[str, Any]:
        """Get stored timeline milestones for an organization"""
        result = self.db.execute(
            text("""
                SELECT milestone_order, milestone_name, milestone_description,
                       estimated_date, quarter, generation_reasoning, generated_at
                FROM phase3_timeline
                WHERE organization_id = :org_id
                ORDER BY milestone_order
            """),
            {'org_id': organization_id}
        )

        milestones = []
        reasoning = ''
        generated_at = None

        for row in result:
            milestones.append({
                'order': row.milestone_order,
                'name': row.milestone_name,
                'description': row.milestone_description,
                'estimated_date': row.estimated_date.isoformat() if row.estimated_date else None,
                'quarter': row.quarter
            })
            if not reasoning and row.generation_reasoning:
                reasoning = row.generation_reasoning
            if not generated_at and row.generated_at:
                generated_at = row.generated_at.isoformat()

        return {
            'milestones': milestones,
            'reasoning': reasoning,
            'generated_at': generated_at,
            'has_timeline': len(milestones) > 0
        }

    # =========================================================================
    # Phase 3 Output/Summary
    # =========================================================================

    def get_phase3_output(self, organization_id: int) -> Dict[str, Any]:
        """Get complete Phase 3 output summary"""
        config = self.get_phase3_config(organization_id)
        modules = self.get_training_modules(organization_id)
        timeline = self.get_timeline(organization_id)

        # Calculate summary stats
        module_list = modules.get('modules', [])
        configured = sum(1 for m in module_list if m.get('selected_format_id'))
        confirmed = sum(1 for m in module_list if m.get('confirmed'))

        # Format distribution
        format_dist = {}
        for m in module_list:
            if m.get('selected_format_id'):
                fmt = self.db.execute(
                    text("SELECT short_name FROM learning_format WHERE id = :id"),
                    {'id': m['selected_format_id']}
                ).fetchone()
                if fmt:
                    format_dist[fmt.short_name] = format_dist.get(fmt.short_name, 0) + 1

        return {
            'organization_id': organization_id,
            'config': config,
            'training_modules': modules,
            'timeline': timeline,
            'summary': {
                'total_modules': len(module_list),
                'configured_modules': configured,
                'confirmed_modules': confirmed,
                'total_estimated_participants': sum(m.get('estimated_participants', 0) for m in module_list),
                'format_distribution': format_dist,
                'completion': {
                    'task1': config.get('task1_completed', False),
                    'task2': configured == len(module_list) and len(module_list) > 0,
                    'task3': timeline.get('has_timeline', False)
                }
            }
        }
