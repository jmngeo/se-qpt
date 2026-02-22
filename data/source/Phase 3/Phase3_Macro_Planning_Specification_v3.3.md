# Phase 3: Macro Planning - Implementation Specification v3.3

## Document Information
- **Module**: Phase 3 - Macro Planning of SE Training Initiative
- **Primary Task**: Building Trainings (structure and plan)
- **Based on**: Conceptual Framework (LaTeX), Theoretical Foundations, Ulf Meeting (11-12-2025)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 3.3 (Implementation Verified)
- **Date**: January 2026

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | Dec 2025 | Complete redesign: User-driven format selection, 3-factor feedback, two training views |
| 3.1 | Jan 2026 | Timeline redesign: LLM-generated milestones (not user input), removed existing training check (moved to Phase 2), removed sessions count, 3-task structure |
| 3.2 | Jan 2026 | Data alignment: Updated all competency keys to match DB (`competency` table), updated all strategy keys to match DB (`strategy_template` table), defined Training Program Clusters concept (6 umbrella clusters distinct from 14 SE Role Clusters), added reference tables for DB alignment |
| **3.3** | **Jan 2026** | **Implementation verified**: Multi-strategy weighted aggregation for Factor 3, Excel export fully implemented, phase3_config table for progress tracking, API endpoints documented, Training Program Cluster stored on phase3_training_module table, Gantt chart visualization with dynamic positioning |

---

## Table of Contents

