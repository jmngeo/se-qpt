# SE-QPT Data Dependency Matrix

## Overview

This document maps the dependencies between all 31 data elements in the SE-QPT application. It shows how data flows through the system and which elements influence or depend on others.

**Companion Document:** SE-QPT_Data_Element_Definitions.md

---

## Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| SE | Systems Engineering |
| LO | Learning Objectives |
| PMT | Processes, Methods, Tools |
| WBT | Web-Based Training |
| CBT | Computer-Based Training |

---

## Comprehensive Dependency Matrix (Single Table)

This table shows all 31 data elements with their complete dependency relationships.

**Legend:**
- **Depends On**: Elements that this element requires as input
- **Influences**: Elements that use this element as input
- **—**: No dependencies (root/reference data)

| # | Element | Category | Depends On (Inputs) | Influences (Outputs) |
|---|---------|----------|---------------------|----------------------|
| 1 | **Organization** | Foundational | — | All elements (organization-scoped) |
| 2 | **User** | Foundational | Organization | Competency Assessment, LO |
| 3 | **Organization's SE Maturity** | Maturity | 4 Fields of Action | Roles (availability), Strategies (selection), Competency Assessment (pathway), LO (view), Training Structure (view) |
| 4 | **4 Fields of Action** | Maturity | User input | SE Maturity |
| 5 | **Training Target Group Size** | Maturity | User input | Strategies (TTT recommendation), Suitability Analysis (Factor 1), Timeline |
| 6 | **Roles (Organization Roles)** | Role Framework | Organization, SE Maturity, 14 SE Role Clusters | Role-Process Matrix, Role-Competency Matrix, Competency Assessment, LO, TrainingProgramCluster, Training Modules |
| 7 | **14 SE Role Clusters** | Role Framework | — (Reference: Könemann et al.) | Roles (mapping), Role-Process Matrix (baseline) |
| 8 | **TrainingProgramCluster** | Role Framework | Roles, Competency Areas, Role-Competency Matrix, Competency Assessment | Training Structure, Training Modules |
| 9 | **Competency** | Competency | — (Reference: Extended INCOSE) | Competency Areas, CompetencyIndicator, Process-Competency Matrix, Role-Competency Matrix, UnknownRoleCompetencyMatrix, LO Templates, Competency Assessment, LO, CompetencyLearningFormatMatrix, Training Modules |
| 10 | **Competency Areas** | Competency | Competency | TrainingProgramCluster |
| 11 | **Competency Levels** | Competency | — (Reference: fixed scale) | CompetencyIndicator, Process-Competency Matrix, Role-Competency Matrix, UnknownRoleCompetencyMatrix, LO Templates, Competency Assessment, LO, Existing Training Check, CompetencyLearningFormatMatrix, Training Modules |
| 12 | **CompetencyIndicator** | Competency | Competency, Competency Levels | Competency Assessment (guidance) |
| 13 | **ISO Processes** | Process | — (Reference: ISO/IEC 15288) | Role-Process Matrix, Process-Competency Matrix, UnknownRoleProcessMatrix |
| 14 | **Role-Process Matrix** | Matrix | Roles, ISO Processes, 14 SE Role Clusters, GenAI (for CUSTOM) | Role-Competency Matrix |
| 15 | **Process-Competency Matrix** | Matrix | — (Reference: Global) | Role-Competency Matrix, UnknownRoleCompetencyMatrix |
| 16 | **Role-Competency Matrix** | Matrix | Role-Process Matrix, Process-Competency Matrix | Competency Assessment (required levels), LO (role requirements), TrainingProgramCluster |
| 17 | **UnknownRoleProcessMatrix** | Matrix | ISO Processes, User task descriptions, GenAI/RAG | UnknownRoleCompetencyMatrix |
| 18 | **UnknownRoleCompetencyMatrix** | Matrix | UnknownRoleProcessMatrix, Process-Competency Matrix | Competency Assessment (task-based required levels), LO (task-based gaps) |
| 19 | **Qualification Strategies** | Strategy | SE Maturity, Training Target Group Size | LO Templates, LO, StrategyLearningFormatMatrix, Suitability Analysis (Factor 3), PMT (requirement trigger), Timeline |
| 20 | **LO Templates (StrategyTemplateCompetency)** | Strategy | Strategies, Competency, Competency Levels | LO |
| 21 | **Competency Assessment** | Assessment | SE Maturity (pathway), Roles OR User tasks, Role-Competency Matrix OR UnknownRoleCompetencyMatrix, CompetencyIndicator, Competency, Competency Levels | LO, TrainingProgramCluster |
| 22 | **Existing Training Check** | LO | Competency, Competency Levels, User input | LO (exclusion), Training Modules (exclusion) |
| 23 | **PMT** | LO | SE Maturity, Strategies, User input/GenAI | LO (customization) |
| 24 | **Learning Objectives** | LO | Strategies, LO Templates, Competency Assessment, Role-Competency Matrix OR UnknownRoleCompetencyMatrix, Existing Training Check, PMT, SE Maturity | Training Modules, Timeline |
| 25 | **Training Structure** | Macro Planning | SE Maturity, Roles, TrainingProgramCluster | Training Modules (presentation) |
| 26 | **Training Modules** | Macro Planning | LO, Training Structure, Competency, Competency Levels, Existing Training Check | Learning Format selection, Suitability Analysis, Timeline |
| 27 | **Learning Formats** | Macro Planning | — (Reference: Sachin Kumar thesis) | StrategyLearningFormatMatrix, CompetencyLearningFormatMatrix, Suitability Analysis, Training Modules, Timeline |
| 28 | **StrategyLearningFormatMatrix** | Macro Planning | — (Reference: Strategies × Formats) | Suitability Analysis (Factor 3) |
| 29 | **CompetencyLearningFormatMatrix** | Macro Planning | — (Reference: Competency × Formats) | Suitability Analysis (Factor 2) |
| 30 | **Suitability Analysis** | Macro Planning | Training Target Group Size, Training Modules, CompetencyLearningFormatMatrix, StrategyLearningFormatMatrix, Learning Formats | Format selection guidance |
| 31 | **Timeline** | Macro Planning | Training Modules, Training Target Group Size, Strategies, Learning Formats | — (Final output) |

