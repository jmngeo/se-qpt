# SE-QPT Backlog - Meeting with Ulf (02.02.2026)

**Meeting Date:** 02 February 2026
**Participants:** Jomon, Ulf
**Created:** 2026-02-06
**Source File:** `data/Meeting notes/Meeting 02.02.2026.txt`

This backlog contains all action items, requirements, and changes discussed during the meeting with Ulf on 02.02.2026 where Phase 3 and Phase 4 implementations were reviewed.

---

## Legend

| Priority | Meaning |
|----------|---------|
| MUST | Ulf explicitly required this change |
| SHOULD | Ulf recommended / suggested this improvement |
| NICE-TO-HAVE | Ulf mentioned as optional or future enhancement |

| Status | Meaning |
|--------|---------|
| TODO | Not started |
| IN PROGRESS | Work started |
| DONE | Completed |

---

## A. THESIS / CONCEPTUAL FRAMEWORK

### A1. Explain Conceptual Framework in Thesis Chapter
- **Priority:** MUST
- **Status:** TODO
- **Source Quote:** _"I need you to make sure that you explain all these things in your conceptual framework chapter in your thesis. Because for me, the conceptual aspect is more important than the implementation aspect."_
- **Details:**
  - Explain the role-clustered training programs (SE for Engineers, SE for Managers, SE for Interfacing Partners)
  - Explain how roles are assigned to these 3 training programs based on their competency gaps
  - Explain the inside clustering of modules into common base and role-specific pathways within SE for Engineers program
  - Conceptual aspect is MORE important than implementation aspect for Ulf

### A2. Research Academic Sources for AVIVA Planning Durations
- **Priority:** SHOULD
- **Status:** TODO
- **Source Quote:** _"It would be nice to do some research on that topic, at least underline that a little bit here on the AVIVA planning durations."_
- **Details:**
  - Find academic research to support/justify the AVIVA planning duration values
  - At minimum, provide some academic backing for the chosen module durations per competency level

---

## B. TRAINING MODULE CLUSTERING / REDUCTION

### B1. Reduce Training Modules by Clustering per Competency Topic
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"One requirement that I have to be implemented is that we have to reduce the number of training modules."_
- **Details:**
  - Currently modules are individual (e.g., "Requirements Definition - Level 1 - Method", "Requirements Definition - Level 2 - Tool", etc.)
  - New structure: Group all modules of the same competency into ONE training course per package
  - Example: "SE for Engineers - Requirements Definition" = 1 single training course
  - This course would include every Method, Tool, and all identified competency level modules within that competency
- **New Hierarchy (3 levels):**
  1. **Package Level:** SE for Engineers / SE for Managers / SE for Interfacing Partners
  2. **Competency Topic Level:** "Systems Thinking for Engineers", "Requirements Definition for Engineers", etc.
  3. **Sub-module Level:** Tool, Method for each identified level (Knowing L1, Understanding L2, Applying L4, Mastering L6)
- **Module Count Reduction Logic:**
  - If a role needs Level 2, we can skip Level 1 (Level 1 is automatically achieved by achieving Level 2)
  - For Level 4, it may be necessary to keep Level 2 as a prerequisite base
  - Focus grouping on the **competency**, not on the **level**
- **Implementation Progress (2026-02-06):**
  - [x] **Level 1 Consolidation** - DONE: Level 1 (Knowing) modules are now automatically skipped in the Role-Clustered view when Level 2+ modules exist for the same competency within the same cluster. This applies to Phase 3 and Phase 4.
    - Backend: `phase3_planning_service.py` - post-processing filter in `_extract_cluster_modules_from_los()` removes redundant Level 1 modules; returns `level1_consolidated` flag and `level1_modules_removed` count
    - Backend: `phase4_aviva_service.py` + `phase4_aviva.py` route - passes consolidation metadata through to Phase 4
    - Frontend: `LearningFormatSelection.vue` (Phase 3) - amber info box explains consolidation to user
    - Frontend: `PhaseFour.vue` (Phase 4) - same info box pattern
    - Scope: Only role-clustered view; competency-level view unchanged. Only Level 1 is skipped; Levels 2, 4, 6 are never removed. Learning Objectives remain unaffected.
  - [x] **Competency Topic Grouping** - DONE (2026-02-06): Modules grouped by competency topic within packages in UI. Overview cards, collapsible packages, and competency-group checkboxes represent each competency topic as a training course.

