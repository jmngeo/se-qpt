# Chapter: Conceptual Framework - ENHANCED VERSION (Verified)

> **Note**: This enhanced version has been verified against the actual codebase, database, and design documents. All information has been validated from source code.

---

## 1. SE-QPT System Overview

The Systems Engineering Qualification Planning Tool (SE-QPT) is a web-based application designed to assess organizational Systems Engineering maturity and individual competency levels, then generate personalized learning objectives to bridge competency gaps. The system implements a **four-phase** qualification planning workflow that adapts to organizational context.

[DIAGRAM OPPORTUNITY: High-level system architecture showing the four phases with inputs/outputs]

### 1.1 The Four Phases

| Phase | Name | Tasks | Results |
|-------|------|-------|---------|
| **Phase 1** | Prepare SE Training | 1. Determine current maturity level (maturity model). 2. Identify SE roles (role clusters). 3. Select SE training strategy (decision tree, strategy profile cards). | SE maturity, SE roles, SE training strategy |
| **Phase 2** | Identify Requirements and Competencies | 1. Determine necessary competencies (SE competencies, task-competency matrix). 2. Identify competency gaps (competency assessor). 3. Formulate learning objectives (learning objective templates). | Competency skill gaps, Learning objectives |
| **Phase 3** | Macro Planning | 1. Define modules. 2. Select formats (qualification format profiles, decision tree). | SE training concept |
| **Phase 4** | Micro Planning | 1. Define detailed concept (AVIVA method, concept template). | SE training detailed concept |

[Source: `SE-QPT.xlsx` - Phases sheet]

[CITATION NEEDED: Research on competency-based qualification frameworks in SE]

---

## 2. Phase 1: Prepare SE Training

Phase 1 establishes the organizational context that guides all subsequent phases. It consists of three sequential tasks:
1. Determine current maturity level (using the maturity model)
2. Identify SE roles (map to role clusters)
3. Select SE training strategy (using decision tree and strategy profile cards)

### 2.1 Task 1: SE Maturity Assessment

The maturity assessment evaluates the organization's current Systems Engineering capability across four dimensions (called "Fields of Action" in the Fraunhofer IEM framework).

[CITATION NEEDED: Fraunhofer IEM SE Maturity Model / Koenemann et al. research]

#### 2.1.1 The Four Fields of Action

| Field | ID | Description | Answer Options |
|-------|-----|-------------|----------------|
| **SE Rollout Scope** | rolloutScope | How broadly SE is deployed across the organization | 5 options (0-4) |
| **SE Processes & Roles** | seProcesses | Formalization of SE processes and role definitions | 6 options (0-5) |
| **SE Mindset** | seMindset | Cultural adoption of SE thinking | 5 options (0-4) |
| **Knowledge Base** | knowledgeBase | SE knowledge management maturity | 5 options (0-4) |

**Note**: The SE Processes & Roles dimension has the most answer options (6 levels: 0-5) because it's the primary decision driver for pathway determination.

[DIAGRAM OPPORTUNITY: Radar/spider chart showing the four dimensions]

#### 2.1.2 SE Processes & Roles Maturity Levels

This dimension is critical as it determines the Phase 2 assessment pathway:

| Value | Level Name | Description |
|-------|------------|-------------|
| 0 | Not Available | No SE processes defined |
| 1 | Ad hoc / Undefined | Informal, unstructured SE activities |
| 2 | Individually Controlled | Some individual SE practices exist |
| 3 | Defined and Established | Formally defined and documented processes |
| 4 | Quantitatively Predictable | Measured and controlled processes |
| 5 | Optimized | Continuous improvement of SE processes |

**Critical Threshold**: The maturity level (specifically the SE Processes value) determines the **pathway** for Phase 2:
- **SE Processes >= 3** (Defined and Established or higher): **Role-Based Pathway**
- **SE Processes < 3**: **Task-Based Pathway**

[Source: `pathway_determination.py`]

### 2.2 Task 2: Role Identification and Mapping

This task identifies the organization's specific roles and maps them to the 14 standard SE Role Clusters defined in the framework.

[CITATION NEEDED: "Identification of stakeholder-specific Systems Engineering competencies for industry" - Koenemann et al.]

#### 2.2.1 The 14 SE Role Clusters

