# Learning Format Recommendation Module - Implementation Specification

## Document Information
- **Module**: Phase 3 - Macro-planning of SE Training Initiative
- **Feature**: Learning Format Selection & Recommendation
- **Based on**: Sachin Kumar Master Thesis (2023) - "Identifying suitable learning formats for Systems Engineering"
- **Integration Target**: SE-QPT (Systems Engineering Qualification Planning Tool)
- **Author**: Jomon George (Master Thesis - SE-QPT)
- **Date**: December 2025

---

## 1. Module Overview

### 1.1 Purpose
This module recommends suitable Learning Formats (LFs) for Systems Engineering qualification based on:
- Company's selected Qualification Archetype (from Phase 1)
- Identified Competency Gaps (from Phase 2)
- Generated Learning Objectives (from Phase 2)
- User-specified constraints (participants, budget, time, delivery mode)

### 1.2 Position in SE-QPT Workflow
```
Phase 1: Prepare SE Training
    ↓ Outputs: Maturity Level, Role Clusters, Qualification Archetype
Phase 2: Determine Requirements & Competencies  
    ↓ Outputs: Competency Gaps, Learning Objectives
Phase 3: Macro-planning of SE Training Initiative  ← THIS MODULE
    ↓ Outputs: Recommended Learning Formats, Learning Arrangement, Module Selection
Phase 4: Micro-planning of SE Training Initiative
    → Outputs: Detailed Concept, Implementation Plan
```

---

## 2. Data Models

### 2.1 Learning Format Entity

```typescript
interface LearningFormat {
  id: string;
  name: string;
  description: string;
  
  // Clustering Characteristics
  modeOfDelivery: 'online' | 'offline' | 'hybrid';
  communicationType: 'synchronous' | 'asynchronous' | 'hybrid';
  collaborationType: 'individual' | 'team' | 'group';
  participantRange: ParticipantRange;
  learningType: 'formal' | 'informal' | 'hybrid';
  
  // Effort Metrics (scale 1-5)
  efforts: {
    contentCreation: number;    // 1-5
    contentUpdation: number;    // 1-5
    perTraining: number;        // 1-5
  };
  
  // SE-specific mappings
  competencyAcquisitionLevel: 'recognize' | 'understand' | 'apply' | 'mastery';
  suitableArchetypes: ArchetypeId[];
  seCharacteristicsScores: SECharacteristicsScore;
  competencyScores: CompetencyScore[];
  
  // Advantages and Disadvantages
  advantages: Advantage[];
  disadvantages: Disadvantage[];
  
  // Learning Methods applicable
  learningMethods: LearningMethod[];
}

interface ParticipantRange {
  min: number;
  max: number | 'unlimited';
  category: 'individual' | 'pairs' | 'small_group' | 'medium_group' | 'large_group';
}

interface SECharacteristicsScore {
  mindset: 0 | 2 | 4;
  commitment: 0 | 2 | 4;
  transdisciplinary: 0 | 2 | 4;
  holism: 0 | 2 | 4;
  stakeholderCentricity: 0 | 2 | 4;
}

interface CompetencyScore {
  competencyId: string;
  competencyName: string;
  score: number;  // 0-7 scale from matrix multiplication
}
```

### 2.2 The 10 Learning Formats (Master Data)

