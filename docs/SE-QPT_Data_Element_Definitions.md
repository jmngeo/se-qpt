# SE-QPT Data Element Definitions

## Overview

This document provides comprehensive definitions for all key data elements used in the SE-QPT (Systems Engineering Qualification Planning Tool) application. These elements are interconnected and form the foundation of the qualification planning process across four phases.

**Source References:**
- 14 SE Role Clusters: Könemann et al.
- 16 SE Competencies: Extended INCOSE Competency Framework (Könemann et al.)
- 10 Learning Formats: Sachin Kumar Master Thesis (2023)

---

## Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| SE | Systems Engineering |
| QPT | Qualification Planning Tool |
| LO | Learning Objectives |
| PMT | Processes, Methods, Tools |
| WBT | Web-Based Training |
| CBT | Computer-Based Training |
| V&V | Verification and Validation |
| ISO | International Organization for Standardization |
| INCOSE | International Council on Systems Engineering |
| GenAI | Generative Artificial Intelligence |
| RAG | Retrieval-Augmented Generation |

---

## SECTION A: FOUNDATIONAL ENTITIES

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 1 | **Organization** | The company/entity for which the SE Qualification Plan is being generated. Root entity that owns all other data. | Name, public key, size (small/medium/large/enterprise) | Setup | All Phases |
| 2 | **User** | Individuals interacting with the system. Two types exist with different permissions and workflows. | Types: **Admin** (performs all phases/tasks), **Employee** (performs competency assessment only) | Setup | Phase 1, Phase 2, Phase 3, Phase 4 |

---

## SECTION B: MATURITY ASSESSMENT (Phase 1 - Task 1)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 3 | **Organization's SE Maturity** | A weighted score representing the organization's current Systems Engineering capability level, calculated from 4 fields of action. Determines whether the organization follows the Role-based (high maturity) or Task-based (low maturity) assessment pathway. | **Score**: 0-100 (weighted calculation with balance penalty)<br>**Levels**: 1=Initial, 2=Developing, 3=Defined, 4=Managed, 5=Optimized<br>**Pathway Threshold**: SE Roles & Processes are "Defined and Established" = High maturity pathway | Phase 1 | Phase 1 (Strategy selection, Role Mapping), Phase 2 (Pathway determination, Learning Objectives results view toggle between Organizational View and Role-Based View), Phase 3 (View availability) |
| 4 | **4 Fields of Action** | The four input dimensions used to calculate Organization's SE Maturity. Each field has different weights reflecting its importance. | **Rollout Scope** (weight: 0.20, values: 0-4)<br>**SE Roles & Processes** (weight: 0.35, values: 0-5) - Primary pathway determinant<br>**SE Mindset** (weight: 0.25, values: 0-4)<br>**Knowledge Base** (weight: 0.20, values: 0-4) | Phase 1 | Phase 1 (Maturity calculation) |
| 5 | **Training Target Group Size** | The total number of employees in the organization who will participate in the SE training program. Used for scaling participant counts and strategy recommendations. | Integer (e.g., 50, 100, 500)<br>If >100, triggers "Train the Trainer" recommendation | Phase 1 | Phase 1 (Strategy selection), Phase 3 (Participant scaling) |

---

## SECTION C: ROLE FRAMEWORK (Phase 1 - Task 2)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 6 | **Roles (Organization Roles)** | Custom job roles defined by the organization that will participate in SE training. For high maturity organizations, these are mapped to standard SE Role Clusters. For low maturity, roles are not formally defined (task-based path used instead). | Role name, description, identification method (STANDARD/CUSTOM) | Phase 1 | Phase 1 (Matrix definition), Phase 2 (Role-based assessment, Learning Objectives), Phase 3 (Role clustering) |
| 7 | **14 SE Role Clusters** | Reference taxonomy of standard Systems Engineering roles from Könemann et al. Used to map organization roles to standardized SE role definitions for baseline matrix values. Roles without a match are marked as CUSTOM. | 1=Customer, 2=Customer Representative, 3=Project Manager, 4=System Engineer, 5=Specialist Developer, 6=Production Planner/Coordinator, 7=Production Employee, 8=Quality Engineer/Manager, 9=Verification and Validation (V&V) Operator, 10=Service Technician, 11=Process and Policy Manager, 12=Internal Support, 13=Innovation Management, 14=Management | Reference Data | Phase 1 (Role mapping, baseline matrix derivation) |
| 8 | **TrainingProgramCluster** | Groups of roles organized by their training needs and competency gap patterns. Used to structure training delivery in Phase 3 for role-clustered view. | **3 clusters**:<br>1=**SE for Engineers** (roles needing Level 4+ in Technical/Core areas)<br>2=**SE for Managers** (roles needing Level 4+ only in Social/Personal or Management areas)<br>3=**SE for Interfacing Partners** (roles needing only Level 1-2 competencies) | Phase 2 (Calculated) | Phase 3 (Role-clustered training structure) |

