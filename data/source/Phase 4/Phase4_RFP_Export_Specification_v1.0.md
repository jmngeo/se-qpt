# Phase 4: RFP Document Export - Design Specification v1.0

## Document Information
- **Module**: Phase 4 - Micro Planning / Task 2: RFP Export
- **Feature**: LLM-Enhanced RFP Document Generation
- **Based on**: ZEISS RFP Reference, Phase4_Micro_Planning_Specification_v1.1.md
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 1.0
- **Date**: January 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Document Structure](#2-document-structure)
3. [Data Sources by Section](#3-data-sources-by-section)
4. [LLM Generation Specifications](#4-llm-generation-specifications)
5. [Data Models](#5-data-models)
6. [API Specification](#6-api-specification)
7. [Export Formats](#7-export-formats)
8. [UI/UX Design](#8-uiux-design)
9. [Implementation Checklist](#9-implementation-checklist)

---

## 1. Overview

### 1.1 Purpose

The RFP (Request for Proposal) Export feature generates a comprehensive document consolidating all organization-specific data from SE-QPT Phases 1-4. This document is designed to be sent to training service providers to request proposals for delivering the SE qualification program.

### 1.2 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Hybrid Generation** | Data-driven tables + LLM-generated prose/narratives |
| **User Choice** | Option to generate with or without LLM enhancement |
| **Professional Output** | RFP-quality document suitable for external providers |
| **Comprehensive** | All relevant data from Phases 1-4 consolidated |
| **Multiple Formats** | Export to Excel, Word, and PDF |

### 1.3 Generation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **LLM-Enhanced** | Full document with AI-generated narratives, goals, content outlines | Professional RFP for providers |
| **Data-Only** | Raw data export with minimal templating | Quick export, internal review |

### 1.4 Position in SE-QPT Workflow

```
Phase 1: Prepare SE Training
    ↓ Outputs: Maturity, Roles, Strategies, Target Group Size
Phase 2: Identify Requirements
    ↓ Outputs: Competency Gaps, Learning Objectives
Phase 3: Macro Planning
    ↓ Outputs: Training Modules, Formats, Timeline
Phase 4: Micro Planning
    |
    |-- Task 1: AVIVA Didactics Planning
    |
    +-- Task 2: RFP Document Export  <-- THIS FEATURE
        |
        +-- Consolidate all Phase 1-4 data
        +-- Generate LLM-enhanced content
        +-- Export to Word/Excel/PDF
```

---

## 2. Document Structure

### 2.1 Complete RFP Document Outline

```
SE QUALIFICATION PROGRAM
Request for Proposal - [Organization Name]
Generated: [Date]

═══════════════════════════════════════════════════════════════════

PART 1: CONTEXT AND CORE CONCEPT
├── 1.1 Executive Summary                          [LLM Generated]
├── 1.2 Organization Profile                       [Data]
├── 1.3 SE Maturity Assessment Results             [Data + LLM Summary]
├── 1.4 Qualification Strategy Selection           [Data + LLM Rationale]
└── 1.5 Curriculum Overview                        [Template]

PART 2: SERVICE REQUIREMENTS
├── 2.1 Service Description                        [LLM Generated]
├── 2.2 Requirements and Constraints               [Data + Template]
├── 2.3 Personnel Subject to Training              [Data Tables]
│   ├── 2.3.1 Target Group Summary
│   ├── 2.3.2 Role Inventory
│   └── 2.3.3 Personnel by Module Matrix
└── 2.4 Training Timeline                          [Data Table]

PART 3: TRAINING PROGRAM STRUCTURE
├── 3.1 Competency Gaps Summary                    [Data + LLM Analysis]
├── 3.2 Training Structure Overview                [Data Table]
├── 3.3 Learning Formats Distribution              [Data Table]
└── 3.4 Existing Training Coverage                 [Data Table]

PART 4: TRAINING MODULE DETAILS
└── For each module:
    ├── Module Header                              [Data]
    ├── Goals                                      [LLM Generated]
    ├── Contents Outline                           [LLM Generated]
    ├── AVIVA Didactic Plan (if available)         [Data + LLM Content]
    └── Suitability Analysis                       [Data]

PART 5: APPENDICES
├── A. SE Competency Framework                     [Reference Data]
├── B. Role-Competency Matrix                      [Data]
├── C. PMT Context Details                         [Data]
├── D. Learning Formats Reference                  [Reference Data]
└── E. Glossary                                    [Reference Data]

═══════════════════════════════════════════════════════════════════
```

### 2.2 Section Generation Summary

| Section | Generation Method | LLM Model | Est. Tokens |
|---------|-------------------|-----------|-------------|
| 1.1 Executive Summary | LLM | gpt-4o-mini | ~500 |
| 1.3 Maturity Summary | LLM | gpt-4o-mini | ~200 |
| 1.4 Strategy Rationale | LLM | gpt-4o-mini | ~200 |
| 2.1 Service Description | LLM | gpt-4o-mini | ~300 |
| 3.1 Gap Analysis | LLM | gpt-4o-mini | ~300 |
| 4.x Module Goals (per module) | LLM | gpt-4o-mini | ~150 each |
| 4.x Module Contents (per module) | LLM | gpt-4o-mini | ~250 each |
| **Total (15 modules)** | | | **~7,500** |

---

## 3. Data Sources by Section

### 3.1 Phase 1 Data Sources

| Data Element | Table | Fields |
|--------------|-------|--------|
| Organization Profile | `organization` | `organization_name`, `created_at` |
| Maturity Score | `organization` | `maturity_score` |
| 4 Fields of Action | `phase_questionnaire_responses` | `computed_scores` (JSONB) |
| Target Group Size | `phase_questionnaire_responses` | `computed_scores.training_target_group_size` |
| Selected Strategies | `learning_strategy` | `strategy_template_id`, `selected`, `priority` |
| Organization Roles | `organization_roles` | `role_name`, `role_description`, `standard_role_cluster_id`, `training_program_cluster_id` |
| Role-Process Matrix | `role_process_matrix` | `role_id`, `process_id`, `involvement_level` |
| Role-Competency Matrix | `role_competency_matrix` | `role_id`, `competency_id`, `required_level` |

### 3.2 Phase 2 Data Sources

| Data Element | Table | Fields |
|--------------|-------|--------|
| Assessment Results | `user_se_competency_survey_results` | `competency_id`, `score`, `target_level` |
| Generated LOs | `generated_learning_objectives` | `objectives_data` (JSONB) |
| PMT Context | `organization_pmt_context` | `processes`, `methods`, `tools`, `industry` |
| Existing Trainings | `organization_existing_trainings` | `competency_id`, `covered_levels` |

### 3.3 Phase 3 Data Sources

| Data Element | Table | Fields |
|--------------|-------|--------|
| Phase 3 Config | `phase3_config` | `selected_view`, `actual_assessed_users`, `target_group_size`, `scaling_factor` |
| Training Modules | `phase3_training_module` | `competency_id`, `target_level`, `pmt_type`, `selected_format_id`, `estimated_participants`, `confirmed` |
| Timeline | `phase3_timeline` | `milestone_order`, `milestone_name`, `estimated_date`, `quarter` |

### 3.4 Phase 4 Data Sources

| Data Element | Table | Fields |
|--------------|-------|--------|
| AVIVA Plans | `phase4_aviva_plan` | `training_module_id`, `aviva_content` (JSONB) |
| RFP Export History | `phase4_rfp_export` | `export_format`, `export_data` |

### 3.5 Reference Data Sources

| Data Element | Table | Fields |
|--------------|-------|--------|
| Competencies | `competency` | `competency_name`, `competency_area`, `description` |
| Competency Indicators | `competency_indicators` | `competency_id`, `level`, `indicator_en` |
| Content Topics | `competency_content_baseline` | `competency_id`, `content_topics` |
| Strategy Templates | `strategy_template` | `strategy_name`, `description` |
| Learning Formats | `learning_format` | `format_name`, `mode_of_delivery`, `max_participants` |
| Training Program Clusters | `training_program_cluster` | `training_program_name` |

---

## 4. LLM Generation Specifications

### 4.1 Executive Summary Generation

**Purpose**: Generate a professional introduction paragraph for the RFP document.

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
  "total_modules": 18,
  "total_training_hours": 92,
  "assessment_pathway": "ROLE_BASED",
  "role_count": 8,
  "competency_gaps_count": 45
}
```

**Prompt Template**:
```
You are writing an executive summary for a Systems Engineering Qualification Program RFP document.

ORGANIZATION CONTEXT:
- Organization: {organization_name}
- Industry: {industry}
- SE Maturity Level: {maturity_level}/5 (Score: {maturity_score}/100)
- Assessment Approach: {assessment_pathway}

QUALIFICATION PROGRAM SCOPE:
- Target Personnel: {total_target_group} employees
- Roles Defined: {role_count}
- Competency Gaps Identified: {competency_gaps_count}
- Training Modules Required: {total_modules}
- Total Training Hours: {total_training_hours}

SELECTED STRATEGIES:
- Primary: {primary_strategy}
- Secondary: {secondary_strategies}

Write a professional executive summary (2-3 paragraphs, ~150-200 words) that:
1. Introduces the organization's SE qualification initiative
2. Summarizes the scope and approach
3. States the purpose of the RFP (seeking training providers)

Use formal business language appropriate for an RFP document.
Do not use bullet points - write in prose paragraphs.
Do not include specific numbers in the summary - keep it high-level.
```

**Expected Output** (~150-200 words):
```
[Organization Name] is undertaking a strategic initiative to strengthen Systems
Engineering capabilities across the organization. This qualification program aims
to equip engineering personnel with the competencies required to excel in complex
system development projects, promoting standardization and best practices.

Based on a comprehensive maturity assessment and competency gap analysis, a
structured training program has been designed following a [primary strategy]
approach. The program addresses identified gaps across technical, management,
and social/personal competency areas, with training modules tailored to different
role clusters and proficiency levels.

This Request for Proposal seeks qualified training service providers to deliver
the defined training modules. Providers should demonstrate expertise in Systems
Engineering education and the ability to create customized training materials
aligned with [Organization Name]'s processes, methods, and tools.
```

---

### 4.2 Maturity Assessment Summary Generation

**Purpose**: Generate a brief narrative interpretation of the maturity assessment results.

**Input Data**:
```json
{
  "overall_score": 62,
  "overall_level": 3,
  "fields_of_action": {
    "rollout_scope": {"score": 3, "answer": "Defined for specific departments"},
    "se_roles_processes": {"score": 4, "answer": "Defined and established"},
    "se_mindset": {"score": 2, "answer": "Partially accepted"},
    "knowledge_base": {"score": 3, "answer": "Documented but not centralized"}
  },
  "assessment_pathway": "ROLE_BASED",
  "pathway_reason": "SE Roles & Processes are defined and established"
}
```

**Prompt Template**:
```
You are interpreting SE maturity assessment results for an RFP document.

MATURITY ASSESSMENT RESULTS:
- Overall Score: {overall_score}/100 (Level {overall_level}/5)

4 FIELDS OF ACTION:
1. Rollout Scope: Level {rollout_scope.score} - "{rollout_scope.answer}"
2. SE Roles & Processes: Level {se_roles_processes.score} - "{se_roles_processes.answer}"
3. SE Mindset: Level {se_mindset.score} - "{se_mindset.answer}"
4. Knowledge Base: Level {knowledge_base.score} - "{knowledge_base.answer}"

RESULTING PATHWAY: {assessment_pathway}
Reason: {pathway_reason}

Write a brief summary (2-3 sentences) interpreting these results for the RFP reader.
Highlight the strongest and weakest areas.
Explain why the {assessment_pathway} pathway was selected.
```

**Expected Output** (~50-75 words):
```
The organization demonstrates moderate SE maturity with established roles and
processes (the strongest area), enabling a role-based competency assessment
approach. Areas for development include SE mindset adoption and knowledge base
centralization. The qualification program addresses these gaps through targeted
training aligned with defined role requirements.
```

---

### 4.3 Strategy Rationale Generation

**Purpose**: Explain why specific qualification strategies were selected.

**Input Data**:
```json
{
  "primary_strategy": {
    "name": "Needs-Based Qualification",
    "description": "Training based on identified competency gaps per role"
  },
  "secondary_strategies": [
    {
      "name": "SE for Managers",
      "description": "Awareness training for management personnel"
    }
  ],
  "maturity_level": 3,
  "target_group_size": 150,
  "has_train_the_trainer": false,
  "role_clusters": ["SE for Engineers", "SE for Managers", "SE for Interfacing Partners"]
}
```

**Prompt Template**:
```
You are explaining the qualification strategy selection for an RFP document.

SELECTED STRATEGIES:
Primary: {primary_strategy.name}
- {primary_strategy.description}

Secondary: {secondary_strategies}

SELECTION FACTORS:
- Maturity Level: {maturity_level}/5
- Target Group Size: {target_group_size} employees
- Train-the-Trainer Required: {has_train_the_trainer}
- Role Clusters: {role_clusters}

Write a brief rationale (2-3 sentences) explaining why these strategies were selected.
Reference the maturity level and target group size as factors.
```

**Expected Output** (~50-75 words):
```
The Needs-Based Qualification strategy was selected as the primary approach given
the organization's moderate maturity level, enabling targeted training based on
specific competency gaps identified per role. SE for Managers complements this
by ensuring management personnel have sufficient SE awareness to support their
teams effectively.
```

---

### 4.4 Service Description Generation

**Purpose**: Generate the "Service Description - General" section describing what services are needed.

**Input Data**:
```json
{
  "total_modules": 18,
  "competency_areas": ["Core", "Technical", "Management", "Social/Personal"],
  "learning_formats": ["Seminar", "Webinar", "Workshop"],
  "has_aviva_plans": true,
  "pmt_context": {
    "tools": ["Polarion", "Enterprise Architect"],
    "methods": ["V-Model", "Agile"],
    "processes": ["Requirements Management", "Change Management"]
  },
  "language": "English",
  "certification_required": false
}
```

**Prompt Template**:
```
You are writing the Service Description section for an SE training RFP.

PROGRAM SCOPE:
- Total Training Modules: {total_modules}
- Competency Areas: {competency_areas}
- Learning Formats Required: {learning_formats}
- AVIVA Didactic Plans Provided: {has_aviva_plans}

ORGANIZATION CONTEXT:
- Tools: {pmt_context.tools}
- Methods: {pmt_context.methods}
- Key Processes: {pmt_context.processes}
- Training Language: {language}

Write a Service Description (bullet points) covering:
1. Training module concept development
2. Training material creation requirements
3. Alignment and review process with the organization
4. Training delivery requirements
5. Any tool-specific requirements

Use bullet points. Be specific but not overly detailed.
```

**Expected Output**:
```
The training service provider shall deliver the following services:

• Concepts for training modules based on pre-defined competency requirements;
  structure and modality shall be didactically optimized following the provided
  AVIVA frameworks.

• Creation of training materials in English, including presentations, exercises,
  and participant handouts.

• Alignment with the organization regarding training contents, modalities, and
  examples; material review cycles as agreed.

• Provision of training with hands-on exercises incorporating the organization's
  tools (Polarion, Enterprise Architect) where applicable.

• Trainers shall be familiar with the V-Model development approach and able to
  relate training content to the organization's processes.
```

---

### 4.5 Gap Analysis Summary Generation

**Purpose**: Generate a narrative summary of the competency gap analysis results.

**Input Data**:
```json
{
  "total_gaps": 45,
  "gaps_by_area": {
    "Core": 8,
    "Technical": 18,
    "Management": 12,
    "Social/Personal": 7
  },
  "gaps_by_level": {
    "1": 12,
    "2": 18,
    "4": 12,
    "6": 3
  },
  "top_gap_competencies": [
    {"name": "Requirements Management", "gap_count": 6},
    {"name": "System Architecture Design", "gap_count": 5},
    {"name": "Project Management", "gap_count": 4}
  ],
  "roles_with_most_gaps": [
    {"name": "Systems Engineer", "gap_count": 12},
    {"name": "Requirements Engineer", "gap_count": 8}
  ]
}
```

**Prompt Template**:
```
You are summarizing competency gap analysis results for an RFP document.

GAP ANALYSIS RESULTS:
- Total Competency Gaps Identified: {total_gaps}

BY COMPETENCY AREA:
{gaps_by_area}

BY TARGET LEVEL:
- Level 1 (Knowing): {gaps_by_level.1} gaps
- Level 2 (Understanding): {gaps_by_level.2} gaps
- Level 4 (Applying): {gaps_by_level.4} gaps
- Level 6 (Mastering): {gaps_by_level.6} gaps

TOP GAP AREAS:
{top_gap_competencies}

ROLES WITH MOST TRAINING NEEDS:
{roles_with_most_gaps}

Write a summary paragraph (3-4 sentences) that:
1. States the overall scope of gaps identified
2. Highlights the primary focus areas (competency areas and levels)
3. Notes which roles have the greatest training needs
```

**Expected Output** (~75-100 words):
```
The competency assessment identified 45 training gaps across the organization's
engineering roles. Technical competencies represent the largest gap area,
particularly in Requirements Management and System Architecture Design,
reflecting the need for stronger foundational SE skills. The majority of gaps
are at the Understanding (Level 2) and Applying (Level 4) levels, indicating
a need for both conceptual training and hands-on practical skill development.
Systems Engineers and Requirements Engineers have the highest training needs
and are priority targets for the qualification program.
```

---

### 4.6 Module Goals Generation

**Purpose**: Generate reader-friendly "Goals" bullet points for each training module.

**Input Data** (per module):
```json
{
  "module_name": "Requirements Management - Applying",
  "competency_name": "Requirements Management",
  "competency_area": "Technical",
  "target_level": 4,
  "level_name": "Applying",
  "pmt_type": "process",
  "training_program": "SE for Engineers",
  "learning_objectives": [
    "The participant can independently identify sources of requirements, derive requirements, document and link them.",
    "The participant can apply stakeholder analysis techniques.",
    "The participant can establish traceability between requirements and design elements."
  ],
  "content_topics": [
    "Requirements process",
    "Stakeholder analysis",
    "Types of requirements",
    "Traceability",
    "Documentation"
  ]
}
```

**Prompt Template**:
```
You are creating training module goals for an RFP document to training providers.

MODULE INFORMATION:
- Module: {module_name}
- Competency: {competency_name} ({competency_area})
- Target Level: {target_level} ({level_name})
- PMT Focus: {pmt_type}
- Target Audience: {training_program}

LEARNING OBJECTIVES (formal):
{learning_objectives}

CONTENT TOPICS:
{content_topics}

Generate 3-5 reader-friendly "Goals" bullet points that:
1. Start with action verbs appropriate for Level {target_level}:
   - Level 1 (Knowing): "Understanding...", "Knowing...", "Being aware of..."
   - Level 2 (Understanding): "Understanding...", "Comprehending...", "Explaining..."
   - Level 4 (Applying): "Applying...", "Being able to...", "Performing..."
   - Level 6 (Mastering): "Mastering...", "Optimizing...", "Teaching..."
2. Are concise (one line each)
3. Cover the main learning outcomes
4. Are appropriate for the {pmt_type} focus

Output as bullet points only, no additional text.
```

**Expected Output**:
```
• Applying the organization's requirements engineering process in development projects
• Being able to identify and analyze stakeholders and their requirements
• Performing requirements documentation using established templates and tools
• Establishing and maintaining traceability between requirements and architecture
• Applying verification criteria to validate requirements quality
```

---

### 4.7 Module Contents Outline Generation

**Purpose**: Generate a structured content outline for each training module.

**Input Data** (per module):
```json
{
  "module_name": "Requirements Management - Applying",
  "competency_name": "Requirements Management",
  "target_level": 4,
  "level_name": "Applying",
  "pmt_type": "process",
  "duration_hours": 8,
  "content_topics": [
    "Requirements process",
    "Stakeholder analysis",
    "Types of requirements",
    "Traceability",
    "Documentation",
    "Elicitation/definition/analysis",
    "Use cases",
    "System boundary",
    "Verification/validation criteria"
  ],
  "organization_tools": ["Polarion"],
  "organization_methods": ["V-Model"],
  "learning_format": "Seminar"
}
```

**Prompt Template**:
```
You are creating a training module content outline for an RFP document.

MODULE INFORMATION:
- Module: {module_name}
- Target Level: {target_level} ({level_name})
- PMT Focus: {pmt_type}
- Duration: {duration_hours} hours
- Learning Format: {learning_format}

CONTENT TOPICS (baseline):
{content_topics}

ORGANIZATION CONTEXT:
- Tools: {organization_tools}
- Methods/Frameworks: {organization_methods}

Generate a numbered content outline with 6-8 main items that:
1. Organizes the content topics into a logical training sequence
2. Includes sub-topics where appropriate (use letters: a, b, c)
3. Adjusts depth based on Level {target_level}:
   - Level 1: Overview, definitions, basic concepts
   - Level 2: Concepts, relationships, examples, case studies
   - Level 4: Hands-on application, tool usage, practical exercises
   - Level 6: Advanced techniques, optimization, mentoring skills
4. References organization tools ({organization_tools}) where relevant
5. Is realistic for {duration_hours} hours of training
6. Starts with a recap/introduction and ends with summary/practice

Output as numbered list with sub-items. No additional explanation.
```

**Expected Output**:
```
1. Introduction and Recap
   a. Module objectives and agenda
   b. Requirements engineering in the V-Model context
   c. Recap of Level 2 concepts

2. Requirements Process in Practice
   a. Organization's requirements workflow
   b. Roles and responsibilities
   c. Process integration points

3. Stakeholder Analysis Techniques
   a. Stakeholder identification methods
   b. Stakeholder mapping and prioritization
   c. Exercise: Stakeholder analysis for case study

4. Requirements Types and Documentation
   a. Functional vs. non-functional requirements
   b. Quality requirements and constraints
   c. Documentation templates and standards
   d. Hands-on: Writing requirements in Polarion

5. Traceability and Linking
   a. Traceability concepts and benefits
   b. Creating trace links in Polarion
   c. Traceability matrices and reports
   d. Exercise: Establishing traceability

6. Requirements Verification
   a. Verification criteria definition
   b. Review techniques
   c. Quality checks and metrics

7. Practical Application
   a. End-to-end exercise: Requirements for case study system
   b. Tool-based documentation and tracing
   c. Peer review and feedback

8. Summary and Next Steps
   a. Key takeaways
   b. Application to current projects
   c. Resources and further learning
```

---

## 5. Data Models

### 5.1 New Table: `phase4_rfp_export`

```sql
CREATE TABLE phase4_rfp_export (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id),

    -- Export metadata
    export_format VARCHAR(20) CHECK (export_format IN ('excel', 'word', 'pdf', 'all')),
    generation_mode VARCHAR(20) CHECK (generation_mode IN ('llm_enhanced', 'data_only')),

    -- Generated content cache
    generated_content JSONB,  -- Cached LLM outputs

    -- Export data snapshot
    export_data JSONB,  -- Full data snapshot at export time

    -- File references
    file_paths JSONB,  -- {"excel": "/path/to/file.xlsx", "word": "...", "pdf": "..."}

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_started_at TIMESTAMP,
    generation_completed_at TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    error_message TEXT
);

CREATE INDEX idx_rfp_export_org ON phase4_rfp_export(organization_id);
```

### 5.2 Generated Content JSON Structure

```json
{
  "generated_at": "2026-01-29T10:30:00Z",
  "generation_mode": "llm_enhanced",
  "model_used": "gpt-4o-mini",
  "sections": {
    "executive_summary": {
      "content": "...",
      "tokens_used": 485,
      "generated_at": "2026-01-29T10:30:05Z"
    },
    "maturity_summary": {
      "content": "...",
      "tokens_used": 120,
      "generated_at": "2026-01-29T10:30:08Z"
    },
    "strategy_rationale": {
      "content": "...",
      "tokens_used": 95,
      "generated_at": "2026-01-29T10:30:10Z"
    },
    "service_description": {
      "content": "...",
      "tokens_used": 180,
      "generated_at": "2026-01-29T10:30:12Z"
    },
    "gap_analysis_summary": {
      "content": "...",
      "tokens_used": 150,
      "generated_at": "2026-01-29T10:30:15Z"
    },
    "modules": {
      "module_1": {
        "goals": "...",
        "contents_outline": "...",
        "tokens_used": 380,
        "generated_at": "2026-01-29T10:30:20Z"
      },
      "module_2": {
        "goals": "...",
        "contents_outline": "...",
        "tokens_used": 395,
        "generated_at": "2026-01-29T10:30:25Z"
      }
    }
  },
  "total_tokens_used": 7250,
  "total_generation_time_seconds": 45
}
```

---

## 6. API Specification

### 6.1 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/phase4/rfp/preview` | Preview RFP data summary |
| POST | `/api/phase4/rfp/generate` | Start RFP generation |
| GET | `/api/phase4/rfp/status/{export_id}` | Check generation status |
| GET | `/api/phase4/rfp/download/{export_id}` | Download generated file |
| GET | `/api/phase4/rfp/history` | List past exports |

### 6.2 GET `/api/phase4/rfp/preview`

**Description**: Get a preview of all data that will be included in the RFP.

**Query Parameters**:
- `organization_id` (required): Organization ID

**Response**:
```json
{
  "organization": {
    "id": 1,
    "name": "Example Corp",
    "created_at": "2025-06-15"
  },
  "maturity": {
    "score": 62,
    "level": 3,
    "fields_of_action": {...},
    "assessment_pathway": "ROLE_BASED"
  },
  "strategies": {
    "primary": "Needs-Based Qualification",
    "secondary": ["SE for Managers"],
    "train_the_trainer": false
  },
  "scope": {
    "target_group_size": 150,
    "assessed_users": 45,
    "scaling_factor": 3.33,
    "role_count": 8,
    "total_modules": 18,
    "total_training_hours": 92,
    "modules_with_aviva": 12
  },
  "timeline": {
    "start_date": "2026-Q2",
    "end_date": "2027-Q2",
    "milestones": [...]
  },
  "gap_summary": {
    "total_gaps": 45,
    "by_area": {...},
    "by_level": {...}
  },
  "phases_complete": {
    "phase1": true,
    "phase2": true,
    "phase3": true,
    "phase4_aviva": true
  },
  "estimated_generation": {
    "llm_calls": 22,
    "estimated_tokens": 7500,
    "estimated_time_seconds": 60
  }
}
```

### 6.3 POST `/api/phase4/rfp/generate`

**Description**: Start RFP document generation.

**Request Body**:
```json
{
  "organization_id": 1,
  "generation_mode": "llm_enhanced",  // or "data_only"
  "export_formats": ["word", "excel"],  // or ["pdf"], or ["all"]
  "options": {
    "include_aviva_plans": true,
    "include_appendices": true,
    "include_role_competency_matrix": true,
    "language": "en"
  }
}
```

**Response**:
```json
{
  "export_id": 123,
  "status": "generating",
  "message": "RFP generation started",
  "estimated_completion_seconds": 60
}
```

### 6.4 GET `/api/phase4/rfp/status/{export_id}`

**Description**: Check the status of an RFP generation job.

**Response** (in progress):
```json
{
  "export_id": 123,
  "status": "generating",
  "progress": {
    "current_step": "Generating module contents",
    "steps_completed": 8,
    "total_steps": 22,
    "percentage": 36
  },
  "started_at": "2026-01-29T10:30:00Z"
}
```

**Response** (completed):
```json
{
  "export_id": 123,
  "status": "completed",
  "completed_at": "2026-01-29T10:31:05Z",
  "files": [
    {
      "format": "word",
      "filename": "SE_QPT_RFP_ExampleCorp_2026-01-29.docx",
      "size_bytes": 245000,
      "download_url": "/api/phase4/rfp/download/123?format=word"
    },
    {
      "format": "excel",
      "filename": "SE_QPT_RFP_ExampleCorp_2026-01-29.xlsx",
      "size_bytes": 180000,
      "download_url": "/api/phase4/rfp/download/123?format=excel"
    }
  ],
  "generation_stats": {
    "total_tokens_used": 7250,
    "total_time_seconds": 65,
    "modules_processed": 18
  }
}
```

### 6.5 GET `/api/phase4/rfp/download/{export_id}`

**Description**: Download a generated RFP file.

**Query Parameters**:
- `format` (required): "word", "excel", or "pdf"

**Response**: File download (binary)

---

## 7. Export Formats

### 7.1 Word Document Structure (.docx)

```
SE_QPT_RFP_{OrgName}_{Date}.docx
│
├── Title Page
│   ├── "SE Qualification Program"
│   ├── "Request for Proposal"
│   ├── Organization Name
│   └── Date
│
├── Table of Contents (auto-generated)
│
├── Part 1: Context and Core Concept
│   ├── Heading 1: "1. Context and Core Concept"
│   ├── 1.1 Executive Summary (LLM prose)
│   ├── 1.2 Organization Profile (table)
│   ├── 1.3 SE Maturity Assessment (table + LLM summary)
│   ├── 1.4 Qualification Strategies (table + LLM rationale)
│   └── 1.5 Curriculum Overview (table)
│
├── Part 2: Service Requirements
│   ├── Heading 1: "2. Service Requirements"
│   ├── 2.1 Service Description (LLM bullets)
│   ├── 2.2 Requirements and Constraints (table)
│   ├── 2.3 Personnel Subject to Training
│   │   ├── 2.3.1 Target Group Summary (table)
│   │   ├── 2.3.2 Role Inventory (table)
│   │   └── 2.3.3 Personnel by Module Matrix (table)
│   └── 2.4 Training Timeline (table)
│
├── Part 3: Training Program Structure
│   ├── Heading 1: "3. Training Program Structure"
│   ├── 3.1 Competency Gaps Summary (LLM prose + chart)
│   ├── 3.2 Training Structure Overview (table)
│   ├── 3.3 Learning Formats Distribution (table)
│   └── 3.4 Existing Training Coverage (table)
│
├── Part 4: Training Module Details
│   ├── Heading 1: "4. Training Module Details"
│   └── For each module:
│       ├── Heading 2: "Module: {Name} - {Level}"
│       ├── Module info table
│       ├── "Goals" section (LLM bullets)
│       ├── "Contents" section (LLM numbered list)
│       ├── AVIVA table (if available)
│       └── Suitability analysis table
│
└── Part 5: Appendices
    ├── Appendix A: SE Competency Framework
    ├── Appendix B: Role-Competency Matrix
    ├── Appendix C: PMT Context Details
    ├── Appendix D: Learning Formats Reference
    └── Appendix E: Glossary
```

### 7.2 Excel Workbook Structure (.xlsx)

```
SE_QPT_RFP_{OrgName}_{Date}.xlsx
│
├── Sheet 1: "Summary"
│   ├── Organization info
│   ├── Key metrics
│   ├── Executive summary text
│   └── Export metadata
│
├── Sheet 2: "Maturity"
│   ├── Overall score and level
│   ├── 4 Fields of Action breakdown
│   └── Assessment pathway
│
├── Sheet 3: "Strategies"
│   ├── Selected strategies
│   └── Strategy details
│
├── Sheet 4: "Roles"
│   ├── Organization roles
│   ├── SE cluster mappings
│   └── Training program assignments
│
├── Sheet 5: "Role-Competency Matrix"
│   └── Full matrix (roles × competencies)
│
├── Sheet 6: "Modules"
│   ├── All training modules
│   ├── Format, participants, duration
│   └── Goals and contents (LLM generated)
│
├── Sheet 7: "Personnel Matrix"
│   └── Participants by module and role
│
├── Sheet 8: "Timeline"
│   └── Milestones with dates
│
├── Sheet 9: "Gap Analysis"
│   ├── Gaps by competency
│   ├── Gaps by level
│   └── Gaps by role
│
├── Sheets 10+: "AVIVA_{ModuleName}"
│   └── One sheet per module with AVIVA plan
│
└── Sheet N: "Reference Data"
    ├── Competency framework
    ├── Learning formats
    └── Competency indicators
```

### 7.3 PDF Generation

PDF will be generated from the Word document using one of:
1. **LibreOffice headless** (server-side conversion)
2. **WeasyPrint** (HTML to PDF)
3. **docx2pdf** (Windows only, requires MS Word)

---

## 8. UI/UX Design

### 8.1 RFP Export Page Layout

```
+------------------------------------------------------------------+
| Phase 4: Micro Planning                                           |
| Task 2: RFP Document Export                                       |
+------------------------------------------------------------------+
|                                                                   |
| RFP Preview                                                       |
| +---------------------------------------------------------------+ |
| | Organization: Example Corp                                     | |
| | Maturity Level: 3/5 (Score: 62)                               | |
| | Assessment Pathway: Role-Based                                 | |
| |                                                                | |
| | Program Scope:                                                 | |
| | • Target Group: 150 employees                                  | |
| | • Roles Defined: 8                                            | |
| | • Training Modules: 18                                        | |
| | • Total Hours: 92                                             | |
| | • Modules with AVIVA Plans: 12                                | |
| +---------------------------------------------------------------+ |
|                                                                   |
| Generation Options                                                |
| +---------------------------------------------------------------+ |
| | Generation Mode:                                               | |
| | (•) LLM-Enhanced (recommended)                                | |
| |     Full document with AI-generated narratives, goals,         | |
| |     and content outlines                                       | |
| | ( ) Data-Only                                                  | |
| |     Raw data export with minimal templating                    | |
| +---------------------------------------------------------------+ |
| | Export Formats:                                                | |
| | [x] Word Document (.docx)                                      | |
| | [x] Excel Workbook (.xlsx)                                     | |
| | [ ] PDF Document (.pdf)                                        | |
| +---------------------------------------------------------------+ |
| | Include Options:                                               | |
| | [x] AVIVA Didactic Plans                                       | |
| | [x] Role-Competency Matrix                                     | |
| | [x] Appendices (Competency Framework, Glossary)                | |
| +---------------------------------------------------------------+ |
|                                                                   |
| Estimated Generation:                                             |
| • LLM Calls: 22                                                   |
| • Estimated Time: ~60 seconds                                     |
|                                                                   |
| [ Generate RFP Document ]                                         |
|                                                                   |
+------------------------------------------------------------------+
| Export History                                                    |
| +---------------------------------------------------------------+ |
| | Date       | Mode         | Formats      | Status   | Actions | |
| |------------|--------------|--------------|----------|---------|  |
| | 2026-01-28 | LLM-Enhanced | Word, Excel  | Complete | [DL]    | |
| | 2026-01-25 | Data-Only    | Excel        | Complete | [DL]    | |
| +---------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

### 8.2 Generation Progress Modal

```
+------------------------------------------+
| Generating RFP Document                   |
+------------------------------------------+
|                                          |
| [=========>                    ] 36%     |
|                                          |
| Current Step: Generating module contents |
| Module: Requirements Management          |
|                                          |
| Steps Completed: 8 / 22                  |
| Time Elapsed: 25 seconds                 |
|                                          |
| [Cancel]                                 |
+------------------------------------------+
```

### 8.3 Download Ready Modal

```
+------------------------------------------+
| RFP Document Ready                        |
+------------------------------------------+
|                                          |
| [SUCCESS] Generation completed in 65s    |
|                                          |
| Download Files:                          |
| +--------------------------------------+ |
| | [DOCX] SE_QPT_RFP_ExampleCorp.docx   | |
| |        245 KB    [Download]           | |
| +--------------------------------------+ |
| | [XLSX] SE_QPT_RFP_ExampleCorp.xlsx   | |
| |        180 KB    [Download]           | |
| +--------------------------------------+ |
|                                          |
| Generation Stats:                        |
| • Tokens Used: 7,250                     |
| • Modules Processed: 18                  |
|                                          |
| [Download All] [Close]                   |
+------------------------------------------+
```

---

## 9. Implementation Checklist

### 9.1 Backend Implementation

#### Database
- [ ] Create `phase4_rfp_export` table
- [ ] Add migration script

#### Service Layer
- [ ] Create `Phase4RFPService` class
- [ ] Implement data aggregation methods:
  - [ ] `_get_organization_profile()`
  - [ ] `_get_maturity_data()`
  - [ ] `_get_strategies()`
  - [ ] `_get_roles_and_mappings()`
  - [ ] `_get_competency_gaps()`
  - [ ] `_get_training_modules()`
  - [ ] `_get_timeline()`
  - [ ] `_get_personnel_matrix()`
  - [ ] `_get_aviva_plans()`
- [ ] Implement LLM generation methods:
  - [ ] `_generate_executive_summary()`
  - [ ] `_generate_maturity_summary()`
  - [ ] `_generate_strategy_rationale()`
  - [ ] `_generate_service_description()`
  - [ ] `_generate_gap_analysis_summary()`
  - [ ] `_generate_module_goals()`
  - [ ] `_generate_module_contents()`
- [ ] Implement export methods:
  - [ ] `export_to_word()`
  - [ ] `export_to_excel()`
  - [ ] `export_to_pdf()`
- [ ] Implement async generation with progress tracking

#### API Routes
- [ ] `GET /api/phase4/rfp/preview`
- [ ] `POST /api/phase4/rfp/generate`
- [ ] `GET /api/phase4/rfp/status/{export_id}`
- [ ] `GET /api/phase4/rfp/download/{export_id}`
- [ ] `GET /api/phase4/rfp/history`

### 9.2 Frontend Implementation

- [ ] Create `RFPExport.vue` component
- [ ] Implement preview panel
- [ ] Implement generation options form
- [ ] Implement progress modal with polling
- [ ] Implement download modal
- [ ] Implement export history table
- [ ] Add to Phase 4 navigation

### 9.3 Dependencies

```txt
# requirements.txt additions
python-docx==0.8.11       # Word document generation
openpyxl==3.1.2          # Excel generation (already present)
weasyprint==60.1         # PDF generation (optional)
```

### 9.4 Testing

- [ ] Unit tests for data aggregation
- [ ] Unit tests for LLM prompt formatting
- [ ] Integration tests for export generation
- [ ] Test with various organization configurations:
  - [ ] Role-based vs task-based pathway
  - [ ] With/without AVIVA plans
  - [ ] Different module counts (5, 15, 30)
- [ ] Test export file validation (open in Word/Excel)
- [ ] Performance testing (generation time)

---

## Appendix A: Complete Prompt Library

All prompts are defined in Section 4. Summary:

| Prompt ID | Purpose | Est. Tokens |
|-----------|---------|-------------|
| `EXEC_SUMMARY` | Executive summary | 500 |
| `MATURITY_SUMMARY` | Maturity interpretation | 200 |
| `STRATEGY_RATIONALE` | Strategy explanation | 200 |
| `SERVICE_DESC` | Service description | 300 |
| `GAP_ANALYSIS` | Gap analysis summary | 300 |
| `MODULE_GOALS` | Module goals (per module) | 150 |
| `MODULE_CONTENTS` | Content outline (per module) | 250 |

---

## Appendix B: Sample Generated Document

*See separate file: `SE_QPT_RFP_Sample_Output.docx`*

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Jomon George | Initial specification |