### B2. Create Group-Within-Group-Within-Group Overview
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"Creating such an overview of trainings by having the group within the group within the group. Focusing the grouping not on the level, but grouping on the competency module."_
- **Details:**
  - Training overview structure: Package > Competency Topic > Sub-modules
  - This hierarchical view applies to both the app UI and all Excel exports
- **Implementation Progress (2026-02-06):**
  - [x] **App UI** - DONE: Phase 4 AVIVA page shows Package > Competency Topic > Sub-modules hierarchy with overview cards, collapsible packages, and competency-group expand/collapse
  - [x] **Excel Exports** - DONE: Hierarchical grouping (Package > Subcluster > Competency Topic > Sub-modules) applied to Phase 3 Excel, Phase 4 AVIVA Excel, and Phase 4 RFP Excel exports with colored section headers

---

## C. PHASE 3 - EXCEL EXPORT ENHANCEMENTS

### C1. Enhance Overview Section with Detailed Information
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"What would be nice would be to have also some more detailed information included in these overview items (Training View, Selected Strategies, Target Group Size, Total Training Modules, Format Distribution)."_
- **Details:**
  - For each overview item, indicate which Phase it comes from:
    - "Target Group Size" - defined in Phase 1
    - "Selected Strategies" - from Phase 1
    - "Training View" - from Phase 3
    - "Total Training Modules" - from Phase 3
    - "Format Distribution" - from Phase 3
  - Add a short description/summary for each overview item
- **Implementation Details (2026-02-07):**
  - Applied to ALL Excel exports (Phase 3, Phase 4 AVIVA, Phase 4 RFP) AND the RFP Word document export
  - **Excel exports:**
    - `phase3_planning.py`: Rewrote entire overview section with `write_overview_item()` helper
    - `phase4_aviva_service.py`: Rewrote Summary sheet overview with same pattern; fetches maturity_score from org table
    - `phase4_rfp_service.py`: Rewrote `_write_summary_sheet()` ORGANIZATION PROFILE, QUALIFICATION STRATEGY, PROGRAM SCOPE sections
    - Each item now shows: label | value | phase origin tag (e.g., "(Phase 1, Task 2)")
    - Below each item: italic description explaining what it is and where it comes from
    - Added new items across all exports: SE Maturity Level, Total Est. Duration, Training View with description
    - Total duration shows hours + approximate training days (e.g., "48 hours (~6.0 training days)")
  - **RFP Word document** (`phase4_rfp_service.py`):
    - Added `_add_intro_paragraph()` and `_add_phase_origin()` helper methods for consistent annotation style
    - New section **1.3 Qualification Strategy**: Each strategy with full description, target audience, qualification level, suitable phase, duration
    - Section 2.1: Intro paragraph explaining service deliverables scope
    - Section 2.2: Intro paragraph noting data derived from Phases 1-3
    - Section 2.3: Intro paragraph explaining target group (Phase 1) and roles (Phase 2) provenance
    - Section 3.1: Intro paragraph explaining competencies from Phase 2 gap analysis; competency count
    - Section 3.2: Intro paragraph describing training view type; **total estimated duration** added; summary stats reformatted as bold-label + value; **Duration (h) column added to modules table**
    - Section 3.3: Intro paragraph explaining timeline estimation context (Phase 3)
    - Part 4 intro: Paragraph explaining modules derive from Phase 2 gaps + Phase 3 planning
    - Per-module info line: Added duration, estimated participants, and roles-needing-training line
    - Table of Contents updated with 1.1, 1.2, 1.3 sub-entries