---

## SECTION D: COMPETENCY FRAMEWORK

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 9 | **Competency** | The 16 core Systems Engineering competencies from the Extended INCOSE Competency Framework (Könemann et al.) that form the basis of all assessments and training objectives. | **Core**: Systems Thinking, Lifecycle Consideration, Customer/Value Orientation, Systems Modelling and Analysis<br>**Social/Personal**: Communication, Leadership, Self-Organization<br>**Management**: Project Management, Decision Management, Information Management, Configuration Management<br>**Technical**: Requirements Definition, System Architecting, Integration Verification Validation, Operation and Support, Agile Methods | Reference Data | Phase 2, Phase 3 |
| 10 | **Competency Areas** | Four categories that group the 16 competencies by their nature. Used for TrainingProgramCluster assignment logic. | **Core** (fundamental SE thinking)<br>**Technical** (engineering methods)<br>**Management** (project/organizational)<br>**Social/Personal** (soft skills, leadership) | Reference Data | Phase 2 (Cluster assignment) |
| 11 | **Competency Levels** | Proficiency levels for each competency, representing depth of knowledge/skill. Used throughout the system for assessments, targets, and gap calculations. | **0** = Not required/Not assessed<br>**1** = Knowing (basic awareness)<br>**2** = Understanding (comprehension)<br>**4** = Applying (practical application)<br>**6** = Mastering (expert level)<br>*Note: Levels 3 and 5 are intentionally skipped* | Reference Data | All competency-related calculations |
| 12 | **CompetencyIndicator** | Observable behavioral indicators that describe what a person at a specific competency level can do. Provides concrete descriptions for assessment and training design. | Indicator text per competency per level (bilingual: EN/DE)<br>Levels: kennen (knowing), verstehen (understanding), anwenden (applying), beherrschen (mastering) | Reference Data | Phase 2 (Assessment guidance), Training design |

---

## SECTION E: PROCESS FRAMEWORK (ISO/IEC 15288)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 13 | **ISO Processes** | The approximately 30 Systems Engineering processes defined in ISO/IEC 15288:2015 standard. Forms the basis for defining role involvement and deriving competency requirements. | 30 processes grouped into 4 life cycle categories:<br>- Agreement Processes<br>- Organizational Processes<br>- Technical Processes<br>- Project Processes | Reference Data | Phase 1 (Role-Process Matrix), Phase 2 (Task-based analysis) |

---

## SECTION F: MATRIX RELATIONSHIPS (Phase 1 - Task 2)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 14 | **Role-Process Matrix** | Defines the involvement level of each organization role in each of the 30 ISO processes. For STANDARD roles, baseline values are derived from the SE Role Cluster template. For CUSTOM roles, GenAI generates baseline values based on role description. | **Values per cell**:<br>0 = Not Involved<br>1 = Supports<br>2 = Responsible<br>3 = Designs | Phase 1 | Phase 1 (Input), Phase 2 (Role-Competency calculation) |
| 15 | **Process-Competency Matrix** | A global standardized matrix defining which competencies are required for each ISO process and at what level. Shared across all organizations. Only actively used when organization has high SE maturity (defined roles and processes). | **Values per cell**:<br>0 = Not relevant<br>1 = Useful<br>2 = Necessary | Reference Data (Global) | Phase 2 (Role-Competency calculation) |
| 16 | **Role-Competency Matrix** | Computed matrix showing the required competency levels for each organization role. Automatically calculated from Role-Process Matrix × Process-Competency Matrix. | **Formula**: For each role-competency pair:<br>`role_competency_value = MAX(role_process_value × process_competency_value)`<br>aggregated across all processes<br><br>**Product Mapping**:<br>0→0, 1→1, 2→2, 3→4, 4→4, 6→6<br><br>**Output Values**: 0, 1, 2, 4, 6 | Phase 1 (Calculated) | Phase 2 (Role-based assessment - required levels) |
| 17 | **UnknownRoleProcessMatrix** | For task-based assessment (low maturity orgs): stores the user's involvement levels in ISO processes, derived from their task descriptions using RAG-based GenAI analysis. | **Values per cell**:<br>0 = Not performing<br>1 = Supporting<br>2 = Responsible<br>3 = Designing<br>*Indexed by username, not role ID* | Phase 2 | Phase 2 (Task-based competency calculation) |
| 18 | **UnknownRoleCompetencyMatrix** | For task-based assessment: computed competency requirements for users with undefined roles. Calculated from UnknownRoleProcessMatrix × Process-Competency Matrix using the same formula as Role-Competency Matrix. | **Values**: 0, 1, 2, 4, 6<br>*Indexed by username* | Phase 2 (Calculated) | Phase 2 (Task-based assessment - required levels) |

