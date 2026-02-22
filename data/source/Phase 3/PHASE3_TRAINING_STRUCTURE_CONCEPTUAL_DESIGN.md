# Phase 3: Training Structure - Conceptual Design

**Document Type**: Conceptual Framework
**Purpose**: Thesis Chapter - Conceptual Framework (not technical implementation)
**Based on**: Meeting with Ulf Martensson, 13.01.2026
**Author**: Jomon George
**Date**: January 2026

---

## 1. Introduction

Phase 3 "Macro Planning" addresses a fundamental question in SE qualification planning: **How should training programs be structured to efficiently develop competencies across diverse organizational roles?**

This document describes the conceptual design decisions for structuring SE training programs, including the rationale for grouping roles into training cohorts and the two alternative approaches organizations can choose from.

---

## 2. The Training Structuring Problem

### 2.1 The Challenge

Organizations implementing SE qualification programs face a structuring dilemma:

- **Too granular**: Creating individual training for each role is resource-intensive and impractical
- **Too generic**: One-size-fits-all training fails to address role-specific competency needs
- **Optimal balance**: Group roles with similar competency needs while maintaining relevance

### 2.2 Key Questions

1. How do we group roles into training cohorts that make pedagogical and organizational sense?
2. How do we handle roles that need deep expertise vs. roles that need only awareness?
3. How do we structure training so common knowledge is taught once, while specialized content is targeted?

---

## 3. Two Training Structure Approaches

The framework offers organizations two distinct approaches to structuring their SE training programs:

### 3.1 Competency-Level Based Approach

**Concept**: Training is organized around competencies and proficiency levels, independent of roles.

```
Training Structure:
├── Systems Thinking - Level 1 (Knowing)
├── Systems Thinking - Level 2 (Understanding)
├── Requirements Definition - Level 1 (Knowing)
├── Requirements Definition - Level 2 (Understanding) - Method
├── Requirements Definition - Level 2 (Understanding) - Tool
├── Requirements Definition - Level 4 (Applying) - Method
├── Requirements Definition - Level 4 (Applying) - Tool
└── ... (all competency-level combinations)
```

**Characteristics**:
- Modules are defined by: Competency + Level + PMT (Process/Method/Tool)
- Any role needing that competency-level attends the same training
- Maximum reuse of training content across roles
- Participants from different roles learn together

**Best suited for**:
- Organizations with lower SE maturity
- Organizations without clearly defined role structures
- Situations where cross-functional learning is valued
- Smaller organizations where role specialization is limited

### 3.2 Role-Clustered Based Approach

**Concept**: Training is organized as pre-packaged programs tailored to role groups with similar competency profiles.

```
Training Structure:
├── SE for Engineers (Program)
│   ├── Common Base Modules (all engineers together)
│   └── Role-Specific Pathways (specialized tracks)
│
├── SE for Managers (Program)
│   └── Modules focused on management & social competencies
│
└── SE for Interfacing Partners (Program)
    └── Basic awareness modules (Level 1-2 only)
```

**Characteristics**:
- Pre-built training packages for role clusters
- Roles are assigned to programs based on their competency gap profiles
- Engineers share a common base but diverge into specialized pathways
- Clear learning paths for different organizational audiences

**Best suited for**:
- Organizations with higher SE maturity
- Organizations with well-defined role structures
- Situations where role identity drives learning motivation
- Larger organizations with distinct functional groups

---

## 4. The Three Training Programs

Based on analysis of SE role competency requirements, roles can be meaningfully grouped into three training programs:

### 4.1 SE for Engineers

**Target Audience**: Roles requiring deep, applicable SE competencies

**Assignment Criterion**: Role needs Level 4 (Applying) or higher in **Technical** or **Core** competencies

**Technical Competencies**:
- Requirements Definition
- System Architecting
- Integration, Verification, Validation
- Operation and Support
- Agile Methods

**Core Competencies** (experience-based, harder to develop):
- Systems Thinking
- Lifecycle Consideration
- Customer/Value Orientation
- Systems Modelling and Analysis

**Program Structure - Hybrid Approach**:

The SE for Engineers program uses a hybrid structure that balances efficiency with specialization:

```
SE for Engineers
│
├── COMMON BASE (all engineer roles together)
│   │
│   │   Modules where all engineering roles need the SAME level.
│   │   Example: All engineers need "Understanding" level in
│   │   Requirements Definition, so they train together.
│   │
│   ├── Systems Thinking - Level 2 (Understanding)
│   ├── Requirements Definition - Level 2 - Method
│   ├── Requirements Definition - Level 2 - Tool
│   ├── Lifecycle Consideration - Level 2
│   └── ... other shared modules
│
└── ROLE-SPECIFIC PATHWAYS (specialized tracks)
    │
    │   Modules where roles need DIFFERENT levels.
    │   Training diverges here based on role requirements.
    │
    ├── Requirements Engineering Track
    │   ├── Requirements Definition - Level 4 - Method
    │   └── Requirements Definition - Level 4 - Tool
    │
    ├── System Architecture Track
    │   ├── System Architecting - Level 4 - Method
    │   └── System Architecting - Level 4 - Tool
    │
    ├── Verification & Validation Track
    │   ├── IVV - Level 4 - Method
    │   └── IVV - Level 4 - Tool
    │
    └── ... other specialized tracks
```