---

## Part 1: Dependency Matrix by Element (Detailed)

This section provides detailed descriptions for each element's dependencies.

### FOUNDATIONAL ENTITIES

#### 1. Organization
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Root entity, no dependencies) |
| **Influences** | All other elements (all data is organization-scoped) |
| **Phase** | Setup |

#### 2. User
| Aspect | Details |
|--------|---------|
| **Depends On** | Organization |
| **Influences** | Competency Assessment (assessment performer), Learning Objectives (assessment data contributor) |
| **Phase** | Setup → All Phases |

---

### MATURITY ASSESSMENT

#### 3. Organization's SE Maturity
| Aspect | Details |
|--------|---------|
| **Depends On** | 4 Fields of Action (input data) |
| **Influences** | Roles (availability of role definition), Strategy Selection (recommendations), Competency Assessment (pathway: Role-based vs Task-based), Learning Objectives (view: Organizational vs Role-based), Training Structure (view availability: Role-clustered) |
| **Phase** | Phase 1 → Phase 2, Phase 3 |
| **Key Logic** | If SE Roles & Processes = "Defined and Established" → High maturity pathway |

#### 4. 4 Fields of Action
| Aspect | Details |
|--------|---------|
| **Depends On** | User input (Admin answers questions) |
| **Influences** | Organization's SE Maturity (calculation input) |
| **Phase** | Phase 1 |
| **Components** | Rollout Scope, SE Roles & Processes, SE Mindset, Knowledge Base |

#### 5. Training Target Group Size
| Aspect | Details |
|--------|---------|
| **Depends On** | User input (Admin specifies) |
| **Influences** | Strategy Selection (if >100, recommends Train the Trainer), Suitability Analysis Factor 1 (participant scaling), Timeline (duration planning) |
| **Phase** | Phase 1 → Phase 3 |

---

### ROLE FRAMEWORK

#### 6. Roles (Organization Roles)
| Aspect | Details |
|--------|---------|
| **Depends On** | Organization, SE Maturity (high maturity required for formal role definition), 14 SE Role Clusters (mapping reference) |
| **Influences** | Role-Process Matrix (role dimension), Role-Competency Matrix (role dimension), Competency Assessment (role selection for role-based path), Learning Objectives (role-based gaps), TrainingProgramCluster (assignment), Training Modules (role-clustered view) |
| **Phase** | Phase 1 → Phase 2, Phase 3 |

#### 7. 14 SE Role Clusters
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Reference data from Könemann et al.) |
| **Influences** | Roles (mapping target for STANDARD roles), Role-Process Matrix (baseline values for mapped roles) |
| **Phase** | Reference Data |

#### 8. TrainingProgramCluster
| Aspect | Details |
|--------|---------|
| **Depends On** | Roles, Competency Areas (for classification), Role-Competency Matrix (gap patterns determine cluster), Competency Assessment results |
| **Influences** | Training Structure (role-clustered view), Training Modules (grouping) |
| **Phase** | Phase 2 (Calculated) → Phase 3 |
| **Assignment Logic** | Engineers: Level 4+ gaps in Technical/Core; Managers: Level 4+ gaps only in Social/Personal or Management; Interfacing Partners: Only Level 1-2 gaps |