### C2. Add Strategy Descriptions to Overview
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"For the Selected Strategies, explain a bit more about the strategy selected as a short summary. For example, the strategy 'Continuous Support' - add its description and notes to describe about the strategy as well."_
- **Details:**
  - Use the Strategy profile cards already defined in Phase 1 (for all 7 strategies)
  - Include the strategy's description and notes alongside the strategy name
  - Similarly provide short descriptions for the other overview items
- **Implementation Details (2026-02-07):**
  - Applied to ALL Excel exports AND the RFP Word document
  - All files import `SE_TRAINING_STRATEGIES` from `strategy_selection_engine.py`
  - Each selected strategy listed with Primary/Secondary label
  - Below each strategy: full description text (wrap_text enabled)
  - Key details line: Target Audience | Qualification Level | Duration
  - RFP Word: New section 1.3 with full strategy profiles including suitable phase

### C3. Add Timeline Planning Column to Training Modules Table
- **Priority:** SHOULD
- **Status:** DONE (covered by J1)
- **Completed:** 2026-02-07
- **Source Quote:** _"Maybe it would be nice to also add the detailed timeline planning to the Training Modules by having a new column after the 'Est. Participants' column to include timeline planning information."_
- **Details:**
  - Added "Est. Duration (h)" column after "Est. Participants" as part of J1 implementation
  - Per-module delivery scheduling deferred to G-series items (G1/G2/G3)
- **Applies to:** Phase 3 Excel export

### C4. Module-Level Timeline Separation (Nice-to-have)
- **Priority:** NICE-TO-HAVE
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"Not a must have requirement, but a nice to have requirement - that we would have also a separation in timeline of these different modules for different trainings."_
- **Details:**
  - Currently timeline is high-level (concept development starts, implementation, etc.)
  - Enhancement: Show separate timeline estimates per module per training package
- **Implementation Details (2026-02-07):**
  - Covered by the Training Schedule sheet (G1/G2/G3 implementation)
  - Each module gets a specific Day #, Date, Time slot (e.g., "9:00 - 11:00"), and Duration per training package
  - Per-package sections show separate schedules for SE for Engineers, SE for Managers, SE for Interfacing Partners
  - Calendar dates assigned when rollout milestones are defined in Phase 3 timeline

---

## D. PHASE 4 - TASK 1: AVIVA DIDACTICS ENHANCEMENTS

### D1. Add Explanatory Text for AVIVA Task
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"Write short sentence in this Task 1 of Phase 4 as something like - Now you have the possibility to select for which training concepts you want to create a detailed didactics using AVIVA. Also here you should explain shortly What AVIVA is to the user - it's a didactics concept for generating learning plans."_
- **Details:**
  - Add introductory text at top of AVIVA page explaining:
    - What AVIVA is (a didactics concept for generating learning plans)
    - That the user can select which training concepts/modules to include
    - Why this step is necessary
  - Text should be user-friendly and explain the purpose

### D2. Add Module Selection via Checkboxes
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"The user could select which all modules they want to have included in the AVIVA planning. It should be like checkboxes on each of the modules that allow selection-deselection of the currently listed modules."_
- **Details:**
  - Add checkbox to each module in the training modules list
  - User can select/deselect individual modules for AVIVA planning
  - User can generate different AVIVA plans for different module selections
  - Allows flexibility to create multiple AVIVA plans for different subsets

### D3. Implement Expand-Collapse for Training Packages (Role-Cluster View)
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"It would be nice to have an expand-collapse functionality here. So that at the start, we just see the high level view of the 3 training packages as collapsed cards and then the user can expand each package to see the modules included in it."_
- **Details:**
  - For role-cluster based training structure:
    - Show 3 training packages (SE for Engineers, SE for Managers, SE for Interfacing Partners) as collapsed cards initially
    - User can expand each package to see included modules
    - Reduces visual overwhelm from all module details at once
  - Layout: High-level overview of 3 packages first, then detailed expandable module view below