**Rationale**:
- The "Understanding" level (Level 2) provides foundational knowledge that all engineers benefit from learning together
- The "Applying" level (Level 4) involves role-specific tools and methods where specialization is valuable
- This structure avoids training engineers in deep tool knowledge they will never use

### 4.2 SE for Managers

**Target Audience**: Roles requiring SE awareness for decision-making and team leadership

**Assignment Criterion**: Role needs Level 4+ **only** in Social/Personal or Management competencies (not in Technical/Core)

**Social/Personal Competencies**:
- Communication
- Leadership
- Self-Organization

**Management Competencies**:
- Project Management
- Decision Management
- Information Management
- Configuration Management

**Program Characteristics**:
- Focus on SE principles relevant to management decisions
- Includes competencies needed for leading SE teams
- Does not require deep technical SE tool/method knowledge
- Executives are included in this program

### 4.3 SE for Interfacing Partners

**Target Audience**: Roles requiring basic SE awareness for effective collaboration

**Assignment Criterion**: Role needs **only** Level 1 (Knowing) or Level 2 (Understanding) across all competencies

**Typical Roles**:
- Support staff
- Quality engineers (non-SE focused)
- Customer representatives
- Operations staff
- External partners
- Supplier managers

**Program Characteristics**:
- Basic awareness and understanding modules only
- No applying-level (Level 4) content
- Focus on "what is SE" and "why it matters"
- Enables effective collaboration with SE practitioners

---

## 5. Role Assignment Logic

The assignment of roles to training programs is determined by analyzing the **competency gaps** identified in Phase 2:

```
Decision Tree for Role Assignment:

1. Does the role have a Level 4+ gap in any Technical or Core competency?
   │
   ├── YES → Assign to "SE for Engineers"
   │
   └── NO → Continue to question 2

2. Does the role have a Level 4+ gap in Social/Personal or Management competencies?
   │
   ├── YES → Assign to "SE for Managers"
   │
   └── NO → Continue to question 3

3. Does the role have any gaps (Level 1 or 2)?
   │
   ├── YES → Assign to "SE for Interfacing Partners"
   │
   └── NO → Role has no training needs (fully competent)
```

**Key Principle**: Assignment is based on **actual competency gaps**, not job titles or organizational hierarchy. A "Project Manager" with Level 4 gaps in Technical competencies would be assigned to Engineers, not Managers.

---

## 6. Relationship to Qualification Strategies

The seven qualification strategies (archetypes) defined in Phase 1 have natural affinities with the two training structure approaches:

| Strategy | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| Common Basic Understanding | Role-Clustered | Brings roles together for shared SE foundation |
| SE for Managers | Role-Clustered | Natural fit - managers train together |
| Orientation in Pilot Project | Both viable | Project teams may mix approaches |
| Needs-Based, Project-Oriented | Competency-Level | Flexible, addresses specific gaps as they arise |
| Continuous Support | Competency-Level | Ongoing, modular learning by competency |
| Train the Trainer | Role-Clustered | Trainers form a natural cohort |
| Certification | Competency-Level | Standardized competency-based assessment |

**Note**: This mapping provides guidance but is not prescriptive. Organizations may choose either approach regardless of strategy.

---

## 7. Existing Training Consideration

### 7.1 Level Differentiation Within Competencies

When organizations have existing training programs, the framework captures this at the **competency-level** granularity, not just competency level:

**Example Scenario**:
- Organization has existing training for "Requirements Definition" at Knowing level (Level 1)
- But no training for Understanding (Level 2) or Applying (Level 4)

**Framework Response**:
- Exclude "Requirements Definition - Level 1" from new training modules
- Include "Requirements Definition - Level 2" and "Level 4" modules

**Rationale**: Organizations rarely have complete training coverage. Partial coverage (e.g., introductory but not advanced) is common and must be accounted for.

### 7.2 Two-Step Existing Training Check

1. **Step 1**: "Do you have training in any of the following competency areas?" (16 competencies)
2. **Step 2**: For selected competencies only: "To which level does your existing training cover?" (Levels 1, 2, 4)

This avoids overwhelming users with 48+ checkboxes (16 competencies x 3 levels) while capturing necessary detail.

---

## 8. Module Counting Principle

**Key Rule**: When modules appear in multiple training packages, they are counted only once toward the total.