```javascript
const LEARNING_FORMATS = [
  {
    id: "seminar",
    name: "Seminar/Instructor Lead Training",
    description: "Face-to-face, in-person training led by trainer(s) with direct interaction. Uses slideshows, videos, storytelling, and lectures customized for target audience.",
    modeOfDelivery: "offline",
    communicationType: "synchronous",
    collaborationType: "group",
    participantRange: { min: 10, max: 100, category: "medium_group" },
    learningType: "formal",
    efforts: { contentCreation: 4, contentUpdation: 4, perTraining: 4 },
    competencyAcquisitionLevel: "apply",
    suitableArchetypes: ["basic_understanding", "se_for_leaders", "make_pilot_project", "need_based_training"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 4,
      transdisciplinary: 4,
      holism: 2,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "direct_feedback", name: "Direct Feedback", description: "Participants can interact with trainer to discuss topics and clear doubts during session" },
      { id: "standardized_content", name: "Standardized Content", description: "Learning material is generally standardized, measured, and tested" },
      { id: "high_interaction", name: "High Interaction", description: "High interaction if group discussions or roleplay are added" }
    ],
    disadvantages: [
      { id: "limited_accessibility", name: "Limited Accessibility", description: "Not suitable for online learners since program is face-to-face" },
      { id: "no_self_paced", name: "Lack of Self-Paced Learning", description: "Follows predetermined schedule with fixed topics and timelines" },
      { id: "travel_expenses", name: "Travel and Expenses", description: "Attendees need to incur travel expenses including transportation, accommodation" }
    ],
    learningMethods: ["presentations", "animations", "videos", "3d_models", "case_studies", "discussions", "lectures", "group_work", "storytelling", "polling", "quizzes"]
  },
  
  {
    id: "webinar",
    name: "Webinar/Live Online Event",
    description: "Online live broadcast at specific time. Interaction via chat, sometimes audio access. Synchronous communication, 30-90 minutes duration, unlimited participants.",
    modeOfDelivery: "online",
    communicationType: "synchronous",
    collaborationType: "group",
    participantRange: { min: 1, max: "unlimited", category: "large_group" },
    learningType: "formal",
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 3 },
    competencyAcquisitionLevel: "understand",
    suitableArchetypes: ["basic_understanding", "se_for_leaders"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 2,
      transdisciplinary: 2,
      holism: 2,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "direct_feedback", name: "Direct Feedback", description: "Participants can engage with trainer to discuss topics and resolve doubts" },
      { id: "global_reach", name: "Global Reach", description: "Can reach global audience, transcending geographical boundaries" },
      { id: "standardized_content", name: "Standardized Content", description: "Learning material is standardized and tested" }
    ],
    disadvantages: [
      { id: "limited_instructors", name: "Limited Instructors", description: "Finding dedicated trainer with appropriate qualifications can be challenging" },
      { id: "low_interaction", name: "Low Interaction", description: "Level of interaction among participants is generally low" },
      { id: "no_self_paced", name: "Lack of Self-Paced Learning", description: "Fixed schedule and timing" }
    ],
    learningMethods: ["presentations", "screen_sharing", "polls", "chat", "q_and_a", "breakout_rooms"]
  },
  
  {
    id: "coaching",
    name: "Coaching",
    description: "Attentive observation of learner's approach with expert assistance through cues. Support gradually fades as learner's competence grows. Includes feedback for external perspective.",
    modeOfDelivery: "hybrid",
    communicationType: "synchronous",
    collaborationType: "individual",
    participantRange: { min: 1, max: 5, category: "small_group" },
    learningType: "formal",
    efforts: { contentCreation: 3, contentUpdation: 2, perTraining: 5 },
    competencyAcquisitionLevel: "mastery",
    suitableArchetypes: ["se_for_leaders", "make_pilot_project", "need_based_training", "train_the_trainer"],
    seCharacteristicsScores: {
      mindset: 4,
      commitment: 4,
      transdisciplinary: 2,
      holism: 2,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "accountability", name: "Accountability", description: "Coaches hold individuals accountable for their actions and commitments" },
      { id: "personalized_guidance", name: "Personalized Guidance", description: "One-on-one support tailored to individual's needs, goals, and challenges" },
      { id: "self_discovery", name: "Self-Discovery", description: "Encourages self-reflection and deeper understanding of strengths and weaknesses" }
    ],
    disadvantages: [
      { id: "gradual_results", name: "Gradual Results", description: "Process takes time and effort, may not provide immediate solutions" },
      { id: "time_intensive", name: "Time Intensive", description: "Requires significant time commitment for both coach and coachee" },
      { id: "limited_instructors", name: "Limited Instructors", description: "Finding qualified coaches can be challenging" }
    ],
    learningMethods: ["one_on_one_sessions", "observation", "feedback", "goal_setting", "action_plans", "reflection_exercises"]
  },
  
  {
    id: "mentoring",
    name: "Mentoring",
    description: "Knowledge acquisition through direct engagement with work-related tasks under experienced colleague mentorship. Provides immediate feedback for continuous improvement.",
    modeOfDelivery: "hybrid",
    communicationType: "synchronous",
    collaborationType: "individual",
    participantRange: { min: 1, max: 3, category: "pairs" },
    learningType: "informal",
    efforts: { contentCreation: 2, contentUpdation: 1, perTraining: 4 },
    competencyAcquisitionLevel: "mastery",
    suitableArchetypes: ["make_pilot_project", "need_based_training", "train_the_trainer"],
    seCharacteristicsScores: {
      mindset: 4,
      commitment: 4,
      transdisciplinary: 0,
      holism: 2,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "successor_training", name: "Successor Training", description: "Aids in succession planning by identifying and preparing future leaders" },
      { id: "personalized_content", name: "Personalized Content", description: "Adapts challenges and resources to individual learners" },
      { id: "self_discovery", name: "Self-Discovery", description: "Encourages reflection and understanding of own capabilities" }
    ],
    disadvantages: [
      { id: "time_intensive", name: "Time Intensive", description: "Requires significant time commitment" },
      { id: "gradual_results", name: "Gradual Results", description: "Results take time to manifest" },
      { id: "limited_mentors", name: "Limited Mentors", description: "Finding suitable experienced mentors can be challenging" }
    ],
    learningMethods: ["shadowing", "on_the_job_learning", "regular_meetings", "career_guidance", "knowledge_transfer"]
  },
  
  {
    id: "wbt",
    name: "Web-Based Training (WBT)",
    description: "Computer-aided multimedia training via internet. Participants can access content at any time and control learning at own pace. Asynchronous, self-directed.",
    modeOfDelivery: "online",
    communicationType: "asynchronous",
    collaborationType: "individual",
    participantRange: { min: 1, max: "unlimited", category: "large_group" },
    learningType: "formal",
    efforts: { contentCreation: 5, contentUpdation: 2, perTraining: 1 },
    competencyAcquisitionLevel: "understand",
    suitableArchetypes: ["continuous_support", "basic_understanding"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 0,
      transdisciplinary: 2,
      holism: 4,
      stakeholderCentricity: 4
    },
    advantages: [
      { id: "tracking_assessment", name: "Allows Tracking and Assessment", description: "Includes tracking features to monitor learner progress and performance" },
      { id: "self_paced", name: "Self-Paced Learning", description: "Learners can pause and return to courses, learning at own pace" },
      { id: "global_reach", name: "Global Reach", description: "Accessible from anywhere with internet connection" }
    ],
    disadvantages: [
      { id: "low_engagement", name: "Low Engagement", description: "May lack interactive or multimedia elements, reducing engagement" },
      { id: "very_low_interaction", name: "Very Low Interaction", description: "Interaction between instructors and participants is very shallow" },
      { id: "limited_guidance", name: "Limited Instructor Guidance", description: "Lacks immediate guidance and support from instructors" }
    ],
    learningMethods: ["video_lessons", "interactive_modules", "quizzes", "progress_tracking", "downloadable_resources", "forums"]
  },
  
  {
    id: "cbt",
    name: "Computer-Based Training (CBT)",
    description: "Computer-assisted multimedia learning program with structured materials. Installed on computer, accessible without internet connection. Self-paced and autonomous.",
    modeOfDelivery: "offline",
    communicationType: "asynchronous",
    collaborationType: "individual",
    participantRange: { min: 1, max: "unlimited", category: "large_group" },
    learningType: "formal",
    efforts: { contentCreation: 5, contentUpdation: 3, perTraining: 1 },
    competencyAcquisitionLevel: "understand",
    suitableArchetypes: ["continuous_support"],
    seCharacteristicsScores: {
      mindset: 0,
      commitment: 0,
      transdisciplinary: 2,
      holism: 2,
      stakeholderCentricity: 4
    },
    advantages: [
      { id: "tracking_assessment", name: "Allows Tracking and Assessment", description: "Includes tracking features for monitoring progress" },
      { id: "self_paced", name: "Self-Paced Learning", description: "Flexible, self-paced learning experience" },
      { id: "global_reach", name: "Global Reach", description: "Can be distributed widely once developed" }
    ],
    disadvantages: [
      { id: "low_engagement", name: "Low Engagement", description: "May lack engaging interactive elements" },
      { id: "very_low_interaction", name: "Very Low Interaction", description: "No real-time interaction with instructors" },
      { id: "technical_issues", name: "Technical Issues", description: "Learning disruptions from software errors or hardware malfunctions" }
    ],
    learningMethods: ["software_simulations", "tutorials", "exercises", "assessments", "multimedia_content"]
  },
  
  {
    id: "game_based",
    name: "Game-Based Learning",
    description: "Integrates game elements (status, levels, bonuses) into learning. Includes gamification, serious gaming, and learning through games. Engaging and interactive.",
    modeOfDelivery: "hybrid",
    communicationType: "synchronous",
    collaborationType: "group",
    participantRange: { min: 5, max: 20, category: "medium_group" },
    learningType: "formal",
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 3 },
    competencyAcquisitionLevel: "apply",
    suitableArchetypes: ["basic_understanding", "se_for_leaders", "make_pilot_project"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 2,
      transdisciplinary: 4,
      holism: 2,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "measurable_outcomes", name: "Measurable Outcomes", description: "Allows measurement of specific learning outcomes and performance improvements" },
      { id: "personalized_content", name: "Personalized Content", description: "Topic-specific games provide interactive platform for learning" },
      { id: "high_interaction", name: "High Interaction", description: "High level of interaction especially in multiplayer games" }
    ],
    disadvantages: [
      { id: "limited_knowledge_transfer", name: "Limited Knowledge Transfer", description: "May prioritize engagement over in-depth content coverage" },
      { id: "high_dev_cost", name: "High Initial Development Cost", description: "Creating high-quality games is expensive and time-consuming" },
      { id: "technical_requirements", name: "Technical Requirements", description: "May require specific hardware or software" }
    ],
    learningMethods: ["simulations", "role_playing", "competitions", "rewards_systems", "scenarios", "team_challenges"]
  },
  
  {
    id: "conference",
    name: "Conference",
    description: "Structured, time-bound gatherings of professionals. Well organized, attended in person with diverse presenters and participants. Fosters knowledge exchange.",
    modeOfDelivery: "offline",
    communicationType: "synchronous",
    collaborationType: "group",
    participantRange: { min: 50, max: "unlimited", category: "large_group" },
    learningType: "formal",
    efforts: { contentCreation: 2, contentUpdation: 2, perTraining: 3 },
    competencyAcquisitionLevel: "recognize",
    suitableArchetypes: ["basic_understanding"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 2,
      transdisciplinary: 2,
      holism: 0,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "new_ideas", name: "Exposure to New Ideas", description: "Showcases innovative ideas, projects, and technologies" },
      { id: "standardized_content", name: "Standardized Content", description: "Presentations are typically well-prepared and reviewed" }
    ],
    disadvantages: [
      { id: "medium_interaction", name: "Medium Interaction", description: "High engagement among participants but limited with presenters" },
      { id: "time_consuming", name: "Time-Consuming", description: "Often spans several days requiring significant time away from work" },
      { id: "travel_expenses", name: "Travel and Expenses", description: "Requires travel and associated costs" }
    ],
    learningMethods: ["keynotes", "presentations", "panel_discussions", "networking", "workshops", "poster_sessions"]
  },
  
  {
    id: "blended",
    name: "Blended Learning",
    description: "Integrates synchronous and asynchronous formats for holistic training. Combines in-person (seminars, coaching) with online (WBT, CBT). Maximizes benefits of e-learning while addressing limitations.",
    modeOfDelivery: "hybrid",
    communicationType: "hybrid",
    collaborationType: "group",
    participantRange: { min: 5, max: 50, category: "medium_group" },
    learningType: "formal",
    efforts: { contentCreation: 5, contentUpdation: 4, perTraining: 4 },
    competencyAcquisitionLevel: "mastery",
    suitableArchetypes: ["basic_understanding", "se_for_leaders", "make_pilot_project", "need_based_training", "train_the_trainer"],
    seCharacteristicsScores: {
      mindset: 4,
      commitment: 4,
      transdisciplinary: 4,
      holism: 4,
      stakeholderCentricity: 4
    },
    advantages: [
      { id: "self_paced_and_interaction", name: "Self-Paced Learning + High Interaction", description: "Combines benefits of both offline and online learning" },
      { id: "standardized_content", name: "Standardized Content", description: "Content is well-structured and tested" }
    ],
    disadvantages: [
      { id: "planning_hurdles", name: "Course Planning Hurdles", description: "Need to balance online and in-person components effectively" },
      { id: "integration_challenges", name: "Integration Challenges", description: "Difficulties incorporating materials into existing LMS or tools" },
      { id: "time_management", name: "Time Management Challenges", description: "Learners may struggle allocating time between online and in-person components" }
    ],
    learningMethods: ["online_modules", "face_to_face_sessions", "virtual_classrooms", "discussion_forums", "project_work", "assessments"]
  },
  
  {
    id: "self_learning",
    name: "Self-Learning",
    description: "Independent, proactive knowledge acquisition beyond formal requirements. Self-directed exploration through online courses, reading, workshops, or seeking mentorship.",
    modeOfDelivery: "hybrid",
    communicationType: "asynchronous",
    collaborationType: "individual",
    participantRange: { min: 1, max: 1, category: "individual" },
    learningType: "informal",
    efforts: { contentCreation: 1, contentUpdation: 1, perTraining: 1 },
    competencyAcquisitionLevel: "understand",
    suitableArchetypes: ["continuous_support"],
    seCharacteristicsScores: {
      mindset: 2,
      commitment: 0,
      transdisciplinary: 0,
      holism: 4,
      stakeholderCentricity: 2
    },
    advantages: [
      { id: "flexibility", name: "Flexibility", description: "Complete flexibility in timing and content selection" },
      { id: "self_directed", name: "Self-Directed", description: "Learner controls entire learning journey" }
    ],
    disadvantages: [
      { id: "lacks_structure", name: "Lacks Structure", description: "No formal curriculum or guidance" },
      { id: "requires_motivation", name: "Requires High Motivation", description: "Success depends on learner's self-discipline" }
    ],
    learningMethods: ["reading", "online_research", "practice_projects", "peer_learning", "experimentation"]
  }
];
```