---

### COMPETENCY FRAMEWORK

#### 9. Competency (16 SE Competencies)
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Reference data from Extended INCOSE Framework, Könemann et al.) |
| **Influences** | Competency Areas (grouped into), CompetencyIndicator (indicators per competency), Process-Competency Matrix (competency dimension), Role-Competency Matrix (competency dimension), UnknownRoleCompetencyMatrix (competency dimension), Learning Objectives Templates (competency dimension), Competency Assessment (assessed competencies), Learning Objectives (gap identification), CompetencyLearningFormatMatrix (competency dimension), Training Modules (competency focus) |
| **Phase** | Reference Data → Phase 2, Phase 3 |

#### 10. Competency Areas
| Aspect | Details |
|--------|---------|
| **Depends On** | Competency (grouping of 16 competencies) |
| **Influences** | TrainingProgramCluster (classification logic uses areas) |
| **Phase** | Reference Data |
| **Categories** | Core, Technical, Management, Social/Personal |

#### 11. Competency Levels
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Reference data, fixed scale) |
| **Influences** | CompetencyIndicator (level dimension), Process-Competency Matrix (level values), Role-Competency Matrix (level values), UnknownRoleCompetencyMatrix (level values), Learning Objectives Templates (target levels), Competency Assessment (assessment scale), Learning Objectives (gap calculation), Existing Training Check (level specification), CompetencyLearningFormatMatrix (achievable levels), Training Modules (target levels) |
| **Phase** | Reference Data → All competency calculations |
| **Values** | 0 (Not required), 1 (Knowing), 2 (Understanding), 4 (Applying), 6 (Mastering) |

#### 12. CompetencyIndicator
| Aspect | Details |
|--------|---------|
| **Depends On** | Competency, Competency Levels |
| **Influences** | Competency Assessment (behavioral guidance for self-assessment) |
| **Phase** | Reference Data |

---

### PROCESS FRAMEWORK

#### 13. ISO Processes
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Reference data from ISO/IEC 15288:2015) |
| **Influences** | Role-Process Matrix (process dimension), Process-Competency Matrix (process dimension), UnknownRoleProcessMatrix (process dimension, task-based mapping target) |
| **Phase** | Reference Data |
| **Count** | ~30 processes in 4 life cycle categories |

---

### MATRIX RELATIONSHIPS

#### 14. Role-Process Matrix
| Aspect | Details |
|--------|---------|
| **Depends On** | Roles (role dimension), ISO Processes (process dimension), 14 SE Role Clusters (baseline values for STANDARD roles), GenAI (baseline values for CUSTOM roles) |
| **Influences** | Role-Competency Matrix (input for calculation) |
| **Phase** | Phase 1 |
| **Values** | 0=Not Involved, 1=Supports, 2=Responsible, 3=Designs |

#### 15. Process-Competency Matrix
| Aspect | Details |
|--------|---------|
| **Depends On** | ISO Processes (process dimension), Competency (competency dimension) — Global reference data |
| **Influences** | Role-Competency Matrix (input for calculation), UnknownRoleCompetencyMatrix (input for calculation) |
| **Phase** | Reference Data (Global, affects all organizations) |
| **Values** | 0=Not relevant, 1=Useful, 2=Necessary |

#### 16. Role-Competency Matrix
| Aspect | Details |
|--------|---------|
| **Depends On** | Role-Process Matrix, Process-Competency Matrix |
| **Influences** | Competency Assessment (required levels for role-based path), Learning Objectives (role requirement component of gap), TrainingProgramCluster (gap pattern analysis) |
| **Phase** | Phase 1 (Calculated automatically) |
| **Formula** | `role_competency_value = MAX(role_process_value × process_competency_value)` aggregated across all processes |
| **Values** | 0, 1, 2, 4, 6 |

#### 17. UnknownRoleProcessMatrix
| Aspect | Details |
|--------|---------|
| **Depends On** | ISO Processes (process dimension), User task descriptions (input), GenAI/RAG (task-to-process mapping) |
| **Influences** | UnknownRoleCompetencyMatrix (input for calculation) |
| **Phase** | Phase 2 (Task-based path only) |
| **Values** | 0=Not performing, 1=Supporting, 2=Responsible, 3=Designing |

#### 18. UnknownRoleCompetencyMatrix
| Aspect | Details |
|--------|---------|
| **Depends On** | UnknownRoleProcessMatrix, Process-Competency Matrix |
| **Influences** | Competency Assessment (required levels for task-based path), Learning Objectives (task-based gaps) |
| **Phase** | Phase 2 (Calculated automatically, task-based path only) |
| **Formula** | Same as Role-Competency Matrix but indexed by username |
| **Values** | 0, 1, 2, 4, 6 |

