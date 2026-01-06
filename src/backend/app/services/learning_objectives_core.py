"""
Learning Objectives Core Generator - Design v5
==============================================

Implements core algorithms for Phase 2 Task 3 Learning Objectives generation.

Based on: LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE.md
Date: 2025-11-25
Status: Week 1 Implementation

Core Algorithms Implemented:
1. calculate_combined_targets() - Separate TTT from main strategies
2. validate_mastery_requirements() - 3-way validation check
3. detect_gaps() - Role-based or organizational gap detection

Key Design Principles:
- ANY gap triggers LO generation (not median-based)
- Both pathways use pyramid structure
- Progressive levels (generate 1,2,4 not just target)
- Exclude TTT from main targets
- Three-way validation (role vs strategy vs current)
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import func

# Import models - use direct import to work both in app context and testing
try:
    from models import (
        db, Organization, Competency, StrategyTemplate, StrategyTemplateCompetency,
        OrganizationRoles, UserCompetencySurveyResult, UserAssessment,
        RoleCompetencyMatrix, UserRoleCluster, GeneratedLearningObjectives,
        OrganizationPMTContext, OrganizationExistingTraining
    )
except ImportError:
    from app.models import (
        db, Organization, Competency, StrategyTemplate, StrategyTemplateCompetency,
        OrganizationRoles, UserCompetencySurveyResult, UserAssessment,
        RoleCompetencyMatrix, UserRoleCluster, GeneratedLearningObjectives,
        OrganizationPMTContext, OrganizationExistingTraining
    )

logger = logging.getLogger(__name__)

# Valid levels in pyramid structure
VALID_LEVELS = [1, 2, 4, 6]


# =============================================================================
# EXISTING TRAINING EXCLUSION HELPER
# Feature: "Check and Integrate Existing Offers" (Ulf's request - 11.12.2025)
# =============================================================================

def get_excluded_competency_ids(organization_id: int) -> set:
    """
    Get competency IDs that should be excluded from training requirements
    because organization has existing training for them.

    These competencies will be shown in "No Training Required" with
    "Training Exists" tag instead of being in "Training Requirements Identified".

    Args:
        organization_id: Organization ID

    Returns:
        Set of competency IDs with existing training
    """
    try:
        existing = OrganizationExistingTraining.query.filter_by(
            organization_id=organization_id
        ).all()
        excluded_ids = {e.competency_id for e in existing}
        if excluded_ids:
            logger.info(f"[get_excluded_competency_ids] Org {organization_id}: "
                       f"{len(excluded_ids)} competencies excluded (existing training)")
        return excluded_ids
    except Exception as e:
        logger.warning(f"[get_excluded_competency_ids] Error: {str(e)}")
        return set()


# =============================================================================
# CACHING FUNCTIONS - Avoid unnecessary LLM calls
# =============================================================================

def compute_input_hash(
    org_id: int,
    selected_strategies: List[Dict],
    pmt_context: Optional[Dict]
) -> str:
    """
    Compute SHA-256 hash of all inputs that affect learning objectives output.

    Hash components:
    1. Selected strategies (IDs and names)
    2. PMT context (if present)
    3. Assessment scores (latest per user per competency)
    4. Strategy template targets

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Normalize strategies to consistent format
    normalized_strategies = sorted([
        {'id': s.get('strategy_id'), 'name': s.get('strategy_name')}
        for s in selected_strategies
    ], key=lambda x: x['id'])

    # Normalize PMT context - only include non-empty fields
    normalized_pmt = None
    if pmt_context:
        normalized_pmt = {
            'processes': (pmt_context.get('processes') or '').strip(),
            'methods': (pmt_context.get('methods') or '').strip(),
            'tools': (pmt_context.get('tools') or '').strip()
        }
        # Remove empty keys
        normalized_pmt = {k: v for k, v in normalized_pmt.items() if v}
        if not normalized_pmt:
            normalized_pmt = None

    hash_input = {
        'org_id': org_id,
        'strategies': normalized_strategies,
        'pmt': normalized_pmt
    }

    print(f"[compute_input_hash] Strategies: {normalized_strategies}")
    print(f"[compute_input_hash] PMT: {normalized_pmt}")

    # Add assessment scores snapshot - ONLY from latest assessment per user
    # This ensures cache invalidates when user retakes assessment
    assessment_scores = []

    # Get latest assessment_id per user for this organization
    from sqlalchemy import func
    latest_assessments = db.session.query(
        UserAssessment.user_id,
        func.max(UserAssessment.id).label('latest_assessment_id')
    ).filter(
        UserAssessment.organization_id == org_id,
        UserAssessment.completed_at.isnot(None)
    ).group_by(UserAssessment.user_id).subquery()

    # Get scores only from latest assessments
    results = db.session.query(UserCompetencySurveyResult).join(
        latest_assessments,
        db.and_(
            UserCompetencySurveyResult.user_id == latest_assessments.c.user_id,
            UserCompetencySurveyResult.assessment_id == latest_assessments.c.latest_assessment_id
        )
    ).filter(
        UserCompetencySurveyResult.organization_id == org_id
    ).all()

    for r in results:
        assessment_scores.append({
            'user_id': r.user_id,
            'comp_id': r.competency_id,
            'score': r.score,
            'assessment_id': r.assessment_id
        })

    hash_input['assessments'] = sorted(
        assessment_scores,
        key=lambda x: (x['user_id'], x['comp_id'])
    )

    # Add user-role assignments snapshot
    # This ensures cache invalidates when user roles change
    role_assignments = []
    user_roles = UserRoleCluster.query.join(
        OrganizationRoles,
        UserRoleCluster.role_cluster_id == OrganizationRoles.id
    ).filter(
        OrganizationRoles.organization_id == org_id
    ).all()

    for ur in user_roles:
        role_assignments.append({
            'user_id': ur.user_id,
            'role_id': ur.role_cluster_id
        })

    hash_input['role_assignments'] = sorted(
        role_assignments,
        key=lambda x: (x['user_id'], x['role_id'])
    )

    # Add excluded competencies (existing training) to hash
    # This ensures cache invalidates when exclusions change
    excluded_ids = get_excluded_competency_ids(org_id)
    hash_input['excluded_competencies'] = sorted(excluded_ids)

    # Create deterministic JSON string
    hash_string = json.dumps(hash_input, sort_keys=True, default=str)

    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()


def get_cached_objectives(org_id: int, input_hash: str) -> Optional[Dict]:
    """
    Check if cached objectives exist and are still valid.

    Args:
        org_id: Organization ID
        input_hash: Current input hash to compare

    Returns:
        Cached objectives data if valid, None otherwise
    """
    try:
        cached = GeneratedLearningObjectives.query.filter_by(
            organization_id=org_id
        ).first()

        if cached and cached.input_hash == input_hash:
            print(
                f"[get_cached_objectives] Cache HIT for org {org_id} "
                f"(hash: {input_hash[:8]}...)"
            )

            # Return cached data with metadata
            result = cached.objectives_data
            if isinstance(result, str):
                result = json.loads(result)

            # Add cache metadata
            result['metadata'] = result.get('metadata', {})
            result['metadata']['from_cache'] = True
            result['metadata']['cached_at'] = cached.generated_at.isoformat() if cached.generated_at else None

            return result

        if cached:
            print(
                f"[get_cached_objectives] Cache MISS for org {org_id} "
                f"(hash mismatch: cached={cached.input_hash[:8]}... vs current={input_hash[:8]}...)"
            )
        else:
            print(f"[get_cached_objectives] No cache exists for org {org_id}")

        return None

    except Exception as e:
        logger.warning(f"[get_cached_objectives] Error checking cache: {e}")
        return None


