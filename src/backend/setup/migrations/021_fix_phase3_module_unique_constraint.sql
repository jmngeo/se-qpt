-- Migration 021: Fix Phase 3 training module unique constraint
-- Removes the old unique constraint that doesn't include training_program_cluster_id
-- Required for Role-Clustered view where the same competency/level/pmt can have different clusters

-- Drop the old unique constraint without cluster_id
-- This constraint prevented proper cluster-specific module entries
ALTER TABLE phase3_training_module
DROP CONSTRAINT IF EXISTS phase3_training_module_organization_id_competency_id_target_key;

-- The correct constraint (phase3_training_module_unique_idx) should already exist:
-- UNIQUE (organization_id, competency_id, target_level, COALESCE(pmt_type, ''), COALESCE(training_program_cluster_id, 0))
-- If not, create it:
CREATE UNIQUE INDEX IF NOT EXISTS phase3_training_module_unique_idx
ON phase3_training_module (
    organization_id,
    competency_id,
    target_level,
    COALESCE(pmt_type, ''),
    COALESCE(training_program_cluster_id, 0)
);
