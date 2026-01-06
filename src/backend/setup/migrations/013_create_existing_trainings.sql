-- Migration 013: Create organization_existing_trainings table
-- Feature: "Check and Integrate Existing Offers" (Ulf's request - 11.12.2025)
--
-- Purpose:
--   Allow organizations to mark competencies that already have existing training programs.
--   These competencies are excluded from "Training Requirements Identified" and shown
--   in "No Training Required" with "Training Exists" tag.
--
-- Affects: All levels (1, 2, 4) of selected competencies are excluded from LO generation
--
-- Date: 2025-12-11
-- Author: Claude Code

-- Create the table
CREATE TABLE IF NOT EXISTS organization_existing_trainings (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
    competency_id INTEGER NOT NULL REFERENCES competency(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    notes TEXT,

    -- Unique constraint: one entry per org-competency pair
    CONSTRAINT unique_org_competency_training UNIQUE (organization_id, competency_id)
);

-- Create index for faster lookups by organization
CREATE INDEX IF NOT EXISTS idx_existing_trainings_org
ON organization_existing_trainings(organization_id);

-- Add comment to table
COMMENT ON TABLE organization_existing_trainings IS
'Stores competencies for which organization has existing training programs.
These are excluded from LO generation and shown with "Training Exists" tag.';

COMMENT ON COLUMN organization_existing_trainings.organization_id IS 'FK to organization table';
COMMENT ON COLUMN organization_existing_trainings.competency_id IS 'FK to competency table (1-18)';
COMMENT ON COLUMN organization_existing_trainings.created_by IS 'Username who marked this competency';
COMMENT ON COLUMN organization_existing_trainings.notes IS 'Optional notes about the existing training program';

-- Verification query (optional - run to confirm table created)
-- SELECT table_name, column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'organization_existing_trainings';
