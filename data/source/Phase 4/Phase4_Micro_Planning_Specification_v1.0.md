# Phase 4: Micro Planning - Design Specification v1.0

## Document Information
- **Module**: Phase 4 - Micro Planning of SE Training Initiative
- **Primary Tasks**: AVIVA Didactics Planning, RFP Document Export
- **Based on**: Ulf Meeting Notes (13.01.2026), Reference Files (RFP PDF, AVIVA Excel)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 1.0 (Initial Design Specification)
- **Date**: January 2026

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial design specification based on Ulf meeting (13.01.2026) |

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
| **User Choice for Content** | Option 1: Manual template OR Option 2: GenAI-generated content |
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
    |   |-- Define A,V,I,V,A steps with timing, methods, materials
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
    |      Option A: Template (empty content column)
    |      Option B: GenAI-assisted content generation
    |-- Step 1.3: Preview content suggestions (from Learning Objectives)
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

### 3.3 Content Generation Options

#### Option A: Manual Template Export

User exports an Excel template with:
- Pre-filled columns: Module, suggested AVIVA phases structure
- Empty columns: What (Content), How (Method), Material
- User fills in content manually

**UI Flow:**
1. Display list of modules from Phase 3
2. Show content suggestions preview (bullet points from Learning Objectives)
3. Button: "Export Template (Manual Completion)"
4. Download Excel with empty content columns

#### Option B: GenAI-Assisted Content Generation

System uses GenAI to generate detailed AVIVA content:
- Input: Module info + Learning Objectives content baseline
- Output: Complete AVIVA plan with suggested activities

**UI Flow:**
1. Display list of modules from Phase 3
2. Show content suggestions preview (bullet points from Learning Objectives)
3. Button: "Generate with GenAI"
4. System calls OpenAI API to generate content
5. Preview generated content
6. User can edit/modify
7. Export final AVIVA Excel

### 3.4 Content Baseline Data

The following content topics are available per competency (from `Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx`, Column H):

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

### 3.5 AVIVA Template Structure (Default)

For each module, generate default AVIVA structure:

```
Module: [Competency] - [Level]
Duration: [Estimated based on level: Know=2h, Understand=4h, Apply=8h, Master=16h]
Learning Objectives: [From Phase 2]

| Time  | Min | Type | AVIVA | What | How | Material |
|-------|-----|------|-------|------|-----|----------|
| 09:00 | 10  | V    | A     | Welcome & Introduction | Lecture | PowerPoint |
| 09:10 | 20  | U    | V     | Activate Prior Knowledge | Discussion | Flip-Chart |
| 09:30 | 45  | V    | I     | [Content Topic 1] | Lecture | PowerPoint |
| 10:15 | 15  | P    | -     | Break | - | - |
| 10:30 | 30  | V    | I     | [Content Topic 2] | Lecture | PowerPoint |
| 11:00 | 45  | U    | V     | [Practice Exercise] | Group Exercise | Exercise Sheet |
| 11:45 | 15  | V    | A     | Summary & Evaluation | Discussion | Feedback Form |
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
- maturity_responses (organization maturity)
- role_mapping (roles to SE clusters)
- archetype_assessment (qualification archetype)
- target_group_config (group sizes)

Phase 2 Data:
- survey_responses (competency assessments)
- competency_gaps (identified gaps)
- learning_objectives (generated LOs)

Phase 3 Data:
- phase3_training_module (modules with formats)
- phase3_timeline_milestone (timeline estimates)
- phase3_config (progress tracking)

Phase 4 Data:
- aviva_plans (AVIVA didactic plans)
- rfp_exports (export history)
```

---

## 5. Content Data Sources

### 5.1 Learning Objectives Content (Column H)

Source: `data/source/excel/Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx`
Sheet: "Learning Objectives"

This data provides baseline content topics for each of the 16 SE competencies. Used as input for:
- AVIVA content generation (GenAI baseline)
- Content preview in UI (bullet points)
- RFP module contents section

