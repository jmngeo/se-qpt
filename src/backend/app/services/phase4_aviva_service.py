"""
Phase 4: Micro Planning - AVIVA Didactics Service

Handles AVIVA didactic plan generation for training modules.
Uses a hybrid approach:
- Programmatic generation for structure (Start, Duration, Type, AVIVA, Method, Material)
- GenAI generation for content (What column)

Based on Phase4_Micro_Planning_Specification_v1.1.md
"""

import os
import json
from datetime import datetime, time, timedelta
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from sqlalchemy import text
from flask import current_app
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


class Phase4AvivaService:
    """Service for Phase 4 AVIVA Didactics operations"""

    # Level configuration
    LEVEL_NAMES = {
        1: 'Knowing',
        2: 'Understanding',
        4: 'Applying',
        6: 'Mastering'
    }

    # Duration in hours per level
    LEVEL_DURATION_HOURS = {
        1: 2,
        2: 4,
        4: 8,
        6: 16
    }

    # AVIVA phase durations in minutes (defaults)
    AVIVA_PHASE_DURATIONS = {
        'A_arrive': {'default': 10, 'range': (5, 15)},
        'V_activate': {'default': 20, 'range': (15, 30)},
        'I_inform': {'default': 30, 'range': (20, 45)},
        'V_process': {'default': 45, 'range': (30, 60)},
        'A_evaluate': {'default': 15, 'range': (10, 20)},
        'P_break': {'default': 15, 'range': (10, 15)},
        'P_lunch': {'default': 60, 'range': (45, 60)}
    }

    # AVIVA phase to Type mapping
    AVIVA_TO_TYPE = {
        'A': 'V',  # Arrival -> Lecture (welcome)
        'V': 'U',  # Activate/Process -> Exercise
        'I': 'V',  # Inform -> Lecture
        'P': 'P'   # Pause -> Pause
    }

    # Methods by AVIVA phase and format
    METHODS_BY_PHASE_FORMAT = {
        'A': {
            'default': 'Lecture',
            'seminar': 'Lecture',
            'webinar': 'Presentation',
            'coaching': 'Introduction',
            'wbt': 'Video Introduction'
        },
        'V_activate': {
            'default': 'Discussion',
            'seminar': 'Group Discussion',
            'webinar': 'Poll / Chat Discussion',
            'coaching': 'One-on-One Discussion',
            'wbt': 'Self-Assessment Quiz'
        },
        'I': {
            'default': 'Lecture',
            'seminar': 'Lecture with Q&A',
            'webinar': 'Presentation with Chat',
            'coaching': 'Guided Explanation',
            'wbt': 'Interactive Content'
        },
        'V_process': {
            'default': 'Group Exercise',
            'seminar': 'Group Exercise',
            'webinar': 'Breakout Room Exercise',
            'coaching': 'Guided Practice',
            'wbt': 'Interactive Exercise'
        },
        'A_evaluate': {
            'default': 'Q&A / Feedback',
            'seminar': 'Discussion / Feedback Form',
            'webinar': 'Q&A / Survey',
            'coaching': 'Reflection Discussion',
            'wbt': 'Summary Quiz'
        },
        'P': {
            'default': '-',
            'seminar': '-',
            'webinar': '-',
            'coaching': '-',
            'wbt': '-'
        }
    }

    # Materials by format mode
    MATERIALS_BY_FORMAT = {
        'offline': {
            'A': 'PowerPoint',
            'V_activate': 'Flip-Chart, Moderation Cards',
            'I': 'PowerPoint, Handouts',
            'V_process': 'Exercise Sheets, Case Study',
            'A_evaluate': 'Feedback Form',
            'P': '-'
        },
        'online': {
            'A': 'PowerPoint, Screen Share',
            'V_activate': 'Poll Tool, Chat',
            'I': 'PowerPoint, Screen Share',
            'V_process': 'Digital Collaboration Tool (Miro/Mural)',
            'A_evaluate': 'Survey Tool',
            'P': '-'
        },
        'hybrid': {
            'A': 'PowerPoint',
            'V_activate': 'Whiteboard, Digital Board',
            'I': 'PowerPoint, Shared Documents',
            'V_process': 'Exercise Materials (Physical/Digital)',
            'A_evaluate': 'Feedback Form / Survey',
            'P': '-'
        }
    }

    def __init__(self, db_session):
        """Initialize the service with database session"""
        self.db = db_session
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    def _get_level_name(self, level: int) -> str:
        """Convert level number to display name"""
        return self.LEVEL_NAMES.get(level, f'Level {level}')

    def _minutes_to_time(self, total_minutes: int, start_hour: int = 9) -> str:
        """Convert total minutes from start to HH:MM format"""
        hours = start_hour + (total_minutes // 60)
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def _get_format_key(self, format_name: str) -> str:
        """Convert format name to key for mapping lookup"""
        if not format_name:
            return 'default'
        name_lower = format_name.lower()
        if 'seminar' in name_lower:
            return 'seminar'
        elif 'webinar' in name_lower:
            return 'webinar'
        elif 'coaching' in name_lower:
            return 'coaching'
        elif 'wbt' in name_lower or 'web-based' in name_lower:
            return 'wbt'
        elif 'blended' in name_lower:
            return 'seminar'  # Default to seminar for blended
        return 'default'

    def _get_mode_key(self, mode_of_delivery: str) -> str:
        """Convert mode of delivery to key for materials lookup"""
        if not mode_of_delivery:
            return 'offline'
        mode_lower = mode_of_delivery.lower()
        if mode_lower == 'online':
            return 'online'
        elif mode_lower == 'hybrid':
            return 'hybrid'
        return 'offline'

    # =========================================================================
    # AVIVA SEQUENCE GENERATION
    # =========================================================================

    def _generate_aviva_sequence(self, level: int, total_minutes: int) -> List[Dict[str, Any]]:
        """
        Generate AVIVA activity sequence based on level and total duration.

        Returns list of activities with:
        - aviva_phase: A, V, I, or P
        - phase_type: 'arrive', 'activate', 'inform', 'process', 'evaluate', 'break', 'lunch'
        - duration: minutes
        - type: V, U, or P
        """
        activities = []

        # Level 1: 2 hours (120 min) - Simple sequence
        if level == 1:
            activities = [
                {'aviva_phase': 'A', 'phase_type': 'arrive', 'duration': 10, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 20, 'type': 'U'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 30, 'type': 'V'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 30, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 25, 'type': 'U'},
                {'aviva_phase': 'A', 'phase_type': 'evaluate', 'duration': 10, 'type': 'V'},
            ]
            # Add break if there's time
            if total_minutes >= 135:
                activities.insert(3, {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'})

        # Level 2: 4 hours (240 min) - Extended sequence
        elif level == 2:
            activities = [
                {'aviva_phase': 'A', 'phase_type': 'arrive', 'duration': 10, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 20, 'type': 'U'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 30, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 40, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 40, 'type': 'U'},
                {'aviva_phase': 'A', 'phase_type': 'evaluate', 'duration': 15, 'type': 'V'},
            ]

        # Level 4: 8 hours (480 min) - Full day with lunch
        elif level == 4:
            activities = [
                {'aviva_phase': 'A', 'phase_type': 'arrive', 'duration': 15, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 25, 'type': 'U'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 40, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'lunch', 'duration': 60, 'type': 'P'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 15, 'type': 'U'},  # Energizer
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'A', 'phase_type': 'evaluate', 'duration': 20, 'type': 'V'},
            ]

        # Level 6: 16 hours (2 days) - Two full days
        elif level == 6:
            day1 = [
                {'aviva_phase': 'A', 'phase_type': 'arrive', 'duration': 15, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 25, 'type': 'U'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'lunch', 'duration': 60, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 50, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 50, 'type': 'U'},
                {'aviva_phase': 'A', 'phase_type': 'evaluate', 'duration': 15, 'type': 'V'},
            ]
            day2 = [
                {'aviva_phase': 'A', 'phase_type': 'arrive', 'duration': 10, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'activate', 'duration': 20, 'type': 'U'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 50, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 40, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 45, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'lunch', 'duration': 60, 'type': 'P'},
                {'aviva_phase': 'I', 'phase_type': 'inform', 'duration': 35, 'type': 'V'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 50, 'type': 'U'},
                {'aviva_phase': 'P', 'phase_type': 'break', 'duration': 15, 'type': 'P'},
                {'aviva_phase': 'V', 'phase_type': 'process', 'duration': 50, 'type': 'U'},
                {'aviva_phase': 'A', 'phase_type': 'evaluate', 'duration': 25, 'type': 'V'},
            ]
            # Mark day2 activities
            for act in day2:
                act['day'] = 2
            for act in day1:
                act['day'] = 1
            activities = day1 + day2

        else:
            # Default to level 1 pattern
            activities = self._generate_aviva_sequence(1, total_minutes)

        return activities

    def _add_methods_and_materials(
        self,
        activities: List[Dict[str, Any]],
        format_key: str,
        mode_key: str
    ) -> List[Dict[str, Any]]:
        """Add method and material columns based on format and mode"""
        for activity in activities:
            phase = activity['aviva_phase']
            phase_type = activity['phase_type']

            # Determine method lookup key
            if phase == 'V':
                method_key = 'V_activate' if phase_type == 'activate' else 'V_process'
            elif phase == 'A':
                method_key = 'A' if phase_type == 'arrive' else 'A_evaluate'
            else:
                method_key = phase

            # Get method
            method_options = self.METHODS_BY_PHASE_FORMAT.get(method_key, self.METHODS_BY_PHASE_FORMAT.get(phase, {}))
            activity['method'] = method_options.get(format_key, method_options.get('default', 'Lecture'))

            # Get materials - use phase_type for more specific lookup
            if phase == 'V':
                material_key = 'V_activate' if phase_type == 'activate' else 'V_process'
            elif phase == 'A':
                material_key = 'A' if phase_type == 'arrive' else 'A_evaluate'
            else:
                material_key = phase

            materials = self.MATERIALS_BY_FORMAT.get(mode_key, self.MATERIALS_BY_FORMAT['offline'])
            activity['material'] = materials.get(material_key, materials.get(phase, 'PowerPoint'))

        return activities

    def _add_start_times(self, activities: List[Dict[str, Any]], start_hour: int = 9) -> List[Dict[str, Any]]:
        """Add start times to activities"""
        current_minutes = 0
        current_day = 1

        for activity in activities:
            # Check if this is day 2
            if activity.get('day', 1) == 2 and current_day == 1:
                current_day = 2
                current_minutes = 0  # Reset for day 2

            activity['start_time'] = self._minutes_to_time(current_minutes, start_hour)
            current_minutes += activity['duration']

        return activities

    def _add_placeholder_content(
        self,
        activities: List[Dict[str, Any]],
        competency_name: str,
        content_topics: List[str]
    ) -> List[Dict[str, Any]]:
        """Add placeholder content for template export"""
        inform_count = 0
        topic_index = 0

        for activity in activities:
            phase = activity['aviva_phase']
            phase_type = activity['phase_type']

            if phase == 'A' and phase_type == 'arrive':
                activity['content'] = f"[Welcome & Introduction to {competency_name}]"
            elif phase == 'V' and phase_type == 'activate':
                activity['content'] = f"[Prior Knowledge Discussion: {competency_name}]"
            elif phase == 'I':
                if topic_index < len(content_topics):
                    activity['content'] = f"[Content: {content_topics[topic_index]}]"
                    topic_index += 1
                else:
                    activity['content'] = f"[Content Topic {inform_count + 1}]"
                inform_count += 1
            elif phase == 'V' and phase_type == 'process':
                activity['content'] = f"[Practice Exercise {topic_index}]"
            elif phase == 'A' and phase_type == 'evaluate':
                activity['content'] = "[Summary & Evaluation / Q&A]"
            elif phase == 'P':
                if phase_type == 'lunch':
                    activity['content'] = "Lunch Break"
                else:
                    activity['content'] = "Break"

        return activities

    # =========================================================================
    # MODULE DATA RETRIEVAL
    # =========================================================================

    def get_modules_for_aviva(self, organization_id: int) -> Dict[str, Any]:
        """
        Get all training modules ready for AVIVA planning.

        IMPORTANT: Reuses Phase 3's exact data by calling Phase3PlanningService.
        This ensures Phase 4 shows the exact same modules the user configured in Phase 3,
        including the correct view type (competency_level or role_clustered).

        Returns dict with:
        - modules: List of confirmed training modules with AVIVA-specific data
        - view_type: 'competency_level' or 'role_clustered' (from Phase 3 config)
        - scaling_info: Participant scaling information
        """
        # Import Phase 3 service to reuse its logic exactly
        from app.services.phase3_planning_service import Phase3PlanningService
        phase3_service = Phase3PlanningService(self.db)

        # Get Phase 3 config to know which view type was selected
        phase3_config = phase3_service.get_phase3_config(organization_id)
        view_type = phase3_config.get('selected_view', 'competency_level')

        # Get modules using Phase 3's exact logic
        phase3_result = phase3_service.get_training_modules(organization_id, view_type=view_type)

        if phase3_result.get('error'):
            return {
                'modules': [],
                'view_type': view_type,
                'scaling_info': phase3_result.get('scaling_info'),
                'error': phase3_result['error']
            }

        phase3_modules = phase3_result.get('modules', [])
        scaling_info = phase3_result.get('scaling_info', {})

        # Get AVIVA plan status for each module from phase3_training_module
        aviva_status = self._get_aviva_plan_status(organization_id)

        # Filter to only CONFIRMED modules and add Phase 4-specific data
        modules = []
        for m in phase3_modules:
            # Only include confirmed modules with format selection
            if not m.get('confirmed') or not m.get('selected_format_id'):
                continue

            # Build lookup key for AVIVA status
            # Try key with cluster_id first (for role_clustered), then without (for competency_level)
            cluster_id = m.get('cluster_id') or 0
            status_key_with_cluster = f"{m['competency_id']}_{m['target_level']}_{m['pmt_type']}_{cluster_id}"
            status_key_without_cluster = f"{m['competency_id']}_{m['target_level']}_{m['pmt_type']}"

            aviva_info = aviva_status.get(status_key_with_cluster) or aviva_status.get(status_key_without_cluster, {})

            # Get format info
            format_info = self._get_format_info(m.get('selected_format_id'))

            level = m['target_level']
            duration_hours = self.LEVEL_DURATION_HOURS.get(level, 2)
            level_name = self._get_level_name(level)

            # Get module ID - prefer from Phase 3 data, fallback to aviva_status lookup
            module_id = m.get('id') or aviva_info.get('module_id')

            modules.append({
                # Phase 3 data (exactly as displayed in Phase 3)
                'id': module_id,
                'competency_id': m['competency_id'],
                'competency_name': m['competency_name'],
                'target_level': level,
                'level_name': level_name,
                'pmt_type': m['pmt_type'],
                'module_name': m.get('module_name', f"{m['competency_name']} - {level_name}"),
                'users_with_gap': m.get('users_with_gap', 0),
                'estimated_participants': m.get('estimated_participants', 0),
                'roles_needing_training': m.get('roles_needing_training', []),

                # Cluster info (for role_clustered view)
                'cluster_id': m.get('cluster_id'),
                'cluster_name': m.get('cluster_name'),
                'subcluster': m.get('subcluster'),  # 'common' or 'pathway' for Engineers
                'shared_roles_count': m.get('shared_roles_count'),
                'pathway_roles': m.get('pathway_roles'),

                # Format info
                'learning_format_id': m.get('selected_format_id'),
                'learning_format_name': format_info.get('format_name') if format_info else None,
                'mode_of_delivery': format_info.get('mode_of_delivery') if format_info else None,

                # Phase 4-specific data
                'estimated_duration_hours': duration_hours,
                'has_aviva_plan': aviva_info.get('has_aviva_plan', False),
                'learning_objective': m.get('learning_objective', ''),

                # Suitability info from Phase 3
                'suitability': m.get('suitability'),
                'confirmed': True  # Already filtered above
            })

        # Sort by cluster (for role_clustered) then competency, level, pmt_type
        if view_type == 'role_clustered':
            modules.sort(key=lambda m: (
                m.get('cluster_id') or 999,
                m.get('subcluster') or 'z',  # 'common' before 'pathway'
                m['competency_name'],
                m['target_level'],
                m['pmt_type']
            ))
        else:
            modules.sort(key=lambda m: (m['competency_name'], m['target_level'], m['pmt_type']))

        return {
            'modules': modules,
            'view_type': view_type,
            'scaling_info': scaling_info
        }

    def _get_aviva_plan_status(self, organization_id: int) -> Dict[str, Dict]:
        """Get AVIVA plan status for all modules in the organization.

        Creates multiple key formats to support both views:
        - competency_level view uses: "{comp_id}_{level}_{pmt}"
        - role_clustered view uses: "{comp_id}_{level}_{pmt}_{cluster_id}"
        """
        result = self.db.execute(
            text("""
                SELECT
                    tm.id as module_id,
                    tm.competency_id,
                    tm.target_level,
                    tm.pmt_type,
                    tm.training_program_cluster_id as cluster_id,
                    CASE
                        WHEN EXISTS (SELECT 1 FROM phase4_aviva_plan WHERE training_module_id = tm.id)
                        THEN true ELSE false
                    END as has_aviva_plan
                FROM phase3_training_module tm
                WHERE tm.organization_id = :org_id
                  AND tm.confirmed = true
            """),
            {'org_id': organization_id}
        ).fetchall()

        status_lookup = {}
        for row in result:
            module_info = {
                'module_id': row.module_id,
                'has_aviva_plan': row.has_aviva_plan
            }

            # Key WITH cluster_id (for role_clustered view)
            cluster_id = row.cluster_id or 0
            key_with_cluster = f"{row.competency_id}_{row.target_level}_{row.pmt_type}_{cluster_id}"
            status_lookup[key_with_cluster] = module_info

            # Key WITHOUT cluster_id (for competency_level view)
            # Only add this key if cluster_id is 0/NULL to avoid conflicts
            if not row.cluster_id:
                key_without_cluster = f"{row.competency_id}_{row.target_level}_{row.pmt_type}"
                status_lookup[key_without_cluster] = module_info

        return status_lookup

    def _get_format_info(self, format_id: int) -> Optional[Dict]:
        """Get format information by ID"""
        if not format_id:
            return None

        result = self.db.execute(
            text("""
                SELECT id, format_name, short_name, mode_of_delivery
                FROM learning_format
                WHERE id = :id
            """),
            {'id': format_id}
        ).fetchone()

        if result:
            return {
                'id': result.id,
                'format_name': result.format_name,
                'short_name': result.short_name,
                'mode_of_delivery': result.mode_of_delivery
            }
        return None

    def get_module_preview(self, module_id: int) -> Dict[str, Any]:
        """
        Get detailed preview for a single module including learning objectives and content topics.
        Also retrieves learning objective from Phase 2's generated data.
        For Method/Tool modules, extracts the PMT-specific learning objective.
        """
        # Get module info including cluster data for role-clustered view
        module = self.db.execute(
            text("""
                SELECT
                    tm.id,
                    tm.organization_id,
                    tm.competency_id,
                    c.competency_name,
                    tm.target_level,
                    tm.pmt_type,
                    tm.selected_format_id,
                    lf.format_name,
                    lf.mode_of_delivery,
                    lf.communication_type,
                    tm.estimated_participants,
                    tm.training_program_cluster_id as cluster_id,
                    tpc.training_program_name as cluster_name
                FROM phase3_training_module tm
                JOIN competency c ON tm.competency_id = c.id
                LEFT JOIN learning_format lf ON tm.selected_format_id = lf.id
                LEFT JOIN training_program_cluster tpc ON tm.training_program_cluster_id = tpc.id
                WHERE tm.id = :module_id
            """),
            {'module_id': module_id}
        ).fetchone()

        if not module:
            return None

        level = module.target_level
        pmt_type = module.pmt_type
        duration_hours = self.LEVEL_DURATION_HOURS.get(level, 2)

        # Get learning objective from competency_indicators (template/baseline)
        learning_obj = self.db.execute(
            text("""
                SELECT indicator_en
                FROM competency_indicators
                WHERE competency_id = :comp_id AND level = :level
            """),
            {'comp_id': module.competency_id, 'level': str(level)}
        ).fetchone()

        # Get learning objective from Phase 2 generated data
        # This includes PMT-specific objectives if available
        generated_lo = None
        generated_lo_pmt = None  # PMT-specific objective
        pmt_breakdown = None
        lo_result = self.db.execute(
            text("""
                SELECT objectives_data
                FROM generated_learning_objectives
                WHERE organization_id = :org_id
                ORDER BY generated_at DESC
                LIMIT 1
            """),
            {'org_id': module.organization_id}
        ).fetchone()

        if lo_result and lo_result.objectives_data:
            objectives_data = lo_result.objectives_data
            if isinstance(objectives_data, str):
                objectives_data = json.loads(objectives_data)

            data = objectives_data.get('data', objectives_data)
            main_pyramid = data.get('main_pyramid', {})
            levels = main_pyramid.get('levels', {})
            level_data = levels.get(str(level), {})

            for comp in level_data.get('competencies', []):
                if comp.get('competency_id') == module.competency_id:
                    lo_data = comp.get('learning_objective', {})
                    generated_lo = lo_data.get('objective_text', '')
                    pmt_breakdown = lo_data.get('pmt_breakdown')

                    # Extract PMT-specific learning objective if module has pmt_type
                    if pmt_type in ('method', 'tool') and pmt_breakdown:
                        generated_lo_pmt = pmt_breakdown.get(pmt_type)
                    break

        # Determine the best learning objective to show
        # Priority: PMT-specific > Generated unified > Template
        final_learning_objective = None
        if pmt_type in ('method', 'tool') and generated_lo_pmt:
            final_learning_objective = generated_lo_pmt
        elif generated_lo:
            final_learning_objective = generated_lo
        elif learning_obj:
            final_learning_objective = learning_obj.indicator_en

        # Get content topics from baseline
        content_result = self.db.execute(
            text("""
                SELECT content_topics
                FROM competency_content_baseline
                WHERE competency_id = :comp_id
            """),
            {'comp_id': module.competency_id}
        ).fetchone()

        content_topics = content_result.content_topics if content_result else []

        # Generate suggested AVIVA sequence (preview) with methods
        sequence = self._generate_aviva_sequence(level, duration_hours * 60)

        # Add methods and materials to the sequence
        format_key = self._get_format_key(module.format_name)
        mode_key = self._get_mode_key(module.mode_of_delivery)
        sequence = self._add_methods_and_materials(sequence, format_key, mode_key)

        # Construct module name
        level_name = self._get_level_name(level)
        if pmt_type == 'combined':
            module_name = f"{module.competency_name} - {level_name}"
        else:
            module_name = f"{module.competency_name} - {level_name} - {pmt_type.title()}"

        # Map activity types to human-readable labels
        # V = Vortrag (Frontal/Lecture), U = Ubung (Active/Exercise), P = Pause (Break)
        type_labels = {'V': 'Frontal', 'U': 'Active', 'P': 'Break'}

        return {
            'id': module.id,
            'organization_id': module.organization_id,
            'competency_id': module.competency_id,
            'competency_name': module.competency_name,
            'module_name': module_name,
            'target_level': level,
            'level_name': level_name,
            'pmt_type': pmt_type,
            'learning_format': {
                'id': module.selected_format_id,
                'name': module.format_name,
                'mode_of_delivery': module.mode_of_delivery,
                'communication_type': module.communication_type
            },
            'learning_objective': final_learning_objective,
            'learning_objective_unified': generated_lo,
            'learning_objective_template': learning_obj.indicator_en if learning_obj else None,
            'pmt_breakdown': pmt_breakdown,
            'content_topics': content_topics,
            'estimated_duration_hours': duration_hours,
            'estimated_participants': module.estimated_participants,
            # Cluster info for role-clustered view
            'cluster_id': module.cluster_id,
            'cluster_name': module.cluster_name,
            'subcluster': None,  # Will be populated from Phase 3 modules data if available
            'suggested_activity_count': len(sequence),
            'suggested_sequence': [
                {
                    'aviva': act['aviva_phase'],
                    'phase_type': act['phase_type'],
                    'duration': act['duration'],
                    'type': type_labels.get(act['type'], act['type']),
                    'method': act.get('method', ''),
                    'material': act.get('material', '')
                }
                for act in sequence
            ]
        }

    # =========================================================================
    # AVIVA PLAN GENERATION
    # =========================================================================

    def generate_aviva_plan(
        self,
        module_id: int,
        generation_method: str = 'template',
        start_time_hour: int = 9
    ) -> Dict[str, Any]:
        """
        Generate AVIVA plan for a single module.

        Args:
            module_id: Training module ID
            generation_method: 'template' or 'genai'
            start_time_hour: Starting hour (default 9 for 09:00)

        Returns:
            Complete AVIVA plan with activities
        """
        # Get module preview (includes all needed data)
        preview = self.get_module_preview(module_id)
        if not preview:
            raise ValueError(f"Module {module_id} not found")

        level = preview['target_level']
        total_minutes = preview['estimated_duration_hours'] * 60
        format_key = self._get_format_key(preview['learning_format']['name'])
        mode_key = self._get_mode_key(preview['learning_format']['mode_of_delivery'])

        # Generate AVIVA sequence
        activities = self._generate_aviva_sequence(level, total_minutes)

        # Add methods and materials
        activities = self._add_methods_and_materials(activities, format_key, mode_key)

        # Add start times
        activities = self._add_start_times(activities, start_time_hour)

        # Add content
        if generation_method == 'genai':
            activities = self._generate_genai_content(
                activities,
                preview['competency_name'],
                level,
                preview['learning_objective'],
                preview['content_topics'],
                preview['pmt_type'],
                preview['learning_format']['name']
            )
        else:
            # Template mode - add placeholders
            activities = self._add_placeholder_content(
                activities,
                preview['competency_name'],
                preview['content_topics']
            )

        # Build module name
        module_name = f"{preview['competency_name']} - {preview['level_name']}"
        if preview['pmt_type'] and preview['pmt_type'] != 'combined':
            module_name += f" ({preview['pmt_type'].capitalize()})"

        # Build complete AVIVA plan
        aviva_plan = {
            'module_id': module_id,
            'module_name': module_name,
            'competency_id': preview['competency_id'],
            'competency_name': preview['competency_name'],
            'target_level': level,
            'level_name': preview['level_name'],
            'pmt_type': preview['pmt_type'],
            'learning_format': preview['learning_format']['name'],
            'mode_of_delivery': preview['learning_format']['mode_of_delivery'],
            'total_duration_minutes': total_minutes,
            'learning_objective': preview['learning_objective'],
            'content_topics': preview['content_topics'],
            # Cluster info for role-clustered view
            'cluster_id': preview.get('cluster_id'),
            'cluster_name': preview.get('cluster_name'),
            'subcluster': preview.get('subcluster'),
            'generated_by': generation_method,
            'generated_at': datetime.now().isoformat(),
            'activities': [
                {
                    'row': i + 1,
                    'start_time': act['start_time'],
                    'duration_min': act['duration'],
                    'type': act['type'],
                    'aviva_phase': act['aviva_phase'],
                    'content': act.get('content', ''),
                    'method': act.get('method', ''),
                    'material': act.get('material', ''),
                    'day': act.get('day', 1)
                }
                for i, act in enumerate(activities)
            ]
        }

        return aviva_plan

    def _generate_genai_content(
        self,
        activities: List[Dict[str, Any]],
        competency_name: str,
        level: int,
        learning_objective: str,
        content_topics: List[str],
        pmt_type: str,
        format_name: str
    ) -> List[Dict[str, Any]]:
        """Generate content using OpenAI for each AVIVA activity"""

        # Build sequence description for prompt
        sequence_desc = []
        for i, act in enumerate(activities):
            sequence_desc.append({
                'row': i + 1,
                'aviva_phase': act['aviva_phase'],
                'phase_type': act['phase_type'],
                'duration': act['duration'],
                'type': act['type']
            })

        prompt = f"""You are creating AVIVA didactic content for a Systems Engineering training module.

== MODULE CONTEXT ==
Module: {competency_name} - Level {level} ({self._get_level_name(level)})
PMT Focus: {pmt_type or 'combined'}
Learning Format: {format_name or 'Seminar'}
Total Duration: {sum(a['duration'] for a in activities)} minutes

== LEARNING OBJECTIVE ==
{learning_objective or 'Enable participants to understand and apply this competency.'}

== CONTENT TOPICS (Baseline) ==
{chr(10).join('- ' + t for t in content_topics) if content_topics else '- General competency topics'}

== INSTRUCTIONS ==
Generate specific, actionable content for the "What (Content)" column for each activity row.

Guidelines by AVIVA phase:
- A (Arrive): Welcome, set expectations, preview learning objectives
- V (Activate): Questions or activities to surface existing knowledge
- I (Inform): Specific topic from content list - adapt depth based on level:
  * Level 1: Overview, definitions, awareness
  * Level 2: Explanations, connections, examples
  * Level 4: Practical application, hands-on guidance
  * Level 6: Strategic thinking, teaching others
- V (Process): Concrete exercise description tied to previous content
- A (Evaluate): Summary, key takeaways, reflection
- P (Break/Lunch): Just "Break" or "Lunch Break"

Keep each description to 1-2 sentences. Be specific to {competency_name}.

== ACTIVITY SEQUENCE ==
{json.dumps(sequence_desc, indent=2)}

== OUTPUT FORMAT ==
Return ONLY a valid JSON array with content for each row:
[
  {{"row": 1, "content": "Welcome: Introduction to {competency_name}..."}},
  {{"row": 2, "content": "Discussion: What experience do you have with..."}},
  ...
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer for Systems Engineering training programs. Generate clear, specific didactic content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON from response
            # Handle markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            generated = json.loads(content)

            # Map generated content to activities
            content_map = {item['row']: item['content'] for item in generated}
            for i, act in enumerate(activities):
                row = i + 1
                if row in content_map:
                    act['content'] = content_map[row]
                else:
                    # Fallback to placeholder
                    act['content'] = f"[{act['aviva_phase']} Activity {row}]"

        except Exception as e:
            current_app.logger.error(f"GenAI content generation failed: {e}")
            # Fallback to placeholder content
            activities = self._add_placeholder_content(
                activities,
                competency_name,
                content_topics
            )

        return activities

    # =========================================================================
    # SAVE AND RETRIEVE PLANS
    # =========================================================================

    def save_aviva_plan(self, organization_id: int, module_id: int, aviva_plan: Dict[str, Any]) -> int:
        """Save AVIVA plan to database"""
        result = self.db.execute(
            text("""
                INSERT INTO phase4_aviva_plan (organization_id, training_module_id, generated_by, aviva_content)
                VALUES (:org_id, :module_id, :generated_by, :content)
                ON CONFLICT (training_module_id) DO UPDATE
                SET generated_by = EXCLUDED.generated_by,
                    aviva_content = EXCLUDED.aviva_content,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """),
            {
                'org_id': organization_id,
                'module_id': module_id,
                'generated_by': aviva_plan['generated_by'],
                'content': json.dumps(aviva_plan)
            }
        )
        self.db.commit()
        return result.fetchone().id

    def get_aviva_plan(self, module_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve saved AVIVA plan for a module"""
        result = self.db.execute(
            text("""
                SELECT aviva_content, generated_by, created_at, updated_at
                FROM phase4_aviva_plan
                WHERE training_module_id = :module_id
            """),
            {'module_id': module_id}
        ).fetchone()

        if result:
            plan = result.aviva_content
            plan['db_generated_by'] = result.generated_by
            plan['created_at'] = result.created_at.isoformat() if result.created_at else None
            plan['updated_at'] = result.updated_at.isoformat() if result.updated_at else None
            return plan
        return None

    # =========================================================================
    # EXCEL EXPORT
    # =========================================================================

    def export_aviva_to_excel(self, aviva_plans: List[Dict[str, Any]], organization_id: int = None) -> io.BytesIO:
        """
        Export AVIVA plans to Excel file.

        Args:
            aviva_plans: List of AVIVA plan dictionaries
            organization_id: Optional organization ID to include Phase 3 summary data

        Returns:
            BytesIO buffer containing Excel file
        """
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        ws = wb.active
        ws.title = "Summary"

        # Styles
        TITLE_FONT = Font(size=16, bold=True)
        SUBTITLE_FONT = Font(size=11, bold=True)
        LABEL_FONT = Font(bold=True)
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="455A64", end_color="455A64", fill_type="solid")  # Blue Grey
        module_header_fill = PatternFill(start_color="607D8B", end_color="607D8B", fill_type="solid")
        aviva_header_fill = PatternFill(start_color="78909C", end_color="78909C", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Level names mapping
        LEVEL_NAMES = {1: 'Knowing', 2: 'Understanding', 4: 'Applying', 6: 'Mastering'}

        row = 1

        # ===== TITLE =====
        ws.merge_cells('A1:G1')
        ws['A1'] = 'SE-QPT Phase 4: AVIVA Didactic Plans Export'
        ws['A1'].font = TITLE_FONT
        ws['A1'].alignment = Alignment(horizontal='center')
        row = 3

        # ===== PHASE 3 SUMMARY DATA (if organization_id provided) =====
        org_name = f'Organization_{organization_id}' if organization_id else 'Unknown'
        view_type = 'competency_level'
        all_strategies = []
        target_group_size = 0
        format_distribution = {}
        milestones = []

        if organization_id:
            # Get organization name
            org_result = self.db.execute(
                text("SELECT organization_name FROM organization WHERE id = :org_id"),
                {'org_id': organization_id}
            ).fetchone()
            if org_result:
                org_name = org_result.organization_name

            # Get Phase 3 output data
            from app.services.phase3_planning_service import Phase3PlanningService
            phase3_service = Phase3PlanningService(self.db)
            try:
                output = phase3_service.get_phase3_output(organization_id)
                config = output.get('config', {})
                summary = output.get('summary', {})
                timeline = output.get('timeline', {})

                view_type = config.get('selected_view', 'competency_level')
                all_strategies = summary.get('all_strategies', [summary.get('strategy_name', '')])
                target_group_size = summary.get('target_group_size', 0)
                format_distribution = summary.get('format_distribution', {})
                milestones = timeline.get('milestones', [])
            except Exception as e:
                logging.warning(f"Could not get Phase 3 data: {e}")

        # Summary info
        ws[f'A{row}'] = 'Organization:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = org_name
        row += 1

        ws[f'A{row}'] = 'Training View:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = 'Role-Clustered' if view_type == 'role_clustered' else 'Competency-Level'
        row += 1

        if all_strategies:
            ws[f'A{row}'] = 'Selected Strategies:'
            ws[f'A{row}'].font = LABEL_FONT
            ws[f'B{row}'] = ', '.join(all_strategies) if all_strategies else 'Not Selected'
            ws.merge_cells(f'B{row}:G{row}')
            row += 1

        ws[f'A{row}'] = 'Target Group Size:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = f"{target_group_size} participants"
        row += 1

        ws[f'A{row}'] = 'Total Training Modules:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = len(aviva_plans)
        row += 1

        if format_distribution:
            ws[f'A{row}'] = 'Format Distribution:'
            ws[f'A{row}'].font = LABEL_FONT
            format_str = ', '.join([f"{k}: {v}" for k, v in format_distribution.items()])
            ws[f'B{row}'] = format_str
            ws.merge_cells(f'B{row}:G{row}')
            row += 1

        ws[f'A{row}'] = 'Export Date:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        row += 2

        # Set first column width for labels
        ws.column_dimensions['A'].width = 22

        # ===== MODULES TABLE =====
        ws[f'A{row}'] = 'Training Modules Overview'
        ws[f'A{row}'].font = SUBTITLE_FONT
        row += 1

        # Check if role-clustered view
        is_role_clustered = view_type == 'role_clustered'

        # Sort plans - by cluster for role_clustered, by competency_id otherwise
        if is_role_clustered:
            # Define cluster order
            cluster_order = {'SE for Engineers': 0, 'SE for Managers': 1, 'SE for Interfacing Partners': 2}
            sorted_plans = sorted(aviva_plans, key=lambda p: (
                cluster_order.get(p.get('cluster_name', ''), 99),
                p.get('subcluster') or 'z',  # 'common' before 'pathway'
                p.get('competency_id', 0)
            ))
        else:
            sorted_plans = sorted(aviva_plans, key=lambda p: p.get('competency_id', 0))

        # Module summary headers - different for role-clustered vs competency-level
        if is_role_clustered:
            summary_headers = ['#', 'Training Program', 'Module Type', 'Module', 'Level', 'Format', 'Roles', 'Est. Participants', 'Duration (h)', 'Activities']
            col_widths = [4, 20, 13, 40, 3, 32, 45, 12, 10, 9]
            center_cols = [1, 5, 8, 9, 10]
        else:
            summary_headers = ['#', 'Module', 'Level', 'Format', 'Roles', 'Est. Participants', 'Duration (h)', 'Activities']
            col_widths = [4, 42, 3, 30, 50, 12, 10, 9]
            center_cols = [1, 3, 6, 7, 8]

        for col, header in enumerate(summary_headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.column_dimensions[get_column_letter(col)].width = col_widths[col - 1]
        row += 1

        # Style for Module Type column (role-clustered only)
        COMMON_BASE_FILL = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
        ROLE_SPECIFIC_FILL = PatternFill(start_color='DEEBF7', end_color='DEEBF7', fill_type='solid')

        for idx, plan in enumerate(sorted_plans, 1):
            level_num = plan.get('target_level', 0)
            level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')

            # Get estimated participants from plan or module info
            est_participants = plan.get('estimated_participants', 0)

            # Build module display name without level (since Level is a separate column)
            # Format: "Competency Name" or "Competency Name (Method/Tool)"
            competency_name = plan.get('competency_name', '')
            pmt_type = plan.get('pmt_type', '')
            if pmt_type and pmt_type.lower() not in ['combined', '', 'null', 'none']:
                module_display_name = f"{competency_name} ({pmt_type.capitalize()})"
            else:
                module_display_name = competency_name

            # Get roles
            roles = plan.get('roles_needing_training', [])
            roles_str = ', '.join(roles) if roles and isinstance(roles, list) else ''

            if is_role_clustered:
                # Determine module type
                cluster_name = plan.get('cluster_name', 'Uncategorized')
                subcluster = plan.get('subcluster')
                if 'Engineer' in cluster_name:
                    module_type = 'Common Base' if subcluster == 'common' else 'Role-Specific'
                else:
                    module_type = '-'

                ws.cell(row=row, column=1, value=idx).border = thin_border
                ws.cell(row=row, column=2, value=cluster_name).border = thin_border
                type_cell = ws.cell(row=row, column=3, value=module_type)
                type_cell.border = thin_border
                # Apply color fill for module type
                if module_type == 'Common Base':
                    type_cell.fill = COMMON_BASE_FILL
                elif module_type == 'Role-Specific':
                    type_cell.fill = ROLE_SPECIFIC_FILL
                ws.cell(row=row, column=4, value=module_display_name).border = thin_border
                ws.cell(row=row, column=5, value=level_name).border = thin_border
                ws.cell(row=row, column=6, value=plan.get('learning_format', '')).border = thin_border
                roles_cell = ws.cell(row=row, column=7, value=roles_str)
                roles_cell.border = thin_border
                roles_cell.alignment = Alignment(wrap_text=True)
                ws.cell(row=row, column=8, value=est_participants).border = thin_border
                ws.cell(row=row, column=9, value=round(plan['total_duration_minutes'] / 60, 1)).border = thin_border
                ws.cell(row=row, column=10, value=len(plan.get('activities', []))).border = thin_border
            else:
                ws.cell(row=row, column=1, value=idx).border = thin_border
                ws.cell(row=row, column=2, value=module_display_name).border = thin_border
                ws.cell(row=row, column=3, value=level_name).border = thin_border
                ws.cell(row=row, column=4, value=plan.get('learning_format', '')).border = thin_border
                roles_cell = ws.cell(row=row, column=5, value=roles_str)
                roles_cell.border = thin_border
                roles_cell.alignment = Alignment(wrap_text=True)
                ws.cell(row=row, column=6, value=est_participants).border = thin_border
                ws.cell(row=row, column=7, value=round(plan['total_duration_minutes'] / 60, 1)).border = thin_border
                ws.cell(row=row, column=8, value=len(plan.get('activities', []))).border = thin_border

            # Center align certain columns
            for col in center_cols:
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
            row += 1

        row += 2

        # ===== TIMELINE SECTION =====
        if milestones:
            ws[f'A{row}'] = 'Implementation Timeline'
            ws[f'A{row}'].font = SUBTITLE_FONT
            row += 1

            timeline_headers = ['#', 'Milestone', 'Date', 'Quarter', 'Description']
            timeline_widths = [5, 35, 15, 18, 30]
            for col, header in enumerate(timeline_headers, 1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                ws.column_dimensions[get_column_letter(col)].width = max(
                    ws.column_dimensions[get_column_letter(col)].width or 0,
                    timeline_widths[col - 1]
                )
            row += 1

            for idx, milestone in enumerate(milestones, 1):
                ws.cell(row=row, column=1, value=idx).border = thin_border
                ws.cell(row=row, column=2, value=milestone.get('milestone_name', milestone.get('name', ''))).border = thin_border
                ws.cell(row=row, column=3, value=milestone.get('estimated_date', '')).border = thin_border
                ws.cell(row=row, column=4, value=milestone.get('quarter', '')).border = thin_border
                ws.cell(row=row, column=5, value=milestone.get('milestone_description', milestone.get('description', ''))).border = thin_border

                for col in [1, 3, 4]:
                    ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
                ws.cell(row=row, column=5).alignment = Alignment(wrap_text=True)
                row += 1

        # ===== SECOND SHEET: ALL AVIVA PLANS COMBINED =====
        ws_aviva = wb.create_sheet(title="AVIVA Plans")
        aviva_row = 1

        # Sheet title
        ws_aviva.merge_cells('A1:G1')
        ws_aviva['A1'] = 'Detailed AVIVA Didactic Plans'
        ws_aviva['A1'].font = TITLE_FONT
        ws_aviva['A1'].alignment = Alignment(horizontal='center')
        aviva_row = 3

        # AVIVA headers
        aviva_headers = ['Start', 'Min', 'Type', 'AVIVA', 'What (Content)', 'How (Method)', 'Material']
        aviva_col_widths = [18, 8, 10, 15, 50, 25, 45]  # First column wider for labels, Material wider

        # Set column widths for AVIVA sheet
        for col, width in enumerate(aviva_col_widths, 1):
            ws_aviva.column_dimensions[get_column_letter(col)].width = width

        # Write each module's AVIVA plan sequentially
        for plan in sorted_plans:
            # Module header section
            level_num = plan.get('target_level', 0)
            level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')

            ws_aviva.merge_cells(f'A{aviva_row}:G{aviva_row}')
            cell = ws_aviva[f'A{aviva_row}']
            cell.value = f"Module: {plan['module_name']}"
            cell.font = Font(bold=True, size=12, color="FFFFFF")
            cell.fill = module_header_fill
            cell.alignment = Alignment(horizontal='left', vertical='center')
            aviva_row += 1

            # Module details - add Training Program for role-clustered view
            if is_role_clustered and plan.get('cluster_name'):
                ws_aviva[f'A{aviva_row}'] = 'Training Program:'
                ws_aviva[f'A{aviva_row}'].font = LABEL_FONT
                ws_aviva[f'B{aviva_row}'] = plan.get('cluster_name', '')
                ws_aviva[f'D{aviva_row}'] = 'Module Type:'
                ws_aviva[f'D{aviva_row}'].font = LABEL_FONT
                cluster_name = plan.get('cluster_name', '')
                subcluster = plan.get('subcluster')
                if 'Engineer' in cluster_name:
                    module_type = 'Common Base' if subcluster == 'common' else 'Role-Specific'
                else:
                    module_type = '-'
                ws_aviva[f'E{aviva_row}'] = module_type
                aviva_row += 1

            ws_aviva[f'A{aviva_row}'] = 'Level:'
            ws_aviva[f'A{aviva_row}'].font = LABEL_FONT
            ws_aviva[f'B{aviva_row}'] = level_name
            ws_aviva[f'C{aviva_row}'] = 'Format:'
            ws_aviva[f'C{aviva_row}'].font = LABEL_FONT
            ws_aviva[f'D{aviva_row}'] = plan.get('learning_format', 'N/A')
            ws_aviva[f'E{aviva_row}'] = 'Duration:'
            ws_aviva[f'E{aviva_row}'].font = LABEL_FONT
            ws_aviva[f'F{aviva_row}'] = f"{plan['total_duration_minutes']} min ({round(plan['total_duration_minutes'] / 60, 1)} h)"
            aviva_row += 1

            ws_aviva[f'A{aviva_row}'] = 'Learning Objective:'
            ws_aviva[f'A{aviva_row}'].font = LABEL_FONT
            ws_aviva.merge_cells(f'B{aviva_row}:G{aviva_row}')
            lo_cell = ws_aviva[f'B{aviva_row}']
            lo_cell.value = plan.get('learning_objective', 'N/A')
            lo_cell.alignment = Alignment(wrap_text=True)
            aviva_row += 1

            # Content Topics if available
            content_topics = plan.get('content_topics', [])
            if content_topics:
                ws_aviva[f'A{aviva_row}'] = 'Content Topics:'
                ws_aviva[f'A{aviva_row}'].font = LABEL_FONT
                ws_aviva.merge_cells(f'B{aviva_row}:G{aviva_row}')
                topics_cell = ws_aviva[f'B{aviva_row}']
                topics_cell.value = ', '.join(content_topics)
                topics_cell.alignment = Alignment(wrap_text=True)
                aviva_row += 1

            aviva_row += 1  # Empty row before table

            # AVIVA table headers
            for col, header in enumerate(aviva_headers, 1):
                cell = ws_aviva.cell(row=aviva_row, column=col, value=header)
                cell.font = header_font
                cell.fill = aviva_header_fill
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', vertical='center')
            aviva_row += 1

            # AVIVA activities
            activities = plan.get('activities', [])
            for activity in activities:
                ws_aviva.cell(row=aviva_row, column=1, value=activity.get('start_time', '')).border = thin_border
                ws_aviva.cell(row=aviva_row, column=2, value=activity.get('duration_min', 0)).border = thin_border
                ws_aviva.cell(row=aviva_row, column=3, value=activity.get('type', '')).border = thin_border
                ws_aviva.cell(row=aviva_row, column=4, value=activity.get('aviva_phase', '')).border = thin_border

                content_cell = ws_aviva.cell(row=aviva_row, column=5, value=activity.get('content', ''))
                content_cell.border = thin_border
                content_cell.alignment = Alignment(wrap_text=True)

                ws_aviva.cell(row=aviva_row, column=6, value=activity.get('method', '')).border = thin_border
                ws_aviva.cell(row=aviva_row, column=7, value=activity.get('material', '')).border = thin_border

                # Center align certain columns
                for col in [1, 2, 3, 4]:
                    ws_aviva.cell(row=aviva_row, column=col).alignment = Alignment(horizontal='center')

                aviva_row += 1

            # Add 3 empty rows between modules
            aviva_row += 3

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    # =========================================================================
    # PHASE 4 CONFIG
    # =========================================================================

    def get_phase4_config(self, organization_id: int) -> Dict[str, Any]:
        """Get or create Phase 4 configuration"""
        result = self.db.execute(
            text("""
                SELECT id, task1_status, task2_status, aviva_generation_method,
                       created_at, updated_at
                FROM phase4_config
                WHERE organization_id = :org_id
            """),
            {'org_id': organization_id}
        ).fetchone()

        if result:
            return {
                'id': result.id,
                'task1_status': result.task1_status,
                'task2_status': result.task2_status,
                'aviva_generation_method': result.aviva_generation_method,
                'created_at': result.created_at.isoformat() if result.created_at else None,
                'updated_at': result.updated_at.isoformat() if result.updated_at else None
            }

        # Create default config
        self.db.execute(
            text("""
                INSERT INTO phase4_config (organization_id)
                VALUES (:org_id)
                ON CONFLICT (organization_id) DO NOTHING
            """),
            {'org_id': organization_id}
        )
        self.db.commit()

        return {
            'id': None,
            'task1_status': 'not_started',
            'task2_status': 'not_started',
            'aviva_generation_method': None,
            'created_at': None,
            'updated_at': None
        }

    def update_phase4_config(self, organization_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update Phase 4 configuration"""
        set_clauses = []
        params = {'org_id': organization_id}

        for key in ['task1_status', 'task2_status', 'aviva_generation_method']:
            if key in updates:
                set_clauses.append(f"{key} = :{key}")
                params[key] = updates[key]

        if set_clauses:
            query = f"""
                UPDATE phase4_config
                SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE organization_id = :org_id
            """
            self.db.execute(text(query), params)
            self.db.commit()

        return self.get_phase4_config(organization_id)