---

### QUALIFICATION STRATEGIES

#### 19. Qualification/Training Strategies
| Aspect | Details |
|--------|---------|
| **Depends On** | SE Maturity (selection logic), Training Target Group Size (TTT recommendation) |
| **Influences** | Learning Objectives Templates (strategy-competency targets), Learning Objectives (target levels), StrategyLearningFormatMatrix (strategy dimension), Suitability Analysis Factor 3 (strategy fit), PMT requirement (certain strategies require PMT input) |
| **Phase** | Phase 1 → Phase 2, Phase 3 |
| **Selection Logic** | Low maturity: SE for Managers + secondary; High maturity: based on rollout scope; If >100 employees: + Train the Trainer |

#### 20. Learning Objectives Templates (StrategyTemplateCompetency)
| Aspect | Details |
|--------|---------|
| **Depends On** | Strategies (strategy dimension), Competency (competency dimension), Competency Levels (target values) |
| **Influences** | Learning Objectives (template text, target levels) |
| **Phase** | Reference Data |
| **Size** | 112 entries (7 strategies × 16 competencies) |

---

### COMPETENCY ASSESSMENT

#### 21. Competency Assessment
| Aspect | Details |
|--------|---------|
| **Depends On** | SE Maturity (pathway determination), Roles (role-based path: role selection), User task descriptions (task-based path), Role-Competency Matrix (role-based path: required levels), UnknownRoleCompetencyMatrix (task-based path: required levels), CompetencyIndicator (assessment guidance), Competency (assessed competencies), Competency Levels (assessment scale) |
| **Influences** | Learning Objectives (current levels, gap identification), TrainingProgramCluster (gap patterns) |
| **Phase** | Phase 2 |
| **Pathways** | Role-based (high maturity): User selects roles → required competencies from Role-Competency Matrix; Task-based (low maturity): User describes tasks → GenAI maps to processes → required competencies from UnknownRoleCompetencyMatrix |

---

### LEARNING OBJECTIVES

#### 22. Existing Training Check
| Aspect | Details |
|--------|---------|
| **Depends On** | Competency (competency selection), Competency Levels (level specification), User input (Admin specifies existing training) |
| **Influences** | Learning Objectives (exclusion of covered levels), Training Modules (exclusion of covered levels) |
| **Phase** | Phase 2 |

#### 23. PMT (Processes, Methods, Tools)
| Aspect | Details |
|--------|---------|
| **Depends On** | SE Maturity (high maturity required), Strategies (certain strategies: Needs-based, Continuous Support), User input or GenAI extraction from documentation |
| **Influences** | Learning Objectives (customization of LO text via GenAI) |
| **Phase** | Phase 2 |
| **Condition** | Only required for high maturity organizations with specific strategies |

#### 24. Learning Objectives
| Aspect | Details |
|--------|---------|
| **Depends On** | Strategies (target levels), Learning Objectives Templates (template text), Competency Assessment (current levels), Role-Competency Matrix OR UnknownRoleCompetencyMatrix (required levels), Existing Training Check (exclusions), PMT (customization), SE Maturity (view: organizational vs role-based) |
| **Influences** | Training Modules (one module per competency-level gap), Timeline (module count input) |
| **Phase** | Phase 2 → Phase 3 |
| **Gap Logic** | High maturity: Gap per role = MAX(strategy target, role requirement) - current level; Low maturity: Gap = strategy target - current level |

---

### MACRO PLANNING

#### 25. Training Structure
| Aspect | Details |
|--------|---------|
| **Depends On** | SE Maturity (view availability), Roles (role-clustered view requirement), TrainingProgramCluster (clustering for role-clustered view) |
| **Influences** | Training Modules (presentation/grouping) |
| **Phase** | Phase 3 |
| **Views** | Competency-level based (always available); Role-clustered based (high maturity only) |

#### 26. Training Modules
| Aspect | Details |
|--------|---------|
| **Depends On** | Learning Objectives (one module per gap), Training Structure (presentation), Competency (module focus), Competency Levels (target level), Existing Training Check (exclusions) |
| **Influences** | Learning Format selection (format per module), Suitability Analysis (module context), Timeline (module count, duration) |
| **Phase** | Phase 3 |

