-- ============================================================================
-- Migration 014: Phase 3 - Macro Planning (Learning Formats & Training Clusters)
-- ============================================================================
--
-- Purpose:
--   Create all required tables and seed data for Phase 3 "Macro Planning"
--   which allows organizations to:
--   1. Choose training structure (Competency-Level vs Role-Clustered)
--   2. Select learning formats with 3-factor suitability feedback
--   3. Receive LLM-generated timeline estimates
--
-- Based on:
--   - Phase3_Macro_Planning_Specification_v3.2.md
--   - PHASE3_IMPLEMENTATION_PLAN.md
--   - Meeting Notes 11.12.2025
--
-- Author: SE-QPT Development Team
-- Date: January 2026
--
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1. LEARNING FORMATS TABLE (10 formats from Sachin's thesis)
-- -----------------------------------------------------------------------------
-- Stores the 10 learning format options available for training module selection
-- Each format has properties like max achievable level, participant ranges, etc.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_format (
    id SERIAL PRIMARY KEY,
    format_key VARCHAR(50) UNIQUE NOT NULL,
    format_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50) NOT NULL,
    description TEXT,
    icon VARCHAR(10),  -- Emoji icon for UI display

    -- Delivery characteristics
    mode_of_delivery VARCHAR(20) CHECK (mode_of_delivery IN ('online', 'offline', 'hybrid')),
    communication_type VARCHAR(20) CHECK (communication_type IN ('synchronous', 'asynchronous', 'hybrid')),
    collaboration_type VARCHAR(20) CHECK (collaboration_type IN ('group', 'individual')),
    learning_type VARCHAR(20) CHECK (learning_type IN ('formal', 'informal')),

    -- Participant constraints
    participant_min INTEGER DEFAULT 1,
    participant_max INTEGER,  -- NULL = unlimited

    -- Level constraints
    max_level_achievable INTEGER CHECK (max_level_achievable IN (1, 2, 4, 6)),

    -- Format flags
    is_e_learning BOOLEAN DEFAULT FALSE,
    is_passive BOOLEAN DEFAULT FALSE,
    is_recommended BOOLEAN DEFAULT FALSE,

    -- Effort ratings (1-5 scale)
    effort_content_creation INTEGER CHECK (effort_content_creation BETWEEN 1 AND 5),
    effort_content_update INTEGER CHECK (effort_content_update BETWEEN 1 AND 5),
    effort_per_training INTEGER CHECK (effort_per_training BETWEEN 1 AND 5),

    -- Advantages and disadvantages (stored as JSON arrays)
    advantages TEXT,   -- JSON array
    disadvantages TEXT, -- JSON array

    -- Display order
    display_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE learning_format IS
    'Learning formats available for training module selection in Phase 3';
COMMENT ON COLUMN learning_format.max_level_achievable IS
    'Maximum competency level that can be achieved with this format (1, 2, 4, or 6)';
COMMENT ON COLUMN learning_format.participant_max IS
    'Maximum participants (NULL = unlimited)';

-- -----------------------------------------------------------------------------
-- 2. TRAINING PROGRAM CLUSTERS TABLE (6 clusters)
-- -----------------------------------------------------------------------------
-- These are organizational groupings for structuring training delivery.
-- IMPORTANT: These are NOT the same as the 14 SE Role Clusters used for
-- competency mapping in Phase 1/2.
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS training_program_cluster (
    id SERIAL PRIMARY KEY,
    cluster_key VARCHAR(50) UNIQUE NOT NULL,
    cluster_name VARCHAR(100) NOT NULL,
    training_program_name VARCHAR(100) NOT NULL,  -- e.g., "SE for Engineers"
    description TEXT,
    typical_org_roles TEXT,  -- JSON array of example organization roles
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE training_program_cluster IS
    'Training Program Clusters for Phase 3 Role-Clustered view (NOT the 14 SE Role Clusters)';
COMMENT ON COLUMN training_program_cluster.training_program_name IS
    'Name of the training program (e.g., "SE for Engineers", "SE for Managers")';

-- -----------------------------------------------------------------------------
-- 3. STRATEGY-LEARNING FORMAT MATRIX
-- -----------------------------------------------------------------------------
-- Defines consistency between qualification strategies and learning formats
-- Values: '++' = Highly Recommended, '+' = Partly Recommended, '--' = Not Consistent
-- 7 strategies x 10 formats = 70 entries
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS strategy_learning_format_matrix (
    id SERIAL PRIMARY KEY,
    strategy_template_id INTEGER NOT NULL REFERENCES strategy_template(id),
    learning_format_id INTEGER NOT NULL REFERENCES learning_format(id),
    consistency VARCHAR(5) NOT NULL CHECK (consistency IN ('++', '+', '--')),
    UNIQUE(strategy_template_id, learning_format_id)
);

COMMENT ON TABLE strategy_learning_format_matrix IS
    'Matrix defining how well each learning format aligns with each qualification strategy';
COMMENT ON COLUMN strategy_learning_format_matrix.consistency IS
    '++ = Highly Recommended (green), + = Partly Recommended (yellow), -- = Not Consistent (red)';

-- -----------------------------------------------------------------------------
-- 4. COMPETENCY-LEARNING FORMAT MATRIX
-- -----------------------------------------------------------------------------
-- Defines maximum achievable level per competency per format
-- Values: 0, 1, 2, 4, or 6 (0 = not suitable)
-- 16 competencies x 10 formats = 160 entries
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS competency_learning_format_matrix (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER NOT NULL REFERENCES competency(id),
    learning_format_id INTEGER NOT NULL REFERENCES learning_format(id),
    max_achievable_level INTEGER NOT NULL CHECK (max_achievable_level IN (0, 1, 2, 4, 6)),
    UNIQUE(competency_id, learning_format_id)
);

COMMENT ON TABLE competency_learning_format_matrix IS
    'Matrix defining maximum achievable competency level per learning format';
COMMENT ON COLUMN competency_learning_format_matrix.max_achievable_level IS
    'Maximum level achievable: 0=not suitable, 1=Knowing, 2=Understanding, 4=Applying, 6=Mastering';

-- -----------------------------------------------------------------------------
-- 5. EXTEND ORGANIZATION_ROLE_MAPPINGS WITH TRAINING PROGRAM CLUSTER
-- -----------------------------------------------------------------------------
-- Add training_program_cluster_id to store which Training Program Cluster
-- each organization role maps to (for Phase 3 Role-Clustered view)
-- -----------------------------------------------------------------------------

ALTER TABLE organization_role_mappings
ADD COLUMN IF NOT EXISTS training_program_cluster_id INTEGER REFERENCES training_program_cluster(id);

COMMENT ON COLUMN organization_role_mappings.training_program_cluster_id IS
    'Training Program Cluster for Phase 3 Role-Clustered view (Engineers, Managers, etc.)';

CREATE INDEX IF NOT EXISTS idx_org_role_training_cluster
ON organization_role_mappings(organization_id, training_program_cluster_id);

-- -----------------------------------------------------------------------------
-- 6. PHASE 3 TRAINING MODULE SELECTIONS
-- -----------------------------------------------------------------------------
-- Stores user's learning format selections for each training module
-- One record per competency-level-PMT combination per organization
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS phase3_training_module (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    competency_id INTEGER NOT NULL REFERENCES competency(id),
    target_level INTEGER NOT NULL CHECK (target_level IN (1, 2, 4)),
    pmt_type VARCHAR(20) DEFAULT 'combined' CHECK (pmt_type IN ('process', 'method', 'tool', 'combined')),

    -- Learning format selection
    selected_format_id INTEGER REFERENCES learning_format(id),

    -- Participant estimation
    actual_users_with_gap INTEGER DEFAULT 0,
    estimated_participants INTEGER DEFAULT 0,

    -- 3-Factor suitability feedback
    suitability_factor1_status VARCHAR(10), -- Participant count: green, yellow, red
    suitability_factor1_message TEXT,
    suitability_factor2_status VARCHAR(10), -- Level achievable: green, yellow, red
    suitability_factor2_message TEXT,
    suitability_factor3_status VARCHAR(10), -- Strategy consistency: green, yellow, red
    suitability_factor3_message TEXT,

    -- Confirmation
    confirmed BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(organization_id, competency_id, target_level, pmt_type)
);

COMMENT ON TABLE phase3_training_module IS
    'Stores user learning format selections for Phase 3 training modules';
COMMENT ON COLUMN phase3_training_module.suitability_factor1_status IS
    'Factor 1: Participant count appropriateness (green/yellow/red)';
COMMENT ON COLUMN phase3_training_module.suitability_factor2_status IS
    'Factor 2: Level achievable by format (green/yellow/red)';
COMMENT ON COLUMN phase3_training_module.suitability_factor3_status IS
    'Factor 3: Strategy consistency (green/yellow/red)';

-- Trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS update_phase3_training_module_timestamp ON phase3_training_module;
CREATE TRIGGER update_phase3_training_module_timestamp
    BEFORE UPDATE ON phase3_training_module
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- -----------------------------------------------------------------------------
-- 7. PHASE 3 TIMELINE MILESTONES
-- -----------------------------------------------------------------------------
-- Stores LLM-generated timeline milestones for the training program
-- 5 milestones per organization: Concept Dev Start/End, Pilot Start, Rollout Start/End
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS phase3_timeline (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,

    -- Milestone info
    milestone_order INTEGER NOT NULL CHECK (milestone_order BETWEEN 1 AND 5),
    milestone_name VARCHAR(100) NOT NULL,
    milestone_description TEXT,

    -- Timeline estimates
    estimated_date DATE,
    quarter VARCHAR(10),  -- e.g., "Q2 2026"

    -- Generation metadata
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generation_reasoning TEXT,  -- LLM's explanation for timeline

    -- Generation context (stored for reference)
    generation_context TEXT,  -- JSON of input parameters used

    UNIQUE(organization_id, milestone_order)
);

COMMENT ON TABLE phase3_timeline IS
    'LLM-generated timeline milestones for Phase 3 training programs';
COMMENT ON COLUMN phase3_timeline.milestone_order IS
    '1=Concept Dev Start, 2=Concept Dev End, 3=Pilot Start, 4=Rollout Start, 5=Rollout End';

-- -----------------------------------------------------------------------------
-- 8. PHASE 3 CONFIGURATION
-- -----------------------------------------------------------------------------
-- Stores Phase 3 configuration per organization (selected view, etc.)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS phase3_config (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER UNIQUE NOT NULL REFERENCES organization(id) ON DELETE CASCADE,

    -- Task 1: Training Structure Selection
    selected_view VARCHAR(30) DEFAULT 'competency_level'
        CHECK (selected_view IN ('competency_level', 'role_clustered')),

    -- Scaling information
    actual_assessed_users INTEGER,
    target_group_size INTEGER,
    scaling_factor DECIMAL(10,2),

    -- Progress tracking
    task1_completed BOOLEAN DEFAULT FALSE,
    task2_completed BOOLEAN DEFAULT FALSE,
    task3_completed BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE phase3_config IS
    'Phase 3 configuration and progress tracking per organization';

-- Trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS update_phase3_config_timestamp ON phase3_config;
CREATE TRIGGER update_phase3_config_timestamp
    BEFORE UPDATE ON phase3_config
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- -----------------------------------------------------------------------------
-- INDEXES FOR PERFORMANCE
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_phase3_module_org ON phase3_training_module(organization_id);
CREATE INDEX IF NOT EXISTS idx_phase3_module_format ON phase3_training_module(selected_format_id);
CREATE INDEX IF NOT EXISTS idx_phase3_timeline_org ON phase3_timeline(organization_id);
CREATE INDEX IF NOT EXISTS idx_strategy_lf_matrix_strategy ON strategy_learning_format_matrix(strategy_template_id);
CREATE INDEX IF NOT EXISTS idx_strategy_lf_matrix_format ON strategy_learning_format_matrix(learning_format_id);
CREATE INDEX IF NOT EXISTS idx_competency_lf_matrix_competency ON competency_learning_format_matrix(competency_id);
CREATE INDEX IF NOT EXISTS idx_competency_lf_matrix_format ON competency_learning_format_matrix(learning_format_id);

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SEED: 10 Learning Formats
-- -----------------------------------------------------------------------------
INSERT INTO learning_format (
    format_key, format_name, short_name, description, icon,
    mode_of_delivery, communication_type, collaboration_type, learning_type,
    participant_min, participant_max, max_level_achievable,
    is_e_learning, is_passive, is_recommended,
    effort_content_creation, effort_content_update, effort_per_training,
    advantages, disadvantages, display_order
) VALUES
-- 1. Seminar
('seminar', 'Seminar / Instructor Lead Training', 'Seminar',
 'Face-to-face, in-person training led by trainer(s) with direct interaction.',
 '1F393',  -- graduation cap emoji
 'offline', 'synchronous', 'group', 'formal',
 10, 100, 4,
 false, false, false,
 4, 4, 4,
 '["Direct Feedback", "Standardized Content", "High Interaction", "Networking Opportunities"]',
 '["Limited Accessibility", "No Self-Paced Option", "Travel Expenses", "Schedule Constraints"]',
 1),

-- 2. Webinar
('webinar', 'Webinar / Live Online Event', 'Webinar',
 'Online live broadcast at specific time with chat interaction.',
 '1F4BB',  -- laptop emoji
 'online', 'synchronous', 'group', 'formal',
 1, NULL, 2,
 false, false, false,
 3, 2, 3,
 '["Direct Feedback", "Global Reach", "Cost Effective", "Recording Possible"]',
 '["Low Interaction", "Technical Issues", "No Self-Paced Option", "Time Zone Challenges"]',
 2),

-- 3. Coaching
('coaching', 'Coaching', 'Coaching',
 'Attentive observation of learner with expert assistance and personalized guidance.',
 '1F3AF',  -- target/bullseye emoji
 'hybrid', 'synchronous', 'individual', 'formal',
 1, 5, 6,
 false, false, false,
 3, 2, 5,
 '["Personalized Guidance", "Accountability", "Deep Learning", "Immediate Feedback"]',
 '["Time Intensive", "Limited Scale", "High Cost", "Coach Availability"]',
 3),

-- 4. Mentoring
('mentoring', 'Mentoring', 'Mentoring',
 'Knowledge acquisition through work-related tasks under experienced guidance.',
 '1F91D',  -- handshake emoji
 'hybrid', 'synchronous', 'individual', 'informal',
 1, 3, 6,
 false, false, false,
 2, 1, 4,
 '["Successor Training", "Real-World Learning", "Relationship Building", "Career Development"]',
 '["Gradual Results", "Limited Mentors", "Inconsistent Quality", "Time Commitment"]',
 4),

-- 5. Web-Based Training (WBT)
('wbt', 'Web-Based Training (WBT)', 'WBT',
 'Self-paced online learning modules via internet.',
 '1F310',  -- globe emoji
 'online', 'asynchronous', 'individual', 'formal',
 1, NULL, 2,
 true, false, false,
 5, 2, 1,
 '["Self-Paced", "Scalable", "Progress Tracking", "Accessible Anywhere"]',
 '["Low Engagement", "No Hands-On Practice", "Limited Support", "Requires Self-Discipline"]',
 5),

-- 6. Computer-Based Training (CBT)
('cbt', 'Computer-Based Training (CBT)', 'CBT',
 'Offline self-paced training software, no internet required.',
 '1F4BE',  -- floppy disk emoji
 'offline', 'asynchronous', 'individual', 'formal',
 1, NULL, 2,
 true, false, false,
 5, 3, 1,
 '["Offline Access", "Self-Paced", "Consistent Quality", "No Internet Required"]',
 '["Outdated Content Risk", "Installation Issues", "Low Engagement", "No Real-Time Support"]',
 6),

-- 7. Game-Based Learning
('game_based', 'Game-Based Learning', 'Game-Based',
 'Learning through gamification, serious games, and simulations.',
 '1F3AE',  -- game controller emoji
 'hybrid', 'synchronous', 'group', 'formal',
 5, 20, 4,
 false, false, false,
 5, 4, 3,
 '["High Engagement", "Safe Practice Environment", "Measurable Progress", "Immersive Experience"]',
 '["High Development Cost", "Limited Scale", "Technical Requirements", "Content Constraints"]',
 7),

-- 8. Conference
('conference', 'Conference', 'Conference',
 'Large-scale professional gatherings with presentations and networking.',
 '1F3AA',  -- circus tent emoji
 'offline', 'synchronous', 'group', 'formal',
 50, NULL, 1,
 false, true, false,
 2, 2, 3,
 '["Networking", "Industry Insights", "Inspiration", "Trend Awareness"]',
 '["Passive Learning", "High Cost", "Time Consuming", "Limited Deep Learning"]',
 8),

-- 9. Blended Learning
('blended', 'Blended Learning', 'Blended',
 'Combination of synchronous/asynchronous, in-person/online formats.',
 '1F504',  -- refresh/cycle emoji
 'hybrid', 'hybrid', 'group', 'formal',
 5, 50, 6,
 false, false, true,
 5, 4, 4,
 '["Flexible", "Best of Both Worlds", "Multi-Level Coverage", "Adaptable"]',
 '["Complex Planning", "Integration Challenges", "Resource Intensive", "Coordination Required"]',
 9),

-- 10. Self-Learning
('self_learning', 'Self-Learning', 'Self-Learning',
 'Independent, self-directed knowledge acquisition.',
 '1F4DA',  -- books emoji
 'hybrid', 'asynchronous', 'individual', 'informal',
 1, 1, 2,
 true, false, false,
 1, 1, 1,
 '["Complete Flexibility", "Low Cost", "Self-Directed", "Personalized Pace"]',
 '["No Structure", "No Feedback", "Requires High Motivation", "No Certification"]',
 10)

ON CONFLICT (format_key) DO UPDATE SET
    format_name = EXCLUDED.format_name,
    short_name = EXCLUDED.short_name,
    description = EXCLUDED.description,
    max_level_achievable = EXCLUDED.max_level_achievable,
    participant_min = EXCLUDED.participant_min,
    participant_max = EXCLUDED.participant_max,
    is_e_learning = EXCLUDED.is_e_learning,
    is_passive = EXCLUDED.is_passive,
    is_recommended = EXCLUDED.is_recommended;

-- -----------------------------------------------------------------------------
-- SEED: 6 Training Program Clusters
-- -----------------------------------------------------------------------------
INSERT INTO training_program_cluster (
    id, cluster_key, cluster_name, training_program_name, description, typical_org_roles, display_order
) VALUES
(1, 'engineers', 'Engineers', 'SE for Engineers',
 'Technical practitioners who design, develop, and implement systems',
 '["Software Engineers", "Hardware Engineers", "System Engineers", "Test Engineers", "Requirements Engineers", "System Architects"]',
 1),

(2, 'managers', 'Managers', 'SE for Managers',
 'Leadership roles responsible for planning, coordination, and decision-making',
 '["Project Managers", "Department Heads", "Team Leads", "Product Managers", "Program Managers"]',
 2),

(3, 'executives', 'Executives', 'SE for Executives',
 'Senior leadership with strategic oversight',
 '["Directors", "VPs", "C-Level Executives", "Senior Management"]',
 3),

(4, 'support_staff', 'Support Staff', 'SE for Support Staff',
 'Roles providing technical and operational support',
 '["Quality Engineers", "Configuration Managers", "IT Support", "Documentation Specialists"]',
 4),

(5, 'external_partners', 'External Partners', 'SE for Partners',
 'Customer-facing and supplier-facing roles',
 '["Customer Representatives", "Account Managers", "Supplier Managers", "Sales Engineers"]',
 5),

(6, 'operations', 'Operations', 'SE for Operations',
 'Roles focused on production, deployment, and maintenance',
 '["Production Engineers", "Service Technicians", "Field Engineers", "Operations Staff"]',
 6)

ON CONFLICT (id) DO UPDATE SET
    cluster_key = EXCLUDED.cluster_key,
    cluster_name = EXCLUDED.cluster_name,
    training_program_name = EXCLUDED.training_program_name,
    description = EXCLUDED.description,
    typical_org_roles = EXCLUDED.typical_org_roles;

-- Reset sequence for training_program_cluster
SELECT setval('training_program_cluster_id_seq', 6, true);

-- -----------------------------------------------------------------------------
-- SEED: Strategy-Learning Format Matrix (7 strategies x 10 formats = 70 entries)
-- -----------------------------------------------------------------------------
-- Strategy IDs from strategy_template table:
-- 1 = Common basic understanding
-- 2 = SE for managers
-- 3 = Orientation in pilot project
-- 4 = Needs-based, project-oriented training
-- 5 = Continuous support
-- 6 = Train the trainer
-- 7 = Certification
--
-- Values: '++' = Highly Recommended, '+' = Partly Recommended, '--' = Not Consistent
-- -----------------------------------------------------------------------------

-- Get format IDs dynamically
DO $$
DECLARE
    fmt_seminar INTEGER;
    fmt_webinar INTEGER;
    fmt_coaching INTEGER;
    fmt_mentoring INTEGER;
    fmt_wbt INTEGER;
    fmt_cbt INTEGER;
    fmt_game_based INTEGER;
    fmt_conference INTEGER;
    fmt_blended INTEGER;
    fmt_self_learning INTEGER;
BEGIN
    -- Get format IDs
    SELECT id INTO fmt_seminar FROM learning_format WHERE format_key = 'seminar';
    SELECT id INTO fmt_webinar FROM learning_format WHERE format_key = 'webinar';
    SELECT id INTO fmt_coaching FROM learning_format WHERE format_key = 'coaching';
    SELECT id INTO fmt_mentoring FROM learning_format WHERE format_key = 'mentoring';
    SELECT id INTO fmt_wbt FROM learning_format WHERE format_key = 'wbt';
    SELECT id INTO fmt_cbt FROM learning_format WHERE format_key = 'cbt';
    SELECT id INTO fmt_game_based FROM learning_format WHERE format_key = 'game_based';
    SELECT id INTO fmt_conference FROM learning_format WHERE format_key = 'conference';
    SELECT id INTO fmt_blended FROM learning_format WHERE format_key = 'blended';
    SELECT id INTO fmt_self_learning FROM learning_format WHERE format_key = 'self_learning';

    -- Strategy 1: Common basic understanding
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (1, fmt_seminar, '++'), (1, fmt_webinar, '+'), (1, fmt_coaching, '--'), (1, fmt_mentoring, '--'),
    (1, fmt_wbt, '--'), (1, fmt_cbt, '--'), (1, fmt_game_based, '+'), (1, fmt_conference, '+'),
    (1, fmt_blended, '++'), (1, fmt_self_learning, '--')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 2: SE for managers
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (2, fmt_seminar, '++'), (2, fmt_webinar, '+'), (2, fmt_coaching, '++'), (2, fmt_mentoring, '++'),
    (2, fmt_wbt, '+'), (2, fmt_cbt, '--'), (2, fmt_game_based, '+'), (2, fmt_conference, '+'),
    (2, fmt_blended, '++'), (2, fmt_self_learning, '--')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 3: Orientation in pilot project
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (3, fmt_seminar, '++'), (3, fmt_webinar, '+'), (3, fmt_coaching, '++'), (3, fmt_mentoring, '++'),
    (3, fmt_wbt, '--'), (3, fmt_cbt, '--'), (3, fmt_game_based, '++'), (3, fmt_conference, '--'),
    (3, fmt_blended, '++'), (3, fmt_self_learning, '--')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 4: Needs-based, project-oriented training
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (4, fmt_seminar, '++'), (4, fmt_webinar, '+'), (4, fmt_coaching, '+'), (4, fmt_mentoring, '+'),
    (4, fmt_wbt, '+'), (4, fmt_cbt, '+'), (4, fmt_game_based, '+'), (4, fmt_conference, '--'),
    (4, fmt_blended, '++'), (4, fmt_self_learning, '+')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 5: Continuous support
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (5, fmt_seminar, '+'), (5, fmt_webinar, '++'), (5, fmt_coaching, '+'), (5, fmt_mentoring, '+'),
    (5, fmt_wbt, '++'), (5, fmt_cbt, '++'), (5, fmt_game_based, '+'), (5, fmt_conference, '++'),
    (5, fmt_blended, '+'), (5, fmt_self_learning, '++')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 6: Train the trainer
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (6, fmt_seminar, '+'), (6, fmt_webinar, '+'), (6, fmt_coaching, '++'), (6, fmt_mentoring, '++'),
    (6, fmt_wbt, '+'), (6, fmt_cbt, '+'), (6, fmt_game_based, '+'), (6, fmt_conference, '--'),
    (6, fmt_blended, '+'), (6, fmt_self_learning, '+')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    -- Strategy 7: Certification
    INSERT INTO strategy_learning_format_matrix (strategy_template_id, learning_format_id, consistency) VALUES
    (7, fmt_seminar, '+'), (7, fmt_webinar, '+'), (7, fmt_coaching, '+'), (7, fmt_mentoring, '+'),
    (7, fmt_wbt, '+'), (7, fmt_cbt, '+'), (7, fmt_game_based, '--'), (7, fmt_conference, '+'),
    (7, fmt_blended, '+'), (7, fmt_self_learning, '+')
    ON CONFLICT (strategy_template_id, learning_format_id) DO UPDATE SET consistency = EXCLUDED.consistency;

    RAISE NOTICE '[OK] Strategy-Learning Format Matrix populated (70 entries)';
END $$;

-- -----------------------------------------------------------------------------
-- SEED: Competency-Learning Format Matrix (16 competencies x 10 formats = 160 entries)
-- -----------------------------------------------------------------------------
-- Competency IDs from competency table:
-- 1 = Systems Thinking, 4 = Lifecycle, 5 = Customer/Value, 6 = Systems Modelling
-- 7 = Communication, 8 = Leadership, 9 = Self-Organization
-- 10 = Project Mgmt, 11 = Decision Mgmt, 12 = Info Mgmt, 13 = Config Mgmt
-- 14 = Requirements Def, 15 = System Architecting, 16 = IVV, 17 = Operation/Support
-- 18 = Agile Methods
--
-- Values: Maximum achievable level (0, 1, 2, 4, or 6)
-- Core competencies (1, 4, 5, 6) have lower achievable levels - these are experience-based
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    fmt_seminar INTEGER;
    fmt_webinar INTEGER;
    fmt_coaching INTEGER;
    fmt_mentoring INTEGER;
    fmt_wbt INTEGER;
    fmt_cbt INTEGER;
    fmt_game_based INTEGER;
    fmt_conference INTEGER;
    fmt_blended INTEGER;
    fmt_self_learning INTEGER;
BEGIN
    -- Get format IDs
    SELECT id INTO fmt_seminar FROM learning_format WHERE format_key = 'seminar';
    SELECT id INTO fmt_webinar FROM learning_format WHERE format_key = 'webinar';
    SELECT id INTO fmt_coaching FROM learning_format WHERE format_key = 'coaching';
    SELECT id INTO fmt_mentoring FROM learning_format WHERE format_key = 'mentoring';
    SELECT id INTO fmt_wbt FROM learning_format WHERE format_key = 'wbt';
    SELECT id INTO fmt_cbt FROM learning_format WHERE format_key = 'cbt';
    SELECT id INTO fmt_game_based FROM learning_format WHERE format_key = 'game_based';
    SELECT id INTO fmt_conference FROM learning_format WHERE format_key = 'conference';
    SELECT id INTO fmt_blended FROM learning_format WHERE format_key = 'blended';
    SELECT id INTO fmt_self_learning FROM learning_format WHERE format_key = 'self_learning';

    -- CORE COMPETENCIES (harder to achieve, experience-based)

    -- 1: Systems Thinking
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (1, fmt_seminar, 2), (1, fmt_webinar, 2), (1, fmt_coaching, 4), (1, fmt_mentoring, 4),
    (1, fmt_wbt, 2), (1, fmt_cbt, 1), (1, fmt_game_based, 2), (1, fmt_conference, 1),
    (1, fmt_blended, 4), (1, fmt_self_learning, 1)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 4: Lifecycle Consideration
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (4, fmt_seminar, 2), (4, fmt_webinar, 2), (4, fmt_coaching, 4), (4, fmt_mentoring, 4),
    (4, fmt_wbt, 2), (4, fmt_cbt, 1), (4, fmt_game_based, 2), (4, fmt_conference, 1),
    (4, fmt_blended, 4), (4, fmt_self_learning, 1)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 5: Customer / Value Orientation
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (5, fmt_seminar, 2), (5, fmt_webinar, 2), (5, fmt_coaching, 4), (5, fmt_mentoring, 6),
    (5, fmt_wbt, 2), (5, fmt_cbt, 1), (5, fmt_game_based, 2), (5, fmt_conference, 1),
    (5, fmt_blended, 4), (5, fmt_self_learning, 1)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 6: Systems Modelling and Analysis
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (6, fmt_seminar, 4), (6, fmt_webinar, 2), (6, fmt_coaching, 4), (6, fmt_mentoring, 4),
    (6, fmt_wbt, 2), (6, fmt_cbt, 2), (6, fmt_game_based, 4), (6, fmt_conference, 1),
    (6, fmt_blended, 6), (6, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- SOCIAL/PERSONAL COMPETENCIES

    -- 7: Communication
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (7, fmt_seminar, 4), (7, fmt_webinar, 2), (7, fmt_coaching, 6), (7, fmt_mentoring, 4),
    (7, fmt_wbt, 2), (7, fmt_cbt, 1), (7, fmt_game_based, 4), (7, fmt_conference, 2),
    (7, fmt_blended, 4), (7, fmt_self_learning, 1)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 8: Leadership
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (8, fmt_seminar, 2), (8, fmt_webinar, 2), (8, fmt_coaching, 6), (8, fmt_mentoring, 6),
    (8, fmt_wbt, 2), (8, fmt_cbt, 1), (8, fmt_game_based, 4), (8, fmt_conference, 2),
    (8, fmt_blended, 6), (8, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 9: Self-Organization
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (9, fmt_seminar, 2), (9, fmt_webinar, 1), (9, fmt_coaching, 4), (9, fmt_mentoring, 4),
    (9, fmt_wbt, 1), (9, fmt_cbt, 1), (9, fmt_game_based, 2), (9, fmt_conference, 1),
    (9, fmt_blended, 4), (9, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- MANAGEMENT COMPETENCIES

    -- 10: Project Management
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (10, fmt_seminar, 4), (10, fmt_webinar, 2), (10, fmt_coaching, 4), (10, fmt_mentoring, 4),
    (10, fmt_wbt, 2), (10, fmt_cbt, 2), (10, fmt_game_based, 4), (10, fmt_conference, 2),
    (10, fmt_blended, 6), (10, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 11: Decision Management
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (11, fmt_seminar, 4), (11, fmt_webinar, 2), (11, fmt_coaching, 6), (11, fmt_mentoring, 6),
    (11, fmt_wbt, 2), (11, fmt_cbt, 2), (11, fmt_game_based, 4), (11, fmt_conference, 2),
    (11, fmt_blended, 6), (11, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 12: Information Management
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (12, fmt_seminar, 4), (12, fmt_webinar, 2), (12, fmt_coaching, 4), (12, fmt_mentoring, 4),
    (12, fmt_wbt, 2), (12, fmt_cbt, 2), (12, fmt_game_based, 2), (12, fmt_conference, 1),
    (12, fmt_blended, 4), (12, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 13: Configuration Management
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (13, fmt_seminar, 4), (13, fmt_webinar, 2), (13, fmt_coaching, 4), (13, fmt_mentoring, 4),
    (13, fmt_wbt, 2), (13, fmt_cbt, 2), (13, fmt_game_based, 4), (13, fmt_conference, 2),
    (13, fmt_blended, 6), (13, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- TECHNICAL COMPETENCIES

    -- 14: Requirements Definition
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (14, fmt_seminar, 4), (14, fmt_webinar, 2), (14, fmt_coaching, 4), (14, fmt_mentoring, 4),
    (14, fmt_wbt, 2), (14, fmt_cbt, 2), (14, fmt_game_based, 4), (14, fmt_conference, 2),
    (14, fmt_blended, 6), (14, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 15: System Architecting
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (15, fmt_seminar, 4), (15, fmt_webinar, 2), (15, fmt_coaching, 4), (15, fmt_mentoring, 6),
    (15, fmt_wbt, 2), (15, fmt_cbt, 2), (15, fmt_game_based, 4), (15, fmt_conference, 2),
    (15, fmt_blended, 6), (15, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 16: Integration, Verification, Validation
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (16, fmt_seminar, 4), (16, fmt_webinar, 2), (16, fmt_coaching, 4), (16, fmt_mentoring, 4),
    (16, fmt_wbt, 2), (16, fmt_cbt, 2), (16, fmt_game_based, 4), (16, fmt_conference, 2),
    (16, fmt_blended, 6), (16, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 17: Operation and Support
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (17, fmt_seminar, 4), (17, fmt_webinar, 2), (17, fmt_coaching, 4), (17, fmt_mentoring, 4),
    (17, fmt_wbt, 2), (17, fmt_cbt, 2), (17, fmt_game_based, 2), (17, fmt_conference, 2),
    (17, fmt_blended, 4), (17, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    -- 18: Agile Methods
    INSERT INTO competency_learning_format_matrix (competency_id, learning_format_id, max_achievable_level) VALUES
    (18, fmt_seminar, 4), (18, fmt_webinar, 2), (18, fmt_coaching, 4), (18, fmt_mentoring, 4),
    (18, fmt_wbt, 2), (18, fmt_cbt, 2), (18, fmt_game_based, 4), (18, fmt_conference, 2),
    (18, fmt_blended, 6), (18, fmt_self_learning, 2)
    ON CONFLICT (competency_id, learning_format_id) DO UPDATE SET max_achievable_level = EXCLUDED.max_achievable_level;

    RAISE NOTICE '[OK] Competency-Learning Format Matrix populated (160 entries)';
END $$;

-- -----------------------------------------------------------------------------
-- GRANT PERMISSIONS
-- -----------------------------------------------------------------------------

GRANT SELECT, INSERT, UPDATE, DELETE ON learning_format TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON training_program_cluster TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON strategy_learning_format_matrix TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON competency_learning_format_matrix TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON phase3_training_module TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON phase3_timeline TO seqpt_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON phase3_config TO seqpt_admin;

GRANT USAGE, SELECT ON SEQUENCE learning_format_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE training_program_cluster_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE strategy_learning_format_matrix_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE competency_learning_format_matrix_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE phase3_training_module_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE phase3_timeline_id_seq TO seqpt_admin;
GRANT USAGE, SELECT ON SEQUENCE phase3_config_id_seq TO seqpt_admin;

-- -----------------------------------------------------------------------------
-- VERIFICATION QUERIES
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    lf_count INTEGER;
    tpc_count INTEGER;
    slf_count INTEGER;
    clf_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO lf_count FROM learning_format;
    SELECT COUNT(*) INTO tpc_count FROM training_program_cluster;
    SELECT COUNT(*) INTO slf_count FROM strategy_learning_format_matrix;
    SELECT COUNT(*) INTO clf_count FROM competency_learning_format_matrix;

    RAISE NOTICE '================================================================';
    RAISE NOTICE '[SUCCESS] Migration 014 completed successfully';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - learning_format (% rows)', lf_count;
    RAISE NOTICE '  - training_program_cluster (% rows)', tpc_count;
    RAISE NOTICE '  - strategy_learning_format_matrix (% rows)', slf_count;
    RAISE NOTICE '  - competency_learning_format_matrix (% rows)', clf_count;
    RAISE NOTICE '  - phase3_training_module (empty, ready for use)';
    RAISE NOTICE '  - phase3_timeline (empty, ready for use)';
    RAISE NOTICE '  - phase3_config (empty, ready for use)';
    RAISE NOTICE '';
    RAISE NOTICE 'Columns added:';
    RAISE NOTICE '  - organization_role_mappings.training_program_cluster_id';
    RAISE NOTICE '';
    RAISE NOTICE 'Expected counts:';
    RAISE NOTICE '  - learning_format: 10';
    RAISE NOTICE '  - training_program_cluster: 6';
    RAISE NOTICE '  - strategy_learning_format_matrix: 70 (7 strategies x 10 formats)';
    RAISE NOTICE '  - competency_learning_format_matrix: 160 (16 competencies x 10 formats)';
    RAISE NOTICE '================================================================';
END $$;
