-- Migration: Add training_program_cluster_id to phase3_training_module
-- Purpose: Support separate training modules per cluster in Role-Clustered view
-- Date: 2026-01-05

-- Add the cluster_id column (nullable - null means competency_level view)
ALTER TABLE phase3_training_module
ADD COLUMN IF NOT EXISTS training_program_cluster_id INTEGER REFERENCES training_program_cluster(id);

-- Drop the existing unique constraint
ALTER TABLE phase3_training_module
DROP CONSTRAINT IF EXISTS phase3_training_module_org_comp_level_pmt_key;

-- Create new unique constraint that includes cluster_id
-- Using COALESCE to handle NULL cluster_id (for competency_level view)
CREATE UNIQUE INDEX IF NOT EXISTS phase3_training_module_unique_idx
ON phase3_training_module (
    organization_id,
    competency_id,
    target_level,
    COALESCE(pmt_type, ''),
    COALESCE(training_program_cluster_id, 0)
);

-- Add index for faster queries by cluster
CREATE INDEX IF NOT EXISTS idx_phase3_training_module_cluster
ON phase3_training_module(training_program_cluster_id)
WHERE training_program_cluster_id IS NOT NULL;

COMMENT ON COLUMN phase3_training_module.training_program_cluster_id IS
'Training program cluster for Role-Clustered view. NULL for Competency-Level view.';