### D4. Implement Expand-Collapse for Competency-Level View
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"Similarly if it's competency level based training structure, we can have the expand-collapse functionality for each of the 16 competencies showing the modules included in each competency when expanded."_
- **Details:**
  - For competency-level based training structure:
    - Show 16 competencies as collapsed cards initially
    - User can expand each competency to see included modules within it

### D5. Package/Competency-Level Checkboxes (Select/Deselect All)
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"Also allow the selection of the higher level packages or competencies as checkboxes for selection-deselection of all modules within that package/competency."_
- **Details:**
  - Add checkbox on each package card (SE for Engineers, etc.) or competency card
  - Selecting a package/competency checkbox = all modules within it get selected
  - Deselecting a package/competency checkbox = all modules within it get deselected
  - Allows quick bulk selection/deselection at the package or competency level
  - Individual module checkboxes still available when package/competency is expanded

### D6. Show High-Level Package Overview First
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"One simple change to be made is to have first of all have the overview of the 3 training packages... so the user understands that these are the 3 main training packages. Then below that, we can have the detailed view of the modules."_
- **Details:**
  - Show overview section at top with the 3 main training packages summary
  - Below that, show the expandable/collapsible detailed module view
  - User first sees the high-level picture, then drills down as needed

---

## E. PHASE 4 - TASK 2: RFP DOCUMENT ENHANCEMENTS

### E1. Add Module Selection Option for RFP Export
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote (Jomon summary):** _"In the Export RFP Document div, we can ask user if they want to include only the modules selected in AVIVA page for export or to include all modules defined in Phase 3."_
- **Details:**
  - In Phase 4 Task 2 RFP page, add a selection option:
    - Option A: Include only the modules selected in AVIVA (Task 1) page
    - Option B: Include all modules defined in Phase 3
  - This gives the user control over what goes into the RFP document
- **Implementation Details (2026-02-07):**
  - Frontend: `PhaseFour.vue` - Added `rfpModuleScope` ref (`'all'` | `'aviva_selected'`), defaulting to `'all'`
  - Radio group added in RFP export panel: "All Phase 3 modules (N)" vs "Only AVIVA-selected modules (X of N)"
  - AVIVA-selected option is disabled when no modules are selected in Task 1
  - Export stats pill and confirmation dialog dynamically reflect the chosen scope
  - Backend unchanged - existing `module_ids` parameter in `get_rfp_data()` already handled `null` (all) vs array (filtered)

---

## F. AVIVA MODULE DURATION CHANGES

### F1. Reduce AVIVA Module Durations (Halve All Values)
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"Currently it is Level 1 (2 hours), Level 2 (4 hours), Level 4 (8 hours), Level 6 (16 hours). I think these timings are a bit too high. So we can reduce them to Level 1 (1 hour), Level 2 (2 hours), Level 4 (4 hours), Level 6 (8 hours)."_
- **Changes Required:**

| Level | Old Duration | New Duration |
|-------|-------------|--------------|
| Level 1 (Knowing) | 2 hours | **1 hour** |
| Level 2 (Understanding) | 4 hours | **2 hours** |
| Level 4 (Applying) | 8 hours | **4 hours** |
| Level 6 (Mastering) | 16 hours (2 days) | **8 hours (1 day)** |

- **Implementation Details:**
  - `phase4_aviva_service.py`: Updated `LEVEL_DURATION_HOURS`, `AVIVA_PHASE_DURATIONS`, and completely rewrote all 4 level sequences in `_generate_aviva_sequence()`
  - All activity sums now match nominal durations exactly (60, 120, 240, 480 min)
  - Level 6 collapsed from 2-day to 1-day structure
  - I:V ratios designed per level: L1=1.3:1 (I-heavy), L2=1.1:1 (balanced), L4=0.84:1 (V-heavy), L6=0.91:1 (V-heavy)
  - Spec file updated to v1.2: `Phase4_Micro_Planning_Specification_v1.1.md`

---

## G. AVIVA DAILY SCHEDULE VIEW