---

## SECTION G: QUALIFICATION STRATEGIES (Phase 1 - Task 3)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 19 | **Qualification/Training Strategies** | The 7 predefined qualification approaches that define training goals and competency targets. Selection depends on maturity level and rollout scope. Organizations select primary (and optionally secondary) strategies. | **7 Strategies**:<br>1=Common Basic Understanding<br>2=SE for Managers<br>3=Orientation in Pilot Project<br>4=Needs-based, Project-oriented Training<br>5=Continuous Support<br>6=Train the Trainer<br>7=Certification<br><br>**Selection Logic**:<br>- Low maturity: "SE for Managers" as primary + choose 1 of 3 secondary<br>- High maturity: Choose 1 of 2 based on rollout scope<br>- If Training Target Group >100: Also recommend "Train the Trainer" | Phase 1 | Phase 2 (Target levels for LO), Phase 3 (Strategy-Format consistency) |
| 20 | **Learning Objectives Templates (StrategyTemplateCompetency)** | Predefined target competency levels for each strategy. Contains 112 entries (7 strategies × 16 competencies). Some entries include Process-Method-Tool distinct learning objective templates. | Matrix of strategy × competency → target level (0-6)<br>Optional PMT-specific templates for certain competencies | Reference Data | Phase 2 (Learning Objectives generation) |

---

## SECTION H: COMPETENCY ASSESSMENT (Phase 2 - Task 1)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 21 | **Competency Assessment** | The process where users self-assess their current competency levels. Two pathways exist based on organization maturity. Results are used to identify gaps. | **Role-based** (high maturity): User selects their role(s), required competencies derived from Role-Competency Matrix<br>**Task-based** (low maturity): User describes tasks with involvement levels (Support, Responsible, Design), system uses GenAI to map to processes, required competencies derived from UnknownRoleCompetencyMatrix | Phase 2 | Phase 2 (Gap identification), Phase 3 (Modules) |

---

## SECTION I: LEARNING OBJECTIVES (Phase 2 - Tasks 2 & 3)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 22 | **Existing Training Check** | Input mechanism for identifying competencies and their specific levels where the organization already has training offerings. These are excluded from Learning Objectives generation to avoid duplication. | Competency ID + covered levels array (e.g., competency 5 has training for levels [1, 2]) | Phase 2 | Phase 2 (LO exclusion), Phase 3 (Module exclusion) |
| 23 | **PMT (Processes, Methods, Tools)** | Organization-specific SE practices context used to customize learning objectives. Extracted from organization documentation using GenAI. Only required for high maturity orgs with certain strategies (Needs-based, Continuous Support). | **Processes**: e.g., "ISO 26262, ASPICE"<br>**Methods**: e.g., "Scrum, V-Model"<br>**Tools**: e.g., "DOORS, JIRA" | Phase 2 | Phase 2 (LO customization via GenAI) |
| 24 | **Learning Objectives** | Generated training requirements based on competency gaps. For each identified competency-level gap, a learning objective is generated using templates and (optionally) PMT customization. | **High maturity**: Gap = MAX(strategy target, role requirement) - current level. Generated per role if any role has gap.<br>**Low maturity**: Gap = strategy target - current level. Generated organizationally.<br>**Exclusion**: Levels with existing training are excluded.<br>**Structure**: Pyramid of levels [1,2,4,6] per competency | Phase 2 | Phase 3 (Training Modules) |

---

## SECTION J: MACRO PLANNING (Phase 3)