def save_to_cache(
    org_id: int,
    input_hash: str,
    pathway: str,
    objectives_data: Dict,
    validation_status: Optional[str] = None,
    gap_percentage: Optional[float] = None
) -> bool:
    """
    Save generated objectives to cache.

    Args:
        org_id: Organization ID
        input_hash: Computed input hash
        pathway: ROLE_BASED or TASK_BASED
        objectives_data: Full objectives output
        validation_status: Optional validation status for quick access
        gap_percentage: Optional gap percentage for dashboard display

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Check if cache entry exists
        cached = GeneratedLearningObjectives.query.filter_by(
            organization_id=org_id
        ).first()

        if cached:
            # Update existing entry
            cached.pathway = pathway
            cached.objectives_data = objectives_data
            cached.input_hash = input_hash
            cached.generated_at = datetime.utcnow()
            cached.validation_status = validation_status
            cached.gap_percentage = gap_percentage
            print(f"[save_to_cache] Updated cache for org {org_id}")
        else:
            # Create new entry
            cached = GeneratedLearningObjectives(
                organization_id=org_id,
                pathway=pathway,
                objectives_data=objectives_data,
                input_hash=input_hash,
                generated_at=datetime.utcnow(),
                validation_status=validation_status,
                gap_percentage=gap_percentage
            )
            db.session.add(cached)
            print(f"[save_to_cache] Created new cache for org {org_id}")

        db.session.commit()
        return True

    except Exception as e:
        logger.error(f"[save_to_cache] Error saving to cache: {e}")
        db.session.rollback()
        return False


def invalidate_cache(org_id: int) -> bool:
    """
    Invalidate cache for an organization.

    Call this when:
    - Assessment is submitted
    - Strategy selection changes
    - PMT context is updated

    Args:
        org_id: Organization ID

    Returns:
        True if invalidated/deleted, False if not found
    """
    try:
        cached = GeneratedLearningObjectives.query.filter_by(
            organization_id=org_id
        ).first()

        if cached:
            db.session.delete(cached)
            db.session.commit()
            logger.info(f"[invalidate_cache] Cache invalidated for org {org_id}")
            return True

        return False

    except Exception as e:
        logger.error(f"[invalidate_cache] Error invalidating cache: {e}")
        db.session.rollback()
        return False


def is_ttt_strategy(strategy: Dict) -> bool:
    """
    Check if a strategy is Train the Trainer (TTT).

    Handles various naming conventions:
    - "Train the Trainer"
    - "Train the SE-Trainer"
    - "train-the-trainer"
    - Strategy ID 6 (database constant)

    Args:
        strategy: Strategy dict with keys like 'strategy_id', 'strategy_name'

    Returns:
        True if this is a TTT strategy
    """
    strategy_name = strategy.get('strategy_name', '').strip().lower()

    return (
        'train the trainer' in strategy_name or
        'train-the-trainer' in strategy_name or
        ('trainer' in strategy_name and 'train' in strategy_name) or
        strategy.get('strategy_id') == 6  # Strategy ID 6 is always TTT in our database
    )


def get_all_competency_ids() -> List[int]:
    """
    Get all competency IDs from database dynamically.

    This replaces the hardcoded ALL_16_COMPETENCY_IDS constant to handle
    databases with different numbers of competencies (e.g., 16, 18, etc.)

    Returns:
        List of competency IDs in ascending order

    Example:
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    """
    competencies = Competency.query.order_by(Competency.id).all()
    return [c.id for c in competencies]


# =============================================================================
# ALGORITHM 1: Calculate Combined Targets
# =============================================================================

def calculate_combined_targets(selected_strategies: List[Dict]) -> Dict:
    """
    Calculate combined strategy targets, separating TTT from other strategies.

    CRITICAL DESIGN PRINCIPLES:
    - Separate "Train the Trainer" from other strategies
    - Main targets: Take HIGHER among non-TTT strategies
    - TTT targets: All level 6 (processed separately)

    Args:
        selected_strategies: List of strategy dicts with keys:
            - strategy_id: int
            - strategy_name: str
            - archetype_id: int (optional)

    Returns:
        {
            'main_targets': {competency_id: target_level},  # 1-16 → level
            'ttt_targets': {competency_id: 6} or None,      # Only if TTT selected
            'ttt_selected': bool,
            'ttt_strategy': dict or None
        }

    Raises:
        ValueError: If no strategies selected or invalid strategy data

    Example:
        >>> strategies = [
        ...     {'strategy_id': 1, 'strategy_name': 'Common basic understanding'},
        ...     {'strategy_id': 6, 'strategy_name': 'Train the Trainer'}
        ... ]
        >>> result = calculate_combined_targets(strategies)
        >>> result['ttt_selected']
        True
        >>> result['main_targets'][1]  # Competency 1 target from non-TTT strategies
        2
    """

    logger.info(f"[calculate_combined_targets] Processing {len(selected_strategies)} strategies")

    # Validate input
    if not selected_strategies or len(selected_strategies) == 0:
        raise ValueError("No strategies selected - at least one strategy is required")

    # Separate TTT from other strategies
    ttt_strategy = None
    other_strategies = []

    for strategy in selected_strategies:
        strategy_name = strategy.get('strategy_name', '').strip()

        # Check for TTT using helper function
        if is_ttt_strategy(strategy):
            ttt_strategy = strategy
            logger.info(f"[calculate_combined_targets] TTT detected: {strategy_name}")
        else:
            other_strategies.append(strategy)

    # Validate: Must have at least one strategy (TTT or non-TTT)
    if len(other_strategies) == 0 and ttt_strategy is None:
        raise ValueError("No valid strategies found")

    # Calculate main targets from non-TTT strategies
    main_targets = {}
    all_competency_ids = get_all_competency_ids()  # FIXED: Dynamic competency loading

    if len(other_strategies) > 0:
        logger.info(f"[calculate_combined_targets] Processing {len(other_strategies)} non-TTT strategies")

        for strategy in other_strategies:
            strategy_id = strategy.get('strategy_id')
            strategy_name = strategy.get('strategy_name', 'Unknown')

            # Get strategy template from database
            strategy_template = StrategyTemplate.query.get(strategy_id)

            if not strategy_template:
                logger.warning(f"[calculate_combined_targets] No template found for strategy {strategy_id} ({strategy_name})")
                continue

            # Process all competencies (dynamic, not hardcoded to 16)
            for competency_id in all_competency_ids:
                # Get target level for this competency from strategy template
                target = get_strategy_template_target_level(strategy_template.id, competency_id)

                if competency_id not in main_targets:
                    main_targets[competency_id] = target
                else:
                    # Take HIGHER target if multiple strategies
                    main_targets[competency_id] = max(main_targets[competency_id], target)

        logger.info(f"[calculate_combined_targets] Main targets calculated for {len(main_targets)} competencies")

    else:
        # Edge case: Only TTT selected (no regular training)
        logger.warning("[calculate_combined_targets] Only TTT selected - main targets set to 0")
        main_targets = {comp_id: 0 for comp_id in all_competency_ids}

    # Calculate TTT targets (all level 6)
    ttt_targets = None
    if ttt_strategy is not None:
        ttt_targets = {comp_id: 6 for comp_id in all_competency_ids}
        logger.info("[calculate_combined_targets] TTT targets set to Level 6 for all competencies")

    result = {
        'main_targets': main_targets,
        'ttt_targets': ttt_targets,
        'ttt_selected': ttt_strategy is not None,
        'ttt_strategy': ttt_strategy
    }

    logger.info(f"[calculate_combined_targets] Complete - TTT selected: {result['ttt_selected']}")

    return result


def get_strategy_template_target_level(strategy_template_id: int, competency_id: int) -> int:
    """
    Get target level for a competency from strategy template.

    Args:
        strategy_template_id: Strategy template ID
        competency_id: Competency ID (1-16)

    Returns:
        Target level (0, 1, 2, 4, or 6)
    """
    # Query the strategy_template_competency table
    template_comp = StrategyTemplateCompetency.query.filter_by(
        strategy_template_id=strategy_template_id,
        competency_id=competency_id
    ).first()

    if not template_comp:
        logger.warning(f"[get_strategy_template_target_level] No target found for template {strategy_template_id}, competency {competency_id} - defaulting to 0")
        return 0

    target = template_comp.target_level

    # Validate level (should be 0, 1, 2, 4, or 6)
    if target not in [0, 1, 2, 4, 6]:
        logger.warning(f"[get_strategy_template_target_level] Invalid target level {target} for competency {competency_id} - defaulting to 0")
        return 0

    return target


# =============================================================================
# ALGORITHM 2: Validate Mastery Requirements
# =============================================================================

def validate_mastery_requirements(
    org_id: int,
    selected_strategies: List[Dict],
    main_targets: Dict[int, int]
) -> Dict:
    """
    Validate that selected strategies can meet role requirements.

    CRITICAL CHECK: If any role requires Level 6, but TTT not selected
    and main strategies don't provide Level 6.

    Three-way validation:
    1. Role requirement (from role-competency matrix)
    2. Strategy target (from selected strategies)
    3. Current level (from assessments - for context only)

    Args:
        org_id: Organization ID
        selected_strategies: List of selected strategy dicts
        main_targets: Target levels from non-TTT strategies

    Returns:
        {
            'status': 'OK' | 'INADEQUATE',
            'severity': 'NONE' | 'MEDIUM' | 'HIGH',
            'message': str,
            'affected': [...],  # List of affected role-competency combinations
            'recommendations': [...]  # Actionable recommendations
        }

    Example:
        >>> result = validate_mastery_requirements(28, strategies, main_targets)
        >>> if result['status'] == 'INADEQUATE':
        ...     print(result['message'])
        ...     for rec in result['recommendations']:
        ...         print(f"- {rec['label']}")
    """

    logger.info(f"[validate_mastery_requirements] Validating for org {org_id}")

    # Check if organization has roles defined
    has_roles = check_if_org_has_roles(org_id)

    if not has_roles:
        logger.info("[validate_mastery_requirements] Low maturity - no role requirements to validate")
        return {
            'status': 'OK',
            'severity': 'NONE',
            'message': 'No role requirements defined (low maturity organization)',
            'affected': [],
            'recommendations': []
        }

    # Check if TTT is selected
    ttt_selected = any(
        is_ttt_strategy(s)
        for s in selected_strategies
    )

    logger.info(f"[validate_mastery_requirements] TTT selected: {ttt_selected}")

    # Get all roles for this organization
    roles = OrganizationRoles.query.filter_by(organization_id=org_id).all()

    if len(roles) == 0:
        logger.warning(f"[validate_mastery_requirements] No roles found for org {org_id} despite has_roles=True")
        return {
            'status': 'OK',
            'severity': 'NONE',
            'message': 'No roles defined',
            'affected': [],
            'recommendations': []
        }

    logger.info(f"[validate_mastery_requirements] Checking {len(roles)} roles")

    affected_combinations = []
    all_competency_ids = get_all_competency_ids()  # FIXED: Dynamic competency loading

    # Check each role-competency combination
    for role in roles:
        for competency_id in all_competency_ids:
            # Get role requirement level from role-competency matrix
            role_requirement = get_role_competency_requirement(role.id, competency_id)

            if role_requirement == 0:
                continue  # No requirement for this combination

            # Get strategy target for this competency
            strategy_target = main_targets.get(competency_id, 0)

            # Check if requirement exceeds what strategy provides
            if role_requirement > strategy_target:
                # INADEQUACY DETECTED
                competency = Competency.query.get(competency_id)

                affected_combinations.append({
                    'role_id': role.id,
                    'role_name': role.role_name,
                    'competency_id': competency_id,
                    'competency_name': competency.competency_name if competency else f"Competency {competency_id}",
                    'required_level': role_requirement,
                    'strategy_provides': strategy_target,
                    'gap': role_requirement - strategy_target
                })

    # Analyze results
    if len(affected_combinations) == 0:
        logger.info("[validate_mastery_requirements] All role requirements can be met")
        return {
            'status': 'OK',
            'severity': 'NONE',
            'message': 'All role requirements can be met by selected strategies',
            'affected': [],
            'recommendations': []
        }

    # Count how many require Level 6 specifically
    level_6_requirements = [
        a for a in affected_combinations
        if a['required_level'] == 6
    ]

    # Determine severity and user-friendly message
    if len(level_6_requirements) > 0 and not ttt_selected:
        severity = 'HIGH'
        # User-friendly message without technical jargon
        message = (
            f"Some roles in your organization require expert-level skills "
            f"that go beyond what the current training strategy covers."
        )
    else:
        severity = 'MEDIUM'
        message = (
            f"Some competency requirements exceed the current training strategy targets."
        )

    # Generate single, actionable recommendation
    recommendations = []

    if len(level_6_requirements) > 0 and not ttt_selected:
        recommendations.append({
            'action': 'add_ttt_strategy',
            'label': 'Enable Advanced Training',
            'description': (
                'To develop expert-level capabilities, select the "Train the Trainer" '
                'strategy in Phase 1 Task 3. This allows you to develop internal trainers '
                'or bring in external experts to train your team to mastery level.'
            ),
            'priority': 'HIGH'
        })

    logger.warning(f"[validate_mastery_requirements] INADEQUATE - {len(affected_combinations)} issues found")

    return {
        'status': 'INADEQUATE',
        'severity': severity,
        'message': message,
        'affected': affected_combinations,
        'recommendations': recommendations
    }


def check_if_org_has_roles(org_id: int) -> bool:
    """
    Check if organization has roles defined AND users assigned to them.

    A "high maturity" organization for gap analysis purposes means:
    1. Roles are defined in organization_roles table
    2. Users are actually assigned to those roles in user_role_cluster table

    If roles exist but no users are assigned, we should fall back to
    organizational (low maturity) processing to ensure gaps are detected.

    Args:
        org_id: Organization ID

    Returns:
        True if roles exist AND have users assigned, False otherwise
    """
    # Get all roles for this organization
    roles = OrganizationRoles.query.filter_by(organization_id=org_id).all()

    if len(roles) == 0:
        logger.debug(f"[check_if_org_has_roles] Org {org_id}: No roles defined")
        return False

    # Check if any users are assigned to these roles
    role_ids = [r.id for r in roles]
    user_count = UserRoleCluster.query.filter(
        UserRoleCluster.role_cluster_id.in_(role_ids)
    ).count()

    has_assigned_users = user_count > 0

    logger.info(
        f"[check_if_org_has_roles] Org {org_id}: "
        f"{len(roles)} roles, {user_count} user assignments - "
        f"{'High maturity (role-based)' if has_assigned_users else 'Low maturity (no user assignments)'}"
    )

    return has_assigned_users


def get_role_competency_requirement(role_id: int, competency_id: int) -> int:
    """
    Get required competency level for a role from role-competency matrix.

    Args:
        role_id: Role ID (organization_roles.id, queried via role_cluster_id column)
        competency_id: Competency ID (1-18)

    Returns:
        Required level (0, 1, 2, 4, or 6)
    """
    matrix_entry = RoleCompetencyMatrix.query.filter_by(
        role_cluster_id=role_id,  # FIXED: Correct column name
        competency_id=competency_id
    ).first()

    if not matrix_entry:
        return 0  # No requirement

    # Get target level from matrix
    target = matrix_entry.role_competency_value or 0  # FIXED: Correct column name

    # Validate level
    if target not in [0, 1, 2, 4, 6]:
        logger.warning(f"[get_role_competency_requirement] Invalid level {target} for role {role_id}, competency {competency_id}")
        return 0

    return target


# =============================================================================
# ALGORITHM 3: Detect Gaps with Role Processing
# =============================================================================

def detect_gaps(
    org_id: int,
    main_targets: Dict[int, int],
    ttt_targets: Optional[Dict[int, int]] = None
) -> Dict:
    """
    Detect training gaps for all competencies.

    CRITICAL DESIGN PRINCIPLES:
    - Generate LO if ANY user has gap (not median-based)
    - Process by role if high maturity, organizationally if low maturity
    - Progressive levels: Current=0, Target=4 → Generate 1, 2, AND 4

    Args:
        org_id: Organization ID
        main_targets: Target levels per competency (excluding TTT)
        ttt_targets: TTT targets (if selected) - all level 6

    Returns:
        {
            'by_competency': {comp_id: gap_data},
            'by_level': {1: [...], 2: [...], 4: [...], 6: [...]},
            'metadata': {...}
        }

    Example:
        >>> gaps = detect_gaps(28, main_targets, ttt_targets)
        >>> # Check if competency 1 has gaps
        >>> if gaps['by_competency'][1]['has_gap']:
        ...     print(f"Levels needed: {gaps['by_competency'][1]['levels_needed']}")
    """

    logger.info(f"[detect_gaps] Processing org {org_id}")

    # Check if organization has roles
    has_roles = check_if_org_has_roles(org_id)

    logger.info(f"[detect_gaps] Has roles: {has_roles}")

    # Initialize structure
    gaps = {
        'by_competency': {},
        'by_level': {1: [], 2: [], 4: [], 6: []},
        'metadata': {
            'organization_id': org_id,
            'has_roles': has_roles,
            'generation_timestamp': datetime.utcnow().isoformat()
        }
    }

    # Process each competency (dynamic, not hardcoded)
    all_competency_ids = get_all_competency_ids()  # FIXED: Dynamic competency loading
    for competency_id in all_competency_ids:
        target_level = main_targets.get(competency_id, 0)

        if has_roles:
            # HIGH MATURITY: Process by role
            competency_gaps = process_competency_with_roles(
                org_id,
                competency_id,
                target_level
            )
        else:
            # LOW MATURITY: Process organizationally
            competency_gaps = process_competency_organizational(
                org_id,
                competency_id,
                target_level
            )

        gaps['by_competency'][competency_id] = competency_gaps

        # Organize by level for pyramid structure
        for level in competency_gaps.get('levels_needed', []):
            if level in VALID_LEVELS:
                competency = Competency.query.get(competency_id)
                gaps['by_level'][level].append({
                    'competency_id': competency_id,
                    'competency_name': competency.competency_name if competency else f"Competency {competency_id}",
                    'gap_data': competency_gaps
                })

    logger.info(f"[detect_gaps] Complete - processed {len(gaps['by_competency'])} competencies")

    return gaps


def process_competency_with_roles(
    org_id: int,
    competency_id: int,
    target_level: int
) -> Dict:
    """
    Process one competency for high maturity organization.

    Calculate gaps per role, check if ANY user has gap.

    Args:
        org_id: Organization ID
        competency_id: Competency ID (1-16)
        target_level: Target level from strategy (0-6)

    Returns:
        Competency gap data with role-specific details
    """

    logger.debug(f"[process_competency_with_roles] Org {org_id}, Comp {competency_id}, Target {target_level}")

    roles = OrganizationRoles.query.filter_by(organization_id=org_id).all()
    competency = Competency.query.get(competency_id)

    competency_data = {
        'competency_id': competency_id,
        'competency_name': competency.competency_name if competency else f"Competency {competency_id}",
        'target_level': target_level,
        'has_gap': False,
        'levels_needed': [],
        'roles': {}
    }

    if target_level == 0:
        logger.debug(f"[process_competency_with_roles] Target is 0 - no gaps")
        return competency_data

    # Process each role
    for role in roles:
        # Get all users in this role
        user_ids = get_users_in_role(role.id)

        if len(user_ids) == 0:
            logger.debug(f"[process_competency_with_roles] No users in role {role.role_name}")
            continue

        # Get assessment scores for these users
        user_scores = get_user_scores_for_competency(user_ids, competency_id)

        if len(user_scores) == 0:
            logger.debug(f"[process_competency_with_roles] No scores for role {role.role_name}")
            continue

        # Calculate statistics
        median_level = calculate_median(user_scores)
        mean_level = calculate_mean(user_scores)
        variance = calculate_variance(user_scores)

        # Determine which levels this role needs
        role_levels_needed = []
        level_details = {}

        for level in VALID_LEVELS:
            if level > target_level:
                continue  # This level exceeds strategy target

            # Count users needing this level
            # User needs level if: current_score < level <= target
            users_needing_level = [
                score for score in user_scores
                if score < level <= target_level
            ]

            if len(users_needing_level) > 0:
                # AT LEAST ONE user needs this level → Generate LO
                competency_data['has_gap'] = True

                if level not in competency_data['levels_needed']:
                    competency_data['levels_needed'].append(level)

                if level not in role_levels_needed:
                    role_levels_needed.append(level)

                # Store level-specific details
                level_details[level] = {
                    'users_needing': len(users_needing_level),
                    'total_users': len(user_scores),
                    'percentage': round(len(users_needing_level) / len(user_scores) * 100, 1)
                }

        # Store role data (only if this role has gaps)
        if len(role_levels_needed) > 0:
            # Calculate overall gap percentage for this role
            users_below_target = [
                score for score in user_scores
                if score < target_level
            ]
            gap_percentage = len(users_below_target) / len(user_scores)

            # Determine training method recommendation
            training_rec = determine_training_method(
                gap_percentage,
                variance,
                len(user_scores)
            )

            competency_data['roles'][role.id] = {
                'role_id': role.id,
                'role_name': role.role_name,
                'total_users': len(user_scores),
                'users_needing_training': len(users_below_target),
                'gap_percentage': round(gap_percentage * 100, 1),
                'median_level': median_level,
                'mean_level': round(mean_level, 2),
                'variance': round(variance, 2),
                'levels_needed': sorted(role_levels_needed),
                'level_details': level_details,
                'training_recommendation': training_rec
            }

    # Sort levels needed
    competency_data['levels_needed'] = sorted(competency_data['levels_needed'])

    return competency_data


def process_competency_organizational(
    org_id: int,
    competency_id: int,
    target_level: int
) -> Dict:
    """
    Process one competency for low maturity organization.

    All users treated as one group (no role separation).

    Args:
        org_id: Organization ID
        competency_id: Competency ID (1-16)
        target_level: Target level from strategy (0-6)

    Returns:
        Competency gap data with organizational stats
    """

    logger.debug(f"[process_competency_organizational] Org {org_id}, Comp {competency_id}, Target {target_level}")

    competency = Competency.query.get(competency_id)

    competency_data = {
        'competency_id': competency_id,
        'competency_name': competency.competency_name if competency else f"Competency {competency_id}",
        'target_level': target_level,
        'has_gap': False,
        'levels_needed': [],
        'organizational_stats': None
    }

    if target_level == 0:
        logger.debug(f"[process_competency_organizational] Target is 0 - no gaps")
        return competency_data

    # Get all user scores for this competency
    all_user_scores = get_all_user_scores_for_competency(org_id, competency_id)

    if len(all_user_scores) == 0:
        logger.debug(f"[process_competency_organizational] No assessment data")
        return competency_data

    # Calculate statistics
    median_level = calculate_median(all_user_scores)
    mean_level = calculate_mean(all_user_scores)
    variance = calculate_variance(all_user_scores)

    # Determine which levels needed
    levels_needed = []
    level_details = {}

    for level in VALID_LEVELS:
        if level > target_level:
            continue

        # Count users needing this level
        users_needing_level = [
            score for score in all_user_scores
            if score < level <= target_level
        ]

        if len(users_needing_level) > 0:
            # AT LEAST ONE user needs this level
            competency_data['has_gap'] = True
            levels_needed.append(level)

            level_details[level] = {
                'users_needing': len(users_needing_level),
                'total_users': len(all_user_scores),
                'percentage': round(len(users_needing_level) / len(all_user_scores) * 100, 1)
            }

    # Calculate overall gap percentage
    if len(levels_needed) > 0:
        users_below_target = [
            score for score in all_user_scores
            if score < target_level
        ]
        gap_percentage = len(users_below_target) / len(all_user_scores)

        # Determine training method recommendation
        training_rec = determine_training_method(
            gap_percentage,
            variance,
            len(all_user_scores)
        )

        competency_data['organizational_stats'] = {
            'total_users': len(all_user_scores),
            'users_needing_training': len(users_below_target),
            'gap_percentage': round(gap_percentage * 100, 1),
            'median_level': median_level,
            'mean_level': round(mean_level, 2),
            'variance': round(variance, 2),
            'level_details': level_details,
            'training_recommendation': training_rec
        }

    competency_data['levels_needed'] = sorted(levels_needed)

    return competency_data


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_users_in_role(role_id: int) -> List[int]:
    """Get all user IDs assigned to a role."""
    assignments = UserRoleCluster.query.filter_by(role_cluster_id=role_id).all()
    return [a.user_id for a in assignments]


def get_user_scores_for_competency(user_ids: List[int], competency_id: int) -> List[int]:
    """
    Get competency scores for specific users from their LATEST assessments only.

    When a user retakes an assessment, we only use their most recent scores.

    Args:
        user_ids: List of user IDs to query
        competency_id: Competency ID (1-18)

    Returns:
        List of integer scores (one per user from their latest assessment)
    """
    if not user_ids:
        return []

    from sqlalchemy import func

    # Get latest assessment_id per user
    latest_assessments = db.session.query(
        UserAssessment.user_id,
        func.max(UserAssessment.id).label('latest_assessment_id')
    ).filter(
        UserAssessment.user_id.in_(user_ids),
        UserAssessment.completed_at.isnot(None)
    ).group_by(UserAssessment.user_id).subquery()

    # Get scores only from latest assessments
    results = db.session.query(UserCompetencySurveyResult).join(
        latest_assessments,
        db.and_(
            UserCompetencySurveyResult.user_id == latest_assessments.c.user_id,
            UserCompetencySurveyResult.assessment_id == latest_assessments.c.latest_assessment_id
        )
    ).filter(
        UserCompetencySurveyResult.user_id.in_(user_ids),
        UserCompetencySurveyResult.competency_id == competency_id
    ).all()

    scores = []
    for result in results:
        if result.score is not None:
            scores.append(int(result.score))

    logger.debug(f"[get_user_scores_for_competency] Found {len(scores)} scores for competency {competency_id} (latest assessments only)")
    return scores


def get_all_user_scores_for_competency(org_id: int, competency_id: int) -> List[int]:
    """
    Get all user scores for a competency in an organization from LATEST assessments only.

    When users retake assessments, we only use their most recent scores.

    Args:
        org_id: Organization ID
        competency_id: Competency ID (1-18)

    Returns:
        List of integer scores for all users in the organization (one per user)
    """
    from sqlalchemy import func

    # Get latest assessment_id per user for this organization
    latest_assessments = db.session.query(
        UserAssessment.user_id,
        func.max(UserAssessment.id).label('latest_assessment_id')
    ).filter(
        UserAssessment.organization_id == org_id,
        UserAssessment.completed_at.isnot(None)
    ).group_by(UserAssessment.user_id).subquery()

    # Get scores only from latest assessments
    results = db.session.query(UserCompetencySurveyResult).join(
        latest_assessments,
        db.and_(
            UserCompetencySurveyResult.user_id == latest_assessments.c.user_id,
            UserCompetencySurveyResult.assessment_id == latest_assessments.c.latest_assessment_id
        )
    ).filter(
        UserCompetencySurveyResult.organization_id == org_id,
        UserCompetencySurveyResult.competency_id == competency_id
    ).all()

    scores = []
    for result in results:
        if result.score is not None:
            scores.append(int(result.score))

    logger.debug(f"[get_all_user_scores_for_competency] Org {org_id}, Competency {competency_id}: {len(scores)} scores (latest assessments only)")
    return scores


def calculate_median(values: List[int]) -> int:
    """Calculate median of integer values, snapping to valid pyramid levels.

    Valid pyramid levels are: 0, 1, 2, 4, 6 (no level 3 or 5)
    When median falls between valid levels, snap to nearest valid level.
    """
    if len(values) == 0:
        return 0

    sorted_values = sorted(values)
    n = len(sorted_values)

    if n % 2 == 0:
        # Even number: average of middle two
        raw_median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    else:
        # Odd number: middle value
        raw_median = sorted_values[n//2]

    # Snap to nearest valid pyramid level [0, 1, 2, 4, 6]
    valid_levels = [0, 1, 2, 4, 6]
    closest_level = min(valid_levels, key=lambda x: abs(x - raw_median))
    return closest_level


def calculate_mean(values: List[int]) -> float:
    """Calculate mean of values."""
    if len(values) == 0:
        return 0.0
    return sum(values) / len(values)


def calculate_variance(values: List[int]) -> float:
    """Calculate variance of values."""
    if len(values) < 2:
        return 0.0

    mean = calculate_mean(values)
    squared_diffs = [(x - mean) ** 2 for x in values]
    return sum(squared_diffs) / len(values)


# =============================================================================
# ALGORITHM 4: Determine Training Method
# =============================================================================

def determine_training_method(
    gap_percentage: float,
    variance: float,
    total_users: int
) -> Dict:
    """
    Recommend training delivery method based on distribution.

    ALGORITHM 4 from Design v5 - Complete implementation with cost-aware
    decision rules based on gap percentage and variance analysis.

    This is Phase 3 logic, but calculated and DISPLAYED in Phase 2
    to provide context for admin decision-making.

    Based on: DISTRIBUTION_SCENARIO_ANALYSIS.md and
              LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE.md

    Args:
        gap_percentage: Fraction of users needing training (0.0 to 1.0)
        variance: Statistical variance of scores
        total_users: Total number of users

    Returns:
        {
            'method': str,        # Specific training method recommendation
            'rationale': str,     # Explanation with context
            'cost_level': str,    # 'Low', 'Medium', 'Low to Medium'
            'icon': str          # Material Design icon for UI
        }

    Decision Matrix:
        Gap %       | Variance | Users | Method
        ------------|----------|-------|---------------------------
        Any         | Any      | < 3   | Individual Coaching
        Any         | > 4.0    | Any   | Blended (Multiple Tracks)
        < 20%       | Low      | Any   | Individual/Certification
        20-40%      | Low      | Any   | Small Group/Mentoring
        40-70%      | Low      | Any   | Group with Differentiation
        70-100%     | Low      | Any   | Group Training

    Example:
        >>> rec = determine_training_method(0.85, 1.2, 20)
        >>> print(rec['method'])
        'Group Training (Experts as Mentors)'
        >>> print(rec['cost_level'])
        'Low'
    """

    # Edge case: Very small group (< 3 users)
    if total_users < 3:
        return {
            'method': 'Individual Coaching',
            'rationale': 'Very small group - individual approach more effective',
            'cost_level': 'Low',
            'icon': 'mdi-account'
        }

    # High variance suggests diverse needs (bimodal or wide spread)
    if variance > 4.0:
        return {
            'method': 'Blended Approach (Multiple Tracks)',
            'rationale': (
                f'High variance ({variance:.1f}) indicates diverse competency '
                f'levels - differentiated approach recommended'
            ),
            'cost_level': 'Medium',
            'icon': 'mdi-format-list-bulleted'
        }

    # Decision based on gap percentage (main logic)

    if gap_percentage < 0.20:
        # Less than 20% need training
        return {
            'method': 'Individual Coaching or External Certification',
            'rationale': (
                f'Only {gap_percentage:.0%} need training - group training '
                f'not cost-effective'
            ),
            'cost_level': 'Medium',
            'icon': 'mdi-account-tie'
        }

    elif gap_percentage < 0.40:
        # 20-40% need training
        return {
            'method': 'Small Group Training or Mentoring',
            'rationale': (
                f'{gap_percentage:.0%} need training - small group or '
                f'mentoring pairs recommended'
            ),
            'cost_level': 'Low to Medium',
            'icon': 'mdi-account-group'
        }

    elif gap_percentage < 0.70:
        # 40-70% need training
        return {
            'method': 'Group Training with Differentiation',
            'rationale': (
                f'{gap_percentage:.0%} need training - mixed group with '
                f'flexibility for varied starting levels'
            ),
            'cost_level': 'Low',
            'icon': 'mdi-school'
        }

    else:
        # 70%+ need training
        expert_percentage = 1.0 - gap_percentage

        if expert_percentage >= 0.10:
            # At least 10% are experts
            return {
                'method': 'Group Training (Experts as Mentors)',
                'rationale': (
                    f'{gap_percentage:.0%} need training, '
                    f'{expert_percentage:.0%} can serve as mentors/helpers'
                ),
                'cost_level': 'Low',
                'icon': 'mdi-school'
            }
        else:
            # Almost everyone needs training (90%+)
            return {
                'method': 'Group Classroom Training',
                'rationale': (
                    f'{gap_percentage:.0%} need training - group approach '
                    f'most cost-effective'
                ),
                'cost_level': 'Low',
                'icon': 'mdi-school'
            }


# =============================================================================
# ALGORITHM 5: Process TTT Gaps (Simplified)
# =============================================================================

def process_ttt_gaps(
    org_id: int,
    ttt_targets: Optional[Dict[int, int]]
) -> Optional[Dict]:
    """
    Process Train the Trainer gaps.

    ALGORITHM 5 from Design v5 - Simplified implementation that identifies
    which competencies need Level 6 training for mastery development.

    SIMPLIFIED: Just identify which competencies need Level 6 training.
    No internal/external trainer selection - that's deferred to Phase 3.

    Based on: LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE_PART2.md

    Args:
        org_id: Organization ID
        ttt_targets: Dictionary {competency_id: 6} for all competencies
                     None if TTT strategy not selected

    Returns:
        {
            'enabled': True,
            'competencies': [
                {
                    'competency_id': int,
                    'competency_name': str,
                    'level': 6,
                    'level_name': 'Mastering SE',
                    'users_needing': int,
                    'total_users': int,
                    'gap_percentage': float
                },
                ...
            ]
        } or None if TTT not selected or no gaps exist

    Edge Cases:
        - All users already at Level 6: Return None (no training needed)
        - No assessment data: Assume gap exists, include competency
        - Some users at Level 6: Still include (ANY gap principle)
        - TTT not selected: Return None

    Example:
        >>> ttt_targets = {1: 6, 2: 6, ..., 16: 6}  # All competencies Level 6
        >>> result = process_ttt_gaps(28, ttt_targets)
        >>> if result:
        ...     print(f"{len(result['competencies'])} competencies need TTT")
    """

    logger.info(f"[process_ttt_gaps] Processing org {org_id}")

    # Check if TTT is selected
    if ttt_targets is None:
        logger.info("[process_ttt_gaps] TTT not selected - returning None")
        return None

    # Initialize TTT data structure
    ttt_data = {
        'enabled': True,
        'competencies': []
    }

    # Process each competency
    all_competency_ids = get_all_competency_ids()

    for competency_id in all_competency_ids:
        target_level = ttt_targets.get(competency_id, 0)

        # Validate: TTT should always target Level 6
        if target_level != 6:
            logger.warning(
                f"[process_ttt_gaps] TTT target for competency {competency_id} "
                f"is {target_level}, expected 6 - skipping"
            )
            continue

        # Get competency details
        competency = Competency.query.get(competency_id)
        competency_name = competency.competency_name if competency else f"Competency {competency_id}"

        # Get all user scores for this competency
        all_user_scores = get_all_user_scores_for_competency(org_id, competency_id)

        if len(all_user_scores) == 0:
            # No assessment data - assume gap exists
            logger.debug(
                f"[process_ttt_gaps] No assessment data for competency {competency_id} "
                f"- assuming gap exists"
            )
            users_needing_mastery = []
            gap_percentage = 1.0  # 100% need training (unknown state)
            total_users = 0
        else:
            # Count users below Level 6
            users_needing_mastery = [
                score for score in all_user_scores
                if score < 6
            ]
            total_users = len(all_user_scores)
            gap_percentage = len(users_needing_mastery) / total_users

            logger.debug(
                f"[process_ttt_gaps] Competency {competency_id}: "
                f"{len(users_needing_mastery)}/{total_users} users need Level 6 "
                f"({gap_percentage:.1%})"
            )

        # If ANY user needs Level 6 (or no data) → Include in TTT
        # This follows the "ANY gap" principle
        if len(all_user_scores) == 0 or len(users_needing_mastery) > 0:
            ttt_data['competencies'].append({
                'competency_id': competency_id,
                'competency_name': competency_name,
                'level': 6,
                'level_name': 'Mastering SE',
                'users_needing': len(users_needing_mastery),
                'total_users': total_users,
                'gap_percentage': round(gap_percentage * 100, 1)
            })

    # Return None if no competencies need TTT
    if len(ttt_data['competencies']) == 0:
        logger.info("[process_ttt_gaps] No competencies need TTT - returning None")
        return None

    logger.info(
        f"[process_ttt_gaps] Complete - {len(ttt_data['competencies'])} "
        f"competencies need Level 6 training"
    )

    return ttt_data


# =============================================================================
# ALGORITHM 6: Generate Learning Objectives
# =============================================================================

def generate_learning_objectives(
    gaps_by_competency: Dict,
    pmt_context: Optional[Dict] = None
) -> Dict:
    """
    Generate learning objectives for all competencies with gaps.

    ALGORITHM 6 from Design v5 - Generates customized learning objectives
    based on standard templates and optional PMT customization.

    Based on: LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE_PART2.md

    Args:
        gaps_by_competency: Output from detect_gaps()['by_competency']
            {
                competency_id: {
                    'has_gap': bool,
                    'levels_needed': [1, 2, 4],
                    'competency_name': str,
                    ...
                }
            }
        pmt_context: Optional PMT context for customization
            {
                'processes': 'Company SE processes',
                'methods': 'Currently used methods',
                'tools': 'Existing tool landscape'
            }

    Returns:
        {
            competency_id: {
                1: {
                    'level': 1,
                    'level_name': 'Performing Basics',
                    'objective_text': 'Participants know...',
                    'customized': bool,
                    'source': 'template' | 'pmt_customized'
                },
                2: {...},
                4: {...}
            }
        }

    Edge Cases:
        - LLM fails: Fallback to standard template
        - PMT missing: Use standard templates only
        - Invalid template: Log error, use generic objective

    Example:
        >>> gaps = detect_gaps(28, main_targets)
        >>> objectives = generate_learning_objectives(
        ...     gaps['by_competency'],
        ...     pmt_context={'processes': 'ISO 26262', 'tools': 'DOORS'}
        ... )
        >>> print(objectives[1][2]['objective_text'])
        'Participants understand how ISO 26262 processes...'
    """

    logger.info(f"[generate_learning_objectives] Processing {len(gaps_by_competency)} competencies")

    # Load templates from JSON
    templates = load_learning_objective_templates()

    if not templates:
        logger.error("[generate_learning_objectives] Failed to load templates")
        raise ValueError("Learning objective templates not available")

    # Check if PMT customization is enabled
    use_pmt = pmt_context is not None and len(pmt_context) > 0
    logger.info(f"[generate_learning_objectives] PMT customization enabled: {use_pmt}")

    # Generate objectives for each competency
    # Generate for ALL levels up to target (not just gaps) so grayed items show objectives too
    all_objectives = {}

    for competency_id, gap_data in gaps_by_competency.items():
        target_level = gap_data.get('target_level', 0)
        if target_level == 0:
            continue  # No target set by strategy

        competency_name = gap_data.get('competency_name', f'Competency {competency_id}')

        # Generate objectives for all levels up to target level
        levels_to_generate = [lvl for lvl in VALID_LEVELS if lvl <= target_level]

        logger.debug(
            f"[generate_learning_objectives] Generating for {competency_name}: "
            f"All levels up to {target_level}: {levels_to_generate}"
        )

        competency_objectives = {}

        for level in levels_to_generate:
            # Get standard template with PMT breakdown (v2 format)
            template_data = get_template_objective_with_pmt(templates, competency_name, level)
            template_text = template_data.get('objective_text')
            template_pmt = template_data.get('pmt_breakdown')
            has_template_pmt = template_data.get('has_pmt', False)

            if not template_text:
                logger.warning(
                    f"[generate_learning_objectives] No template for "
                    f"{competency_name} Level {level} - using generic"
                )
                template_text = generate_generic_objective(competency_name, level)
                has_template_pmt = False
                template_pmt = None

            # PMT Customization Logic:
            # - Templates WITH pmt_breakdown -> customize each breakdown section (process/method/tool)
            # - Templates WITHOUT pmt_breakdown -> use template text as-is (no LLM call needed)
            customized = False
            final_text = template_text
            final_pmt_breakdown = template_pmt

            if use_pmt and has_template_pmt and template_pmt:
                # This template has PMT breakdown - customize each section with LLM
                print(
                    f"[generate_learning_objectives] Customizing PMT breakdown for "
                    f"{competency_name} Level {level}"
                )
                try:
                    customized_breakdown = customize_pmt_breakdown(
                        competency_name,
                        level,
                        template_pmt,
                        pmt_context
                    )

                    if customized_breakdown:
                        final_pmt_breakdown = customized_breakdown
                        customized = True
                        # Also update the unified text to reflect customization
                        # by combining the customized breakdown sections
                        combined_sections = []
                        if customized_breakdown.get('process'):
                            combined_sections.append(customized_breakdown['process'])
                        if customized_breakdown.get('method'):
                            combined_sections.append(customized_breakdown['method'])
                        if customized_breakdown.get('tool'):
                            combined_sections.append(customized_breakdown['tool'])
                        if combined_sections:
                            final_text = ' '.join(combined_sections)

                except Exception as e:
                    logger.error(
                        f"[generate_learning_objectives] PMT breakdown customization failed "
                        f"for {competency_name} Level {level}: {e}"
                    )
                    # Fallback to standard template breakdown
            elif use_pmt and not has_template_pmt:
                # No PMT breakdown in template - just use template text as-is
                # These competencies don't have process/method/tool structure
                print(
                    f"[generate_learning_objectives] No PMT breakdown for "
                    f"{competency_name} Level {level} - using template text"
                )

            # Store objective with PMT breakdown from template (or customized)
            objective_entry = {
                'level': level,
                'level_name': get_level_name(level),
                'objective_text': final_text,
                'customized': customized,
                'source': 'pmt_customized' if customized else 'template',
                'has_pmt_breakdown': has_template_pmt
            }

            # Include PMT breakdown if available (original or customized)
            if has_template_pmt and final_pmt_breakdown:
                objective_entry['pmt_breakdown'] = final_pmt_breakdown

            competency_objectives[level] = objective_entry

        all_objectives[competency_id] = competency_objectives

    logger.info(
        f"[generate_learning_objectives] Complete - generated objectives for "
        f"{len(all_objectives)} competencies"
    )

    return all_objectives


def load_learning_objective_templates() -> Optional[Dict]:
    """
    Load learning objective templates from JSON file.

    Returns:
        {
            'competencies': [...],
            'learningObjectiveTemplates': {
                'Systems Thinking': {
                    '1': 'The participant knows...',
                    '2': 'The participant understands...',
                    '4': 'The participant is able to...',
                    '6': 'The participant is able to...'
                },
                ...
            }
        } or None if loading fails
    """
    import json
    import os
    from pathlib import Path

    # Path to template JSON (v2 with PMT breakdown structure)
    # Supports both Docker deployment and local development
    _current_file = Path(__file__).resolve()
    _backend_root = _current_file.parent.parent.parent  # services -> app -> backend

    # Path 1: Docker path (template inside backend)
    docker_path = _backend_root / 'data' / 'templates' / 'se_qpt_learning_objectives_template_v2.json'
    if docker_path.exists():
        template_path = str(docker_path)
    else:
        # Path 2: Local dev path (template at project root)
        _project_root = _backend_root.parent.parent  # backend -> src -> project_root
        template_path = str(_project_root / 'data' / 'source' / 'Phase 2' / 'se_qpt_learning_objectives_template_v2.json')

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"[load_learning_objective_templates] Loaded templates from {template_path}")
            return data

    except FileNotFoundError:
        logger.error(f"[load_learning_objective_templates] Template file not found: {template_path}")
        return None

    except json.JSONDecodeError as e:
        logger.error(f"[load_learning_objective_templates] Invalid JSON: {e}")
        return None

    except Exception as e:
        logger.error(f"[load_learning_objective_templates] Unexpected error: {e}")
        return None


def get_template_objective(templates: Dict, competency_name: str, level: int) -> Optional[str]:
    """
    Get learning objective template text for a competency and level.

    Args:
        templates: Loaded template data
        competency_name: Name of competency (e.g., 'Systems Thinking')
        level: Level (1, 2, 4, or 6)

    Returns:
        Template text or None if not found

    Note:
        Template v2 format supports both:
        - Simple string: "The participant knows..."
        - Dict with PMT: {"unified": "...", "pmt_breakdown": {...}}

        This function returns the unified/simple text for backward compatibility.
        Use get_template_objective_with_pmt() to get full PMT breakdown.
    """
    template_dict = templates.get('learningObjectiveTemplates', {})

    if competency_name not in template_dict:
        logger.warning(
            f"[get_template_objective] Competency '{competency_name}' "
            f"not found in templates"
        )
        return None

    competency_templates = template_dict[competency_name]
    level_str = str(level)

    if level_str not in competency_templates:
        logger.warning(
            f"[get_template_objective] Level {level} not found for "
            f"competency '{competency_name}'"
        )
        return None

    template_data = competency_templates[level_str]

    # Handle both string and dict (with PMT breakdown) formats
    if isinstance(template_data, dict):
        return template_data.get('unified', '')
    else:
        return template_data


def get_template_objective_with_pmt(templates: Dict, competency_name: str, level: int) -> Dict:
    """
    Get learning objective template with PMT breakdown for a competency and level.

    Args:
        templates: Loaded template data
        competency_name: Name of competency (e.g., 'Systems Thinking')
        level: Level (1, 2, 4, or 6)

    Returns:
        Dict with structure:
        {
            'objective_text': str,  # Unified text
            'has_pmt': bool,        # Whether PMT breakdown exists
            'pmt_breakdown': {      # Only present if has_pmt is True
                'process': str or None,
                'method': str or None,
                'tool': str or None
            }
        }
    """
    template_dict = templates.get('learningObjectiveTemplates', {})

    result = {
        'objective_text': None,
        'has_pmt': False,
        'pmt_breakdown': None
    }

    if competency_name not in template_dict:
        logger.warning(
            f"[get_template_objective_with_pmt] Competency '{competency_name}' "
            f"not found in templates"
        )
        return result

    competency_templates = template_dict[competency_name]
    level_str = str(level)

    if level_str not in competency_templates:
        logger.warning(
            f"[get_template_objective_with_pmt] Level {level} not found for "
            f"competency '{competency_name}'"
        )
        return result

    template_data = competency_templates[level_str]

    # Handle both string and dict (with PMT breakdown) formats
    if isinstance(template_data, dict):
        result['objective_text'] = template_data.get('unified', '')
        if 'pmt_breakdown' in template_data:
            result['has_pmt'] = True
            result['pmt_breakdown'] = template_data['pmt_breakdown']
    else:
        result['objective_text'] = template_data

    return result


def generate_generic_objective(competency_name: str, level: int) -> str:
    """
    Generate a generic learning objective when template is missing.

    Args:
        competency_name: Name of competency
        level: Level (1, 2, 4, or 6)

    Returns:
        Generic objective text
    """
    level_descriptions = {
        1: 'know the basic concepts',
        2: 'understand the fundamental principles',
        4: 'apply the competency in practical situations',
        6: 'demonstrate mastery and teach others'
    }

    description = level_descriptions.get(level, 'develop proficiency')

    return f"Participants will {description} of {competency_name}."


def get_level_name(level: int) -> str:
    """
    Get descriptive name for competency level.

    Args:
        level: Level (1, 2, 4, or 6)

    Returns:
        Level name string
    """
    level_names = {
        1: 'Performing Basics',
        2: 'Performing Appropriately',
        4: 'Shaping Adequately',
        6: 'Mastering SE'
    }

    return level_names.get(level, f'Level {level}')


# =============================================================================
# Cross-Contamination Validation Functions
# =============================================================================

# Keywords that indicate content from OTHER competencies (cross-contamination)
# Key = competency name, Value = keywords that should NOT appear in that competency's LO
CROSS_CONTAMINATION_KEYWORDS = {
    'Agile Methods': [
        'sysml', 'architecture model', 'bdd', 'ibd', 'req diagram',
        'requirements diagram', 'block definition', 'internal block',
        'architecture diagram', 'system architecture', 'logical architecture',
        'physical architecture', 'doors', 'requirements database',
        'test plan', 'verification', 'validation plan'
    ],
    'System Architecting': [
        'agile values', 'scrum', 'sprint', 'kanban', 'user story',
        'retrospective', 'agile manifesto', 'daily standup'
    ],
    'Requirements Definition': [
        'architecture model', 'sysml diagram', 'bdd', 'ibd',
        'test execution', 'verification report', 'agile sprint'
    ],
    'Integration, Verification, Validation': [
        'architecture model', 'sysml', 'requirements elicitation',
        'stakeholder analysis', 'agile values'
    ],
    'Project Management': [
        'sysml', 'architecture diagram', 'requirements traceability',
        'test execution', 'agile values'
    ],
    'Configuration Management': [
        'sysml', 'architecture model', 'requirements elicitation',
        'agile sprint', 'test execution'
    ],
    'Systems Thinking': [
        'sysml diagram', 'requirements database', 'test plan',
        'project schedule', 'configuration item'
    ],
    'Lifecycle Consideration': [
        'sysml diagram', 'requirements database', 'agile sprint',
        'configuration item'
    ],
    'Customer / Value Orientation': [
        'sysml diagram', 'architecture model', 'test plan',
        'configuration item', 'project schedule'
    ],
    'Systems Modelling and Analysis': [
        'agile sprint', 'scrum', 'kanban', 'requirements elicitation',
        'test execution', 'project schedule'
    ],
    'Communication': [
        'sysml', 'requirements database', 'test plan', 'architecture model',
        'configuration item'
    ],
    'Leadership': [
        'sysml', 'requirements database', 'test plan', 'architecture model',
        'configuration item'
    ],
    'Self-Organization': [
        'sysml', 'requirements database', 'test plan', 'architecture model',
        'configuration item'
    ],
    'Decision Management': [
        'sysml', 'architecture diagram', 'requirements database',
        'test execution', 'agile sprint'
    ],
    'Information Management': [
        'sysml', 'architecture diagram', 'requirements traceability',
        'test execution', 'agile sprint'
    ],
    'Operation and Support': [
        'sysml', 'architecture diagram', 'requirements elicitation',
        'agile sprint', 'project schedule'
    ]
}


def _validate_text_relevance(
    competency_name: str,
    original_text: str,
    customized_text: str
) -> bool:
    """
    Validate that customized text stays within competency boundaries.

    Checks if the customized text contains keywords from other competencies
    that would indicate cross-contamination/hallucination.

    Args:
        competency_name: Name of the competency being customized
        original_text: Original template text
        customized_text: LLM-customized text

    Returns:
        True if text appears relevant to competency, False if cross-contamination detected
    """
    forbidden_keywords = CROSS_CONTAMINATION_KEYWORDS.get(competency_name, [])

    if not forbidden_keywords:
        # No specific rules for this competency
        return True

    customized_lower = customized_text.lower()
    original_lower = original_text.lower()

    for keyword in forbidden_keywords:
        keyword_lower = keyword.lower()
        # Only flag if keyword is in customized but NOT in original
        # (If it was in original, it's intentional)
        if keyword_lower in customized_lower and keyword_lower not in original_lower:
            logger.warning(
                f"[_validate_text_relevance] Forbidden keyword '{keyword}' found in "
                f"{competency_name} customization (not in original)"
            )
            return False

    return True


def _validate_customization_relevance(
    competency_name: str,
    original_breakdown: Dict,
    customized_breakdown: Dict
) -> bool:
    """
    Validate that customized PMT breakdown stays within competency boundaries.

    Args:
        competency_name: Name of the competency being customized
        original_breakdown: Original PMT breakdown dict
        customized_breakdown: LLM-customized PMT breakdown dict

    Returns:
        True if customization appears relevant, False if cross-contamination detected
    """
    # Combine all original text
    original_text_parts = []
    for key in ['process', 'method', 'tool']:
        if original_breakdown.get(key):
            original_text_parts.append(original_breakdown[key])
    original_text = ' '.join(original_text_parts)

    # Combine all customized text
    customized_text_parts = []
    for key in ['process', 'method', 'tool']:
        if customized_breakdown.get(key):
            customized_text_parts.append(customized_breakdown[key])
    customized_text = ' '.join(customized_text_parts)

    return _validate_text_relevance(competency_name, original_text, customized_text)


def customize_objective_with_pmt(
    competency_name: str,
    level: int,
    template_text: str,
    pmt_context: Dict
) -> Optional[str]:
    """
    Customize learning objective with PMT context using LLM.

    Uses OpenAI GPT-4 to adapt standard template to company context.

    Args:
        competency_name: Name of competency
        level: Level (1, 2, 4, or 6)
        template_text: Standard template text
        pmt_context: PMT context dictionary

    Returns:
        Customized objective text or None if customization fails

    Raises:
        Exception: If LLM call fails (caller should handle)
    """
    import openai
    import os

    # Get OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("[customize_objective_with_pmt] No OpenAI API key - skipping customization")
        return None

    # Extract PMT details
    processes = pmt_context.get('processes', 'company processes')
    methods = pmt_context.get('methods', 'current methods')
    tools = pmt_context.get('tools', 'existing tools')

    # Build prompt
    prompt = f"""You are an expert in Systems Engineering qualification planning.