### G1. Create Daily View for AVIVA Plans (Multiple Modules Per Day)
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"It would be nice if we can bring 2 or more modules in 1 day and, it being like saying the first day is from 9 to 5, and at the end of 1st module, we start the next module, etc.. So that we can have multiple modules in 1 day."_
- **Details:**
  - Create whole training days (9am to 5pm = 8 hours)
  - Bring multiple modules together to fill a complete day
  - Modules are sequential within a day (NOT parallel)
  - Only one module is being trained at any given time
  - Example: Day 1 (9:00-11:00 Module A, 11:00-13:00 Module B, 14:00-18:00 Module C)
- **Implementation Details (2026-02-07):**
  - `phase4_aviva_service.py`: `_generate_daily_schedule()` + `_pack_modules_into_days()` implement greedy first-fit-decreasing bin-packing into 8-hour days (480 min capacity)
  - Each module gets start_time and end_time (e.g., "9:00 - 11:00"), sequential within each day
  - Automatic 45-minute lunch break insertion at 12:00 for days >= 5 hours with multiple modules
  - L6 (Mastering) modules are full-day (8h) with built-in lunch
  - Small days (<4 hours) are merged together where possible
  - "Training Schedule" sheet in AVIVA Excel export + RFP Excel export

### G2. Synchronize Learning Formats Per Day
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"You have to also somehow synchronize the modules taking into consideration the learning formats chosen for each of the modules."_ / _"to have this separate view to synchronize to use the same learning formats (Webinar, WBT, ..) for everything at least per day."_
- **Details:**
  - Within a single training day, try to use consistent learning formats
  - Example: If Day 1 is a Webinar day, schedule Webinar-compatible modules together
  - Ensures consistency in training delivery per day
  - May use LLM to intelligently group and schedule modules into daily views
  - Applies primarily to role-cluster based training structure
  - Competency-level based structure can keep its current format
- **Implementation Details (2026-02-07):**
  - `phase4_aviva_service.py`: `_generate_daily_schedule()` sub-groups modules by learning format before bin-packing
  - Each format group gets a descriptive day label: "Seminar Day", "Webinar Day", "Coaching Day", "WBT Day", "Blended Day"
  - Format groups are packed independently, so all modules in a given day share the same learning format
  - Day headers in Excel show format label: e.g., "Day 1 -- Mon, 2025-02-10 | Seminar Day | 6.5h"

### G3. Ensure Package Consistency in Planning
- **Priority:** SHOULD
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"This Training Module planning should be somehow consistent. So that we have an overview of packages that are somehow consistent."_
- **Details:**
  - Training packages should have a consistent structure
  - Modules within packages should be coherently organized
  - Daily schedule should reflect this consistency
- **Implementation Details (2026-02-07):**
  - `phase4_aviva_service.py`: `_generate_daily_schedule()` creates separate schedule sections per training package for role_clustered view (SE for Engineers, SE for Managers, SE for Interfacing Partners)
  - Each package section has its own set of days, day numbering, totals, and format grouping
  - Sequential calendar date assignment across packages (Package 2 starts after Package 1 completes)
  - For competency_level view: single "All Modules" section with consistent formatting
  - Per-section summary in Excel: "{X} training day(s) | {Y}h total"
  - Color-coded package headers in the Training Schedule sheet

---

## H. APP-WIDE GUIDANCE AND EXPLANATIONS

### H1. Add Guidance Text to All Tasks in All Phases
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"One observation I have for the whole web application is that we need more explanations in the app everywhere to everything that we have did in each task in each Phase. Because the user would not be aware of what's happening in each task."_
- **Details:**
  - For EVERY task in EVERY Phase, add guidance text explaining:
    1. **What** is happening in this step
    2. **Why** it is necessary
    3. **What** the user should do
    4. **Where** the data/decisions are based on (which previous phases/inputs)
  - Examples given by Ulf:
    - Phase 4 Task 1 AVIVA: Explain what AVIVA is, why it's necessary, what should be done
    - Phase 4 Task 2 RFP: "Based on everything you have input and every information we have gathered together, we're going to create now the RFP document export for you that you can use, and what it is used for."
  - **Double-check all Phases** to ensure proper guidance exists
