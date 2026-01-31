-- Migration 022: Phase 4 AVIVA Didactics Tables
-- Created: January 2026
-- Purpose: Add tables for Phase 4 Micro Planning (AVIVA didactics and RFP export)

-- ============================================
-- Table: competency_content_baseline
-- Stores content topics per competency from Excel Column H
-- ============================================
CREATE TABLE IF NOT EXISTS competency_content_baseline (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER REFERENCES competency(id) ON DELETE CASCADE,
    content_topics TEXT[],  -- Array of topic strings
    source VARCHAR(100) DEFAULT 'Qualifizierungsmodule_v4',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(competency_id)
);

COMMENT ON TABLE competency_content_baseline IS 'Baseline content topics per competency for AVIVA generation';
COMMENT ON COLUMN competency_content_baseline.content_topics IS 'Array of topic strings from Excel Column H';

-- ============================================
-- Table: phase4_config
-- Tracks Phase 4 progress per organization
-- ============================================
CREATE TABLE IF NOT EXISTS phase4_config (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    task1_status VARCHAR(20) DEFAULT 'not_started' CHECK (task1_status IN ('not_started', 'in_progress', 'completed')),
    task2_status VARCHAR(20) DEFAULT 'not_started' CHECK (task2_status IN ('not_started', 'in_progress', 'completed')),
    aviva_generation_method VARCHAR(20) CHECK (aviva_generation_method IN ('template', 'genai')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id)
);

COMMENT ON TABLE phase4_config IS 'Phase 4 progress tracking per organization';

-- ============================================
-- Table: phase4_aviva_plan
-- Stores generated AVIVA plans per training module
-- ============================================
CREATE TABLE IF NOT EXISTS phase4_aviva_plan (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    training_module_id INTEGER REFERENCES phase3_training_module(id) ON DELETE CASCADE,
    generated_by VARCHAR(20) CHECK (generated_by IN ('template', 'genai', 'manual')),
    aviva_content JSONB NOT NULL,  -- Full AVIVA plan as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(training_module_id)  -- One AVIVA plan per module
);

COMMENT ON TABLE phase4_aviva_plan IS 'AVIVA didactic plans per training module';
COMMENT ON COLUMN phase4_aviva_plan.aviva_content IS 'JSON structure with module_name, total_duration_minutes, activities array';