CRITICAL CONSTRAINT: You MUST ONLY customize the exact text I provide below. Do NOT add content from other SE competencies or topics.

Your task: Adapt the following learning objective to a specific company context.

Competency: {competency_name}
Level: {level} - {get_level_name(level)}

IMPORTANT: This learning objective is ONLY about "{competency_name}". Do NOT include content about other competencies.

Standard Learning Objective:
{template_text}

Company Context (PMT):
- Processes: {processes}
- Methods: {methods}
- Tools: {tools}

Instructions:
1. ONLY modify text to incorporate company-specific tools/methods/processes where relevant
2. Keep the EXACT SAME competency topic - do NOT change what the objective is about
3. If the company PMT does not relate to this competency, return the ORIGINAL TEXT UNCHANGED
4. Maintain the same structure (e.g., "Participants know...", "Participants understand...")
5. Keep it concise (1-3 sentences maximum)
6. Do NOT add content about topics not mentioned in the original text

Return ONLY the customized learning objective text (or the original if PMT doesn't apply), nothing else."""

    try:
        # Call OpenAI GPT-4 using new SDK (v1.x)
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in Systems Engineering education. Stay strictly within the competency topic provided."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,  # Lower temperature for more deterministic, less hallucination
            timeout=10  # 10 second timeout
        )

        customized_text = response.choices[0].message.content.strip()

        # Validate for cross-contamination
        if not _validate_text_relevance(competency_name, template_text, customized_text):
            logger.warning(
                f"[customize_objective_with_pmt] Cross-contamination detected for "
                f"{competency_name} Level {level} - returning None"
            )
            return None

        logger.debug(
            f"[customize_objective_with_pmt] LLM customization successful for "
            f"{competency_name} Level {level}"
        )

        return customized_text

    except openai.APITimeoutError:
        logger.warning(
            f"[customize_objective_with_pmt] LLM timeout for "
            f"{competency_name} Level {level}"
        )
        return None

    except openai.RateLimitError:
        logger.warning(
            f"[customize_objective_with_pmt] Rate limit exceeded"
        )
        return None

    except Exception as e:
        logger.error(
            f"[customize_objective_with_pmt] LLM error for "
            f"{competency_name} Level {level}: {e}"
        )
        raise