| ID | Role Cluster | Description |
|----|--------------|-------------|
| 1 | Customer | Party ordering/using the product with influence on design |
| 2 | Customer Representative | Interface between customer and company |
| 3 | Project Manager | Planning, coordination, goal achievement |
| 4 | System Engineer | Requirements, decomposition, interfaces, integration |
| 5 | Specialist Developer | Domain-specific development (SW, HW, etc.) |
| 6 | Production Planner/Coordinator | Product realization preparation |
| 7 | Production Employee | Implementation, assembly, manufacture |
| 8 | Quality Engineer/Manager | Quality standards and V&V cooperation |
| 9 | V&V Operator | Verification and Validation activities |
| 10 | Service Technician | Installation, commissioning, maintenance |
| 11 | Process and Policy Manager | Internal guidelines and compliance |
| 12 | Internal Support | Advisory and support during development |
| 13 | Innovation Management | Commercial implementation, new business models |
| 14 | Management | Decision-makers, company vision and oversight |

[DIAGRAM OPPORTUNITY: Role cluster grouping or hierarchy visualization]

#### 2.2.2 AI-Powered Role Mapping

When organizations enter their specific role titles and descriptions, SE-QPT uses **OpenAI GPT-4o-mini** to intelligently map them to the SE Role Clusters.

**Mapping Process** (`role_cluster_mapping_service.py`):
1. Organization provides: Role title, description, responsibilities (optional), required skills (optional)
2. AI analyzes the role using a structured prompt with all 14 cluster definitions
3. AI returns mappings with:
   - Cluster name and ID
   - Confidence score (0-100%)
   - Reasoning for the mapping
   - Matched responsibilities
   - Primary/secondary mapping indicator

**Quality Threshold**: Only mappings with **confidence >= 80%** are accepted.

**Non-SE Role Handling**: Pure business roles (Finance, Legal, Marketing, etc.) are explicitly excluded and return empty mappings. These can be handled as "Custom Roles".

[DIAGRAM OPPORTUNITY: Role mapping process flow showing input, AI processing, and output]

#### 2.2.3 Role-Process Matrix Configuration

After roles are mapped, the **Role-Process Matrix (RPM)** must be configured for each role-cluster assignment. This matrix defines how each role is involved in each of the 30 ISO processes.

**Matrix Source** (`Matrix Design notes.md`):
- For **STANDARD** mappings (role mapped to predefined cluster): Values are copied from the reference matrix (Organization 1)
- For **CUSTOM** roles (unmapped or custom-defined): Values are initialized to 0, then generated using AI

**Involvement Levels**:
| Value | Meaning | Description |
|-------|---------|-------------|
| 0 | Not Relevant | The role does not participate in the process |
| 1 | Supporting | The role provides assistance in performing the process |
| 2 | Responsible | The role is primarily accountable for process execution |
| 3 | Designing | The role actively designs and improves the process |

**Key Point**: The Role-Process Matrix can be edited by administrators to reflect organization-specific role-process involvements. Any changes trigger automatic recalculation of the Role-Competency Matrix.

[Source: `phase1_roles.py:399-438`]

### 2.3 Task 3: Strategy Selection

Based on the maturity assessment results, SE-QPT recommends appropriate learning strategies from seven predefined options.

#### 2.3.1 The Seven Training Strategies

| ID | Strategy Name | Category | Target Audience | Description |
|----|---------------|----------|-----------------|-------------|
| 1 | **SE for Managers** | Foundational | Management/Leadership | Focuses on managers as enablers of change; understanding SE introduction and change management |
| 2 | **Common Basic Understanding** | Awareness | All stakeholders | Interdisciplinary exchange creating SE awareness through basic training and group reflection |
| 3 | **Orientation in Pilot Project** | Application | Development teams | Application-oriented qualification through SE pilot project experience |
| 4 | **Certification** | Specialization | SE specialists | Standardized training with certification (SE-Zert, CSEP, INCOSE) |
| 5 | **Continuous Support** | Sustainment | All SE employees | Self-directed, proactive learning with query documentation and answers |
| 6 | **Needs-based Project-oriented Training** | Targeted | Specific project roles | Targeted further training for specific roles with project accompaniment |
| 7 | **Train the SE-Trainer** | Multiplier | Internal trainers | Training coaches/trainers to bring SE into the company |

[Source: `strategy_selection_engine.py`]