- **Progress Assessment (2026-02-07):**
  - Phase 1: GOOD - Maturity assessment has "Why measure maturity?" rationale, strategy cards with pro/con, "What's Next?" alerts
  - Phase 2: DONE - All 4 tasks now have comprehensive info boxes
  - Phase 3: GOOD - Excellent info boxes explaining scaling, consolidation, structure selection rationale, timeline phases
  - Phase 4 Task 1 AVIVA: GOOD - AVIVA model explanation with all 5 phases described
  - Phase 4 Task 2 RFP: DONE - Comprehensive guidance explaining RFP purpose, data consolidation from all phases, export options
- **Implementation Details (2026-02-07):**
  - `DerikTaskSelector.vue` (Phase 2 Task 1a): Blue info box explaining task-based assessment, AI process mapping, data flow
  - `Phase2RoleSelection.vue` (Phase 2 Task 1b): Blue info box explaining role-based assessment, Phase 1 data source, role-to-competency mapping
  - `Phase2CompetencyAssessment.vue` (Phase 2 Task 2): Green info box explaining INCOSE framework, how to rate, why accuracy matters
  - `CompetencyResults.vue` (Phase 2 Task 3): Amber info box explaining gap analysis, radar chart interpretation, what happens next
  - `PhaseFour.vue` (Phase 4 Task 2 RFP): Enhanced info box with RFP definition, data consolidation from Phases 1-4, export format details, GenAI disclaimer note