**Example**:
- "Systems Thinking - Level 2" appears in both SE for Engineers and SE for Managers
- Total module count: 1 (not 2)

**Rationale**:
- The same training content is delivered once
- Participants from both programs may attend together
- Avoids inflating training effort estimates

---

## 9. Participant Estimation

### 9.1 The Scaling Problem

- Target group (from Phase 1): May be 200-500 employees
- Assessment participants (Phase 2): Typically 10-50 users
- Gap: Assessment represents only a sample of the target group

### 9.2 Scaling Formula

```
Scaling Factor = Target Group Size / Assessed Users

Estimated Participants = Users with Gap x Scaling Factor
```

**Example**:
- Target group: 200 employees
- Assessed users: 15
- Scaling factor: 200/15 = 13.3x
- Users with Requirements Definition Level 2 gap: 8
- Estimated participants: 8 x 13.3 = 107

### 9.3 Transparency

The framework always displays:
- Original assessment numbers
- Scaling factor applied
- Estimated (scaled) participant counts

This ensures users understand estimates are projections, not precise counts.

---

## 10. Learning Format Selection

### 10.1 The 10 Learning Formats

| Format | Max Achievable Level | Key Characteristic |
|--------|---------------------|-------------------|
| Seminar | Level 4 (Applying) | Traditional instructor-led |
| Webinar | Level 2 (Understanding) | Remote, synchronous |
| Coaching | Level 6 (Mastery) | One-on-one guidance |
| Mentoring | Level 6 (Mastery) | Long-term relationship |
| WBT (Web-Based Training) | Level 2 (Understanding) | E-learning, self-paced |
| CBT (Computer-Based Training) | Level 2 (Understanding) | E-learning, offline capable |
| Game-Based Learning | Level 4 (Applying) | Interactive, experiential |
| Conference | Level 1 (Knowing) | Passive, awareness |
| Blended Learning | Level 6 (Mastery) | Combination approach |
| Self-Learning | Level 2 (Understanding) | Individual study |

### 10.2 Three-Factor Suitability Evaluation

When a user selects a learning format, the system evaluates suitability across three factors:

**Factor 1: Participant Count**
- Does the format's capacity range match the estimated participants?
- Example: Coaching (1-5 participants) for 100 participants = unsuitable

**Factor 2: Level Achievability**
- Can the format develop competency to the target level?
- Example: Webinar (max Level 2) for Level 4 target = unsuitable

**Factor 3: Strategy Consistency**
- Is the format aligned with the organization's qualification strategy?
- Example: WBT for "Orientation in Pilot Project" strategy = less suitable

### 10.3 Advisory Nature

Suitability indicators are **advisory, not blocking**:
- Green: Suitable
- Yellow: Manageable with considerations
- Red: Potential issues to consider

Users may select any format regardless of indicators. The system provides information for informed decisions, not restrictions.

---

## 11. Timeline Planning

### 11.1 Five Milestones

The framework generates five key milestones for the training program:

| # | Milestone | Description |
|---|-----------|-------------|
| 1 | Concept Development Start | Training material development begins |
| 2 | Concept Development End | Materials ready for pilot testing |
| 3 | Pilot Start | Trial training with test group |
| 4 | Rollout Start | Full training program begins |
| 5 | Rollout End | Last planned session completes |

### 11.2 Factors Influencing Timeline

- **Participant count**: More participants = longer rollout
- **Module count**: More modules = longer development
- **Format mix**: E-learning requires more upfront development but enables parallel delivery
- **Organization maturity**: Higher maturity enables faster execution

### 11.3 Informational Nature

Timeline estimates are:
- Generated automatically based on inputs
- Informational/indicative only
- Not user-adjustable
- Starting points for detailed planning with training providers

---

## 12. Summary: Key Conceptual Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Number of training programs | 3 (Engineers, Managers, Interfacing Partners) | Balances specificity with practicality |
| Program assignment basis | Competency gaps, not job titles | Ensures training relevance |
| Engineers program structure | Hybrid (common base + pathways) | Efficiency + specialization |
| Two structure approaches | Competency-Level and Role-Clustered | Accommodates different organizational needs |
| Existing training granularity | Competency + Level | Captures partial coverage |
| Format suitability | Advisory, not restrictive | Supports informed decisions |
| Timeline | System-generated estimates | Consistent, data-driven starting point |

---

## 13. References

- Martensson, U. (2026). Meeting notes on SE-QPT implementation, January 13, 2026.
- Kumar, S. (2023). Identifying suitable learning formats for Systems Engineering. Master Thesis.
- INCOSE Systems Engineering Competency Framework.
- Kirkpatrick Training Evaluation Model.

---

*This document describes the conceptual framework for Phase 3 training structure design. Technical implementation details are documented separately.*
