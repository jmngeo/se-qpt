-- Migration 017: Add training_program_cluster_id to organization_roles table
-- Purpose: Allow mapping organization roles to Training Program Clusters for Phase 3 Role-Clustered view
-- Date: 2026-01-06
--
-- Note: Migration 014 added this to organization_role_mappings, but the service
-- queries organization_roles.training_program_cluster_id. This migration adds
-- the column to the correct table.

-- Add the training_program_cluster_id column to organization_roles
ALTER TABLE organization_roles
ADD COLUMN IF NOT EXISTS training_program_cluster_id INTEGER REFERENCES training_program_cluster(id);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_org_roles_training_cluster
ON organization_roles(organization_id, training_program_cluster_id);

COMMENT ON COLUMN organization_roles.training_program_cluster_id IS
'Training Program Cluster assignment for Phase 3 Role-Clustered view (Engineers, Managers, Executives, etc.)';

-- Auto-assign clusters based on role names (best-effort mapping)
-- This provides sensible defaults that users can override later
UPDATE organization_roles SET training_program_cluster_id =
    CASE
        -- Engineers cluster (id=1)
        WHEN LOWER(role_name) LIKE '%engineer%' THEN 1
        WHEN LOWER(role_name) LIKE '%developer%' THEN 1
        WHEN LOWER(role_name) LIKE '%architect%' THEN 1
        WHEN LOWER(role_name) LIKE '%test%' THEN 1
        WHEN LOWER(role_name) LIKE '%requirement%' THEN 1

        -- Managers cluster (id=2)
        WHEN LOWER(role_name) LIKE '%manager%' THEN 2
        WHEN LOWER(role_name) LIKE '%lead%' THEN 2
        WHEN LOWER(role_name) LIKE '%head%' THEN 2
        WHEN LOWER(role_name) LIKE '%supervisor%' THEN 2

        -- Executives cluster (id=3)
        WHEN LOWER(role_name) LIKE '%director%' THEN 3
        WHEN LOWER(role_name) LIKE '%executive%' THEN 3
        WHEN LOWER(role_name) LIKE '%vp%' THEN 3
        WHEN LOWER(role_name) LIKE '%chief%' THEN 3
        WHEN LOWER(role_name) LIKE '%cto%' THEN 3
        WHEN LOWER(role_name) LIKE '%ceo%' THEN 3

        -- Support Staff cluster (id=4)
        WHEN LOWER(role_name) LIKE '%quality%' THEN 4
        WHEN LOWER(role_name) LIKE '%config%' THEN 4
        WHEN LOWER(role_name) LIKE '%support%' THEN 4
        WHEN LOWER(role_name) LIKE '%document%' THEN 4

        -- External Partners cluster (id=5)
        WHEN LOWER(role_name) LIKE '%customer%' THEN 5
        WHEN LOWER(role_name) LIKE '%sales%' THEN 5
        WHEN LOWER(role_name) LIKE '%partner%' THEN 5
        WHEN LOWER(role_name) LIKE '%supplier%' THEN 5

        -- Operations cluster (id=6)
        WHEN LOWER(role_name) LIKE '%operation%' THEN 6
        WHEN LOWER(role_name) LIKE '%production%' THEN 6
        WHEN LOWER(role_name) LIKE '%service%' THEN 6
        WHEN LOWER(role_name) LIKE '%field%' THEN 6
        WHEN LOWER(role_name) LIKE '%maintenance%' THEN 6

        -- Default to Engineers for technical-sounding roles
        ELSE 1
    END
WHERE training_program_cluster_id IS NULL;

-- Verification
DO $$
DECLARE
    total_roles INTEGER;
    roles_with_cluster INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_roles FROM organization_roles;
    SELECT COUNT(*) INTO roles_with_cluster FROM organization_roles WHERE training_program_cluster_id IS NOT NULL;

    RAISE NOTICE '================================================================';
    RAISE NOTICE '[SUCCESS] Migration 017 completed';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Column added: organization_roles.training_program_cluster_id';
    RAISE NOTICE 'Total roles: %', total_roles;
    RAISE NOTICE 'Roles with cluster assignment: %', roles_with_cluster;
    RAISE NOTICE '================================================================';
END $$;
