-- Migration 020: Add covered_levels column to organization_existing_trainings
-- Feature: 2-step level differentiation for Existing Training Check (Ulf's request - 13.01.2026)
--
-- Purpose:
--   Allow organizations to specify which levels are covered by existing training
--   for each competency, instead of excluding all levels (1, 2, 4).
--
-- Before: Selecting a competency excludes ALL levels (1, 2, 4)
-- After:  User selects competency, then specifies which levels are covered
--
-- Example:
--   If organization has "Requirements Definition" training at Knowing level only,
--   they set covered_levels = '[1]', so only level 1 is excluded from LO generation,
--   while levels 2 and 4 are still generated.
--
-- Date: 2026-01-18
-- Author: Claude Code

BEGIN;

-- Step 1: Add covered_levels column
-- Stores JSON array of levels covered by existing training, e.g., [1, 2] or [1, 2, 4]
-- Default is all levels [1, 2, 4] for backward compatibility with existing data
ALTER TABLE organization_existing_trainings
ADD COLUMN IF NOT EXISTS covered_levels TEXT DEFAULT '[1, 2, 4]';

-- Step 2: Update existing records to have all levels (maintaining backward compatibility)
UPDATE organization_existing_trainings
SET covered_levels = '[1, 2, 4]'
WHERE covered_levels IS NULL;

-- Step 3: Add comment
COMMENT ON COLUMN organization_existing_trainings.covered_levels IS
'JSON array of competency levels covered by existing training. E.g., [1] = Knowing only, [1,2] = Knowing & Understanding, [1,2,4] = all levels';

COMMIT;

-- Verification
DO $$
DECLARE
    col_exists BOOLEAN;
    rec_count INTEGER;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'organization_existing_trainings'
        AND column_name = 'covered_levels'
    ) INTO col_exists;

    SELECT COUNT(*) INTO rec_count FROM organization_existing_trainings;

    RAISE NOTICE '================================================================';
    RAISE NOTICE '[SUCCESS] Migration 020 completed';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Column covered_levels exists: %', col_exists;
    RAISE NOTICE 'Existing records updated: %', rec_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Existing training now supports level differentiation:';
    RAISE NOTICE '  - [1] = Knowing level only';
    RAISE NOTICE '  - [1, 2] = Knowing and Understanding';
    RAISE NOTICE '  - [1, 2, 4] = All levels (default)';
    RAISE NOTICE '================================================================';
END $$;
