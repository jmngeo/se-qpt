-- Migration 018: Consolidate 6 training program clusters to 3
-- Date: 2026-01-18
-- Reason: Ulf's requirement from 13.01.2026 meeting
--
-- Before: Engineers, Managers, Executives, Support Staff, External Partners, Operations (6 clusters)
-- After: Engineers, Managers, Interfacing Partners (3 clusters)
--
-- Mapping:
--   1 (Engineers) -> 1 (Engineers) - unchanged
--   2 (Managers) -> 2 (Managers) - unchanged
--   3 (Executives) -> 2 (Managers) - absorbed into Managers
--   4 (Support Staff) -> 3 (Interfacing Partners) - consolidated
--   5 (External Partners) -> 3 (Interfacing Partners) - consolidated
--   6 (Operations) -> 3 (Interfacing Partners) - consolidated

BEGIN;

-- Step 1: Update organization_roles to map old clusters to new
-- Executives (3) -> Managers (2)
UPDATE organization_roles
SET training_program_cluster_id = 2
WHERE training_program_cluster_id = 3;

-- Support Staff, External Partners, Operations (4, 5, 6) -> will become Interfacing Partners (3)
-- First map them to temporary ID (use 3 since we'll rename cluster 3)
UPDATE organization_roles
SET training_program_cluster_id = 3
WHERE training_program_cluster_id IN (4, 5, 6);

-- Step 2: Update the cluster table itself
UPDATE training_program_cluster
SET cluster_name = 'Engineers',
    cluster_key = 'engineers',
    training_program_name = 'SE for Engineers',
    description = 'Roles requiring Level 4+ competency development in Technical or Core areas',
    typical_org_roles = '["Software Engineers", "Hardware Engineers", "System Engineers", "Test Engineers", "Requirements Engineers", "System Architects"]'
WHERE id = 1;

UPDATE training_program_cluster
SET cluster_name = 'Managers',
    cluster_key = 'managers',
    training_program_name = 'SE for Managers',
    description = 'Roles requiring Level 4+ competency development only in Social/Personal or Management areas (not Technical/Core)',
    typical_org_roles = '["Project Managers", "Department Heads", "Team Leads", "Product Managers", "Program Managers", "Directors", "Executives"]'
WHERE id = 2;

UPDATE training_program_cluster
SET cluster_name = 'Interfacing Partners',
    cluster_key = 'interfacing_partners',
    training_program_name = 'SE for Interfacing Partners',
    description = 'Roles requiring only Level 1-2 competency (basic awareness and understanding)',
    typical_org_roles = '["Support Staff", "Quality Engineers", "Configuration Managers", "Customer Representatives", "Operations Staff", "Field Engineers"]'
WHERE id = 3;

-- Step 3: Delete old clusters (4, 5, 6) - they have been mapped to clusters 2 and 3
DELETE FROM training_program_cluster WHERE id > 3;

-- Step 4: Reset any role assignments - they will be recalculated based on gaps
-- during the next Learning Objectives generation
-- NOTE: We keep existing assignments as fallback; the new assignment logic
-- will overwrite them during LO generation when gaps are calculated.
-- This ensures backward compatibility.

COMMIT;

-- Verification
DO $$
DECLARE
    cluster_count INTEGER;
    roles_in_1 INTEGER;
    roles_in_2 INTEGER;
    roles_in_3 INTEGER;
BEGIN
    SELECT COUNT(*) INTO cluster_count FROM training_program_cluster;
    SELECT COUNT(*) INTO roles_in_1 FROM organization_roles WHERE training_program_cluster_id = 1;
    SELECT COUNT(*) INTO roles_in_2 FROM organization_roles WHERE training_program_cluster_id = 2;
    SELECT COUNT(*) INTO roles_in_3 FROM organization_roles WHERE training_program_cluster_id = 3;

    RAISE NOTICE '================================================================';
    RAISE NOTICE '[SUCCESS] Migration 018 completed';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Training Program Clusters consolidated: 6 -> %', cluster_count;
    RAISE NOTICE 'New clusters:';
    RAISE NOTICE '  1. Engineers - % roles', roles_in_1;
    RAISE NOTICE '  2. Managers - % roles', roles_in_2;
    RAISE NOTICE '  3. Interfacing Partners - % roles', roles_in_3;
    RAISE NOTICE '';
    RAISE NOTICE 'Training program assignment will be recalculated';
    RAISE NOTICE 'based on actual competency gaps during LO generation.';
    RAISE NOTICE '================================================================';
END $$;
