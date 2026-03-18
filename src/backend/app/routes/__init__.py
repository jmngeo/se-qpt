"""
SE-QPT Routes Package
=====================
Organizes API routes into domain-specific blueprints.

Blueprint Structure:
- auth_bp: Authentication endpoints (/mvp/auth/*, /auth/*)
- org_bp: Organization management (/organization/*)
- phase1_maturity_bp: Phase 1 Task 1 - Maturity assessment (/phase1/maturity/*)
- phase1_roles_bp: Phase 1 Task 2 - Role identification (/phase1/roles/*, /findProcesses)
- phase1_strategies_bp: Phase 1 Task 3 - Strategy selection (/phase1/strategies/*)
- phase2_assessment_bp: Phase 2 Task 1-2 - Competency assessment (/phase2/*, /assessment/*)
- phase2_learning_bp: Phase 2 Task 3 - Learning objectives (/phase2/learning-objectives/*)
- phase3_planning_bp: Phase 3 - Macro Planning (/phase3/*)
- phase4_aviva_bp: Phase 4 - Micro Planning / AVIVA Didactics (/phase4/*)
- main_bp: Miscellaneous/legacy routes (/, /assessments, /roles, etc.)
"""

# Common imports used across all route modules
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from datetime import datetime, timedelta
import json
import sys
import traceback
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict

# Import all models
from models import (
    db,
    User,
    SECompetency,
    SERole,
    Organization,
    CompetencyAssessment,
    RoleCluster,
    OrganizationRoles,
    OrganizationRoleMapping,
    IsoProcesses,
    Competency,
    CompetencyIndicator,
    RoleProcessMatrix,
    ProcessCompetencyMatrix,
    RoleCompetencyMatrix,
    UnknownRoleProcessMatrix,
    UnknownRoleCompetencyMatrix,
    UserCompetencySurveyResult,
    UserRoleCluster,
    UserCompetencySurveyFeedback,
    LearningStrategy,
    OrganizationPMTContext,
    calculate_maturity_score,
    select_archetype
)

# Import services
from app.services.generate_survey_feedback import generate_feedback_with_llm
from app.services.role_cluster_mapping_service import RoleClusterMappingService
from app.services.custom_role_matrix_generator import CustomRoleMatrixGenerator

# Initialize shared services (singleton instances)
role_mapping_service = RoleClusterMappingService()
custom_role_matrix_generator = CustomRoleMatrixGenerator()


# =============================================================================
# SHARED HELPER FUNCTIONS
# =============================================================================

def _initialize_organization_matrices(new_org_id):
    """
    Initialize a new organization with default role-process matrix and CALCULATE role-competency matrix.
    Copies role-process from organization_id=1 (default/template organization).
    Then CALCULATES role-competency matrix using update_role_competency_matrix stored procedure.
    """
    try:
        # 1. Copy role-process matrix from org 1
        db.session.execute(
            text('CALL insert_new_org_default_role_process_matrix(:org_id);'),
            {'org_id': new_org_id}
        )
        current_app.logger.info(f"[OK] Copied 420 role-process matrix entries for org {new_org_id}")

        # 2. CALCULATE role-competency matrix (don't copy - always calculate fresh!)
        try:
            db.session.execute(
                text('CALL update_role_competency_matrix(:org_id);'),
                {'org_id': new_org_id}
            )
            current_app.logger.info(f"[OK] Calculated role-competency matrix for org {new_org_id}")
        except Exception as calc_error:
            current_app.logger.warning(f"[SKIP] Role-competency calculation failed: {calc_error}")

        return True

    except Exception as e:
        current_app.logger.error(f"[ERROR] Failed to initialize matrices for org {new_org_id}: {e}")
        return False


def get_maturity_level_from_score(score):
    """Convert numeric maturity score to level name"""
    if score >= 4.5:
        return 5, 'Optimizing'
    elif score >= 3.5:
        return 4, 'Managed'
    elif score >= 2.5:
        return 3, 'Defined'
    elif score >= 1.5:
        return 2, 'Repeatable'
    else:
        return 1, 'Initial'


# =============================================================================
# BLUEPRINT IMPORTS
# =============================================================================

from app.routes.auth import auth_bp
from app.routes.organization import org_bp
from app.routes.phase1_maturity import phase1_maturity_bp
from app.routes.phase1_roles import phase1_roles_bp
from app.routes.phase1_strategies import phase1_strategies_bp
from app.routes.phase2_assessment import phase2_assessment_bp
from app.routes.phase2_learning import phase2_learning_bp
from app.routes.phase3_planning import phase3_planning_bp
from app.routes.phase4_aviva import phase4_aviva_bp
from app.routes.main import main_bp

# Export all blueprints
__all__ = [
    'auth_bp',
    'org_bp',
    'phase1_maturity_bp',
    'phase1_roles_bp',
    'phase1_strategies_bp',
    'phase2_assessment_bp',
    'phase2_learning_bp',
    'phase3_planning_bp',
    'phase4_aviva_bp',
    'main_bp',
    # Helper functions
    '_initialize_organization_matrices',
    'get_maturity_level_from_score',
    # Shared services
    'role_mapping_service',
    'custom_role_matrix_generator',
]
