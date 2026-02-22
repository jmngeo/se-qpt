# Role-Aware Training Program Implementation Plan

**Created:** 2026-01-18
**Status:** Ready for Implementation
**Context:** Meeting with Ulf on 13.01.2026 - Phase 3 changes

---

## Executive Summary

This document outlines the implementation plan for role-aware training program assignment in SE-QPT. The changes ensure that:
1. Roles are only assigned training for competencies they actually need
2. Training programs (Engineers, Managers, Interfacing Partners) are assigned based on actual competency gaps
3. Low maturity organizations (no roles) continue to work as before

---

## 1. Current State Analysis

### Gap Calculation (Current)
- **Target Source:** Strategy template (same for ALL roles)
- **Formula:** `gap = strategy_target - current_level`
- **Issue:** Roles may show gaps for competencies they don't need

### Training Program Clusters (Current - 6 groups)
1. Engineers
2. Managers
3. Executives
4. Support Staff
5. External Partners
6. Operations

### Assignment Method (Current)
- Hardcoded mapping from SE role cluster to training program cluster
- Happens at Phase 1 Task 2 (before gaps are known)

---

## 2. Target State

### Gap Calculation (Role-Aware)
- **Target Source:** MIN(strategy_target, role_requirement) per role
- **Formula:** `effective_target = min(strategy_target, role_requirement)`
- **Benefit:** Roles only show gaps for competencies they actually need

### Training Program Clusters (New - 3 groups)
1. **Engineers** - Roles needing Level 4+ in Technical/Core competencies
2. **Managers** - Roles needing Level 4+ ONLY in Social/Management competencies
3. **Interfacing Partners** - Roles needing only Level 1-2 across all competencies

### Assignment Method (New)
- Calculated from actual competency gaps
- Happens during Learning Objectives generation (Phase 2 Task 2)

---

## 3. Competency Groups (From Database)

| Group | Competencies (IDs) |
|-------|-------------------|
| **Core** (4) | 1-Systems Thinking, 4-Lifecycle Consideration, 5-Customer/Value Orientation, 6-Systems Modelling |
| **Technical** (5) | 14-Requirements Definition, 15-System Architecting, 16-Integration/V&V, 17-Operation & Support, 18-Agile Methods |
| **Social/Personal** (3) | 7-Communication, 8-Leadership, 9-Self-Organization |
| **Management** (4) | 10-Project Management, 11-Decision Management, 12-Information Management, 13-Configuration Management |

---

## 4. Implementation Changes

### 4.1 File: `src/backend/app/services/learning_objectives_core.py`

#### Function: `process_competency_with_roles()` (Lines ~871-994)

**Current:**
```python
def process_competency_with_roles(org_id, competency_id, target_level):
    # target_level is STRATEGY target (same for all roles)
    for role in roles:
        for level in VALID_LEVELS:
            if level > target_level:
                continue
            users_needing_level = [
                score for score in user_scores
                if score < level <= target_level
            ]
```

