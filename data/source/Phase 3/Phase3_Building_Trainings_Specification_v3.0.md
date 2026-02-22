# Phase 3: Building Trainings - Implementation Specification v3.0

## Document Information
- **Module**: Phase 3 - Macro-planning of SE Training Initiative
- **Previous Name**: "Module Selection & Format Selection"
- **New Name**: "Building Trainings"
- **Based on**: Ulf Meeting (11-12-2025), Sachin Kumar Thesis (2023)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Version**: 3.0 (Complete Redesign)
- **Date**: December 2025

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial LF recommendation specification |
| 2.0 | Dec 2025 | Added aggregate view, distribution analysis, level constraints |
| 2.1 | Dec 2025 | Added Training Group Size, clarified Level 4 constraints |
| **3.0** | **Dec 2025** | **COMPLETE REDESIGN**: User-driven selection, 3 suitability factors, two training views, corrected matrices, timeline planning |

---

## Table of Contents

1. [Module Overview](#1-module-overview)
2. [Phase 3 Structure](#2-phase-3-structure)
3. [Task 1: Building Trainings](#3-task-1-building-trainings)
4. [Training Structure Views](#4-training-structure-views)
5. [Learning Format Selection](#5-learning-format-selection)
6. [The 3 Suitability Factors](#6-the-3-suitability-factors)
7. [Learning Format Master Data](#7-learning-format-master-data)
8. [Corrected Matrices](#8-corrected-matrices)
9. [User Count Scaling](#9-user-count-scaling)
10. [Task 2: Timeline Planning](#10-task-2-timeline-planning)
11. [UI/UX Design](#11-uiux-design)
12. [Data Models](#12-data-models)
13. [API Specification](#13-api-specification)
14. [Database Schema](#14-database-schema)
15. [Export Specification](#15-export-specification)
16. [Implementation Checklist](#16-implementation-checklist)

---

## 1. Module Overview

### 1.1 Purpose

Phase 3 "Building Trainings" helps organizations:
1. **Structure their training program** (by competency-level OR by role clusters)
2. **Select appropriate Learning Formats** for each training module
3. **Understand format suitability** through 3-factor feedback (not automatic recommendations)
4. **Plan high-level timeline** for training rollout

### 1.2 Key Design Principles (from Ulf - 11-12-2025)

| Principle | Description |
|-----------|-------------|
| **User-Driven Selection** | NO automatic recommendations. User selects format, we show suitability feedback |
| **Two Training Views** | Competency-Level Based OR Role-Clustered Based |
| **3-Factor Suitability** | Simple green/yellow/red feedback for each factor |
| **Modules Already Defined** | Modules come from Learning Objectives (Phase 2), not created here |
| **Overview, Not Automation** | "Give a good overview of options and provide the possibility to select" |

**Ulf's Key Quote**: *"NO RECOMMENDATION of learning format, but instead we provide the information to the user when they select format by themselves."*

### 1.3 Position in SE-QPT Workflow

```
Phase 1: Prepare SE Training
    ↓ Outputs: Maturity Level, Role Clusters, Qualification Archetype, 
               Target Group Size, Training Group Size
    
Phase 2: Determine Requirements & Competencies  
    ↓ Outputs: Competency Gaps per User per Level, Learning Objectives,
               Training Modules (defined via LOs)
    
Phase 3: Macro-planning of SE Training Initiative  ← THIS MODULE
    │
    ├── Task 3.1: Building Trainings
    │   ├── Choose training structure view
    │   ├── Select Learning Format per module
    │   └── View suitability feedback (3 factors)
    │
    └── Task 3.2: Timeline Planning
        ├── Define Concept Phase dates
        ├── Define Pilot Phase dates
        └── Define Run Phase dates
    
    ↓ Outputs: Selected Learning Formats, Training Structure, Timeline
    
Phase 4: Micro-planning of SE Training Initiative
    → Outputs: AVIVA Templates, Detailed Training Plans
```

### 1.4 What Changed from v2.x

| Aspect | v2.x (Previous) | v3.0 (Current) |
|--------|-----------------|----------------|
| **Approach** | Automatic scoring & ranking | User selection + suitability feedback |
| **View** | Aggregate per competency | Two views: Competency-Level OR Role-Clustered |
| **Factors** | 4-5 weighted factors with scores | 3 simple factors with 🟢🟡🔴 |
| **Output** | Primary recommendation + alternatives | All formats shown, user selects |
| **Matrices** | Sachin's C_Co-LF (invalid values) | New corrected matrices |
| **Strategy** | Not used for scoring | Factor 3: Strategy Consistency |
| **Distribution** | Complex pattern analysis | Simplified for user count scaling only |
| **Timeline** | Not included | Task 2: Timeline Planning |

---

## 2. Phase 3 Structure

### 2.1 Two Main Tasks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: MACRO-PLANNING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TASK 1: BUILDING TRAININGS                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Choose training structure (Competency-Level vs Role-Clustered)           │
│  • View training modules (from Phase 2 Learning Objectives)                 │
│  • Select Learning Format for each module                                   │
│  • View suitability feedback (3 factors: 🟢🟡🔴)                            │
│  • Learn more about formats (Sachin's posters)                              │
│                                                                              │
│  TASK 2: TIMELINE PLANNING                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Define Concept Phase (start/end dates)                                   │
│  • Define Pilot Phase (start date)                                          │
│  • Define Run Phase (first/last training dates)                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Prerequisites (from Phase 2)

Before entering Phase 3, the following must be completed:

| Prerequisite | Source | Data Needed |
|--------------|--------|-------------|
| Learning Objectives | Phase 2 | Competency, Level, PMT breakdown, Roles |
| Training Modules | Phase 2 | One module per competency-level (+ MT split if applicable) |
| Gap Data | Phase 2 | Users needing training per competency-level |
| Qualification Archetype | Phase 1 | Selected strategy for Factor 3 |
| Target Group Size | Phase 1 | For user count scaling |

### 2.3 Module Definition (Already Done)

**Ulf's Clarification**: *"Our modules are actually defined already in the Learning Objectives task. So we have one module for each competency level and also further we can separate between Method and Tool if possible or applicable."*

**Module Structure**:
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

---

## 3. Task 1: Building Trainings

### 3.1 Overview

Building Trainings is about **structuring how modules are grouped into trainings** and **selecting the appropriate Learning Format** for each.

### 3.2 Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Choose Training Structure                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│  User selects: Competency-Level Based  OR  Role (Clustered) Based           │
│  (For Low Maturity: Only Competency-Level Based available)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 2: View Training Modules                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Display all modules from Phase 2 organized by chosen structure             │
│  Show roles needing each module, estimated participant count                │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 3: Select Learning Format                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  User clicks on a module → sees 10 Learning Format options                  │
│  User selects a format → sees 3-factor suitability feedback                 │
│  User can click "Learn more" to see format details (poster)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 4: Confirm Selections                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Review all modules with selected formats                                   │
│  Proceed to Timeline Planning                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Training Structure Views

### 4.1 Competency-Level Based View

**Concept**: Training organized by competency + level. Multiple roles participate together.

**Example**:
```
Training: "Requirements Definition - Level 2 - Tool"
├── Roles: Requirements Engineer, Systems Architect, Project Manager
├── Estimated Participants: 45
└── Learning Format: [Select]

Training: "Requirements Definition - Level 2 - Method"
├── Roles: Requirements Engineer, Systems Architect
├── Estimated Participants: 38
└── Learning Format: [Select]

Training: "Systems Thinking - Level 2"
├── Roles: All Engineering Roles
├── Estimated Participants: 120
└── Learning Format: [Select]
```

**When to Use**:
- Want to focus on competency development
- Bring different roles together for shared learning
- Standardize training across organization

**Visual Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMPETENCY-LEVEL BASED TRAININGS                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Role 1, Role 2, Role 3                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  "Competency 1" Level 2 - Tool            [Select Format ▼]             ││
│  │  Estimated: 45 participants                                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Role 1, Role 3                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  "Competency 1" Level 2 - Method          [Select Format ▼]             ││
│  │  Estimated: 38 participants                                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Role 3                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  "Competency 2" Level 4 - Method          [Select Format ▼]             ││
│  │  Estimated: 12 participants                                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Role (Clustered) Based View

**Concept**: Training organized by role clusters. Each cluster gets a training program containing multiple competencies.

**Pre-requisite**: Define which roles belong to which cluster:
- **Engineers**: Requirements Engineer, Systems Architect, System Developer, etc.
- **Leaders/Managers**: Project Manager, SE Manager, Team Lead, etc.
- **Interfacing Partners**: Customer Representative, Supplier Manager, etc.

**Example**:
```
Training Program: "SE for Engineers"
├── Roles Included: Requirements Engineer, Systems Architect, System Developer
├── Contains:
│   ├── "Competency 1" Level 2 - Tool
│   ├── "Competency 1" Level 2 - Method
│   ├── "Competency 1" Level 1 - Tool
│   └── "Competency 1" Level 1 - Method
└── Learning Format: [Select per module or for whole program]

Training Program: "SE for Leaders" [STRATEGY]
├── Roles Included: Project Manager, SE Manager
├── Part of Strategy: "SE for Managers"
├── Contains:
│   ├── "Competency 1" Level 2 - Method
│   └── "Leadership" Level 4
└── Learning Format: [Select]
```

**When to Use**:
- Want role-specific training programs
- Different roles need different competency focuses
- Align with specific strategies (e.g., "SE for Managers")

**Visual Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ROLE (CLUSTERED) BASED TRAININGS                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📁 "SE for Engineers"                                                  ││
│  │  Roles: Requirements Engineer, Systems Architect, System Developer      ││
│  │  ────────────────────────────────────────────────────────────────────── ││
│  │  ┌───────────────────────────┐  ┌───────────────────────────┐          ││
│  │  │ Comp 1 L2 - Tool [Format]│  │ Comp 1 L2 - Method [Format]│          ││
│  │  └───────────────────────────┘  └───────────────────────────┘          ││
│  │  ┌───────────────────────────┐  ┌───────────────────────────┐          ││
│  │  │ Comp 1 L1 - Tool [Format]│  │ Comp 1 L1 - Method [Format]│          ││
│  │  └───────────────────────────┘  └───────────────────────────┘          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📁 "SE for Leaders" [STRATEGY: SE for Managers]                        ││
│  │  Roles: Project Manager, SE Manager                                     ││
│  │  ────────────────────────────────────────────────────────────────────── ││
│  │  ┌───────────────────────────┐  ┌───────────────────────────┐          ││
│  │  │ Comp 1 L2 - Method [Fmt] │  │ Leadership L4 [Format]    │          ││
│  │  └───────────────────────────┘  └───────────────────────────┘          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 View Selection Logic

```javascript
function determineAvailableViews(projectData) {
  const { maturityLevel, hasRolesDefined } = projectData;
  
  // Low maturity: Only Competency-Level view (no roles defined)
  if (maturityLevel <= 2 || !hasRolesDefined) {
    return {
      availableViews: ['competency_level'],
      defaultView: 'competency_level',
      showViewSelector: false
    };
  }
  
  // High maturity: Both views available
  return {
    availableViews: ['competency_level', 'role_clustered'],
    defaultView: 'competency_level',
    showViewSelector: true
  };
}
```

### 4.4 Role Clustering Definition

For Role-Clustered view, roles must be grouped into clusters:

```javascript
const DEFAULT_ROLE_CLUSTERS = {
  engineers: {
    name: "Engineers",
    trainingProgramName: "SE for Engineers",
    roles: [
      "Requirements Engineer",
      "Systems Architect", 
      "System Developer",
      "V&V Operator",
      "Integration Manager"
    ]
  },
  leaders: {
    name: "Leaders/Managers",
    trainingProgramName: "SE for Leaders",
    linkedStrategy: "se_for_leaders",  // Links to archetype
    roles: [
      "Project Manager",
      "SE Manager",
      "Team Lead",
      "Department Head"
    ]
  },
  interfacing_partners: {
    name: "Interfacing Partners",
    trainingProgramName: "SE for Interfacing Partners",
    roles: [
      "Customer Representative",
      "Supplier Manager",
      "External Stakeholder"
    ]
  }
};
```

---

## 5. Learning Format Selection

### 5.1 Selection Flow

**Ulf's Direction**: *"We provide the list of formats with their benefits and they can select by themselves. But we also do format recommendations based on some input aspects... it's just like using the information to show which one can should be selected and giving the user feedback on their selection."*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  User clicks on a training module                                           │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  SELECT LEARNING FORMAT                                                 ││
│  │  ─────────────────────────────────────────────────────────────────────  ││
│  │                                                                          ││
│  │  [Seminar] [Webinar] [Coaching] [Mentoring] [WBT]                       ││
│  │  [CBT] [Game-Based] [Conference] [Blended] [Self-Learning]             ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              ↓                                              │
│  User selects a format (e.g., "Seminar")                                   │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  SUITABILITY FEEDBACK                                                   ││
│  │  ─────────────────────────────────────────────────────────────────────  ││
│  │                                                                          ││
│  │  Factor 1: Participants (45)           🟢 Suitable                      ││
│  │  → Seminar works well for 10-100 participants                           ││
│  │                                                                          ││
│  │  Factor 2: Level Achievable            🟢 Level 4 achievable            ││
│  │  → Seminar can achieve up to Level 4 for this competency                ││
│  │                                                                          ││
│  │  Factor 3: Strategy Consistency        🟡 Partly Recommended            ││
│  │  → Seminar works with "Need-Based Training" but consider Blended        ││
│  │                                                                          ││
│  │  [Learn more about Seminar]  [Confirm Selection]                        ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 The 10 Learning Formats

| # | ID | Name | Max Level |
|---|-----|------|-----------|
| 1 | `seminar` | Seminar/Instructor Lead Training | Level 4 |
| 2 | `webinar` | Webinar/Live Online Event | Level 2 |
| 3 | `coaching` | Coaching | Level 6 |
| 4 | `mentoring` | Mentoring | Level 6 |
| 5 | `wbt` | Web-Based Training (WBT) | Level 2 |
| 6 | `cbt` | Computer-Based Training (CBT) | Level 2 |
| 7 | `game_based` | Game-Based Learning | Level 4 |
| 8 | `conference` | Conference | Level 1 |
| 9 | `blended` | Blended Learning | Level 6 |
| 10 | `self_learning` | Self-Learning | Level 2 |

### 5.3 "Learn More" - Format Details

When user clicks "Learn more about [Format]", show Sachin's poster information:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEMINAR / INSTRUCTOR LEAD TRAINING                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DESCRIPTION                                                                 │
│  Face-to-face, in-person training led by trainer(s) with direct            │
│  interaction. Uses slideshows, videos, storytelling, and lectures.          │
│                                                                              │
│  CHARACTERISTICS                                                             │
│  ┌──────────────────┬─────────────────┬──────────────────┐                  │
│  │ Mode: Offline    │ Comm: Sync      │ Collab: Group    │                  │
│  │ Participants:    │ Learning Type:  │ Max Level:       │                  │
│  │ 10-100           │ Formal          │ Apply (L4)       │                  │
│  └──────────────────┴─────────────────┴──────────────────┘                  │
│                                                                              │
│  EFFORT (1-5 scale)                                                         │
│  Content Creation: ████░ (4)                                                │
│  Content Updation: ████░ (4)                                                │
│  Per Training:     ████░ (4)                                                │
│                                                                              │
│  ✅ ADVANTAGES                                                               │
│  • Direct Feedback - Interact with trainer, clear doubts                    │
│  • Standardized Content - Consistent delivery                               │
│  • High Interaction - Group discussions, roleplay                           │
│                                                                              │
│  ❌ DISADVANTAGES                                                            │
│  • Limited Accessibility - Face-to-face only                                │
│  • No Self-Paced - Fixed schedule                                           │
│  • Travel Expenses - Transportation, accommodation                          │
│                                                                              │
│  SUITABLE FOR STRATEGIES                                                     │
│  ✓ Common Basic Understanding                                               │
│  ✓ SE for Leaders                                                           │
│  ✓ Make Pilot Project                                                       │
│  ✓ Need-Based Training                                                      │
│                                                                              │
│  LEARNING METHODS                                                            │
│  Presentations, Videos, Case Studies, Discussions, Group Work,              │
│  Quizzes, Storytelling, Lectures                                            │
│                                                                              │
│                                              [Close]                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. The 3 Suitability Factors

### 6.1 Overview

| Factor | Question | Data Source | Output |
|--------|----------|-------------|--------|
| **Factor 1** | Does format suit the participant count? | Scaled user count | 🟢🟡🔴 |
| **Factor 2** | Can format achieve the required level? | Competency-Level Matrix | 🟢🟡🔴 |
| **Factor 3** | Is format consistent with strategy? | Strategy-LF Matrix | 🟢🟡🔴 |

### 6.2 Factor 1: Participant Count Suitability

**Question**: Does the selected format suit the number of participants?

**Logic**:
```javascript
function checkParticipantSuitability(formatId, participantCount) {
  const format = LEARNING_FORMATS[formatId];
  const { min, max } = format.participantRange;
  
  // Perfect fit
  if (participantCount >= min && participantCount <= max) {
    return {
      status: 'green',
      message: `Suitable for ${participantCount} participants`,
      detail: `${format.name} works well for groups of ${min}-${max}`
    };
  }
  
  // Slightly outside range (within 20%)
  const tolerance = 0.2;
  if (participantCount >= min * (1 - tolerance) && 
      participantCount <= max * (1 + tolerance)) {
    return {
      status: 'yellow',
      message: `Manageable but not ideal`,
      detail: `${format.name} is designed for ${min}-${max} participants. Consider splitting into multiple sessions.`
    };
  }
  
  // Far outside range
  return {
    status: 'red',
    message: `Not suitable for ${participantCount} participants`,
    detail: `${format.name} works best for ${min}-${max}. Consider a different format.`
  };
}
```

**Participant Ranges per Format**:

| Format | Min | Max | Best For |
|--------|-----|-----|----------|
| Seminar | 10 | 100 | Medium groups |
| Webinar | 1 | unlimited | Large scale |
| Coaching | 1 | 5 | Individual/small |
| Mentoring | 1 | 3 | Pairs |
| WBT | 1 | unlimited | Any size |
| CBT | 1 | unlimited | Any size |
| Game-Based | 5 | 20 | Small-medium |
| Conference | 50 | unlimited | Large gatherings |
| Blended | 5 | 50 | Medium groups |
| Self-Learning | 1 | 1 | Individual |

### 6.3 Factor 2: Competency-Level Achievable

**Question**: Can the selected format achieve the required competency level?

**Logic**:
```javascript
function checkLevelAchievable(competencyId, targetLevel, formatId) {
  const achievableLevel = COMPETENCY_LEVEL_MATRIX[competencyId][formatId];
  
  // Can achieve target or higher
  if (achievableLevel >= targetLevel) {
    return {
      status: 'green',
      message: `Can achieve Level ${targetLevel}`,
      detail: `${formatName} can help achieve up to Level ${achievableLevel} for ${competencyName}`
    };
  }
  
  // Can achieve one level below (e.g., target L4, can do L2)
  if (achievableLevel >= targetLevel - 2 && achievableLevel > 0) {
    return {
      status: 'yellow',
      message: `Can only achieve Level ${achievableLevel}`,
      detail: `${formatName} can achieve Level ${achievableLevel}, but target is Level ${targetLevel}. Consider combining with another format.`
    };
  }
  
  // Cannot achieve
  return {
    status: 'red',
    message: `Cannot achieve Level ${targetLevel}`,
    detail: `${formatName} can only achieve Level ${achievableLevel} for ${competencyName}. Choose a different format.`
  };
}
```

### 6.4 Factor 3: Strategy Consistency

**Question**: Is the selected format consistent with the chosen Qualification Archetype/Strategy?

**Logic**:
```javascript
function checkStrategyConsistency(archetypeId, formatId) {
  const consistency = STRATEGY_LF_MATRIX[archetypeId][formatId];
  
  switch (consistency) {
    case '++':
      return {
        status: 'green',
        message: 'Highly recommended',
        detail: `${formatName} is highly recommended for "${archetypeName}" strategy`
      };
    case '+':
      return {
        status: 'yellow',
        message: 'Partly recommended',
        detail: `${formatName} can work with "${archetypeName}" but consider alternatives for better alignment`
      };
    case '-':
      return {
        status: 'red',
        message: 'Not consistent',
        detail: `${formatName} may conflict with "${archetypeName}" strategy goals. Consider a different approach.`
      };
  }
}
```

### 6.5 Combined Suitability Display

```javascript
function evaluateFormatSuitability(moduleData, formatId, projectContext) {
  const factor1 = checkParticipantSuitability(formatId, moduleData.estimatedParticipants);
  const factor2 = checkLevelAchievable(moduleData.competencyId, moduleData.targetLevel, formatId);
  const factor3 = checkStrategyConsistency(projectContext.archetypeId, formatId);
  
  return {
    format: formatId,
    factors: [factor1, factor2, factor3],
    overallSuitability: calculateOverall(factor1, factor2, factor3),
    canProceed: !hasRedFactors([factor1, factor2, factor3])
  };
}

function calculateOverall(f1, f2, f3) {
  const statuses = [f1.status, f2.status, f3.status];
  
  if (statuses.includes('red')) return 'caution';
  if (statuses.filter(s => s === 'yellow').length >= 2) return 'review';
  if (statuses.every(s => s === 'green')) return 'excellent';
  return 'good';
}
```

---

## 7. Learning Format Master Data

### 7.1 Complete Format Definitions

```javascript
const LEARNING_FORMATS = {
  seminar: {
    id: "seminar",
    name: "Seminar / Instructor Lead Training",
    description: "Face-to-face, in-person training led by trainer(s) with direct interaction. Uses slideshows, videos, storytelling, and lectures customized for target audience.",
    
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 10, max: 100, category: "medium" },
      learningType: "formal"
    },
    
    efforts: {
      contentCreation: 4,
      contentUpdation: 4,
      perTraining: 4
    },
    
    competencyAcquisition: {
      maxLevel: "Apply",
      levelValue: 4
    },
    
    advantages: [
      { id: "direct_feedback", name: "Direct Feedback", description: "Interact with trainer to discuss topics and clear doubts" },
      { id: "standardized_content", name: "Standardized Content", description: "Learning material is standardized and tested" },
      { id: "high_interaction", name: "High Interaction", description: "Group discussions and roleplay possible" }
    ],
    
    disadvantages: [
      { id: "limited_accessibility", name: "Limited Accessibility", description: "Face-to-face only, not for remote learners" },
      { id: "no_self_paced", name: "No Self-Paced", description: "Fixed schedule and timeline" },
      { id: "travel_expenses", name: "Travel Expenses", description: "Transportation and accommodation costs" }
    ],
    
    suitableArchetypes: ["common_basic_understanding", "se_for_leaders", "make_pilot_project", "need_based_training"],
    
    learningMethods: ["presentations", "videos", "case_studies", "discussions", "group_work", "quizzes", "storytelling", "lectures"]
  },
  
  webinar: {
    id: "webinar",
    name: "Webinar / Live Online Event",
    description: "Online live broadcast at specific time. Interaction via chat, sometimes audio. Synchronous, typically 30-90 minutes, unlimited global reach.",
    
    characteristics: {
      modeOfDelivery: "online",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 1, max: Infinity, category: "large" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 3 },
    competencyAcquisition: { maxLevel: "Understand", levelValue: 2 },
    
    advantages: [
      { id: "direct_feedback", name: "Direct Feedback", description: "Can engage with trainer via chat or unmuting" },
      { id: "global_reach", name: "Global Reach", description: "No geographical limits" },
      { id: "standardized_content", name: "Standardized Content", description: "Consistent delivery" }
    ],
    
    disadvantages: [
      { id: "limited_instructors", name: "Limited Instructors", description: "Finding qualified trainers challenging" },
      { id: "low_interaction", name: "Low Interaction", description: "Limited engagement compared to in-person" },
      { id: "no_self_paced", name: "No Self-Paced", description: "Fixed schedule" }
    ],
    
    suitableArchetypes: ["common_basic_understanding", "se_for_leaders", "continuous_support"],
    learningMethods: ["presentations", "screen_sharing", "polls", "chat", "q_and_a", "breakout_rooms"]
  },
  
  coaching: {
    id: "coaching",
    name: "Coaching",
    description: "Attentive observation of learner with expert assistance. Support fades as competence grows. Individual, team, or organizational level.",
    
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 5, category: "individual" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 5 },
    competencyAcquisition: { maxLevel: "Mastery", levelValue: 6 },
    
    advantages: [
      { id: "accountability", name: "Accountability", description: "Coach holds individual accountable" },
      { id: "personalized_guidance", name: "Personalized Guidance", description: "One-on-one tailored support" },
      { id: "self_discovery", name: "Self-Discovery", description: "Deep understanding of strengths and weaknesses" }
    ],
    
    disadvantages: [
      { id: "gradual_results", name: "Gradual Results", description: "Takes time, not immediate solutions" },
      { id: "time_intensive", name: "Time Intensive", description: "Significant commitment from both parties" },
      { id: "limited_instructors", name: "Limited Instructors", description: "Qualified coaches scarce" }
    ],
    
    suitableArchetypes: ["se_for_leaders", "make_pilot_project", "need_based_training", "train_the_trainer"],
    learningMethods: ["one_on_one_sessions", "observation", "feedback", "goal_setting", "action_plans"]
  },
  
  mentoring: {
    id: "mentoring",
    name: "Mentoring",
    description: "Knowledge acquisition through work-related tasks under experienced colleague guidance. Mentor serves as role model. Immediate feedback.",
    
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 3, category: "pairs" },
      learningType: "informal"
    },
    
    efforts: { contentCreation: 2, contentUpdation: 1, perTraining: 4 },
    competencyAcquisition: { maxLevel: "Mastery", levelValue: 6 },
    
    advantages: [
      { id: "successor_training", name: "Successor Training", description: "Prepares future leaders" },
      { id: "personalized_content", name: "Personalized Content", description: "Adapts to individual learner" },
      { id: "self_discovery", name: "Self-Discovery", description: "Self-reflection and growth" }
    ],
    
    disadvantages: [
      { id: "time_intensive", name: "Time Intensive", description: "Significant mentor time" },
      { id: "gradual_results", name: "Gradual Results", description: "Takes time to see results" },
      { id: "limited_mentors", name: "Limited Mentors", description: "Finding qualified mentors challenging" }
    ],
    
    suitableArchetypes: ["make_pilot_project", "need_based_training", "train_the_trainer"],
    learningMethods: ["shadowing", "on_the_job_learning", "regular_meetings", "knowledge_transfer"]
  },
  
  wbt: {
    id: "wbt",
    name: "Web-Based Training (WBT)",
    description: "Computer-aided multimedia training via internet. Self-paced, anytime access. Content easily updated. Can be individually tailored.",
    
    characteristics: {
      modeOfDelivery: "online",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: Infinity, category: "unlimited" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 5, contentUpdation: 2, perTraining: 1 },
    competencyAcquisition: { maxLevel: "Understand", levelValue: 2 },
    
    advantages: [
      { id: "tracking_assessment", name: "Tracking & Assessment", description: "Monitor learner progress" },
      { id: "self_paced", name: "Self-Paced", description: "Learn at own speed" },
      { id: "global_reach", name: "Global Reach", description: "Accessible worldwide" }
    ],
    
    disadvantages: [
      { id: "low_engagement", name: "Low Engagement", description: "May lack interactive elements" },
      { id: "very_low_interaction", name: "Very Low Interaction", description: "Shallow instructor interaction" },
      { id: "limited_instructor_guidance", name: "Limited Guidance", description: "No immediate support" }
    ],
    
    suitableArchetypes: ["need_based_training", "continuous_support", "train_the_trainer"],
    learningMethods: ["video_lessons", "interactive_modules", "quizzes", "progress_tracking", "downloadable_resources"]
  },
  
  cbt: {
    id: "cbt",
    name: "Computer-Based Training (CBT)",
    description: "Computer-assisted multimedia learning. Software installed on computer, no internet required. Flexible, self-paced offline learning.",
    
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: Infinity, category: "unlimited" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 5, contentUpdation: 3, perTraining: 1 },
    competencyAcquisition: { maxLevel: "Understand", levelValue: 2 },
    
    advantages: [
      { id: "tracking_assessment", name: "Tracking & Assessment", description: "Monitor progress locally" },
      { id: "self_paced", name: "Self-Paced", description: "Flexible timing" },
      { id: "no_internet", name: "No Internet Required", description: "Works offline" }
    ],
    
    disadvantages: [
      { id: "low_engagement", name: "Low Engagement", description: "Limited interactivity" },
      { id: "very_low_interaction", name: "Very Low Interaction", description: "No instructor access" },
      { id: "technical_issues", name: "Technical Issues", description: "Installation/compatibility problems" }
    ],
    
    suitableArchetypes: ["need_based_training", "continuous_support"],
    learningMethods: ["software_simulations", "tutorials", "exercises", "assessments", "offline_modules"]
  },
  
  game_based: {
    id: "game_based",
    name: "Game-Based Learning",
    description: "Learning through gamification, serious games, simulations. Highly engaging, safe practice environment for learning from mistakes.",
    
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 5, max: 20, category: "small_medium" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 3 },
    competencyAcquisition: { maxLevel: "Apply", levelValue: 4 },
    
    advantages: [
      { id: "high_engagement", name: "High Engagement", description: "Fun, motivating experience" },
      { id: "measurable_outcomes", name: "Measurable Outcomes", description: "Clear performance metrics" },
      { id: "safe_practice", name: "Safe Practice", description: "Learn from mistakes safely" }
    ],
    
    disadvantages: [
      { id: "high_dev_cost", name: "High Development Cost", description: "Expensive to create" },
      { id: "technical_requirements", name: "Technical Requirements", description: "May need special hardware" },
      { id: "not_scalable", name: "Limited Scalability", description: "Best for smaller groups" }
    ],
    
    suitableArchetypes: ["common_basic_understanding", "se_for_leaders", "make_pilot_project"],
    learningMethods: ["simulations", "role_playing", "competitions", "scenarios", "team_challenges"]
  },
  
  conference: {
    id: "conference",
    name: "Conference",
    description: "Structured professional gatherings. Presentations, networking, knowledge exchange. Exposure to new ideas and industry trends.",
    
    characteristics: {
      modeOfDelivery: "offline",
      communicationType: "synchronous",
      collaborationType: "group",
      participantRange: { min: 50, max: Infinity, category: "large" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 2, contentUpdation: 2, perTraining: 3 },
    competencyAcquisition: { maxLevel: "Recognize", levelValue: 1 },
    
    advantages: [
      { id: "new_ideas", name: "New Ideas", description: "Latest trends and innovations" },
      { id: "networking", name: "Networking", description: "Build industry connections" },
      { id: "inspiration", name: "Inspiration", description: "Keynotes and success stories" }
    ],
    
    disadvantages: [
      { id: "passive_learning", name: "Passive Learning", description: "Primarily listening" },
      { id: "time_consuming", name: "Time-Consuming", description: "Multi-day events" },
      { id: "travel_expenses", name: "Travel Expenses", description: "Registration, travel, accommodation" }
    ],
    
    suitableArchetypes: ["common_basic_understanding", "continuous_support"],
    learningMethods: ["keynotes", "presentations", "panel_discussions", "networking", "workshops"]
  },
  
  blended: {
    id: "blended",
    name: "Blended Learning",
    description: "Combines synchronous/asynchronous, in-person/online. Best of both worlds. Can cover multiple competency levels in one program.",
    
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "hybrid",
      collaborationType: "group",
      participantRange: { min: 5, max: 50, category: "flexible" },
      learningType: "formal"
    },
    
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 4 },
    competencyAcquisition: { maxLevel: "Mastery", levelValue: 6 },
    
    advantages: [
      { id: "best_of_both", name: "Best of Both", description: "Self-paced + interactive sessions" },
      { id: "flexible", name: "Flexible", description: "Accommodates different schedules" },
      { id: "multi_level", name: "Multi-Level Coverage", description: "Covers L1, L2, L4 in one program" }
    ],
    
    disadvantages: [
      { id: "complex_planning", name: "Complex Planning", description: "Hard to coordinate modalities" },
      { id: "integration_challenges", name: "Integration Challenges", description: "LMS complexity" },
      { id: "resource_intensive", name: "Resource Intensive", description: "Needs platform and physical space" }
    ],
    
    suitableArchetypes: ["common_basic_understanding", "se_for_leaders", "make_pilot_project", "need_based_training", "train_the_trainer"],
    learningMethods: ["online_modules", "face_to_face_sessions", "virtual_classrooms", "discussion_forums", "project_work"]
  },
  
  self_learning: {
    id: "self_learning",
    name: "Self-Learning",
    description: "Independent, self-directed knowledge acquisition. Reading, online courses, experimentation. Complete control but requires self-discipline.",
    
    characteristics: {
      modeOfDelivery: "hybrid",
      communicationType: "asynchronous",
      collaborationType: "individual",
      participantRange: { min: 1, max: 1, category: "individual" },
      learningType: "informal"
    },
    
    efforts: { contentCreation: 1, contentUpdation: 1, perTraining: 1 },
    competencyAcquisition: { maxLevel: "Understand", levelValue: 2 },
    
    advantages: [
      { id: "flexibility", name: "Complete Flexibility", description: "Total schedule control" },
      { id: "low_cost", name: "Low Cost", description: "Minimal investment" },
      { id: "self_directed", name: "Self-Directed", description: "Learn what you want" }
    ],
    
    disadvantages: [
      { id: "no_structure", name: "No Structure", description: "Easy to lose focus" },
      { id: "requires_motivation", name: "Requires Motivation", description: "Self-discipline essential" },
      { id: "no_feedback", name: "No Feedback", description: "No expert guidance" }
    ],
    
    suitableArchetypes: ["continuous_support", "need_based_training"],
    learningMethods: ["reading", "online_research", "practice_projects", "experimentation", "video_tutorials"]
  }
};
```

---

## 8. Corrected Matrices

### 8.1 Competency-Level Achievable Matrix

**Purpose**: Shows which competency LEVEL (0, 1, 2, 4, 6) can be achieved for each competency with each format.

**Key Principles**:
1. E-Learning (WBT, CBT, Self-Learning): Max Level 2
2. Passive Formats (Conference): Max Level 1
3. Coaching & Mentoring: Can reach Level 6 for some competencies
4. Core Competencies: Harder to achieve (experience-based)
5. Blended: Highest potential

```javascript
const COMPETENCY_LEVEL_MATRIX = {
  // CORE COMPETENCIES (harder to achieve, experience-based)
  systems_thinking:          { seminar: 2, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  lifecycle_consideration:   { seminar: 2, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  customer_value_orientation:{ seminar: 2, webinar: 2, coaching: 4, mentoring: 6, wbt: 2, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 1 },
  system_modeling_analysis:  { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 1, blended: 6, self_learning: 2 },
  
  // SOCIAL/PERSONAL COMPETENCIES
  communication:             { seminar: 4, webinar: 2, coaching: 6, mentoring: 4, wbt: 2, cbt: 1, game_based: 4, conference: 2, blended: 4, self_learning: 1 },
  leadership:                { seminar: 2, webinar: 2, coaching: 6, mentoring: 6, wbt: 2, cbt: 1, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  self_organisation:         { seminar: 2, webinar: 1, coaching: 4, mentoring: 4, wbt: 1, cbt: 1, game_based: 2, conference: 1, blended: 4, self_learning: 2 },
  
  // MANAGEMENT COMPETENCIES
  project_management:        { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  decision_management:       { seminar: 4, webinar: 2, coaching: 6, mentoring: 6, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  information_management:    { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 2, conference: 1, blended: 4, self_learning: 2 },
  configuration_management:  { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  
  // TECHNICAL COMPETENCIES
  requirements_definition:   { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  system_architecting:       { seminar: 4, webinar: 2, coaching: 4, mentoring: 6, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  ivv:                       { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 },
  operation_and_support:     { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 2, conference: 2, blended: 4, self_learning: 2 },
  
  // AGILE
  agile_methods:             { seminar: 4, webinar: 2, coaching: 4, mentoring: 4, wbt: 2, cbt: 2, game_based: 4, conference: 2, blended: 6, self_learning: 2 }
};
```

**Value Legend**:
- `0` = Not suitable for this competency
- `1` = Can achieve Level 1 (Knowing/Recognize)
- `2` = Can achieve Level 2 (Understanding)
- `4` = Can achieve Level 4 (Applying)
- `6` = Can achieve Level 6 (Mastery)

### 8.2 Strategy-Learning Format Consistency Matrix

**Purpose**: Shows which formats are consistent with each Qualification Archetype.

```javascript
const STRATEGY_LF_MATRIX = {
  common_basic_understanding: { seminar: '++', webinar: '+',  coaching: '-',  mentoring: '-',  wbt: '-',  cbt: '-',  game_based: '+',  conference: '+',  blended: '++', self_learning: '-'  },
  se_for_leaders:             { seminar: '++', webinar: '+',  coaching: '++', mentoring: '++', wbt: '+',  cbt: '-',  game_based: '+',  conference: '+',  blended: '++', self_learning: '-'  },
  make_pilot_project:         { seminar: '++', webinar: '+',  coaching: '++', mentoring: '++', wbt: '-',  cbt: '-',  game_based: '++', conference: '-',  blended: '++', self_learning: '-'  },
  need_based_training:        { seminar: '++', webinar: '+',  coaching: '+',  mentoring: '+',  wbt: '+',  cbt: '+',  game_based: '+',  conference: '-',  blended: '++', self_learning: '+'  },
  train_the_trainer:          { seminar: '+',  webinar: '+',  coaching: '++', mentoring: '++', wbt: '+',  cbt: '+',  game_based: '+',  conference: '-',  blended: '+',  self_learning: '+'  },
  continuous_support:         { seminar: '+',  webinar: '++', coaching: '+',  mentoring: '+',  wbt: '++', cbt: '++', game_based: '+',  conference: '++', blended: '+',  self_learning: '++' },
  certification:              { seminar: '+',  webinar: '+',  coaching: '+',  mentoring: '+',  wbt: '+',  cbt: '+',  game_based: '-',  conference: '+',  blended: '+',  self_learning: '+'  }
};
```

**Value Legend**:
- `++` = Highly Recommended (🟢)
- `+` = Partly Recommended (🟡)
- `-` = Not Consistent (🔴)

---

## 9. User Count Scaling

### 9.1 The Problem

**Ulf's Observation**: *"If we say the target group size for training in Phase 1 is 100-500, then every employee in the company needs to use our app and do the competency assessment to get the real gap data. But in reality, max 10 to 20 users will use the app."*

### 9.2 Scaling Logic

```javascript
function scaleUserCounts(gapData, projectContext) {
  const { targetGroupSize } = projectContext;  // From Phase 1
  const actualAssessedUsers = gapData.totalAssessedUsers;
  
  // Calculate scaling factor
  const scalingFactor = targetGroupSize / actualAssessedUsers;
  
  // Scale gap counts
  return gapData.modules.map(module => {
    const scaledUsersWithGap = Math.round(module.usersWithGap * scalingFactor);
    
    return {
      ...module,
      actualUsersWithGap: module.usersWithGap,
      estimatedParticipants: scaledUsersWithGap,
      scalingApplied: true,
      scalingFactor: scalingFactor
    };
  });
}
```

### 9.3 Display to User

**Ulf's Requirement**: *"We should do this so that the user is aware that these are Estimations of user counts that we've scaled up."*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ℹ️ USER COUNT ESTIMATION                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  For training planning, we have scaled the competency assessment data:      │
│                                                                              │
│  • Assessed users: 15                                                        │
│  • Target group size (Phase 1): 200                                          │
│  • Scaling factor: 13.3x                                                     │
│                                                                              │
│  Estimated participant counts are based on this scaling.                     │
│  This provides better input for Learning Format decisions.                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Task 2: Timeline Planning

### 10.1 Overview

**Ulf's Requirement**: *"Defining the timeline itself would be actually part of macro planning. When shall the concept be developed, When shall the first training be performed, When shall the last training be performed."*

### 10.2 Timeline Phases

| Phase | Description | User Input |
|-------|-------------|------------|
| **Concept Phase** | Detailed planning of training content and materials | Start Date, End Date |
| **Pilot Phase** | Run training with small test group for validation | Start Date |
| **Run Phase** | Full rollout of training program | First Training Date, Last Training Date |

### 10.3 UI Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIMELINE PLANNING                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONCEPT PHASE                                                               │
│  Define training content and materials                                       │
│  ├── Start Date: [📅 2026-01-15]                                            │
│  └── End Date:   [📅 2026-03-31]                                            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PILOT PHASE                                                                 │
│  Test training with small group                                             │
│  └── Start Date: [📅 2026-04-01]                                            │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  RUN PHASE (Full Rollout)                                                    │
│  Execute all planned trainings                                              │
│  ├── First Training: [📅 2026-05-01]                                        │
│  └── Last Training:  [📅 2026-12-15]                                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SUMMARY                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec             ││
│  │ [===CONCEPT===][PIL][=============RUN PHASE===============]            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Planned training sessions: [12]                                             │
│                                                                              │
│                                              [Save Timeline]                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. UI/UX Design

### 11.1 Phase 3 Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: MACRO-PLANNING - BUILDING TRAININGS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Progress: ████████░░░░░░░░░░░░ 40%                                         │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │                                 │  │                                 │   │
│  │  📋 TASK 1                      │  │  📅 TASK 2                      │   │
│  │  Building Trainings             │  │  Timeline Planning              │   │
│  │                                 │  │                                 │   │
│  │  Status: In Progress            │  │  Status: Not Started            │   │
│  │  Modules: 12 / 18 configured    │  │                                 │   │
│  │                                 │  │                                 │   │
│  │  [Continue →]                   │  │  [Start →]                      │   │
│  │                                 │  │                                 │   │
│  └─────────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SUMMARY                                                                     │
│  • Training Modules: 18                                                      │
│  • Estimated Total Participants: 847 (scaled from 63 assessed)              │
│  • Selected Archetype: Need-Based Project Oriented Training                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Task 1: Building Trainings Page

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BUILDING TRAININGS                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  How do you want to structure your trainings?                               │
│                                                                              │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐     │
│  │                                │  │                                │     │
│  │  📊 COMPETENCY-LEVEL BASED    │  │  👥 ROLE (CLUSTERED) BASED     │     │
│  │  ─────────────────────────────│  │  ─────────────────────────────│     │
│  │  Focus on competency and      │  │  Focus on roles and their     │     │
│  │  bring all roles together     │  │  specific competency needs    │     │
│  │                                │  │                                │     │
│  │  Example: "Req Def L2 - Tool" │  │  Example: "SE for Engineers"  │     │
│  │  with multiple roles          │  │  with multiple competencies   │     │
│  │                                │  │                                │     │
│  │       [Select ●]               │  │       [Select ○]               │     │
│  │                                │  │                                │     │
│  └────────────────────────────────┘  └────────────────────────────────┘     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TRAINING MODULES                                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Req. Engineer, Sys. Architect, PM                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Requirements Definition - Level 2 - Tool                               ││
│  │  Estimated participants: 45                                             ││
│  │                                                                          ││
│  │  Learning Format: [Seminar ▼]                                           ││
│  │                                                                          ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ SUITABILITY                                                         │││
│  │  │ Factor 1: Participants    🟢 Suitable (45 within 10-100 range)      │││
│  │  │ Factor 2: Level Achievable 🟢 Level 4 achievable                     │││
│  │  │ Factor 3: Strategy        🟢 Highly Recommended                      │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  │  [Learn more about Seminar]                            [✓ Confirmed]    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Req. Engineer, Sys. Architect                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Requirements Definition - Level 2 - Method                             ││
│  │  Estimated participants: 38                                             ││
│  │                                                                          ││
│  │  Learning Format: [Select Format ▼]                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ... (more modules)                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.3 Format Selection Dropdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SELECT LEARNING FORMAT                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐  Max Level: 4                                  │
│  │ ○ Seminar               │  ← Hover: "Face-to-face training, 10-100"      │
│  │ ○ Webinar               │  Max Level: 2                                  │
│  │ ○ Coaching              │  Max Level: 6                                  │
│  │ ○ Mentoring             │  Max Level: 6                                  │
│  │ ○ WBT                   │  Max Level: 2  ⚠️ E-Learning                   │
│  │ ○ CBT                   │  Max Level: 2  ⚠️ E-Learning                   │
│  │ ○ Game-Based            │  Max Level: 4                                  │
│  │ ○ Conference            │  Max Level: 1  ⚠️ Passive                      │
│  │ ○ Blended               │  Max Level: 6  ⭐ Recommended                  │
│  │ ○ Self-Learning         │  Max Level: 2                                  │
│  └─────────────────────────┘                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Data Models

### 12.1 Training Module (from Phase 2)

```typescript
interface TrainingModule {
  id: string;
  competencyId: string;
  competencyName: string;
  targetLevel: 1 | 2 | 4;
  pmtType: 'process' | 'method' | 'tool' | 'combined';
  
  // From Phase 2 Learning Objectives
  learningObjectives: LearningObjective[];
  
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

### 12.2 Format Suitability Result

```typescript
interface FormatSuitability {
  formatId: string;
  formatName: string;
  
  factors: {
    participants: {
      status: 'green' | 'yellow' | 'red';
      message: string;
      detail: string;
    };
    levelAchievable: {
      status: 'green' | 'yellow' | 'red';
      message: string;
      detail: string;
      achievableLevel: number;
      targetLevel: number;
    };
    strategyConsistency: {
      status: 'green' | 'yellow' | 'red';
      message: string;
      detail: string;
    };
  };
  
  overallSuitability: 'excellent' | 'good' | 'review' | 'caution';
}
```

### 12.3 Timeline Data

```typescript
interface TrainingTimeline {
  projectId: string;
  
  conceptPhase: {
    startDate: Date;
    endDate: Date;
  };
  
  pilotPhase: {
    startDate: Date;
  };
  
  runPhase: {
    firstTrainingDate: Date;
    lastTrainingDate: Date;
    plannedSessions: number;
  };
}
```

### 12.4 Phase 3 Output

```typescript
interface Phase3Output {
  projectId: string;
  
  // Training structure
  selectedView: 'competency_level' | 'role_clustered';
  
  // All modules with selections
  trainingModules: TrainingModule[];
  
  // Scaling info
  scalingInfo: {
    actualAssessedUsers: number;
    targetGroupSize: number;
    scalingFactor: number;
  };
  
  // Timeline
  timeline: TrainingTimeline;
  
  // Summary stats
  summary: {
    totalModules: number;
    configuredModules: number;
    totalEstimatedParticipants: number;
    formatDistribution: Record<string, number>;
  };
}
```

---

## 13. API Specification

### 13.1 Endpoints

```
# Get training modules (from Phase 2)
GET /api/phase3/training-modules/:projectId
Response: TrainingModule[]

# Get all learning formats with details
GET /api/phase3/learning-formats
Response: LearningFormat[]

# Evaluate format suitability for a module
POST /api/phase3/evaluate-format
Body: { projectId, moduleId, formatId }
Response: FormatSuitability

# Save format selection for a module
POST /api/phase3/select-format
Body: { projectId, moduleId, formatId, confirmed }
Response: { success: boolean }

# Get/Update timeline
GET /api/phase3/timeline/:projectId
Response: TrainingTimeline

PUT /api/phase3/timeline/:projectId
Body: TrainingTimeline
Response: { success: boolean }

# Get complete Phase 3 output
GET /api/phase3/output/:projectId
Response: Phase3Output

# Export to Excel
GET /api/phase3/export/:projectId
Response: Excel file (blob)
```

### 13.2 Sample API Implementation

```javascript
// Evaluate format suitability
app.post('/api/phase3/evaluate-format', async (req, res) => {
  const { projectId, moduleId, formatId } = req.body;
  
  // Get module data
  const module = await getTrainingModule(projectId, moduleId);
  
  // Get project context (archetype, etc.)
  const context = await getProjectContext(projectId);
  
  // Evaluate each factor
  const factor1 = checkParticipantSuitability(formatId, module.estimatedParticipants);
  const factor2 = checkLevelAchievable(module.competencyId, module.targetLevel, formatId);
  const factor3 = checkStrategyConsistency(context.archetypeId, formatId);
  
  // Calculate overall
  const overall = calculateOverallSuitability(factor1, factor2, factor3);
  
  res.json({
    formatId,
    formatName: LEARNING_FORMATS[formatId].name,
    factors: {
      participants: factor1,
      levelAchievable: factor2,
      strategyConsistency: factor3
    },
    overallSuitability: overall
  });
});
```

---

## 14. Database Schema

### 14.1 Tables

```sql
-- Learning Formats (pre-populated)
CREATE TABLE learning_formats (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    mode_of_delivery VARCHAR(20),
    communication_type VARCHAR(20),
    collaboration_type VARCHAR(20),
    participant_min INT,
    participant_max INT,
    learning_type VARCHAR(20),
    max_level INT,
    effort_content_creation INT,
    effort_content_updation INT,
    effort_per_training INT,
    advantages JSONB,
    disadvantages JSONB,
    suitable_archetypes JSONB,
    learning_methods JSONB
);

-- Competency-Level Matrix (pre-populated)
CREATE TABLE competency_level_matrix (
    id SERIAL PRIMARY KEY,
    competency_id VARCHAR(50) NOT NULL,
    format_id VARCHAR(50) NOT NULL,
    achievable_level INT NOT NULL,
    UNIQUE(competency_id, format_id)
);

-- Strategy-LF Matrix (pre-populated)
CREATE TABLE strategy_lf_matrix (
    id SERIAL PRIMARY KEY,
    archetype_id VARCHAR(50) NOT NULL,
    format_id VARCHAR(50) NOT NULL,
    consistency VARCHAR(5) NOT NULL,  -- '++', '+', '-'
    UNIQUE(archetype_id, format_id)
);

-- Project Training Modules (Phase 3 data)
CREATE TABLE project_training_modules (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    module_id VARCHAR(100) NOT NULL,
    competency_id VARCHAR(50) NOT NULL,
    target_level INT NOT NULL,
    pmt_type VARCHAR(20),
    actual_users_with_gap INT,
    estimated_participants INT,
    selected_format_id VARCHAR(50),
    format_suitability JSONB,
    confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, module_id)
);

-- Project Timeline
CREATE TABLE project_timeline (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL UNIQUE,
    concept_start_date DATE,
    concept_end_date DATE,
    pilot_start_date DATE,
    run_first_training DATE,
    run_last_training DATE,
    planned_sessions INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Phase 3 Settings
CREATE TABLE project_phase3_settings (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL UNIQUE,
    selected_view VARCHAR(30) DEFAULT 'competency_level',
    scaling_factor DECIMAL(10,2),
    actual_assessed_users INT,
    target_group_size INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 15. Export Specification

### 15.1 Excel Export Content

**Ulf's Requirement**: *"An exported excel sheet with overview of all the information - number of people going to be trained, the selected learning format, timeline data."*

**Sheets**:

1. **Overview**
   - Project info
   - Selected view (Competency-Level / Role-Clustered)
   - Archetype
   - Scaling info
   - Summary stats

2. **Training Modules**
   - Module name
   - Competency
   - Level
   - PMT Type
   - Roles
   - Estimated Participants
   - Selected Format
   - Suitability (Factor 1, 2, 3)

3. **Timeline**
   - Phase
   - Start Date
   - End Date
   - Notes

4. **Learning Objectives** (from Phase 2)
   - All LO data

### 15.2 Personnel Subject to Training (Ulf's Reference)

Similar to the reference PDF "SE Qualification Program", create overview table:

| Training Module | Roles | Estimated Persons |
|-----------------|-------|-------------------|
| RqE1 (Req Def L1) | Req Eng, Sys Arch | 120 |
| RqE2 (Req Def L2 - Method) | Req Eng, Sys Arch, PM | 94 |
| RqE3 (Req Def L2 - Tool) | Req Eng | 45 |
| SyA1 (Sys Arch L1) | Sys Arch, Sys Dev | 80 |
| ... | ... | ... |

---

## 16. Implementation Checklist

### 16.1 Task Breakdown

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 1 | Create Learning Format database tables and seed data | HIGH | M |
| 2 | Create Competency-Level Matrix and seed data | HIGH | S |
| 3 | Create Strategy-LF Matrix and seed data | HIGH | S |
| 4 | Build Phase 3 dashboard page | HIGH | M |
| 5 | Build view selector (Competency-Level vs Role-Clustered) | HIGH | M |
| 6 | Build training modules list (Competency-Level view) | HIGH | L |
| 7 | Build training modules list (Role-Clustered view) | MEDIUM | L |
| 8 | Build format selection dropdown | HIGH | M |
| 9 | Implement 3-factor suitability evaluation | HIGH | M |
| 10 | Build "Learn more" modal with format details | MEDIUM | M |
| 11 | Implement user count scaling logic | HIGH | S |
| 12 | Build Timeline Planning page | MEDIUM | M |
| 13 | Build Phase 3 summary/review page | MEDIUM | M |
| 14 | Implement Excel export | LOW | M |
| 15 | API endpoints implementation | HIGH | L |
| 16 | Integration tests | MEDIUM | M |

### 16.2 Testing Checklist

**Factor 1 (Participants)**:
- [ ] Green when within range
- [ ] Yellow when slightly outside (±20%)
- [ ] Red when far outside range

**Factor 2 (Level Achievable)**:
- [ ] Green when can achieve target or higher
- [ ] Yellow when can achieve one level below
- [ ] Red when cannot achieve
- [ ] E-Learning formats max at Level 2

**Factor 3 (Strategy)**:
- [ ] Green for ++ consistency
- [ ] Yellow for + consistency
- [ ] Red for - consistency
- [ ] Correct mappings for all 7 archetypes

**Views**:
- [ ] Low maturity shows only Competency-Level view
- [ ] High maturity shows both views
- [ ] View switching works correctly

**Scaling**:
- [ ] Scaling factor calculated correctly
- [ ] User notification displayed
- [ ] Scaled values used in Factor 1

**Timeline**:
- [ ] All dates can be entered
- [ ] Validation (concept before pilot before run)
- [ ] Timeline visualization displays correctly

---

## References

1. Ulf Meeting Notes (11-12-2025)
2. Sachin Kumar Master Thesis (2023) - "Identifying suitable learning formats for Systems Engineering"
3. SE Qualification Program - Input for identifying training service providers (Reference PDF)
4. Phase 2 Learning Objectives Specification
5. Phase 1 Analysis Specification

---

## Document Version

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 3.0 | December 2025 | Jomon George | COMPLETE REDESIGN |

**Major Changes from v2.x**:
- User-driven selection instead of automatic recommendations
- Two training structure views
- 3 simple suitability factors (green/yellow/red)
- Corrected matrices for Level Achievable and Strategy Consistency
- Added Timeline Planning as Task 2
- Added user count scaling with notification
