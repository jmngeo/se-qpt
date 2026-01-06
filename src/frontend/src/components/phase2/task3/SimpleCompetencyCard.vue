<template>
  <div
    class="simple-competency-card"
    :class="{
      'is-grayed': grayed,
      'has-gap': !grayed && hasSkillGap
    }"
  >
    <!-- Header -->
    <div class="card-header">
      <h4 class="competency-name">{{ competency.competency_name }}</h4>

      <!-- Show level progression if there's a gap (non-TTT) -->
      <div v-if="hasSkillGap && !grayed && !isTTT" class="level-progression">
        <span class="level current">{{ currentLevel }}</span>
        <span class="arrow">-></span>
        <span class="level target">{{ targetLevel }}</span>
      </div>

      <!-- Show achieved badge if target is already met (non-TTT only) -->
      <div v-else-if="!isTTT && !hasSkillGap" class="achieved-badge" :class="{ 'not-targeted': isNotTargeted, 'training-exists': hasExistingTraining }">
        <svg v-if="!isNotTargeted && !hasExistingTraining" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <!-- Training Exists icon (box/package) -->
        <svg v-else-if="hasExistingTraining" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
        <span>{{ achievedLabel }}</span>
      </div>
      <!-- TTT competencies: no badge shown -->
    </div>

    <!-- Learning Objective - always show if available -->
    <div v-if="objectiveText || hasTemplatePMT" class="objective-box" :class="{ 'grayed-objective': grayed, 'has-pmt-breakdown': hasTemplatePMT && !grayed }">
      <!-- For competencies WITH PMT breakdown: show tagged sections -->
      <div v-if="hasTemplatePMT && !grayed" class="pmt-tagged-content">
        <div v-if="templatePMT?.process" class="pmt-tagged-section">
          <span class="pmt-tag pmt-tag-process">Process</span>
          <span class="pmt-tagged-text">{{ templatePMT.process }}</span>
        </div>
        <div v-if="templatePMT?.method" class="pmt-tagged-section">
          <span class="pmt-tag pmt-tag-method">Method</span>
          <span class="pmt-tagged-text">{{ templatePMT.method }}</span>
        </div>
        <div v-if="templatePMT?.tool" class="pmt-tagged-section">
          <span class="pmt-tag pmt-tag-tool">Tool</span>
          <span class="pmt-tagged-text">{{ templatePMT.tool }}</span>
        </div>
      </div>

      <!-- For competencies WITHOUT PMT breakdown: show unified text as bullet points -->
      <ul v-else-if="objectiveBullets.length > 0" class="objective-bullets">
        <li v-for="(bullet, idx) in objectiveBullets" :key="idx" class="objective-bullet">
          {{ bullet }}
        </li>
      </ul>
      <p v-else class="objective-text">{{ objectiveText }}</p>
    </div>

    <!-- Roles Needing This Level (Organizational View with roles defined) -->
    <div v-if="!grayed && hasSkillGap && rolesWithGaps.length > 0" class="roles-section">
      <div class="roles-title">Roles Needing This Level:</div>
      <div class="role-chips">
        <span
          v-for="role in rolesWithGaps"
          :key="role.role_id"
          class="role-chip"
        >
          {{ role.role_name }}
          <span class="user-count">{{ role.users_needing }}/{{ role.total_users }}</span>
        </span>
      </div>
    </div>

    <!-- Users below target (fallback when no roles defined) -->
    <div v-else-if="!grayed && usersBelowTarget > 0 && rolesWithGaps.length === 0" class="users-section">
      <span class="users-label">Users below target level:</span>
      <span class="users-value">{{ usersBelowTarget }}</span>
    </div>

    <!-- PMT Context (if available) -->
    <div v-if="hasSkillGap && !grayed && hasPMT" class="pmt-section">
      <el-collapse>
        <el-collapse-item title="Company Context (PMT)" name="pmt">
          <div class="pmt-content">
            <div v-if="competency.pmt_breakdown?.processes" class="pmt-item">
              <strong>Processes:</strong> {{ competency.pmt_breakdown.processes }}
            </div>
            <div v-if="competency.pmt_breakdown?.methods" class="pmt-item">
              <strong>Methods:</strong> {{ competency.pmt_breakdown.methods }}
            </div>
            <div v-if="competency.pmt_breakdown?.tools" class="pmt-item">
              <strong>Tools:</strong> {{ competency.pmt_breakdown.tools }}
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  competency: {
    type: Object,
    required: true
  },
  pathway: {
    type: String,
    default: 'ROLE_BASED'
  },
  level: {
    type: Number,
    default: null
  },
  showObjectiveAlways: {
    type: Boolean,
    default: false
  }
})