### 2.3 Qualification Archetypes

```javascript
const QUALIFICATION_ARCHETYPES = [
  {
    id: "basic_understanding",
    name: "Basic Understanding",
    description: "Foundational approach for SE, creating awareness through interdisciplinary exchange, fostering commitment, establishing common language.",
    sePhase: "motivation",
    competencyLevel: "recognize",
    suitableLFs: ["seminar", "webinar", "blended", "game_based"],
    characteristics: ["No prerequisites", "External trainers", "External qualification offerings"]
  },
  {
    id: "se_for_leaders",
    name: "SE for Leaders",
    description: "Concentrates on decision-makers crucial in steering SE adoption. Executives must grasp implications of integrating SE.",
    sePhase: "motivation",
    competencyLevel: "understand",
    suitableLFs: ["seminar", "coaching", "blended", "game_based", "webinar"],
    characteristics: ["For executives and managers", "Simulates development processes"]
  },
  {
    id: "make_pilot_project",
    name: "Make Pilot Project",
    description: "Hands-on qualification with practical application. Trains team to implement pilot SE project while providing foundation.",
    sePhase: "introduction",
    competencyLevel: "apply",
    suitableLFs: ["coaching", "seminar", "mentoring", "blended", "game_based"],
    characteristics: ["Initial topic introduction", "Ongoing coaching", "Certification possible (SE-Zert, C-SEP)"]
  },
  {
    id: "need_based_training",
    name: "Need-Based Project Oriented Training",
    description: "Additional training of specific roles, providing extended project support. Ranges from basic to expert knowledge.",
    sePhase: "introduction",
    competencyLevel: "apply",
    suitableLFs: ["seminar", "coaching", "mentoring", "blended", "wbt"],
    characteristics: ["Role-specific training", "Requires company standards/methods/tools defined", "All team members actively involved"]
  },
  {
    id: "continuous_support",
    name: "Continuous Support",
    description: "Fosters ongoing learning within organizational structure. Assumes self-directed learning with users proactively seeking knowledge.",
    sePhase: "stabilization",
    competencyLevel: "mastery",
    suitableLFs: ["wbt", "cbt", "self_learning"],
    characteristics: ["No learning support from trainers", "FAQs and video-based nuggets", "Majority of employees already qualified"]
  },
  {
    id: "train_the_trainer",
    name: "Train the Trainer",
    description: "Centers on coaches, trainers, and key stakeholders tasked with introducing SE. Includes SE skills, conflict awareness, and didactic skills.",
    sePhase: "stabilization",
    competencyLevel: "mastery",
    suitableLFs: ["coaching", "mentoring", "blended", "seminar"],
    characteristics: ["Trainer certification", "Trainer community building", "Didactic and moderation skills"]
  }
];
```

