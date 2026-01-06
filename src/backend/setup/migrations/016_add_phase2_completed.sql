-- Migration: Add phase2_completed and phase3_completed columns to organization table
-- Date: 2025-01-05
-- Description: Track Phase 2 and Phase 3 completion status in database instead of localStorage

-- Add phase2_completed column if it doesn't exist
ALTER TABLE organization ADD COLUMN IF NOT EXISTS phase2_completed BOOLEAN DEFAULT FALSE;

-- Add phase3_completed column if it doesn't exist
ALTER TABLE organization ADD COLUMN IF NOT EXISTS phase3_completed BOOLEAN DEFAULT FALSE;

-- Update existing organizations that have completed Phase 2
-- (Organizations with completed assessments)
UPDATE organization
SET phase2_completed = TRUE
WHERE id IN (
    SELECT DISTINCT organization_id FROM user_assessment WHERE completed_at IS NOT NULL
)
AND (phase2_completed IS NULL OR phase2_completed = FALSE);

-- Update existing organizations that have completed Phase 3
-- (Organizations with task3_completed in phase3_config)
UPDATE organization
SET phase3_completed = TRUE
WHERE id IN (
    SELECT organization_id FROM phase3_config WHERE task3_completed = TRUE
)
AND (phase3_completed IS NULL OR phase3_completed = FALSE);
