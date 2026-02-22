# Timeline Planning Task - Phase 3 (Macro Planning)
## SE-QPT Implementation Specifications

---

## 1. Overview

Timeline Planning is **Task 3** within Phase 3 (Macro Planning) of SE-QPT. It focuses on **macro-level milestone scheduling** for the remaining phases of the training lifecycle that occur AFTER qualification planning is complete.

### Key Principle
- SE-QPT's Phases 1-2 already cover the **Exploration/Needs Assessment** and **Design/Planning** phases of the training lifecycle
- Timeline Planning therefore focuses on scheduling **Development through Sustainment** phases

---

## 2. Mapping SE-QPT to Training Lifecycle

| Lifecycle Phase | Covered By |
|-----------------|------------|
| 1. Exploration/Needs Assessment | SE-QPT Phase 1 (Maturity Assessment, Role Identification) + Phase 2 (Competency Assessment, Gap Identification) |
| 2. Design/Planning | SE-QPT Phase 2 (Learning Objectives) + Phase 3 (Building Trainings, Format Selection) |
| 3-6. Development through Sustainment | **Timeline Planning focuses here** |

---

## 3. Timeline Milestones (5 Milestones)

The system generates **5 estimated milestones** from the current date using suggested phase durations:

| Milestone | Description | Estimated Timeframe | Lifecycle Phase |
|-----------|-------------|---------------------|-----------------|
| **Concept Development Start** | When training material development begins | Current Quarter | Development |
| **Concept Development End** | When training materials should be ready | +2–4 months | Development |
| **Pilot Start** | When pilot training with test group begins | +3–5 months | Pilot |
| **Rollout Start** | When first full training session occurs | +4–8 months | Initial Implementation |
| **Rollout End** | When last planned training session completes | +10–20 months | Initial Implementation |

### Note on Sustainment
The **Sustainment/Continuous Improvement phase** (Phase 6 in lifecycle) occurs after rollout and represents **ongoing activities** rather than a fixed date. It is NOT scheduled as a specific milestone but acknowledged as a continuous process following rollout completion.

---

## 4. Timeline Estimation Basis

Durations from the Training Lifecycle Model:

| Phase | Suggested Duration |
|-------|-------------------|
| Development | 2–4 months |
| Pilot | 1–3 months |
| Initial Implementation | 6–12 months |

---

## 5. Example Timeline (Starting Q1 2026)

```
Q1 2026: Concept Development Start
Q2 2026: Concept Development End, Pilot Start
Q3 2026: Rollout Start
Q4 2026 – Q2 2027: Initial Implementation (Rollout)
Q3 2027 onwards: Sustainment/Continuous Improvement
```

---

## 6. Implementation Logic

### 6.1 Calculation Algorithm

```python
# Pseudocode for Timeline Milestone Generation

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def generate_timeline_milestones(start_date=None):
    """
    Generate 5 timeline milestones from start date.
    
    Args:
        start_date: Starting date (defaults to current date)
    
    Returns:
        Dictionary with 5 milestone dates (min and max ranges)
    """
    if start_date is None:
        start_date = datetime.now()
    
    milestones = {
        "concept_development_start": {
            "date": start_date,
            "description": "When training material development begins",
            "phase": "Development"
        },
        "concept_development_end": {
            "date_min": start_date + relativedelta(months=2),
            "date_max": start_date + relativedelta(months=4),
            "description": "When training materials should be ready",
            "phase": "Development"
        },
        "pilot_start": {
            "date_min": start_date + relativedelta(months=3),
            "date_max": start_date + relativedelta(months=5),
            "description": "When pilot training with test group begins",
            "phase": "Pilot"
        },
        "rollout_start": {
            "date_min": start_date + relativedelta(months=4),
            "date_max": start_date + relativedelta(months=8),
            "description": "When first full training session occurs",
            "phase": "Initial Implementation"
        },
        "rollout_end": {
            "date_min": start_date + relativedelta(months=10),
            "date_max": start_date + relativedelta(months=20),
            "description": "When last planned training session completes",
            "phase": "Initial Implementation"
        }
    }
    
    return milestones
```