def customize_pmt_breakdown(
    competency_name: str,
    level: int,
    pmt_breakdown: Dict,
    pmt_context: Dict
) -> Optional[Dict]:
    """
    Customize each PMT breakdown section with organization's PMT context using LLM.

    This is used for competencies that have a pmt_breakdown structure in the template
    (e.g., Project Management, System Architecting, Requirements Definition).

    Args:
        competency_name: Name of competency
        level: Level (1, 2, 4, or 6)
        pmt_breakdown: Template PMT breakdown dict with 'process', 'method', 'tool' keys
        pmt_context: Organization's PMT context dictionary

    Returns:
        Customized PMT breakdown dict or None if customization fails
    """
    import openai
    import os

    # Get OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("[customize_pmt_breakdown] No OpenAI API key - skipping customization")
        return None

    # Extract organization's PMT details
    org_processes = pmt_context.get('processes', 'company processes')
    org_methods = pmt_context.get('methods', 'current methods')
    org_tools = pmt_context.get('tools', 'existing tools')

    # Build a single prompt to customize all PMT sections at once (more efficient)
    sections_to_customize = []
    for section_type in ['process', 'method', 'tool']:
        if section_type in pmt_breakdown and pmt_breakdown[section_type]:
            sections_to_customize.append({
                'type': section_type,
                'text': pmt_breakdown[section_type]
            })

    if not sections_to_customize:
        return pmt_breakdown  # Nothing to customize

    # Build prompt for customization
    sections_text = "\n".join([
        f"- {s['type'].upper()}: {s['text']}"
        for s in sections_to_customize
    ])

    prompt = f"""You are an expert in Systems Engineering qualification planning.

CRITICAL CONSTRAINT: You MUST ONLY customize the exact text I provide below. Do NOT add content from other SE competencies or topics.

Your task: Adapt each section of the following learning objective breakdown to a specific company context.

Competency: {competency_name}
Level: {level} - {get_level_name(level)}

IMPORTANT: This learning objective is ONLY about "{competency_name}". Do NOT include content about other competencies (e.g., if this is about Agile Methods, do NOT mention SysML, architecture diagrams, requirements tools, etc.).

Original Learning Objective Sections (KEEP THE CORE MEANING AND TOPIC INTACT):
{sections_text}

Company Context (PMT):
- Processes: {org_processes}
- Methods: {org_methods}
- Tools: {org_tools}

Instructions:
1. ONLY modify text to incorporate company-specific tools/methods/processes where relevant
2. Keep the EXACT SAME competency topic as the original text - do NOT change what the objective is about
3. If the company PMT does not relate to this competency's content, return the ORIGINAL TEXT UNCHANGED
4. Maintain the same structure (e.g., "The participant knows...", "The participant can...")
5. Keep each section concise (1-2 sentences)
6. Do NOT add content about topics not mentioned in the original text

If the company PMT context does not apply to this competency, respond with:
{{"unchanged": true}}

Otherwise, return the customized sections in this EXACT JSON format:
{{
  "process": "customized process text here (or null if not present in original)",
  "method": "customized method text here (or null if not present in original)",
  "tool": "customized tool text here (or null if not present in original)"
}}

Return ONLY the JSON object, nothing else."""

    try:
        # Call OpenAI GPT-4 using new SDK (v1.x)
        from openai import OpenAI
        import json
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in Systems Engineering education. Return only valid JSON. Stay strictly within the competency topic provided."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3,  # Lower temperature for more deterministic, less hallucination
            timeout=15  # 15 second timeout for this more complex task
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            customized = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                customized = json.loads(json_match.group())
            else:
                logger.warning(f"[customize_pmt_breakdown] Could not parse JSON response")
                return None

        # Check if LLM returned "unchanged" response (PMT doesn't apply to this competency)
        if customized.get('unchanged'):
            logger.info(
                f"[customize_pmt_breakdown] LLM indicated PMT doesn't apply to "
                f"{competency_name} Level {level} - returning original"
            )
            return pmt_breakdown

        # Validate for cross-contamination before accepting customization
        if not _validate_customization_relevance(competency_name, pmt_breakdown, customized):
            logger.warning(
                f"[customize_pmt_breakdown] Cross-contamination detected for "
                f"{competency_name} Level {level} - returning original"
            )
            return pmt_breakdown

        # Validate and merge with original (keep original if LLM didn't provide)
        result = {}
        for section_type in ['process', 'method', 'tool']:
            if section_type in pmt_breakdown and pmt_breakdown[section_type]:
                # Use customized if available and non-null, else use original
                if customized.get(section_type):
                    result[section_type] = customized[section_type]
                else:
                    result[section_type] = pmt_breakdown[section_type]

        print(
            f"[customize_pmt_breakdown] PMT breakdown customization successful for "
            f"{competency_name} Level {level}"
        )

        return result

    except openai.APITimeoutError:
        logger.warning(
            f"[customize_pmt_breakdown] LLM timeout for "
            f"{competency_name} Level {level}"
        )
        return None

    except openai.RateLimitError:
        logger.warning(
            f"[customize_pmt_breakdown] Rate limit exceeded"
        )
        return None

    except Exception as e:
        logger.error(
            f"[customize_pmt_breakdown] LLM error for "
            f"{competency_name} Level {level}: {e}"
        )
        return None


