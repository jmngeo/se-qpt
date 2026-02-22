# SE-QPT Phase 3: Learning Format Recommendation - Conceptual Design

## 1. HIGH-LEVEL PROCESS FLOW

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                          LEARNING FORMAT RECOMMENDATION                        ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║   ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐       ║
║   │    INPUTS       │───►│   PROCESSING     │───►│     OUTPUTS         │       ║
║   │  (What we have) │    │  (What we do)    │    │  (What user sees)   │       ║
║   └─────────────────┘    └──────────────────┘    └─────────────────────┘       ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## 2. DETAILED INPUT-PROCESS-OUTPUT MODEL

### 2.1 INPUTS (What We Already Have)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AVAILABLE INPUTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FROM PHASE 1 (Organization Analysis)                                       │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ • Selected Training Strategy                                       │     │
│  │ • Training Group Size (small/medium/large)                         │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  FROM PHASE 2 (Competency Assessment + Learning Objectives)                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ • Gap Data per User per Competency per Level                       │     │
│  │   Example: User A has gap at Level 2 in Systems Thinking           │     │
│  │                                                                    │     │
│  │ • Aggregated Gap Counts (what we can calculate)                    │     │
│  │   Example: 45 users need Level 2 in Systems Thinking               │     │
│  │                                                                    │     │
│  │ • Learning Objectives (already generated)                          │     │
│  │   Example: "Participant understands system boundaries..."          │     │
│  │                                                                    │     │
│  │ • Role-User Mapping                                                │     │
│  │   Example: 45 users = 20 Req Engineers + 15 Sys Architects + 10... │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  FROM SACHIN'S THESIS (Reference Knowledge)                                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ • 10 Learning Format Definitions                                   │     │
│  │ • Format-Level Suitability Matrix                                  │     │
│  │ • Competency-Format Scores (C_Co-LF Matrix)                        │     │
│  │ • Archetype-Format Mappings                                        │     │
│  │ • Effort Metrics (Content Creation, Per Training)                  │     │
│  │ • Advantages/Disadvantages per Format                              │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 PROCESSING (What We Do With Inputs)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PROCESSING STEPS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: AGGREGATE GAP DATA                                                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  FOR each competency (16 total):                                   │     │
│  │      FOR each level (1, 2, 4):                                     │     │
│  │          Count total users with gap at this level                  │     │
│  │          Calculate gap_percentage = users_with_gap / total_users   │     │
│  │                                                                    │     │
│  │  OUTPUT: Aggregate gap counts                                      │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ Competency       │ L1 Gap │ L2 Gap │ L4 Gap │ Total      │      │     │
│  │  │ Systems Thinking │ 45     │ 120    │ 30     │ 195 users  │      │     │
│  │  │ Requirements Def │ 80     │ 90     │ 50     │ 220 users  │      │     │
│  │  │ ...              │ ...    │ ...    │ ...    │ ...        │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  STEP 2: ANALYZE DISTRIBUTION PATTERNS                                      │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  FOR each competency:                                              │     │
│  │      Calculate variance across user scores                         │     │
│  │      Detect if bimodal (two distinct clusters)                     │     │
│  │      Determine pattern: uniform | bimodal | skewed | normal        │     │
│  │                                                                    │     │
│  │  OUTPUT: Distribution flags                                        │     │
│  │  ┌──────────────────────────────────────────────────────────┐      │     │
│  │  │ Competency       │ Pattern  │ Variance │ Flag            │      │     │
│  │  │ Systems Thinking │ normal   │ 2.1      │ None            │      │     │
│  │  │ Requirements Def │ bimodal  │ 8.5      │ ⚠️ Split needed │      │     │
│  │  │ Agile Methods    │ skewed   │ 1.2      │ 🔹 Few outliers │      │     │
│  │  └──────────────────────────────────────────────────────────┘      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  STEP 3: FILTER FORMATS BY LEVEL (E-Learning Rule)                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  FOR each level:                                                   │     │
│  │      IF level = 4 (Applying):                                      │     │
│  │          EXCLUDE: WBT, CBT, Self-Learning                          │     │
│  │          KEEP: Seminar, Webinar, Coaching, Mentoring,              │     │
│  │                Game-Based, Blended                                 │     │
│  │      ELSE (level 1 or 2):                                          │     │
│  │          ALL formats eligible                                      │     │
│  │                                                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  STEP 4: SCORE AND RANK FORMATS                                             │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  FOR each competency, FOR each level:                              │     │
│  │      FOR each eligible format:                                     │     │
│  │          score = 0                                                 │     │
│  │                                                                    │     │
│  │          // Factor 1: User count appropriateness (30%)             │     │
│  │          IF users > 100 AND format.supports_large: score += 30     │     │
│  │          IF users < 10 AND format.supports_individual: score += 30 │     │
│  │                                                                    │     │
│  │          // Factor 2: Distribution pattern match (25%)             │     │
│  │          IF bimodal AND format = seminar: score += 25              │     │
│  │          IF few_outliers AND format = coaching: score += 25        │     │
│  │                                                                    │     │
│  │          // Factor 3: Sachin's competency-format score (25%)       │     │
│  │          score += COMPETENCY_LF_MATRIX[comp][format] * weight      │     │
│  │                                                                    │     │
│  │                                                                    │     │
│  │      RANK formats by score                                         │     │
│  │      SELECT top format as primary recommendation                   │     │
│  │                                                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  STEP 5: GENERATE RATIONALE                                                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  FOR each recommendation:                                          │     │
│  │      Generate human-readable explanation:                          │     │
│  │      "We recommend [FORMAT] because:                               │     │
│  │       - [X] users need Level [Y] training                          │     │
│  │       - [Distribution pattern observation]                         │     │
│  │       - This format scores highest for [competency] competency"    │     │
│  │                                                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 OUTPUTS (What User Sees)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER OUTPUTS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OUTPUT 1: AGGREGATE GAP OVERVIEW                                           │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  ┌─────────────────────────────────────────────────────────────┐   │     │
│  │  │  📊 Gap Overview                                            │   │     │
│  │  │  ────────────────────────────────────────────────────────── │   │     │
│  │  │  12 of 16 competencies have gaps                            │   │     │
│  │  │  28 level advancements needed (sum of all modules)          │   │     │
│  │  └─────────────────────────────────────────────────────────────┘   │     │
│  │                                                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  OUTPUT 2: PER-COMPETENCY RECOMMENDATIONS                                   │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                                                                    │     │
│  │  ┌─────────────────────────────────────────────────────────────┐   │     │
│  │  │  🎯 Systems Thinking                                        │   │     │
│  │  │  ────────────────────────────────────────────────────────── │    │     │
│  │  │                                                             │    │     │
│  │  │  Level 1 (Knowing):     45 users need training              │    │     │
│  │  │  Level 2 (Understanding): 120 users need training           │    │     │
│  │  │  Level 4 (Applying):    30 users need training              │    │     │
│  │  │                                                             │    │     │
│  │  │  📌 RECOMMENDED FORMAT: Blended Learning                    │    │     │
│  │  │                                                             │    │     │
│  │  │  Rationale: "195 users across 3 levels suggests a           │    │     │
│  │  │  progressive approach. Blended Learning allows WBT for      │    │     │
│  │  │  Levels 1-2 (165 users) combined with Seminars for          │    │     │
│  │  │  Level 4 application practice (30 users)."                  │    │     │
│  │  │                                                             │    │     │
│  │  │  [View Format Details]  [Select Different Format ▼]         │    │     │
│  │  │                                                             │    │     │
│  │  │  Alternative Options:                                       │    │     │
│  │  │  • Seminar (score: 72)                                      │    │     │
│  │  │  • Webinar + Coaching (score: 68)                           │    │     │
│  │  │                                                             │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  │                                                                     │     │
│  │  ┌─────────────────────────────────────────────────────────────┐    │     │
│  │  │  🎯 Requirements Definition                                 │    │     │
│  │  │  ────────────────────────────────────────────────────────── │    │     │
│  │  │                                                             │    │     │
│  │  │  Level 1: 80 users  │  Level 2: 90 users  │  Level 4: 50    │    │     │
│  │  │                                                             │    │     │
│  │  │  ⚠️ FLAG: Bimodal distribution detected                     │    │     │
│  │  │  "50% of users at Level 0, 45% at Level 4. Consider         │    │     │
│  │  │  splitting into two separate training tracks."              │    │     │
│  │  │                                                             │    │     │
│  │  │  📌 RECOMMENDED: Two Seminars (beginner + advanced)         │    │     │
│  │  │                                                             │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  │                                                                     │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  OUTPUT 3: FORMAT INFORMATION (Sachin's Posters)                             │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │                                                                    │      │
│  │  When user clicks [View Format Details]:                           │      │
│  │  Show Sachin's 12-section poster with:                             │      │
│  │  • Description                                                     │      │
│  │  • Characteristics (online/offline, sync/async, etc.)              │      │
│  │  • Advantages & Disadvantages                                      │      │
│  │  • Effort metrics (content creation, per training)                 │      │
│  │  • Suitable archetypes                                             │      │
│  │  • Learning methods included                                       │      │
│  │                                                                    │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                              │
│  OUTPUT 4: USER SELECTION & EXPORT                                           │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │                                                                    │      │
│  │  User can:                                                         │      │
│  │  • Accept recommendations as-is                                    │      │
│  │  • Override with different format selection                        │      │
│  │                                                                    │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. DECISION RULES SUMMARY

### 3.1 Primary Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LEARNING FORMAT DECISION MATRIX                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Users Needing    │ Target Level    │ Distribution    │ Recommendation      │
│  Training         │                 │                 │                     │
│  ────────────────────────────────────────────────────────────────────────── │
│  > 100 users      │ Level 1 or 2    │ Any             │ WBT / Webinar       │
│  > 100 users      │ Level 4         │ Any             │ Blended / Seminar   │
│  ────────────────────────────────────────────────────────────────────────── │
│  30-100 users     │ Level 1 or 2    │ Normal          │ Seminar / WBT       │
│  30-100 users     │ Level 4         │ Normal          │ Seminar             │
│  30-100 users     │ Any             │ Bimodal         │ Split into 2 groups │
│  ────────────────────────────────────────────────────────────────────────── │
│  10-30 users      │ Any             │ Any             │ Seminar / Blended   │
│  ────────────────────────────────────────────────────────────────────────── │
│  < 10 users       │ Level 1 or 2    │ Any             │ WBT / Self-Learning │
│  < 10 users       │ Level 4         │ Any             │ Coaching / Mentoring│
│  ────────────────────────────────────────────────────────────────────────── │
│  1-3 users        │ Any             │ Outliers        │ Coaching / External │
│                   │                 │                 │ Certification       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Hard Constraints (Always Apply)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HARD CONSTRAINTS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONSTRAINT 1: E-Learning Level Limit                                       │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  IF target_level = 4 (Applying):                                   │     │
│  │      NEVER recommend: WBT, CBT, Self-Learning, Conference          │     │
│  │      REASON: "Application requires hands-on practice"              │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  CONSTRAINT 2: Very Small Groups                                            │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  IF users_needing_training < 5:                                    │     │
│  │      FLAG: "Group training not cost-effective"                     │     │
│  │      RECOMMEND: Coaching, Mentoring, or External Certification     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  CONSTRAINT 3: Bimodal Distribution                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  IF variance > 6.0 AND two_peaks_detected:                          │    │
│  │      FLAG: "Bimodal distribution - median misleading"               │    │
│  │      RECOMMEND: Split into separate training tracks                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Level-Based Format Restrictions (HARD CONSTRAINT)

**Rule**: "E-learning can help you create understanding basics. You probably might not be able to achieve Applying level with e-learning."

| Learning Format | Level 1 (Knowing) | Level 2 (Understanding) | Level 4 (Applying) |
|-----------------|:-----------------:|:----------------------:|:-----------------:|
| Seminar | ✅ | ✅ | ✅ |
| Webinar | ✅ | ✅ | ⚠️ Limited |
| Coaching | ✅ | ✅ | ✅ Best |
| Mentoring | ✅ | ✅ | ✅ Best |
| **WBT** | ✅ | ✅ | ❌ **EXCLUDED** |
| **CBT** | ✅ | ✅ | ❌ **EXCLUDED** |
| Game-Based | ✅ | ✅ | ✅ |
| **Conference** | ✅ | ⚠️ Limited | ❌ **EXCLUDED** |
| Blended | ✅ | ✅ | ✅ |
| **Self-Learning** | ✅ | ⚠️ Limited | ❌ **EXCLUDED** |

### 3.4 Recommendation Algorithm Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: Aggregate gap data per competency                       │
│          → Count users needing L1, L2, L4 across ALL roles       │
│                                                                  │
│  STEP 2: Analyze distribution patterns                           │
│          → Detect bimodal, calculate variance, set flags         │
│                                                                  │
│  STEP 3: Filter formats by level (HARD CONSTRAINT)               │
│          → IF Level 4: EXCLUDE WBT, CBT, Conference, Self-Learn  │
│                                                                  │
│  STEP 4: Score eligible formats                                  │
│          → Based on user count, distribution, competency match   │
│                                                                  │
│  STEP 5: Generate recommendation with rationale                  │
│          → "We recommend X because Y users need training..."     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 Scenario Decision Matrix

| Scenario | Gap % | Pattern | Level 1-2 Recommendation | Level 4 Recommendation |
|----------|-------|---------|--------------------------|------------------------|
| All beginners | >90% | uniform | Seminar or WBT | Seminar |
| All experts | 0% | uniform | No training | No training |
| 90% beginners | >70% | skewed_low | Seminar (experts as mentors) | Seminar |
| 10% beginners | <20% | skewed_high | Coaching/Mentoring | Coaching/Mentoring |
| Bimodal 50/50 | ~50% | bimodal | Split: Two Seminars | Split: Two Seminars |
| Equal spread | ~50% | normal | Blended Learning | Blended Learning |
| Tight cluster | varies | uniform | Seminar | Seminar |
| Few outliers | <10% | skewed_high | Coaching for outliers | Coaching for outliers |
---

## 4. QUESTIONS

### 4.1 Scope Questions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUESTION 1: Recommendation Granularity                                     │
│  ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Option A: ONE recommendation per COMPETENCY                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Systems Thinking → Recommended: Blended Learning                  │     │
│  │  (covers all 3 levels together)                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  Option B: ONE recommendation per LEVEL per COMPETENCY                      │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Systems Thinking Level 1 → WBT                                    │     │
│  │  Systems Thinking Level 2 → WBT                                    │     │
│  │  Systems Thinking Level 4 → Seminar                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  CURRENT ASSUMPTION: Option A (per competency)                              │
│  NEED CONFIRMATION: Is this correct?                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  QUESTION 2: Module Combination                                             │
│  ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  Note: "One big workshop covering Levels 1+2+4 together"           │
│                                                                             │
│  When should we recommend combined modules vs separate?                     │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Combined Workshop (L1+L2+L4):                                     │     │
│  │  - Same users need all 3 levels                                    │     │
│  │  - Intensive, compressed timeline                                  │     │
│  │                                                                    │     │
│  │  Separate Modules (L1, then L2, then L4):                          │     │
│  │  - Different users need different levels                           │     │
│  │  - Progressive, spaced learning                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  NEED DECISION: What criteria trigger combined vs separate?                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  QUESTION 3: Role Drill-Down                                                │
│  ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│  When showing "45 users need Level 2 in Systems Thinking"                   │
│                                                                             │
│  Should we always show role breakdown?                                      │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Option A: Show aggregate only, drill-down on click                │     │
│  │  Option B: Always show role breakdown inline                       │     │
│  │  Option C: Show breakdown only if few roles (< 5)                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  CURRENT ASSUMPTION: Option A (aggregate first)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. EXAMPLE WALKTHROUGH

### Complete Example: Company with 500 employees, 5 roles

```
INPUT DATA:
├── Company: Miele (example)
├── Employees: 500 total
├── Roles: Req Engineer (100), Sys Architect (80), Test Eng (120), PM (50), SE Lead (50)
├── Maturity: Level 2
├── Archetype: Need-Based Project Oriented Training
└── Training Group Size: Medium

COMPETENCY: Systems Thinking

STEP 1: AGGREGATE GAPS
├── Level 1 gap: 45 users (Req: 20, Sys: 10, Test: 15)
├── Level 2 gap: 120 users (Req: 40, Sys: 30, Test: 30, PM: 20)
├── Level 4 gap: 30 users (SE Lead: 20, PM: 10)
└── Total: 195 users need some level of training

STEP 2: ANALYZE DISTRIBUTION
├── Variance: 2.1 (moderate)
├── Pattern: Normal distribution
└── Flag: None

STEP 3: FILTER BY LEVEL
├── Level 1: All formats eligible
├── Level 2: All formats eligible
└── Level 4: Exclude WBT, CBT, Conference, Self-Learning

STEP 4: SCORE FORMATS
├── Blended Learning: 85/100 (best for multi-level, large group)
├── Seminar: 72/100 (good for interaction, but 3 separate needed)
├── WBT + Coaching: 68/100 (WBT for L1-2, Coaching for L4)
└── Winner: Blended Learning

STEP 5: GENERATE OUTPUT
┌──────────────────────────────────────────────────────────────────┐
│  🎯 Systems Thinking                                             │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  Level 1 (Knowing):        45 users                              │
│  Level 2 (Understanding): 120 users                              │
│  Level 4 (Applying):       30 users                              │
│  ──────────────────────────────────────────────                  │
│  Total:                   195 users across 5 roles               │
│                                                                  │
│  📌 RECOMMENDED: Blended Learning                                │
│                                                                  │
│  "195 users across 3 levels makes Blended Learning optimal.      │
│  Users can complete Levels 1-2 via Web-Based Training            │
│  (self-paced, flexible), then attend Seminars for Level 4        │
│  application practice. This balances cost-effectiveness for      │
│  large groups with hands-on learning for application level."     │
│                                                                  │
│  [View Blended Learning Details]  [Select Different ▼]           │
│                                                                  │
│  Roles affected:                                                 │
│  • Requirements Engineer: 60 users (L1: 20, L2: 40)              │
│  • Systems Architect: 40 users (L1: 10, L2: 30)                  │
│  • Test Engineer: 45 users (L1: 15, L2: 30)                      │
│  • Project Manager: 30 users (L2: 20, L4: 10)                    │
│  • SE Lead: 20 users (L4: 20)                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. User Interface Design

### 7.1 Page Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 3: Learning Format Recommendations                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📊 Gap Overview                                                        ││
│  │  ───────────────────────────────────────────────────────────────────────││
│  │  12 of 16 competencies have gaps                                        ││
│  │  28 level advancements needed                                           ││
│  │  847 total training instances                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  🎯 Systems Thinking                                          [Expand ▼]││
│  │  ───────────────────────────────────────────────────────────────────────││
│  │                                                                         ││
│  │  Level 1 (Knowing):        45 users   → Recommended: WBT                ││
│  │  Level 2 (Understanding): 120 users   → Recommended: Blended Learning   ││
│  │  Level 4 (Applying):       30 users   → Recommended: Seminar            ││
│  │                                                                         ││
│  │  [View Details] [Select Different Format ▼] [See Role Breakdown]        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  🎯 Requirements Definition                                   [Expand ▼]││
│  │  ───────────────────────────────────────────────────────────────────────││
│  │  ⚠️ FLAG: Bimodal distribution detected - consider splitting            ││
│  │                                                                         ││
│  │  Level 1: 80 users  │  Level 2: 90 users  │  Level 4: 50 users          ││
│  │  Recommended: Split into Two Seminars (beginner + advanced track)       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ... (more competencies)                                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  [Export to Excel]  [Confirm Selections & Proceed to Module Selection]  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Format Detail Modal (Sachin's Poster)

When user clicks "View Details":

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Blended Learning                                                    [Close]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CHARACTERISTICS                                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Mode: Hybrid  │ Communication: Hybrid  │ Collaboration: Group          │ │
│  │ Participants: 5-50  │ Learning Type: Formal                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  DESCRIPTION                                                                │
│  Combines synchronous and asynchronous, in-person and online.               │
│  Maximizes benefits of both e-learning and face-to-face training.           │
│                                                                             │
│  ADVANTAGES ✅                          DISADVANTAGES ❌                    │
│  • Best of both worlds                  • Complex planning                  │
│  • Flexible scheduling                  • Integration challenges            │
│  • Can cover Levels 1, 2, AND 4         • Time management needed            │
│                                                                             │
│  EFFORT METRICS (1-5 scale)                                                 │
│  Content Creation: ████▒ (5)  │  Updates: ████░ (4)  │  Per Training: ████░ │
│                                                                             │
│  LEARNING METHODS INCLUDED                                                  │
│  Online modules, Face-to-face sessions, Virtual classrooms,                 │
│  Discussion forums, Project work, Assessments                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---