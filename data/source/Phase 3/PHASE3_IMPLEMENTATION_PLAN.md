# Phase 3: Macro Planning - Implementation Plan

## Document Information
- **Purpose**: Implementation planning and data requirements for Phase 3
- **Based on**: Phase3_Macro_Planning_Specification_v3.2.md, Meeting Notes 11.12.2025
- **Created**: January 2026
- **Status**: Ready for Implementation

---

## Table of Contents

1. [Data Requirements Summary](#1-data-requirements-summary)
2. [Existing Data Inventory](#2-existing-data-inventory)
3. [New Data to Create](#3-new-data-to-create)
4. [Training Program Cluster Mapping Strategy](#4-training-program-cluster-mapping-strategy)
5. [Implementation Phases](#5-implementation-phases)
6. [Database Migration Plan](#6-database-migration-plan)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Data Requirements Summary

### Status Overview

| Category | Data Element | Status | Location/Action |
|----------|--------------|--------|-----------------|
| **EXISTING** | 16 SE Competencies | EXISTS | `competency` table |
| **EXISTING** | 7 Qualification Strategies | EXISTS | `strategy_template` table |
| **EXISTING** | 14 SE Role Clusters | EXISTS | `role_cluster` table |
| **EXISTING** | Organization Maturity Level | EXISTS | `organization.maturity_score` |
| **EXISTING** | Target Group Size | EXISTS | `phase_questionnaire_responses` |
| **EXISTING** | Selected Strategy | EXISTS | `learning_strategy` table |
| **EXISTING** | Learning Objectives/Gaps | EXISTS | `generated_learning_objectives` |
| **EXISTING** | Org Roles to SE Cluster Mapping | EXISTS | `organization_role_mappings` |
| **EXISTING** | Existing Trainings Exclusion | EXISTS | `organization_existing_trainings` |
| **EXISTING** | PMT Context | EXISTS | `organization_pmt_context` |
| **NEEDS CREATION** | 10 Learning Formats | MISSING | New `learning_format` table |
| **NEEDS CREATION** | 6 Training Program Clusters | MISSING | New `training_program_cluster` table |
| **NEEDS CREATION** | Competency-LF Matrix | MISSING | New `competency_learning_format_matrix` table |
| **NEEDS CREATION** | Strategy-LF Matrix | MISSING | New `strategy_learning_format_matrix` table |
| **NEEDS CREATION** | Org Role to Training Cluster Mapping | MISSING | Extend `organization_role_mappings` + LLM prompt |

---

## 2. Existing Data Inventory

### 2.1 Organization Context (from Phase 1)

```sql
-- Organization basic info
organization.id
organization.organization_name
organization.maturity_score        -- Determines low vs high maturity
organization.selected_archetype    -- Strategy name

-- Target Group Size (from Phase 1 questionnaire)
-- Stored in phase_questionnaire_responses WHERE questionnaire_type = 'target_group'
-- JSON structure: {"id": "large", "range": "100-500", "value": 300, ...}
```

**Phase 3 Usage:**
- `maturity_score < 3` → Low Maturity → Only Competency-Level view available
- `maturity_score >= 3` AND has roles → Both views available
- `value` from target_group → Used for participant count scaling

### 2.2 16 SE Competencies

| ID | competency_name | competency_area | Spec Key |
|----|-----------------|-----------------|----------|
| 1 | Systems Thinking | Core | `systems_thinking` |
| 4 | Lifecycle Consideration | Core | `lifecycle_consideration` |
| 5 | Customer / Value Orientation | Core | `customer_value_orientation` |
| 6 | Systems Modelling and Analysis | Core | `systems_modelling_and_analysis` |
| 7 | Communication | Social / Personal | `communication` |
| 8 | Leadership | Social / Personal | `leadership` |
| 9 | Self-Organization | Social / Personal | `self_organization` |
| 10 | Project Management | Management | `project_management` |
| 11 | Decision Management | Management | `decision_management` |
| 12 | Information Management | Management | `information_management` |
| 13 | Configuration Management | Management | `configuration_management` |
| 14 | Requirements Definition | Technical | `requirements_definition` |
| 15 | System Architecting | Technical | `system_architecting` |
| 16 | Integration, Verification, Validation | Technical | `integration_verification_validation` |
| 17 | Operation and Support | Technical | `operation_and_support` |
| 18 | Agile Methods | Technical | `agile_methods` |

**Note:** IDs match spec v3.2 Section 7.2 exactly.

### 2.3 7 Qualification Strategies

| ID | strategy_name | Spec Key |
|----|---------------|----------|
| 1 | Common basic understanding | `common_basic_understanding` |
| 2 | SE for managers | `se_for_managers` |
| 3 | Orientation in pilot project | `orientation_in_pilot_project` |
| 4 | Needs-based, project-oriented training | `needs_based_project_oriented` |
| 5 | Continuous support | `continuous_support` |
| 6 | Train the trainer | `train_the_trainer` |
| 7 | Certification | `certification` |

**Note:** IDs match spec v3.2 Section 7.1 exactly.

### 2.4 14 SE Role Clusters (for Competency Mapping)

| ID | role_cluster_name |
|----|-------------------|
| 1 | Customer |
| 2 | Customer Representative |
| 3 | Project Manager |
| 4 | System Engineer |
| 5 | Specialist Developer |
| 6 | Production Planner/Coordinator |
| 7 | Production Employee |
| 8 | Quality Engineer/Manager |
| 9 | Verification and Validation (V&V) Operator |
| 10 | Service Technician |
| 11 | Process and Policy Manager |
| 12 | Innovation Management |
| 13 | Internal Support |
| 14 | Management |

**IMPORTANT:** These 14 SE Role Clusters are for competency profile mapping.
They are **NOT** the 6 Training Program Clusters used in Phase 3 for training organization.

### 2.5 Learning Objectives Data Structure (from Phase 2)

```json
{
  "metadata": {
    "pathway": "ROLE_BASED_DUAL_TRACK",
    "has_roles": true,
    "selected_strategies": [
      {"strategy_id": 6, "strategy_name": "Train the SE-Trainer"},
      {"strategy_id": 1, "strategy_name": "Common Basic Understanding"}
    ],
    "pmt_customization": true
  },
  "data": {
    "main_pyramid": {
      "levels": {
        "1": { "level_name": "Performing Basics", "competencies": [...] },
        "2": { "level_name": "Understanding", "competencies": [...] },
        "4": { "level_name": "Applying", "competencies": [...] }
      }
    },
    "train_the_trainer": { ... },
    "strategy_comparison": { ... },
    "validation": { "status": "OK", ... }
  }
}
```

**Key data per competency:**
```json
{
  "competency_id": 14,
  "competency_name": "Requirements Definition",
  "target_level": 4,
  "current_level": 2,
  "status": "gap",
  "gap_data": {
    "has_gap": true,
    "roles_needing_training": ["System Engineer", "Requirement Engineer"]
  },
  "learning_objective": {
    "level": 4,
    "objective_text": "...",
    "has_pmt_breakdown": true
  }
}
```

**Phase 3 Usage:**
- `status: "gap"` → Training module required
- `roles_needing_training` → For Role-Clustered view grouping
- `has_pmt_breakdown` → Creates separate Method/Tool modules
- Gap count → Participant estimation (needs scaling)

---

## 3. New Data to Create

### 3.1 Learning Formats Table (10 Formats)

**Table: `learning_format`**

| format_key | format_name | max_level | participant_min | participant_max | is_e_learning |
|------------|-------------|-----------|-----------------|-----------------|---------------|
| seminar | Seminar / Instructor Lead Training | 4 | 10 | 100 | false |
| webinar | Webinar / Live Online Event | 2 | 1 | NULL | false |
| coaching | Coaching | 6 | 1 | 5 | false |
| mentoring | Mentoring | 6 | 1 | 3 | false |
| wbt | Web-Based Training (WBT) | 2 | 1 | NULL | true |
| cbt | Computer-Based Training (CBT) | 2 | 1 | NULL | true |
| game_based | Game-Based Learning | 4 | 5 | 20 | false |
| conference | Conference | 1 | 50 | NULL | false |
| blended | Blended Learning | 6 | 5 | 50 | false |
| self_learning | Self-Learning | 2 | 1 | 1 | true |

**Note:** NULL participant_max = unlimited

### 3.2 Training Program Clusters Table (6 Clusters)

**Table: `training_program_cluster`**

| id | cluster_key | cluster_name | training_program_name | description |
|----|-------------|--------------|----------------------|-------------|
| 1 | engineers | Engineers | SE for Engineers | Technical practitioners who design, develop, and implement systems |
| 2 | managers | Managers | SE for Managers | Leadership roles responsible for planning, coordination, and decision-making |
| 3 | executives | Executives | SE for Executives | Senior leadership with strategic oversight |
| 4 | support_staff | Support Staff | SE for Support Staff | Roles providing technical and operational support |
| 5 | external_partners | External Partners | SE for Partners | Customer-facing and supplier-facing roles |
| 6 | operations | Operations | SE for Operations | Roles focused on production, deployment, and maintenance |

### 3.3 Strategy-Learning Format Matrix

**Table: `strategy_learning_format_matrix`**

Values: `++` = Highly Recommended, `+` = Partly Recommended, `--` = Not Consistent

| Strategy ID | seminar | webinar | coaching | mentoring | wbt | cbt | game_based | conference | blended | self_learning |
|-------------|---------|---------|----------|-----------|-----|-----|------------|------------|---------|---------------|
| 1 (Common basic) | ++ | + | -- | -- | -- | -- | + | + | ++ | -- |
| 2 (SE for managers) | ++ | + | ++ | ++ | + | -- | + | + | ++ | -- |
| 3 (Orientation pilot) | ++ | + | ++ | ++ | -- | -- | ++ | -- | ++ | -- |
| 4 (Needs-based) | ++ | + | + | + | + | + | + | -- | ++ | + |
| 5 (Continuous support) | + | ++ | + | + | ++ | ++ | + | ++ | + | ++ |
| 6 (Train trainer) | + | + | ++ | ++ | + | + | + | -- | + | + |
| 7 (Certification) | + | + | + | + | + | + | -- | + | + | + |

### 3.4 Competency-Level Achievement Matrix

**Table: `competency_learning_format_matrix`**

Values: Maximum achievable level (0, 1, 2, 4, or 6)

| Competency ID | seminar | webinar | coaching | mentoring | wbt | cbt | game_based | conference | blended | self_learning |
|---------------|---------|---------|----------|-----------|-----|-----|------------|------------|---------|---------------|
| 1 (Systems Thinking) | 2 | 2 | 4 | 4 | 2 | 1 | 2 | 1 | 4 | 1 |
| 4 (Lifecycle) | 2 | 2 | 4 | 4 | 2 | 1 | 2 | 1 | 4 | 1 |
| 5 (Customer/Value) | 2 | 2 | 4 | 6 | 2 | 1 | 2 | 1 | 4 | 1 |
| 6 (Systems Modelling) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 1 | 6 | 2 |
| 7 (Communication) | 4 | 2 | 6 | 4 | 2 | 1 | 4 | 2 | 4 | 1 |
| 8 (Leadership) | 2 | 2 | 6 | 6 | 2 | 1 | 4 | 2 | 6 | 2 |
| 9 (Self-Organization) | 2 | 1 | 4 | 4 | 1 | 1 | 2 | 1 | 4 | 2 |
| 10 (Project Mgmt) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 2 | 6 | 2 |
| 11 (Decision Mgmt) | 4 | 2 | 6 | 6 | 2 | 2 | 4 | 2 | 6 | 2 |
| 12 (Info Mgmt) | 4 | 2 | 4 | 4 | 2 | 2 | 2 | 1 | 4 | 2 |
| 13 (Config Mgmt) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 2 | 6 | 2 |
| 14 (Requirements Def) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 2 | 6 | 2 |
| 15 (System Architecting) | 4 | 2 | 4 | 6 | 2 | 2 | 4 | 2 | 6 | 2 |
| 16 (IVV) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 2 | 6 | 2 |
| 17 (Operation/Support) | 4 | 2 | 4 | 4 | 2 | 2 | 2 | 2 | 4 | 2 |
| 18 (Agile Methods) | 4 | 2 | 4 | 4 | 2 | 2 | 4 | 2 | 6 | 2 |

**Note:** Core competencies (1, 4, 5, 6) have lower achievable levels - these are experience-based.

---

## 4. Training Program Cluster Mapping Strategy

### 4.1 The Challenge

For the **Role-Clustered Based View** in Phase 3, we need to group organization roles into Training Program Clusters (e.g., "SE for Engineers", "SE for Managers").

This requires mapping each organization role to one of the 6 Training Program Clusters:
1. Engineers
2. Managers
3. Executives
4. Support Staff
5. External Partners
6. Operations

### 4.2 Recommended Approach: Integrate with Phase 1 Task 2 Role Mapping

**RECOMMENDATION:** Add Training Program Cluster mapping to the existing Phase 1 Task 2 LLM-based role mapping process.

**Why this is the best approach:**

| Advantage | Explanation |
|-----------|-------------|
| **Efficiency** | One LLM call instead of two separate calls |
| **Context availability** | LLM already has full role context (title, description, responsibilities, skills) |
| **Logical grouping** | Both mappings are role classification tasks |
| **Avoid redundancy** | No need to re-process role data later |
| **User experience** | Single confirmation step for both mappings |
| **Data consistency** | Both mappings stored together, updated together |

### 4.3 Implementation Details

#### Current Phase 1 Task 2 LLM Prompt (Role Mapping)

The current prompt maps organization roles to the 14 SE Role Clusters.

#### Enhanced LLM Prompt (Add Training Program Cluster)

```python
ENHANCED_ROLE_MAPPING_PROMPT = """
You are an expert in Systems Engineering organizational structures.

## Task
For each organization role provided, determine:
1. The best matching SE Role Cluster (for competency profile)
2. The best matching Training Program Cluster (for training organization)

## 14 SE Role Clusters (for competency mapping):
1. Customer - External customers/end users
2. Customer Representative - Internal customer advocates
3. Project Manager - Project planning and execution
4. System Engineer - Core SE practitioners
5. Specialist Developer - Domain-specific developers
6. Production Planner/Coordinator - Production planning
7. Production Employee - Production execution
8. Quality Engineer/Manager - Quality assurance
9. V&V Operator - Verification and validation
10. Service Technician - Field service and support
11. Process and Policy Manager - Process governance
12. Innovation Management - Innovation and R&D
13. Internal Support - Internal services
14. Management - General management

## 6 Training Program Clusters (for training organization):
1. Engineers - Technical practitioners (design, develop, implement systems)
2. Managers - Leadership roles (planning, coordination, decisions)
3. Executives - Senior leadership (strategic oversight)
4. Support Staff - Technical/operational support (QA, config mgmt, IT)
5. External Partners - Customer/supplier facing (sales, account mgmt)
6. Operations - Production, deployment, maintenance roles

## Organization Role to Analyze:
Title: {role_title}
Description: {role_description}
Responsibilities: {role_responsibilities}
Skills: {role_skills}

## Response Format (JSON):
{
  "se_role_cluster": {
    "cluster_id": <1-14>,
    "cluster_name": "<name>",
    "confidence": <0-100>,
    "reasoning": "<brief explanation>"
  },
  "training_program_cluster": {
    "cluster_id": <1-6>,
    "cluster_name": "<name>",
    "reasoning": "<brief explanation>"
  }
}
"""
```

#### Database Schema Extension

```sql
-- Add training_program_cluster_id to organization_role_mappings
ALTER TABLE organization_role_mappings
ADD COLUMN training_program_cluster_id INTEGER REFERENCES training_program_cluster(id);

-- Add index for Phase 3 queries
CREATE INDEX idx_org_role_training_cluster
ON organization_role_mappings(organization_id, training_program_cluster_id);
```

### 4.4 Mapping Logic (LLM Guidelines)

| Organization Role Type | SE Role Cluster | Training Program Cluster |
|------------------------|-----------------|--------------------------|
| Software Engineer, System Engineer, Test Engineer | System Engineer (4) | Engineers (1) |
| Requirements Engineer, Architect | System Engineer (4) | Engineers (1) |
| Project Manager, Team Lead | Project Manager (3) | Managers (2) |
| Department Head, Director | Management (14) | Managers (2) |
| VP, C-Level, Senior Director | Management (14) | Executives (3) |
| QA Engineer, Config Manager | Quality Engineer (8) | Support Staff (4) |
| IT Support, Documentation | Internal Support (13) | Support Staff (4) |
| Account Manager, Sales Engineer | Customer Representative (2) | External Partners (5) |
| Supplier Manager | Customer Representative (2) | External Partners (5) |
| Production Engineer, Field Engineer | Service Technician (10) | Operations (6) |
| Production Worker | Production Employee (7) | Operations (6) |

### 4.5 Files to Modify

1. **Backend Service**: `src/backend/app/services/role_mapping_service.py` (or similar)
   - Update LLM prompt to include Training Program Cluster mapping
   - Parse and store both cluster assignments

2. **Database Migration**: New migration file
   - Create `training_program_cluster` table
   - Add `training_program_cluster_id` column to `organization_role_mappings`

3. **Frontend (if applicable)**: Role mapping confirmation UI
   - Show both cluster assignments for user review/confirmation

---

## 5. Implementation Phases

### Phase 5.1: Database Schema Setup (Week 1)

**Tasks:**
1. Create migration: `014_phase3_learning_formats.sql`
   - `learning_format` table with 10 formats
   - `training_program_cluster` table with 6 clusters
   - `strategy_learning_format_matrix` table
   - `competency_learning_format_matrix` table
   - Extend `organization_role_mappings` with `training_program_cluster_id`

2. Seed reference data
   - 10 learning formats with all properties
   - 6 training program clusters
   - 70 strategy-LF matrix entries (7 strategies x 10 formats)
   - 160 competency-LF matrix entries (16 competencies x 10 formats)

### Phase 5.2: Phase 1 Task 2 Enhancement (Week 1-2)

**Tasks:**
1. Update LLM prompt for role mapping to include Training Program Cluster
2. Update role mapping service to parse and store both mappings
3. Update frontend confirmation UI (if needed)
4. Test with existing organizations

### Phase 5.3: Phase 3 Backend API (Week 2-3)

**Tasks:**
1. Create Phase 3 routes/blueprints
2. Implement Task 1: Training Structure Selection
3. Implement Task 2: Format Selection with 3-Factor Suitability
4. Implement Task 3: LLM Timeline Generation
5. Implement participant count scaling logic

### Phase 5.4: Phase 3 Frontend (Week 3-4)

**Tasks:**
1. Create Phase 3 dashboard with 3 tasks
2. Task 1: View selection UI (Competency-Level vs Role-Clustered)
3. Task 2: Module list with format dropdown and suitability feedback
4. Task 3: Timeline display (read-only)
5. Export to Excel functionality

### Phase 5.5: Integration and Testing (Week 4)

**Tasks:**
1. End-to-end testing with test organizations
2. Verify data flow from Phase 1 → Phase 2 → Phase 3
3. Test participant scaling calculations
4. Test LLM timeline generation
5. Test Excel export

---

## 6. Database Migration Plan

### Migration: `014_phase3_learning_formats.sql`

```sql
-- ============================================================================
-- Phase 3: Macro Planning - Database Schema
-- Migration: 014_phase3_learning_formats.sql
-- Based on: Phase3_Macro_Planning_Specification_v3.2.md
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1. Learning Formats Table (10 formats)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_format (
    id SERIAL PRIMARY KEY,
    format_key VARCHAR(50) UNIQUE NOT NULL,
    format_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50) NOT NULL,
    description TEXT,
    mode_of_delivery VARCHAR(20) CHECK (mode_of_delivery IN ('online', 'offline', 'hybrid')),
    communication_type VARCHAR(20) CHECK (communication_type IN ('synchronous', 'asynchronous', 'hybrid')),
    collaboration_type VARCHAR(20) CHECK (collaboration_type IN ('group', 'individual')),
    participant_min INTEGER DEFAULT 1,
    participant_max INTEGER,  -- NULL = unlimited
    max_level_achievable INTEGER CHECK (max_level_achievable IN (1, 2, 4, 6)),
    is_e_learning BOOLEAN DEFAULT FALSE,
    is_passive BOOLEAN DEFAULT FALSE,
    effort_content_creation INTEGER CHECK (effort_content_creation BETWEEN 1 AND 5),
    effort_content_update INTEGER CHECK (effort_content_update BETWEEN 1 AND 5),
    effort_per_training INTEGER CHECK (effort_per_training BETWEEN 1 AND 5),
    advantages TEXT[],
    disadvantages TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. Training Program Clusters Table (6 clusters)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS training_program_cluster (
    id SERIAL PRIMARY KEY,
    cluster_key VARCHAR(50) UNIQUE NOT NULL,
    cluster_name VARCHAR(100) NOT NULL,
    training_program_name VARCHAR(100) NOT NULL,
    description TEXT,
    typical_org_roles TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. Strategy-Learning Format Matrix
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_learning_format_matrix (
    id SERIAL PRIMARY KEY,
    strategy_template_id INTEGER NOT NULL REFERENCES strategy_template(id),
    learning_format_id INTEGER NOT NULL REFERENCES learning_format(id),
    consistency VARCHAR(5) NOT NULL CHECK (consistency IN ('++', '+', '--')),
    UNIQUE(strategy_template_id, learning_format_id)
);

-- -----------------------------------------------------------------------------
-- 4. Competency-Learning Format Matrix
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competency_learning_format_matrix (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER NOT NULL REFERENCES competency(id),
    learning_format_id INTEGER NOT NULL REFERENCES learning_format(id),
    max_achievable_level INTEGER NOT NULL CHECK (max_achievable_level IN (0, 1, 2, 4, 6)),
    UNIQUE(competency_id, learning_format_id)
);

-- -----------------------------------------------------------------------------
-- 5. Extend organization_role_mappings with Training Program Cluster
-- -----------------------------------------------------------------------------
ALTER TABLE organization_role_mappings
ADD COLUMN IF NOT EXISTS training_program_cluster_id INTEGER REFERENCES training_program_cluster(id);

CREATE INDEX IF NOT EXISTS idx_org_role_training_cluster
ON organization_role_mappings(organization_id, training_program_cluster_id);

-- -----------------------------------------------------------------------------
-- 6. Phase 3 Training Module Selections (future - for storing user selections)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS phase3_training_module (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    competency_id INTEGER NOT NULL REFERENCES competency(id),
    target_level INTEGER NOT NULL CHECK (target_level IN (1, 2, 4)),
    pmt_type VARCHAR(20) CHECK (pmt_type IN ('process', 'method', 'tool', 'combined')),
    selected_format_id INTEGER REFERENCES learning_format(id),
    estimated_participants INTEGER,
    actual_users_with_gap INTEGER,
    suitability_factor1_status VARCHAR(10), -- green, yellow, red
    suitability_factor2_status VARCHAR(10),
    suitability_factor3_status VARCHAR(10),
    confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, competency_id, target_level, pmt_type)
);

-- -----------------------------------------------------------------------------
-- 7. Phase 3 Timeline Milestones (LLM-generated)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS phase3_timeline (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    milestone_name VARCHAR(100) NOT NULL,
    milestone_order INTEGER NOT NULL,
    estimated_date DATE,
    quarter VARCHAR(10),  -- e.g., "Q2 2026"
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_reasoning TEXT,
    UNIQUE(organization_id, milestone_order)
);

-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_phase3_module_org ON phase3_training_module(organization_id);
CREATE INDEX IF NOT EXISTS idx_phase3_timeline_org ON phase3_timeline(organization_id);
CREATE INDEX IF NOT EXISTS idx_strategy_lf_matrix_strategy ON strategy_learning_format_matrix(strategy_template_id);
CREATE INDEX IF NOT EXISTS idx_competency_lf_matrix_competency ON competency_learning_format_matrix(competency_id);
```

---

## 7. Verification Checklist

### Meeting Notes (11.12.2025) vs Implementation

| Meeting Point | Spec Section | Implementation Status |
|---------------|--------------|----------------------|
| Two training views (competency-level, role-clustered) | 3.1 | Schema ready, logic needed |
| Low maturity = only competency view | 3.2 | Logic check on maturity_score |
| 6 Training Program Clusters | 3.3.2 | New table to create |
| Training Program Clusters != 14 SE Role Clusters | 3.3 | Clarified in spec |
| 10 Learning Formats from Sachin | 4.1 | New table to create |
| 3 Suitability Factors | 4.4 | Logic to implement |
| NO auto-recommendation, user selects | 4.3 | Design confirmed |
| Feedback based on 3 factors (green/yellow/red) | 4.5 | Logic to implement |
| Competency-LF Matrix | 7.2 | New table to create |
| Strategy-LF Matrix | 7.1 | New table to create |
| Participant count scaling | 8 | Logic to implement |
| Existing training check in Phase 2 | 2.2 | Already implemented |
| Timeline (concept, pilot, rollout) | 5 | LLM generation to implement |
| Export to Excel | 11 | Feature to implement |

### Data Alignment Verification

| Data Type | DB Column/Table | Spec Reference | Verified |
|-----------|-----------------|----------------|----------|
| Competency IDs | competency.id | Section 7.2 | YES - IDs match |
| Strategy IDs | strategy_template.id | Section 7.1 | YES - IDs match |
| Role Cluster IDs | role_cluster.id | N/A (different) | YES - clarified |
| Training Cluster IDs | training_program_cluster.id | Section 3.3.2 | TO CREATE |
| Learning Format IDs | learning_format.id | Section 4.1 | TO CREATE |

---

## References

1. **Specification**: `data/source/Phase 3/Phase3_Macro_Planning_Specification_v3.2.md`
2. **Meeting Notes**: `data/Meeting notes/Meeting notes 11.12.2025.txt`
3. **Sachin's Thesis**: Learning Formats definitions and matrices
4. **Existing Tables**: See Section 2 for current schema

---

## Next Steps

1. Review this implementation plan
2. Create migration `014_phase3_learning_formats.sql`
3. Seed reference data (learning formats, clusters, matrices)
4. Update Phase 1 Task 2 role mapping with Training Cluster
5. Implement Phase 3 backend services
6. Implement Phase 3 frontend components

---

*Document created: January 2026*
*Last updated: January 2026*