-- ============================================
-- Table: phase4_rfp_export
-- Tracks RFP document exports
-- ============================================
CREATE TABLE IF NOT EXISTS phase4_rfp_export (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    export_format VARCHAR(20) CHECK (export_format IN ('excel', 'word', 'both')),
    file_path VARCHAR(500),
    export_data JSONB,  -- Snapshot of data at export time
    include_aviva BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE phase4_rfp_export IS 'RFP document export history';

-- ============================================
-- Insert content baseline data for all 16 competencies
-- Data sourced from Qualifizierungsmodule_v4 Excel Column H
-- ============================================
INSERT INTO competency_content_baseline (competency_id, content_topics, source)
SELECT c.id, topics.content_topics, 'Qualifizierungsmodule_v4'
FROM competency c
JOIN (VALUES
    -- Correct competency names matching database (id order)
    -- 1. Systems Thinking
    ('Systems Thinking', ARRAY[
        'Motivation for SE',
        'Definition of terms (index)',
        'Values of SE',
        'SE process models (V-model)',
        'SE standards',
        'SE mental models'
    ]),
    -- 4. Lifecycle Consideration
    ('Lifecycle Consideration', ARRAY[
        'Life cycle phases',
        'Operating costs during the life cycle',
        'Lifecycle planning',
        'End-of-life considerations'
    ]),
    -- 5. Customer / Value Orientation
    ('Customer / Value Orientation', ARRAY[
        'Agile Manifesto',
        'Customer-centric thinking',
        'Value-driven development',
        'Stakeholder value analysis'
    ]),
    -- 6. Systems Modelling and Analysis
    ('Systems Modelling and Analysis', ARRAY[
        'Model theory',
        'Simulation',
        'Cross-domain vs domain-specific models',
        'Model-based systems engineering (MBSE)'
    ]),
    -- 7. Communication
    ('Communication', ARRAY[
        'Stakeholder-oriented communication',
        'Basics of communication techniques (4 sides model, self-image, external image, Johari window)',
        'Cooperation and personalities',
        'Negotiation technique',
        'Interpersonal communication',
        'Socially competent behavior',
        'Methods of conflict resolution and motivation',
        'Feedback rules and active listening'
    ]),
    -- 8. Leadership
    ('Leadership', ARRAY[
        'Definition of team and team leadership',
        'Phases of team development',
        'Characters in a team (personality models, e.g. Riemann-Thomann)',
        'Characteristics and methods of team leadership',
        'Situational leadership theory',
        'Collaboration - special features and characteristics of a successful team',
        'Leadership styles (Hersey and Blanchard)'
    ]),
    -- 9. Self-Organization
    ('Self-Organization', ARRAY[
        'Own behavior and personal characteristics',
        'Time management',
        'Personal work organization',
        'Goal setting and prioritization',
        'Self-motivation techniques'
    ]),
    -- 10. Project Management
    ('Project Management', ARRAY[
        'Project goals and scope',
        'PSP - Planning projects (WBS)',
        'Work packages',
        'Schedule and budget plan, SE plan',
        'Resources, roles, responsibilities',
        'Release planning',
        'Project structure',
        'Review milestones',
        'Corrective measures and changes',
        'Project completion',
        'Determination of KPIs',
        'Reporting',
        'Evaluation'
    ]),
    -- 11. Decision Management (NOT Decision Making)
    ('Decision Management', ARRAY[
        'Decision strategy',
        'Evaluation of alternatives',
        'Recording the decisions',
        'Risk profiles',
        'Risk identification',
        'Dealing with risks (planning, measures)',
        'Preventive measures',
        'Technological classification in project'
    ]),
    -- 12. Information Management
    ('Information Management', ARRAY[
        'Communication planning',
        'Information distribution',
        'Information storage',
        'Knowledge management systems',
        'Documentation standards'
    ]),
    -- 13. Configuration Management
    ('Configuration Management', ARRAY[
        'Configuration item definition',
        'Create configurations',
        'Configuration control',
        'Configuration control cycle (V&V, evaluation, release)',
        'Configuration documentation',
        'Baselines',
        'Change management'
    ]),
    -- 14. Requirements Definition (NOT Requirements Engineering)
    ('Requirements Definition', ARRAY[
        'The requirements process in the company',
        'Identification and analysis of all stakeholders',
        'Types of requirements and needs',
        'Restrictions from other life cycle phases (V&V, maintenance, etc.)',
        'Requirements for requirements (quality criteria)',
        'Traceability of requirements',
        'Documentation of requirements (ID, text, tool, etc.)',
        'Identification of requirements sources',
        'Hierarchy and derivation of requirements',
        'Elicitation, definition, analysis and evaluation of requirements',
        'Design of scenarios/use cases',
        'Description of end users',
        'Definition of the system boundary',
        'Identification of external interfaces',
        'Black Box consideration',
        'Verification criteria, validation criteria',
        'Influence of constraints on system architecture and design'
    ]),
    -- 15. System Architecting (NOT System Architecture)
    ('System Architecting', ARRAY[
        'The architecture process in the company',
        'Development of functional, logical architecture',
        'Synthesis - deriving the physical architecture from the logical architecture',
        'Assignment of requirements to the architecture incl. derivation of requirements',
        'Further architecture views (security, safety, etc.)',
        'Images of alternatives, selection of alternatives',
        'Criteria for architectures (comparative studies)',
        'Interfaces and interactions between system elements, external systems and peripheral systems',
        'Relationship between functional and physical elements'
    ]),
    -- 16. Integration, Verification, Validation (NOT Integration and Verification)
    ('Integration, Verification, Validation', ARRAY[
        'System integration strategies',
        'Definition of IVV',
        'Verification procedures (system, element, device)',
        'Verification methods',
        'Traceability to requirements',
        'Validation procedures',
        'Corrective actions',
        'Validation methods',
        'V&V in the phases of the life cycle (esp. early phase)',
        'Final acceptance of the system'
    ]),
    -- 17. Operation and Support (NOT Service and Maintenance)
    ('Operation and Support', ARRAY[
        'Operating strategies',
        'Evaluation of operating data',
        'Obtaining and evaluating user feedback',
        'Recording performance data, error messages',
        'Maintenance strategies',
        'Consumables',
        'Maintenance analyses',
        'Continue and reuse',
        'Deactivation, decommissioning',
        'Disposal strategy'
    ]),
    -- 18. Agile Methods
    ('Agile Methods', ARRAY[
        'Scrum framework',
        'SAFe (Scaled Agile Framework)',
        'Agile values and principles',
        'Sprint planning and retrospectives',
        'Agile in hardware/systems context'
    ])
) AS topics(competency_name, content_topics)
ON c.competency_name = topics.competency_name
ON CONFLICT (competency_id) DO UPDATE
SET content_topics = EXCLUDED.content_topics,
    source = EXCLUDED.source;

-- ============================================
-- Create indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_phase4_aviva_plan_org ON phase4_aviva_plan(organization_id);
CREATE INDEX IF NOT EXISTS idx_phase4_aviva_plan_module ON phase4_aviva_plan(training_module_id);
CREATE INDEX IF NOT EXISTS idx_phase4_rfp_export_org ON phase4_rfp_export(organization_id);

-- ============================================
-- Add trigger for updated_at on phase4_aviva_plan
-- ============================================
CREATE OR REPLACE FUNCTION update_phase4_aviva_plan_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_phase4_aviva_plan_timestamp ON phase4_aviva_plan;
CREATE TRIGGER trigger_update_phase4_aviva_plan_timestamp
    BEFORE UPDATE ON phase4_aviva_plan
    FOR EACH ROW
    EXECUTE FUNCTION update_phase4_aviva_plan_timestamp();

-- ============================================
-- Add trigger for updated_at on phase4_config
-- ============================================
CREATE OR REPLACE FUNCTION update_phase4_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_phase4_config_timestamp ON phase4_config;
CREATE TRIGGER trigger_update_phase4_config_timestamp
    BEFORE UPDATE ON phase4_config
    FOR EACH ROW
    EXECUTE FUNCTION update_phase4_config_timestamp();

-- Log migration
DO $$
BEGIN
    RAISE NOTICE '[OK] Migration 022: Phase 4 AVIVA tables created successfully';
END $$;