#### 2.3.2 Strategy Selection Decision Tree

The strategy selection engine uses the following logic:

**Step 1: Evaluate Train-the-Trainer Need**
```
IF estimated_count >= 100 OR size_category in ['LARGE', 'VERY_LARGE', 'ENTERPRISE']:
    ADD train_the_trainer as SUPPLEMENTARY
```

**Step 2: Main Strategy Selection Based on Maturity**

| SE Processes Value | Primary Strategy | Reasoning |
|--------------------|-----------------|-----------|
| **<= 2** (Low maturity) | SE for Managers (PRIMARY) | Management buy-in essential for SE introduction |
| **> 2, rolloutScope <= 1** | Needs-based Project-oriented Training | Processes defined but not widely deployed |
| **> 2, rolloutScope > 1** | Continuous Support | SE widely deployed, focus on sustainment |

**Step 3: Secondary Strategy Selection (Low Maturity Only)**

When SE Processes <= 2, the user must choose a secondary strategy from:
- Common Basic Understanding
- Orientation in Pilot Project
- Certification

This is presented as a **Pro-Con Comparison** in the frontend.

[DIAGRAM OPPORTUNITY: Strategy selection decision tree flowchart]

[Source: `strategy_selection_engine.py:227-341`]

---

## 3. The Matrix Architecture

SE-QPT uses a sophisticated matrix architecture to derive role-specific competency requirements. This is the technical foundation for generating personalized learning objectives.

[DIAGRAM OPPORTUNITY: Matrix architecture overview showing three matrices and their relationships]

### 3.1 The Three Core Matrices

#### 3.1.1 Role-Process Matrix (RPM)

**Definition**: Maps each of the 14 Role Clusters to the 30 ISO Processes, indicating the involvement level of each role in each process.

**Dimensions**: 14 roles x 30 processes = 420 entries

**Value Range**: 0-3 (Not Relevant, Supporting, Responsible, Designing)

**Characteristics** (`Matrix Design notes.md`):
- Organization-specific (can vary between organizations)
- Default values from Koenemann et al.
- Editable by administrators
- Changes trigger Role-Competency Matrix recalculation

#### 3.1.2 Process-Competency Matrix (PCM)

**Definition**: Maps each of the 30 ISO Processes to the 16 SE Competencies, indicating which competencies are required to execute each process.

**Dimensions**: 30 processes x 16 competencies = 480 entries

**Value Range**: 0-2
| Value | Meaning |
|-------|---------|
| 0 | Not Useful - Competency not required for the process |
| 1 | Useful - Competency is beneficial but not essential |
| 2 | Necessary - Competency is critical for process execution |

**Characteristics**:
- **Static** - Does not vary between organizations
- Pre-filled with values from Koenemann et al.
- View-only in normal operation (not editable per organization)

#### 3.1.3 Role-Competency Matrix (RCM) - DERIVED

**Definition**: The final matrix showing the required competency levels for each role cluster.

**Dimensions**: 14 roles x 16 competencies

**Derivation Formula** (`Matrix Design notes.md`):
```
Role_Competency_Value = MAX(Role_Process_Value × Process_Competency_Value)
                        for all processes
```

This means: for each role-competency pair, find the maximum product across all processes.

**Computed Level Categories**:
| Value | Level Name | Description |
|-------|------------|-------------|
| 0 | Not Relevant | Competency not required for the role |
| 1 | Knowing | Basic awareness and familiarity required |
| 2 | Understanding | Conceptual understanding required |
| 3/4 | Applying | Practical application in work tasks |
| 6 | Mastering | Expertise and leadership in the competency |

**Automatic Updates**: The RCM is automatically recalculated when:
- Role-Process Matrix is modified
- A new organization is added

[DIAGRAM OPPORTUNITY: Visual showing RPM × PCM = RCM derivation with example]

### 3.2 The 30 ISO Processes

The system uses **30 processes** based on ISO/IEC 15288:2015, organized into 4 lifecycle process groups:

[CITATION NEEDED: ISO/IEC/IEEE 15288:2015 Systems and software engineering - System life cycle processes]

#### Agreement Processes (2 processes)
| ID | Process Name |
|----|--------------|
| 1 | Acquisition process |
| 2 | Supply process |