#### 27. Learning Formats
| Aspect | Details |
|--------|---------|
| **Depends On** | — (Reference data from Sachin Kumar thesis) |
| **Influences** | StrategyLearningFormatMatrix (format dimension), CompetencyLearningFormatMatrix (format dimension), Suitability Analysis (format characteristics), Training Modules (format selection), Timeline (format-based duration estimates) |
| **Phase** | Reference Data → Phase 3 |
| **Count** | 10 formats: Seminar, Webinar, Coaching, Mentoring, WBT, CBT, Game-Based Learning, Conference, Blended Learning, Self-Learning |

#### 28. StrategyLearningFormatMatrix
| Aspect | Details |
|--------|---------|
| **Depends On** | Strategies (strategy dimension), Learning Formats (format dimension) — Reference data |
| **Influences** | Suitability Analysis Factor 3 (strategy-format consistency) |
| **Phase** | Reference Data |
| **Size** | 70 entries (7 strategies × 10 formats) |
| **Values** | ++ (Highly Recommended), + (Partly Recommended), -- (Not Consistent) |

#### 29. CompetencyLearningFormatMatrix
| Aspect | Details |
|--------|---------|
| **Depends On** | Competency (competency dimension), Learning Formats (format dimension) — Reference data |
| **Influences** | Suitability Analysis Factor 2 (max achievable level) |
| **Phase** | Reference Data |
| **Size** | 160 entries (16 competencies × 10 formats) |
| **Values** | 0 (not suitable), 1, 2, 4, 6 (max achievable level) |

#### 30. Suitability Analysis (3 Factors)
| Aspect | Details |
|--------|---------|
| **Depends On** | Training Target Group Size (Factor 1: participant scaling), Training Modules (participant count per module), CompetencyLearningFormatMatrix (Factor 2: level achievability), StrategyLearningFormatMatrix (Factor 3: strategy fit), Learning Formats (format characteristics) |
| **Influences** | Format selection guidance (Green/Yellow/Red indicators) |
| **Phase** | Phase 3 |
| **Factors** | Factor 1: Participant Count fit; Factor 2: Level Achievable; Factor 3: Strategy Fit |

#### 31. Timeline
| Aspect | Details |
|--------|---------|
| **Depends On** | Training Modules (count, content), Training Target Group Size (scaling), Strategies (approach), Learning Formats (selected formats, duration estimates) |
| **Influences** | — (Final output, nothing depends on it) |
| **Phase** | Phase 3 (Final output) |
| **Generation** | GenAI-generated milestones based on all inputs |

---

## Part 2: Cross-Reference Dependency Matrix

This matrix shows dependencies between elements using symbols:
- **→** Element in row influences element in column
- **←** Element in row depends on element in column
- **↔** Bidirectional relationship
- **—** No direct dependency

### Matrix Legend
- **Row**: Source element
- **Column**: Target element
- **Cell**: Dependency direction from row to column

### Phase 1 Elements Cross-Reference

| Element | SE Maturity | Fields of Action | Target Group Size | Roles | 14 Role Clusters | Role-Process Matrix | Strategies |
|---------|-------------|------------------|-------------------|-------|------------------|---------------------|------------|
| **SE Maturity** | — | ← | — | → | — | — | → |
| **Fields of Action** | → | — | — | — | — | — | — |
| **Target Group Size** | — | — | — | — | — | — | → |
| **Roles** | ← | — | — | — | ← | → | — |
| **14 Role Clusters** | — | — | — | → | — | → | — |
| **Role-Process Matrix** | — | — | — | ← | ← | — | — |
| **Strategies** | ← | — | ← | — | — | — | — |

### Phase 2 Elements Cross-Reference

| Element | Role-Comp Matrix | Unknown Role-Process | Unknown Role-Comp | Competency Assessment | Existing Training | PMT | Learning Objectives |
|---------|------------------|---------------------|-------------------|----------------------|-------------------|-----|---------------------|
| **Role-Comp Matrix** | — | — | — | → | — | — | → |
| **Unknown Role-Process** | — | — | → | — | — | — | — |
| **Unknown Role-Comp** | — | ← | — | → | — | — | → |
| **Competency Assessment** | ← | — | ← | — | — | — | → |
| **Existing Training** | — | — | — | — | — | — | → |
| **PMT** | — | — | — | — | — | — | → |
| **Learning Objectives** | ← | — | ← | ← | ← | ← | — |

### Phase 3 Elements Cross-Reference

| Element | Training Structure | Training Modules | Learning Formats | Strategy-Format Matrix | Comp-Format Matrix | Suitability Analysis | Timeline |
|---------|-------------------|------------------|------------------|----------------------|-------------------|---------------------|----------|
| **Training Structure** | — | → | — | — | — | — | — |
| **Training Modules** | ← | — | ← | — | — | → | → |
| **Learning Formats** | — | → | — | → | → | → | → |
| **Strategy-Format Matrix** | — | — | ← | — | — | → | — |
| **Comp-Format Matrix** | — | — | ← | — | — | → | — |
| **Suitability Analysis** | — | ← | ← | ← | ← | — | — |
| **Timeline** | — | ← | ← | — | — | — | — |

