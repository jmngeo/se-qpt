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

    Query Params:
        view_type: 'competency_level' (default) or 'role_clustered'

    Returns modules with gap data, participant estimates, and existing selections.
    For role_clustered view, returns separate modules per training cluster.
    """
    try:
        view_type = request.args.get('view_type', 'competency_level')

        service = _get_service()
        result = service.get_training_modules(organization_id, view_type=view_type)

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
            "confirmed": true,
            "cluster_id": null | 1  // Optional: for role_clustered view
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

        # Save selection (with optional cluster_id for role_clustered view)
        result = service.save_format_selection(
            organization_id=data['organization_id'],
            competency_id=data['competency_id'],
            target_level=data['target_level'],
            pmt_type=data['pmt_type'],
            format_id=data['format_id'],
            suitability=suitability,
            estimated_participants=data.get('estimated_participants', 0),
            confirmed=data.get('confirmed', False),
            cluster_id=data.get('cluster_id')
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


@phase3_planning_bp.route('/phase3/complete-task2/<int:organization_id>', methods=['POST'])
@jwt_required()
def complete_task2(organization_id):
    """
    Mark Task 2 (Learning Format Selection) as completed.
    Called when user clicks 'Continue to Task 3' after configuring all modules.
    """
    try:
        service = _get_service()
        result = service.mark_task2_completed(organization_id)
        return jsonify({
            'success': True,
            'message': 'Task 2 marked as completed'
        })
    except Exception as e:
        current_app.logger.error(f"Error completing Task 2: {e}")
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


# ==============================================================================
# Export to Excel
# ==============================================================================

@phase3_planning_bp.route('/phase3/export/<int:organization_id>', methods=['GET'])
@jwt_required()
def export_phase3_excel(organization_id):
    """
    Export Phase 3 Macro Planning data to Excel.

    Only available after all 3 tasks are completed.
    Single sheet with Summary header + Training Modules table.
    For Role-Clustered view: groups modules by Training Program Cluster.
    """
    from flask import send_file
    from datetime import datetime
    import io

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Excel export not available',
            'message': 'openpyxl library not installed'
        }), 500

    try:
        service = _get_service()

        # Get Phase 3 output data
        output = service.get_phase3_output(organization_id)
        config = output.get('config', {})
        summary = output.get('summary', {})
        modules = output.get('modules', [])
        timeline = output.get('timeline', {})

        # Check if all tasks are completed
        completion = summary.get('completion', {})
        if not (completion.get('task1') and completion.get('task2') and completion.get('task3')):
            return jsonify({
                'success': False,
                'error': 'Export only available after completing all Phase 3 tasks'
            }), 400

        # Get organization name
        org_result = db.session.execute(
            db.text("SELECT organization_name FROM organization WHERE id = :org_id"),
            {'org_id': organization_id}
        ).fetchone()
        org_name = org_result.organization_name if org_result else f'Organization_{organization_id}'

        # Determine view type
        selected_view = config.get('selected_view', 'competency_level')
        is_role_clustered = selected_view == 'role_clustered'

        # Style definitions
        HEADER_FILL = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        HEADER_FONT = Font(bold=True, color='FFFFFF')
        TITLE_FONT = Font(size=16, bold=True)
        SUBTITLE_FONT = Font(size=11, bold=True)
        LABEL_FONT = Font(bold=True)
        CLUSTER_FILL = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
        CLUSTER_FONT = Font(bold=True, size=11)
        THIN_BORDER = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Level name mapping
        LEVEL_NAMES = {1: 'Knowing', 2: 'Understanding', 4: 'Applying'}

        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Phase 3 - Macro Planning'

        row = 1

        # ===== TITLE =====
        ws.merge_cells('A1:F1')
        ws['A1'] = 'SE-QPT Phase 3: Macro Planning Export'
        ws['A1'].font = TITLE_FONT
        ws['A1'].alignment = Alignment(horizontal='center')
        row = 3

        # ===== SUMMARY SECTION =====
        ws[f'A{row}'] = 'Organization:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = org_name
        row += 1

        ws[f'A{row}'] = 'Training View:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = 'Role-Clustered' if is_role_clustered else 'Competency-Level'
        row += 1

        ws[f'A{row}'] = 'Selected Strategies:'
        ws[f'A{row}'].font = LABEL_FONT
        all_strategies = summary.get('all_strategies', [summary.get('strategy_name', 'Not Selected')])
        ws[f'B{row}'] = ', '.join(all_strategies) if all_strategies else 'Not Selected'
        ws.merge_cells(f'B{row}:F{row}')
        row += 1

        ws[f'A{row}'] = 'Target Group Size:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = f"{summary.get('target_group_size', 0)} participants"
        row += 1

        ws[f'A{row}'] = 'Total Training Modules:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = summary.get('total_modules', 0)
        row += 1

        # Format distribution
        format_dist = summary.get('format_distribution', {})
        if format_dist:
            ws[f'A{row}'] = 'Format Distribution:'
            ws[f'A{row}'].font = LABEL_FONT
            format_str = ', '.join([f"{k}: {v}" for k, v in format_dist.items()])
            ws[f'B{row}'] = format_str
            ws.merge_cells(f'B{row}:F{row}')
            row += 1

        ws[f'A{row}'] = 'Export Date:'
        ws[f'A{row}'].font = LABEL_FONT
        ws[f'B{row}'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        row += 2

        # ===== SCALED PARTICIPANT ESTIMATION NOTE =====
        # Get scaling info from training_modules
        training_modules_data = output.get('training_modules', {})
        scaling_info = training_modules_data.get('scaling_info', {})
        if scaling_info and scaling_info.get('scaling_factor') and scaling_info.get('scaling_factor', 1) > 1:
            NOTE_FILL = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
            NOTE_BORDER = Border(
                left=Side(style='thin', color='E6A23C'),
                right=Side(style='thin', color='E6A23C'),
                top=Side(style='thin', color='E6A23C'),
                bottom=Side(style='thin', color='E6A23C')
            )

            ws[f'A{row}'] = 'Note: Scaled Participant Estimation'
            ws[f'A{row}'].font = Font(bold=True, color='E6A23C')
            row += 1

            assessed = scaling_info.get('actual_assessed_users', 0)
            target = scaling_info.get('target_group_size', 0)
            factor = scaling_info.get('scaling_factor', 1)

            note_lines = [
                f"Only {assessed} out of {target} employees in the target group completed the competency assessment.",
                f"Participant counts are scaled by a factor of {factor:.1f}x to estimate organization-wide training needs.",
                "Actual participation may vary based on individual competency gaps and role assignments.",
                "These estimates should be used for planning purposes and may require adjustment."
            ]

            for note_line in note_lines:
                cell = ws[f'A{row}']
                cell.value = f"  - {note_line}"
                cell.fill = NOTE_FILL
                cell.border = NOTE_BORDER
                ws.merge_cells(f'A{row}:F{row}')
                row += 1

            row += 1

        # ===== TRAINING MODULES TABLE =====
        ws[f'A{row}'] = 'Training Modules'
        ws[f'A{row}'].font = SUBTITLE_FONT
        row += 1

        # Helper to format module name (Competency + PMT Type)
        def format_module_name(competency_name, pmt_type):
            """Format module name: 'Competency - PMT' or just 'Competency' if combined/null"""
            if not pmt_type or pmt_type.lower() in ['combined', '-', 'null', 'none', '']:
                return competency_name
            return f"{competency_name} - {pmt_type.capitalize()}"

        # Helper to get cluster name from cluster_id
        def get_cluster_name(cluster_id):
            """Look up cluster name from training_program_cluster table"""
            if not cluster_id:
                return None
            result = db.session.execute(
                db.text("SELECT training_program_name FROM training_program_cluster WHERE id = :id"),
                {'id': cluster_id}
            ).fetchone()
            return result.training_program_name if result else None

        # Table headers
        if is_role_clustered:
            headers = ['Training Program', 'Module Type', 'Training Module', 'Level', 'Learning Format', 'Est. Participants']
            col_widths = [22, 18, 40, 15, 18, 16]
        else:
            headers = ['Training Module', 'Level', 'Learning Format', 'Est. Participants']
            col_widths = [50, 15, 20, 18]

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = THIN_BORDER
            ws.column_dimensions[get_column_letter(col_idx)].width = col_widths[col_idx - 1]

        header_row = row
        row += 1

        # Group modules by cluster for Role-Clustered view
        if is_role_clustered:
            # Style for Common Base vs Role-Specific
            COMMON_BASE_FILL = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
            ROLE_SPECIFIC_FILL = PatternFill(start_color='DEEBF7', end_color='DEEBF7', fill_type='solid')

            # Sort modules by cluster - use cluster_id to look up proper name
            cluster_groups = {}
            for module in modules:
                # Try to get cluster name from module, or look it up from cluster_id
                cluster_display = module.get('cluster_name')
                if not cluster_display or cluster_display == 'Uncategorized':
                    cluster_id = module.get('cluster_id') or module.get('training_program_cluster_id')
                    if cluster_id:
                        cluster_display = get_cluster_name(cluster_id)
                if not cluster_display:
                    cluster_display = 'Uncategorized'

                if cluster_display not in cluster_groups:
                    cluster_groups[cluster_display] = []
                cluster_groups[cluster_display].append(module)

            # Define cluster order (Engineers first, then Managers, then Interfacing Partners)
            cluster_order = ['SE for Engineers', 'SE for Managers', 'SE for Interfacing Partners']
            sorted_clusters = []
            for cluster in cluster_order:
                if cluster in cluster_groups:
                    sorted_clusters.append((cluster, cluster_groups[cluster]))
            # Add any remaining clusters
            for cluster, mods in cluster_groups.items():
                if cluster not in cluster_order:
                    sorted_clusters.append((cluster, mods))

            # Write modules grouped by cluster
            for cluster_display, cluster_modules in sorted_clusters:
                cluster_start_row = row

                # For Engineers, separate into Common Base and Role-Specific
                # Uses 'subcluster' field: 'common' = Common Base, 'pathway' = Role-Specific
                if 'Engineer' in cluster_display:
                    common_base = [m for m in cluster_modules if m.get('subcluster') == 'common']
                    role_specific = [m for m in cluster_modules if m.get('subcluster') != 'common']

                    # Write Common Base modules first
                    for module in common_base:
                        level_num = module.get('target_level', 0)
                        level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')
                        module_name = format_module_name(
                            module.get('competency_name', ''),
                            module.get('pmt_type', '')
                        )
                        format_name = module.get('format_name', '')
                        if not format_name and module.get('selected_format_id'):
                            fmt_result = db.session.execute(
                                db.text("SELECT format_name FROM learning_format WHERE id = :id"),
                                {'id': module['selected_format_id']}
                            ).fetchone()
                            format_name = fmt_result.format_name if fmt_result else 'Not Selected'
                        elif not format_name:
                            format_name = 'Not Selected'

                        values = [cluster_display, 'Common Base', module_name, level_name, format_name,
                                  module.get('estimated_participants', 0)]
                        for col_idx, value in enumerate(values, 1):
                            cell = ws.cell(row=row, column=col_idx, value=value)
                            cell.border = THIN_BORDER
                            if col_idx == 1:
                                cell.fill = CLUSTER_FILL
                                cell.font = CLUSTER_FONT
                            if col_idx == 2:
                                cell.fill = COMMON_BASE_FILL
                            if col_idx in [4, 6]:
                                cell.alignment = Alignment(horizontal='center')
                        row += 1

                    # Write Role-Specific modules
                    for module in role_specific:
                        level_num = module.get('target_level', 0)
                        level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')
                        module_name = format_module_name(
                            module.get('competency_name', ''),
                            module.get('pmt_type', '')
                        )
                        # Include role info if available (pathway_roles from subcluster logic)
                        pathway_roles = module.get('pathway_roles') or module.get('roles_needing_training', [])
                        if pathway_roles and isinstance(pathway_roles, list):
                            role_info = ', '.join(pathway_roles[:2])  # Limit to first 2 roles
                            if len(pathway_roles) > 2:
                                role_info += f' +{len(pathway_roles)-2} more'
                            module_name = f"{module_name} ({role_info})"

                        format_name = module.get('format_name', '')
                        if not format_name and module.get('selected_format_id'):
                            fmt_result = db.session.execute(
                                db.text("SELECT format_name FROM learning_format WHERE id = :id"),
                                {'id': module['selected_format_id']}
                            ).fetchone()
                            format_name = fmt_result.format_name if fmt_result else 'Not Selected'
                        elif not format_name:
                            format_name = 'Not Selected'

                        values = [cluster_display, 'Role-Specific', module_name, level_name, format_name,
                                  module.get('estimated_participants', 0)]
                        for col_idx, value in enumerate(values, 1):
                            cell = ws.cell(row=row, column=col_idx, value=value)
                            cell.border = THIN_BORDER
                            if col_idx == 1:
                                cell.fill = CLUSTER_FILL
                                cell.font = CLUSTER_FONT
                            if col_idx == 2:
                                cell.fill = ROLE_SPECIFIC_FILL
                            if col_idx in [4, 6]:
                                cell.alignment = Alignment(horizontal='center')
                        row += 1
                else:
                    # For Managers and Interfacing Partners - no Common Base distinction
                    for module in cluster_modules:
                        level_num = module.get('target_level', 0)
                        level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')
                        module_name = format_module_name(
                            module.get('competency_name', ''),
                            module.get('pmt_type', '')
                        )
                        format_name = module.get('format_name', '')
                        if not format_name and module.get('selected_format_id'):
                            fmt_result = db.session.execute(
                                db.text("SELECT format_name FROM learning_format WHERE id = :id"),
                                {'id': module['selected_format_id']}
                            ).fetchone()
                            format_name = fmt_result.format_name if fmt_result else 'Not Selected'
                        elif not format_name:
                            format_name = 'Not Selected'

                        values = [cluster_display, '-', module_name, level_name, format_name,
                                  module.get('estimated_participants', 0)]
                        for col_idx, value in enumerate(values, 1):
                            cell = ws.cell(row=row, column=col_idx, value=value)
                            cell.border = THIN_BORDER
                            if col_idx == 1:
                                cell.fill = CLUSTER_FILL
                                cell.font = CLUSTER_FONT
                            if col_idx in [4, 6]:
                                cell.alignment = Alignment(horizontal='center')
                        row += 1

                # Merge cluster cells if multiple modules
                if row - cluster_start_row > 1:
                    ws.merge_cells(f'A{cluster_start_row}:A{row - 1}')
                    ws[f'A{cluster_start_row}'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        else:
            # Standard competency-level view
            for module in modules:
                level_num = module.get('target_level', 0)
                level_name = LEVEL_NAMES.get(level_num, f'Level {level_num}')

                # Format module name (Competency + PMT Type)
                module_name = format_module_name(
                    module.get('competency_name', ''),
                    module.get('pmt_type', '')
                )

                # Get format name
                format_name = module.get('format_name', '')
                if not format_name and module.get('selected_format_id'):
                    fmt_result = db.session.execute(
                        db.text("SELECT format_name FROM learning_format WHERE id = :id"),
                        {'id': module['selected_format_id']}
                    ).fetchone()
                    format_name = fmt_result.format_name if fmt_result else 'Not Selected'
                elif not format_name:
                    format_name = 'Not Selected'

                values = [
                    module_name,
                    level_name,
                    format_name,
                    module.get('estimated_participants', 0)
                ]

                for col_idx, value in enumerate(values, 1):
                    cell = ws.cell(row=row, column=col_idx, value=value)
                    cell.border = THIN_BORDER
                    if col_idx in [2, 4]:  # Center align level, participants
                        cell.alignment = Alignment(horizontal='center')

                row += 1

        row += 2

        # ===== TIMELINE SECTION =====
        milestones = timeline.get('milestones', [])
        if milestones:
            ws[f'A{row}'] = 'Implementation Timeline'
            ws[f'A{row}'].font = SUBTITLE_FONT
            row += 1

            # Timeline headers
            timeline_headers = ['#', 'Milestone', 'Date', 'Quarter', 'Description']
            timeline_widths = [5, 30, 15, 12, 50]

            for col_idx, header in enumerate(timeline_headers, 1):
                cell = ws.cell(row=row, column=col_idx, value=header)
                cell.font = HEADER_FONT
                cell.fill = HEADER_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = THIN_BORDER
                if col_idx > len(col_widths):
                    ws.column_dimensions[get_column_letter(col_idx)].width = timeline_widths[col_idx - 1]

            row += 1

            for idx, milestone in enumerate(milestones, 1):
                values = [
                    idx,
                    milestone.get('milestone_name', milestone.get('name', '')),
                    milestone.get('estimated_date', ''),
                    milestone.get('quarter', ''),
                    milestone.get('milestone_description', milestone.get('description', ''))
                ]

                for col_idx, value in enumerate(values, 1):
                    cell = ws.cell(row=row, column=col_idx, value=value)
                    cell.border = THIN_BORDER
                    if col_idx in [1, 3, 4]:
                        cell.alignment = Alignment(horizontal='center')
                    if col_idx == 5:
                        cell.alignment = Alignment(wrap_text=True)

                row += 1

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Generate filename
        safe_org_name = ''.join(c for c in org_name if c.isalnum() or c in ' -_')[:30]
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"Phase3_MacroPlanning_{safe_org_name}_{timestamp}.xlsx"

        current_app.logger.info(f"[Phase3 Export] Excel export created for org {organization_id}")

        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting Phase 3: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