### 2.4 SE Competencies (Könemann's 16 Competencies)

```javascript
const SE_COMPETENCIES = [
  // Core Competencies
  { id: "systems_thinking", name: "Systems Thinking", category: "core" },
  { id: "lifecycle_consideration", name: "Lifecycle Consideration", category: "core" },
  { id: "customer_value_orientation", name: "Customer/Value Orientation", category: "core" },
  { id: "system_modeling_analysis", name: "System Modeling and Analysis", category: "core" },
  
  // Social/Personal Competencies
  { id: "communication", name: "Communication", category: "social_personal" },
  { id: "leadership", name: "Leadership", category: "social_personal" },
  { id: "self_organisation", name: "Self-Organisation", category: "social_personal" },
  
  // Management Competencies
  { id: "project_management", name: "Project Management", category: "management" },
  { id: "decision_management", name: "Decision Management", category: "management" },
  { id: "information_management", name: "Information Management", category: "management" },
  { id: "configuration_management", name: "Configuration Management", category: "management" },
  
  // Technical Competencies
  { id: "requirements_definition", name: "Requirements Definition", category: "technical" },
  { id: "system_architecting", name: "System Architecting", category: "technical" },
  { id: "ivv", name: "Integration, Verification, Validation", category: "technical" },
  { id: "operation_support", name: "Operation and Support", category: "technical" },
  { id: "agile_methods", name: "Agile Methods", category: "technical" }
];
```

### 2.5 Competency-LF Matrix (Pre-calculated Scores)

```javascript
// Matrix CCo-LF: SE Competencies × Learning Formats
// Scores derived from matrix multiplication (BCo-C × AC-LF) / 10, rounded
const COMPETENCY_LF_MATRIX = {
  "systems_thinking": { seminar: 5, coaching: 5, mentoring: 4, game_based: 4, cbt: 2, conference: 2, wbt: 3, webinar: 3, blended: 6, self_learning: 2 },
  "lifecycle_consideration": { seminar: 4, coaching: 4, mentoring: 3, game_based: 4, cbt: 2, conference: 2, wbt: 3, webinar: 3, blended: 6, self_learning: 2 },
  "customer_value_orientation": { seminar: 3, coaching: 4, mentoring: 4, game_based: 2, cbt: 1, conference: 2, wbt: 2, webinar: 2, blended: 5, self_learning: 2 },
  "system_modeling_analysis": { seminar: 3, coaching: 3, mentoring: 2, game_based: 3, cbt: 2, conference: 2, wbt: 4, webinar: 2, blended: 5, self_learning: 2 },
  "communication": { seminar: 3, coaching: 3, mentoring: 3, game_based: 2, cbt: 1, conference: 2, wbt: 2, webinar: 2, blended: 4, self_learning: 1 },
  "leadership": { seminar: 4, coaching: 4, mentoring: 4, game_based: 4, cbt: 2, conference: 2, wbt: 4, webinar: 3, blended: 6, self_learning: 3 },
  "self_organisation": { seminar: 2, coaching: 2, mentoring: 2, game_based: 1, cbt: 0, conference: 1, wbt: 1, webinar: 1, blended: 2, self_learning: 1 },
  "project_management": { seminar: 5, coaching: 5, mentoring: 4, game_based: 4, cbt: 2, conference: 3, wbt: 4, webinar: 4, blended: 7, self_learning: 3 },
  "decision_management": { seminar: 4, coaching: 4, mentoring: 4, game_based: 3, cbt: 2, conference: 2, wbt: 4, webinar: 3, blended: 6, self_learning: 3 },
  "information_management": { seminar: 2, coaching: 2, mentoring: 2, game_based: 2, cbt: 1, conference: 1, wbt: 2, webinar: 2, blended: 3, self_learning: 2 },
  "configuration_management": { seminar: 4, coaching: 4, mentoring: 3, game_based: 4, cbt: 2, conference: 2, wbt: 3, webinar: 3, blended: 6, self_learning: 2 },
  "requirements_definition": { seminar: 4, coaching: 3, mentoring: 2, game_based: 3, cbt: 3, conference: 2, wbt: 3, webinar: 2, blended: 5, self_learning: 2 },
  "system_architecting": { seminar: 4, coaching: 4, mentoring: 3, game_based: 4, cbt: 3, conference: 2, wbt: 4, webinar: 3, blended: 6, self_learning: 3 },
  "ivv": { seminar: 4, coaching: 3, mentoring: 2, game_based: 3, cbt: 3, conference: 2, wbt: 3, webinar: 2, blended: 5, self_learning: 2 },
  "operation_support": { seminar: 2, coaching: 2, mentoring: 2, game_based: 2, cbt: 2, conference: 2, wbt: 3, webinar: 2, blended: 4, self_learning: 2 },
  "agile_methods": { seminar: 4, coaching: 4, mentoring: 4, game_based: 3, cbt: 2, conference: 3, wbt: 3, webinar: 3, blended: 6, self_learning: 2 }
};
```