### H2. Phases to Review for Guidance Text
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-07
- **Checklist:**
  - [x] Phase 1 - Task 1: Organization Profile (has phase header alert, What's Next sections)
  - [x] Phase 1 - Task 2: Strategy Selection (has strategy cards with pro/con and descriptions)
  - [x] Phase 1 - Task 3: Maturity Assessment (has "Why measure maturity?" rationale, rating descriptions)
  - [x] Phase 2 - Task 1: Role Input / Task-Based Assessment (DONE - info boxes for both task-based and role-based pathways)
  - [x] Phase 2 - Task 2: Competency Assessment (Survey) (DONE - INCOSE framework explanation, rating methodology)
  - [x] Phase 2 - Task 3: Competency Results / Gap Analysis (DONE - gap analysis interpretation, radar chart guide, next steps)
  - [x] Phase 2 - Task 4: Learning Objectives (already comprehensive - overview card, process steps, prerequisites)
  - [x] Phase 3 - Task 1: Training Structure Selection (excellent - auto-selection rationale, structure comparison)
  - [x] Phase 3 - Task 2: Training Modules Building (excellent - scaling info, consolidation explanation, training programs info)
  - [x] Phase 3 - Task 3: Learning Format Recommendations (covered in Task 2 format selection)
  - [x] Phase 3 - Task 4: Timeline Planning (excellent - phase overview cards, generation context, disclaimer)
  - [x] Phase 3 - Excel Export (N/A - export action, no guidance needed)
  - [x] Phase 4 - Task 1: AVIVA Didactics (has AVIVA model explanation with all 5 phases)
  - [x] Phase 4 - Task 2: RFP Document Export (DONE - RFP definition, data consolidation, export options, GenAI note)

---

## I. GENAI DISCLAIMER ON EXPORTED DOCUMENTS

### I1. Add GenAI Disclaimer to All AI-Generated Exports
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-06
- **Source Quote:** _"For the file exports that we do (the Phase 4 AVIVA excel, and the RFP Word document) that use GenAI to populate contents, there's also something we need to write at the very end of the document - like every GenAI topic, that this document or file is generated using GenAI and it could have mistakes. This document should be like a reference file or like a starting point and they might be changes necessary."_
- **Disclaimer Text (suggested):**
  > **Disclaimer:** This document was generated using Generative AI (GenAI) and may contain inaccuracies or errors. It is intended as a reference document and starting point. Review and modifications may be necessary to ensure accuracy and alignment with your specific organizational requirements.
- **Applies to:**
  - [x] Phase 4 AVIVA GenAI Excel export (Summary sheet + AVIVA Plans sheet headers)
  - [x] Phase 4 RFP Word document export (after title page, before table of contents)
  - [ ] Any other GenAI-generated export files

---

## J. TIMELINE COLUMN IN ALL EXCEL EXPORTS

### J1. Add Duration Column to All 4 Excel Exports
- **Priority:** MUST
- **Status:** DONE
- **Completed:** 2026-02-07
- **Source Quote:** _"We need to include the detailed timeline into the Training Modules Overview of all the modules by adding a new column in the 4 excel sheet exports in the app."_ / Ulf: _"Yes, exactly."_
- **Details:**
  - Original requirement was a "timeline" column mapping milestones to modules, but the 5 org-level milestones (Concept Dev, Pilot, Rollout) describe the program lifecycle, not per-module scheduling - every module goes through all phases
  - Instead, added an "Est. Duration (h)" column after "Est. Participants" showing estimated training duration per module based on competency level: L1=1h, L2=2h, L4=4h, L6=8h
  - Per-module delivery scheduling (which training day/wave) deferred to G-series backlog items (G1/G2/G3)
- **Applies to:**
  - [x] Phase 3 Excel export - `phase3_planning.py`: Added `LEVEL_DURATION_HOURS` mapping, updated headers and row writers for both role-clustered and competency-level views
  - [x] Phase 4 Task 1 AVIVA Template Excel export - Already had "Duration (h)" column, no changes needed
  - [x] Phase 4 Task 1 AVIVA GenAI Excel export - Already had "Duration (h)" column, no changes needed
  - [x] Phase 4 Task 2 RFP Excel export - `phase4_rfp_service.py`: Added `LEVEL_DURATION_HOURS` class constant, updated headers and `write_module_row_rc()`/`write_module_row_cl()` for both views

---

## SUMMARY TABLE

| ID | Item | Area | Priority | Status |
|----|------|------|----------|--------|
| A1 | Explain conceptual framework in thesis | Thesis | MUST | TODO |
| A2 | Research academic sources for AVIVA durations | Thesis/Research | SHOULD | TODO |
| B1 | Reduce modules by clustering per competency topic | Training Structure | MUST | DONE |
| B2 | Create group-within-group overview structure | Training Structure | MUST | DONE |
| C1 | Enhance Excel overview with detailed info & phase origins | Phase 3 Excel | SHOULD | DONE |
| C2 | Add strategy descriptions to Excel overview | Phase 3 Excel | SHOULD | DONE |
| C3 | Add timeline column to Training Modules table | Phase 3 Excel | SHOULD | DONE (J1) |
| C4 | Module-level timeline separation | Phase 3 Excel | NICE-TO-HAVE | DONE |
| D1 | Add explanatory text for AVIVA task | Phase 4 AVIVA UI | MUST | DONE |
| D2 | Add module selection via checkboxes | Phase 4 AVIVA UI | MUST | DONE |
| D3 | Implement expand-collapse for training packages | Phase 4 AVIVA UI | MUST | DONE |
| D4 | Implement expand-collapse for competency-level view | Phase 4 AVIVA UI | SHOULD | DONE |
| D5 | Package/competency-level select-all checkboxes | Phase 4 AVIVA UI | MUST | DONE |
| D6 | Show high-level package overview first | Phase 4 AVIVA UI | MUST | DONE |
| E1 | Add module selection option for RFP export | Phase 4 RFP UI | MUST | DONE |
| F1 | Reduce AVIVA module durations (halve all values) | AVIVA Backend | MUST | DONE |
| G1 | Create daily view for AVIVA plans | AVIVA Export | SHOULD | DONE |
| G2 | Synchronize learning formats per day | AVIVA Export | SHOULD | DONE |
| G3 | Ensure package consistency in planning | AVIVA Export | SHOULD | DONE |
| H1 | Add guidance text to all tasks in all phases | App-Wide UI | MUST | DONE |
| H2 | Review all phases for guidance text completeness | App-Wide UI | MUST | DONE |
| I1 | Add GenAI disclaimer to AI-generated exports | Phase 4 Exports | MUST | DONE |
| J1 | Add duration column to all 4 Excel exports | All Excel Exports | MUST | DONE |

---

## PRIORITY COUNTS

| Priority | Count | DONE | IN PROGRESS | TODO |
|----------|-------|------|-------------|------|
| **MUST** | 14 | 12 (B1, B2, D1, D2, D3, D5, D6, E1, F1, H1, H2, I1, J1) | 0 | 1 (A1) |
| **SHOULD** | 8 | 7 (C1, C2, C3, D4, G1, G2, G3) | 0 | 1 (A2) |
| **NICE-TO-HAVE** | 1 | 1 (C4) | 0 | 0 |
| **Total** | 23 | **20** | **0** | **2** |

**Overall Progress: 20/23 DONE (87%), 0 IN PROGRESS, 2 TODO (thesis-only tasks, not app changes)**

---

## SUGGESTED IMPLEMENTATION ORDER

### Sprint 1: Quick Wins & Backend Changes
1. **F1** - Reduce AVIVA durations (simple config change)
2. **I1** - Add GenAI disclaimer to exports (small text addition)
3. **D1** - Add explanatory text for AVIVA task (text content)

### Sprint 2: Training Module Clustering
4. **B1** - Reduce modules by clustering per competency topic
5. **B2** - Create hierarchical group overview structure

### Sprint 3: Phase 4 UI - Module Selection & Expand-Collapse
6. **D6** - Show high-level package overview first
7. **D3** - Implement expand-collapse for training packages
8. **D2** - Add module selection via checkboxes
9. **D5** - Package-level select-all checkboxes
10. **D4** - Expand-collapse for competency-level view

### Sprint 4: RFP & Excel Export Enhancements
11. **E1** - Module selection option for RFP export
12. **J1** - Add timeline column to all 4 Excel exports
13. **C1** - Enhance Excel overview with detailed info
14. **C2** - Add strategy descriptions to Excel overview
15. **C3** - Add timeline column to Phase 3 Training Modules table

### Sprint 5: App-Wide Guidance & AVIVA Scheduling
16. **H1** + **H2** - Add guidance text to all tasks in all phases
17. **G1** - Daily view for AVIVA plans
18. **G2** - Synchronize learning formats per day
19. **G3** - Package consistency in planning

### Sprint 6: Thesis & Research
20. **A1** - Write conceptual framework chapter
21. **A2** - Research academic sources for AVIVA durations

### Backlog (Nice-to-have)
22. **C4** - Module-level timeline separation

---

*File created: 2026-02-06*
*Last updated: 2026-02-07 - G1+G2+G3 Training Schedule with bin-packed daily view, format-synchronized days, per-package sections in AVIVA + RFP Excel exports; C4 covered by Training Schedule (per-module time slots per package); H1+H2 assessed as IN PROGRESS (Phase 1 & 3 good, Phase 2 & Phase 4 Task 2 need work); Timeline moved from Summary sheet to Training Schedule sheet in AVIVA export; RFP export now has Training Schedule sheet replacing standalone Timeline sheet*
*Previous updates: 2026-02-07 - C1+C2 enhanced overview in ALL Excel exports + RFP Word doc with phase origins, descriptions, strategy details, maturity level, total duration; RFP Word: new 1.3 Qualification Strategy section, intro paragraphs for all sections, duration column in modules table, per-module roles/duration info; C3 covered by J1; E1 RFP module scope selection; J1 duration column in Phase 3 + RFP exports*
*Previous updates: 2026-02-06 - F1 AVIVA durations halved, I1 GenAI disclaimers added, D1 AVIVA explanatory text added, B1 competency topic grouping completed, D2-D6 AVIVA page redesign (checkboxes, expand-collapse, overview cards) completed, B2 DONE (UI + Excel exports with hierarchical grouping)*