# =============================================================================
# ALGORITHM 7: Structure Pyramid Output
# =============================================================================

def structure_pyramid_output(
    org_id: int,
    gaps_data: Dict,
    objectives: Dict,
    main_targets: Dict[int, int],
    has_roles: bool
) -> Dict:
    """
    Structure learning objectives into pyramid format.

    ALGORITHM 7 from Design v5 - Organizes all 16 competencies into
    4 pyramid levels, with proper graying logic for levels exceeding targets.

    Based on: LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE_PART2.md

    Args:
        org_id: Organization ID
        gaps_data: Output from detect_gaps()
        objectives: Output from generate_learning_objectives()
        main_targets: Target levels per competency
        has_roles: Whether organization has roles defined

    Returns:
        {
            'levels': {
                1: {
                    'level': 1,
                    'level_name': 'Performing Basics',
                    'competencies': [
                        {
                            'competency_id': int,
                            'competency_name': str,
                            'status': 'training_required' | 'achieved' | 'not_targeted',
                            'grayed_out': bool,
                            'learning_objective': {...} or None,
                            'message': str (if grayed)
                        },
                        ... (all 16 competencies)
                    ]
                },
                2: {...},
                4: {...},
                6: {...}
            },
            'metadata': {
                'organization_id': int,
                'has_roles': bool,
                'total_competencies': int,
                'active_competencies_per_level': {1: 5, 2: 8, 4: 3, 6: 0},
                'generation_timestamp': str
            }
        }

    Example:
        >>> pyramid = structure_pyramid_output(28, gaps, objectives, main_targets, True)
        >>> level_2 = pyramid['levels'][2]
        >>> print(f"Level 2 has {len(level_2['competencies'])} competencies")
        Level 2 has 16 competencies
    """

    logger.info(f"[structure_pyramid_output] Structuring pyramid for org {org_id}")

    all_competency_ids = get_all_competency_ids()
    gaps_by_competency = gaps_data.get('by_competency', {})

    # Get excluded competencies (existing training offers)
    excluded_comp_ids = get_excluded_competency_ids(org_id)
    if excluded_comp_ids:
        logger.info(f"[structure_pyramid_output] Excluding {len(excluded_comp_ids)} competencies with existing training")

    pyramid = {
        'levels': {},
        'metadata': {
            'organization_id': org_id,
            'has_roles': has_roles,
            'total_competencies': len(all_competency_ids),
            'active_competencies_per_level': {},
            'generation_timestamp': datetime.utcnow().isoformat()
        }
    }

    # Build each pyramid level
    for level in VALID_LEVELS:
        level_data = {
            'level': level,
            'level_name': get_level_name(level),
            'competencies': []
        }

        active_count = 0

        # Process all competencies (show all 16, even if grayed)
        for competency_id in all_competency_ids:
            competency = Competency.query.get(competency_id)
            competency_name = competency.competency_name if competency else f"Competency {competency_id}"

            target_level = main_targets.get(competency_id, 0)
            gap_data = gaps_by_competency.get(competency_id, {})
            levels_needed = gap_data.get('levels_needed', [])

            # Determine if this competency needs training at this level
            needs_this_level = level in levels_needed

            # Determine if this level should be grayed out
            grayed_out, status, message = check_if_grayed(
                competency_id,
                level,
                target_level,
                needs_this_level
            )

            # Get learning objective for this level (always, even if grayed)
            # This allows UI to show objectives for all competencies
            learning_objective = None
            if competency_id in objectives and level in objectives[competency_id]:
                learning_objective = objectives[competency_id][level]

            # Count as active only if not grayed and needs this level
            if not grayed_out and needs_this_level:
                active_count += 1

            # Extract current level (median) from gap_data for display
            # Handle both organizational and role-based structures
            current_level = 0
            if gap_data:
                # Try organizational stats first
                org_stats = gap_data.get('organizational_stats')
                if org_stats and 'median_level' in org_stats:
                    current_level = org_stats['median_level']
                # For role-based, calculate average median across all roles
                elif 'roles' in gap_data and gap_data['roles']:
                    role_medians = []
                    for role_id, role_data in gap_data['roles'].items():
                        if isinstance(role_data, dict) and 'median_level' in role_data:
                            role_medians.append(role_data['median_level'])
                    if role_medians:
                        # Use the minimum median (most common gap case)
                        current_level = min(role_medians)

            # Check if competency has existing training (should be excluded)
            has_existing_training = competency_id in excluded_comp_ids

            # Override status if excluded due to existing training
            if has_existing_training:
                status = 'training_exists'
                grayed_out = True
                message = 'Training already exists in organization'

            # Build competency card data
            competency_card = {
                'competency_id': competency_id,
                'competency_name': competency_name,
                'status': status,
                'grayed_out': grayed_out,
                'target_level': target_level,
                'current_level': current_level,  # Add current level for UI display
                'learning_objective': learning_objective,
                'gap_data': gap_data if not grayed_out else None,
                'has_existing_training': has_existing_training  # Flag for UI
            }

            if grayed_out:
                competency_card['message'] = message

            level_data['competencies'].append(competency_card)

        pyramid['levels'][level] = level_data
        pyramid['metadata']['active_competencies_per_level'][level] = active_count

        logger.debug(
            f"[structure_pyramid_output] Level {level}: "
            f"{active_count}/{len(all_competency_ids)} active competencies"
        )

    logger.info(
        f"[structure_pyramid_output] Complete - pyramid structured with "
        f"{len(VALID_LEVELS)} levels"
    )

    return pyramid