---

## 3. Input Requirements

### 3.1 Required Inputs from Previous Phases

```typescript
interface Phase3Input {
  // From Phase 1
  companyMaturityLevel: 1 | 2 | 3 | 4 | 5;
  selectedArchetype: ArchetypeId;
  identifiedRoleClusters: RoleCluster[];
  
  // From Phase 2
  competencyGaps: CompetencyGap[];
  learningObjectives: LearningObjective[];
  targetCompetencies: string[];  // competency IDs that need training
  
  // User Constraints (collected in Phase 3)
  constraints: LFConstraints;
}

interface LFConstraints {
  // Participant Information
  numberOfParticipants: number;
  participantGroupType: 'individual' | 'team' | 'department' | 'organization';
  
  // Delivery Preferences
  preferredDeliveryMode: 'online' | 'offline' | 'hybrid' | 'no_preference';
  availableTimePerWeek: '<2_hours' | '2-5_hours' | '5-10_hours' | '>10_hours';
  trainingDuration: 'short_term' | 'medium_term' | 'long_term';
  
  // Organizational Factors
  learningCulture: 'formal_structured' | 'interactive_collaborative' | 'experiential_hands_on' | 'self_directed';
  technologyInfrastructure: 'basic' | 'standard' | 'advanced' | 'cutting_edge';
  budgetLevel: 'low' | 'medium' | 'high';
  
  // Priority Characteristics (from pairwise comparison)
  seCharacteristicPriorities: {
    mindset: 0 | 1 | 2;
    commitment: 0 | 1 | 2;
    transdisciplinary: 0 | 1 | 2;
    holism: 0 | 1 | 2;
    stakeholderCentricity: 0 | 1 | 2;
  };
  
  // Advantage Priorities (from pairwise comparison)
  advantagePriorities: {
    directFeedback: 0 | 1 | 2;
    globalReach: 0 | 1 | 2;
    selfPacedLearning: 0 | 1 | 2;
    highInteraction: 0 | 1 | 2;
    personalizedGuidance: 0 | 1 | 2;
    trackingAssessment: 0 | 1 | 2;
    standardizedContent: 0 | 1 | 2;
    measurableOutcomes: 0 | 1 | 2;
  };
}
```

### 3.2 Constraint Collection Questionnaire

```javascript
const LF_SELECTION_QUESTIONNAIRE = [
  {
    id: "q1_participants",
    question: "What is the typical group size for your training sessions?",
    options: [
      { value: "1-5", label: "1-5 (Individual/Pairs)" },
      { value: "6-15", label: "6-15 (Small Group)" },
      { value: "16-30", label: "16-30 (Medium Group)" },
      { value: "31-50", label: "31-50 (Large Group)" },
      { value: ">50", label: "More than 50" }
    ],
    weight: 0.20
  },
  {
    id: "q2_delivery",
    question: "What is your preferred learning delivery method?",
    options: [
      { value: "offline", label: "Face-to-face (In-person)" },
      { value: "online", label: "Virtual (Online)" },
      { value: "hybrid", label: "Hybrid (Mixed)" },
      { value: "self_paced", label: "Self-paced (Asynchronous)" }
    ],
    weight: 0.25
  },
  {
    id: "q3_time",
    question: "How much time can employees dedicate to learning activities?",
    options: [
      { value: "<2_hours", label: "Less than 2 hours/week" },
      { value: "2-5_hours", label: "2-5 hours/week" },
      { value: "5-10_hours", label: "5-10 hours/week" },
      { value: ">10_hours", label: "More than 10 hours/week" }
    ],
    weight: 0.15
  },
  {
    id: "q4_culture",
    question: "What is your organization's learning culture preference?",
    options: [
      { value: "formal_structured", label: "Formal Structured (Curriculum-based)" },
      { value: "interactive_collaborative", label: "Interactive Collaborative (Team-based)" },
      { value: "experiential_hands_on", label: "Experiential Hands-on (Project-based)" },
      { value: "self_directed", label: "Self-Directed (Autonomous)" }
    ],
    weight: 0.15
  },
  {
    id: "q5_technology",
    question: "What technology infrastructure is available for learning?",
    options: [
      { value: "basic", label: "Basic (Email/Documents)" },
      { value: "standard", label: "Standard (LMS/Video Conferencing)" },
      { value: "advanced", label: "Advanced (VR/AR/Gaming capabilities)" },
      { value: "cutting_edge", label: "Cutting-edge (AI/Adaptive Learning)" }
    ],
    weight: 0.10
  },
  {
    id: "q6_budget",
    question: "What is your training budget level?",
    options: [
      { value: "low", label: "Low (Minimal investment)" },
      { value: "medium", label: "Medium (Standard training budget)" },
      { value: "high", label: "High (Significant investment possible)" }
    ],
    weight: 0.15
  }
];
```

---

## 4. Recommendation Algorithm

### 4.1 Multi-Factor Scoring Algorithm