---

## Part 3: Data Flow by Phase

### Phase 1: Assessment & Planning Foundation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: MATURITY ASSESSMENT & ROLE IDENTIFICATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Task 1: Maturity Assessment                                                │
│  ┌──────────────────┐                                                       │
│  │ 4 Fields of      │──────────▶ Organization's SE Maturity                 │
│  │ Action (input)   │                    │                                  │
│  └──────────────────┘                    │                                  │
│                                          ▼                                  │
│  ┌──────────────────┐           ┌────────────────────┐                      │
│  │ Training Target  │           │ High/Low Maturity  │                      │
│  │ Group Size       │           │ Pathway Decision   │                      │
│  └────────┬─────────┘           └─────────┬──────────┘                      │
│           │                               │                                 │
│           │                               ▼                                 │
│  Task 2: Role Identification (High Maturity Path)                           │
│           │         ┌──────────────────────────────────┐                    │
│           │         │ 14 SE Role Clusters (Reference)  │                    │
│           │         └─────────────┬────────────────────┘                    │
│           │                       │                                         │
│           │                       ▼                                         │
│           │         ┌──────────────────────────────────┐                    │
│           │         │ Roles (Organization Roles)       │◀─── User defines   │
│           │         └─────────────┬────────────────────┘                    │
│           │                       │                                         │
│           │                       ▼                                         │
│           │         ┌──────────────────────────────────┐                    │
│           │         │ Role-Process Matrix              │◀─── ISO Processes  │
│           │         └─────────────┬────────────────────┘     (Reference)    │
│           │                       │                                         │
│           │                       │ × Process-Competency Matrix (Global)    │
│           │                       │                                         │
│           │                       ▼                                         │
│           │         ┌──────────────────────────────────┐                    │
│           │         │ Role-Competency Matrix           │ (Calculated)       │
│           │         └──────────────────────────────────┘                    │
│           │                                                                 │
│  Task 3: Strategy Selection                                                 │
│           │         ┌──────────────────────────────────┐                    │
│           └────────▶│ Qualification Strategies         │◀─── SE Maturity    │
│                     │ (7 options, primary + secondary) │                    │
│                     └──────────────────────────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Competency Assessment & Learning Objectives

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: COMPETENCY ASSESSMENT & LEARNING OBJECTIVES                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Task 1: Competency Assessment                                              │
│                                                                             │
│  HIGH MATURITY PATH:                    LOW MATURITY PATH:                  │
│  ┌────────────────────┐                 ┌────────────────────┐              │
│  │ User selects Roles │                 │ User describes     │              │
│  └─────────┬──────────┘                 │ tasks (Support/    │              │
│            │                            │ Responsible/Design)│              │
│            ▼                            └─────────┬──────────┘              │
│  ┌────────────────────┐                           │                         │
│  │ Role-Competency    │                           ▼                         │
│  │ Matrix (Required   │                 ┌────────────────────┐              │
│  │ levels)            │                 │ GenAI/RAG Analysis │              │
│  └─────────┬──────────┘                 │ (Task → Processes) │              │
│            │                            └─────────┬──────────┘              │
│            │                                      ▼                         │
│            │                            ┌────────────────────┐              │
│            │                            │ UnknownRole-       │              │
│            │                            │ ProcessMatrix      │              │
│            │                            └─────────┬──────────┘              │
│            │                                      │                         │
│            │                                      │ × Process-Competency    │
│            │                                      │   Matrix (Global)       │
│            │                                      ▼                         │
│            │                            ┌────────────────────┐              │
│            │                            │ UnknownRole-       │              │
│            │                            │ CompetencyMatrix   │              │
│            └──────────┬─────────────────┴─────────┬──────────┘              │
│                       │                           │                         │
│                       ▼                           ▼                         │
│            ┌──────────────────────────────────────────────────┐             │
│            │ Self-Assessment (User rates current levels)      │             │
│            │ using CompetencyIndicators as guidance           │             │
│            └──────────────────────┬───────────────────────────┘             │
│                                   │                                         │
│                                   ▼                                         │
│  Task 2: Existing Training Check                                            │
│            ┌──────────────────────────────────────────────────┐             │
│            │ Existing Training Check                          │             │
│            │ (Competencies + Levels already covered)          │             │
│            └──────────────────────┬───────────────────────────┘             │
│                                   │                                         │
│  Task 3: Learning Objectives Generation                                     │
│                                   │                                         │
│  ┌────────────────┐               │     ┌────────────────────┐              │
│  │ Strategies     │───────────────┼────▶│ Learning           │              │
│  │ (Target levels)│               │     │ Objectives         │              │
│  └────────────────┘               │     │                    │              │
│                                   │     │ Gap = MAX(strategy,│              │
│  ┌────────────────┐               │     │ role req) - current│              │
│  │ LO Templates   │───────────────┼────▶│                    │              │
│  │ (Template text)│               │     │ Exclusions applied │              │
│  └────────────────┘               │     │ from Existing      │              │
│                                   │     │ Training           │              │
│  ┌────────────────┐               │     │                    │              │
│  │ PMT (optional) │───────────────┴────▶│ Customized with    │              │
│  │ (Customization)│                     │ PMT via GenAI      │              │
│  └────────────────┘                     └─────────┬──────────┘              │
│                                                   │                         │
│            ┌──────────────────────────────────────┘                         │
│            ▼                                                                │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ TrainingProgramCluster Assignment                          │             │
│  │ (Based on gap patterns: Engineers/Managers/Partners)       │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Macro Planning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: MACRO PLANNING                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Task 1: Training Structure Selection                                       │
│  ┌────────────────────┐      ┌────────────────────────────────────┐         │
│  │ SE Maturity        │─────▶│ Training Structure                 │         │
│  │ (View availability)│      │ • Competency-level (always)        │         │
│  └────────────────────┘      │ • Role-clustered (high maturity)   │         │
│                              └─────────────────┬──────────────────┘         │
│  ┌────────────────────┐                        │                            │
│  │ TrainingProgram-   │────────────────────────┘                            │
│  │ Cluster            │                                                     │
│  └────────────────────┘                                                     │
│                                                                             │
│  Task 2: Training Modules & Learning Format Selection                       │
│  ┌────────────────────┐      ┌────────────────────────────────────┐         │
│  │ Learning Objectives│─────▶│ Training Modules                   │         │
│  │ (Gaps identified)  │      │ (One per competency-level gap)     │         │
│  └────────────────────┘      └─────────────────┬──────────────────┘         │
│                                                │                            │
│                                                ▼                            │
│  ┌────────────────────┐      ┌────────────────────────────────────┐         │
│  │ Learning Formats   │─────▶│ Format Selection per Module        │         │
│  │ (10 options)       │      └─────────────────┬──────────────────┘         │
│  └────────────────────┘                        │                            │
│                                                ▼                            │
│                              ┌────────────────────────────────────┐         │
│                              │ Suitability Analysis (3 Factors)   │         │
│  ┌────────────────────┐      │                                    │         │
│  │ Training Target    │─────▶│ Factor 1: Participant Count        │         │
│  │ Group Size         │      │ (Can format handle scaled count?)  │         │
│  └────────────────────┘      │                                    │         │
│                              │                                    │         │
│  ┌────────────────────┐      │                                    │         │
│  │ Competency-        │─────▶│ Factor 2: Level Achievable         │         │
│  │ LearningFormat     │      │ (Can format achieve target level?) │         │
│  │ Matrix             │      │                                    │         │
│  └────────────────────┘      │                                    │         │
│                              │                                    │         │
│  ┌────────────────────┐      │                                    │         │
│  │ Strategy-          │─────▶│ Factor 3: Strategy Fit             │         │
│  │ LearningFormat     │      │ (Is format consistent with         │         │
│  │ Matrix             │      │  selected strategy?)               │         │
│  └────────────────────┘      │                                    │         │
│                              │ Output: Green/Yellow/Red per factor│         │
│                              └─────────────────┬──────────────────┘         │
│                                                │                            │
│  Task 3: Timeline Generation                   │                            │
│                                                ▼                            │
│  ┌────────────────────┐      ┌────────────────────────────────────┐         │
│  │ Training Modules   │─────▶│ Timeline                           │         │
│  │ (Count, content)   │      │ (GenAI-generated milestones)       │         │
│  └────────────────────┘      │                                    │         │
│                              │ Inputs:                            │         │
│  ┌────────────────────┐      │ • Module count                     │         │
│  │ Selected Formats   │─────▶│ • Target group size                │         │
│  └────────────────────┘      │ • Selected strategies              │         │
│                              │ • Learning formats chosen          │         │
│  ┌────────────────────┐      │                                    │         │
│  │ Strategies         │─────▶│ Output:                            │         │
│  └────────────────────┘      │ • Milestones with dates            │         │
│                              │ • Phases                           │         │
│  ┌────────────────────┐      │ • Dependencies                     │         │
│  │ Training Target    │─────▶│                                    │         │
│  │ Group Size         │      └────────────────────────────────────┘         │
│  └────────────────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 4: Reference Data vs. Calculated Data