**Change to:**
```python
def process_competency_with_roles(org_id, competency_id, strategy_target):
    competency = Competency.query.get(competency_id)

    competency_data = {
        'competency_id': competency_id,
        'competency_name': competency.competency_name,
        'competency_area': competency.competency_area,  # NEW: For training program assignment
        'strategy_target': strategy_target,
        'has_gap': False,
        'levels_needed': [],
        'roles': {}
    }

    if strategy_target == 0:
        return competency_data

    for role in roles:
        # NEW: Get role-specific requirement
        role_requirement = get_role_competency_requirement(role.id, competency_id)

        # NEW: Skip roles that don't need this competency
        if role_requirement == 0:
            continue

        # NEW: Calculate effective target
        effective_target = min(strategy_target, role_requirement)

        if effective_target == 0:
            continue

        user_ids = get_users_in_role(role.id)
        if not user_ids:
            continue

        user_scores = get_user_scores_for_competency(user_ids, competency_id)
        if not user_scores:
            continue

        # Statistics for display
        median_level = calculate_median(user_scores)
        mean_level = calculate_mean(user_scores)
        variance = calculate_variance(user_scores)

        role_levels_needed = []
        level_details = {}

        for level in VALID_LEVELS:
            if level > effective_target:  # USE EFFECTIVE TARGET
                continue

            users_needing_level = [
                score for score in user_scores
                if score < level <= effective_target  # USE EFFECTIVE TARGET
            ]

            if len(users_needing_level) > 0:
                competency_data['has_gap'] = True
                if level not in competency_data['levels_needed']:
                    competency_data['levels_needed'].append(level)
                role_levels_needed.append(level)
                level_details[level] = {
                    'users_needing': len(users_needing_level),
                    'total_users': len(user_scores),
                    'percentage': round(len(users_needing_level) / len(user_scores) * 100, 1)
                }

        if role_levels_needed:
            users_below_target = [s for s in user_scores if s < effective_target]
            gap_percentage = len(users_below_target) / len(user_scores)
            training_rec = determine_training_method(gap_percentage, variance, len(user_scores))

            competency_data['roles'][role.id] = {
                'role_id': role.id,
                'role_name': role.role_name,
                'role_requirement': role_requirement,  # NEW
                'effective_target': effective_target,  # NEW
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

    competency_data['levels_needed'] = sorted(competency_data['levels_needed'])
    return competency_data
```

#### NEW Function: `calculate_training_program_assignments()`

```python
def calculate_training_program_assignments(
    org_id: int,
    gaps_by_competency: Dict
) -> Dict[int, str]:
    """
    Assign each role to a training program based on their competency gaps.

    Training Programs:
    - Engineers: Level 4+ gap in Technical OR Core competencies
    - Managers: Level 4+ gap ONLY in Social/Personal OR Management (no L4+ in Tech/Core)
    - Interfacing Partners: Only Level 1-2 gaps across all competencies

    Returns:
        Dict[role_id -> program_name]: "Engineers" | "Managers" | "Interfacing Partners" | None
    """
    TECHNICAL_CORE_AREAS = ['Core', 'Technical']
    SOCIAL_MGMT_AREAS = ['Social / Personal', 'Management']

    role_gap_summary = {}

    for comp_id, comp_data in gaps_by_competency.items():
        comp_area = comp_data.get('competency_area', '')
        roles_data = comp_data.get('roles', {})

        for role_id, role_info in roles_data.items():
            role_id_int = int(role_id) if isinstance(role_id, str) else role_id

            if role_id_int not in role_gap_summary:
                role_gap_summary[role_id_int] = {
                    'role_name': role_info.get('role_name'),
                    'has_tech_core_l4': False,
                    'has_social_mgmt_l4': False,
                    'max_level': 0,
                    'has_any_gap': False
                }

            levels_needed = role_info.get('levels_needed', [])
            if not levels_needed:
                continue

            role_gap_summary[role_id_int]['has_any_gap'] = True
            role_gap_summary[role_id_int]['max_level'] = max(
                role_gap_summary[role_id_int]['max_level'],
                max(levels_needed)
            )

            has_level_4_plus = any(level >= 4 for level in levels_needed)

            if has_level_4_plus:
                if comp_area in TECHNICAL_CORE_AREAS:
                    role_gap_summary[role_id_int]['has_tech_core_l4'] = True
                elif comp_area in SOCIAL_MGMT_AREAS:
                    role_gap_summary[role_id_int]['has_social_mgmt_l4'] = True

    assignments = {}

    for role_id, summary in role_gap_summary.items():
        if not summary['has_any_gap']:
            assignments[role_id] = None
            continue

        if summary['has_tech_core_l4']:
            assignments[role_id] = 'Engineers'
        elif summary['has_social_mgmt_l4'] and not summary['has_tech_core_l4']:
            assignments[role_id] = 'Managers'
        elif summary['max_level'] <= 2:
            assignments[role_id] = 'Interfacing Partners'
        else:
            assignments[role_id] = 'Interfacing Partners'

    return assignments


def save_training_program_assignments(org_id: int, assignments: Dict[int, str]) -> None:
    """Save training program assignments to organization_roles table."""
    from app.models import OrganizationRoles, TrainingProgramCluster

    PROGRAM_TO_CLUSTER_ID = {
        'Engineers': 1,
        'Managers': 2,
        'Interfacing Partners': 3
    }

    for role_id, program in assignments.items():
        if program:
            cluster_id = PROGRAM_TO_CLUSTER_ID.get(program)
            if cluster_id:
                role = OrganizationRoles.query.get(role_id)
                if role:
                    role.training_program_cluster_id = cluster_id

    db.session.commit()
    logger.info(f"[save_training_program_assignments] Saved {len(assignments)} assignments for org {org_id}")
```