```javascript
function calculateLFScore(learningFormat, input) {
  let totalScore = 0;
  const weights = {
    archetypeMatch: 0.25,
    competencyMatch: 0.25,
    constraintMatch: 0.20,
    seCharacteristicMatch: 0.15,
    advantageMatch: 0.15
  };
  
  // Factor 1: Archetype Match (0.25)
  const archetypeScore = calculateArchetypeMatch(learningFormat, input.selectedArchetype);
  totalScore += archetypeScore * weights.archetypeMatch;
  
  // Factor 2: Competency Match (0.25)
  const competencyScore = calculateCompetencyMatch(learningFormat, input.targetCompetencies);
  totalScore += competencyScore * weights.competencyMatch;
  
  // Factor 3: Constraint Match (0.20)
  const constraintScore = calculateConstraintMatch(learningFormat, input.constraints);
  totalScore += constraintScore * weights.constraintMatch;
  
  // Factor 4: SE Characteristic Match (0.15)
  const seCharScore = calculateSECharacteristicMatch(learningFormat, input.constraints.seCharacteristicPriorities);
  totalScore += seCharScore * weights.seCharacteristicMatch;
  
  // Factor 5: Advantage Match (0.15)
  const advantageScore = calculateAdvantageMatch(learningFormat, input.constraints.advantagePriorities);
  totalScore += advantageScore * weights.advantageMatch;
  
  return totalScore;
}

function calculateArchetypeMatch(lf, archetypeId) {
  // Returns 1 if LF is suitable for archetype, 0.5 if partially suitable, 0 if not
  const archetype = QUALIFICATION_ARCHETYPES.find(a => a.id === archetypeId);
  if (archetype.suitableLFs.includes(lf.id)) return 1.0;
  return 0.0;
}

function calculateCompetencyMatch(lf, targetCompetencies) {
  // Average score from competency-LF matrix for target competencies
  let totalScore = 0;
  targetCompetencies.forEach(compId => {
    const score = COMPETENCY_LF_MATRIX[compId][lf.id] || 0;
    totalScore += score / 7;  // Normalize to 0-1 scale (max score is 7)
  });
  return totalScore / targetCompetencies.length;
}

function calculateConstraintMatch(lf, constraints) {
  let score = 0;
  let factors = 0;
  
  // Delivery mode match
  if (constraints.preferredDeliveryMode !== 'no_preference') {
    factors++;
    if (lf.modeOfDelivery === constraints.preferredDeliveryMode || lf.modeOfDelivery === 'hybrid') {
      score += 1;
    }
  }
  
  // Participant count match
  factors++;
  const numParticipants = constraints.numberOfParticipants;
  if (numParticipants >= lf.participantRange.min && 
      (lf.participantRange.max === 'unlimited' || numParticipants <= lf.participantRange.max)) {
    score += 1;
  }
  
  // Learning culture match
  factors++;
  if ((constraints.learningCulture === 'formal_structured' && lf.learningType === 'formal') ||
      (constraints.learningCulture === 'self_directed' && lf.learningType === 'informal') ||
      (constraints.learningCulture === 'interactive_collaborative' && lf.collaborationType !== 'individual') ||
      (constraints.learningCulture === 'experiential_hands_on' && ['coaching', 'mentoring', 'game_based'].includes(lf.id))) {
    score += 1;
  }
  
  // Budget consideration
  factors++;
  const effortSum = lf.efforts.contentCreation + lf.efforts.contentUpdation + lf.efforts.perTraining;
  if ((constraints.budgetLevel === 'low' && effortSum <= 6) ||
      (constraints.budgetLevel === 'medium' && effortSum <= 10) ||
      (constraints.budgetLevel === 'high')) {
    score += 1;
  }
  
  return score / factors;
}

function calculateSECharacteristicMatch(lf, priorities) {
  let weightedScore = 0;
  let totalWeight = 0;
  
  Object.keys(priorities).forEach(char => {
    const priority = priorities[char];
    if (priority > 0) {
      totalWeight += priority;
      const charKey = char.replace(/([A-Z])/g, '_$1').toLowerCase(); // Convert camelCase
      const lfScore = lf.seCharacteristicsScores[charKey] || 0;
      weightedScore += (lfScore / 4) * priority;  // Normalize to 0-1 (max is 4)
    }
  });
  
  return totalWeight > 0 ? weightedScore / totalWeight : 0;
}

function calculateAdvantageMatch(lf, priorities) {
  const advantageMapping = {
    directFeedback: 'direct_feedback',
    globalReach: 'global_reach',
    selfPacedLearning: 'self_paced',
    highInteraction: 'high_interaction',
    personalizedGuidance: 'personalized_guidance',
    trackingAssessment: 'tracking_assessment',
    standardizedContent: 'standardized_content',
    measurableOutcomes: 'measurable_outcomes'
  };
  
  let matchScore = 0;
  let totalWeight = 0;
  
  Object.keys(priorities).forEach(advKey => {
    const priority = priorities[advKey];
    if (priority > 0) {
      totalWeight += priority;
      const mappedId = advantageMapping[advKey];
      if (lf.advantages.some(a => a.id === mappedId)) {
        matchScore += priority;
      }
    }
  });
  
  return totalWeight > 0 ? matchScore / totalWeight : 0;
}
```

### 4.2 Main Recommendation Function

```javascript
function recommendLearningFormats(input) {
  // Step 1: Filter by archetype (hard constraint)
  const archetype = QUALIFICATION_ARCHETYPES.find(a => a.id === input.selectedArchetype);
  const eligibleLFs = LEARNING_FORMATS.filter(lf => archetype.suitableLFs.includes(lf.id));
  
  // Step 2: Score each eligible LF
  const scoredLFs = eligibleLFs.map(lf => ({
    ...lf,
    score: calculateLFScore(lf, input),
    scoreBreakdown: {
      archetype: calculateArchetypeMatch(lf, input.selectedArchetype),
      competency: calculateCompetencyMatch(lf, input.targetCompetencies),
      constraints: calculateConstraintMatch(lf, input.constraints),
      seCharacteristics: calculateSECharacteristicMatch(lf, input.constraints.seCharacteristicPriorities),
      advantages: calculateAdvantageMatch(lf, input.constraints.advantagePriorities)
    }
  }));
  
  // Step 3: Sort by score descending
  scoredLFs.sort((a, b) => b.score - a.score);
  
  // Step 4: Determine learning arrangement
  const learningArrangement = determineLearningArrangement(scoredLFs[0]);
  
  // Step 5: Return top 3 recommendations with details
  return {
    primaryRecommendation: scoredLFs[0],
    alternativeRecommendations: scoredLFs.slice(1, 3),
    learningArrangement: learningArrangement,
    allScores: scoredLFs,
    rationale: generateRationale(scoredLFs[0], input)
  };
}

function determineLearningArrangement(topLF) {
  if (['seminar', 'coaching', 'mentoring', 'game_based', 'conference'].includes(topLF.id)) {
    return 'face_to_face';
  } else if (['wbt', 'cbt', 'webinar'].includes(topLF.id)) {
    return 'e_learning';
  } else {
    return 'blended_learning';
  }
}

function generateRationale(recommendedLF, input) {
  const archetype = QUALIFICATION_ARCHETYPES.find(a => a.id === input.selectedArchetype);
  
  return {
    summary: `${recommendedLF.name} is recommended based on your ${archetype.name} archetype and ${input.targetCompetencies.length} target competencies.`,
    archetypeReason: `Suitable for ${archetype.name} because: ${archetype.characteristics.join(', ')}`,
    competencyReason: `Best supports your target competencies with average score of ${(recommendedLF.scoreBreakdown.competency * 100).toFixed(0)}%`,
    constraintReason: `Matches ${(recommendedLF.scoreBreakdown.constraints * 100).toFixed(0)}% of your organizational constraints`,
    keyAdvantages: recommendedLF.advantages.map(a => a.name),
    keyLimitations: recommendedLF.disadvantages.map(d => d.name),
    suggestedLearningMethods: recommendedLF.learningMethods.slice(0, 5)
  };
}
```