### 5.2 AVIVA Template Structure

Source: `data/source/Phase 4/M1+M2 - Konzeption_fein.xlsx`
Sheets: "Vorlage" (Template), "Beispiel" (Example)

Column structure:
1. Start (time)
2. min (duration)
3. Type (V/U/P)
4. WER (Who - optional)
5. AVIVA (phase)
6. Was (What - content)
7. Wie (How - method)
8. Womit (Material)

### 5.3 RFP Reference Structure

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
|   |-- [Content Preview Panel]
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
| Training Modules from Phase 3                    | Content Preview |
| +--------------------------------------------+   | +-------------+ |
| | [x] Systems Thinking - Knowing      2h     |   | | Suggested   | |
| | [x] Systems Thinking - Understanding 4h    |   | | Topics:     | |
| | [x] Requirements Mgmt - Applying    8h     |   | | - Topic 1   | |
| | [ ] Architecture Design - Knowing   2h     |   | | - Topic 2   | |
| +--------------------------------------------+   | | - Topic 3   | |
|                                                  | +-------------+ |
| Export Options:                                  |                 |
| +--------------------------------------------+   |                 |
| | (o) Template Only (Manual Completion)      |   |                 |
| | ( ) Generate with GenAI                    |   |                 |
| +--------------------------------------------+   |                 |
|                                                  |                 |
| [ Export Selected Modules ]  [ Export All ]      |                 |
+------------------------------------------------------------------+
```

#### Info Box (Content Preview)

Display bullet-point list of content topics when module is selected:
```
+----------------------------------+
| Content Topics for:              |
| Systems Thinking - Knowing       |
+----------------------------------+
| - Motivation for SE              |
| - Definition of terms (index)    |
| - Values of SE                   |
| - SE process models (V-model)    |
| - SE standards                   |
+----------------------------------+
| These topics will be used as     |
| baseline for AVIVA planning.     |
+----------------------------------+
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
    survey_id INTEGER REFERENCES new_survey_user(id),
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
  "total_duration_minutes": 120,
  "learning_objectives": ["..."],
  "activities": [
    {
      "start_time": "09:00",
      "duration_min": 10,
      "type": "V",
      "aviva_phase": "A",
      "content": "Welcome & Introduction",
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
    survey_id INTEGER REFERENCES new_survey_user(id),
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
    survey_id INTEGER REFERENCES new_survey_user(id) UNIQUE,
    task1_status VARCHAR(20) DEFAULT 'not_started',
    task2_status VARCHAR(20) DEFAULT 'not_started',
    aviva_generation_method VARCHAR(20),  -- 'template' or 'genai'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 Content Baseline Data

Store Learning Objectives content as reference data:

```sql
CREATE TABLE competency_content_baseline (
    id SERIAL PRIMARY KEY,
    competency_key VARCHAR(50) REFERENCES competency(competency_key),
    content_topics TEXT[],  -- Array of topic strings
    source VARCHAR(100) DEFAULT 'Qualifizierungsmodule_v4'
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
      "competency_key": "systems_thinking",
      "competency_name": "Systems Thinking",
      "level": 1,
      "level_name": "Knowing",
      "learning_format": "Blended Learning",
      "estimated_duration_hours": 2,
      "has_aviva_plan": false
    }
  ]
}
```

#### GET `/api/phase4/aviva/content-baseline/{competency_key}`
Get content topics for a competency.

**Response:**
```json
{
  "competency_key": "systems_thinking",
  "competency_name": "Systems Thinking",
  "content_topics": [
    "Motivation for SE",
    "Definition of terms",
    "Values of SE",
    "SE process models (V-model)",
    "SE standards"
  ]
}
```

#### POST `/api/phase4/aviva/generate`
Generate AVIVA plan(s) for selected modules.

**Request:**
```json
{
  "module_ids": [1, 2, 3],
  "generation_method": "genai"  // or "template"
}
```

**Response:**
```json
{
  "success": true,
  "plans": [
    {
      "module_id": 1,
      "aviva_content": { ... }
    }
  ]
}
```

#### GET `/api/phase4/aviva/export`
Export AVIVA plans as Excel.

**Query Parameters:**
- `module_ids`: Comma-separated list (optional, defaults to all)
- `format`: "excel" (default)

**Response:** File download

### 8.2 RFP Export Endpoints

#### GET `/api/phase4/rfp/summary`
Get summary of all data for RFP preview.

**Response:**
```json
{
  "organization": {
    "name": "...",
    "maturity_level": 2,
    "archetype": "common_basic_understanding"
  },
  "statistics": {
    "total_modules": 15,
    "total_participants": 120,
    "total_training_hours": 80
  },
  "timeline": {
    "start_date": "2026-03-01",
    "end_date": "2027-03-01"
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
  "include_aviva": true
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
- Module identification
- AVIVA-structured activity plan
- Timing, methods, materials

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
- [ ] Populate content baseline from Excel file

### 10.2 Backend API

- [ ] Implement AVIVA modules list endpoint
- [ ] Implement content baseline endpoint
- [ ] Implement AVIVA generation (template)
- [ ] Implement AVIVA generation (GenAI)
- [ ] Implement AVIVA Excel export
- [ ] Implement RFP summary endpoint
- [ ] Implement RFP Excel export
- [ ] Implement RFP Word export

### 10.3 Frontend UI

- [ ] Phase 4 navigation/routing
- [ ] Task 1: AVIVA Planning page
- [ ] Module list component with selection
- [ ] Content preview panel
- [ ] Export options (template vs GenAI)
- [ ] Task 2: RFP Export page
- [ ] Data summary display
- [ ] Export format selection
- [ ] Download handling

### 10.4 GenAI Integration

- [ ] Design prompt template for AVIVA generation
- [ ] Implement OpenAI API call for content generation
- [ ] Handle response parsing and validation
- [ ] Error handling for API failures

### 10.5 Testing

- [ ] Test AVIVA template export
- [ ] Test AVIVA GenAI generation
- [ ] Test RFP Excel export with all data
- [ ] Test RFP Word export formatting
- [ ] Test with various module counts
- [ ] Integration testing with Phases 1-3 data

---

## Appendix A: Reference Files

| File | Location | Purpose |
|------|----------|---------|
| AVIVA Template | `data/source/Phase 4/M1+M2 - Konzeption_fein.xlsx` | AVIVA structure reference |
| RFP Sample | `data/source/Phase 4/SE Qualification Program - Input for identifying training service providers.pdf` | RFP format reference |
| Learning Objectives | `data/source/excel/Qualifizierungsmodule_Qualifizierungsplane_v4_enUS.xlsx` | Content baseline data |

## Appendix B: AVIVA Methods Reference

| Method (English) | Method (German) | Description |
|-----------------|-----------------|-------------|
| Lecture | Impulsvortrag | Presentation by trainer |
| Discussion | Diskussion | Open group discussion |
| Individual Exercise | Einzelubung | Solo practice activity |
| Pair Work | Parchenarbeit | Two-person collaboration |
| Group Exercise | Gruppenubung | Team-based activity |
| Q&A | Abfrage | Question and answer session |
| Hands-on Practice | Praktische Ubung | Applied practice with tools |

## Appendix C: AVIVA Materials Reference

| Material (English) | Material (German) |
|-------------------|-------------------|
| PowerPoint | Powerpoint |
| Flip-Chart | Flip-Chart |
| Moderation Cards | Moderationskarten |
| Whiteboard/Pinboard | Pinnwand |
| Exercise Sheets | Ubungsblatter |
| Handbook | Handbuch |
| Digital Collaboration Tool | Conceptboard/Miro |