def check_if_grayed(
    competency_id: int,
    level: int,
    target_level: int,
    needs_this_level: bool
) -> Tuple[bool, str, str]:
    """
    Determine if a competency should be grayed out at a specific level.

    Graying Logic:
    1. Level exceeds target → Gray ("Not part of selected strategies")
    2. Level within target but no gap → Gray ("Already at Level X+")
    3. Level within target and has gap → Active (show learning objective)

    Args:
        competency_id: Competency ID
        level: Current pyramid level (1, 2, 4, or 6)
        target_level: Target level from strategies
        needs_this_level: Whether gap exists at this level

    Returns:
        Tuple of (grayed_out: bool, status: str, message: str)
        - grayed_out: True if should be grayed
        - status: 'training_required' | 'achieved' | 'not_targeted'
        - message: Explanation for graying
    """

    # Case 1: Level exceeds target
    if level > target_level:
        return (
            True,
            'not_targeted',
            f'Level {level} not targeted by selected strategies (target: Level {target_level})'
        )

    # Case 2: Level within target but no gap (already achieved)
    if not needs_this_level:
        return (
            True,
            'achieved',
            f'Already at Level {level} or higher'
        )

    # Case 3: Active - training required
    return (
        False,
        'training_required',
        ''
    )


# =============================================================================
# ALGORITHM 8: Strategy Validation (Informational)
# =============================================================================

