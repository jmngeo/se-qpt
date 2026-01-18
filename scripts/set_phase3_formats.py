"""
Script to bulk-set learning format selections for Phase 3 modules.
Sets reasonable default formats based on participant count and level.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from app import create_app
from models import db
from sqlalchemy import text
import json

def get_recommended_format(participant_count, target_level):
    """
    Get recommended format ID based on participant count and target level.

    Format IDs (from learning_format table):
    1 = Seminar (5-25 participants, good for group interaction)
    2 = Webinar (10-100+ participants, good for large groups)
    3 = Coaching (1-5 participants, individual focused)
    4 = Mentoring (1-3 participants, individual focused)
    5 = WBT (1-unlimited, self-paced online)
    6 = CBT (1-unlimited, self-paced computer)
    7 = Game-Based (5-30 participants, interactive)
    8 = Conference (50-500+ participants, large events)
    9 = Blended (10-50 participants, best for deep learning)
    10 = Self-Learning (1-unlimited, individual study)
    """
    # For very small groups (< 5), use coaching or mentoring
    if participant_count <= 5:
        return 3  # Coaching

    # For small groups (5-25), use seminar or blended based on level
    if participant_count <= 25:
        if target_level >= 4:  # Applying level needs more interaction
            return 9  # Blended Learning
        else:
            return 1  # Seminar

    # For medium groups (25-50), use blended or webinar
    if participant_count <= 50:
        if target_level >= 4:
            return 9  # Blended Learning
        else:
            return 2  # Webinar

    # For large groups (50-100), use webinar or WBT
    if participant_count <= 100:
        if target_level >= 4:
            return 2  # Webinar (still need some interaction)
        else:
            return 5  # WBT (Web-Based Training)

    # For very large groups (100+), use WBT or self-learning
    if target_level >= 4:
        return 5  # WBT
    else:
        return 10  # Self-Learning


def set_formats_for_org(organization_id, view_type='role_clustered'):
    """Set format selections for all modules in an organization"""

    app = create_app()

    with app.app_context():
        # Get all modules that need format selection
        # First, get the training modules from the service
        from app.services.phase3_planning_service import Phase3PlanningService
        service = Phase3PlanningService(db.session)

        result = service.get_training_modules(organization_id, view_type)
        modules = result.get('modules', [])

        print(f"[INFO] Found {len(modules)} modules for org {organization_id}, view: {view_type}")

        if not modules:
            print("[ERROR] No modules found!")
            return

        # Track statistics
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        format_dist = {}

        for module in modules:
            try:
                competency_id = module.get('competency_id')
                target_level = module.get('target_level', 1)
                pmt_type = module.get('pmt_type') or 'combined'
                estimated_participants = module.get('estimated_participants', 10)
                cluster_id = module.get('cluster_id') or module.get('training_program_cluster_id')

                # Skip if already has a format selected
                if module.get('selected_format_id'):
                    stats['skipped'] += 1
                    continue

                # Get recommended format
                format_id = get_recommended_format(estimated_participants, target_level)

                # Track distribution
                format_dist[format_id] = format_dist.get(format_id, 0) + 1

                # For role_clustered view, check if entry exists with this cluster_id
                # Use the full unique key including cluster_id
                existing = db.session.execute(
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
                    # Update existing entry
                    db.session.execute(
                        text("""
                            UPDATE phase3_training_module
                            SET selected_format_id = :fmt_id,
                                estimated_participants = :est,
                                confirmed = true,
                                updated_at = NOW()
                            WHERE id = :id
                        """),
                        {
                            'id': existing.id,
                            'fmt_id': format_id,
                            'est': estimated_participants
                        }
                    )
                    stats['updated'] += 1
                else:
                    # Insert new entry
                    db.session.execute(
                        text("""
                            INSERT INTO phase3_training_module
                            (organization_id, competency_id, target_level, pmt_type,
                             selected_format_id, estimated_participants, confirmed,
                             training_program_cluster_id, created_at, updated_at)
                            VALUES
                            (:org_id, :comp_id, :level, :pmt,
                             :fmt_id, :est, true, :cluster_id, NOW(), NOW())
                        """),
                        {
                            'org_id': organization_id,
                            'comp_id': competency_id,
                            'level': target_level,
                            'pmt': pmt_type,
                            'fmt_id': format_id,
                            'est': estimated_participants,
                            'cluster_id': cluster_id
                        }
                    )
                    stats['inserted'] += 1

            except Exception as e:
                print(f"[ERROR] Failed to set format for module: {e}")
                import traceback
                traceback.print_exc()
                stats['errors'] += 1

        db.session.commit()

        # Get format names for display
        format_names = {}
        formats = db.session.execute(
            text("SELECT id, short_name FROM learning_format")
        ).fetchall()
        for f in formats:
            format_names[f.id] = f.short_name

        print(f"\n[SUCCESS] Format selection complete!")
        print(f"  - Inserted: {stats['inserted']}")
        print(f"  - Updated: {stats['updated']}")
        print(f"  - Skipped (already set): {stats['skipped']}")
        print(f"  - Errors: {stats['errors']}")
        print(f"\nFormat Distribution:")
        for fmt_id, count in sorted(format_dist.items()):
            print(f"  - {format_names.get(fmt_id, f'Format {fmt_id}')}: {count} modules")


if __name__ == '__main__':
    org_id = 48
    view_type = 'role_clustered'

    if len(sys.argv) > 1:
        org_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        view_type = sys.argv[2]

    print(f"Setting formats for organization {org_id}, view: {view_type}")
    set_formats_for_org(org_id, view_type)
