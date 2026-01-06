<template>
  <div class="level-content-view">
    <!-- Level Header -->
    <div class="level-header" :style="{ '--level-color': levelConfig.color }">
      <div class="header-left">
        <!-- Per Ulf's meeting 28.11.2025: Remove level numbers, just show names -->
        <h2 class="level-title">{{ levelConfig.name }}</h2>
        <p class="level-description">{{ levelConfig.description }}</p>
      </div>
      <div class="header-stats">
        <div class="stat-item" :class="{ 'highlight': trainingNeededCount > 0 }">
          <span class="stat-value">{{ trainingNeededCount }}</span>
          <span class="stat-label">Training Needed</span>
        </div>
        <div class="stat-item achieved">
          <span class="stat-value">{{ achievedAtLevelCount }}</span>
          <span class="stat-label">Achieved</span>
        </div>
        <div class="stat-item not-targeted" v-if="notTargetedCount > 0">
          <span class="stat-value">{{ notTargetedCount }}</span>
          <span class="stat-label">Not Targeted</span>
        </div>
        <div class="stat-item training-exists" v-if="trainingExistsCount > 0">
          <span class="stat-value">{{ trainingExistsCount }}</span>
          <span class="stat-label">Training Exists</span>
        </div>
        <div class="stat-item total">
          <span class="stat-value">{{ competencies.length }}</span>
          <span class="stat-label">Total</span>
        </div>
      </div>
    </div>

    <!-- Filter Toggle -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-switch
          v-model="showAchieved"
          active-text="Show all competencies"
          inactive-text="Show gaps only"
          size="small"
        />
        <span class="filter-info">
          Showing {{ filteredCompetencies.length }} of {{ competencies.length }} competencies
        </span>
      </div>
      <div class="legends-container">
        <div class="level-legend">
          <span class="legend-label">Level indicator:</span>
          <div class="legend-example">
            <span class="level-badge current">Current</span>
            <span class="arrow">-></span>
            <span class="level-badge target">Target</span>
          </div>
        </div>
        <div class="role-legend">
          <span class="legend-label">Role (X/Y):</span>
          <span class="legend-explanation">X users of Y total have not achieved this level</span>
        </div>
      </div>
    </div>

    <!-- Competencies List -->
    <div class="competencies-container">
      <!-- Active competencies first -->
      <div v-if="activeCompetencies.length > 0" class="competencies-section">
        <h3 class="section-title needs-training">
          <span class="icon">!</span>
          Training Requirements Identified ({{ activeCompetencies.length }})
        </h3>
        <div class="competencies-grid">
          <SimpleCompetencyCard
            v-for="comp in activeCompetencies"
            :key="comp.competency_id"
            :competency="comp"
            :pathway="pathway"
            :level="level"
          />
        </div>
      </div>

      <!-- Achieved competencies (if showing) -->
      <div v-if="showAchieved && achievedCompetencies.length > 0" class="competencies-section achieved-section">
        <h3 class="section-title achieved">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          No Training Required ({{ achievedCompetencies.length }})
        </h3>
        <div class="competencies-grid grayed-grid">
          <SimpleCompetencyCard
            v-for="comp in achievedCompetencies"
            :key="comp.competency_id"
            :competency="comp"
            :pathway="pathway"
            :level="level"
            :show-objective-always="true"
          />
        </div>
      </div>

      <!-- All achieved - Success State -->
      <div v-if="activeCompetencies.length === 0" class="all-achieved-state">
        <div class="success-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3 class="success-title">{{ achievedTitle }}</h3>
        <p class="success-description">
          {{ achievedMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import SimpleCompetencyCard from './SimpleCompetencyCard.vue'

const props = defineProps({
  level: {
    type: Number,
    required: true
  },
  competencies: {
    type: Array,
    default: () => []
  },
  pathway: {
    type: String,
    default: 'ROLE_BASED'
  }
})

// State
const showAchieved = ref(true)

// Level configuration
const levelConfigs = {
  1: {
    name: 'Knowing SE',
    description: 'Foundation level - Users can recall and identify learned SE content accurately',
    color: '#1976D2'
  },
  2: {
    name: 'Understanding SE',
    description: 'Users can reproduce, interpret and explain SE concepts meaningfully',
    color: '#388E3C'
  },
  4: {
    name: 'Applying SE',
    description: 'Users can independently apply SE knowledge to similar situations',
    color: '#F57C00'
  },
  6: {
    name: 'Mastering SE',
    description: 'Expert level - Users can adapt to diverse situations and evaluate at systemic level',
    color: '#7B1FA2'
  }
}

const levelConfig = computed(() => levelConfigs[props.level] || levelConfigs[1])

// Helper to check if a competency has a skill gap that needs development
const hasSkillGap = (c) => {
  // TTT competencies are ALWAYS active (mastery development, not gap remediation)
  if (c.is_ttt === true) {
    // For TTT, just check it has learning objective text
    const hasObjective = typeof c.learning_objective === 'string'
      ? c.learning_objective.length > 0
      : c.learning_objective?.objective_text?.length > 0
    return hasObjective
  }

  // Must have status 'training_required' explicitly
  if (c.status !== 'training_required') {
    return false
  }

  // Must NOT be grayed out
  if (c.grayed_out === true) {
    return false
  }

  // Must have a learning objective with actual text
  const hasObjective = typeof c.learning_objective === 'string'
    ? c.learning_objective.length > 0
    : c.learning_objective?.objective_text?.length > 0

  if (!hasObjective) {
    return false
  }

  // Must have a positive gap (current < target)
  const currentLevel = c.current_level ?? 0
  const targetLevel = c.target_level ?? props.level
  if (currentLevel >= targetLevel) {
    return false
  }

  return true
}

// Separate competencies into categories
const activeCompetencies = computed(() => {
  return props.competencies.filter(hasSkillGap)
})

// Achieved = competencies that don't need training AND are not "not_targeted"
// These are competencies where user already meets or exceeds the target level
const achievedCompetencies = computed(() => {
  return props.competencies.filter(c => {
    if (hasSkillGap(c)) return false
    // Exclude "not_targeted" status from achieved
    if (c.status === 'not_targeted') return false
    if (c.target_level === 0) return false // Also not targeted
    return true
  })
})

// Not targeted = competencies with status 'not_targeted' or target_level = 0
const notTargetedCompetencies = computed(() => {
  return props.competencies.filter(c => {
    if (hasSkillGap(c)) return false
    // Exclude training_exists from not_targeted
    if (c.status === 'training_exists' || c.has_existing_training) return false
    return c.status === 'not_targeted' || c.target_level === 0
  })
})

// Training exists = competencies with existing training in org
const trainingExistsCompetencies = computed(() => {
  return props.competencies.filter(c => {
    return c.status === 'training_exists' || c.has_existing_training === true
  })
})

// Count values for the header stats
const trainingNeededCount = computed(() => activeCompetencies.value.length)
const achievedAtLevelCount = computed(() => achievedCompetencies.value.length)
const notTargetedCount = computed(() => notTargetedCompetencies.value.length)
const trainingExistsCount = computed(() => trainingExistsCompetencies.value.length)

// Legacy - keeping for backward compatibility
const activeCount = computed(() => activeCompetencies.value.length)
const achievedCount = computed(() => achievedCompetencies.value.length + notTargetedCompetencies.value.length)

const filteredCompetencies = computed(() => {
  if (showAchieved.value) {
    return props.competencies
  }
  return activeCompetencies.value
})

const achievedTitle = computed(() => {
  if (props.level === 6) {
    return 'Level 6 Not Targeted'
  }
  return `No Training Needed at Level ${props.level}`
})

const achievedMessage = computed(() => {
  if (props.level === 6) {
    return 'Level 6 (Mastering) represents expert-level capability. This level is not included in the selected strategy, or users need to complete lower levels first.'
  }
  return `Users already have Level ${props.level} capabilities in the targeted competencies, or the competencies at this level have different targets based on the selected strategy.`
})
</script>

<style scoped>
.level-content-view {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* Level Header */
.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, var(--level-color) 0%, color-mix(in srgb, var(--level-color), black 15%) 100%);
  color: white;
}

.header-left {
  flex: 1;
}

.level-title {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 600;
}

.level-description {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  min-width: 70px;
}

.stat-item.highlight {
  background: rgba(255, 255, 255, 0.25);
}

.stat-item.achieved {
  background: rgba(103, 194, 58, 0.3);
}

.stat-item.not-targeted {
  background: rgba(144, 147, 153, 0.2);
}

.stat-item.training-exists {
  background: rgba(24, 144, 255, 0.25);
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 10px;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.9;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-info {
  font-size: 13px;
  color: #909399;
}

.legends-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.level-legend,
.role-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.legend-explanation {
  font-size: 12px;
  color: #606266;
  font-style: italic;
}

.legend-label {
  font-size: 12px;
  color: #909399;
}

.legend-example {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-example .level-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.legend-example .level-badge.current {
  background: #fafafa;
  color: #909399;
  border: 1px solid #e9ecef;
}

.legend-example .level-badge.target {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.legend-example .arrow {
  color: #1890ff;
  font-size: 11px;
}

/* Competencies Container */
.competencies-container {
  padding: 24px;
}

.competencies-section {
  margin-bottom: 24px;
}

.competencies-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-title.needs-training {
  color: #E6A23C;
}

.section-title.needs-training .icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #E6A23C;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

.section-title.achieved {
  color: #67C23A;
}

.competencies-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.competencies-grid > * {
  flex: 0 0 calc(50% - 8px);
  max-width: calc(50% - 8px);
}

.grayed-grid {
  opacity: 0.85;
}

.achieved-section {
  padding-top: 24px;
  border-top: 1px dashed #e9ecef;
}

/* All Achieved State */
.all-achieved-state {
  padding: 48px 40px;
  text-align: center;
}

.success-icon {
  color: #67C23A;
  margin-bottom: 16px;
}

.success-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.success-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .level-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-stats {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-bar {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .competencies-grid > * {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>