#### Organizational Project-Enabling Processes (5 processes)
| ID | Process Name |
|----|--------------|
| 3 | Life Cycle Model Management process |
| 4 | Infrastructure Management process |
| 5 | Portfolio Management process |
| 6 | Human Resource Management process |
| 7 | Quality Management process |
| 8 | Knowledge Management process |

#### Technical Management Processes (8 processes)
| ID | Process Name |
|----|--------------|
| 9 | Project Planning process |
| 10 | Project Assessment and Control process |
| 11 | Decision Management process |
| 12 | Risk Management process |
| 13 | Configuration Management process |
| 14 | Information Management process |
| 15 | Measurement process |
| 16 | Quality Assurance process |

#### Technical Processes (14 processes)
| ID | Process Name |
|----|--------------|
| 17 | Business or Mission Analysis process |
| 18 | Stakeholder Needs and Requirements Definition process |
| 19 | System Requirements Definition process |
| 20 | System Architecture Definition process |
| 21 | Design Definition process |
| 22 | System Analysis process |
| 23 | Implementation process |
| 24 | Integration process |
| 25 | Verification process |
| 26 | Transition process |
| 27 | Validation process |
| 28 | Operation process |
| 29 | Maintenance process |
| 30 | Disposal process |

[Source: `align_iso_processes.py`]

[DIAGRAM OPPORTUNITY: Process categories diagram with groupings]

### 3.3 The 16 SE Competencies

The competencies are organized into four categories:

[CITATION NEEDED: INCOSE SE Competency Framework; Koenemann et al.]

#### Core Competencies (4)
| ID | Competency Name | Description |
|----|-----------------|-------------|
| 1 | Systems Thinking | Apply fundamental concepts of systems thinking and understand the system's role in overall context |
| 4 | Lifecycle Consideration | Consider all lifecycle phases in requirements, architectures, and designs |
| 5 | Customer / Value Orientation | Place agile values and customer benefits at the center of development |
| 6 | Systems Modelling and Analysis | Provide precise data using cross-domain models for decision-making |

#### Social / Personal Competencies (3)
| ID | Competency Name | Description |
|----|-----------------|-------------|
| 7 | Communication | Communicate constructively across domains while maintaining relationships |
| 8 | Leadership | Select goals, negotiate, and efficiently achieve them with a team |
| 9 | Self-Organization | Organize oneself and manage tasks independently |

#### Management Competencies (4)
| ID | Competency Name | Description |
|----|-----------------|-------------|
| 10 | Project Management | Plan, coordinate, and adapt activities to deliver quality systems on time and budget |
| 11 | Decision Management | Identify and evaluate alternatives in structured analytical manner |
| 12 | Information Management | Deliver right information at right time with appropriate security |
| 13 | Configuration Management | Design system functions and properties consistently across lifecycle |

#### Technical Competencies (5)
| ID | Competency Name | Description |
|----|-----------------|-------------|
| 14 | Requirements Definition | Analyze stakeholder needs and derive system requirements |
| 15 | System Architecting | Define system elements, hierarchy, interfaces, and behavior |
| 16 | Integration, Verification, Validation | Integrate elements and provide evidence of requirement fulfillment |
| 17 | Operation and Support | Commission, operate, and maintain system capabilities |
| 18 | Agile Methods | Apply methods supporting agile values and parallel work |

**Note**: IDs 2 and 3 are not used (possibly deprecated in the original framework).

[Source: `db_export.sql` competency table]

### 3.4 The Competency Pyramid Levels

Competencies are assessed and developed according to a **pyramid structure** with specific valid levels:

