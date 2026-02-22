# Phase 4: Micro Planning - Design Specification v1.1

## Document Information
- **Module**: Phase 4 - Micro Planning of SE Training Initiative
- **Primary Tasks**: AVIVA Didactics Planning, RFP Document Export
- **Based on**: Ulf Meeting Notes (13.01.2026), Reference Files (RFP PDF, AVIVA Excel)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 1.2 (Halved AVIVA Durations per Ulf Review 02.02.2026)
- **Date**: February 2026

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial design specification based on Ulf meeting (13.01.2026) |
| 1.1 | Jan 2026 | Added detailed AVIVA column generation strategy with hybrid approach (programmatic + GenAI) |
| 1.2 | Feb 2026 | Halved all AVIVA module durations per Ulf review (02.02.2026): L1 2h->1h, L2 4h->2h, L4 8h->4h, L6 16h/2days->8h/1day. Redesigned all activity sequences. |

---

## Table of Contents

1. [Module Overview](#1-module-overview)
2. [Phase 4 Structure](#2-phase-4-structure)
3. [Task 1: AVIVA Didactics Planning](#3-task-1-aviva-didactics-planning)
4. [Task 2: RFP Document Export](#4-task-2-rfp-document-export)
5. [Content Data Sources](#5-content-data-sources)
6. [UI/UX Design](#6-uiux-design)
7. [Data Models](#7-data-models)
8. [API Specification](#8-api-specification)
9. [Phase 4 Outputs](#9-phase-4-outputs)
10. [Implementation Checklist](#10-implementation-checklist)

---

## 1. Module Overview

### 1.1 Purpose

Phase 4 "Micro Planning" helps organizations:
1. **Plan detailed didactics** for each training module using the AVIVA model
2. **Export comprehensive RFP document** containing all SE-QPT data for training providers

### 1.2 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Sequential Tasks** | AVIVA planning must be completed before RFP export |
| **Hybrid Generation** | Programmatic generation for structure + GenAI for content |
| **Comprehensive RFP** | All data from Phases 1-4 consolidated into exportable document |
| **Multiple Export Formats** | Support for Excel and Word document exports |

### 1.3 Position in SE-QPT Workflow

```
Phase 1: Prepare SE Training
    | Outputs: Maturity Level, Role Clusters, Qualification Archetype,
               Target Group Size, Training Group Size
    v
Phase 2: Identify Requirements and Competencies
    | Outputs: Competency Gaps, Learning Objectives, Training Modules,
               Existing Training Offers (with level differentiation)
    v
Phase 3: Macro Planning
    | Outputs: Training Structure, Selected Learning Formats,
               Timeline Milestones, Participant Estimates
    v
Phase 4: Micro Planning  <-- THIS MODULE
    |
    |-- Task 1: AVIVA Didactics Planning
    |   |-- For each training module from Phase 3
    |   |-- Hybrid approach: Programmatic structure + GenAI content
    |   +-- Option: Manual template OR GenAI-assisted content
    |
    +-- Task 2: RFP Document Export
        |-- Consolidate all data from Phases 1-4
        +-- Export as Word document and/or Excel spreadsheet

    v Outputs: AVIVA Plans per Module, RFP Document
```

### 1.4 What is AVIVA?

AVIVA is a German didactic model for structuring training sessions. The acronym stands for:

| Phase | German | English | Purpose |
|-------|--------|---------|---------|
| **A** | Ankommen | Arrival | Welcome, orientation, setting expectations |
| **V** | Vorwissen aktivieren | Activate Prior Knowledge | Connect to existing knowledge, motivation |
| **I** | Informieren | Inform | Present new content, concepts, methods |
| **V** | Verarbeiten | Process | Practice, exercises, apply learning |
| **A** | Auswerten | Evaluate | Reflect, assess learning, feedback |

---

## 2. Phase 4 Structure

### 2.1 Task Flow

```
Entry Point: Phase 3 Completed
    |
    v
+------------------------+
| Task 1: AVIVA Planning |
+------------------------+
    |
    |-- Step 1.1: Display module list from Phase 3
    |-- Step 1.2: User selects export option:
    |      Option A: Template (programmatic, empty content)
    |      Option B: GenAI-assisted (full content generation)
    |-- Step 1.3: Preview learning objectives and content topics
    |-- Step 1.4: Generate/Export AVIVA Excel
    |
    v
+------------------------+
| Task 2: RFP Export     |
+------------------------+
    |
    |-- Step 2.1: Preview RFP data summary
    |-- Step 2.2: Select export format (Word/Excel/Both)
    |-- Step 2.3: Generate and download RFP document
    |
    v
Phase 4 Complete
```

### 2.2 Prerequisites

| Prerequisite | Source | Required |
|-------------|--------|----------|
| Training modules with selected learning formats | Phase 3 Task 2 | Yes |
| Timeline milestones | Phase 3 Task 3 | Yes |
| Competency gaps and learning objectives | Phase 2 | Yes |
| Organization info (maturity, archetype, group sizes) | Phase 1 | Yes |

---

## 3. Task 1: AVIVA Didactics Planning

### 3.1 Overview

For each training module defined in Phase 3, the user can generate an AVIVA-structured didactic plan that outlines how the training session should be conducted.

**Key Insight**: The system uses a **hybrid approach** where most columns are generated programmatically based on rules, while the "Content" column uses GenAI for intelligent text generation.

### 3.2 AVIVA Excel Structure

Based on the reference template `M1+M2 - Konzeption_fein.xlsx`:

| Column | Name | Description | Example |
|--------|------|-------------|---------|
| A | **Module** | Training module identifier | "Systems Thinking - Knowing" |
| B | **Start** | Start time of activity | "10:00" |
| C | **Duration (min)** | Duration in minutes | 15 |
| D | **Type** | Activity type code | V, U, P |
| E | **AVIVA** | AVIVA phase | A, V, I, V, A |
| F | **What (Content)** | Content/topic of activity | "Introduction to SE concepts" |
| G | **How (Method)** | Delivery method | "Lecture", "Group Exercise", "Discussion" |
| H | **Material** | Materials/resources | "PowerPoint", "Flip-Chart", "Exercise Sheet" |

**Type Codes:**
- `V` = Vortrag (Lecture/Presentation)
- `U` = Ubung (Exercise/Practice)
- `P` = Pause (Break)

### 3.3 AVIVA Column Generation Strategy (Hybrid Approach)

#### 3.3.1 Generation Summary

| Column | Name | Generation Method | GenAI Required? |
|--------|------|-------------------|-----------------|
| A | Module | **Programmatic** | NO |
| B | Start | **Programmatic** | NO |
| C | Duration | **Programmatic** (rule-based) | NO |
| D | Type | **Programmatic** (mapping) | NO |
| E | AVIVA | **Programmatic** (sequence) | NO |
| F | What (Content) | **GenAI** | YES |
| G | How (Method) | **Programmatic** (with enhancement option) | Optional |
| H | Material | **Programmatic** (with enhancement option) | Optional |

#### 3.3.2 Column A: Module - 100% Programmatic

**Source Data:**
- `phase3_training_module.competency_id` → `competency.competency_name`
- `phase3_training_module.target_level`
- `phase3_training_module.pmt_type` (process/method/tool/combined)

**Generation Logic:**
```
Format: "{competency_name} - {level_name} ({pmt_type})"
Example: "Systems Thinking - Knowing (Process)"
         "Requirements Management - Applying (Method)"
```

**Level Name Mapping:**
| Level | Level Name |
|-------|------------|
| 1 | Knowing |
| 2 | Understanding |
| 4 | Applying |
| 6 | Mastery |

#### 3.3.3 Column B: Start Time - 100% Programmatic

**Generation Logic:**
```python
start_time = "09:00"  # Default start
for each activity:
    activity.start_time = current_time
    current_time = current_time + activity.duration
```

**Rules:**
- Default start: 09:00
- Each activity starts immediately after previous ends
- Lunch break (50 min) inserted around 12:30-13:30 for full-day modules (Level 6 only)
- Short breaks (10-15 min) inserted every ~60-90 minutes for modules 2h+

#### 3.3.4 Column C: Duration (min) - Programmatic with Rules

**Duration by AVIVA Phase:**

| AVIVA Phase | Purpose | Default Duration | Range |
|-------------|---------|------------------|-------|
| A (Arrive) | Welcome/Introduction | 10 min | 5-15 min |
| V (Activate) | Prior knowledge activation | 15 min | 10-25 min |
| I (Inform) | Content delivery | 25 min | 20-35 min |
| V (Process) | Practice/Exercises | 30 min | 15-45 min |
| A (Evaluate) | Summary/Feedback | 10 min | 10-20 min |
| P (Break) | Short break | 10 min | 10-15 min |
| P (Lunch) | Lunch break | 50 min | 45-50 min |

**Total Duration by Level:**

| Level | Total Duration | Activity Distribution | I:V Ratio |
|-------|---------------|----------------------|-----------|
| 1 (Knowing) | 1 hour (60 min) | Single I-V cycle, no breaks | 1.3:1 (I-heavy) |
| 2 (Understanding) | 2 hours (120 min) | Two I-V cycles, 1 break | 1.1:1 (balanced) |
| 4 (Applying) | 4 hours (240 min) | Three practice rounds, 2 breaks, no lunch | 0.84:1 (V-heavy) |
| 6 (Mastery) | 8 hours (480 min, 1 day) | Four practice rounds, lunch + 2 breaks | 0.91:1 (V-heavy) |

**Activity Count by Level:**

| Level | A (Arrive) | V (Activate) | I (Inform) | V (Process) | A (Evaluate) | P (Break/Lunch) | Total |
|-------|------------|--------------|------------|-------------|--------------|-----------------|-------|
| 1 | 1 | 1 | 1 | 1 | 1 | 0 | 5 |
| 2 | 1 | 1 | 2 | 2 | 1 | 1 | 8 |
| 4 | 1 | 1 | 4 | 3 | 1 | 2 | 12 |
| 6 | 1 | 2 | 5 | 4 | 1 | 3 | 16 |

#### 3.3.5 Column D: Type (V/U/P) - Programmatic Mapping

**AVIVA Phase to Type Mapping:**

| AVIVA Phase | Default Type | Rationale |
|-------------|--------------|-----------|
| A (Arrive) | V (Lecture) | Welcome is typically presenter-led |
| V (Activate) | U (Exercise) | Activation involves participant engagement |
| I (Inform) | V (Lecture) | Information delivery is presenter-led |
| V (Process) | U (Exercise) | Practice is participant activity |
| A (Evaluate) | V (Lecture) | Summary can be mixed, default to lecture |
| P (Break) | P (Pause) | Break |

**Adjustment by Learning Format:**

| Learning Format | Type Adjustments |
|-----------------|------------------|
| Webinar | More V (lectures), limit U to polls/chat |
| Seminar | Balanced V and U |
| Coaching | More U (individual exercises) |
| WBT | All V (self-paced content) |
| Blended | Mix based on online/offline portions |

#### 3.3.6 Column E: AVIVA Phase - 100% Programmatic

**Standard Sequence Pattern:**
```
A → V → I → [I...] → V → [P] → [I → V]... → A
```

**Sequence Templates by Level:**

**Level 1 (1 hour / 60 min) - Single I-V cycle:**
```
A  →  V  →  I  →  V  →  A
(5)  (10)  (20)  (15)  (10) = 60 min
```

**Level 2 (2 hours / 120 min) - Two I-V cycles with break:**
```
A  →  V  →  I  →  V  →  P  →  I  →  V  →  A
(5)  (10)  (25)  (20)  (10)  (20)  (20)  (10) = 120 min
```

**Level 4 (4 hours / 240 min) - Half-day workshop, 3 practice rounds:**
```
A  →  V  →  I  →  I  →  V  →  P  →  I  →  V  →  P  →  I  →  V  →  A
(10)  (15)  (20)  (20)  (30)  (15)  (20)  (35)  (10)  (20)  (30)  (15) = 240 min
```

**Level 6 (8 hours / 480 min / 1 day) - Full day intensive with lunch:**
```
A  →  V  →  I  →  I  →  V  →  P  →  I  →  V  →  P(lunch) →  V  →  I  →  V  →  P  →  I  →  V  →  A
(15)  (25)  (35)  (30)  (45)  (15)  (30)  (40)    (50)     (15)  (30)  (40)  (15)  (30)  (45)  (20) = 480 min
```

#### 3.3.7 Column F: What (Content) - GenAI Required

**This is the primary column requiring GenAI generation.**

**Input Data for GenAI:**

| Data Source | Table/Field | Description |
|-------------|-------------|-------------|
| Module Name | `competency.competency_name` + level | e.g., "Systems Thinking - Knowing" |
| Learning Objective | `competency_indicators.indicator_en` | Level-specific learning objective text |
| Generated LOs | `generated_learning_objectives.objectives_data` | Organization-specific learning objectives from Phase 2 |
| Content Topics | Excel Column H (or new `competency_content_baseline` table) | Baseline content topics for the competency |
| PMT Type | `phase3_training_module.pmt_type` | Focus area: process, method, tool, or combined |
| AVIVA Phase | Current row's AVIVA phase | Context for what type of content (welcome, activation, info, practice, summary) |
| Learning Format | `learning_format.format_name` | Influences content delivery style |

**GenAI Prompt Template:**

```
You are creating AVIVA didactic content for a Systems Engineering training module.

== MODULE CONTEXT ==
Module: {competency_name} - Level {target_level} ({level_name})
PMT Focus: {pmt_type}
Learning Format: {format_name} ({mode_of_delivery})
Total Duration: {total_duration_hours} hours

== LEARNING OBJECTIVE ==
{level_specific_learning_objective}

== CONTENT TOPICS (Baseline) ==
{content_topics_list}

== GENERATED LEARNING OBJECTIVES (from Phase 2) ==
{organization_specific_learning_objectives}

== TASK ==
Generate specific, actionable content for each activity in the AVIVA sequence below.
Each content description should be 1-2 sentences, specific to the competency and level.

For AVIVA phases:
- A (Arrive): Welcome activity, set expectations, module overview
- V (Activate): Discussion questions or activities to surface prior knowledge
- I (Inform): Specific topic from content list to present
- V (Process): Hands-on exercise or practice activity related to recent I block
- A (Evaluate): Summary question, key takeaways, or feedback activity

== AVIVA SEQUENCE TO FILL ==
{aviva_sequence_with_durations}

== OUTPUT FORMAT ==
Return a JSON array with content for each activity:
[
  {"row": 1, "aviva_phase": "A", "content": "..."},
  {"row": 2, "aviva_phase": "V", "content": "..."},
  ...
]
```

**Content Guidelines by AVIVA Phase:**

| AVIVA Phase | Content Focus | Example |
|-------------|---------------|---------|
| A (Arrive) | Welcome, objectives, agenda | "Welcome and Introduction: Module objectives and agenda overview" |
| V (Activate) | Prior knowledge question/discussion | "Discussion: What system boundaries have you encountered in your work?" |
| I (Inform) | Specific topic delivery | "SE Process Models: Introduction to V-Model and lifecycle phases" |
| V (Process) | Exercise tied to previous I block | "Group Exercise: Identify system boundaries in the provided case study" |
| A (Evaluate) | Summary and feedback | "Key Takeaways Quiz: 5 questions on system thinking fundamentals" |

#### 3.3.8 Column G: How (Method) - Programmatic with Optional Enhancement

**Base Method Mapping (Programmatic):**

| AVIVA Phase | Learning Format | Default Methods |
|-------------|-----------------|-----------------|
| A (Arrive) | Any | Lecture, Introduction |
| V (Activate) | Seminar | Discussion, Brainstorm |
| V (Activate) | Webinar | Poll, Chat Discussion |
| V (Activate) | Coaching | One-on-One Discussion |
| I (Inform) | Seminar | Lecture, Demonstration |
| I (Inform) | Webinar | Presentation, Screen Share |
| I (Inform) | WBT | Video, Interactive Content |
| V (Process) | Seminar | Group Exercise, Role Play, Case Study |
| V (Process) | Webinar | Breakout Room Exercise, Quiz |
| V (Process) | Coaching | Guided Practice, Feedback Session |
| A (Evaluate) | Any | Q&A, Feedback Form, Discussion |

**Level-Based Adjustments:**

| Level | Method Emphasis |
|-------|-----------------|
| 1 (Knowing) | More lectures, basic discussions |
| 2 (Understanding) | Case studies, explain-to-partner exercises |
| 4 (Applying) | Hands-on practice, simulations, tool exercises |
| 6 (Mastery) | Teaching others, strategy development, mentoring exercises |

#### 3.3.9 Column H: Material - Programmatic with Optional Enhancement

**Base Material Mapping (Programmatic):**

| Learning Format | Mode | Default Materials |
|-----------------|------|-------------------|
| Seminar | Offline | PowerPoint, Flip-Chart, Handouts, Exercise Sheets |
| Webinar | Online | PowerPoint, Screen Share, Chat, Polls |
| Coaching | Hybrid | Whiteboard, Notes, Tool Access, Feedback Forms |
| WBT | Online | LMS, Videos, Quizzes, Interactive Modules |
| Blended | Hybrid | Mix of above based on activity |

**AVIVA Phase Material Defaults:**

| AVIVA Phase | Typical Materials |
|-------------|-------------------|
| A (Arrive) | PowerPoint (agenda slide), Name tags |
| V (Activate) | Flip-Chart, Moderation Cards, Whiteboard |
| I (Inform) | PowerPoint, Handouts, Handbook |
| V (Process) | Exercise Sheets, Case Study Documents, Tools |
| A (Evaluate) | Feedback Forms, Quiz, PowerPoint (summary) |
| P (Break) | - (none) |

### 3.4 Content Generation Options

#### Option A: Template Export (Programmatic Only)

User exports an Excel template with:
- **Fully generated**: Module, Start, Duration, Type, AVIVA, Method, Material
- **Placeholder text**: What (Content) column contains placeholders based on content topics
- User fills in specific content manually

**Placeholder Example:**
```
Row | AVIVA | What (Content) - Placeholder
----|-------|-----------------------------
1   | A     | [Welcome & Introduction]
2   | V     | [Prior Knowledge: Discussion on {topic_1}]
3   | I     | [Content Delivery: {topic_1} - {topic_2}]
4   | V     | [Practice Exercise: {topic_1} application]
5   | A     | [Summary & Evaluation]
```

**UI Flow:**
1. Display list of modules from Phase 3
2. Show learning objectives and content topics preview
3. Button: "Export Template (Manual Completion)"
4. Download Excel with placeholder content

#### Option B: GenAI-Assisted Content Generation

System uses GenAI to generate detailed AVIVA content:
- All programmatic columns generated first
- GenAI called only for "What (Content)" column
- Optional: GenAI can enhance Method and Material columns

**UI Flow:**
1. Display list of modules from Phase 3
2. Show learning objectives and content topics preview
3. Button: "Generate with GenAI"
4. System generates programmatic columns
5. System calls OpenAI API to generate content
6. Preview generated content
7. User can edit/modify
8. Export final AVIVA Excel

### 3.5 Data Sources for AVIVA Generation

#### 3.5.1 Available Database Tables

| Table | Relevant Fields | Usage |
|-------|-----------------|-------|
| `phase3_training_module` | competency_id, target_level, selected_format_id, pmt_type, estimated_participants | Module metadata |
| `competency` | competency_name, competency_area, description | Competency info |
| `competency_indicators` | competency_id, level, indicator_en | Level-specific learning objectives |
| `learning_format` | format_name, mode_of_delivery, communication_type, collaboration_type | Format-specific adaptations |
| `generated_learning_objectives` | objectives_data (JSONB) | Organization-specific LOs from Phase 2 |
| `training_program_cluster` | cluster_name | Role-cluster context (if applicable) |

#### 3.5.2 Content Topics (To Be Imported)

Source: `data/source/excel/Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx`, Column H

**Note:** Content topics are at the **competency level only** (not level-differentiated).
The GenAI adapts these topics based on the target level.

| Competency | Content Topics (Baseline) |
|------------|--------------------------|
| **Systems Thinking** | Motivation for SE, Definition of terms, Values of SE, SE process models (V-model), SE standards |
| **System Modeling & Analysis** | Model theory, Simulation |
| **System Life Cycle Phases** | Life cycle phases, Operating costs during the life cycle |
| **Customer Benefit Orientation** | Agile Manifesto |
| **Requirements Management** | Requirements process, Stakeholder analysis, Types of requirements, Traceability, Documentation, Elicitation/definition/analysis, Use cases, System boundary, Verification/validation criteria |
| **System Architecture Design** | Architecture process, Functional/logical architecture, Synthesis, Architecture views (security, safety), Alternatives evaluation, Interfaces and interactions |
| **Integration, Verification & Validation** | Integration strategies, IVV definition, Verification/validation procedures and methods, Traceability, Corrective actions, System acceptance |
| **Operation, Service & Maintenance** | Operating strategies, User feedback, Maintenance strategies, Decommissioning/disposal |
| **Agile Methodological Competence** | Scrum, SAFe |
| **Self-Organization** | Personal behavior, Time management, Work organization |
| **Communication & Collaboration** | Stakeholder communication, Communication techniques, Negotiation, Conflict resolution, Feedback |
| **Leadership** | Team definition, Team development phases, Personality models, Leadership styles |
| **Project Management** | Project goals/scope, WBS planning, Schedule/budget, Resources/roles, KPIs, Reporting |
| **Decision Management** | Decision strategy, Alternatives evaluation, Risk profiles, Risk management |
| **Information Management** | Communication planning, Information distribution/storage |
| **Configuration Management** | Configuration items, Configuration control cycle, Baselines, Change management |

### 3.6 AVIVA Template Structure Examples

#### Example: Level 1 Module (1 hour) - Systems Thinking

```
Module: Systems Thinking - Knowing (Combined)
Duration: 1 hour (60 minutes)
Learning Objective: "The participant knows the interrelationships of their system and the associated system boundaries."

| Start | Min | Type | AVIVA | What (Content) | How (Method) | Material |
|-------|-----|------|-------|----------------|--------------|----------|
| 09:00 |  5  | V    | A     | Welcome: Module objectives and SE importance | Lecture | PowerPoint |
| 09:05 | 10  | U    | V     | Discussion: What systems do you work with? | Group Discussion | Flip-Chart |
| 09:15 | 20  | V    | I     | SE Fundamentals: Terms, V-Model, Standards, Rule of 10 | Lecture | PowerPoint, Handout |
| 09:35 | 15  | U    | V     | Exercise: Identify system boundaries in case | Pair Work | Exercise Sheet |
| 09:50 | 10  | V    | A     | Summary: Key takeaways and Q&A | Discussion | Feedback Form |
```

#### Example: Level 4 Module (4 hours) - Requirements Management

```
Module: Requirements Management - Applying (Process)
Duration: 4 hours (240 minutes)
Learning Objective: "Participants can independently identify sources of requirements, derive requirements, document and link them."

| Start | Min | Type | AVIVA | What (Content) | How | Material |
|-------|-----|------|-------|----------------|-----|----------|
| 09:00 | 10  | V    | A     | Welcome: Module objectives, practical outcomes | Lecture | PowerPoint |
| 09:10 | 15  | U    | V     | Discussion: Requirements challenges you face | Group | Flip-Chart |
| 09:25 | 20  | V    | I     | Requirements Process: Company process overview | Lecture | PowerPoint |
| 09:45 | 20  | V    | I     | Stakeholder Analysis: Identification methods | Lecture | PowerPoint |
| 10:05 | 30  | U    | V     | Exercise: Map your project's requirements flow | Group | Template |
| 10:35 | 15  | P    | -     | Break | - | - |
| 10:50 | 20  | V    | I     | Types of Requirements: Functional, non-functional | Lecture | PowerPoint |
| 11:10 | 35  | U    | V     | Exercise: Classify requirements from spec | Group | Handout |
| 11:45 | 10  | P    | -     | Break | - | - |
| 11:55 | 20  | V    | I     | Traceability: Links, matrices, tools | Demo | Tool, PPT |
| 12:15 | 30  | U    | V     | Hands-on: Create traceability in tool | Individual | Tool |
| 12:45 | 15  | V    | A     | Summary: Key skills gained, next steps | Discussion | Feedback |
```

---

## 4. Task 2: RFP Document Export

### 4.1 Overview

The RFP (Request for Proposal) document consolidates all information gathered across SE-QPT Phases 1-4 into a comprehensive document that can be sent to training service providers.

### 4.2 RFP Document Structure

Based on reference document `SE Qualification Program - Input for identifying training service providers.pdf`:

#### Section 1: Context and Core Concept

| Subsection | Content Source | Description |
|------------|---------------|-------------|
| 1.1 Introduction | Static + Phase 1 | SE Qualification Program overview |
| 1.2 SE Context | Static | V-Model diagram, SE activities definition |
| 1.3 Core Concept | Phase 1 | Curriculum levels (A-D), target personnel types |
| 1.4 Organization Profile | Phase 1 | Maturity level, qualification archetype |

#### Section 2: Service Requirements

| Subsection | Content Source | Description |
|------------|---------------|-------------|
| 2.1 General Service Description | Static | Training module concepts, material creation, alignment process |
| 2.2 Requirements/Constraints | Phase 1 + Config | Trainer requirements, locations, language, group size |
| 2.3 Personnel Subject to Training | Phase 1 | Role clusters, target group sizes per module |
| 2.4 Training Timeline | Phase 3 | Milestone estimates, implementation timeline |

#### Section 3: Training Modules

| Subsection | Content Source | Description |
|------------|---------------|-------------|
| 3.1 Module Overview | Phase 2 + 3 | List of all training modules with competency/level |
| 3.2 Per-Module Details | Phase 2 + 3 + 4 | For each module: Goals, Contents, Learning Format, AVIVA outline |
| 3.3 Participant Estimates | Phase 3 | Estimated participants per module (scaled) |

#### Section 4: Appendices

| Appendix | Content Source | Description |
|----------|---------------|-------------|
| A. Competency Framework | Phase 2 | 16 SE competencies with levels |
| B. Role-Competency Matrix | Phase 1 + 2 | Which roles need which competencies |
| C. AVIVA Detailed Plans | Phase 4 | Full AVIVA Excel exports per module |
| D. Learning Objectives | Phase 2 | Detailed learning objectives |

### 4.3 Export Formats

#### Excel Export

Multi-sheet workbook containing:

| Sheet Name | Content |
|------------|---------|
| **Summary** | Organization info, timeline, key statistics |
| **Modules** | All training modules with formats, participants |
| **Competencies** | Competency framework with levels |
| **Role-Mapping** | Roles to competencies mapping |
| **AVIVA_[Module]** | One sheet per module with AVIVA plan |

#### Word Export

Formatted document following RFP structure:
- Title page with organization info
- Table of contents
- Sections 1-4 as defined above
- Professional formatting for provider review

### 4.4 Data Aggregation

All data consolidated from:

```
Phase 1 Data:
- organization (organization info)
- organization_role_mappings (roles to SE clusters)
- phase_questionnaire_responses (maturity, archetype)

Phase 2 Data:
- user_se_competency_survey_results (competency assessments)
- generated_learning_objectives (learning objectives data)

Phase 3 Data:
- phase3_training_module (modules with formats)
- phase3_timeline (timeline milestones)
- phase3_config (progress tracking)

Phase 4 Data:
- phase4_aviva_plan (AVIVA didactic plans)
- phase4_rfp_export (export history)
```

---

## 5. Content Data Sources

### 5.1 Database Tables Summary

| Table | Key Fields | Phase 4 Usage |
|-------|------------|---------------|
| `phase3_training_module` | competency_id, target_level, selected_format_id, pmt_type | Module list for AVIVA |
| `competency` | competency_name, description | Module naming |
| `competency_indicators` | level, indicator_en | Level-specific learning objectives |
| `learning_format` | format_name, mode_of_delivery | Method/Material adaptation |
| `generated_learning_objectives` | objectives_data (JSONB) | Generated LOs from Phase 2 |
| `competency_content_baseline` (new) | content_topics | Content topics from Excel |

### 5.2 Content Baseline Import

The content topics from Excel Column H need to be imported into a new database table:

```sql
CREATE TABLE competency_content_baseline (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER REFERENCES competency(id),
    content_topics TEXT[],  -- Array of topic strings
    source VARCHAR(100) DEFAULT 'Qualifizierungsmodule_v4',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 AVIVA Template Structure

Source: `data/source/Phase 4/M1+M2 - Konzeption_fein.xlsx`
Sheets: "Vorlage" (Template), "Beispiel" (Example)

Column structure:
1. Start (time)
2. min (duration)
3. Type (V/U/P)
4. WER (Who - optional, not used in SE-QPT)
5. AVIVA (phase)
6. Was (What - content)
7. Wie (How - method)
8. Womit (Material)

### 5.4 RFP Reference Structure

Source: `data/source/Phase 4/SE Qualification Program - Input for identifying training service providers.pdf`

21-page document showing:
- Professional formatting for training provider communication
- Section structure for service requirements
- Module details presentation format
- Personnel/location planning tables

---

## 6. UI/UX Design

### 6.1 Phase 4 Navigation

```
Phase 4: Micro Planning
|
+-- Task 1: AVIVA Planning
|   |-- [Module List Panel]
|   |-- [Learning Objectives Preview Panel]
|   |-- [Content Topics Preview Panel]
|   +-- [Export Options Panel]
|
+-- Task 2: RFP Export
    |-- [Data Summary Panel]
    |-- [Export Format Selection]
    +-- [Download Panel]
```

### 6.2 Task 1: AVIVA Planning UI

#### Main Layout

```
+------------------------------------------------------------------+
| AVIVA Didactics Planning                                          |
+------------------------------------------------------------------+
| Training Modules from Phase 3        | Module Details              |
| +--------------------------------+   | +------------------------+ |
| | [x] Systems Thinking - L1  1h  |   | | Learning Objective:    | |
| | [x] Systems Thinking - L2  2h  |   | | "The participant knows | |
| | [x] Requirements Mgmt - L4 4h  |   | | the interrelationships | |
| | [ ] Architecture - L1      1h  |   | | of their system..."    | |
| +--------------------------------+   | +------------------------+ |
|                                      | | Content Topics:        | |
| Selected: 3 modules                  | | - Motivation for SE    | |
| Total Duration: 7 hours              | | - Definition of terms  | |
|                                      | | - Values of SE         | |
| Export Options:                      | | - SE process models    | |
| +--------------------------------+   | | - SE standards         | |
| | (o) Template Only              |   | +------------------------+ |
| |     (Programmatic + Placeholders)  |                            |
| | ( ) Generate with GenAI        |   |                            |
| |     (Full content generation)  |   |                            |
| +--------------------------------+   |                            |
|                                      |                            |
| [ Export Selected ]  [ Export All ]  |                            |
+------------------------------------------------------------------+
```

#### Learning Objectives Preview

When a module is selected, show:
```
+------------------------------------------+
| Systems Thinking - Level 1 (Knowing)      |
+------------------------------------------+
| LEARNING OBJECTIVE:                       |
| "The participant knows the                |
| interrelationships of their system and    |
| the associated system boundaries."        |
+------------------------------------------+
| CONTENT TOPICS (from baseline):           |
| * Motivation for SE                       |
| * Definition of terms (index)             |
| * Values of SE                            |
| * SE process models (V-model)             |
| * SE standards                            |
+------------------------------------------+
| GENERATED LOs (from Phase 2):             |
| * Understand the role of SE in product... |
| * Recognize system boundaries in...       |
+------------------------------------------+
```

### 6.3 Task 2: RFP Export UI

```
+------------------------------------------------------------------+
| RFP Document Export                                               |
+------------------------------------------------------------------+
| Data Summary                                                      |
| +--------------------------------------------------------------+ |
| | Organization: [Name]                                          | |
| | Maturity Level: [Level]                                       | |
| | Qualification Archetype: [Archetype]                          | |
| | Total Modules: [N]                                            | |
| | Total Estimated Participants: [N]                             | |
| | Timeline: [Start] to [End]                                    | |
| +--------------------------------------------------------------+ |
|                                                                   |
| Export Format:                                                    |
| +--------------------------------------------------------------+ |
| | [x] Excel Workbook (.xlsx)                                    | |
| | [x] Word Document (.docx)                                     | |
| +--------------------------------------------------------------+ |
|                                                                   |
| Include AVIVA Plans: [x] Yes                                      |
|                                                                   |
| [ Preview RFP ]  [ Generate & Download ]                          |
+------------------------------------------------------------------+
```

---

## 7. Data Models

### 7.1 New Tables for Phase 4

#### Table: `phase4_aviva_plan`

```sql
CREATE TABLE phase4_aviva_plan (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id),
    training_module_id INTEGER REFERENCES phase3_training_module(id),
    generated_by VARCHAR(20) CHECK (generated_by IN ('template', 'genai', 'manual')),
    aviva_content JSONB,  -- Full AVIVA plan as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

AVIVA content JSON structure:
```json
{
  "module_name": "Systems Thinking - Knowing",
  "competency_id": 1,
  "target_level": 1,
  "pmt_type": "combined",
  "learning_format": "Seminar",
  "total_duration_minutes": 60,
  "learning_objective": "The participant knows...",
  "content_topics": ["Motivation for SE", "..."],
  "activities": [
    {
      "row": 1,
      "start_time": "09:00",
      "duration_min": 10,
      "type": "V",
      "aviva_phase": "A",
      "content": "Welcome & Introduction: Module objectives and SE importance",
      "method": "Lecture",
      "material": "PowerPoint"
    }
  ]
}
```

#### Table: `phase4_rfp_export`

```sql
CREATE TABLE phase4_rfp_export (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id),
    export_format VARCHAR(20) CHECK (export_format IN ('excel', 'word', 'both')),
    file_path VARCHAR(500),
    export_data JSONB,  -- Snapshot of data at export time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `phase4_config`

```sql
CREATE TABLE phase4_config (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) UNIQUE,
    task1_status VARCHAR(20) DEFAULT 'not_started',
    task2_status VARCHAR(20) DEFAULT 'not_started',
    aviva_generation_method VARCHAR(20),  -- 'template' or 'genai'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `competency_content_baseline`

```sql
CREATE TABLE competency_content_baseline (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER REFERENCES competency(id),
    content_topics TEXT[],  -- Array of topic strings
    source VARCHAR(100) DEFAULT 'Qualifizierungsmodule_v4',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. API Specification

### 8.1 AVIVA Planning Endpoints

#### GET `/api/phase4/aviva/modules`
Get list of modules ready for AVIVA planning.

**Response:**
```json
{
  "modules": [
    {
      "id": 1,
      "competency_id": 1,
      "competency_name": "Systems Thinking",
      "target_level": 1,
      "level_name": "Knowing",
      "pmt_type": "combined",
      "learning_format_id": 1,
      "learning_format_name": "Seminar",
      "mode_of_delivery": "offline",
      "estimated_duration_hours": 1,
      "estimated_participants": 25,
      "has_aviva_plan": false,
      "learning_objective": "The participant knows...",
      "content_topics": ["Motivation for SE", "..."]
    }
  ],
  "total_modules": 15,
  "total_duration_hours": 48
}
```

#### GET `/api/phase4/aviva/module/{module_id}/preview`
Get detailed preview for a single module including all data for AVIVA generation.

**Response:**
```json
{
  "module_id": 1,
  "competency_name": "Systems Thinking",
  "target_level": 1,
  "level_name": "Knowing",
  "pmt_type": "combined",
  "learning_format": {
    "name": "Seminar",
    "mode_of_delivery": "offline",
    "communication_type": "synchronous"
  },
  "learning_objective": "The participant knows the interrelationships...",
  "content_topics": [
    "Motivation for SE",
    "Definition of terms",
    "Values of SE",
    "SE process models (V-model)",
    "SE standards"
  ],
  "generated_learning_objectives": [
    "Understand the role of SE in product development",
    "Recognize system boundaries in their work context"
  ],
  "estimated_duration_hours": 1,
  "suggested_aviva_sequence": [
    {"aviva": "A", "duration": 5, "type": "V"},
    {"aviva": "V", "duration": 10, "type": "U"},
    {"aviva": "I", "duration": 20, "type": "V"},
    {"aviva": "V", "duration": 15, "type": "U"},
    {"aviva": "A", "duration": 10, "type": "V"}
  ]
}
```

#### POST `/api/phase4/aviva/generate`
Generate AVIVA plan(s) for selected modules.

**Request:**
```json
{
  "module_ids": [1, 2, 3],
  "generation_method": "genai",  // or "template"
  "options": {
    "start_time": "09:00",
    "include_breaks": true,
    "lunch_time": "12:30"
  }
}
```

**Response:**
```json
{
  "success": true,
  "plans": [
    {
      "module_id": 1,
      "module_name": "Systems Thinking - Knowing",
      "generation_method": "genai",
      "aviva_content": {
        "total_duration_minutes": 60,
        "activities": [...]
      }
    }
  ],
  "errors": []
}
```

#### GET `/api/phase4/aviva/export`
Export AVIVA plans as Excel.

**Query Parameters:**
- `module_ids`: Comma-separated list (optional, defaults to all)
- `format`: "excel" (default)
- `combined`: "true" to combine all modules in one file, "false" for separate files

**Response:** File download

### 8.2 RFP Export Endpoints

#### GET `/api/phase4/rfp/summary`
Get summary of all data for RFP preview.

**Response:**
```json
{
  "organization": {
    "id": 1,
    "name": "Example Corp",
    "maturity_level": 2,
    "archetype": "common_basic_understanding"
  },
  "statistics": {
    "total_modules": 15,
    "total_participants": 120,
    "total_training_hours": 80,
    "modules_with_aviva": 12
  },
  "timeline": {
    "start_date": "2026-03-01",
    "end_date": "2027-03-01",
    "milestones": [...]
  },
  "phases_complete": {
    "phase1": true,
    "phase2": true,
    "phase3": true,
    "phase4_aviva": true
  }
}
```

#### POST `/api/phase4/rfp/export`
Generate and export RFP document.

**Request:**
```json
{
  "formats": ["excel", "word"],
  "include_aviva": true,
  "options": {
    "language": "en",
    "include_appendices": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "format": "excel",
      "filename": "SE_QPT_RFP_2026-01-21.xlsx",
      "download_url": "/api/phase4/rfp/download/abc123"
    },
    {
      "format": "word",
      "filename": "SE_QPT_RFP_2026-01-21.docx",
      "download_url": "/api/phase4/rfp/download/def456"
    }
  ]
}
```

---

## 9. Phase 4 Outputs

### 9.1 AVIVA Excel Export

Per-module or combined Excel file with:
- Module header (name, duration, learning objective)
- AVIVA-structured activity table
- All 8 columns (Module, Start, Duration, Type, AVIVA, What, How, Material)

### 9.2 RFP Document

Comprehensive document containing:
- Organization context and SE program overview
- Service requirements and constraints
- All training modules with details
- AVIVA plans (if included)
- Appendices with full data

### 9.3 Data Exports

- Phase 4 progress tracking
- Export history for audit trail

---

## 10. Implementation Checklist

### 10.1 Database Setup

- [ ] Create `phase4_aviva_plan` table
- [ ] Create `phase4_rfp_export` table
- [ ] Create `phase4_config` table
- [ ] Create `competency_content_baseline` table
- [ ] Populate content baseline from Excel file (import script)

### 10.2 Backend - AVIVA Generation Engine

- [ ] Implement programmatic AVIVA sequence generator
  - [ ] Level-based sequence templates
  - [ ] Duration calculation logic
  - [ ] Type mapping logic
  - [ ] Method mapping by format
  - [ ] Material mapping by format
- [ ] Implement GenAI content generation
  - [ ] Design and test prompt template
  - [ ] OpenAI API integration
  - [ ] Response parsing and validation
  - [ ] Error handling and fallback
- [ ] Implement AVIVA Excel export
  - [ ] Single module export
  - [ ] Combined multi-module export

### 10.3 Backend - RFP Export

- [ ] Implement RFP summary endpoint
- [ ] Implement RFP Excel export
- [ ] Implement RFP Word export (using python-docx)

### 10.4 Frontend UI

- [ ] Phase 4 navigation/routing
- [ ] Task 1: AVIVA Planning page
  - [ ] Module list component with selection
  - [ ] Learning objectives preview panel
  - [ ] Content topics preview panel
  - [ ] Export options (template vs GenAI)
  - [ ] Progress indicator for GenAI generation
- [ ] Task 2: RFP Export page
  - [ ] Data summary display
  - [ ] Export format selection
  - [ ] Include AVIVA checkbox
  - [ ] Download handling

### 10.5 Testing

- [ ] Test programmatic AVIVA generation for all levels (1, 2, 4, 6)
- [ ] Test GenAI content generation quality
- [ ] Test AVIVA Excel export formatting
- [ ] Test RFP Excel export with all data
- [ ] Test RFP Word export formatting
- [ ] Test with various module counts
- [ ] Integration testing with Phases 1-3 data
- [ ] Performance testing with large organizations

---

## Appendix A: Reference Files

| File | Location | Purpose |
|------|----------|---------|
| AVIVA Template | `data/source/Phase 4/M1+M2 - Konzeption_fein.xlsx` | AVIVA structure reference |
| RFP Sample | `data/source/Phase 4/SE Qualification Program - Input for identifying training service providers.pdf` | RFP format reference |
| Learning Objectives | `data/source/excel/Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx` | Content baseline data |

## Appendix B: AVIVA Methods Reference

| Method (English) | Method (German) | Best For |
|-----------------|-----------------|----------|
| Lecture | Impulsvortrag | I phase, A phase |
| Discussion | Diskussion | V (activate), A phase |
| Individual Exercise | Einzelubung | V (process), online formats |
| Pair Work | Parchenarbeit | V (process), understanding level |
| Group Exercise | Gruppenubung | V (process), applying level |
| Q&A | Abfrage | A phase, V (activate) |
| Hands-on Practice | Praktische Ubung | V (process), applying/mastery |
| Case Study | Fallstudie | V (process), all levels |
| Role Play | Rollenspiel | V (process), communication competencies |
| Demonstration | Demonstration | I phase, tool-focused modules |

## Appendix C: AVIVA Materials Reference

| Material (English) | Material (German) | Format Suitability |
|-------------------|-------------------|-------------------|
| PowerPoint | Powerpoint | All formats |
| Flip-Chart | Flip-Chart | Seminar only |
| Moderation Cards | Moderationskarten | Seminar only |
| Whiteboard/Pinboard | Pinnwand | Seminar, Hybrid |
| Exercise Sheets | Ubungsblatter | All formats (PDF for online) |
| Handbook | Handbuch | All formats |
| Digital Collaboration Tool | Conceptboard/Miro | Online, Hybrid |
| Screen Share | Bildschirmfreigabe | Webinar, WBT |
| Polls/Quiz | Umfragen/Quiz | Online formats |
| Video | Video | WBT, Blended |
| LMS Module | LMS-Modul | WBT |

## Appendix D: GenAI Prompt Template (Full)

```
You are creating AVIVA didactic content for a Systems Engineering training module.

== MODULE CONTEXT ==
Module: {competency_name} - Level {target_level} ({level_name})
PMT Focus: {pmt_type}
Learning Format: {format_name} ({mode_of_delivery})
Total Duration: {total_duration_minutes} minutes

== LEARNING OBJECTIVE (Level-Specific) ==
{level_specific_learning_objective}

== CONTENT TOPICS (Baseline for this Competency) ==
{content_topics_list}

== ORGANIZATION-SPECIFIC LEARNING OBJECTIVES (from Phase 2) ==
{organization_specific_learning_objectives}

== AVIVA SEQUENCE TO GENERATE CONTENT FOR ==
{aviva_sequence_json}

== INSTRUCTIONS ==
Generate specific, actionable content for the "What (Content)" column for each activity row.

Guidelines:
1. A (Arrive): Welcome, set expectations, preview what participants will learn
2. V (Activate Prior Knowledge): Questions or discussion prompts to surface existing knowledge
3. I (Inform): Specific topic from content list - adapt depth based on level:
   - Level 1 (Know): Overview, definitions, awareness
   - Level 2 (Understand): Explanations, connections, examples
   - Level 4 (Apply): Practical application, hands-on guidance
   - Level 6 (Mastery): Strategic thinking, teaching others, optimization
4. V (Process): Concrete exercise description tied to the previous I block
5. A (Evaluate): Summary activity, key takeaways, reflection questions

Keep each content description to 1-2 sentences. Be specific to the competency and level.

== OUTPUT FORMAT ==
Return a JSON array:
[
  {"row": 1, "content": "Welcome: Introduction to {competency_name} module and learning objectives"},
  {"row": 2, "content": "Discussion: What experience do you have with {topic}?"},
  ...
]
```