def generate_strategy_comparison(
    org_id: int,
    main_targets: Dict[int, int],
    gaps_by_competency: Dict
) -> Dict:
    """
    Generate informational strategy comparison.

    ALGORITHM 8 from Design v5 - Provides context on how selected strategies
    compare to current competency levels. This is INFORMATIONAL only, not
    blocking. Helps admin understand the scope of training needed.

    Based on: LEARNING_OBJECTIVES_DESIGN_V5_COMPREHENSIVE_PART2.md

    Args:
        org_id: Organization ID
        main_targets: Target levels from selected strategies
        gaps_by_competency: Gap detection results

    Returns:
        {
            'overall_summary': {
                'total_competencies': int,
                'competencies_with_gaps': int,
                'competencies_achieved': int,
                'gap_percentage': float
            },
            'by_competency': [
                {
                    'competency_id': int,
                    'competency_name': str,
                    'current_median': int,
                    'target_level': int,
                    'gap_size': int,
                    'status': 'gap' | 'achieved' | 'not_targeted'
                },
                ...
            ],
            'severity_breakdown': {
                'critical': int,    # Gap >= 4 levels
                'significant': int, # Gap 2-3 levels
                'minor': int,       # Gap 1 level
                'achieved': int     # No gap
            }
        }

    Example:
        >>> comparison = generate_strategy_comparison(28, main_targets, gaps)
        >>> print(f"Gap percentage: {comparison['overall_summary']['gap_percentage']:.1%}")
        Gap percentage: 65.0%
    """

    logger.info(f"[generate_strategy_comparison] Generating comparison for org {org_id}")

    all_competency_ids = get_all_competency_ids()

    comparison = {
        'overall_summary': {
            'total_competencies': len(all_competency_ids),
            'competencies_with_gaps': 0,
            'competencies_achieved': 0,
            'competencies_not_targeted': 0
        },
        'by_competency': [],
        'severity_breakdown': {
            'critical': 0,      # Gap >= 4
            'significant': 0,   # Gap 2-3
            'minor': 0,         # Gap 1
            'achieved': 0       # No gap
        }
    }

    # Process each competency
    for competency_id in all_competency_ids:
        competency = Competency.query.get(competency_id)
        competency_name = competency.competency_name if competency else f"Competency {competency_id}"

        target_level = main_targets.get(competency_id, 0)
        gap_data = gaps_by_competency.get(competency_id, {})

        # Get current level (median from organizational or role-based data)
        if 'organizational_stats' in gap_data and gap_data['organizational_stats']:
            current_median = gap_data['organizational_stats'].get('median_level', 0)
        elif 'roles' in gap_data and len(gap_data['roles']) > 0:
            # For role-based, take average of role medians
            role_medians = [
                role_data.get('median_level', 0)
                for role_data in gap_data['roles'].values()
            ]
            current_median = int(sum(role_medians) / len(role_medians)) if role_medians else 0
        else:
            current_median = 0

        # Calculate gap
        gap_size = max(0, target_level - current_median)

        # Determine status
        if target_level == 0:
            status = 'not_targeted'
            comparison['overall_summary']['competencies_not_targeted'] += 1
        elif gap_size == 0:
            status = 'achieved'
            comparison['overall_summary']['competencies_achieved'] += 1
            comparison['severity_breakdown']['achieved'] += 1
        else:
            status = 'gap'
            comparison['overall_summary']['competencies_with_gaps'] += 1

            # Categorize severity
            if gap_size >= 4:
                comparison['severity_breakdown']['critical'] += 1
            elif gap_size >= 2:
                comparison['severity_breakdown']['significant'] += 1
            else:
                comparison['severity_breakdown']['minor'] += 1

        # Add competency comparison
        comparison['by_competency'].append({
            'competency_id': competency_id,
            'competency_name': competency_name,
            'current_median': current_median,
            'target_level': target_level,
            'gap_size': gap_size,
            'status': status
        })

    # Calculate gap percentage
    targeted_competencies = (
        comparison['overall_summary']['competencies_with_gaps'] +
        comparison['overall_summary']['competencies_achieved']
    )

    if targeted_competencies > 0:
        gap_percentage = (
            comparison['overall_summary']['competencies_with_gaps'] / targeted_competencies
        )
    else:
        gap_percentage = 0.0

    comparison['overall_summary']['gap_percentage'] = round(gap_percentage * 100, 1)

    logger.info(
        f"[generate_strategy_comparison] Complete - "
        f"{comparison['overall_summary']['competencies_with_gaps']}/{targeted_competencies} "
        f"competencies have gaps ({comparison['overall_summary']['gap_percentage']}%)"
    )

    return comparison