#### Function: `generate_complete_learning_objectives()` (Add after Algorithm 3)

```python
# After detect_gaps() call (~line 2850):
gaps_by_competency = detect_gaps(org_id, main_targets, ttt_targets)

# NEW: Calculate and save training program assignments (only for high maturity)
if has_roles:
    training_assignments = calculate_training_program_assignments(
        org_id,
        gaps_by_competency['by_competency']
    )
    save_training_program_assignments(org_id, training_assignments)
    logger.info(f"[generate_complete_learning_objectives] Training program assignments: {training_assignments}")
```

### 4.2 Database Migration: Consolidate Training Program Clusters

**File:** `src/backend/setup/migrations/014_consolidate_training_clusters.sql`

```sql
-- Migration: Consolidate 6 training program clusters to 3
-- Date: 2026-01-18
-- Reason: Ulf's requirement from 13.01.2026 meeting

-- Step 1: Update cluster names and consolidate
-- Map: Executives -> Managers, Support Staff/External Partners/Operations -> Interfacing Partners

BEGIN;

-- First, update organization_roles to map old clusters to new
UPDATE organization_roles
SET training_program_cluster_id = 2  -- Managers
WHERE training_program_cluster_id = 3;  -- Executives

UPDATE organization_roles
SET training_program_cluster_id = 3  -- Interfacing Partners (will be new ID)
WHERE training_program_cluster_id IN (4, 5, 6);  -- Support Staff, External Partners, Operations

-- Update the cluster table itself
UPDATE training_program_cluster
SET cluster_name = 'Engineers',
    cluster_key = 'engineers',
    training_program_name = 'SE for Engineers',
    description = 'Roles requiring Level 4+ competency in Technical or Core areas'
WHERE id = 1;

UPDATE training_program_cluster
SET cluster_name = 'Managers',
    cluster_key = 'managers',
    training_program_name = 'SE for Managers',
    description = 'Roles requiring Level 4+ competency only in Social/Personal or Management areas'
WHERE id = 2;

UPDATE training_program_cluster
SET cluster_name = 'Interfacing Partners',
    cluster_key = 'interfacing_partners',
    training_program_name = 'SE for Interfacing Partners',
    description = 'Roles requiring only Level 1-2 competency (basic awareness)'
WHERE id = 3;

-- Delete old clusters (4, 5, 6) - they've been mapped to cluster 3
DELETE FROM training_program_cluster WHERE id > 3;

COMMIT;
```

---

## 5. Low Maturity Organizations (No Changes)

For organizations without defined roles:
- `check_if_org_has_roles()` returns `False`
- `process_competency_organizational()` is used (unchanged)
- Strategy targets are the only targets available
- No training program assignment (no roles to assign)
- Phase 3 shows only "Competency Level" view

**This is correct behavior - no changes needed.**

---

## 6. Edge Cases