---

## 5. Output Specification

### 5.1 Recommendation Output Structure

```typescript
interface LFRecommendationOutput {
  // Primary Recommendation
  primaryRecommendation: {
    format: LearningFormat;
    score: number;
    scoreBreakdown: ScoreBreakdown;
    rationale: Rationale;
  };
  
  // Alternative Options
  alternativeRecommendations: {
    format: LearningFormat;
    score: number;
    comparisonWithPrimary: string;
  }[];
  
  // Learning Arrangement
  learningArrangement: 'face_to_face' | 'e_learning' | 'blended_learning';
  arrangementDescription: string;
  
  // Implementation Guidance
  implementationGuidance: {
    suggestedLearningMethods: string[];
    estimatedEffort: EffortEstimate;
    keySuccessFactors: string[];
    potentialChallenges: string[];
  };
  
  // Integration with Phase 4
  phase4Inputs: {
    selectedFormat: string;
    learningMethods: string[];
    competencyLevelTargets: CompetencyLevel[];
    estimatedDuration: string;
  };
}
```

### 5.2 Example Output

```json
{
  "primaryRecommendation": {
    "format": {
      "id": "blended",
      "name": "Blended Learning",
      "description": "Integrates synchronous and asynchronous formats..."
    },
    "score": 0.85,
    "scoreBreakdown": {
      "archetype": 1.0,
      "competency": 0.82,
      "constraints": 0.75,
      "seCharacteristics": 0.90,
      "advantages": 0.80
    },
    "rationale": {
      "summary": "Blended Learning is recommended based on your Need-Based Project Oriented Training archetype and 5 target competencies.",
      "archetypeReason": "Suitable for Need-Based Training because: Role-specific training, Requires company standards/methods/tools defined",
      "competencyReason": "Best supports your target competencies with average score of 82%",
      "constraintReason": "Matches 75% of your organizational constraints",
      "keyAdvantages": ["Self-Paced Learning + High Interaction", "Standardized Content"],
      "keyLimitations": ["Course Planning Hurdles", "Integration Challenges"],
      "suggestedLearningMethods": ["online_modules", "face_to_face_sessions", "virtual_classrooms", "discussion_forums", "project_work"]
    }
  },
  "alternativeRecommendations": [
    {
      "format": { "id": "seminar", "name": "Seminar/Instructor Lead Training" },
      "score": 0.72,
      "comparisonWithPrimary": "More suitable for initial introduction but lacks self-paced flexibility"
    },
    {
      "format": { "id": "coaching", "name": "Coaching" },
      "score": 0.68,
      "comparisonWithPrimary": "Better for individual development but limited scalability"
    }
  ],
  "learningArrangement": "blended_learning",
  "arrangementDescription": "Combines face-to-face sessions for interaction with online modules for flexibility",
  "implementationGuidance": {
    "suggestedLearningMethods": ["online_modules", "face_to_face_sessions", "virtual_classrooms", "discussion_forums", "project_work"],
    "estimatedEffort": {
      "contentCreation": "5/5 - High initial investment",
      "contentUpdation": "4/5 - Moderate ongoing effort",
      "perTraining": "4/5 - Significant delivery effort"
    },
    "keySuccessFactors": [
      "Clear integration between online and offline components",
      "Strong LMS support",
      "Dedicated facilitators for both modalities"
    ],
    "potentialChallenges": [
      "Balancing workload between modalities",
      "Technology adoption barriers",
      "Maintaining engagement across formats"
    ]
  },
  "phase4Inputs": {
    "selectedFormat": "blended",
    "learningMethods": ["online_modules", "face_to_face_sessions", "virtual_classrooms", "discussion_forums", "project_work"],
    "competencyLevelTargets": ["apply", "mastery"],
    "estimatedDuration": "medium_term"
  }
}
```

---

## 6. User Interface Components

### 6.1 Phase 3 Page Structure

```
Phase 3: Macro-planning of SE Training
├── Step 3.1: Review Inputs (from Phase 1 & 2)
│   ├── Display Selected Archetype
│   ├── Display Target Competencies
│   └── Display Learning Objectives Summary
│
├── Step 3.2: Collect Training Constraints
│   ├── Participant Information Form
│   ├── Delivery Preferences Form
│   └── Organizational Factors Form
│
├── Step 3.3: Priority Setting
│   ├── SE Characteristics Pairwise Comparison
│   └── Advantage Priorities Selection
│
├── Step 3.4: View Recommendations
│   ├── Primary Recommendation Card (with score breakdown)
│   ├── Alternative Options Cards
│   ├── Learning Arrangement Diagram
│   └── Comparison View (if user wants to compare)
│
├── Step 3.5: Learning Format Details
│   ├── Format Poster View (based on Sachin's design)
│   ├── Learning Methods Selection
│   └── Implementation Guidance
│
└── Step 3.6: Confirm & Proceed to Phase 4
    ├── Selection Summary
    └── Export/Save Configuration
```

### 6.2 Key UI Components

```jsx
// LearningFormatCard.jsx
const LearningFormatCard = ({ format, score, isRecommended }) => (
  <Card className={isRecommended ? "border-primary" : ""}>
    <CardHeader>
      <Badge>{format.modeOfDelivery}</Badge>
      <h3>{format.name}</h3>
      <ProgressBar value={score * 100} label={`${(score * 100).toFixed(0)}% Match`} />
    </CardHeader>
    <CardBody>
      <p>{format.description}</p>
      <ChipGroup>
        {format.advantages.slice(0, 3).map(adv => (
          <Chip color="success" key={adv.id}>{adv.name}</Chip>
        ))}
      </ChipGroup>
    </CardBody>
    <CardFooter>
      <Button onClick={() => viewDetails(format)}>View Details</Button>
      {isRecommended && <Badge color="primary">Recommended</Badge>}
    </CardFooter>
  </Card>
);

// PairwiseComparison.jsx
const PairwiseComparison = ({ items, onComplete }) => {
  // Implement pairwise comparison UI for SE characteristics or advantages
};

// LearningFormatPoster.jsx  
const LearningFormatPoster = ({ format }) => (
  <div className="poster">
    {/* 12 sections as defined by Sachin */}
    <Section1_Header format={format} />
    <Section2_Characteristics format={format} />
    <Section3_Description format={format} />
    <Section4_Advantages format={format} />
    <Section5_Disadvantages format={format} />
    <Section6_Efforts format={format} />
    <Section7_CompetencyAcquisition format={format} />
    <Section8_Archetypes format={format} />
    <Section9_LearningMethods format={format} />
    <Section10_SEUsage format={format} />
    <Section11_Conclusion format={format} />
    <Section12_References format={format} />
  </div>
);
```