### Reference Data (Static, Predefined)
These elements are predefined and shared across all organizations:

| Element | Source | Size/Count |
|---------|--------|------------|
| 14 SE Role Clusters | Könemann et al. | 14 clusters |
| Competency (16 SE) | Extended INCOSE (Könemann et al.) | 16 competencies |
| Competency Areas | Grouping of 16 competencies | 4 areas |
| Competency Levels | Fixed scale | 5 values (0,1,2,4,6) |
| CompetencyIndicator | Per competency per level | ~64 indicators |
| ISO Processes | ISO/IEC 15288:2015 | ~30 processes |
| Process-Competency Matrix | Global baseline | 30×16 = 480 cells |
| Learning Objectives Templates | Per strategy per competency | 7×16 = 112 entries |
| Learning Formats | Sachin Kumar thesis | 10 formats |
| StrategyLearningFormatMatrix | Strategy-format consistency | 7×10 = 70 entries |
| CompetencyLearningFormatMatrix | Competency-format achievability | 16×10 = 160 entries |

### Organization-Specific Input Data
These elements are provided by users for each organization:

| Element | Input By | Phase |
|---------|----------|-------|
| 4 Fields of Action | Admin | Phase 1 |
| Training Target Group Size | Admin | Phase 1 |
| Roles (Organization Roles) | Admin | Phase 1 |
| Existing Training Check | Admin | Phase 2 |
| PMT (optional) | Admin / GenAI | Phase 2 |
| Competency Assessment scores | Employees | Phase 2 |
| User task descriptions (task-based) | Employees | Phase 2 |
| Training Structure selection | Admin | Phase 3 |
| Learning Format selections | Admin | Phase 3 |