| # | Element | Definition | Valid Values / Structure | Phase Defined | Used In |
|---|---------|------------|--------------------------|---------------|---------|
| 25 | **Training Structure** | The organizational view for presenting training modules. High maturity organizations can choose between two views; low maturity organizations only have one option. | **Competency-level based**: Modules organized by competency and level<br>**Role-clustered based**: Modules organized by TrainingProgramCluster (only available for high maturity orgs with defined roles) | Phase 3 | Phase 3 (Module presentation) |
| 26 | **Training Modules** | Individual training units, one per competency-level gap identified in Learning Objectives. Each module requires a learning format selection. | Module = Competency + Target Level + (optional) PMT type<br>Contains: participant count, gap data, format selection | Phase 3 | Phase 3 (Format selection, Timeline) |
| 27 | **Learning Formats** | The 10 delivery formats available for training modules (from Sachin Kumar thesis). Each format has specific characteristics affecting its suitability for different competencies and participant counts. | **10 Formats**:<br>1=Seminar/Instructor Lead Training<br>2=Webinar/Live Online Event<br>3=Coaching<br>4=Mentoring<br>5=Web-Based Training (WBT)<br>6=Computer-Based Training (CBT)<br>7=Game-Based Learning<br>8=Conference<br>9=Blended Learning<br>10=Self-Learning<br><br>**Attributes per format**: mode of delivery, communication type, collaboration type, participant min/max, max level achievable, effort metrics, advantages, disadvantages, SE relevance | Reference Data | Phase 3 (Format selection) |
| 28 | **StrategyLearningFormatMatrix** | Defines the consistency/fit between each strategy and each learning format. Used in suitability analysis Factor 3. | **Values**:<br>++ = Highly Recommended<br>+ = Partly Recommended<br>-- = Not Consistent<br><br>Matrix: 7 strategies × 10 formats = 70 entries | Reference Data | Phase 3 (Suitability Factor 3: Strategy Fit) |
| 29 | **CompetencyLearningFormatMatrix** | Defines the maximum competency level achievable through each learning format for each competency. Used in suitability analysis Factor 2. | **Values**: 0 (not suitable), 1, 2, 4, 6<br>Matrix: 16 competencies × 10 formats = 160 entries | Reference Data | Phase 3 (Suitability Factor 2: Level Achievable) |
| 30 | **Suitability Analysis (3 Factors)** | Evaluation of learning format appropriateness for a training module, based on three parameters. | **Factor 1**: Participant Count - Can format accommodate the scaled participant count? (derived from roles with gaps × Training Target Group Size scaling)<br>**Factor 2**: Level Achievable - Can format achieve the target competency level? (from CompetencyLearningFormatMatrix)<br>**Factor 3**: Strategy Fit - Is format consistent with selected strategy? (from StrategyLearningFormatMatrix)<br><br>**Status per factor**: Green/Yellow/Red | Phase 3 | Phase 3 (Format selection guidance) |
| 31 | **Timeline** | GenAI-generated implementation schedule with milestones for the training program. | **Inputs**: Module count, Training Target Group Size, selected strategies, learning formats selected<br>**Outputs**: Milestones with dates, phases, dependencies | Phase 3 | Phase 3 (Final output) |

---

## SUMMARY

| Category | Count | Elements |
|----------|-------|----------|
| Foundational Entities | 2 | Organization, User |
| Maturity Assessment | 3 | SE Maturity, 4 Fields of Action, Training Target Group Size |
| Role Framework | 3 | Roles, 14 SE Role Clusters, TrainingProgramCluster |
| Competency Framework | 4 | Competency, Competency Areas, Competency Levels, CompetencyIndicator |
| Process Framework | 1 | ISO Processes |
| Matrix Relationships | 5 | Role-Process Matrix, Process-Competency Matrix, Role-Competency Matrix, UnknownRoleProcessMatrix, UnknownRoleCompetencyMatrix |
| Qualification Strategies | 2 | Strategies, Learning Objectives Templates |
| Competency Assessment | 1 | Competency Assessment |
| Learning Objectives | 3 | Existing Training Check, PMT, Learning Objectives |
| Macro Planning | 7 | Training Structure, Training Modules, Learning Formats, StrategyLearningFormatMatrix, CompetencyLearningFormatMatrix, Suitability Analysis, Timeline |
| **TOTAL** | **31** | |

---

## Document Information

- **Created**: January 2026
- **Purpose**: Thesis documentation - Dependency matrix foundation
- **Application**: SE-QPT (Systems Engineering Qualification Planning Tool)
