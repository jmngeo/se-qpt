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

    # Level name mapping for display
    LEVEL_NAMES = {
        1: 'Knowing',
        2: 'Understanding',
        4: 'Applying',
        6: 'Mastering'
    }

    def __init__(self, db_session):
        """Initialize the service with database session"""
        self.db = db_session
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    def _get_level_name(self, level: int) -> str:
        """Convert level number to display name"""
        return self.LEVEL_NAMES.get(level, f'Level {level}')

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

    def get_training_modules(self, organization_id: int, view_type: str = 'competency_level') -> Dict[str, Any]:
        """
        Get training modules from Phase 2 Learning Objectives.

        Args:
            organization_id: The organization ID
            view_type: 'competency_level' or 'role_clustered'

        Returns modules with gap data, participant counts, and any existing format selections.
        For role_clustered view, generates separate modules per training cluster.
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

        # Get existing format selections (include cluster_id for role_clustered)
        existing_selections = self._get_existing_selections(organization_id, view_type)

        if view_type == 'role_clustered':
            # Get role to cluster mapping
            role_cluster_map = self._get_role_cluster_map(organization_id)
            # Extract cluster-specific modules
            modules = self._extract_cluster_modules_from_los(
                objectives_data,
                organization_id,
                org_info,
                existing_selections,
                role_cluster_map
            )
        else:
            # Extract standard modules (competency_level view)
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

    def _get_existing_selections(self, organization_id: int, view_type: str = 'competency_level') -> Dict[str, Dict]:
        """Get existing format selections for an organization"""
        result = self.db.execute(
            text("""
                SELECT competency_id, target_level, pmt_type, training_program_cluster_id,
                       selected_format_id, estimated_participants, confirmed,
                       suitability_factor1_status, suitability_factor2_status, suitability_factor3_status
                FROM phase3_training_module
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
        )

        selections = {}
        for row in result:
            # For role_clustered view, include cluster_id in key
            if view_type == 'role_clustered' and row.training_program_cluster_id:
                key = f"{row.competency_id}_{row.target_level}_{row.pmt_type}_{row.training_program_cluster_id}"
            else:
                key = f"{row.competency_id}_{row.target_level}_{row.pmt_type}"

            selections[key] = {
                'selected_format_id': row.selected_format_id,
                'estimated_participants': row.estimated_participants,
                'confirmed': row.confirmed,
                'cluster_id': row.training_program_cluster_id,
                'suitability': {
                    'factor1_status': row.suitability_factor1_status,
                    'factor2_status': row.suitability_factor2_status,
                    'factor3_status': row.suitability_factor3_status
                }
            }

        return selections

    def _get_role_cluster_map(self, organization_id: int) -> Dict[str, Dict]:
        """Get mapping of role names to their cluster info"""
        result = self.db.execute(
            text("""
                SELECT orl.id as role_id, orl.role_name, tpc.id as cluster_id,
                       tpc.cluster_name, tpc.training_program_name
                FROM organization_roles orl
                JOIN training_program_cluster tpc ON orl.training_program_cluster_id = tpc.id
                WHERE orl.organization_id = :org_id
            """),
            {'org_id': organization_id}
        )

        role_map = {}
        for row in result:
            role_map[str(row.role_id)] = {
                'role_id': row.role_id,
                'role_name': row.role_name,
                'cluster_id': row.cluster_id,
                'cluster_name': row.cluster_name,
                'training_program_name': row.training_program_name
            }
            # Also map by role name for convenience
            role_map[row.role_name] = role_map[str(row.role_id)]

        return role_map

    def _get_clusters_info(self, organization_id: int) -> Dict[int, Dict]:
        """Get all training clusters with their info"""
        result = self.db.execute(
            text("""
                SELECT tpc.id, tpc.cluster_name, tpc.training_program_name,
                       COUNT(orl.id) as role_count
                FROM training_program_cluster tpc
                LEFT JOIN organization_roles orl ON orl.training_program_cluster_id = tpc.id
                                                 AND orl.organization_id = :org_id
                GROUP BY tpc.id, tpc.cluster_name, tpc.training_program_name
                HAVING COUNT(orl.id) > 0
                ORDER BY tpc.id
            """),
            {'org_id': organization_id}
        )

        clusters = {}
        for row in result:
            clusters[row.id] = {
                'cluster_id': row.id,
                'cluster_name': row.cluster_name,
                'training_program_name': row.training_program_name,
                'role_count': row.role_count
            }

        return clusters

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
                # Skip if no gap/training needed
                # Phase 2 uses 'training_required' or 'gap' for competencies needing training
                status = comp.get('status', '')
                if status not in ('gap', 'training_required'):
                    continue

                competency_id = comp.get('competency_id')
                competency_name = comp.get('competency_name', competencies.get(competency_id, 'Unknown'))

                # Check if PMT breakdown exists
                lo_data = comp.get('learning_objective', {})
                has_pmt = lo_data.get('has_pmt_breakdown', False)

                # Get users with gap (for participant estimation)
                gap_data = comp.get('gap_data', {})

                # Extract role names and calculate users with gap FOR THIS SPECIFIC LEVEL
                # gap_data.roles contains level_details with per-level users_needing counts
                roles_data = gap_data.get('roles', {})
                roles_needing = []
                users_with_gap = 0

                if isinstance(roles_data, dict):
                    for role_id, role_info in roles_data.items():
                        if isinstance(role_info, dict):
                            role_name = role_info.get('role_name', '')

                            # Get level-specific user count from level_details
                            level_details = role_info.get('level_details', {})
                            level_data = level_details.get(str(target_level), {})
                            level_users_needing = level_data.get('users_needing', 0)

                            # Only include role if it has users needing training at this level
                            if level_users_needing > 0 and role_name:
                                roles_needing.append(role_name)
                                users_with_gap += level_users_needing

                # Fallback if no level-specific data found
                if users_with_gap == 0:
                    # Try the aggregate users_needing_training as fallback
                    for role_id, role_info in roles_data.items():
                        if isinstance(role_info, dict):
                            users_with_gap += role_info.get('users_needing_training', 0)
                            role_name = role_info.get('role_name', '')
                            if role_name and role_name not in roles_needing:
                                roles_needing.append(role_name)

                    # Final fallback
                    if users_with_gap == 0:
                        users_with_gap = gap_data.get('users_with_gap', 1)

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
                            'module_name': f"{competency_name} - {self._get_level_name(target_level)} - {pmt_type.title()}",
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
                        'module_name': f"{competency_name} - {self._get_level_name(target_level)}",
                        'users_with_gap': users_with_gap,
                        'estimated_participants': estimated_participants,
                        'roles_needing_training': roles_needing,
                        'selected_format_id': selection.get('selected_format_id'),
                        'confirmed': selection.get('confirmed', False),
                        'suitability': selection.get('suitability')
                    })

        return modules

    def _extract_cluster_modules_from_los(
        self,
        objectives_data: Dict,
        organization_id: int,
        scaling_info: Dict,
        existing_selections: Dict,
        role_cluster_map: Dict
    ) -> List[Dict[str, Any]]:
        """
        Extract training modules from learning objectives, creating separate modules per cluster.
        For Role-Clustered view - each cluster gets its own training module.

        For Engineers cluster (id=1): Implements hybrid approach
        - "common" subcluster: Modules ALL engineering roles need at same level
        - "pathway" subcluster: Modules only SOME engineering roles need
        """
        modules = []

        # Get data section
        data = objectives_data.get('data', objectives_data)
        main_pyramid = data.get('main_pyramid', {})
        levels = main_pyramid.get('levels', {})

        # Get competency lookup
        competencies = self._get_competency_lookup()

        # Get clusters info
        clusters_info = self._get_clusters_info(organization_id)

        # ENGINEERS_CLUSTER_ID = 1 (SE for Engineers)
        ENGINEERS_CLUSTER_ID = 1

        # Get all roles per cluster for subcluster determination
        all_roles_by_cluster = self._get_all_roles_by_cluster(organization_id)
        all_engineering_roles = set(all_roles_by_cluster.get(ENGINEERS_CLUSTER_ID, []))

        for level_key, level_data in levels.items():
            target_level = int(level_key)
            comps = level_data.get('competencies', [])

            for comp in comps:
                status = comp.get('status', '')
                if status not in ('gap', 'training_required'):
                    continue

                competency_id = comp.get('competency_id')
                competency_name = comp.get('competency_name', competencies.get(competency_id, 'Unknown'))

                lo_data = comp.get('learning_objective', {})
                has_pmt = lo_data.get('has_pmt_breakdown', False)

                gap_data = comp.get('gap_data', {})
                roles_data = gap_data.get('roles', {})

                # Group roles by cluster
                cluster_roles = {}  # cluster_id -> list of (role_id, role_name, users_needing)

                for role_id, role_info in roles_data.items():
                    if not isinstance(role_info, dict):
                        continue

                    role_name = role_info.get('role_name', '')
                    if not role_name:
                        continue

                    # Get level-specific user count
                    level_details = role_info.get('level_details', {})
                    level_data_item = level_details.get(str(target_level), {})
                    level_users_needing = level_data_item.get('users_needing', 0)

                    if level_users_needing == 0:
                        continue

                    # Find which cluster this role belongs to
                    role_mapping = role_cluster_map.get(role_id) or role_cluster_map.get(role_name)
                    if not role_mapping:
                        continue

                    cluster_id = role_mapping['cluster_id']
                    if cluster_id not in cluster_roles:
                        cluster_roles[cluster_id] = []

                    cluster_roles[cluster_id].append({
                        'role_id': role_id,
                        'role_name': role_name,
                        'users_needing': level_users_needing
                    })

                # Create modules for each cluster that has roles needing training
                for cluster_id, roles_list in cluster_roles.items():
                    if not roles_list:
                        continue

                    cluster_info = clusters_info.get(cluster_id, {})
                    cluster_name = cluster_info.get('training_program_name', f'Cluster {cluster_id}')

                    roles_needing = [r['role_name'] for r in roles_list]
                    roles_needing_set = set(roles_needing)
                    users_with_gap = sum(r['users_needing'] for r in roles_list)
                    estimated_participants = int(users_with_gap * scaling_info['scaling_factor'])

                    # Determine subcluster type for Engineers cluster
                    # NEW LOGIC: Common Base = 2+ roles share this module
                    #            Pathway = only 1 role needs this module
                    subcluster = None
                    pathway_roles = None
                    shared_roles_count = len(roles_needing_set)

                    if cluster_id == ENGINEERS_CLUSTER_ID and len(all_engineering_roles) > 0:
                        if shared_roles_count >= 2:
                            # 2+ engineering roles need this module - COMMON BASE
                            # These roles can train together
                            subcluster = 'common'
                        else:
                            # Only 1 role needs this - ROLE-SPECIFIC PATHWAY
                            subcluster = 'pathway'
                            pathway_roles = roles_needing

                    if has_pmt:
                        for pmt_type in ['method', 'tool']:
                            key = f"{competency_id}_{target_level}_{pmt_type}_{cluster_id}"
                            selection = existing_selections.get(key, {})

                            module_data = {
                                'competency_id': competency_id,
                                'competency_name': competency_name,
                                'target_level': target_level,
                                'pmt_type': pmt_type,
                                'cluster_id': cluster_id,
                                'cluster_name': cluster_name,
                                'module_name': f"{competency_name} - {self._get_level_name(target_level)} - {pmt_type.title()}",
                                'users_with_gap': users_with_gap,
                                'estimated_participants': estimated_participants,
                                'roles_needing_training': roles_needing,
                                'selected_format_id': selection.get('selected_format_id'),
                                'confirmed': selection.get('confirmed', False),
                                'suitability': selection.get('suitability')
                            }
                            # Add subcluster info for Engineers
                            if subcluster:
                                module_data['subcluster'] = subcluster
                                module_data['shared_roles_count'] = shared_roles_count
                                if pathway_roles:
                                    module_data['pathway_roles'] = pathway_roles

                            modules.append(module_data)
                    else:
                        key = f"{competency_id}_{target_level}_combined_{cluster_id}"
                        selection = existing_selections.get(key, {})

                        module_data = {
                            'competency_id': competency_id,
                            'competency_name': competency_name,
                            'target_level': target_level,
                            'pmt_type': 'combined',
                            'cluster_id': cluster_id,
                            'cluster_name': cluster_name,
                            'module_name': f"{competency_name} - {self._get_level_name(target_level)}",
                            'users_with_gap': users_with_gap,
                            'estimated_participants': estimated_participants,
                            'roles_needing_training': roles_needing,
                            'selected_format_id': selection.get('selected_format_id'),
                            'confirmed': selection.get('confirmed', False),
                            'suitability': selection.get('suitability')
                        }
                        # Add subcluster info for Engineers
                        if subcluster:
                            module_data['subcluster'] = subcluster
                            module_data['shared_roles_count'] = shared_roles_count
                            if pathway_roles:
                                module_data['pathway_roles'] = pathway_roles

                        modules.append(module_data)

        return modules

    def _get_all_roles_by_cluster(self, organization_id: int) -> Dict[int, List[str]]:
        """Get all role names grouped by their training program cluster."""
        result = self.db.execute(
            text("""
                SELECT training_program_cluster_id, role_name
                FROM organization_roles
                WHERE organization_id = :org_id
                  AND training_program_cluster_id IS NOT NULL
            """),
            {'org_id': organization_id}
        )

        roles_by_cluster = {}
        for row in result:
            cluster_id = row.training_program_cluster_id
            if cluster_id not in roles_by_cluster:
                roles_by_cluster[cluster_id] = []
            roles_by_cluster[cluster_id].append(row.role_name)

        return roles_by_cluster

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

        # Factor 3: Strategy Consistency (supports multiple strategies with weighted aggregation)
        factor3 = self._evaluate_strategy_factor(
            organization_id,
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
        organization_id: int,
        format_id: int
    ) -> Dict[str, str]:
        """
        Evaluate Factor 3: Strategy consistency with weighted multi-strategy support.

        For organizations with multiple strategies:
        - PRIMARY strategy (priority=1): weight = 2
        - SUPPLEMENTARY strategies (priority>1): weight = 1

        Scoring:
        - '++' = 2 points (highly recommended)
        - '+' = 1 point (partly recommended)
        - '--' = 0 points (not consistent)

        Weighted average thresholds:
        - >= 1.5: Green (highly recommended)
        - >= 0.5: Yellow (partly recommended)
        - < 0.5: Red (not consistent)

        For single strategy: works exactly as before.
        """
        # Get all selected strategies for the organization
        strategies = self.db.execute(
            text("""
                SELECT ls.strategy_template_id, ls.strategy_name, ls.priority
                FROM learning_strategy ls
                WHERE ls.organization_id = :org_id
                  AND ls.selected = true
                  AND ls.strategy_template_id IS NOT NULL
                ORDER BY ls.priority ASC
            """),
            {'org_id': organization_id}
        ).fetchall()

        if not strategies:
            # Fallback to single strategy lookup
            strategy_id = self._get_strategy_id(organization_id)
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

        # Single strategy case - use simple logic (same as before)
        if len(strategies) == 1:
            result = self.db.execute(
                text("""
                    SELECT consistency
                    FROM strategy_learning_format_matrix
                    WHERE strategy_template_id = :strat_id AND learning_format_id = :fmt_id
                """),
                {'strat_id': strategies[0].strategy_template_id, 'fmt_id': format_id}
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

        # Multiple strategies - use weighted aggregation
        consistency_points = {'++': 2, '+': 1, '--': 0}
        total_weighted_score = 0
        total_weight = 0
        strategy_details = []

        for strategy in strategies:
            # Weight: PRIMARY (priority=1) gets weight 2, others get weight 1
            weight = 2 if strategy.priority == 1 else 1

            result = self.db.execute(
                text("""
                    SELECT consistency
                    FROM strategy_learning_format_matrix
                    WHERE strategy_template_id = :strat_id AND learning_format_id = :fmt_id
                """),
                {'strat_id': strategy.strategy_template_id, 'fmt_id': format_id}
            ).fetchone()

            if result:
                consistency = result.consistency
                points = consistency_points.get(consistency, 0)
                total_weighted_score += points * weight
                total_weight += weight
                strategy_details.append({
                    'name': strategy.strategy_name,
                    'consistency': consistency,
                    'is_primary': strategy.priority == 1
                })

        if total_weight == 0:
            return {'status': 'yellow', 'message': 'No strategy data available'}

        # Calculate weighted average
        weighted_avg = total_weighted_score / total_weight

        # Build descriptive message
        primary_strategies = [s for s in strategy_details if s['is_primary']]
        primary_name = primary_strategies[0]['name'] if primary_strategies else 'selected strategies'
        strategy_count = len(strategy_details)

        if weighted_avg >= 1.5:
            if strategy_count == 1:
                return {'status': 'green', 'message': 'Highly recommended for your strategy'}
            else:
                return {
                    'status': 'green',
                    'message': f'Highly recommended across {strategy_count} strategies'
                }
        elif weighted_avg >= 0.5:
            if strategy_count == 1:
                return {'status': 'yellow', 'message': 'Partly recommended for your strategy'}
            else:
                return {
                    'status': 'yellow',
                    'message': f'Partly recommended across {strategy_count} strategies'
                }
        else:
            if strategy_count == 1:
                return {'status': 'red', 'message': 'Not consistent with your strategy'}
            else:
                return {
                    'status': 'red',
                    'message': f'Not consistent with {strategy_count} strategies'
                }

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
        confirmed: bool = False,
        cluster_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Save a format selection for a training module"""
        # Check if record exists
        existing = self.db.execute(
            text("""
                SELECT id FROM phase3_training_module
                WHERE organization_id = :org_id
                  AND competency_id = :comp_id
                  AND target_level = :level
                  AND COALESCE(pmt_type, '') = COALESCE(:pmt, '')
                  AND COALESCE(training_program_cluster_id, 0) = COALESCE(:cluster_id, 0)
            """),
            {
                'org_id': organization_id,
                'comp_id': competency_id,
                'level': target_level,
                'pmt': pmt_type,
                'cluster_id': cluster_id
            }
        ).fetchone()

        if existing:
            # Update existing record
            self.db.execute(
                text("""
                    UPDATE phase3_training_module SET
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
                    WHERE id = :id
                """),
                {
                    'id': existing.id,
                    'fmt_id': format_id,
                    'est_participants': estimated_participants,
                    'f1_status': suitability['factors']['factor1']['status'],
                    'f1_msg': suitability['factors']['factor1']['message'],
                    'f2_status': suitability['factors']['factor2']['status'],
                    'f2_msg': suitability['factors']['factor2']['message'],
                    'f3_status': suitability['factors']['factor3']['status'],
                    'f3_msg': suitability['factors']['factor3']['message'],
                    'confirmed': confirmed
                }
            )
        else:
            # Insert new record
            self.db.execute(
                text("""
                    INSERT INTO phase3_training_module (
                        organization_id, competency_id, target_level, pmt_type,
                        training_program_cluster_id,
                        selected_format_id, estimated_participants, actual_users_with_gap,
                        suitability_factor1_status, suitability_factor1_message,
                        suitability_factor2_status, suitability_factor2_message,
                        suitability_factor3_status, suitability_factor3_message,
                        confirmed
                    ) VALUES (
                        :org_id, :comp_id, :level, :pmt,
                        :cluster_id,
                        :fmt_id, :est_participants, :users_gap,
                        :f1_status, :f1_msg,
                        :f2_status, :f2_msg,
                        :f3_status, :f3_msg,
                        :confirmed
                    )
                """),
                {
                    'org_id': organization_id,
                    'comp_id': competency_id,
                    'level': target_level,
                    'pmt': pmt_type,
                    'cluster_id': cluster_id,
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

    def mark_task2_completed(self, organization_id: int) -> Dict[str, Any]:
        """Mark Task 2 (Learning Format Selection) as completed"""
        self.db.execute(
            text("""
                UPDATE phase3_config
                SET task2_completed = true, updated_at = CURRENT_TIMESTAMP
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
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

            # Parse JSON response with error handling
            raw_content = response.choices[0].message.content
            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError as json_err:
                current_app.logger.error(f"Failed to parse LLM response as JSON: {json_err}")
                current_app.logger.error(f"Raw response: {raw_content[:500]}")
                return {
                    'success': False,
                    'error': 'Failed to parse timeline response. Please try again.'
                }

            # Validate required structure
            milestones = result.get('milestones', [])
            if not isinstance(milestones, list):
                current_app.logger.error(f"Invalid milestones format: {type(milestones)}")
                return {
                    'success': False,
                    'error': 'Invalid timeline format received. Please try again.'
                }

            # Validate milestone count (should be exactly 5)
            if len(milestones) < 5:
                current_app.logger.warning(f"Received {len(milestones)} milestones, expected 5")
                # Pad with default milestones if needed
                default_milestones = [
                    {'order': 1, 'name': 'Concept Development Start', 'description': 'Training material development begins'},
                    {'order': 2, 'name': 'Concept Development End', 'description': 'Training materials ready for pilot'},
                    {'order': 3, 'name': 'Pilot Start', 'description': 'Pilot training with test group begins'},
                    {'order': 4, 'name': 'Rollout Start', 'description': 'Full training rollout begins'},
                    {'order': 5, 'name': 'Rollout End', 'description': 'Training program completion'}
                ]
                while len(milestones) < 5:
                    idx = len(milestones)
                    milestones.append(default_milestones[idx])
                result['milestones'] = milestones

            # Validate each milestone has required fields
            for i, m in enumerate(milestones):
                if not m.get('name'):
                    m['name'] = f"Milestone {i+1}"
                if not m.get('order'):
                    m['order'] = i + 1
                if not m.get('estimated_date'):
                    # Generate default dates starting from current month
                    from datetime import datetime, timedelta
                    base_date = datetime.now()
                    months_offset = [0, 3, 4, 6, 12]  # Default spacing
                    m['estimated_date'] = (base_date + timedelta(days=30*months_offset[min(i, 4)])).strftime('%Y-%m-%d')
                if not m.get('quarter'):
                    from datetime import datetime
                    date = datetime.strptime(m['estimated_date'], '%Y-%m-%d')
                    quarter = (date.month - 1) // 3 + 1
                    m['quarter'] = f"Q{quarter} {date.year}"

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

            # Normalize milestone field names for frontend consistency
            normalized_milestones = []
            for m in result.get('milestones', []):
                normalized_milestones.append({
                    'order': m.get('order'),
                    'milestone_name': m.get('name'),  # LLM returns 'name', frontend expects 'milestone_name'
                    'milestone_description': m.get('description', ''),
                    'estimated_date': m.get('estimated_date'),
                    'quarter': m.get('quarter'),
                    'generation_reasoning': result.get('reasoning', '')
                })

            return {
                'success': True,
                'milestones': normalized_milestones,
                'reasoning': result.get('reasoning', ''),
                'generation_context': context
            }

        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parsing error in timeline generation: {e}")
            return {
                'success': False,
                'error': 'Failed to parse timeline response. Please try again.'
            }
        except Exception as e:
            current_app.logger.error(f"Timeline generation failed: {e}")
            import traceback
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
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

        # Get all selected strategies from Phase 1
        all_strategies = self._get_all_strategies(organization_id)
        strategy_name = all_strategies[0]['name'] if all_strategies else 'Not Selected'
        strategy_names_list = [s['name'] for s in all_strategies]

        # Get target group size from Phase 1 (actual unique participants)
        target_group_result = self.db.execute(
            text("""
                SELECT (responses::jsonb)->>'value' as target_size,
                       (responses::jsonb)->>'range' as range_label
                FROM phase_questionnaire_responses
                WHERE organization_id = :org_id
                  AND questionnaire_type = 'target_group'
                ORDER BY completed_at DESC
                LIMIT 1
            """),
            {'org_id': organization_id}
        ).fetchone()

        target_group_size = int(target_group_result.target_size) if target_group_result and target_group_result.target_size else 100
        target_group_range = target_group_result.range_label if target_group_result else 'Unknown'

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
            'selected_strategy': strategy_name,  # Primary strategy for backward compatibility
            'all_strategies': strategy_names_list,  # All selected strategies
            'strategy_count': len(strategy_names_list),
            'total_modules': len(module_list),
            'target_group_size': target_group_size,
            'target_group_range': target_group_range,
            'competencies_included': competencies[:10],  # Limit to 10
            'format_distribution': format_counts,
            'has_elearning_components': has_elearning,
            'has_in_person_components': has_in_person,
            'current_date': datetime.now().isoformat()
        }

    def _build_timeline_prompt(self, context: Dict[str, Any]) -> str:
        """Build the LLM prompt for timeline generation"""
        # Format strategies for prompt
        strategies_text = ', '.join(context.get('all_strategies', [context['selected_strategy']]))
        strategy_count = context.get('strategy_count', 1)

        return f"""You are an expert in training program planning and implementation. Based on the following SE training program context, generate realistic timeline estimates for 5 key milestones.

## Training Program Context
- Organization: {context['organization_name']}
- Organization Maturity Level: {context['maturity_level']}
- Selected Qualification Strategies ({strategy_count}): {strategies_text}
- Total Training Modules: {context['total_modules']}
- Target Group Size: {context['target_group_size']} participants ({context['target_group_range']})
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
                'milestone_name': row.milestone_name,  # Frontend expects 'milestone_name'
                'milestone_description': row.milestone_description,
                'estimated_date': row.estimated_date.isoformat() if row.estimated_date else None,
                'quarter': row.quarter,
                'generation_reasoning': row.generation_reasoning
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
        # Pass the selected view type to get proper cluster info for role_clustered view
        selected_view = config.get('selected_view', 'competency_level')
        modules = self.get_training_modules(organization_id, view_type=selected_view)
        timeline = self.get_timeline(organization_id)

        # Get all strategies
        all_strategies = self._get_all_strategies(organization_id)
        strategy_name = all_strategies[0]['name'] if all_strategies else 'Not Selected'
        all_strategy_names = [s['name'] for s in all_strategies]

        # Get target group size from Phase 1
        target_group_result = self.db.execute(
            text("""
                SELECT (responses::jsonb)->>'value' as target_size,
                       (responses::jsonb)->>'range' as range_label
                FROM phase_questionnaire_responses
                WHERE organization_id = :org_id
                  AND questionnaire_type = 'target_group'
                ORDER BY completed_at DESC
                LIMIT 1
            """),
            {'org_id': organization_id}
        ).fetchone()

        target_group_size = int(target_group_result.target_size) if target_group_result and target_group_result.target_size else 0
        target_group_range = target_group_result.range_label if target_group_result else 'Unknown'

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
            'modules': module_list,  # Direct list for frontend convenience
            'training_modules': modules,  # Full response with scaling_info
            'timeline': timeline,
            'summary': {
                'module_count': len(module_list),  # Frontend-compatible name
                'total_modules': len(module_list),
                'configured_modules': configured,
                'confirmed_modules': confirmed,
                'target_group_size': target_group_size,
                'target_group_range': target_group_range,
                'total_estimated_participants': sum(m.get('estimated_participants', 0) for m in module_list),
                'format_distribution': format_dist,
                'strategy_name': strategy_name,  # Primary strategy for backward compatibility
                'all_strategies': all_strategy_names,  # All selected strategies
                'strategy_count': len(all_strategy_names),
                'completion': {
                    'task1': config.get('task1_completed', False),
                    'task2': configured == len(module_list) and len(module_list) > 0,
                    'task3': timeline.get('has_timeline', False)
                }
            }
        }

    def _get_strategy_name(self, organization_id: int) -> str:
        """Get the strategy name for an organization"""
        # First try: check phase_questionnaire_responses for strategies (Phase 1 selection)
        try:
            strategy_result = self.db.execute(
                text("""
                    SELECT (responses::jsonb)->'strategies'->0->>'strategyName' as strategy_name
                    FROM phase_questionnaire_responses
                    WHERE organization_id = :org_id
                      AND questionnaire_type = 'strategies'
                    ORDER BY completed_at DESC
                    LIMIT 1
                """),
                {'org_id': organization_id}
            ).fetchone()

            if strategy_result and strategy_result.strategy_name:
                return strategy_result.strategy_name
        except Exception:
            self.db.rollback()

        # Second try: check organization.selected_archetype directly
        try:
            org_result = self.db.execute(
                text("""
                    SELECT selected_archetype FROM organization WHERE id = :org_id
                """),
                {'org_id': organization_id}
            ).fetchone()

            if org_result and org_result.selected_archetype:
                return org_result.selected_archetype
        except Exception:
            self.db.rollback()

        # Fallback: check learning objectives data
        try:
            lo_result = self.db.execute(
                text("""
                    SELECT objectives_data->'data'->'strategy_name' as strategy_name
                    FROM generated_learning_objectives
                    WHERE organization_id = :org_id
                    ORDER BY generated_at DESC
                    LIMIT 1
                """),
                {'org_id': organization_id}
            ).fetchone()

            if lo_result and lo_result.strategy_name:
                name = lo_result.strategy_name
                if isinstance(name, str):
                    return name.strip('"')
        except Exception:
            self.db.rollback()

        return 'Not Selected'

    def _get_strategy_id(self, organization_id: int) -> int:
        """
        Get the strategy template ID for an organization.
        Uses the learning_strategy table which has proper strategy_template_id.
        Returns default strategy ID (1) if no match found.
        """
        # BEST SOURCE: learning_strategy table has strategy_template_id properly linked
        try:
            result = self.db.execute(
                text("""
                    SELECT strategy_template_id
                    FROM learning_strategy
                    WHERE organization_id = :org_id
                      AND selected = true
                      AND strategy_template_id IS NOT NULL
                    ORDER BY priority ASC
                    LIMIT 1
                """),
                {'org_id': organization_id}
            ).fetchone()

            if result and result.strategy_template_id:
                return result.strategy_template_id
        except Exception:
            self.db.rollback()

        # FALLBACK: Try to match from phase_questionnaire_responses using strategy key
        try:
            # Get the strategy key from questionnaire responses
            strategy_key_result = self.db.execute(
                text("""
                    SELECT (responses::jsonb)->'strategies'->0->>'strategy' as strategy_key
                    FROM phase_questionnaire_responses
                    WHERE organization_id = :org_id
                      AND questionnaire_type = 'strategies'
                    ORDER BY completed_at DESC
                    LIMIT 1
                """),
                {'org_id': organization_id}
            ).fetchone()

            if strategy_key_result and strategy_key_result.strategy_key:
                # Map strategy keys to template IDs
                strategy_key_map = {
                    'common_basic_understanding': 1,
                    'se_for_managers': 2,
                    'orientation_in_pilot': 3,
                    'needs_based_project': 4,
                    'continuous_support': 5,
                    'train_the_trainer': 6,
                    'certification': 7
                }
                strategy_id = strategy_key_map.get(strategy_key_result.strategy_key)
                if strategy_id:
                    return strategy_id
        except Exception:
            self.db.rollback()

        # LAST FALLBACK: Try name-based matching
        strategy_name = self._get_strategy_name(organization_id)

        if strategy_name != 'Not Selected':
            try:
                # Case-insensitive, normalize punctuation
                normalized_name = strategy_name.lower().replace('-', ' ').replace(',', ' ')
                result = self.db.execute(
                    text("""
                        SELECT id FROM strategy_template
                        WHERE LOWER(REPLACE(REPLACE(strategy_name, '-', ' '), ',', ' '))
                              LIKE :pattern
                        ORDER BY id
                        LIMIT 1
                    """),
                    {'pattern': f'%{normalized_name.split()[0]}%'}
                ).fetchone()

                if result:
                    return result.id
            except Exception:
                self.db.rollback()

        # Default to strategy 1 (Common basic understanding)
        return 1

    def _get_all_strategies(self, organization_id: int) -> List[Dict[str, Any]]:
        """
        Get all selected strategies for an organization with their priorities.

        Returns a list of strategy dicts sorted by priority:
        [
            {'id': 5, 'name': 'Continuous Support', 'priority': 1, 'is_primary': True},
            {'id': 2, 'name': 'SE for Managers', 'priority': 3, 'is_primary': False},
            ...
        ]
        """
        try:
            result = self.db.execute(
                text("""
                    SELECT ls.strategy_template_id, ls.strategy_name, ls.priority
                    FROM learning_strategy ls
                    WHERE ls.organization_id = :org_id
                      AND ls.selected = true
                      AND ls.strategy_template_id IS NOT NULL
                    ORDER BY ls.priority ASC, ls.strategy_name ASC
                """),
                {'org_id': organization_id}
            ).fetchall()

            if result:
                strategies = []
                for row in result:
                    strategies.append({
                        'id': row.strategy_template_id,
                        'name': row.strategy_name,
                        'priority': row.priority,
                        'is_primary': row.priority == 1
                    })
                return strategies
        except Exception:
            self.db.rollback()

        # Fallback: try phase_questionnaire_responses
        try:
            pqr_result = self.db.execute(
                text("""
                    SELECT responses::jsonb->'strategies' as strategies
                    FROM phase_questionnaire_responses
                    WHERE organization_id = :org_id
                      AND questionnaire_type = 'strategies'
                    ORDER BY completed_at DESC
                    LIMIT 1
                """),
                {'org_id': organization_id}
            ).fetchone()

            if pqr_result and pqr_result.strategies:
                import json
                strategies_data = json.loads(pqr_result.strategies) if isinstance(pqr_result.strategies, str) else pqr_result.strategies
                strategies = []
                for i, s in enumerate(strategies_data):
                    is_primary = s.get('priority') == 'PRIMARY'
                    strategies.append({
                        'id': None,  # Not available from this source
                        'name': s.get('strategyName', 'Unknown'),
                        'priority': 1 if is_primary else 3,
                        'is_primary': is_primary
                    })
                # Sort by priority
                strategies.sort(key=lambda x: x['priority'])
                return strategies
        except Exception:
            self.db.rollback()

        # Default: return single default strategy
        return [{'id': 1, 'name': 'Common basic understanding', 'priority': 1, 'is_primary': True}]
