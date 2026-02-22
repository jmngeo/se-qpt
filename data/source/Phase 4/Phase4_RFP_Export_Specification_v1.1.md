# Phase 4: RFP Document Export - Design Specification v1.1

## Document Information
- **Module**: Phase 4 - Micro Planning / Task 2: RFP Export
- **Feature**: LLM-Enhanced RFP Document Generation
- **Based on**: ZEISS RFP Reference, Ulf's Meeting Notes (11.12.2025)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 1.1
- **Date**: January 2026
- **Change Log**: Added Ulf's requirements, content baseline details, updated section mappings

---

## Table of Contents

1. [Overview](#1-overview)
2. [ZEISS Reference Document Analysis](#2-zeiss-reference-document-analysis)
3. [RFP Sections Specification](#3-rfp-sections-specification)
4. [Data Sources by Section](#4-data-sources-by-section)
5. [LLM Generation Specifications](#5-llm-generation-specifications)
6. [Content Baseline for Modules](#6-content-baseline-for-modules)
7. [Export Formats](#7-export-formats)
8. [UI/UX Design](#8-uiux-design)
9. [Implementation Status](#9-implementation-status)

---

## 1. Overview

### 1.1 Purpose

The RFP (Request for Proposal) Export feature generates a comprehensive document consolidating all organization-specific data from SE-QPT Phases 1-4. This document is designed to be sent to training service providers to request proposals for delivering the SE qualification program.

**Quote from Ulf (Meeting 11.12.2025):**
> "Our app's final output should be similar to this document [ZEISS RFP] and we can use LLM to generate something similar. We generate it as the last step of our app where we can call it as 'Generate a Request for Proposal'."

### 1.2 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Hybrid Generation** | Data-driven tables + LLM-generated prose/narratives |
| **User Choice** | Option to generate with or without LLM enhancement |
| **Professional Output** | RFP-quality document suitable for external providers |
| **Comprehensive** | All relevant data from Phases 1-4 consolidated |
| **Multiple Formats** | Export to Excel (data-only), Word/PDF (LLM-enhanced) |

### 1.3 Export Modes

| Format | Generation Mode | Use Case |
|--------|-----------------|----------|
| **Excel (.xlsx)** | Data-Only | Quick export, internal review, data analysis |
| **Word (.docx)** | LLM-Enhanced | Professional RFP document for providers |
| **PDF (.pdf)** | LLM-Enhanced | Final printable version |

### 1.4 Position in SE-QPT Workflow

```
Phase 1: Prepare SE Training
    ↓ Outputs: Maturity, Roles, Strategies, Target Group Size
Phase 2: Identify Requirements
    ↓ Outputs: Competency Gaps, Learning Objectives, PMT Context
Phase 3: Macro Planning
    ↓ Outputs: Training Modules, Formats, Timeline
Phase 4: Micro Planning
    |
    |-- Task 1: AVIVA Didactics Planning
    |
    +-- Task 2: RFP Document Export  <-- THIS FEATURE
        |
        +-- Consolidate all Phase 1-4 data
        +-- Generate LLM-enhanced content (Word/PDF only)
        +-- Export to Excel/Word/PDF
```

---

## 2. ZEISS Reference Document Analysis

### 2.1 Reference Document
- **File**: `SE Qualification Program - Input for identifying training service providers.pdf`
- **Source**: ZEISS Medical Technology (MED)
- **Pages**: 21 pages

### 2.2 Document Structure Mapping

| ZEISS Page | Section Title | SE-QPT Equivalent |
|------------|---------------|-------------------|
| p3 | Context (V-Model) | Static SE reference diagram |
| p4 | Core Concept | Organization-specific narrative |
| p6 | Service Description - General | Service requirements |
| p7 | Service Description - Requirements/Constraints | Training constraints |
| p8 | Service Description - Personnel Subject to Training | Roles & participant counts |
| p10 | Key Competencies | Competency list |
| p11-20 | Training Module Details (RqE1, RqE2, SyA1, etc.) | Module Goals & Contents |

### 2.3 Key Observations from ZEISS Document

1. **Document is DATA-HEAVY with minimal prose** - Only Page 4 has a real narrative paragraph
2. **Module sections follow a consistent pattern**:
   - Goals: 3-5 bullet points starting with "Understanding..." or "Applying..."
   - Contents: Numbered list of 6-10 topics
3. **Goals are LEVEL-APPROPRIATE**:
   - Level A (Knowing/Understanding): "Understanding the role of...", "Understanding how..."
   - Level B: "Understanding the relations...", "Understanding the levels..."
   - Level C (Applying): "Understanding how to...", "Procedure for..."

---

## 3. RFP Sections Specification

### 3.1 Complete Section Mapping

Based on Ulf's meeting (11.12.2025) and ZEISS reference analysis:

| Section | ZEISS Page | Generation Method | Data Source | Notes |
|---------|------------|-------------------|-------------|-------|
| **Context** | p3 | Static Template | N/A | Generalized SE/V-Model diagram |
| **Core Concept** | p4 | **LLM Generated** | org profile, roles, strategies | Organization-specific narrative |
| **Service Description - General** | p6 | Template + LLM | PMT context, formats | Only for high maturity orgs |
| **Service Description - Requirements** | p7 | Template + Conditional | formats, PMT tools | See detailed breakdown |
| **Personnel Subject to Training** | p8 | **Data Only** | roles, scaled participants | Participant matrix |
| **Key Competencies** | p10 | **Data Only** | training modules | List of competencies |
| **Module Details** | p11-20 | **LLM for Goals/Contents** | modules, content baseline | Per-module sections |

### 3.2 Service Description - Requirements/Constraints Detail

From Ulf's meeting notes:

| Point | Content | Method | Condition |
|-------|---------|--------|-----------|
| 1 | "Trainer shall be proficient in SE..." | **Static template** | Always |
| 2 | "Trainer able to delve into [Org] processes" | **LLM using PMT data** | If PMT processes exist |
| 3 | "Travel to locations..." | **Conditional on format** | Seminar = travel needed, E-learning = no travel |
| 4 | "Training material in English" | **Static template** | Always |
| 5 | "Hands-on exercises with tools" | **From PMT tools** | If tools defined (e.g., "Polarion, Enterprise Architect") |
| 6 | "Training group size" | **From learning format** | Max participants from format selection |
| 7 | "Timeline constraint" | **From Phase 3 timeline** | Start/end dates |

### 3.3 Module Details Section Structure

For each training module, generate:

```
Training Module: [Competency Name] - [Level Name]
Target Level: [Level A/B/C/D] ([Knowing/Understanding/Applying/Mastering])
Target Audience: [Training Program Cluster] (if role-clustered view)

Goals
• [LLM-generated goal 1 - level-appropriate verb]
• [LLM-generated goal 2]
• [LLM-generated goal 3]
• [LLM-generated goal 4]

Contents
1. [LLM-generated content topic 1]
2. [LLM-generated content topic 2]
   a. Sub-topic
   b. Sub-topic
3. [LLM-generated content topic 3]
...
```

---

## 4. Data Sources by Section

### 4.1 Phase 1 Data Sources

| Data Element | Table | Fields | Used In |
|--------------|-------|--------|---------|
| Organization Profile | `organization` | `organization_name`, `maturity_score` | Core Concept, Summary |
| Maturity Score | `organization` | `maturity_score` | Core Concept |
| 4 Fields of Action | `phase_questionnaire_responses` | `responses` (JSONB) | Maturity section |
| Target Group Size | `phase_questionnaire_responses` | `responses.value` | Personnel scaling |
| Selected Strategies | `learning_strategy` | `strategy_template_id`, `selected` | Core Concept, Service Desc |
| Organization Roles | `organization_roles` | `role_name`, `training_program_cluster_id` | Personnel section |

### 4.2 Phase 2 Data Sources

| Data Element | Table | Fields | Used In |
|--------------|-------|--------|---------|
| Competency Gaps | `generated_learning_objectives` | `objectives_data` | Gap summary |
| PMT Context | `organization_pmt_context` | `processes`, `methods`, `tools`, `industry` | Service Description |
| Learning Objectives | `generated_learning_objectives` | `objectives_data.main_pyramid.levels` | Module Goals |
| Existing Trainings | `organization_existing_trainings` | `competency_id`, `covered_levels` | Coverage section |

### 4.3 Phase 3 Data Sources

| Data Element | Table | Fields | Used In |
|--------------|-------|--------|---------|
| Training Modules | `phase3_training_module` | All fields | Module Details |
| Phase 3 Config | `phase3_config` | `selected_view`, `scaling_factor` | Personnel scaling |
| Timeline | `phase3_timeline` | `milestones` | Timeline section |
| Learning Formats | `learning_format` | `format_name`, `max_participants` | Service Requirements |

### 4.4 Reference Data Sources

| Data Element | Table | Fields | Used In |
|--------------|-------|--------|---------|
| Competencies | `competency` | `competency_name`, `competency_area` | All sections |
| **Content Topics** | `competency_content_baseline` | `content_topics[]` | **Module Contents** |
| Competency Indicators | `competency_indicators` | `level`, `indicator_en` | Module Goals |
| Training Program Clusters | `training_program_cluster` | `training_program_name` | Personnel grouping |

---

## 5. LLM Generation Specifications

### 5.1 LLM-Generated Sections Summary

| Section | LLM Required | Input Data | Output Length |
|---------|--------------|------------|---------------|
| Core Concept | **Yes** | org, roles, strategies, target_size | 2 paragraphs (~150-200 words) |
| Service Description - General | **Yes** | PMT context, formats, AVIVA status | 5-7 bullet points |
| Service Description - Requirements | **Partial** | formats, tools, timeline | Template + conditionals |
| Module Goals | **Yes** | competency, level, learning_objective | 3-5 bullets per module |
| Module Contents | **Yes** | content_topics[], level, org_tools | 6-10 numbered items per module |

### 5.2 Core Concept Generation

**Purpose**: Generate organization-specific narrative introducing the SE qualification initiative.

**Input Data**:
```json
{
  "organization_name": "Example Corp",
  "industry": "Medical Devices",
  "maturity_level": 3,
  "maturity_score": 62,
  "primary_strategy": "Needs-Based Qualification",
  "secondary_strategies": ["SE for Managers"],
  "total_target_group": 150,
  "role_count": 8,
  "core_personnel": ["Systems Engineers", "Requirements Engineers", "System Architects"]
}
```

**Prompt Template**:
```
You are writing a Core Concept section for a Systems Engineering Qualification Program RFP document.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Industry: {industry}
- SE Maturity Level: {maturity_level}/5 (Score: {maturity_score}/100)

QUALIFICATION PROGRAM SCOPE:
- Target Personnel: {total_target_group} employees
- Roles Identified: {role_count}
- Core Personnel to be Trained: {core_personnel}

SELECTED STRATEGIES:
- Primary: {primary_strategy}
- Secondary: {secondary_strategies}

Write a Core Concept section (2 paragraphs, ~150-200 words) that:
1. Introduces the organization's SE qualification initiative
2. Explains the systematic approach to equip personnel with SE capabilities
3. Lists the core personnel to be trained

Use formal business language appropriate for an RFP document.
End with: "The core personnel to be trained include: [list roles]"
```

### 5.3 Module Goals Generation

**Purpose**: Generate reader-friendly "Goals" bullet points for each training module.

**Input Data**:
```json
{
  "competency_name": "Requirements Definition",
  "target_level": 4,
  "level_name": "Applying",
  "pmt_type": "method",
  "learning_objective": "The participant can independently identify sources of requirements, derive requirements, document and link them.",
  "content_topics": ["Requirements process", "Stakeholder analysis", "Types of requirements", ...]
}
```

**Level-Appropriate Verbs**:
- Level 1 (Knowing): "Understanding...", "Knowing...", "Being aware of..."
- Level 2 (Understanding): "Understanding...", "Comprehending...", "Explaining..."
- Level 4 (Applying): "Applying...", "Being able to...", "Performing..."
- Level 6 (Mastering): "Mastering...", "Optimizing...", "Teaching..."

**Prompt Template**:
```
Generate 3-5 reader-friendly "Goals" bullet points for this training module:

MODULE: {competency_name} - {level_name}
TARGET LEVEL: {target_level} ({level_name})
PMT FOCUS: {pmt_type}

LEARNING OBJECTIVE (formal):
{learning_objective}

CONTENT TOPICS:
{content_topics}

Guidelines:
1. Start each bullet with level-appropriate verb:
   - Level 1-2: "Understanding...", "Knowing..."
   - Level 4: "Applying...", "Being able to..."
   - Level 6: "Mastering...", "Optimizing..."
2. Keep each bullet concise (one line)
3. Cover main learning outcomes
4. Be appropriate for {pmt_type} focus

Output as bullet points only.
```

### 5.4 Module Contents Generation

**Purpose**: Generate structured content outline for each training module.

**Input Data**:
```json
{
  "competency_name": "Requirements Definition",
  "target_level": 4,
  "level_name": "Applying",
  "pmt_type": "method",
  "duration_hours": 8,
  "content_topics": [
    "The requirements process in the company",
    "Identification and analysis of all stakeholders",
    "Types of requirements and needs",
    ...
  ],
  "organization_tools": ["Polarion"],
  "learning_format": "Seminar"
}
```

**Prompt Template**:
```
Generate a numbered content outline for this training module:

MODULE: {competency_name} - {level_name}
TARGET LEVEL: {target_level} ({level_name})
PMT FOCUS: {pmt_type}
DURATION: {duration_hours} hours
FORMAT: {learning_format}

CONTENT TOPICS (baseline from Qualifizierungsmodule):
{content_topics}

ORGANIZATION TOOLS: {organization_tools}

Guidelines:
1. Organize topics into logical training sequence (6-10 main items)
2. Include sub-topics where appropriate (a, b, c)
3. Adjust depth based on Level {target_level}:
   - Level 1: Overview, definitions, basic concepts
   - Level 2: Concepts, relationships, examples
   - Level 4: Hands-on application, tool usage, practical exercises
   - Level 6: Advanced techniques, optimization, mentoring
4. Reference organization tools ({organization_tools}) in practical sections
5. Start with Recap/Introduction, end with Summary/Application
6. Make realistic for {duration_hours} hours

Output as numbered list with sub-items.
```

---

## 6. Content Baseline for Modules

### 6.1 Source

The `competency_content_baseline` table stores content topics per competency, sourced from:
- **File**: Qualifizierungsmodule_v4.xlsx (Column H)
- **Table**: `competency_content_baseline`
- **Migration**: `022_phase4_aviva_tables.sql`

### 6.2 Content Topics per Competency

| Competency | Topic Count | Sample Topics |
|------------|-------------|---------------|
| **Systems Thinking** | 6 | Motivation for SE, SE process models (V-model), SE standards |
| **Lifecycle Consideration** | 4 | Life cycle phases, Operating costs, End-of-life considerations |
| **Customer/Value Orientation** | 4 | Agile Manifesto, Customer-centric thinking, Value-driven development |
| **Systems Modelling and Analysis** | 4 | Model theory, Simulation, MBSE |
| **Communication** | 8 | Stakeholder-oriented communication, Negotiation technique, Feedback rules |
| **Leadership** | 7 | Team leadership, Situational leadership theory, Leadership styles |
| **Self-Organization** | 5 | Time management, Goal setting, Self-motivation techniques |
| **Project Management** | 13 | WBS, Schedule/budget plan, KPIs, Reporting |
| **Decision Management** | 8 | Decision strategy, Risk identification, Preventive measures |
| **Information Management** | 5 | Communication planning, Knowledge management systems |
| **Configuration Management** | 7 | Configuration control, Baselines, Change management |
| **Requirements Definition** | 17 | Requirements process, Stakeholder analysis, Traceability, Use cases |
| **System Architecting** | 9 | Functional/logical architecture, Synthesis, Interface design |
| **Integration, Verification, Validation** | 10 | IVV definition, V&V methods, Final acceptance |
| **Operation and Support** | 10 | Operating strategies, Maintenance, Disposal strategy |
| **Agile Methods** | 5 | Scrum, SAFe, Sprint planning |

### 6.3 Usage in RFP Generation

1. **AVIVA Content Generation**: Already uses these topics as baseline
2. **RFP Module Contents**: LLM expands these topics into structured outline
3. **Level Adaptation**: Topics are filtered/expanded based on target level

### 6.4 Database Query

```sql
SELECT c.competency_name, ccb.content_topics
FROM competency_content_baseline ccb
JOIN competency c ON ccb.competency_id = c.id
WHERE ccb.competency_id = :competency_id;
```

---

## 7. Export Formats

### 7.1 Format Comparison

| Aspect | Excel (.xlsx) | Word (.docx) | PDF (.pdf) |
|--------|---------------|--------------|------------|
| **Generation Mode** | Data-Only | LLM-Enhanced | LLM-Enhanced |
| **Use Case** | Internal review, data analysis | Professional RFP | Final printable |
| **LLM Content** | No | Yes | Yes |
| **Narrative Sections** | No | Yes | Yes |
| **Module Goals/Contents** | Data columns only | Full generated text | Full generated text |
| **Tables** | Full data tables | Summary tables | Summary tables |
| **Editable** | Yes | Yes | No |

### 7.2 Excel Structure (Data-Only)

```
SE_QPT_RFP_{OrgName}_{Date}.xlsx
│
├── Sheet 1: "Summary" - Organization profile, key metrics
├── Sheet 2: "Maturity Assessment" - 4 Fields of Action
├── Sheet 3: "Organization Roles" - Role inventory
├── Sheet 4: "Training Modules" - All modules with formats
├── Sheet 5: "Timeline" - Implementation milestones
└── Sheet 6: "Role-Competency Matrix" (if role-based)
```

### 7.3 Word/PDF Structure (LLM-Enhanced)

```
SE_QPT_RFP_{OrgName}_{Date}.docx
│
├── Title Page
├── Table of Contents
│
├── PART 1: CONTEXT AND CORE CONCEPT
│   ├── 1.1 Context (SE V-Model diagram - static)
│   └── 1.2 Core Concept [LLM GENERATED]
│
├── PART 2: SERVICE REQUIREMENTS
│   ├── 2.1 Service Description - General [LLM + Template]
│   ├── 2.2 Requirements and Constraints [Template + Conditional]
│   └── 2.3 Personnel Subject to Training [Data Table]
│
├── PART 3: TRAINING PROGRAM
│   ├── 3.1 Key Competencies [Data List]
│   ├── 3.2 Training Structure Overview [Data Table]
│   └── 3.3 Timeline [Data Table]
│
├── PART 4: TRAINING MODULE DETAILS
│   └── For each module:
│       ├── Module Header [Data]
│       ├── Goals [LLM GENERATED]
│       └── Contents [LLM GENERATED]
│
└── APPENDICES (optional)
    ├── A. SE Competency Framework
    └── B. Learning Formats Reference
```

---

## 8. UI/UX Design

### 8.1 Export Options Layout

```
+------------------------------------------------------------------+
| RFP Document Export                                               |
+------------------------------------------------------------------+
|                                                                   |
| Export Format                                                     |
| +---------------------------------------------------------------+ |
| | [x] Excel Workbook (.xlsx)                                    | |
| |     Data tables only - for internal review and analysis       | |
| +---------------------------------------------------------------+ |
|                                                                   |
| +---------------------------------------------------------------+ |
| | --- GenAI Enhanced Documents ---                              | |
| |                                                                | |
| | [ ] Word Document (.docx)                                     | |
| |     Professional RFP with AI-generated narratives             | |
| |                                                                | |
| | [ ] PDF Document (.pdf)                                       | |
| |     Final printable version                                   | |
| |                                                                | |
| | Note: Word/PDF exports use AI to generate:                    | |
| | - Core Concept narrative                                      | |
| | - Service Description requirements                            | |
| | - Module Goals and Contents outlines                          | |
| +---------------------------------------------------------------+ |
|                                                                   |
| [ Export Selected Formats ]                                       |
|                                                                   |
+------------------------------------------------------------------+
```

### 8.2 Generation Progress (for Word/PDF)

```
+------------------------------------------+
| Generating RFP Document                   |
+------------------------------------------+
|                                          |
| [=========>                    ] 36%     |
|                                          |
| Current Step: Generating module contents |
| Module: Requirements Definition          |
|                                          |
| Steps Completed: 8 / 22                  |
|                                          |
| [Cancel]                                 |
+------------------------------------------+
```

---

## 9. Implementation Status

### 9.1 Current Status (as of January 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| **Excel Export** | Complete | Data-only, all sheets working |
| **Word Export** | Not Started | Requires python-docx, LLM integration |
| **PDF Export** | Not Started | Requires Word export first |
| **LLM Generation** | Not Started | Core Concept, Module Goals/Contents |
| **Frontend UI** | Partial | Only Excel button, needs format selection |

### 9.2 Implementation Checklist

#### Backend
- [x] Data aggregation methods (all phases)
- [x] Excel export (data-only)
- [ ] LLM prompt templates
- [ ] Core Concept generation
- [ ] Service Description generation
- [ ] Module Goals generation
- [ ] Module Contents generation
- [ ] Word document builder (python-docx)
- [ ] PDF generation (from Word)
- [ ] Async generation with progress

#### Frontend
- [x] RFP preview panel
- [x] Basic Excel export button
- [ ] Format selection (Excel/Word/PDF)
- [ ] GenAI section grouping
- [ ] Generation progress modal
- [ ] Download ready modal

### 9.3 Dependencies

```txt
# Current
openpyxl==3.1.2          # Excel generation

# Required for Word/PDF
python-docx==0.8.11      # Word document generation
openai>=1.0.0            # LLM API (already present for AVIVA)
```

---

## Appendix A: Meeting Notes Reference

### Ulf's Key Quotes (Meeting 11.12.2025)

1. **On Final Output**:
   > "Our app's final output should be similar to this document [ZEISS RFP] and we can use LLM to generate something similar."

2. **On Core Concept**:
   > "When we talk about the Core Concept section, it is something very organisation specific that's tailored to their context. We can maybe generate something similar using GenAI LLM based."

3. **On Service Description**:
   > "The line 'Alignment with ZEISS regarding training contents and modalities' - this would be shown only for high maturity organisations as we are asking the org to input their PMT data only for high maturity pathway."

4. **On Travel Requirements**:
   > "If it's e-learning format, then we can say that travel is not needed. If it's seminar format, then we can say that travel is needed."

5. **On Module Details**:
   > "Then we need the rest of the pages - The Key Competencies, The overview of each of the Training modules with their Goals and Contents."

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Jomon George | Initial specification |
| 1.1 | 2026-01-31 | Jomon George | Added Ulf's requirements (11.12.2025), content baseline details, updated section mappings, implementation status |