### 6.2 Quarter Calculation Helper

```python
def get_quarter(date):
    """Return quarter string (e.g., 'Q1 2026') for a date."""
    quarter = (date.month - 1) // 3 + 1
    return f"Q{quarter} {date.year}"

def format_milestone_range(date_min, date_max):
    """Format a milestone date range as quarter string."""
    q_min = get_quarter(date_min)
    q_max = get_quarter(date_max)
    if q_min == q_max:
        return q_min
    return f"{q_min} – {q_max}"
```

---

## 7. UI/UX Requirements

### 7.1 Display Format
- Show milestones as a **visual timeline** (Gantt-like or milestone chart)
- Display **date ranges** (not fixed dates) to indicate flexibility
- Use quarter-based display for macro-level planning

### 7.2 User Adjustability
Organizations can **adjust** the generated timeline estimates based on:
- Specific constraints
- Resource availability
- Urgency of training needs

### 7.3 Notification/Warning
Display a notification indicating:
> "These timeline estimates are system-generated based on typical training lifecycle durations. Adjust as needed for your organization's specific constraints."

---

## 8. Why Macro-Level Only?

Timeline planning in Phase 3 remains at **macro level (milestones only)** rather than detailed session scheduling because:

1. **Unknown logistics**: Detailed scheduling depends on trainer availability, room bookings, and other logistics unknown at this stage
2. **Provider responsibility**: Training providers (internal or external) typically handle detailed scheduling
3. **RFP integration**: The RFP output document specifies timeline requirements; providers respond with detailed schedules

---

## 9. Data Structure for Storage

```typescript
interface TimelineMilestone {
  id: string;
  name: string;
  description: string;
  lifecyclePhase: 'Development' | 'Pilot' | 'Initial Implementation' | 'Sustainment';
  estimatedDateMin: Date;
  estimatedDateMax: Date;
  adjustedDate?: Date;  // User-adjusted date (optional)
  isAdjusted: boolean;
}

interface TimelinePlan {
  organizationId: string;
  createdAt: Date;
  startDate: Date;
  milestones: TimelineMilestone[];
  notes?: string;
}
```

---

## 10. Phase 3 Outputs (Including Timeline)

Phase 3 produces the following outputs for Phase 4:

1. **Existing training coverage documentation**: Record of competencies covered by existing organizational training programs
2. **Training modules with assigned formats**: Each module (not covered by existing training) has a selected learning format
3. **Participant estimates**: Scaled from assessment data to target group size
4. **Suitability documentation**: Record of 3-factor feedback for each selection
5. **Timeline milestones**: System-generated estimates for Concept Development, Pilot, and Rollout phases ← **This is the Timeline Planning output**
6. **Warnings and notes**: Any red indicators or constraints flagged during selection

---

## 11. Integration with RFP Output (Phase 4)

Phase 4 can generate **Request for Proposal (RFP)** documents for external training procurement, containing:
- Training requirements specification
- Learning objectives
- Target audience description
- Format requirements
- **Timeline constraints** ← Uses Timeline Planning output
- Evaluation criteria

---

## 12. Key Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| 5-milestone timeline (macro) | Exploration/Design done by SE-QPT; schedule remaining phases |
| Date ranges not fixed dates | Flexibility for organizational constraints |
| Quarter-based display | Appropriate granularity for macro-level planning |
| User-adjustable | Organizations have context system cannot capture |
| No Sustainment milestone | Continuous process, not fixed endpoint |

---

## 13. Related Components

- **Phase 3 Task 1**: Building Training Structure (provides training modules)
- **Phase 3 Task 2**: Select Learning Formats (provides format selections)
- **Phase 4**: Micro Planning (uses timeline milestones for RFP)
- **Training Lifecycle Model**: Theoretical foundation (6-phase model)

---

## 14. Source References

- Conceptual Framework Chapter, Section: Phase 3 - Task 3: Timeline Planning
- Training Lifecycle Model (6-phase model from theoretical foundations)
- Kugelmeier et al. (2021) - Training development process model