// Get current level
const currentLevel = computed(() => {
  if (props.competency.current_level !== undefined) {
    return props.competency.current_level
  }
  if (props.competency.gap_data?.organizational_stats?.median_level !== undefined) {
    return props.competency.gap_data.organizational_stats.median_level
  }
  return 0
})

// Get target level
const targetLevel = computed(() => {
  return props.competency.target_level || props.level || 0
})

// Calculate gap
const gap = computed(() => {
  if (props.competency.gap !== undefined) {
    return props.competency.gap
  }
  return targetLevel.value - currentLevel.value
})

// Determine if there's a skill gap that needs development
const hasSkillGap = computed(() => {
  // TTT competencies are ALWAYS active (mastery development, not gap remediation)
  if (props.competency.is_ttt === true) {
    return objectiveText.value && objectiveText.value.length > 0
  }

  const status = props.competency.status

  // MUST have status 'training_required' explicitly
  if (status !== 'training_required') {
    return false
  }

  // MUST NOT be grayed out
  if (props.competency.grayed_out === true) {
    return false
  }

  // MUST have a learning objective with actual text
  if (!objectiveText.value || objectiveText.value.length === 0) {
    return false
  }

  // MUST have current level below target (positive gap)
  if (currentLevel.value >= targetLevel.value) {
    return false
  }

  return true
})

// Determine if card should be grayed out
const grayed = computed(() => {
  // Explicit grayed_out flag from backend
  if (props.competency.grayed_out === true) {
    return true
  }

  // No skill gap = grayed
  if (!hasSkillGap.value) {
    return true
  }

  return false
})

// Check if this is not targeted
const isNotTargeted = computed(() => {
  return props.competency.status === 'not_targeted'
})

// Check if this competency has existing training (excluded from requirements)
const hasExistingTraining = computed(() => {
  return props.competency.status === 'training_exists' ||
         props.competency.has_existing_training === true
})

// Label for achieved badge
const achievedLabel = computed(() => {
  const status = props.competency.status

  // NEW: Check for existing training status first
  if (status === 'training_exists' || props.competency.has_existing_training) {
    return 'Training Exists'
  }
  if (status === 'target_achieved' || status === 'achieved') {
    return 'Achieved'
  }
  if (status === 'role_requirement_met') {
    return 'Role Met'
  }
  if (status === 'not_targeted') {
    return 'Not Targeted'
  }
  if (currentLevel.value >= targetLevel.value) {
    return 'Achieved'
  }
  return 'Complete'
})

// Get the learning objective text
const objectiveText = computed(() => {
  // Direct string field (backend uses 'learning_objective')
  if (typeof props.competency.learning_objective === 'string') {
    return props.competency.learning_objective
  }

  // Object with objective_text (from pyramid structure)
  if (props.competency.learning_objective?.objective_text) {
    return props.competency.learning_objective.objective_text
  }

  // Alternative field name
  if (props.competency.learning_objective_text) {
    return props.competency.learning_objective_text
  }

  // Base template as fallback
  if (props.competency.base_template) {
    return props.competency.base_template
  }

  return null
})

// Convert objective text to bullet points (split by sentence)
// Per Ulf's meeting 28.11.2025 - makes it easier to see how many objectives exist
const objectiveBullets = computed(() => {
  if (!objectiveText.value) return []

  // Split by periods, filter empty, trim whitespace
  const sentences = objectiveText.value
    .split(/\.(?=\s|$)/)  // Split on periods followed by space or end of string
    .map(s => s.trim())
    .filter(s => s.length > 0)

  // If only one sentence, don't use bullets (just show as paragraph)
  if (sentences.length <= 1) return []

  return sentences
})

// Get users below target level
const usersBelowTarget = computed(() => {
  return props.competency.users_requiring_training ||
         props.competency.users_affected ||
         0
})

// Check if PMT breakdown exists (company context - legacy)
const hasPMT = computed(() => {
  const pmt = props.competency.pmt_breakdown
  return pmt && (pmt.processes || pmt.methods || pmt.tools)
})

// Check if template PMT breakdown exists (from learning_objective)
const hasTemplatePMT = computed(() => {
  const lo = props.competency.learning_objective
  if (typeof lo === 'object' && lo !== null) {
    return lo.has_pmt_breakdown === true || lo.pmt_breakdown !== undefined
  }
  return false
})