1. [Module Overview](#1-module-overview)
2. [Phase 3 Structure](#2-phase-3-structure)
3. [Task 1: Choose Training Structure](#3-task-1-choose-training-structure)
4. [Task 2: Select Learning Formats](#4-task-2-select-learning-formats)
5. [Task 3: Timeline Planning (LLM-Generated)](#5-task-3-timeline-planning-llm-generated)
6. [Learning Format Master Data](#6-learning-format-master-data)
7. [Matrices](#7-matrices)
8. [Participant Count Scaling](#8-participant-count-scaling)
9. [UI/UX Design](#9-uiux-design)
10. [Data Models](#10-data-models)
11. [API Specification](#11-api-specification)
12. [Phase 3 Outputs](#12-phase-3-outputs)
13. [Implementation Checklist](#13-implementation-checklist)

---

## 1. Module Overview

### 1.1 Purpose

Phase 3 "Macro Planning" helps organizations:
1. **Structure their training program** (by competency-level OR by role clusters)
2. **Select appropriate Learning Formats** for each training module with 3-factor suitability feedback
3. **Receive LLM-generated timeline estimates** for training program milestones

### 1.2 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **User-Driven Format Selection** | NO automatic recommendations. User selects format, system shows suitability feedback |
| **Two Training Views** | Competency-Level Based OR Role-Clustered Based |
| **3-Factor Suitability** | Green/yellow/red feedback for each factor |
| **LLM-Generated Timeline** | System generates estimated milestones (not user-entered) |
| **Modules Pre-Defined** | Modules come from Phase 2 Learning Objectives, not created here |

### 1.3 Position in SE-QPT Workflow

```
Phase 1: Prepare SE Training
    ↓ Outputs: Maturity Level, Role Clusters, Qualification Archetype, 
               Target Group Size, Training Group Size
    
Phase 2: Identify Requirements and Competencies  
    ↓ Outputs: Competency Gaps, Learning Objectives, Training Modules
    ↓ Note: "Check Existing Training Offers" happens here in LO dashboard
    
Phase 3: Macro Planning  ← THIS MODULE
    │
    ├── Task 1: Choose Training Structure
    │   └── Select view: Competency-Level OR Role-Clustered
    │
    ├── Task 2: Select Learning Formats
    │   ├── Select format per module
    │   └── View 3-factor suitability feedback
    │
    └── Task 3: Timeline Planning
        └── View LLM-generated milestone estimates
    
    ↓ Outputs: Training Structure, Selected Formats, Timeline Milestones
    
Phase 4: Micro Planning
    → Outputs: AVIVA Templates, Detailed Training Plans, RFP Document
```

### 1.4 Training Lifecycle Context

The 6-Phase Training Lifecycle provides theoretical grounding for timeline planning:

| Lifecycle Phase | Duration | Covered By |
|-----------------|----------|------------|
| 1. Exploration/Needs Assessment | 2-6 months | SE-QPT Phase 1 + Phase 2 |
| 2. Design/Planning | 1-3 months | SE-QPT Phase 2 + Phase 3 |
| 3. Development/Installation | 2-4 months | **Timeline focuses here** |
| 4. Pilot | 1-3 months | **Timeline focuses here** |
| 5. Initial Implementation | 6-12 months | **Timeline focuses here** |
| 6. Sustainment | Ongoing | **Timeline focuses here** |

**Key Insight**: Phases 1-2 are already addressed by SE-QPT's qualification planning process. Timeline planning focuses on phases 3-6 that occur after training providers are engaged.

### 1.5 What Changed from v3.0

| Aspect | v3.0 | v3.1 |
|--------|------|------|
| **Phase Name** | "Building Trainings" | **"Macro Planning"** |
| **Task Structure** | 2 tasks | **3 tasks** |
| **Timeline Input** | Manual date entry by user | **LLM-generated estimates** |
| **Timeline Adjustability** | User can edit dates | **Not adjustable** (informational) |
| **Sessions Count** | User enters number | **Removed** |
| **Existing Training Check** | Listed in Phase 3 | **Clarified: Phase 2 LO dashboard** |
| **Display** | Concept/Pilot/Run phases | **5 Milestones only** |

---

## 2. Phase 3 Structure

### 2.1 Three Main Tasks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: MACRO PLANNING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TASK 1: CHOOSE TRAINING STRUCTURE                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Select view: Competency-Level Based OR Role-Clustered Based              │
│  • View training modules organized by chosen structure                      │
│  • (For Low Maturity: Only Competency-Level Based available)                │
│                                                                              │
│  TASK 2: SELECT LEARNING FORMATS                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • View all training modules from Phase 2                                   │
│  • Select Learning Format for each module (10 options)                      │
│  • View 3-factor suitability feedback (🟢🟡🔴)                              │
│  • Access "Learn more" for format details                                   │
│                                                                              │
│  TASK 3: TIMELINE PLANNING                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • System generates timeline milestones via LLM                             │
│  • View 5 estimated milestones with dates                                   │
│  • Timeline is informational (not adjustable)                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Prerequisites (from Phase 1 & 2)

| Prerequisite | Source | Data Needed |
|--------------|--------|-------------|
| Learning Objectives | Phase 2 | Competency, Level, PMT breakdown |
| Training Modules | Phase 2 | One module per competency-level (+ MT split if applicable) |
| Gap Data | Phase 2 | Users needing training per competency-level |
| Qualification Archetype | Phase 1 | Selected strategy for Factor 3 |
| Target Group Size | Phase 1 | For participant count scaling |
| Existing Training Coverage | Phase 2 | Competencies already covered (excluded from modules) |

### 2.3 Module Definition (From Phase 2)

Modules are pre-defined in Phase 2's Learning Objectives task:

```
Competency: Requirements Definition
├── Level 1 (Knowing)
│   └── Module: "Requirements Definition - Level 1"
├── Level 2 (Understanding)
│   ├── Module: "Requirements Definition - Level 2 - Method"  ← PMT split
│   └── Module: "Requirements Definition - Level 2 - Tool"    ← PMT split
└── Level 4 (Applying)
    ├── Module: "Requirements Definition - Level 4 - Method"
    └── Module: "Requirements Definition - Level 4 - Tool"
```

**Note**: Competencies marked as having existing training in Phase 2 are excluded from module list.

---

## 3. Task 1: Choose Training Structure

### 3.1 Two Training Views

The administrator selects how to structure the training program:

#### Competency-Level Based View

| Aspect | Description |
|--------|-------------|
| **Organization** | Training by Competency + Level + PMT type |
| **Example** | "Requirements Definition Level 2 - Tool" |
| **Participants** | Multiple roles together in same training |
| **Best For** | Efficient delivery of common competency needs |
| **Availability** | **Default for low-maturity organizations** |

```
Training: "Requirements Definition - Level 2 - Tool"
├── Roles: Requirements Engineer, Systems Architect, Project Manager
├── Estimated Participants: 45
└── Learning Format: [Select]
```

#### Role-Clustered Based View

| Aspect | Description |
|--------|-------------|
| **Organization** | Training by Role cluster groups |
| **Example** | "SE for Engineers" (combining multiple roles) |
| **Participants** | Multiple competencies for one role cluster |
| **Best For** | Role-specific development programs |
| **Requires** | Pre-defined role clusters |

```
Training Program: "SE for Engineers"
├── Roles: Requirements Engineer, Systems Architect, System Developer
├── Contains:
│   ├── "Requirements Definition" Level 2 - Tool
│   ├── "Requirements Definition" Level 2 - Method
│   └── "Systems Thinking" Level 2
└── Learning Format: [Select per module]
```

### 3.2 View Selection Logic

```javascript
function determineAvailableViews(projectData) {
  const { maturityLevel, hasRolesDefined } = projectData;
  
  // Low maturity or no roles: Only Competency-Level view
  if (maturityLevel <= 2 || !hasRolesDefined) {
    return {
      availableViews: ['competency_level'],
      defaultView: 'competency_level',
      showViewSelector: false
    };
  }
  
  // High maturity with roles: Both views available
  return {
    availableViews: ['competency_level', 'role_clustered'],
    defaultView: 'competency_level',
    showViewSelector: true
  };
}
```

### 3.3 Training Program Clusters (For Role-Clustered View)

> **Important Distinction**: Training Program Clusters are **NOT** the same as the 14 SE Role Clusters used for competency mapping in Phase 1/2.
>
> - **14 SE Role Clusters** (from `role_cluster` table): Used for mapping organization roles to SE competency profiles (e.g., System Engineer, V&V Operator, Project Manager)
> - **Training Program Clusters** (defined below): Organizational umbrella groupings for structuring training delivery (e.g., Engineers, Managers, Partners)

#### 3.3.1 Purpose

Training Program Clusters group organization roles into sensible training cohorts from an organizational perspective. This allows:
- Training multiple related roles together efficiently
- Aligning with how organizations typically structure their workforce
- Creating role-appropriate training programs with shared context

#### 3.3.2 Standard Training Program Clusters

| ID | Cluster Name | Description | Typical Organization Roles |
|----|--------------|-------------|---------------------------|
| 1 | **Engineers** | Technical practitioners who design, develop, and implement systems | Software Engineers, Hardware Engineers, System Engineers, Test Engineers, Requirements Engineers, System Architects |
| 2 | **Managers** | Leadership roles responsible for planning, coordination, and decision-making | Project Managers, Department Heads, Team Leads, Product Managers, Program Managers |
| 3 | **Executives** | Senior leadership with strategic oversight | Directors, VPs, C-Level Executives, Senior Management |
| 4 | **Support Staff** | Roles providing technical and operational support | Quality Engineers, Configuration Managers, IT Support, Documentation Specialists |
| 5 | **External Partners** | Customer-facing and supplier-facing roles | Customer Representatives, Account Managers, Supplier Managers, Sales Engineers |
| 6 | **Operations** | Roles focused on production, deployment, and maintenance | Production Engineers, Service Technicians, Field Engineers, Operations Staff |

#### 3.3.3 Mapping Organization Roles to Training Program Clusters

**When**: During Phase 1 Task 2 (Role Mapping), alongside mapping to the 14 SE Role Clusters.

**How**: The LLM will analyze each organization role and assign it to:
1. One of the 14 SE Role Clusters (for competency assessment)
2. One of the Training Program Clusters (for Phase 3 training organization)

**Example Mapping**:

| Organization Role | SE Role Cluster (for competency) | Training Program Cluster (for Phase 3) |
|-------------------|----------------------------------|---------------------------------------|
| "Senior Software Developer" | System Engineer (4) | Engineers |
| "VP of Engineering" | Management (14) | Executives |
| "QA Lead" | Quality Engineer/Manager (8) | Support Staff |
| "Solutions Architect" | System Engineer (4) | Engineers |
| "Project Director" | Project Manager (3) | Managers |
| "Field Service Engineer" | Service Technician (10) | Operations |

#### 3.3.4 Training Program Naming

For Role-Clustered view, training programs are named by cluster:

| Training Program Cluster | Training Program Name |
|--------------------------|----------------------|
| Engineers | "SE for Engineers" |
| Managers | "SE for Managers" |
| Executives | "SE for Executives" |
| Support Staff | "SE for Support Staff" |
| External Partners | "SE for Partners" |
| Operations | "SE for Operations" |

#### 3.3.5 Implementation Note

**Future Task**: When implementing Phase 3, add the Training Program Cluster mapping to Phase 1 Task 2:
1. Create `training_program_cluster` reference table with the 6 clusters above
2. Extend `organization_role_mappings` table to include `training_program_cluster_id`
3. Update the LLM prompt in Role Mapping to assign both cluster types

---

## 4. Task 2: Select Learning Formats

### 4.1 The 10 Learning Formats

| # | ID | Name | Max Level | Participant Range |
|---|-----|------|-----------|-------------------|
| 1 | `seminar` | Seminar/Instructor Lead Training | Level 4 | 10-100 |
| 2 | `webinar` | Webinar/Live Online Event | Level 2 | 1-unlimited |
| 3 | `coaching` | Coaching | Level 6 | 1-5 |
| 4 | `mentoring` | Mentoring | Level 6 | 1-3 |
| 5 | `wbt` | Web-Based Training (WBT) | Level 2 | 1-unlimited |
| 6 | `cbt` | Computer-Based Training (CBT) | Level 2 | 1-unlimited |
| 7 | `game_based` | Game-Based Learning | Level 4 | 5-20 |
| 8 | `conference` | Conference | Level 1 | 50-unlimited |
| 9 | `blended` | Blended Learning | Level 6 | 5-50 |
| 10 | `self_learning` | Self-Learning | Level 2 | 1 |

### 4.2 Level Achievement Constraints

| Constraint | Formats | Max Level | Reason |
|------------|---------|-----------|--------|
| **E-Learning** | WBT, CBT, Self-Learning | Level 2 | No hands-on practice, no real-time feedback |
| **Passive** | Conference | Level 1 | Primarily listening, limited interaction |
| **High-Achievement** | Coaching, Mentoring, Blended | Level 6 | Personalized, hands-on, iterative |

### 4.3 Selection Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  User clicks on a training module                                           │
│                              ↓                                              │
│  Shows 10 Learning Format options (grid/list)                               │
│                              ↓                                              │
│  User selects a format                                                      │
│                              ↓                                              │
│  System displays 3-factor suitability feedback                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Factor 1: Participants    🟢 Suitable                                   ││
│  │ Factor 2: Level Achievable 🟢 Can achieve Level 4                        ││
│  │ Factor 3: Strategy        🟡 Partly Recommended                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              ↓                                              │
│  [Learn more about format]  [Confirm Selection]                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 The 3 Suitability Factors

| Factor | Question | Green 🟢 | Yellow 🟡 | Red 🔴 |
|--------|----------|----------|-----------|--------|
| **Factor 1: Participants** | Does format suit the estimated participant count? | Within optimal range | Within ±20% tolerance | Far outside range |
| **Factor 2: Level Achievable** | Can format achieve the target competency level? | Max level ≥ target | Max level = target - 2 | Max level < target - 2 |
| **Factor 3: Strategy** | Does format align with selected qualification strategy? | Highly recommended (++) | Partly recommended (+) | Not consistent (--) |

**Important**: The system does NOT prevent selection of formats with red indicators. Feedback is advisory.

### 4.5 Factor Evaluation Logic

```javascript
// Factor 1: Participant Count Suitability
function checkParticipantSuitability(formatId, participantCount) {
  const format = LEARNING_FORMATS[formatId];
  const { min, max } = format.participantRange;
  
  if (participantCount >= min && participantCount <= max) {
    return { status: 'green', message: `Suitable for ${participantCount} participants` };
  }
  
  const tolerance = 0.2;
  if (participantCount >= min * (1 - tolerance) && 
      participantCount <= max * (1 + tolerance)) {
    return { status: 'yellow', message: 'Manageable but not ideal' };
  }
  
  return { status: 'red', message: `Not suitable for ${participantCount} participants` };
}

// Factor 2: Level Achievable
function checkLevelAchievable(competencyId, targetLevel, formatId) {
  const achievableLevel = COMPETENCY_LEVEL_MATRIX[competencyId][formatId];
  
  if (achievableLevel >= targetLevel) {
    return { status: 'green', message: `Can achieve Level ${targetLevel}` };
  }
  
  if (achievableLevel >= targetLevel - 2 && achievableLevel > 0) {
    return { status: 'yellow', message: `Can only achieve Level ${achievableLevel}` };
  }
  
  return { status: 'red', message: `Cannot achieve Level ${targetLevel}` };
}

// Factor 3: Strategy Consistency (Multi-Strategy Weighted Support)
// Organizations may have multiple strategies from Phase 1: PRIMARY (weight=2) and SUPPLEMENTARY (weight=1)
function checkStrategyConsistency(strategies, formatId) {
  // If single strategy, use simple lookup
  if (strategies.length === 1) {
    const consistency = STRATEGY_LF_MATRIX[strategies[0].id][formatId];
    switch (consistency) {
      case '++': return { status: 'green', message: 'Highly recommended' };
      case '+':  return { status: 'yellow', message: 'Partly recommended' };
      case '--': return { status: 'red', message: 'Not consistent' };
    }
  }

  // Multi-strategy: calculate weighted average
  let totalScore = 0;
  let totalWeight = 0;
  const scoreMap = { '++': 3, '+': 2, '--': 1 };

  for (const strategy of strategies) {
    const consistency = STRATEGY_LF_MATRIX[strategy.id][formatId];
    const weight = strategy.type === 'PRIMARY' ? 2 : 1;  // PRIMARY=2x, SUPPLEMENTARY=1x
    totalScore += scoreMap[consistency] * weight;
    totalWeight += weight;
  }

  const avgScore = totalScore / totalWeight;

  if (avgScore >= 2.5) return { status: 'green', message: 'Highly recommended' };
  if (avgScore >= 1.5) return { status: 'yellow', message: 'Partly recommended' };
  return { status: 'red', message: 'Not consistent' };
}
```

---

## 5. Task 3: Timeline Planning (LLM-Generated)

### 5.1 Overview

Timeline planning uses LLM to generate estimated milestone dates based on the training program context. The timeline is **informational only** and **not adjustable** by the user.

### 5.2 The 5 Milestones

| # | Milestone | Description | Typical Timeframe |
|---|-----------|-------------|-------------------|
| 1 | **Concept Development Start** | Training material development begins | Current Quarter |
| 2 | **Concept Development End** | Training materials ready | +2-4 months |
| 3 | **Pilot Start** | Pilot training with test group begins | +3-5 months |
| 4 | **Rollout Start** | First full training session occurs | +4-8 months |
| 5 | **Rollout End** | Last planned training session completes | +10-20 months |

**Note**: Sustainment/Continuous Improvement is acknowledged as ongoing after rollout, not scheduled as a specific milestone.

### 5.3 LLM Input Context

The LLM receives the following context to generate timeline estimates:

```javascript
const timelinePromptContext = {
  // Project Context
  organizationName: project.organizationName,
  maturityLevel: project.maturityLevel,
  selectedStrategy: project.archetypeId,
  
  // Training Scope
  totalModules: modules.length,
  totalEstimatedParticipants: calculateTotalParticipants(modules),
  competenciesIncluded: getUniqueCompetencies(modules),
  
  // Format Distribution
  formatDistribution: getFormatCounts(modules),
  hasELearningComponents: modules.some(m => isELearning(m.formatId)),
  hasInPersonComponents: modules.some(m => isInPerson(m.formatId)),
  
  // Complexity Indicators
  targetLevelDistribution: getLevelCounts(modules),
  pmtBreakdownCount: modules.filter(m => m.pmtType !== 'combined').length,
  
  // Reference Durations (from Training Lifecycle Model)
  referenceDurations: {
    development: "2-4 months",
    pilot: "1-3 months",
    initialImplementation: "6-12 months"
  },
  
  // Current Date for baseline
  currentDate: new Date().toISOString()
};
```

### 5.4 LLM Prompt Template

```
You are an expert in training program planning and implementation. Based on the following SE training program context, generate realistic timeline estimates for 5 key milestones.

## Training Program Context
- Organization Maturity Level: {maturityLevel}
- Selected Qualification Strategy: {selectedStrategy}
- Total Training Modules: {totalModules}
- Total Estimated Participants: {totalEstimatedParticipants}
- Competencies: {competenciesIncluded}
- Format Distribution: {formatDistribution}
- Has E-Learning Components: {hasELearningComponents}
- Has In-Person Components: {hasInPersonComponents}
- Target Levels: {targetLevelDistribution}

## Reference Durations (from Training Lifecycle Research)
- Development Phase: 2-4 months
- Pilot Phase: 1-3 months  
- Initial Implementation: 6-12 months

## Current Date
{currentDate}

## Task
Generate estimated dates for these 5 milestones:
1. Concept Development Start - When training material development should begin
2. Concept Development End - When training materials should be ready
3. Pilot Start - When pilot training with test group should begin
4. Rollout Start - When first full training session should occur
5. Rollout End - When last planned training session should complete

Consider:
- Larger participant counts require longer rollout periods
- E-learning content requires more upfront development time but enables parallel delivery
- In-person formats require sequential scheduling
- Higher maturity organizations may move faster
- More modules/competencies extend development time
- Complex format mixes (blended) require more coordination

Respond in JSON format:
{
  "milestones": [
    {"id": 1, "name": "Concept Development Start", "estimatedDate": "YYYY-MM-DD", "quarter": "Q1 2026"},
    {"id": 2, "name": "Concept Development End", "estimatedDate": "YYYY-MM-DD", "quarter": "Q2 2026"},
    {"id": 3, "name": "Pilot Start", "estimatedDate": "YYYY-MM-DD", "quarter": "Q2 2026"},
    {"id": 4, "name": "Rollout Start", "estimatedDate": "YYYY-MM-DD", "quarter": "Q3 2026"},
    {"id": 5, "name": "Rollout End", "estimatedDate": "YYYY-MM-DD", "quarter": "Q4 2027"}
  ],
  "reasoning": "Brief explanation of timeline estimation logic"
}
```

### 5.5 LLM Response Processing

```javascript
async function generateTimelineMilestones(projectContext) {
  const prompt = buildTimelinePrompt(projectContext);
  
  const response = await llmService.generate({
    prompt: prompt,
    responseFormat: 'json',
    temperature: 0.3  // Lower temperature for more consistent estimates
  });
  
  const parsed = JSON.parse(response);
  
  return {
    milestones: parsed.milestones.map(m => ({
      id: m.id,
      name: m.name,
      estimatedDate: new Date(m.estimatedDate),
      quarter: m.quarter,
      displayDate: formatDisplayDate(m.estimatedDate)
    })),
    reasoning: parsed.reasoning,
    generatedAt: new Date(),
    isEditable: false  // Timeline is not adjustable
  };
}
```

### 5.6 Timeline Display

The timeline is displayed as read-only information:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIMELINE MILESTONES                                                         │
│  Generated based on your training program scope and complexity               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ● Concept Development Start                              Q1 2026           │
│    Training material development begins                   Jan 2026          │
│                                                                              │
│  ● Concept Development End                                Q2 2026           │
│    Training materials ready                               Apr 2026          │
│                                                                              │
│  ● Pilot Start                                            Q2 2026           │
│    Pilot training with test group begins                  May 2026          │
│                                                                              │
│  ● Rollout Start                                          Q3 2026           │
│    First full training session                            Jul 2026          │
│                                                                              │
│  ● Rollout End                                            Q4 2027           │
│    Last planned training session                          Dec 2027          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ℹ️ These estimates are based on your program scope (6 modules, 240         │
│     participants) and selected formats. Sustainment continues after         │
│     rollout as an ongoing activity.                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.7 Visual Timeline Bar

```
2026                                              2027
Q1      Q2      Q3      Q4      Q1      Q2      Q3      Q4
├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤
[==DEV==][PILOT][=======ROLLOUT / IMPLEMENTATION========]
    ↑       ↑       ↑                               ↑
    │       │       │                               │
    │       │       │                               └── Rollout End
    │       │       └── Rollout Start
    │       └── Pilot Start
    └── Dev Start/End
```

---

## 6. Learning Format Master Data

### 6.1 Complete Format Definitions

```javascript
const LEARNING_FORMATS = {
  seminar: {
    id: "seminar",
    name: "Seminar / Instructor Lead Training",
    shortName: "Seminar",
    description: "Face-to-face, in-person training led by trainer(s) with direct interaction.",
    icon: "🎓",
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 10, max: 100 },
      learningType: "formal"
    },
    maxLevel: 4,
    efforts: { contentCreation: 4, contentUpdation: 4, perTraining: 4 },
    advantages: ["Direct Feedback", "Standardized Content", "High Interaction"],
    disadvantages: ["Limited Accessibility", "No Self-Paced", "Travel Expenses"],
    suitableArchetypes: ["common_basic_understanding", "se_for_managers", "orientation_in_pilot_project", "needs_based_project_oriented"]
  },
  
  webinar: {
    id: "webinar",
    name: "Webinar / Live Online Event",
    shortName: "Webinar",
    description: "Online live broadcast at specific time with chat interaction.",
    icon: "💻",
    characteristics: {
      modeOfDelivery: "online",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 1, max: Infinity },
      learningType: "formal"
    },
    maxLevel: 2,
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 3 },
    advantages: ["Direct Feedback", "Global Reach", "Cost Effective"],
    disadvantages: ["Low Interaction", "Technical Issues", "No Self-Paced"],
    suitableArchetypes: ["common_basic_understanding", "se_for_managers", "continuous_support"]
  },
  
  coaching: {
    id: "coaching",
    name: "Coaching",
    shortName: "Coaching",
    description: "Attentive observation of learner with expert assistance.",
    icon: "🎯",
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 5 },
      learningType: "formal"
    },
    maxLevel: 6,
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 5 },
    advantages: ["Personalized Guidance", "Accountability", "Deep Learning"],
    disadvantages: ["Time Intensive", "Limited Scale", "High Cost"],
    suitableArchetypes: ["se_for_managers", "orientation_in_pilot_project", "needs_based_project_oriented", "train_the_trainer"]
  },
  
  mentoring: {
    id: "mentoring",
    name: "Mentoring",
    shortName: "Mentoring",
    description: "Knowledge acquisition through work-related tasks under experienced guidance.",
    icon: "🤝",
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 3 },
      learningType: "informal"
    },
    maxLevel: 6,
    efforts: { contentCreation: 2, contentUpdation: 1, perTraining: 4 },
    advantages: ["Successor Training", "Real-World Learning", "Relationship Building"],
    disadvantages: ["Gradual Results", "Limited Mentors", "Inconsistent Quality"],
    suitableArchetypes: ["orientation_in_pilot_project", "needs_based_project_oriented", "train_the_trainer"]
  },
  
  wbt: {
    id: "wbt",
    name: "Web-Based Training (WBT)",
    shortName: "WBT",
    description: "Self-paced online learning modules via internet.",
    icon: "🌐",
    characteristics: {
      modeOfDelivery: "online",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: Infinity },
      learningType: "formal"
    },
    maxLevel: 2,
    isELearning: true,
    efforts: { contentCreation: 5, contentUpdation: 2, perTraining: 1 },
    advantages: ["Self-Paced", "Scalable", "Tracking"],
    disadvantages: ["Low Engagement", "No Hands-On", "Limited Support"],
    suitableArchetypes: ["needs_based_project_oriented", "continuous_support", "train_the_trainer"]
  },
  
  cbt: {
    id: "cbt",
    name: "Computer-Based Training (CBT)",
    shortName: "CBT",
    description: "Offline self-paced training software, no internet required.",
    icon: "💾",
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: Infinity },
      learningType: "formal"
    },
    maxLevel: 2,
    isELearning: true,
    efforts: { contentCreation: 5, contentUpdation: 3, perTraining: 1 },
    advantages: ["Offline Access", "Self-Paced", "Consistent"],
    disadvantages: ["Outdated Content", "Installation Issues", "Low Engagement"],
    suitableArchetypes: ["needs_based_project_oriented", "continuous_support"]
  },
  
  game_based: {
    id: "game_based",
    name: "Game-Based Learning",
    shortName: "Game-Based",
    description: "Learning through gamification, serious games, and simulations.",
    icon: "🎮",
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 5, max: 20 },
      learningType: "formal"
    },
    maxLevel: 4,
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 3 },
    advantages: ["High Engagement", "Safe Practice", "Measurable"],
    disadvantages: ["High Cost", "Limited Scale", "Technical Needs"],
    suitableArchetypes: ["common_basic_understanding", "se_for_managers", "orientation_in_pilot_project"]
  },
  
  conference: {
    id: "conference",
    name: "Conference",
    shortName: "Conference",
    description: "Large-scale professional gatherings with presentations and networking.",
    icon: "🎪",
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 50, max: Infinity },
      learningType: "formal"
    },
    maxLevel: 1,
    isPassive: true,
    efforts: { contentCreation: 2, contentUpdation: 2, perTraining: 3 },
    advantages: ["Networking", "New Ideas", "Inspiration"],
    disadvantages: ["Passive Learning", "High Cost", "Time Consuming"],
    suitableArchetypes: ["common_basic_understanding", "continuous_support"]
  },
  
  blended: {
    id: "blended",
    name: "Blended Learning",
    shortName: "Blended",
    description: "Combination of synchronous/asynchronous, in-person/online formats.",
    icon: "🔄",
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "hybrid",
      collaborationType: "group",
      participantRange: { min: 5, max: 50 },
      learningType: "formal"
    },
    maxLevel: 6,
    isRecommended: true,
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 4 },
    advantages: ["Flexible", "Best of Both", "Multi-Level Coverage"],
    disadvantages: ["Complex Planning", "Integration Challenges", "Resource Intensive"],
    suitableArchetypes: ["common_basic_understanding", "se_for_managers", "orientation_in_pilot_project", "needs_based_project_oriented", "train_the_trainer"]
  },
  
  self_learning: {
    id: "self_learning",
    name: "Self-Learning",
    shortName: "Self-Learning",
    description: "Independent, self-directed knowledge acquisition.",
    icon: "📚",
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 1 },
      learningType: "informal"
    },
    maxLevel: 2,
    isELearning: true,
    efforts: { contentCreation: 1, contentUpdation: 1, perTraining: 1 },
    advantages: ["Complete Flexibility", "Low Cost", "Self-Directed"],
    disadvantages: ["No Structure", "No Feedback", "Requires Motivation"],
    suitableArchetypes: ["continuous_support", "needs_based_project_oriented"]
  }
};
```

---

## 7. Matrices

### 7.1 Strategy-Learning Format Consistency Matrix

**Note**: Strategy keys match the `strategy_template` table in the database.

| Strategy Template ID | DB Name | Key Used Below |
|---------------------|---------|----------------|
| 1 | Common basic understanding | `common_basic_understanding` |
| 2 | SE for managers | `se_for_managers` |
| 3 | Orientation in pilot project | `orientation_in_pilot_project` |
| 4 | Needs-based, project-oriented training | `needs_based_project_oriented` |
| 5 | Continuous support | `continuous_support` |
| 6 | Train the trainer | `train_the_trainer` |
| 7 | Certification | `certification` |

```javascript
const STRATEGY_LF_MATRIX = {
  common_basic_understanding:      { seminar: '++', webinar: '+',  coaching: '--', mentoring: '--', wbt: '--', cbt: '--', game_based: '+',  conference: '+',  blended: '++', self_learning: '--' },
  se_for_managers:                 { seminar: '++', webinar: '+',  coaching: '++', mentoring: '++', wbt: '+',  cbt: '--', game_based: '+',  conference: '+',  blended: '++', self_learning: '--' },
  orientation_in_pilot_project:    { seminar: '++', webinar: '+',  coaching: '++', mentoring: '++', wbt: '--', cbt: '--', game_based: '++', conference: '--', blended: '++', self_learning: '--' },
  needs_based_project_oriented:    { seminar: '++', webinar: '+',  coaching: '+',  mentoring: '+',  wbt: '+',  cbt: '+',  game_based: '+',  conference: '--', blended: '++', self_learning: '+'  },
  train_the_trainer:               { seminar: '+',  webinar: '+',  coaching: '++', mentoring: '++', wbt: '+',  cbt: '+',  game_based: '+',  conference: '--', blended: '+',  self_learning: '+'  },
  continuous_support:              { seminar: '+',  webinar: '++', coaching: '+',  mentoring: '+',  wbt: '++', cbt: '++', game_based: '+',  conference: '++', blended: '+',  self_learning: '++' },
  certification:                   { seminar: '+',  webinar: '+',  coaching: '+',  mentoring: '+',  wbt: '+',  cbt: '+',  game_based: '--', conference: '+',  blended: '+',  self_learning: '+'  }
};
```

**Legend**: `++` = Highly Recommended (🟢), `+` = Partly Recommended (🟡), `--` = Not Consistent (🔴)

### 7.2 Competency-Level Achievable Matrix

**Note**: Competency keys match the `competency` table in the database.

| Competency ID | DB Name | Key Used Below | Area |
|---------------|---------|----------------|------|
| 1 | Systems Thinking | `systems_thinking` | Core |
| 4 | Lifecycle Consideration | `lifecycle_consideration` | Core |
| 5 | Customer / Value Orientation | `customer_value_orientation` | Core |
| 6 | Systems Modelling and Analysis | `systems_modelling_and_analysis` | Core |
| 7 | Communication | `communication` | Social/Personal |
| 8 | Leadership | `leadership` | Social/Personal |
| 9 | Self-Organization | `self_organization` | Social/Personal |
| 10 | Project Management | `project_management` | Management |
| 11 | Decision Management | `decision_management` | Management |
| 12 | Information Management | `information_management` | Management |
| 13 | Configuration Management | `configuration_management` | Management |
| 14 | Requirements Definition | `requirements_definition` | Technical |
| 15 | System Architecting | `system_architecting` | Technical |
| 16 | Integration, Verification, Validation | `integration_verification_validation` | Technical |
| 17 | Operation and Support | `operation_and_support` | Technical |
| 18 | Agile Methods | `agile_methods` | Technical |

```javascript
const COMPETENCY_LEVEL_MATRIX = {
  // CORE COMPETENCIES (harder to achieve, experience-based)
  systems_thinking:                  { seminar: 2, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  lifecycle_consideration:           { seminar: 2, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  customer_value_orientation:        { seminar: 2, webinar: 2, coaching: 4, mentoring: 6, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  systems_modelling_and_analysis:    { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 1, blended: 6, self_learning: 2 },

  // SOCIAL/PERSONAL COMPETENCIES
  communication:                     { seminar: 4, webinar: 2, coaching: 6, mentoring: 4, wbt: 2, cbt: 1, game_based: 4, conference: 2, blended: 4, self_learning: 1 },
  leadership:                        { seminar: 2, webinar: 2, coaching: 6, mentoring: 6, wbt: 2, cbt: 1, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  self_organization:                 { seminar: 2, webinar: 1, coaching: 4, mentoring: 4, wbt: 1, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 2 },

  // MANAGEMENT COMPETENCIES
  project_management:                { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  decision_management:               { seminar: 4, webinar: 2, coaching: 6, mentoring: 6, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  information_management:            { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 2, conference: 1, blended: 4, self_learning: 2 },
  configuration_management:          { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },

  // TECHNICAL COMPETENCIES
  requirements_definition:           { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  system_architecting:               { seminar: 4, webinar: 2, coaching: 4, mentoring: 6, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  integration_verification_validation: { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  operation_and_support:             { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 2, conference: 2, blended: 4, self_learning: 2 },

  // AGILE
  agile_methods:                     { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 }
};
```

**Value Legend**: `0` = Not suitable, `1` = Level 1, `2` = Level 2, `4` = Level 4, `6` = Level 6

---

## 8. Participant Count Scaling

### 8.1 The Challenge

Competency assessment data typically comes from a subset of the organization. If target group is 200 but only 15 completed assessment, raw gap counts underrepresent actual training needs.

### 8.2 Scaling Formula

```
Scaling Factor = Target Group Size (Phase 1) / Assessed Users (Phase 2)

Estimated Participants = Users with Gap × Scaling Factor
```

### 8.3 Example

| Data Point | Value |
|------------|-------|
| Target Group Size | 200 |
| Assessed Users | 15 |
| Scaling Factor | 200 / 15 = 13.33 |
| Users with Gap (Req Def L2) | 8 |
| **Estimated Participants** | 8 × 13.33 ≈ **107** |

### 8.4 User Notification

Display scaling information transparently:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ℹ️ PARTICIPANT ESTIMATION                                                   │
│  Participant counts are scaled estimates based on:                          │
│  • Assessed users: 15                                                        │
│  • Target group size: 200                                                    │
│  • Scaling factor: 13.3x                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. UI/UX Design

### 9.1 Phase 3 Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: MACRO PLANNING                                                     │
│  Building Trainings Structure and Plan                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Progress: ████████████░░░░░░░░ 60%                                         │
│                                                                              │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐        │
│  │                   │  │                   │  │                   │        │
│  │  📋 TASK 1        │  │  🎓 TASK 2        │  │  📅 TASK 3        │        │
│  │  Training         │  │  Learning         │  │  Timeline         │        │
│  │  Structure        │  │  Formats          │  │  Planning         │        │
│  │                   │  │                   │  │                   │        │
│  │  ✅ Complete      │  │  ⏳ In Progress   │  │  ○ Not Started    │        │
│  │                   │  │  4/6 configured   │  │                   │        │
│  │                   │  │                   │  │                   │        │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Task 1: Training Structure Selection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TASK 1: CHOOSE TRAINING STRUCTURE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  How do you want to structure your training program?                        │
│                                                                              │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐     │
│  │                                │  │                                │     │
│  │  📊 COMPETENCY-LEVEL BASED    │  │  👥 ROLE-CLUSTERED BASED       │     │
│  │  ─────────────────────────────│  │  ─────────────────────────────│     │
│  │  Training by competency and   │  │  Training by role groups       │     │
│  │  bring all roles together     │  │  with multiple competencies    │     │
│  │                                │  │                                │     │
│  │  Example:                      │  │  Example:                      │     │
│  │  "Req Def L2 - Tool"          │  │  "SE for Engineers"            │     │
│  │  with Req Eng, Sys Arch, PM   │  │  with Req Def, Sys Think, etc  │     │
│  │                                │  │                                │     │
│  │       [Select ●]               │  │       [Select ○]               │     │
│  │                                │  │                                │     │
│  └────────────────────────────────┘  └────────────────────────────────┘     │
│                                                                              │
│                                              [Continue to Task 2 →]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Task 2: Format Selection (Module List)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TASK 2: SELECT LEARNING FORMATS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ℹ️ Participant counts scaled: 15 assessed → 200 target (13.3x)             │
│  Strategy: Need-Based Training                                              │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Req Eng, Sys Arch, PM                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Requirements Definition - Level 2 - Tool                               ││
│  │  Est. 45 participants │ Target: L2 (Understanding)                      ││
│  │                                                           [Seminar 🎓]  ││
│  │  Suitability: 🟢 🟢 🟢                                    [✓ Confirmed] ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Req Eng, Sys Arch                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Requirements Definition - Level 2 - Method                             ││
│  │  Est. 38 participants │ Target: L2 (Understanding)                      ││
│  │                                                        [Select Format ▼]││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  All Engineering Roles                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Systems Thinking - Level 2                                             ││
│  │  Est. 120 participants │ Target: L2 (Understanding)                     ││
│  │                                                           [Webinar 💻]  ││
│  │  Suitability: 🟢 🟢 🟡                                    [✓ Confirmed] ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│                                              [Continue to Task 3 →]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.4 Format Selection Panel (Expanded)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SELECT LEARNING FORMAT                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                   │
│  │ 🎓  │ │ 💻  │ │ 🎯  │ │ 🤝  │ │ 🌐  │                                   │
│  │Sem. │ │Web. │ │Coach│ │Ment.│ │ WBT │                                   │
│  │L4   │ │L2   │ │L6   │ │L6   │ │L2 ⚠│                                   │
│  │🟢🟢🟢│ │🟢🟢🟡│ │🔴🟢🟢│ │🔴🟢🟢│ │🟢🟡🟡│                                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                                   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                   │
│  │ 💾  │ │ 🎮  │ │ 🎪  │ │ 🔄  │ │ 📚  │                                   │
│  │ CBT │ │Game │ │Conf.│ │Blend│ │Self │                                   │
│  │L2 ⚠│ │L4   │ │L1 ⚠│ │L6 ⭐│ │L2 ⚠│                                   │
│  │🟢🟡🟡│ │🟡🟢🟢│ │🟢🔴🔴│ │🟢🟢🟢│ │🔴🟡🟡│                                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                                   │
│                                                                              │
│  ⚠ = E-Learning (max L2)  ⭐ = Recommended                                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  SELECTED: 🎓 Seminar                                                        │
│                                                                              │
│  SUITABILITY CHECK:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 🟢 Factor 1: Participants (45)                                          ││
│  │    Suitable - Seminar works well for 10-100 participants                ││
│  │                                                                          ││
│  │ 🟢 Factor 2: Level Achievable                                            ││
│  │    Can achieve Level 4 (target is Level 2)                              ││
│  │                                                                          ││
│  │ 🟢 Factor 3: Strategy Consistency                                        ││
│  │    Highly Recommended for "Need-Based Training"                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [Learn more about Seminar]                        [Confirm Selection]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.5 Task 3: Timeline Planning (LLM-Generated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TASK 3: TIMELINE PLANNING                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Based on your training program scope and complexity, here are the          │
│  estimated timeline milestones:                                             │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  📍 MILESTONES                                                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ● Concept Development Start                                            ││
│  │    Training material development begins                                 ││
│  │                                                     Q1 2026 │ Jan 2026  ││
│  │                                                                          ││
│  │  ● Concept Development End                                              ││
│  │    Training materials ready for pilot                                   ││
│  │                                                     Q2 2026 │ Apr 2026  ││
│  │                                                                          ││
│  │  ● Pilot Start                                                          ││
│  │    Pilot training with test group begins                                ││
│  │                                                     Q2 2026 │ May 2026  ││
│  │                                                                          ││
│  │  ● Rollout Start                                                        ││
│  │    First full training session                                          ││
│  │                                                     Q3 2026 │ Jul 2026  ││
│  │                                                                          ││
│  │  ● Rollout End                                                          ││
│  │    Last planned training session completes                              ││
│  │                                                     Q4 2027 │ Dec 2027  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  📊 TIMELINE VISUALIZATION                                                   │
│                                                                              │
│  2026                                              2027                      │
│  Q1      Q2      Q3      Q4      Q1      Q2      Q3      Q4                 │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤          │
│  [==DEV==][PILOT][=============ROLLOUT / IMPLEMENTATION==========]          │
│      ↑       ↑       ↑                                       ↑              │
│      │       │       │                                       │              │
│    Start    Pilot  Rollout                              Rollout             │
│    Dev      Start  Start                                End                 │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ℹ️ These estimates are based on:                                            │
│  • 6 training modules                                                        │
│  • 240 total estimated participants                                          │
│  • Mix of Seminar and Webinar formats                                       │
│  • Need-Based Training strategy                                             │
│                                                                              │
│  Sustainment and continuous improvement continues as an ongoing             │
│  activity after rollout completion.                                         │
│                                                                              │
│                                              [Complete Phase 3 →]            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Data Models

### 10.1 Training Module (from Phase 2)

```typescript
interface TrainingModule {
  id: string;
  competencyId: string;
  competencyName: string;
  targetLevel: 1 | 2 | 4;
  pmtType: 'process' | 'method' | 'tool' | 'combined';
  
  // Roles needing this module
  roles: RoleInfo[];
  
  // User counts
  actualUsersWithGap: number;
  estimatedParticipants: number;  // After scaling
  
  // Phase 3 selections
  selectedFormatId?: string;
  formatSuitability?: FormatSuitability;
  confirmed: boolean;
}
```

### 10.2 Format Suitability Result

```typescript
interface FormatSuitability {
  formatId: string;
  formatName: string;
  
  factors: {
    participants: { status: 'green' | 'yellow' | 'red'; message: string };
    levelAchievable: { status: 'green' | 'yellow' | 'red'; message: string; achievableLevel: number };
    strategyConsistency: { status: 'green' | 'yellow' | 'red'; message: string };
  };
}
```

### 10.3 Timeline Milestones (LLM-Generated)

```typescript
interface TimelineMilestones {
  projectId: string;
  
  milestones: Milestone[];
  
  reasoning: string;  // LLM's explanation
  generatedAt: Date;
  isEditable: false;  // Always false - not adjustable
  
  // Context used for generation
  generationContext: {
    totalModules: number;
    totalParticipants: number;
    formatDistribution: Record<string, number>;
    strategy: string;
  };
}

interface Milestone {
  id: number;
  name: string;
  description: string;
  estimatedDate: Date;
  quarter: string;  // e.g., "Q2 2026"
}
```

### 10.4 Phase 3 Configuration (Progress Tracking)

```typescript
// Database table: phase3_config
interface Phase3Config {
  id: number;
  organization_id: number;
  selected_view: 'competency_level' | 'role_clustered';
  task1_completed: boolean;
  task2_completed: boolean;
  task3_completed: boolean;
  created_at: Date;
  updated_at: Date;
}
```

### 10.5 Phase 3 Training Module (Database Table)

```typescript
// Database table: phase3_training_module
interface Phase3TrainingModule {
  id: number;
  organization_id: number;
  module_key: string;               // e.g., "requirements_definition_L2_method"
  competency_id: number;
  competency_name: string;
  target_level: 1 | 2 | 4;
  pmt_type: 'process' | 'method' | 'tool' | 'combined';
  actual_users_with_gap: number;
  estimated_participants: number;   // Scaled value
  selected_format_id: number | null;
  format_suitability: JSON;         // Stores 3-factor results
  confirmed: boolean;
  training_program_cluster_id: number | null;  // For role-clustered view
  cluster_name: string | null;                 // "SE for Engineers", etc.
  created_at: Date;
  updated_at: Date;
}
```

### 10.6 Phase 3 Output

```typescript
interface Phase3Output {
  projectId: string;
  
  // Task 1: Training Structure
  selectedView: 'competency_level' | 'role_clustered';
  
  // Task 2: Learning Format Selections
  trainingModules: TrainingModule[];
  
  // Task 3: Timeline
  timeline: TimelineMilestones;
  
  // Scaling info
  scalingInfo: {
    actualAssessedUsers: number;
    targetGroupSize: number;
    scalingFactor: number;
  };
  
  // Summary
  summary: {
    totalModules: number;
    configuredModules: number;
    totalEstimatedParticipants: number;
    formatDistribution: Record<string, number>;
    warningsCount: number;
  };
}
```

---

## 11. API Specification

### 11.1 Endpoints (Implemented)

```
# Phase 3 Configuration & Progress Tracking
GET  /api/phase3/config/<organization_id>
     Response: { success: true, config: Phase3Config }
     Purpose: Get Phase 3 progress status (task completion states)

# Task 1: Training Structure
GET  /api/phase3/available-views/<organization_id>
     Response: { success: true, available_views: ['competency_level', 'role_clustered'] }
     Purpose: Get available views based on organization maturity

POST /api/phase3/select-view/<organization_id>
     Body: { selected_view: 'competency_level' | 'role_clustered' }
     Response: { success: true, message: '...' }
     Purpose: Select training structure view

# Training Program Clusters (for Role-Clustered View)
GET  /api/phase3/training-clusters
     Response: { success: true, clusters: TrainingProgramCluster[] }
     Purpose: Get all 6 training program clusters

GET  /api/phase3/training-clusters/<organization_id>/distribution
     Response: { success: true, distribution: {...} }
     Purpose: Get organization's role distribution across clusters

# Task 2: Learning Formats
GET  /api/phase3/training-modules/<organization_id>
     Response: { success: true, modules: TrainingModule[] }
     Purpose: Get all training modules with current selections

GET  /api/phase3/learning-formats
     Response: { success: true, formats: LearningFormat[] }
     Purpose: Get all 10 learning formats with properties

POST /api/phase3/evaluate-format
     Body: { organization_id, module_id, learning_format_id }
     Response: { success: true, suitability: FormatSuitability }
     Purpose: Evaluate 3-factor suitability for a format

POST /api/phase3/select-format
     Body: { organization_id, module_id, learning_format_id }
     Response: { success: true, ... }
     Purpose: Select and confirm format for a module

POST /api/phase3/complete-task2/<organization_id>
     Response: { success: true }
     Purpose: Mark Task 2 as complete

# Task 3: Timeline (LLM-Generated)
POST /api/phase3/generate-timeline
     Body: { organization_id }
     Response: { success: true, milestones: Milestone[] }
     Purpose: Generate LLM-based timeline milestones

GET  /api/phase3/timeline/<organization_id>
     Response: { success: true, milestones: Milestone[] }
     Purpose: Get previously generated timeline

# Phase 3 Output & Export
GET  /api/phase3/output/<organization_id>
     Response: Phase3Output (full summary with all data)
     Purpose: Get complete Phase 3 output for review/export

GET  /api/phase3/export/<organization_id>
     Response: Excel file (blob, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
     Purpose: Export Phase 3 data to Excel file
```

### 11.2 Timeline Generation Endpoint

```javascript
// POST /api/phase3/generate-timeline
app.post('/api/phase3/generate-timeline', async (req, res) => {
  const { projectId } = req.body;
  
  // Gather context
  const project = await getProject(projectId);
  const modules = await getTrainingModules(projectId);
  
  const context = {
    organizationName: project.organizationName,
    maturityLevel: project.maturityLevel,
    selectedStrategy: project.archetypeId,
    totalModules: modules.length,
    totalEstimatedParticipants: modules.reduce((s, m) => s + m.estimatedParticipants, 0),
    competenciesIncluded: [...new Set(modules.map(m => m.competencyName))],
    formatDistribution: countFormats(modules),
    hasELearningComponents: modules.some(m => isELearning(m.selectedFormatId)),
    hasInPersonComponents: modules.some(m => isInPerson(m.selectedFormatId)),
    targetLevelDistribution: countLevels(modules),
    currentDate: new Date().toISOString()
  };
  
  // Generate via LLM
  const prompt = buildTimelinePrompt(context);
  const llmResponse = await llmService.generate({ prompt, responseFormat: 'json' });
  
  // Parse and save
  const timeline = parseTimelineResponse(llmResponse);
  await saveTimeline(projectId, timeline);
  
  res.json(timeline);
});
```

---

## 12. Phase 3 Outputs

Phase 3 produces the following outputs for Phase 4:

| Output | Description |
|--------|-------------|
| **Training Structure** | Selected view (Competency-Level or Role-Clustered) |
| **Training Modules with Formats** | Each module has selected learning format |
| **Participant Estimates** | Scaled from assessment data to target group size |
| **Suitability Documentation** | Record of 3-factor feedback for each selection |
| **Timeline Milestones** | LLM-generated estimates for 5 key milestones |
| **Warnings and Notes** | Any red indicators or constraints flagged |

These outputs form the **SE Training Concept** that guides detailed planning in Phase 4.

---

## 13. Implementation Checklist

### 13.1 Task Breakdown (Implementation Status)

| # | Task | Priority | Effort | Status |
|---|------|----------|--------|--------|
| 1 | Seed Learning Format data | HIGH | S | DONE (migration 014) |
| 2 | Seed Strategy-LF Matrix | HIGH | S | DONE (migration 014) |
| 3 | Seed Competency-Level Matrix | HIGH | S | DONE (migration 014) |
| 4 | Build Phase 3 dashboard with 3 tasks | HIGH | M | DONE (PhaseThree.vue) |
| 5 | Build Task 1: Training structure selection | HIGH | M | DONE (TrainingStructureSelection.vue) |
| 6 | Build Task 2: Module list (Competency-Level view) | HIGH | L | DONE (LearningFormatSelection.vue) |
| 7 | Build Task 2: Module list (Role-Clustered view) | MEDIUM | L | DONE |
| 8 | Build format selection dropdown with 10 formats | HIGH | M | DONE (FormatSelectorDialog.vue) |
| 9 | Implement 3-factor suitability evaluation | HIGH | M | DONE (phase3_planning_service.py) |
| 10 | Build "Learn more" format details modal | MEDIUM | M | DONE (advantages/disadvantages stored) |
| 11 | Implement participant count scaling | HIGH | S | DONE |
| 12 | Build Task 3: LLM timeline generation | HIGH | L | DONE (GPT-4o-mini) |
| 13 | Build timeline display (read-only) | HIGH | M | DONE (TimelinePlanning.vue + Gantt) |
| 14 | Build Phase 3 summary/review page | MEDIUM | M | DONE (dashboard with completion banner) |
| 15 | Implement Excel export | LOW | M | DONE (openpyxl export) |
| 16 | API endpoints implementation | HIGH | L | DONE (phase3_planning.py) |
| 17 | Integration tests | MEDIUM | M | PENDING |

### 13.2 Testing Checklist

**Task 1: Training Structure**
- [x] Low maturity shows only Competency-Level view
- [x] High maturity shows both views
- [x] Selection persists (stored in phase3_config table)

**Task 2: Format Selection**
- [x] All 10 formats display correctly
- [x] Factor 1 (participants) evaluates correctly with ±20% tolerance
- [x] Factor 2 (level) evaluates correctly against competency-LF matrix
- [x] Factor 3 (strategy) evaluates correctly with multi-strategy weighted support
- [x] E-Learning formats show max L2 constraint
- [x] Red indicators don't block selection (advisory only)
- [x] Multi-strategy weighted aggregation (PRIMARY=2x, SUPPLEMENTARY=1x)

**Task 3: Timeline**
- [x] LLM generates 5 milestones via GPT-4o-mini
- [x] Dates are reasonable based on context
- [x] Timeline is NOT editable (view only)
- [x] Gantt chart visualization with dynamic bar positioning
- [x] Regenerate timeline option available
- [x] AI reasoning displayed

**Export**
- [x] Excel export includes all Phase 3 data
- [x] Role-Clustered view groups by Training Program with merged cells
- [x] Timeline milestones included in export

---

## References

1. Conceptual Framework (LaTeX) - Chapter 4
2. Theoretical Foundations (LaTeX) - Chapter 3, Section: Training Program Lifecycle
3. Ulf Meeting Notes (11-12-2025)
4. Sachin Kumar Master Thesis (2023) - Learning Formats
5. Marcel Niemeyer Master Thesis (2023) - SE Qualification Planning Methodology

---

## Document Version

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 3.3 | January 2026 | Jomon George | CURRENT |

**Key Changes in v3.3:**
- Verified implementation against codebase (January 2026)
- Added multi-strategy weighted aggregation for Factor 3 (PRIMARY=2x, SUPPLEMENTARY=1x)
- Documented Phase 3 Configuration table (`phase3_config`) for progress tracking
- Documented Phase 3 Training Module table (`phase3_training_module`) with all fields
- Updated API endpoints to match actual implementation
- Updated implementation checklist with completion status (16/17 tasks complete)
- Added Export testing checklist
- Documented Gantt chart visualization with dynamic bar positioning
- All core features verified as implemented and working

**Key Changes in v3.2:**
- Updated all competency keys to match database `competency` table names
- Updated all strategy/archetype keys to match database `strategy_template` table names
- Added reference mapping tables (Competency ID → Key, Strategy ID → Key)
- Defined **Training Program Clusters** concept (6 umbrella clusters: Engineers, Managers, Executives, Support Staff, External Partners, Operations)
- Clarified distinction between 14 SE Role Clusters (for competency mapping) vs Training Program Clusters (for Phase 3 training organization)
- Added implementation note for Phase 1 Task 2 LLM prompt update

**Key Changes in v3.1:**
- Renamed Phase 3 to "Macro Planning"
- 3-task structure (Structure, Formats, Timeline)
- Timeline is LLM-generated (not user input)
- Timeline is informational only (not adjustable)
- Removed sessions count
- Clarified existing training check is in Phase 2
- Show only Milestones (not lifecycle phases)