| Case | Behavior |
|------|----------|
| Role requirement = 0 | Skip role for this competency (no gap generated) |
| Role requirement > Strategy target | Use strategy target (org's chosen limit) |
| Strategy target = 0 | Skip competency entirely (org not training this) |
| All users meet effective_target | No gap for this role |
| No gaps for a role | Role excluded from training programs (assignment = None) |
| Low maturity org | Use strategy targets only, no training program assignment |

---

## 7. Training Program Assignment Logic

```
FOR each role in organization:
  Collect all gaps by competency area

  IF role has Level 4+ gap in Technical OR Core competencies:
    → Assign to "Engineers"

  ELSE IF role has Level 4+ gap ONLY in Social/Personal OR Management:
    → Assign to "Managers"

  ELSE IF role has ONLY Level 1-2 gaps (max_level <= 2):
    → Assign to "Interfacing Partners"

  ELSE IF role has NO gaps:
    → No assignment (excluded from training)
```

---

## 8. Files to Modify

| File | Changes |
|------|---------|
| `src/backend/app/services/learning_objectives_core.py` | Modify `process_competency_with_roles()`, add assignment functions |
| `src/backend/setup/migrations/014_consolidate_training_clusters.sql` | NEW: Migration to consolidate clusters |
| `src/backend/app/models.py` | No changes needed |
| `src/backend/app/routes/phase2_learning.py` | No changes needed |
| `src/backend/app/services/phase3_planning_service.py` | No changes needed (benefits automatically) |

---

## 9. Testing Checklist

- [ ] Low maturity org: Verify behavior unchanged
- [ ] High maturity org with roles: Verify gaps only for roles needing competency
- [ ] Role with requirement=0: Verify excluded from gap
- [ ] Role with requirement > strategy: Verify uses strategy target
- [ ] Training program assignment: Verify Engineers/Managers/Interfacing split
- [ ] Phase 3 modules: Verify correct roles_needing_training
- [ ] All users meet target: Verify no gap shown
- [ ] Migration: Verify cluster consolidation works

---

## 10. Rollback Plan

If issues arise:
1. Revert `learning_objectives_core.py` to previous version
2. Run reverse migration to restore 6 clusters
3. Clear `generated_learning_objectives` cache for affected orgs

---

## 11. Implementation Order

1. Create and run migration `014_consolidate_training_clusters.sql`
2. Modify `process_competency_with_roles()` function
3. Add `calculate_training_program_assignments()` function
4. Add `save_training_program_assignments()` function
5. Update `generate_complete_learning_objectives()` to call assignment
6. Test with sample data
7. Deploy

---

## Appendix: Competency Area Reference

From `src/backend/setup/populate/populate_competencies.py`:

```python
COMPETENCY_DATA = [
    # Core Competencies (area: "Core")
    {"id": 1, "name": "Systems Thinking", "area": "Core"},
    {"id": 4, "name": "Lifecycle Consideration", "area": "Core"},
    {"id": 5, "name": "Customer / Value Orientation", "area": "Core"},
    {"id": 6, "name": "Systems Modelling and Analysis", "area": "Core"},

    # Social / Personal Competencies (area: "Social / Personal")
    {"id": 7, "name": "Communication", "area": "Social / Personal"},
    {"id": 8, "name": "Leadership", "area": "Social / Personal"},
    {"id": 9, "name": "Self-Organization", "area": "Social / Personal"},

    # Management Competencies (area: "Management")
    {"id": 10, "name": "Project Management", "area": "Management"},
    {"id": 11, "name": "Decision Management", "area": "Management"},
    {"id": 12, "name": "Information Management", "area": "Management"},
    {"id": 13, "name": "Configuration Management", "area": "Management"},

    # Technical Competencies (area: "Technical")
    {"id": 14, "name": "Requirements Definition", "area": "Technical"},
    {"id": 15, "name": "System Architecting", "area": "Technical"},
    {"id": 16, "name": "Integration, Verification, Validation", "area": "Technical"},
    {"id": 17, "name": "Operation and Support", "area": "Technical"},
    {"id": 18, "name": "Agile Methods", "area": "Technical"},
]
```