// Get template PMT breakdown data
const templatePMT = computed(() => {
  const lo = props.competency.learning_objective
  if (typeof lo === 'object' && lo !== null && lo.pmt_breakdown) {
    return lo.pmt_breakdown
  }
  return null
})

// Check if this is a TTT (Train the Trainer) competency
const isTTT = computed(() => {
  return props.competency.is_ttt === true
})

// Get roles with gaps at this level (for Organizational View)
const rolesWithGaps = computed(() => {
  const gapData = props.competency.gap_data
  if (!gapData || !gapData.roles) {
    return []
  }

  const roles = []
  const currentDisplayLevel = props.level || targetLevel.value

  for (const [roleId, roleData] of Object.entries(gapData.roles)) {
    if (!roleData || typeof roleData !== 'object') continue

    // Check if this role needs training at this level
    const levelsNeeded = roleData.levels_needed || []
    const levelDetails = roleData.level_details || {}

    // If role needs this specific level, add it
    if (levelsNeeded.includes(currentDisplayLevel) || levelDetails[currentDisplayLevel]) {
      const detail = levelDetails[currentDisplayLevel] || {}
      roles.push({
        role_id: roleId,
        role_name: roleData.role_name || `Role ${roleId}`,
        users_needing: detail.users_needing ?? roleData.users_needing_training ?? 0,
        total_users: detail.total_users ?? roleData.total_users ?? 0
      })
    }
  }

  return roles
})
</script>

<style scoped>
.simple-competency-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.simple-competency-card.has-gap:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #d0d0d0;
}

/* Grayed out state */
.simple-competency-card.is-grayed {
  background: #fafafa;
  border-color: #e9ecef;
  opacity: 0.75;
}

.simple-competency-card.is-grayed .competency-name {
  color: #909399;
}

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.competency-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  flex: 1;
}

.level-progression {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  padding: 4px 10px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
}

.level.current {
  color: #909399;
}

.arrow {
  color: #1890ff;
}

.level.target {
  color: #1890ff;
}

/* Achieved Badge */
.achieved-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #f0f9eb;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  color: #67C23A;
}

.achieved-badge.not-targeted {
  background: #f5f5f5;
  color: #909399;
}

.achieved-badge.training-exists {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

/* Objective Box */
.objective-box {
  background: #f0f9ff;
  border-left: 3px solid #1890ff;
  border-radius: 4px;
  padding: 12px 14px;
  margin-bottom: 12px;
}

.objective-box.grayed-objective {
  background: #f5f7fa;
  border-left-color: #909399;
}

.objective-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.objective-bullets {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.objective-bullet {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 6px;
}

.objective-bullet:last-child {
  margin-bottom: 0;
}

.grayed-objective .objective-text,
.grayed-objective .objective-bullet {
  color: #606266;
}

/* Roles Section */
.roles-section {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.roles-title {
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 8px;
}

.role-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.role-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  color: #606266;
}

.role-chip .user-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #1890ff;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  min-width: 32px;
}

/* Users Section (fallback when no roles) */
.users-section {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.users-label {
  color: #909399;
}

.users-value {
  font-weight: 600;
  color: #303133;
}

/* PMT Section */
.pmt-section {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.pmt-section :deep(.el-collapse) {
  border: none;
}

.pmt-section :deep(.el-collapse-item__header) {
  font-size: 12px;
  font-weight: 500;
  color: #909399;
  height: 32px;
  line-height: 32px;
  background: transparent;
  border: none;
}

.pmt-section :deep(.el-collapse-item__wrap) {
  border: none;
}

.pmt-section :deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

.pmt-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pmt-item {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.pmt-item strong {
  color: #303133;
}

/* PMT Tagged Content - Inline display with P/M/T tags */
.pmt-tagged-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pmt-tagged-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.pmt-tagged-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.pmt-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  padding: 4px 10px;
  height: 26px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 1px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.pmt-tag-process {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #0958d9;
  border: 1px solid #91d5ff;
}

.pmt-tag-method {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #389e0d;
  border: 1px solid #b7eb8f;
}

.pmt-tag-tool {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  color: #d46b08;
  border: 1px solid #ffd591;
}

.pmt-tagged-text {
  font-size: 14px;
  line-height: 1.7;
  color: #303133;
  flex: 1;
}

/* PMT Card has special styling */
.objective-box.has-pmt-breakdown {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f4ff 100%);
  border-left: 4px solid #1890ff;
  padding: 14px 16px;
  min-height: auto;
}
</style>