[CITATION NEEDED: Bloom's Taxonomy of Educational Objectives; INCOSE competency levels]

**Valid Pyramid Levels**: 0, 1, 2, 4, 6 (levels 3 and 5 are NOT used)

| Level | Short Name | Full Name | Description |
|-------|------------|-----------|-------------|
| 0 | Not Relevant | - | Competency not required |
| 1 | Knowing | Performing Basics | Can recognize and recall concepts |
| 2 | Understanding | Performing Appropriately | Can explain concepts and apply in simple situations |
| 4 | Applying | Shaping Adequately | Can apply knowledge in complex situations |
| 6 | Mastering | Mastering SE | Can evaluate, improve, and teach the competency |

**Survey Question Groups** (mapping to levels):
- Group 1 indicators -> Level 1 (Knowing)
- Group 2 indicators -> Level 2 (Understanding)
- Group 3 indicators -> Level 4 (Applying)
- Group 4 indicators -> Level 6 (Mastering)
- "None" option -> Level 0

[DIAGRAM OPPORTUNITY: Pyramid visualization showing levels 1, 2, 4, 6]

[Source: `learning_objectives_core.py:50` - `VALID_LEVELS = [1, 2, 4, 6]`]

---

## 4. Phase 2: Identify Requirements and Competencies

Phase 2 identifies competency requirements and gaps using one of two pathways determined by Phase 1 maturity level. It consists of three tasks:
1. Determine necessary competencies (using SE competencies, task-competency matrix)
2. Identify competency gaps (using the competency assessor)
3. Formulate learning objectives (using learning objective templates)

### 4.1 Pathway Determination

**The Decision Logic** (`pathway_determination.py`):
```
IF se_processes_maturity >= 3 (Defined and Established or higher):
    pathway = ROLE_BASED
    reason = "Organization has formally defined SE processes and roles"
ELSE:
    pathway = TASK_BASED
    reason = "Organization lacks formal role definitions"
```

[DIAGRAM OPPORTUNITY: Pathway determination decision tree]

### 4.2 Role-Based Pathway (High Maturity)

Used when SE Processes maturity >= 3.

#### 4.2.1 Assessment Approach

1. **User Selection**: User selects their organizational role from the mapped roles
2. **Role Mapping**: System retrieves the SE Role Cluster mapping for that role
3. **Competency Requirements**: System retrieves required competencies from the Role-Competency Matrix
4. **Self-Assessment Survey**: User completes the competency questionnaire

#### 4.2.2 Three-Way Validation

The role-based pathway performs **three-way validation**:
1. **Role Requirements** (from RCM)
2. **Strategy Target** (from selected strategies)
3. **User's Current Level** (from survey)

Gap = MAX(role_requirement, strategy_target) - current_level

[Source: `role_based_pathway_fixed.py`]

### 4.3 Task-Based Pathway (Low Maturity)

Used when SE Processes maturity < 3.

#### 4.3.1 Assessment Approach (`task_based_pathway.py`)

Since formal roles may not exist, this pathway assesses based on actual tasks performed:

1. **Task Input**: User describes tasks in three categories:
   - Tasks they are **responsible for** (ownership) -> Value 2
   - Tasks they **support** (contribute to) -> Value 1
   - Tasks they **design** (define processes for) -> Value 3

2. **AI Task Analysis**: OpenAI GPT-4 analyzes the described tasks and maps them to the 30 ISO Processes with involvement levels

3. **Dynamic Matrix Creation**: System creates a "personal role-process matrix" for this user based on their task descriptions

4. **Competency Derivation**: Uses the same matrix multiplication to derive competency requirements

5. **Self-Assessment Survey**: Same questionnaire as role-based pathway

#### 4.3.2 Algorithm Difference

**Task-Based**: 2-Way Comparison
- Current Level (median of users) vs Strategy Target (from archetype)
- NO role requirements (organization has no roles defined)
- Simpler decision logic

**Role-Based**: 3-Way Comparison
- Current Level vs Role Requirements vs Strategy Target

### 4.4 The Competency Assessment Survey

The survey consists of **competency indicators** organized by level. For each of the 16 competencies, there are 4 levels of indicators.

**Survey Structure**:
- 16 competencies × 4 indicators per competency = 64 indicator questions
- Each indicator corresponds to a level (1, 2, 4, or 6)
- Users select the highest level they can perform

[Source: `db_export.sql` competency_indicators table]

---

## 5. Learning Objectives Generation (Phase 2, Task 3)

After competency gaps are identified, SE-QPT generates personalized learning objectives.

### 5.1 Design Principles (`learning_objectives_core.py`)

1. **ANY Gap Triggers Generation**: If current < target for any competency, LOs are generated
2. **Progressive Levels**: Generate objectives for intermediate levels, not just the target
3. **TTT Separation**: Train the Trainer objectives are handled separately
4. **Pyramid Structure**: Output organized by the 4 valid levels (1, 2, 4, 6)
5. **Caching**: Results cached using input hash to avoid redundant AI calls

### 5.2 Gap Detection Algorithm

For each competency:
```python
current_level = user's survey response (median for org-level)
target_level = MAX(role_requirement, strategy_template_target)
gap = target_level - current_level
if gap > 0:
    generate_learning_objectives()
```

### 5.3 Progressive Level Generation

Instead of jumping directly to the target level, SE-QPT generates LOs for intermediate levels:

```python
VALID_LEVELS = [1, 2, 4, 6]

def get_levels_to_generate(current, target):
    return [level for level in VALID_LEVELS
            if level > current and level <= target]
```

**Example**:
- Current: 1, Target: 6
- Generates LOs for: Level 2, Level 4, Level 6

### 5.4 PMT Context Integration

Organizations can provide **Process, Methods, and Tools (PMT)** context to customize learning objectives:

**PMT Fields**:
- **Processes**: Organization-specific process names and standards
- **Methods**: Methodologies used (Agile, SAFe, V-Model, etc.)
- **Tools**: Specific tools (DOORS, Jira, Cameo, etc.)
- **Industry**: Industry sector for domain relevance
- **Additional Context**: Free-form organizational context

**How PMT Affects LO Generation**:
The PMT context is used to customize the generated learning objective text via LLM:
- Reference organization-specific tools
- Align with industry standards
- Use appropriate terminology

[DIAGRAM OPPORTUNITY: Learning objectives generation pipeline]

### 5.5 Train the Trainer (TTT) Special Handling

When "Train the SE-Trainer" strategy is selected:
- Target is always Level 6 (Mastering SE)
- TTT objectives are separated from main strategy objectives
- Used for building internal training capacity

---

## 6. Phase 3: Macro Planning

Phase 3 creates the SE training concept by defining modules and selecting appropriate learning formats.

**Note**: Phase 3 is currently in design phase based on meeting notes from 11-12-2025.

### 6.1 Phase 3 Tasks

**Task 1: Define Modules**
- Modules are derived from Phase 2 learning objectives (one per competency level)
- Modules can be separated by Method and Tool if applicable (based on PMT breakdown)

**Task 2: Select Formats**
- Select appropriate learning formats for each module
- Format recommendations based on qualification format profiles and decision tree
- Considers group size, competency-format suitability, distribution patterns

### 6.2 The 10 Learning Formats (from Sachin's Thesis)

[CITATION NEEDED: Sachin's thesis on learning formats]

The system uses 10 predefined learning formats with attributes like:
- Advantages and disadvantages
- Suitable group sizes
- Effort metrics (content creation, per training)
- Level suitability

### 6.3 Learning Format Recommendation Inputs

**From Phase 1**:
- Selected training strategy
- Training group size

**From Phase 2**:
- Gap data per user per competency per level
- Aggregated gap counts
- Learning objectives (already generated)
- Role-user mappings

**From Reference Knowledge**:
- Competency-Format Matrix (C_Co-LF)
- Strategy-Format Matrix
- Format-Level Suitability Matrix

### 6.4 Format Recommendation Algorithm Design

**Step 1**: Aggregate gap data (count users per level per competency)

**Step 2**: Analyze distribution patterns (uniform, bimodal, skewed)

**Step 3**: Filter formats by level
- If target = Level 4 (Applying): Exclude WBT, CBT, Self-Learning
- Levels 1-2: All formats eligible

**Step 4**: Score and rank formats based on:
- User count appropriateness (30%)
- Distribution pattern match (25%)
- Competency-format score from matrix (25%)
- Other factors (20%)

**Step 5**: Generate rationale for recommendations

[DIAGRAM OPPORTUNITY: Phase 3 architecture and recommendation flow]

---

## 7. Phase 4: Micro Planning

Phase 4 creates the detailed SE training concept using the AVIVA method and concept templates.

**Note**: Phase 4 is currently in design phase.

### 7.1 Phase 4 Tasks

**Task 1: Define Detailed Concept**
- Use AVIVA method for training design
- Apply concept templates
- Create detailed training materials and schedules

### 7.2 AVIVA Method

[CITATION NEEDED: AVIVA method for training concept design]

The AVIVA method provides a structured approach for designing detailed training concepts:
- **A**nkommen (Arrival) - Introduction and orientation
- **V**orwissen aktivieren (Activate prior knowledge) - Connect to existing knowledge
- **I**nformieren (Inform) - Present new content
- **V**erarbeiten (Process) - Apply and practice
- **A**uswerten (Evaluate) - Reflect and assess

[DIAGRAM OPPORTUNITY: AVIVA method phases for training design]

---

## 8. Technology Architecture

### 8.1 Technology Stack

**Backend**:
- Python Flask web framework
- PostgreSQL database
- SQLAlchemy ORM
- OpenAI API (GPT-4o-mini for role mapping, GPT-4 for task analysis)

**Frontend**:
- Vue.js 3 with Composition API
- Vuetify 3 component framework
- Pinia state management

**Deployment**:
- Docker containerization
- DigitalOcean cloud hosting
- Nginx reverse proxy

### 8.2 Key Services

| Service | File | Responsibility |
|---------|------|----------------|
| MaturityCalculator | `MaturityCalculator.js` | Phase 1 maturity score calculation |
| StrategySelectionEngine | `strategy_selection_engine.py` | Strategy recommendation logic |
| RoleClusterMappingService | `role_cluster_mapping_service.py` | AI-powered role mapping |
| PathwayDetermination | `pathway_determination.py` | ROLE vs TASK pathway selection |
| LearningObjectivesCore | `learning_objectives_core.py` | LO generation algorithms |
| TaskBasedPathway | `task_based_pathway.py` | Low-maturity assessment pathway |
| RoleBasedPathway | `role_based_pathway_fixed.py` | High-maturity assessment pathway |

---

## 9. Key Data Relationships

```
Organization
    ├── OrganizationRoles (mapped to RoleClusters)
    │       └── RoleProcessMatrix (per role, per process)
    │               └── RoleCompetencyMatrix (derived)
    │
    ├── UserAssessments
    │       ├── survey_type: 'selected_roles' | 'unknown_roles'
    │       └── UserCompetencySurveyResults
    │
    ├── LearningStrategies (selected from 7)
    │       └── StrategyTemplateCompetencies (target levels)
    │
    └── PMTContext (optional customization)

Global Tables (shared across organizations):
    ├── RoleClusters (14)
    ├── IsoProcesses (30)
    ├── Competencies (16)
    ├── ProcessCompetencyMatrix (30 × 16)
    └── CompetencyIndicators (4 per competency)
```

[DIAGRAM OPPORTUNITY: Entity-Relationship diagram]

---

## 10. Summary of Diagram Opportunities

1. High-level system architecture (4 phases)
2. Four Fields of Action radar chart
3. Role cluster grouping visualization
4. Role mapping process flow (AI-powered)
5. Strategy selection decision tree
6. Matrix architecture (RPM × PCM = RCM)
7. Matrix derivation example with calculations
8. 30 ISO processes grouped by category
9. Competency pyramid (levels 1, 2, 4, 6)
10. Pathway determination decision tree
11. Learning objectives generation pipeline
12. Phase 3 format recommendation flow
13. Phase 4 AVIVA method phases
14. Entity-Relationship diagram
15. Service architecture dependencies

---

## 11. Topics Requiring Research Citations

### Primary Citations
1. **Fraunhofer IEM SE Framework** - Koenemann et al.
2. **INCOSE SE Competency Framework** - Industry standard
3. **ISO/IEC 15288:2015** - System life cycle processes
4. **Bloom's Taxonomy** - Educational objectives classification

### Supporting Citations
5. **Sachin's Thesis** - Learning formats and matrices
6. **CMMI Model** - Maturity model parallels
7. **Adult Learning Theory** (Andragogy)
8. **Competency-Based Education** frameworks

### Methodological Citations
9. **Self-Assessment Validity** research
10. **LLM/AI in Education** applications
11. **Training Needs Analysis** frameworks

---

## 12. Verification Notes

This document has been verified against:
- `data/source/excel/SE-QPT.xlsx` - 4 phases, strategies, roles, maturity levels
- `src/backend/app/strategy_selection_engine.py` - 7 strategies and decision logic
- `src/backend/setup/populate/align_iso_processes.py` - 30 ISO processes
- `src/backend/setup/populate/populate_competencies.py` - 16 competencies
- `src/backend/app/services/learning_objectives_core.py` - Pyramid levels [1,2,4,6]
- `src/backend/app/services/pathway_determination.py` - Pathway logic
- `data/Meeting notes/Matrix Design notes.md` - Matrix architecture
- `db_export.sql` - Database structure verification
- Meeting notes 11-12-2025 - Phase 3/4 design

*Document verified: December 2025*
