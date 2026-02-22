# SE-QPT Application Report
## Systems Engineering Qualification Planning Tool - Comprehensive Documentation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Big Picture Overview](#2-big-picture-overview)
3. [Technology Stack and Architecture](#3-technology-stack-and-architecture)
4. [User Journey: From Login to Results](#4-user-journey-from-login-to-results)
5. [Phase 1: Prepare SE Training](#5-phase-1-prepare-se-training)
6. [Phase 2: Identify Requirements and Competencies](#6-phase-2-identify-requirements-and-competencies)
7. [Phase 3: Macro Planning](#7-phase-3-macro-planning)
8. [Phase 4: Detailed Implementation](#8-phase-4-detailed-implementation)
9. [Database Schema](#9-database-schema)
10. [Data Sources and Reference Data](#10-data-sources-and-reference-data)
11. [API Endpoints](#11-api-endpoints)
12. [Appendix: Key Files Reference](#12-appendix-key-files-reference)

---

## 1. Executive Summary

The **SE-QPT (Systems Engineering Qualification Planning Tool)** is a web-based application designed to help organizations assess and plan competency development for Systems Engineering roles. The tool is based on the **ISO/IEC/IEEE 15288** systems engineering standards and incorporates research from INCOSE (International Council on Systems Engineering).

### Purpose

The application serves two primary user types:
1. **Organization Administrators**: Set up and configure the SE training framework for their organization
2. **Employees**: Complete competency assessments and receive personalized training recommendations

### Core Capabilities

- **Maturity Assessment**: Evaluate organizational SE maturity across four key dimensions
- **Role Identification**: Map organization-specific roles to 14 standard SE role clusters
- **Strategy Selection**: Choose from 7 proven qualification strategies based on maturity level
- **Competency Assessment**: Assess individual competency levels against 16 core SE competencies
- **Learning Objectives Generation**: AI-powered generation of personalized learning objectives
- **Training Planning**: Create comprehensive qualification plans with module selection

---

## 2. Big Picture Overview

### 2.1 What is SE-QPT?

SE-QPT is a qualification planning platform that bridges the gap between organizational SE maturity and individual competency development. It follows a structured, phase-based approach:

```
+------------------+     +------------------+     +------------------+     +------------------+
|    Phase 1       | --> |    Phase 2       | --> |    Phase 3       | --> |    Phase 4       |
| Prepare Training |     | Assess Competency|     | Macro Planning   |     | Implementation   |
+------------------+     +------------------+     +------------------+     +------------------+
       |                        |                        |                        |
  - Maturity           - Role Selection          - Gap Analysis          - Cohort Formation
  - Roles              - Self-Assessment         - Module Selection      - Scheduling
  - Strategy           - Results & LOs           - Format Optimization   - Tracking
```

### 2.2 The 3-Matrix System

The core of SE-QPT is built on a **3-Matrix System** that connects roles, processes, and competencies:

```
Matrix 1: ROLE_PROCESS_MATRIX           Matrix 2: PROCESS_COMPETENCY_MATRIX
(14 Roles x 28 ISO Processes)           (28 ISO Processes x 16 Competencies)
  - Values: 0-4 (involvement level)       - Values: 0-1 (binary requirement)
  - Customizable per organization         - Based on ISO/IEC/IEEE 15288 standards
                    \                             /
                     \                           /
                      v                         v
                Matrix 3: ROLE_COMPETENCY_MATRIX
                (14 Roles x 16 Competencies)
                  - Values: 0-6 (required proficiency level)
                  - Auto-calculated from Matrix 1 x Matrix 2
```

### 2.3 The 16 Core SE Competencies

SE-QPT assesses individuals against 16 core Systems Engineering competencies, organized into four areas:

| Area | Competencies |
|------|-------------|
| **Core** (4) | Systems Thinking, Lifecycle Consideration, Customer/Value Orientation, Systems Modelling and Analysis |
| **Social/Personal** (3) | Communication, Leadership, Self-Organization |
| **Management** (4) | Project Management, Decision Management, Information Management, Configuration Management |
| **Technical** (5) | Requirements Definition, System Architecting, Integration/Verification/Validation, Operation and Support, Agile Methods |

### 2.4 The 7 Qualification Strategies

Based on organizational maturity and needs, one or more of these strategies are recommended:

1. **SE for Managers** - Focus on leadership understanding of SE
2. **Common Basic Understanding** - Foundational awareness across organization
3. **Orientation in Pilot Project** - Hands-on learning through project work
4. **Certification** - Formal SE certifications (CSEP, SE-Zert)
5. **Continuous Support** - Ongoing learning for mature organizations
6. **Needs-based Project-oriented Training** - Targeted role-specific training
7. **Train the SE-Trainer** - Developing internal SE training capability

### 2.5 Two Assessment Pathways

The system determines which pathway to use based on organizational maturity:

| Pathway | Trigger | Description |
|---------|---------|-------------|
| **Task-Based** | Maturity Level < 3 | User describes their tasks; AI analyzes to derive competency requirements |
| **Role-Based** | Maturity Level >= 3 | User selects from pre-defined organizational roles |

---

## 3. Technology Stack and Architecture

### 3.1 Frontend

| Technology | Purpose |
|------------|---------|
| **Vue 3** | JavaScript framework with Composition API |
| **Vuetify 3** | Material Design component library |
| **Element Plus** | Additional UI components |
| **Pinia** | State management |
| **Vite** | Build tool and dev server |
| **Vue Router** | Client-side routing |
| **Axios** | HTTP client for API requests |

**Key Frontend Directories:**
```
src/frontend/src/
├── views/              # Page-level components
│   ├── phases/         # PhaseOne.vue, PhaseTwo.vue, PhaseThree.vue
│   ├── auth/           # Login.vue, Register.vue
│   └── assessments/    # Assessment management views
├── components/         # Reusable components
│   ├── phase1/         # Task 1-3 components (Maturity, Roles, Strategy)
│   ├── phase2/         # Competency assessment components
│   └── common/         # Shared components
├── stores/             # Pinia state stores
├── router/             # Vue Router configuration
└── api/                # API client modules
```

### 3.2 Backend

| Technology | Purpose |
|------------|---------|
| **Flask** | Python web framework |
| **SQLAlchemy** | ORM for database operations |
| **PostgreSQL** | Relational database |
| **OpenAI GPT-4** | AI for task analysis and LO generation |
| **FAISS** | Vector similarity search for role matching |
| **JWT** | Authentication tokens |

**Key Backend Directories:**
```
src/backend/
├── app/
│   ├── routes/                 # API endpoints (8 blueprints)
│   │   ├── auth.py            # Authentication
│   │   ├── organization.py    # Organization management
│   │   ├── phase1_maturity.py # Maturity assessment
│   │   ├── phase1_roles.py    # Role identification
│   │   ├── phase1_strategies.py # Strategy selection
│   │   ├── phase2_assessment.py # Competency assessment
│   │   ├── phase2_learning.py   # Learning objectives
│   │   └── main.py            # Miscellaneous routes
│   └── services/              # Business logic
│       ├── learning_objectives_core.py      # LO generation engine
│       ├── pathway_determination.py         # Pathway selection logic
│       ├── role_based_pathway_fixed.py      # Role-based algorithm
│       └── task_based_pathway.py            # Task-based algorithm
├── models.py                  # Database models (1,621 lines)
├── setup/                     # Database initialization scripts
└── run.py                     # Application entry point
```

### 3.3 Database

**Database**: PostgreSQL 12+
**Credentials**: `seqpt_admin:SeQpt_2025@localhost:5432/seqpt_database`

**Core Tables** (see Section 9 for complete schema):
- `organization` - Multi-tenant organization data
- `users` - User accounts
- `competency` - 16 SE competencies
- `role_cluster` - 14 standard SE roles
- `organization_roles` - Organization-specific roles
- `learning_strategy` - Selected qualification strategies
- `user_assessment` - Assessment records
- `user_se_competency_survey_results` - Competency scores

---

## 4. User Journey: From Login to Results

### 4.1 User Registration and Authentication

**Registration Flow:**

1. User visits the home page (`/`)
2. Clicks "Get Started" or "Register"
3. Provides:
   - Username
   - Email
   - Password
   - User Type: **Admin** (creates organization) or **Employee** (joins existing)
   - For Admin: Organization name
   - For Employee: Organization code (16-character alphanumeric)

**Key Files:**
- Frontend: `src/frontend/src/views/auth/Register.vue`
- Backend: `src/backend/app/routes/auth.py`

**Database Tables:**
- `users` - User credentials and profile
- `organization` - Organization details (Admin creates, Employee joins)

### 4.2 Dashboard

After login, users land on the Dashboard (`/app/dashboard`):

**For Admins:**
- View all 4 phases with completion status
- See organization code for sharing with employees
- Access Phase 1 (setup) through Phase 4 (implementation)

**For Employees:**
- View organization's Phase 1 results (read-only)
- Complete Phases 2-4 (personal assessment journey)
- See competency overview and progress

**Key Files:**
- Frontend: `src/frontend/src/views/Dashboard.vue`
- Backend: Various phase status endpoints

---

## 5. Phase 1: Prepare SE Training

**Purpose**: Establish the foundation for SE training by assessing organizational maturity, identifying roles, and selecting qualification strategies.

**Access**: Admin users only (employees see read-only results)

### 5.1 Task 1: Maturity Assessment

**What It Does:**
Assesses the organization's SE maturity level across four dimensions using a 4-question assessment.

**The Four Dimensions:**

1. **Rollout Scope** (0-100 points)
   - How widely SE practices are deployed across the organization
   - Options: None (0) -> Pilot (25) -> Partial (50) -> Wide (75) -> Full (100)

2. **SE Roles & Processes** (0-100 points)
   - Extent to which SE roles and processes are defined
   - Options: None (0) -> Basic (25) -> Partial (50) -> Defined (75) -> Optimized (100)

3. **SE Mindset** (0-100 points)
   - Cultural adoption of SE principles
   - Options: None (0) -> Emerging (25) -> Developing (50) -> Established (75) -> Ingrained (100)

4. **Knowledge Base** (0-100 points)
   - Documentation and knowledge management maturity
   - Options: None (0) -> Ad-hoc (25) -> Basic (50) -> Structured (75) -> Comprehensive (100)

**Calculation:**
```
Final Score = (Rollout + SEProcesses + Mindset + KnowledgeBase) / 4
Maturity Level = 1-5 based on score thresholds
```

**Maturity Levels:**
| Level | Score Range | Name |
|-------|-------------|------|
| 1 | 0-20 | Initial |
| 2 | 21-40 | Developing |
| 3 | 41-60 | Defined |
| 4 | 61-80 | Managed |
| 5 | 81-100 | Optimized |

**Key Files:**
- Frontend: `src/frontend/src/components/phase1/task1/MaturityAssessment.vue`
- Frontend: `src/frontend/src/components/phase1/task1/MaturityResults.vue`
- Backend: `src/backend/app/routes/phase1_maturity.py`
- Database: `phase_questionnaire_responses` (stores maturity assessment data)

### 5.2 Task 2: Role Identification

**What It Does:**
Identifies which SE roles exist in the organization and configures target group sizes.

**Two Approaches Based on Maturity:**

**For Low Maturity (Level 1-2): Task-Based Role Identification**
- Uses AI (GPT-4) to analyze user-provided task descriptions
- Derives role involvement from task analysis
- Automatically maps to standard SE roles

**For Higher Maturity (Level 3+): Standard Role Selection**
- Select from 14 standard SE role clusters
- Customize role names for organization context
- Define process involvement levels

**The 14 Standard SE Role Clusters:**

| ID | Role Name | Description |
|----|-----------|-------------|
| 1 | Systems Engineer | Integrates technical aspects across lifecycle |
| 2 | Requirements Engineer | Elicits, analyzes, documents requirements |
| 3 | System Architect | Designs system structure and interfaces |
| 4 | Configuration Manager | Manages configuration and changes |
| 5 | Test Engineer | Plans and executes verification activities |
| 6 | Safety Engineer | Ensures system safety requirements |
| 7 | Quality Manager | Ensures quality processes and standards |
| 8 | Project Manager | Plans and manages project execution |
| 9 | Integration Engineer | Integrates system components |
| 10 | Domain Expert | Provides specialized domain knowledge |
| 11 | Systems Analyst | Analyzes system performance and behavior |
| 12 | End User | Represents operational requirements |
| 13 | Specialist Developer | Develops specialized system components |
| 14 | Operator | Operates and maintains the system |

**Target Group Size Selection:**
| Category | Size Range | Impact |
|----------|------------|--------|
| Individual | 1-5 | One-on-one coaching |
| Small Group | 6-15 | Workshop-style training |
| Medium Group | 16-30 | Standard classroom |
| Large Group | 31-100 | Lecture format |
| Very Large | 100+ | Organization-wide programs |

**Key Files:**
- Frontend: `src/frontend/src/components/phase1/task2/RoleIdentification.vue`
- Frontend: `src/frontend/src/components/phase1/task2/StandardRoleSelection.vue`
- Frontend: `src/frontend/src/components/phase1/task2/TaskBasedMapping.vue`
- Backend: `src/backend/app/routes/phase1_roles.py` (75,933 lines - largest route file)
- Database: `organization_roles`, `role_process_matrix`

### 5.3 Task 3: Strategy Selection

**What It Does:**
Recommends and allows selection of qualification strategies based on maturity level and target group.

**Strategy Selection Algorithm:**

```python
if se_processes_maturity < 3:
    # Low maturity - dual selection required
    primary = "SE for Managers"  # Always selected
    secondary = user_choice_from([
        "Common Basic Understanding",
        "Orientation in Pilot Project",
        "Certification"
    ])
else:
    # Higher maturity - needs-based training
    strategy = "Needs-based Project-oriented Training"
    # OR "Continuous Support" based on scope
```

**The 7 Qualification Strategies in Detail:**

| Strategy | Target Maturity | Qualification Goal | Description |
|----------|-----------------|-------------------|-------------|
| SE for Managers | Low (1-2) | Understanding | Focus on leadership; enablers of change |
| Common Basic Understanding | Low (1-2) | Recognition | Interdisciplinary exchange; SE awareness |
| Orientation in Pilot Project | Low-Medium (2-3) | Application | Hands-on learning in real projects |
| Certification | Any | Application | Formal certifications (CSEP, SE-Zert) |
| Continuous Support | High (4-5) | Application | Self-directed learning, ongoing support |
| Needs-based Training | Medium-High (3-4) | Application | Targeted role-specific training |
| Train the Trainer | Any (additive) | Mastery | Developing internal trainers |

**Pro-Con Comparison (for low maturity selection):**

The system provides detailed pros and cons for each strategy option, helping users make informed decisions. For example:

**Common Basic Understanding:**
- PRO: Creates organizational awareness quickly
- PRO: Low barrier to entry
- CON: May not provide depth for specialists

**Key Files:**
- Frontend: `src/frontend/src/components/phase1/task3/StrategySelection.vue`
- Frontend: `src/frontend/src/components/phase1/task3/StrategyCard.vue`
- Frontend: `src/frontend/src/components/phase1/task3/ProConComparison.vue`
- Backend: `src/backend/app/routes/phase1_strategies.py`
- Database: `learning_strategy`, `strategy_template`, `strategy_template_competency`

---

## 6. Phase 2: Identify Requirements and Competencies

**Purpose**: Assess individual competency levels and generate personalized learning objectives.

**Access**: All authenticated users (Admin and Employee)

### 6.1 Pathway Determination

The system automatically determines the assessment pathway:

```javascript
const MATURITY_THRESHOLD = 3;

if (maturityLevel < MATURITY_THRESHOLD) {
    pathway = "TASK_BASED";
    // User describes their tasks
    // AI derives competency requirements
} else {
    pathway = "ROLE_BASED";
    // User selects from organization roles
    // Requirements come from role-competency matrix
}
```

**Key Files:**
- Frontend: `src/frontend/src/views/phases/PhaseTwo.vue`
- Frontend: `src/frontend/src/components/phase2/Phase2TaskFlowContainer.vue`
- Backend: `src/backend/app/services/pathway_determination.py`

### 6.2 Step 1: Role/Task Selection

**Role-Based Pathway (Maturity >= 3):**
1. View list of organization roles (from Phase 1)
2. Select one or more roles that apply to you
3. System calculates required competencies based on role-competency matrix

**Task-Based Pathway (Maturity < 3):**
1. Enter tasks in three categories:
   - **Responsible for**: Tasks you own and deliver
   - **Supporting**: Tasks you assist with
   - **Designing**: Design/architecture work you do
2. AI (GPT-4) analyzes task descriptions
3. System derives process involvement and competency requirements

**Task Analysis via LLM:**
```python
# Simplified representation of task analysis
prompt = f"""
Analyze these tasks and map to ISO 15288 processes:

Responsible for: {responsible_tasks}
Supporting: {supporting_tasks}
Designing: {design_tasks}

For each ISO process, determine involvement level:
- 0: Not performing
- 1: Occasionally performing
- 2: Regularly performing
- 4: Primary responsibility
"""
```

**Key Files:**
- Frontend: `src/frontend/src/components/phase2/DerikTaskSelector.vue`
- Frontend: `src/frontend/src/components/phase2/Phase2RoleSelection.vue`
- Backend: `src/backend/app/services/task_based_pathway.py`
- Backend: `src/backend/app/derik_integration.py`

### 6.3 Step 2: Review Necessary Competencies

After role/task selection, the system displays:

1. **List of Required Competencies** - All 16 competencies with required levels
2. **Why These Matter** - Context for each competency
3. **Target Levels** - What proficiency is expected (1, 2, 4, or 6)

**Proficiency Levels:**
| Level | Name | Description |
|-------|------|-------------|
| 0 | Not Required | Not needed for this role |
| 1 | Awareness | Basic understanding, recognition |
| 2 | Understanding | Can explain concepts, know when to apply |
| 4 | Application | Can apply in practice, solve problems |
| 6 | Mastery | Expert level, can teach others |

**Key Files:**
- Frontend: `src/frontend/src/components/phase2/Phase2NecessaryCompetencies.vue`
- Backend: Calculated from `role_competency_matrix` or `unknown_role_competency_matrix`

### 6.4 Step 3: Self-Assessment Survey

**The Assessment Interface:**

For each of the 16 competencies, the user:
1. Reads the competency description
2. Reviews behavioral indicators for each level
3. Self-rates their current proficiency (0-6)

**Competency Indicators (from Derik's research):**

Each competency has behavioral indicators at multiple levels. For example:

**Systems Thinking (Competency ID: 1):**
- Level 1: "Can identify system components and boundaries"
- Level 2: "Understands system interactions and dependencies"
- Level 4: "Applies systems thinking to complex problem solving"
- Level 6: "Leads organizational adoption of systems approaches"

**Assessment Validation:**
- All 16 competencies must be rated
- Scores must be 0, 1, 2, 4, or 6 (valid levels only)
- Cannot proceed until all are complete

**Key Files:**
- Frontend: `src/frontend/src/components/phase2/Phase2CompetencyAssessment.vue`
- Backend: `src/backend/app/routes/phase2_assessment.py`
- Database: `user_se_competency_survey_results`, `competency_indicators`

### 6.5 Step 4: Results and Gap Analysis

**Results Dashboard:**

After completing the assessment, users see:

1. **Radar Chart** - Visual comparison of:
   - Current competency levels (actual scores)
   - Required competency levels (target from role/strategy)

2. **Gap Analysis Table:**
   | Competency | Current | Required | Gap | Priority |
   |------------|---------|----------|-----|----------|
   | Systems Thinking | 2 | 4 | 2 | High |
   | Communication | 4 | 4 | 0 | Achieved |
   | ... | ... | ... | ... | ... |

3. **LLM-Generated Feedback** - Personalized narrative feedback analyzing:
   - Strengths (where you exceed requirements)
   - Development areas (gaps to close)
   - Recommended focus areas

**Key Files:**
- Frontend: `src/frontend/src/components/phase2/CompetencyResults.vue`
- Backend: `src/backend/app/generate_survey_feedback.py`

### 6.6 Learning Objectives Generation (Task 3 - Admin Only)

**Purpose**: Generate AI-powered learning objectives for the organization.

**The Learning Objectives Algorithm (Design v5):**

```
For each selected strategy:
    For each competency with target_level > 0:
        If NOT "Train the Trainer":
            Add to main pyramid targets
        Else:
            Add to mastery (TTT) section

For each user assessment:
    For each competency:
        current_level = user's score
        target_level = strategy target

        If target_level == 0:
            status = "not_targeted"
        Elif current_level >= target_level:
            status = "achieved"
        Else:
            status = "training_required"
            # Generate progressive LOs for levels 1 -> target
```

**Learning Objective Structure:**

Each LO includes:
- **Competency**: Which SE competency
- **Level**: Target proficiency level (1, 2, 4, or 6)
- **Status**: Achieved, Training Required, or Not Targeted
- **Objective Text**: AI-generated learning objective
- **PMT Context** (optional): Customized with organization's Processes, Methods, Tools

**PMT Context Form:**
Organizations with higher maturity can provide:
- **Processes**: SE processes used (e.g., "ISO 26262, V-model")
- **Methods**: Methods employed (e.g., "Agile, MBSE")
- **Tools**: Tool landscape (e.g., "DOORS, JIRA, Enterprise Architect")
- **Industry**: Domain context (e.g., "Automotive, Medical Devices")

**Caching System:**
- Generated LOs are cached in database
- Cache key = hash of (strategies + assessments + PMT context)
- Regeneration only when inputs change

**Key Files:**
- Frontend: `src/frontend/src/views/phases/Phase2Task3Admin.vue`
- Frontend: `src/frontend/src/components/phase2/task3/Phase2Task3Dashboard.vue`
- Frontend: `src/frontend/src/components/phase2/task3/LearningObjectivesView.vue`
- Backend: `src/backend/app/services/learning_objectives_core.py` (111,708 lines)
- Backend: `src/backend/app/routes/phase2_learning.py`
- Database: `generated_learning_objectives`, `organization_pmt_context`

---

## 7. Phase 3: Macro Planning

**Purpose**: Create a high-level qualification plan by selecting training modules and optimizing formats.

**Current Status**: Partially implemented (UI exists, some backend integration pending)

### 7.1 Step 1: Competency Gap Analysis

**Displays:**
- Total competencies assessed
- Average score across organization
- Critical gaps (largest deficits)
- Gap priority ranking (Critical > High > Medium > Low)

**Gap Calculation:**
```python
gap = target_level - current_level
if gap > 2:
    priority = "critical"
elif gap > 1:
    priority = "high"
elif gap > 0:
    priority = "medium"
else:
    priority = "achieved"
```

### 7.2 Step 2: Module Selection

**Training Module Catalog:**

Modules are tagged with:
- **Competencies covered** - Which of the 16 competencies
- **Duration** - Training days required
- **Format** - Online, In-Person, Hybrid
- **Priority alignment** - Which gaps this addresses

**Filtering Options:**
- By priority (Critical, High, Medium)
- By format (Online, In-Person, Hybrid)
- By duration (Short <=2 days, Medium 3-5 days, Long >5 days)

**Selection Metrics:**
- Total training days
- Gap coverage percentage

### 7.3 Step 3: Format Optimization

**Learning Preferences:**
- Preferred format (Online/In-Person/Hybrid/Flexible)
- Time availability (Full-time/Part-time/Weekends/Flexible)
- Learning pace (1-5 scale)
- Group size preference (Individual/Small/Large)

**Organizational Constraints:**
- Budget range (<5K, 5K-15K, >15K EUR)
- Timeline (date range)
- Location preferences
- Travel restrictions

**Optimization Output:**
- Optimized training timeline
- Scheduled modules with dates
- Format adjustments based on constraints

### 7.4 Step 4: Review & Confirmation

**Confirmation Checklist:**
- Plan reviewed
- Objectives aligned
- Constraints considered
- Ready to proceed

**Key Files:**
- Frontend: `src/frontend/src/views/phases/PhaseThree.vue`
- Backend: Various endpoints (partially implemented)

---

## 8. Phase 4: Detailed Implementation

**Purpose**: Execute the qualification plan with cohort formation and tracking.

**Current Status**: Not yet implemented (placeholder in navigation)

### 8.1 Planned Features

1. **Cohort Formation**
   - Group participants by competency gaps
   - Optimize group sizes for training efficiency
   - Consider location and availability

2. **Scheduling**
   - Assign specific dates to modules
   - Manage instructor availability
   - Handle conflicts and dependencies

3. **Progress Tracking**
   - Module completion status
   - Assessment retakes
   - Competency improvement over time

4. **Reporting**
   - Individual progress reports
   - Organizational overview
   - ROI metrics

---

## 9. Database Schema

### 9.1 Core Entity Tables

**organization**
```sql
CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL UNIQUE,
    organization_public_key VARCHAR(50) NOT NULL UNIQUE,
    size VARCHAR(20),                    -- 'small', 'medium', 'large', 'enterprise'
    maturity_score FLOAT,
    selected_archetype VARCHAR(100),
    phase1_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    organization_id INTEGER REFERENCES organization(id),
    role VARCHAR(100),                   -- 'admin', 'employee'
    user_type VARCHAR(20) DEFAULT 'participant',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**competency**
```sql
CREATE TABLE competency (
    id INTEGER PRIMARY KEY,
    competency_name VARCHAR(255) NOT NULL,
    competency_area VARCHAR(50),         -- 'Core', 'Social/Personal', 'Management', 'Technical'
    description TEXT,
    why_it_matters TEXT
);
-- Contains 16 rows (the 16 SE competencies)
```

**role_cluster**
```sql
CREATE TABLE role_cluster (
    id INTEGER PRIMARY KEY,
    role_cluster_name VARCHAR(255) NOT NULL,
    role_cluster_description TEXT NOT NULL
);
-- Contains 14 rows (the 14 standard SE roles)
```

### 9.2 Organization-Specific Tables

**organization_roles**
```sql
CREATE TABLE organization_roles (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    role_name VARCHAR(255) NOT NULL,
    role_description TEXT,
    standard_role_cluster_id INTEGER REFERENCES role_cluster(id),
    identification_method VARCHAR(50) DEFAULT 'STANDARD',
    participating_in_training BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, role_name)
);
```

**learning_strategy**
```sql
CREATE TABLE learning_strategy (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    strategy_name VARCHAR(255) NOT NULL,
    strategy_description TEXT,
    selected BOOLEAN DEFAULT FALSE,
    priority INTEGER,
    strategy_template_id INTEGER REFERENCES strategy_template(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, strategy_name)
);
```

### 9.3 Matrix Tables

**role_process_matrix**
```sql
CREATE TABLE role_process_matrix (
    id SERIAL PRIMARY KEY,
    role_cluster_id INTEGER REFERENCES organization_roles(id) ON DELETE CASCADE,
    iso_process_id INTEGER REFERENCES iso_processes(id),
    role_process_value INTEGER DEFAULT -100,  -- -100, 0, 1, 2, 4
    organization_id INTEGER REFERENCES organization(id),
    UNIQUE(organization_id, role_cluster_id, iso_process_id)
);
```

**process_competency_matrix**
```sql
CREATE TABLE process_competency_matrix (
    id SERIAL PRIMARY KEY,
    iso_process_id INTEGER REFERENCES iso_processes(id),
    competency_id INTEGER REFERENCES competency(id),
    process_competency_value INTEGER DEFAULT -100,
    UNIQUE(iso_process_id, competency_id)
);
```

**role_competency_matrix**
```sql
CREATE TABLE role_competency_matrix (
    id SERIAL PRIMARY KEY,
    role_cluster_id INTEGER REFERENCES organization_roles(id) ON DELETE CASCADE,
    competency_id INTEGER REFERENCES competency(id),
    role_competency_value INTEGER DEFAULT -100,  -- 0, 1, 2, 4, 6
    organization_id INTEGER REFERENCES organization(id),
    UNIQUE(organization_id, role_cluster_id, competency_id)
);
```

### 9.4 Assessment Tables

**user_assessment**
```sql
CREATE TABLE user_assessment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    organization_id INTEGER REFERENCES organization(id) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,      -- 'role_based', 'task_based'
    survey_type VARCHAR(50),
    tasks_responsibilities JSONB,              -- For task-based pathway
    selected_roles JSONB,                      -- Array of role IDs
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

**user_se_competency_survey_results**
```sql
CREATE TABLE user_se_competency_survey_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    organization_id INTEGER REFERENCES organization(id),
    competency_id INTEGER REFERENCES competency(id),
    score INTEGER NOT NULL,                    -- Current level (0-6)
    target_level INTEGER,
    gap_size INTEGER,
    assessment_id INTEGER REFERENCES user_assessment(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP DEFAULT NOW()
);
```

### 9.5 Strategy Template Tables (Global)

**strategy_template**
```sql
CREATE TABLE strategy_template (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL UNIQUE,
    strategy_description TEXT,
    requires_pmt_context BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Contains 7 rows (the 7 qualification strategies)
```

**strategy_template_competency**
```sql
CREATE TABLE strategy_template_competency (
    id SERIAL PRIMARY KEY,
    strategy_template_id INTEGER REFERENCES strategy_template(id) ON DELETE CASCADE,
    competency_id INTEGER REFERENCES competency(id) ON DELETE CASCADE,
    target_level INTEGER NOT NULL,             -- 1, 2, 4, or 6
    UNIQUE(strategy_template_id, competency_id),
    CHECK(target_level >= 1 AND target_level <= 6)
);
-- Contains 112 rows (7 strategies x 16 competencies)
```

### 9.6 Learning Objectives Cache

**generated_learning_objectives**
```sql
CREATE TABLE generated_learning_objectives (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL UNIQUE,
    pathway VARCHAR(20) NOT NULL,              -- 'TASK_BASED' or 'ROLE_BASED'
    objectives_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    input_hash VARCHAR(64) NOT NULL,           -- SHA-256 hash for cache validation
    validation_status VARCHAR(20),
    gap_percentage FLOAT
);
```

---

## 10. Data Sources and Reference Data

### 10.1 ISO/IEC 15288 Processes

The system uses 28 ISO/IEC/IEEE 15288 system life cycle processes organized into 4 process groups:

**Agreement Processes (2):**
- Acquisition Process
- Supply Process

**Organizational Project-Enabling Processes (6):**
- Life Cycle Model Management
- Infrastructure Management
- Project Portfolio Management
- Human Resource Management
- Quality Management
- Knowledge Management

**Project Processes (7):**
- Project Planning
- Project Assessment and Control
- Decision Management
- Risk Management
- Configuration Management
- Information Management
- Measurement

**Technical Processes (13):**
- Business or Mission Analysis
- Stakeholder Needs and Requirements Definition
- System Requirements Definition
- Architecture Definition
- Design Definition
- System Analysis
- Implementation
- Integration
- Verification
- Transition
- Validation
- Operation
- Maintenance
- Disposal

### 10.2 Competency Indicator Data

Located in: `src/backend/setup/populate/`

**competency_indicators** table contains behavioral indicators for each competency at each level, derived from:
- INCOSE SE Competency Framework
- SE4OWL (Systems Engineering for Open World Learning) research
- Derik's original competency assessment system

### 10.3 Strategy Definitions

Located in: `data/source/strategy_definitions.json`

Contains detailed descriptions of all 7 qualification strategies including:
- Strategy name
- Full description
- Target maturity levels
- Qualification goals

### 10.4 Learning Objectives Guidelines

Located in: `data/source/templates/learning_objectives_guidelines.json`

Contains templates and guidelines for AI-generated learning objectives including:
- Bloom's taxonomy verb mappings
- Level-appropriate action verbs
- Format templates

---

## 11. API Endpoints

### 11.1 Authentication (`/api/` and `/auth/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/auth/me` | Get current user |
| POST | `/auth/logout` | Logout |

### 11.2 Phase 1 - Maturity (`/api/phase1/maturity/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{org_id}/latest` | Get latest maturity assessment |
| POST | `/save` | Save maturity assessment |

### 11.3 Phase 1 - Roles (`/api/phase1/roles/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/standard` | Get 14 standard role clusters |
| GET | `/{org_id}` | Get organization roles |
| POST | `/save` | Save organization roles |
| POST | `/analyze-tasks` | Analyze tasks via LLM |
| GET | `/target-group/{org_id}` | Get target group data |
| POST | `/target-group/save` | Save target group size |

### 11.4 Phase 1 - Strategies (`/api/phase1/strategies/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{org_id}` | Get organization strategies |
| POST | `/save` | Save strategy selection |
| GET | `/templates` | Get global strategy templates |

### 11.5 Phase 2 - Assessment (`/api/phase2/` and `/assessment/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/start` | Start new assessment |
| POST | `/submit` | Submit assessment responses |
| GET | `/results/{assessment_id}` | Get assessment results |
| GET | `/latest_competency_overview` | Get latest competency scores |
| GET | `/competencies` | Get 16 competencies |

### 11.6 Phase 2 - Learning Objectives (`/api/phase2/learning-objectives/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{org_id}` | Get cached learning objectives |
| POST | `/generate` | Generate new learning objectives |
| GET | `/export/excel` | Export LOs to Excel |
| GET | `/pmt-context/{org_id}` | Get PMT context |
| POST | `/pmt-context/save` | Save PMT context |

### 11.7 Organization (`/organization/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{org_id}` | Get organization details |
| PUT | `/{org_id}` | Update organization |
| GET | `/{org_id}/completion-status` | Get phase completion status |

---

## 12. Appendix: Key Files Reference

### 12.1 Frontend Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/frontend/src/views/Dashboard.vue` | 734 | Main dashboard with phase navigation |
| `src/frontend/src/views/phases/PhaseOne.vue` | ~1,200 | Phase 1 container (4 tasks) |
| `src/frontend/src/views/phases/PhaseTwo.vue` | 185 | Phase 2 entry point |
| `src/frontend/src/views/phases/PhaseThree.vue` | 1,086 | Phase 3 macro planning |
| `src/frontend/src/components/phase1/task1/MaturityAssessment.vue` | ~400 | Maturity questionnaire |
| `src/frontend/src/components/phase1/task2/RoleIdentification.vue` | ~500 | Role identification |
| `src/frontend/src/components/phase1/task3/StrategySelection.vue` | ~600 | Strategy selection |
| `src/frontend/src/components/phase2/Phase2TaskFlowContainer.vue` | ~350 | Phase 2 flow coordinator |
| `src/frontend/src/components/phase2/Phase2CompetencyAssessment.vue` | ~400 | Self-assessment form |
| `src/frontend/src/components/phase2/CompetencyResults.vue` | ~500 | Results with radar chart |
| `src/frontend/src/components/phase2/task3/LearningObjectivesView.vue` | ~600 | LO display |
| `src/frontend/src/router/index.js` | 367 | Route definitions |

### 12.2 Backend Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/backend/models.py` | 1,621 | All database models |
| `src/backend/app/routes/phase1_roles.py` | 75,933 | Role identification API |
| `src/backend/app/routes/phase2_learning.py` | 74,045 | Learning objectives API |
| `src/backend/app/routes/phase2_assessment.py` | 59,855 | Assessment API |
| `src/backend/app/services/learning_objectives_core.py` | 111,708 | LO generation engine |
| `src/backend/app/services/role_based_pathway_fixed.py` | 94,917 | Role-based algorithm |
| `src/backend/app/services/task_based_pathway.py` | 30,180 | Task-based algorithm |
| `src/backend/app/derik_integration.py` | 59,788 | Derik's competency system integration |

### 12.3 Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (DB URL, API keys) |
| `docker-compose.yml` | Docker configuration |
| `requirements.txt` | Python dependencies |
| `src/frontend/package.json` | Node.js dependencies |
| `src/frontend/vite.config.js` | Vite build configuration |

### 12.4 Data Files

| File | Purpose |
|------|---------|
| `data/source/strategy_definitions.json` | 7 strategy definitions |
| `data/source/templates/learning_objectives_guidelines.json` | LO generation templates |
| `src/backend/setup/populate/*.py` | Database population scripts |
| `src/backend/setup/migrations/*.sql` | Database migrations |

---

## Document Information

- **Generated**: December 2025
- **Version**: 1.0
- **Application Version**: SE-QPT Master Thesis Project
- **Authors**: Based on Derik's original competency assessment system, integrated by Jomon

---

*End of Report*