# =============================================================================
# MASTER ORCHESTRATION FUNCTION
# =============================================================================

def generate_complete_learning_objectives(
    org_id: int,
    selected_strategies: List[Dict],
    pmt_context: Optional[Dict] = None
) -> Dict:
    """
    Master orchestration function - Generate complete learning objectives.

    This function orchestrates all 8 algorithms to produce the complete
    learning objectives output for Phase 2 Task 3.

    Algorithm Flow:
        1. Calculate combined targets (separate TTT)
        2. Validate mastery requirements
        3. Detect gaps (role-based or organizational)
        4. [Included in #3] Determine training methods
        5. Process TTT gaps
        6. Generate learning objectives (with PMT customization)
        7. Structure pyramid output
        8. Generate strategy comparison

    Args:
        org_id: Organization ID
        selected_strategies: List of selected strategy dicts
            [
                {'strategy_id': 1, 'strategy_name': 'Continuous Support'},
                {'strategy_id': 6, 'strategy_name': 'Train the Trainer'}
            ]
        pmt_context: Optional PMT context for customization
            {
                'processes': 'ISO 26262, ASPICE',
                'methods': 'Scrum, V-Model',
                'tools': 'DOORS, JIRA, Git'
            }

    Returns:
        {
            'success': True,
            'data': {
                'main_pyramid': {
                    'levels': {...},
                    'metadata': {...}
                },
                'train_the_trainer': {
                    'enabled': bool,
                    'competencies': [...]
                } or None,
                'validation': {
                    'status': 'OK' | 'INADEQUATE',
                    'severity': str,
                    'message': str,
                    'affected': [...],
                    'recommendations': [...]
                },
                'strategy_comparison': {
                    'overall_summary': {...},
                    'by_competency': [...],
                    'severity_breakdown': {...}
                }
            },
            'metadata': {
                'organization_id': int,
                'selected_strategies': [...],
                'pmt_customization': bool,
                'generation_timestamp': str
            }
        }

    Raises:
        ValueError: If invalid input or processing fails

    Example:
        >>> result = generate_complete_learning_objectives(
        ...     org_id=28,
        ...     selected_strategies=[
        ...         {'strategy_id': 1, 'strategy_name': 'Continuous Support'},
        ...         {'strategy_id': 6, 'strategy_name': 'Train the Trainer'}
        ...     ],
        ...     pmt_context={'processes': 'ISO 26262', 'tools': 'DOORS'}
        ... )
        >>> print(result['data']['validation']['status'])
        'OK'
    """

    logger.info(
        f"[generate_complete_learning_objectives] Starting for org {org_id} "
        f"with {len(selected_strategies)} strategies"
    )

    start_time = datetime.utcnow()

    try:
        # =================================================================
        # CACHING CHECK - Return cached result if inputs haven't changed
        # =================================================================
        input_hash = compute_input_hash(org_id, selected_strategies, pmt_context)
        print(f"[CACHING] Computed input hash: {input_hash[:16]}...")

        cached_result = get_cached_objectives(org_id, input_hash)
        if cached_result:
            print(f"[CACHING] Returning CACHED result for org {org_id}")
            return cached_result

        print(f"[CACHING] No valid cache, generating NEW objectives...")

        # =================================================================
        # ALGORITHM 1: Calculate Combined Targets
        # =================================================================
        logger.info("[ALGORITHM 1] Calculating combined targets...")
        targets_result = calculate_combined_targets(selected_strategies)

        main_targets = targets_result['main_targets']
        ttt_targets = targets_result['ttt_targets']
        ttt_selected = targets_result['ttt_selected']

        logger.info(f"[ALGORITHM 1] Complete - TTT selected: {ttt_selected}")

        # =================================================================
        # ALGORITHM 2: Validate Mastery Requirements
        # =================================================================
        logger.info("[ALGORITHM 2] Validating mastery requirements...")
        validation_result = validate_mastery_requirements(
            org_id,
            selected_strategies,
            main_targets
        )

        logger.info(
            f"[ALGORITHM 2] Complete - Status: {validation_result['status']}, "
            f"Severity: {validation_result['severity']}"
        )

        # =================================================================
        # ALGORITHM 3 + 4: Detect Gaps (includes Training Method determination)
        # =================================================================
        logger.info("[ALGORITHM 3+4] Detecting gaps and determining training methods...")
        gaps_data = detect_gaps(org_id, main_targets, ttt_targets)

        has_roles = gaps_data['metadata']['has_roles']
        logger.info(
            f"[ALGORITHM 3+4] Complete - Has roles: {has_roles}, "
            f"Processed {len(gaps_data['by_competency'])} competencies"
        )

        # =================================================================
        # ALGORITHM 5: Process TTT Gaps
        # =================================================================
        logger.info("[ALGORITHM 5] Processing TTT gaps...")
        ttt_data = process_ttt_gaps(org_id, ttt_targets)

        if ttt_data:
            logger.info(
                f"[ALGORITHM 5] Complete - {len(ttt_data['competencies'])} "
                f"competencies need Level 6"
            )
        else:
            logger.info("[ALGORITHM 5] Complete - No TTT training needed")

        # =================================================================
        # ALGORITHM 6: Generate Learning Objectives
        # =================================================================
        logger.info("[ALGORITHM 6] Generating learning objectives...")
        objectives = generate_learning_objectives(
            gaps_data['by_competency'],
            pmt_context
        )

        logger.info(
            f"[ALGORITHM 6] Complete - Generated objectives for "
            f"{len(objectives)} competencies"
        )

        # Generate TTT objectives if needed
        ttt_objectives = None
        if ttt_data and ttt_data['competencies']:
            logger.info("[ALGORITHM 6] Generating TTT learning objectives...")
            # For TTT, we need Level 6 objectives for all TTT competencies
            ttt_objectives = {}
            templates = load_learning_objective_templates()

            for comp_data in ttt_data['competencies']:
                comp_id = comp_data['competency_id']
                comp_name = comp_data['competency_name']

                # Get Level 6 template
                template_text = get_template_objective(templates, comp_name, 6)
                if not template_text:
                    template_text = generate_generic_objective(comp_name, 6)

                # PMT customization for TTT (optional)
                customized = False
                final_text = template_text

                if pmt_context:
                    try:
                        customized_text = customize_objective_with_pmt(
                            comp_name, 6, template_text, pmt_context
                        )
                        if customized_text:
                            final_text = customized_text
                            customized = True
                    except Exception as e:
                        logger.warning(
                            f"[ALGORITHM 6] TTT customization failed for {comp_name}: {e}"
                        )

                ttt_objectives[comp_id] = {
                    'level': 6,
                    'level_name': 'Mastering SE',
                    'objective_text': final_text,
                    'customized': customized,
                    'source': 'pmt_customized' if customized else 'template',
                    'competency_name': comp_name,
                    'gap_percentage': comp_data['gap_percentage']
                }

            logger.info(
                f"[ALGORITHM 6] TTT objectives generated for "
                f"{len(ttt_objectives)} competencies"
            )

        # =================================================================
        # ALGORITHM 7: Structure Pyramid Output
        # =================================================================
        logger.info("[ALGORITHM 7] Structuring pyramid output...")
        main_pyramid = structure_pyramid_output(
            org_id,
            gaps_data,
            objectives,
            main_targets,
            has_roles
        )

        logger.info(
            f"[ALGORITHM 7] Complete - Pyramid structured with "
            f"{len(main_pyramid['levels'])} levels"
        )

        # =================================================================
        # ALGORITHM 8: Strategy Comparison
        # =================================================================
        logger.info("[ALGORITHM 8] Generating strategy comparison...")
        strategy_comparison = generate_strategy_comparison(
            org_id,
            main_targets,
            gaps_data['by_competency']
        )

        logger.info(
            f"[ALGORITHM 8] Complete - Gap percentage: "
            f"{strategy_comparison['overall_summary']['gap_percentage']}%"
        )

        # =================================================================
        # BUILD FINAL RESPONSE
        # =================================================================
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Determine pathway based on roles
        if has_roles:
            if ttt_selected:
                pathway = 'ROLE_BASED_DUAL_TRACK'
                pathway_reason = 'High maturity organization with roles defined. Train the Trainer strategy included.'
            else:
                pathway = 'ROLE_BASED'
                pathway_reason = 'High maturity organization with roles defined. Using role-based gap detection.'
        else:
            if ttt_selected:
                pathway = 'TASK_BASED_DUAL_TRACK'
                pathway_reason = 'Low maturity organization without formal roles. Train the Trainer strategy included.'
            else:
                pathway = 'TASK_BASED'
                pathway_reason = 'Low maturity organization without formal roles. Using organizational median for gap detection.'

        result = {
            'success': True,
            'pathway': pathway,
            'pathway_reason': pathway_reason,
            'data': {
                'main_pyramid': main_pyramid,
                'train_the_trainer': ttt_objectives,
                'validation': validation_result,
                'strategy_comparison': strategy_comparison
            },
            'metadata': {
                'organization_id': org_id,
                'pathway': pathway,
                'pathway_reason': pathway_reason,
                'selected_strategies': selected_strategies,
                'pmt_customization': pmt_context is not None,
                'has_roles': has_roles,
                'ttt_selected': ttt_selected,
                'generation_timestamp': end_time.isoformat(),
                'processing_time_seconds': round(processing_time, 2)
            }
        }

        logger.info(
            f"[generate_complete_learning_objectives] SUCCESS - "
            f"Completed in {processing_time:.2f} seconds"
        )

        # =================================================================
        # SAVE TO CACHE - Store result for future requests
        # =================================================================
        # Get validation status and gap percentage for quick access fields
        validation_status = strategy_comparison.get('overall_summary', {}).get('gap_percentage')
        gap_percentage = strategy_comparison.get('overall_summary', {}).get('gap_percentage')

        save_to_cache(
            org_id=org_id,
            input_hash=input_hash,
            pathway=pathway,
            objectives_data=result,
            validation_status=validation_result.get('status'),
            gap_percentage=gap_percentage
        )
        logger.info(f"[CACHING] Saved result to cache for org {org_id}")

        return result

    except Exception as e:
        logger.error(
            f"[generate_complete_learning_objectives] FAILED: {e}",
            exc_info=True
        )
        raise
