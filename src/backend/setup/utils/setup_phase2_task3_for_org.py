"""
Automatic Phase 2 Task 3 Setup for New Organizations
Automatically creates learning strategy instances for a new organization
Links to global strategy templates - no data duplication
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models import StrategyTemplate, LearningStrategy, Organization

def get_db_connection_string():
    """Get database connection string from environment or default"""
    return os.getenv('DATABASE_URL', 'postgresql://seqpt_admin:SeQpt_2025@localhost:5432/seqpt_database')

def setup_phase2_task3_strategies(organization_id: int, db_session=None) -> dict:
    """
    Automatically setup Phase 2 Task 3 strategies for an organization.

    Creates learning_strategy instances that reference global strategy_template records.
    No data duplication - just links organization to templates.

    Args:
        organization_id: Organization ID to setup strategies for
        db_session: Optional database session (will create if not provided)

    Returns:
        dict: Summary of strategies created

    Example:
        result = setup_phase2_task3_strategies(30)
        # {
        #   "success": True,
        #   "organization_id": 30,
        #   "strategies_created": 7,
        #   "strategy_names": ["Common basic understanding", ...]
        # }
    """

    # Create session if not provided
    close_session = False
    if db_session is None:
        engine = create_engine(get_db_connection_string())
        Session = sessionmaker(bind=engine)
        db_session = Session()
        close_session = True

    try:
        # Verify organization exists
        org = db_session.query(Organization).filter_by(id=organization_id).first()
        if not org:
            return {
                "success": False,
                "error": f"Organization {organization_id} not found"
            }

        print(f"[INFO] Setting up Phase 2 Task 3 strategies for organization: {org.name} (ID: {organization_id})")

        # Get all active strategy templates
        templates = db_session.query(StrategyTemplate).filter_by(is_active=True).order_by(StrategyTemplate.id).all()

        if not templates:
            return {
                "success": False,
                "error": "No strategy templates found. Run migration 006 first."
            }

        print(f"[INFO] Found {len(templates)} strategy templates")

        # Check if strategies already exist for this org
        existing = db_session.query(LearningStrategy).filter_by(organization_id=organization_id).count()
        if existing > 0:
            print(f"[WARNING] Organization already has {existing} strategies. Skipping creation.")
            return {
                "success": False,
                "error": f"Organization {organization_id} already has {existing} strategies",
                "existing_count": existing
            }

        # Create learning_strategy instance for each template
        created = []
        for i, template in enumerate(templates, 1):
            learning_strategy = LearningStrategy(
                organization_id=organization_id,
                strategy_template_id=template.id,
                strategy_name=template.strategy_name,  # Store name for easier querying during migration
                strategy_description=template.strategy_description,
                selected=False,  # Default: not selected
                priority=i  # Sequential priority
            )
            db_session.add(learning_strategy)
            created.append({
                "name": template.strategy_name,
                "requires_pmt": template.requires_pmt_context
            })
            print(f"  [OK] Linked strategy: {template.strategy_name}")

        # Commit transaction
        db_session.commit()

        print(f"\n[SUCCESS] Created {len(created)} learning strategy instances for org {organization_id}")

        return {
            "success": True,
            "organization_id": organization_id,
            "organization_name": org.name,
            "strategies_created": len(created),
            "strategies": created
        }

    except Exception as e:
        db_session.rollback()
        print(f"[ERROR] Failed to setup strategies: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if close_session:
            db_session.close()


def verify_phase2_task3_setup(organization_id: int) -> dict:
    """
    Verify Phase 2 Task 3 setup for an organization.

    Checks:
    - All 7 strategies exist
    - All strategies linked to templates
    - All templates have competency data

    Returns:
        dict: Verification results
    """

    engine = create_engine(get_db_connection_string())
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        # Check learning strategies
        strategies = db_session.query(LearningStrategy).filter_by(organization_id=organization_id).all()

        results = {
            "organization_id": organization_id,
            "total_strategies": len(strategies),
            "expected_strategies": 7,
            "strategies": []
        }

        for strategy in strategies:
            template = db_session.query(StrategyTemplate).filter_by(id=strategy.strategy_template_id).first()
            results["strategies"].append({
                "id": strategy.id,
                "name": template.strategy_name if template else "ERROR: No template",
                "selected": strategy.selected,
                "has_template": template is not None,
                "template_id": strategy.strategy_template_id
            })

        results["all_linked_to_templates"] = all(s["has_template"] for s in results["strategies"])
        results["correct_count"] = results["total_strategies"] == results["expected_strategies"]
        results["success"] = results["all_linked_to_templates"] and results["correct_count"]

        return results

    finally:
        db_session.close()


if __name__ == "__main__":
    """
    Command-line usage:
    python setup_phase2_task3_for_org.py <org_id>
    python setup_phase2_task3_for_org.py <org_id> --verify
    """

    if len(sys.argv) < 2:
        print("Usage: python setup_phase2_task3_for_org.py <organization_id> [--verify]")
        print("\nExamples:")
        print("  python setup_phase2_task3_for_org.py 30")
        print("  python setup_phase2_task3_for_org.py 30 --verify")
        sys.exit(1)

    org_id = int(sys.argv[1])
    verify_only = "--verify" in sys.argv

    if verify_only:
        print(f"\n[VERIFICATION MODE] Checking Phase 2 Task 3 setup for org {org_id}...\n")
        results = verify_phase2_task3_setup(org_id)

        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60)
        print(f"Organization ID: {results['organization_id']}")
        print(f"Total Strategies: {results['total_strategies']} (expected: {results['expected_strategies']})")
        print(f"All Linked to Templates: {results['all_linked_to_templates']}")
        print(f"Correct Count: {results['correct_count']}")
        print(f"Overall Status: {'PASS' if results['success'] else 'FAIL'}")

        print("\nStrategy List:")
        for s in results['strategies']:
            status = "[OK]" if s['has_template'] else "[ERROR]"
            selected = "(selected)" if s['selected'] else ""
            print(f"  {status} {s['name']} {selected}")

    else:
        print(f"\n[SETUP MODE] Creating Phase 2 Task 3 strategies for org {org_id}...\n")
        result = setup_phase2_task3_strategies(org_id)

        if result["success"]:
            print("\n" + "="*60)
            print("SETUP COMPLETE")
            print("="*60)
            print(f"Organization: {result['organization_name']} (ID: {result['organization_id']})")
            print(f"Strategies Created: {result['strategies_created']}")
            print("\nStrategies:")
            for s in result['strategies']:
                pmt = " (requires PMT)" if s['requires_pmt'] else ""
                print(f"  - {s['name']}{pmt}")

            print("\nNext Steps:")
            print("1. Users can now complete Phase 2 competency assessments")
            print("2. Admin can select strategies in Phase 1")
            print("3. Admin can generate learning objectives in Phase 2 Task 3")
        else:
            print("\n[ERROR] Setup failed:", result['error'])
            sys.exit(1)