---

## 7. Integration Points

### 7.1 Integration with Phase 2 (Competency Assessment)

```javascript
// Receive competency gaps from Derik's Competency Assessor
async function receivePhase2Outputs() {
  const phase2Data = await getPhase2Results();
  
  return {
    competencyGaps: phase2Data.identifiedGaps,  // Array of competency IDs with gap levels
    learningObjectives: phase2Data.generatedObjectives,  // RAG-generated objectives
    targetCompetencies: phase2Data.gaps.filter(g => g.level > 0).map(g => g.competencyId),
    roleClusterMappings: phase2Data.roleMappings
  };
}
```

### 7.2 Integration with Phase 4 (Micro-planning)

```javascript
// Pass selected format and configuration to Phase 4
function preparePhase4Inputs(recommendation, userSelections) {
  return {
    selectedLearningFormat: recommendation.primaryRecommendation.format,
    learningArrangement: recommendation.learningArrangement,
    selectedLearningMethods: userSelections.learningMethods,
    targetCompetencies: userSelections.targetCompetencies,
    estimatedParticipants: userSelections.numberOfParticipants,
    deliveryMode: recommendation.primaryRecommendation.format.modeOfDelivery,
    
    // For AVIVA method in Phase 4
    competencyLevels: determineTargetLevels(userSelections.targetCompetencies),
    suggestedDuration: estimateDuration(recommendation),
    
    // For detailed concept creation
    formatCharacteristics: recommendation.primaryRecommendation.format,
    implementationGuidance: recommendation.implementationGuidance
  };
}
```

### 7.3 Database Schema Additions

```sql
-- Learning Formats Reference Table
CREATE TABLE learning_formats (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    mode_of_delivery VARCHAR(20),
    communication_type VARCHAR(20),
    collaboration_type VARCHAR(20),
    min_participants INT,
    max_participants INT,
    learning_type VARCHAR(20),
    effort_content_creation INT,
    effort_content_updation INT,
    effort_per_training INT,
    competency_acquisition_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LF-Archetype Mapping
CREATE TABLE lf_archetype_mapping (
    lf_id VARCHAR(50) REFERENCES learning_formats(id),
    archetype_id VARCHAR(50),
    suitability VARCHAR(20), -- 'achievable', 'partially_achievable', 'not_achievable'
    PRIMARY KEY (lf_id, archetype_id)
);

-- LF-Competency Scores (Pre-calculated Matrix)
CREATE TABLE lf_competency_scores (
    lf_id VARCHAR(50) REFERENCES learning_formats(id),
    competency_id VARCHAR(50),
    score DECIMAL(3,2),
    PRIMARY KEY (lf_id, competency_id)
);

-- LF-SE Characteristic Scores
CREATE TABLE lf_se_characteristic_scores (
    lf_id VARCHAR(50) REFERENCES learning_formats(id),
    characteristic VARCHAR(50),
    score INT, -- 0, 2, or 4
    PRIMARY KEY (lf_id, characteristic)
);

-- LF Advantages
CREATE TABLE lf_advantages (
    id SERIAL PRIMARY KEY,
    lf_id VARCHAR(50) REFERENCES learning_formats(id),
    advantage_key VARCHAR(50),
    advantage_name VARCHAR(200),
    description TEXT
);

-- LF Disadvantages
CREATE TABLE lf_disadvantages (
    id SERIAL PRIMARY KEY,
    lf_id VARCHAR(50) REFERENCES learning_formats(id),
    disadvantage_key VARCHAR(50),
    disadvantage_name VARCHAR(200),
    description TEXT
);

-- User LF Selections (per qualification project)
CREATE TABLE qualification_lf_selections (
    id SERIAL PRIMARY KEY,
    qualification_project_id INT REFERENCES qualification_projects(id),
    selected_lf_id VARCHAR(50) REFERENCES learning_formats(id),
    recommendation_score DECIMAL(4,3),
    user_overridden BOOLEAN DEFAULT FALSE,
    constraints_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. API Endpoints

```javascript
// GET /api/phase3/learning-formats
// Returns all learning formats with their characteristics

// GET /api/phase3/archetypes
// Returns all qualification archetypes

// POST /api/phase3/recommend
// Body: { projectId, constraints }
// Returns: LFRecommendationOutput

// GET /api/phase3/format/:formatId
// Returns detailed format information (poster data)

// POST /api/phase3/select
// Body: { projectId, selectedFormatId, selectedMethods }
// Saves user selection and prepares Phase 4 inputs

// GET /api/phase3/comparison?formats=seminar,coaching,blended
// Returns side-by-side comparison of specified formats
```

---

## 9. Testing Checklist

- [ ] All 10 learning formats load correctly with complete data
- [ ] Archetype filtering works (only eligible LFs shown)
- [ ] Competency score calculation matches matrix values
- [ ] Constraint matching algorithm produces expected scores
- [ ] Pairwise comparison UI functions correctly
- [ ] Recommendation ranking is consistent and logical
- [ ] Learning arrangement determination is accurate
- [ ] Format poster displays all 12 sections correctly
- [ ] Phase 2 inputs are correctly received
- [ ] Phase 4 outputs are correctly formatted
- [ ] Database stores and retrieves selections properly
- [ ] API endpoints return expected responses
- [ ] Edge cases handled (no competencies, no constraints)

---

## 10. References

- Kumar, S. (2023). "Identifying suitable learning formats for Systems Engineering" - Master Thesis, Universität Paderborn
- Könemann, U. et al. (2022). "Identification of stakeholder-specific SE competencies for industry"
- Könemann, U. et al. (2023). "Leitfaden zur Systems Engineering Qualifizierung"
- INCOSE SE Competency Framework (2018)
- Bloom's Taxonomy - Adapted SE Competency Levels

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Jomon George | Initial specification based on Sachin Kumar's thesis analysis |