### Calculated Data (Derived Automatically)
These elements are computed by the system:

| Element | Calculated From | Formula/Logic |
|---------|-----------------|---------------|
| Organization's SE Maturity | 4 Fields of Action | Weighted average with balance penalty |
| Role-Process Matrix (baseline) | 14 SE Role Clusters + GenAI | Template for STANDARD, GenAI for CUSTOM |
| Role-Competency Matrix | Role-Process × Process-Competency | MAX(product) per role-competency pair |
| UnknownRoleProcessMatrix | User tasks + GenAI/RAG | Task-to-process mapping |
| UnknownRoleCompetencyMatrix | UnknownRoleProcess × Process-Competency | Same formula as Role-Competency |
| TrainingProgramCluster | Gap patterns + Competency Areas | Engineers/Managers/Partners assignment |
| Learning Objectives | Strategies + Assessment + Matrices | Gap = MAX(strategy, role req) - current |
| Training Modules | Learning Objectives | One per competency-level gap |
| Suitability Analysis | 3 matrices + inputs | Factor 1,2,3 evaluation |
| Timeline | Modules + formats + inputs | GenAI-generated milestones |

---

## Part 5: Key Decision Points

### Decision 1: Assessment Pathway
| Condition | Result |
|-----------|--------|
| SE Roles & Processes = "Defined and Established" | **High Maturity → Role-based Assessment** |
| SE Roles & Processes < "Defined and Established" | **Low Maturity → Task-based Assessment** |

**Impact:**
- High maturity: Uses Roles, Role-Process Matrix, Role-Competency Matrix
- Low maturity: Uses task descriptions, UnknownRoleProcessMatrix, UnknownRoleCompetencyMatrix

### Decision 2: Strategy Recommendation
| Condition | Primary Strategy | Additional |
|-----------|-----------------|------------|
| Low maturity | SE for Managers | + Choose 1 of 3 secondary |
| High maturity | Based on Rollout Scope | Choose 1 of 2 |
| Target Group > 100 | — | + Train the Trainer |

### Decision 3: PMT Requirement
| Condition | PMT Required |
|-----------|--------------|
| Low maturity | No (uses standard templates) |
| High maturity + Needs-based strategy | Yes |
| High maturity + Continuous Support strategy | Yes |
| High maturity + other strategies | Optional |

### Decision 4: Training Structure View
| Condition | Available Views |
|-----------|-----------------|
| Low maturity | Competency-level only |
| High maturity with defined roles | Competency-level + Role-clustered |

### Decision 5: Learning Objectives View
| Condition | Available Views |
|-----------|-----------------|
| Low maturity | Organizational view only |
| High maturity | Organizational view + Role-based view |

---

## Document Information

- **Created**: January 2026
- **Purpose**: Thesis documentation - Dependency matrix for SE-QPT data elements
- **Companion Document**: SE-QPT_Data_Element_Definitions.md
- **Application**: SE-QPT (Systems Engineering Qualification Planning Tool)
