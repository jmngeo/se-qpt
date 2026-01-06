<template>
  <div class="learning-objectives-view">
    <!-- Header Card -->
    <el-card>
      <template #header>
        <div class="card-header">
          <h3 class="section-heading">Learning Objectives Results</h3>
          <div class="header-actions" v-if="hasData">
            <el-button
              type="primary"
              :icon="Download"
              :loading="isExporting"
              @click="handleExport"
            >
              Export to Excel
            </el-button>
          </div>
        </div>
      </template>

      <!-- View Toggle for Role-Based Organizations - placed above Definition note -->
      <div v-if="hasRoles && hasData" class="view-toggle-wrapper">
        <div class="view-toggle-container">
          <button
            class="view-toggle-btn"
            :class="{ active: selectedView === 'organizational' }"
            @click="selectedView = 'organizational'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            Organizational View
          </button>
          <button
            class="view-toggle-btn"
            :class="{ active: selectedView === 'role-based' }"
            @click="selectedView = 'role-based'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            Role-Based View
          </button>
        </div>
      </div>

      <!-- LO Definition Note -->
      <div class="lo-definition-note">
        <div class="note-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
        </div>
        <div class="note-content">
          <span class="note-label">Definition:</span>
          A learning objective is a description of the state in which the participants find themselves at the end of the course/module in terms of competence, knowledge and qualifications.
        </div>
      </div>

      <!-- Main Content -->
      <div v-if="hasData" class="content-container">
        <!-- Quick Summary Stats -->
        <div class="quick-stats">
          <div class="stat-card strategy-card">
            <span class="stat-value strategy-names">{{ strategyNames }}</span>
            <span class="stat-label">Selected Strategy</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ totalGapsToClose }}</span>
            <span class="stat-label">Levels to Advance</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ competenciesWithGap }}</span>
            <span class="stat-label">Competencies with Gap</span>
          </div>
        </div>

        <!-- Mastery Level Advisory (informational, not critical) -->
        <div v-if="validationData && validationData.status === 'INADEQUATE'" class="validation-section">
          <el-alert
            :type="validationAlertType"
            title="Mastery Level Advisory"
            show-icon
            :closable="true"
          >
            <div class="validation-content">
              <p class="validation-message">{{ validationData.message }}</p>
              <div v-if="validationData.recommendations" class="validation-recommendations">
                <p class="recommendations-header">Options to address this:</p>
                <div
                  v-for="rec in validationData.recommendations"
                  :key="rec.action"
                  class="recommendation-item"
                >
                  <span class="rec-label">{{ rec.label }}</span>
                  <span class="rec-description">{{ rec.description }}</span>
                </div>
              </div>
            </div>
          </el-alert>
        </div>

        <!-- Pyramid Level View (Organizational View) -->
        <div v-if="mainPyramid && selectedView === 'organizational'" class="pyramid-section">
          <PyramidLevelView
            :strategy-data="pyramidStrategyData"
            :pyramid-data="mainPyramid"
            :pathway="pathway"
            :ttt-data="tttObjectives"
            :ttt-enabled="tttEnabled"
          />
        </div>

        <!-- Role-Based View -->
        <div v-else-if="hasRoles && selectedView === 'role-based'" class="role-based-section">
          <RoleBasedObjectivesView
            :objectives="objectives"
            :organization-id="organizationId"
          />
        </div>

        <!-- TTT Info Banner - HIDDEN per Ulf's meeting 28.11.2025
             Level 6 and TTT handling deferred to backlog - see BACKLOG.md #14, #15 -->
        <!-- <div v-if="tttEnabled" class="ttt-banner">
          <div class="ttt-banner-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="ttt-banner-content">
            <h4 class="ttt-banner-title">Train the Trainer Strategy Active</h4>
            <p class="ttt-banner-text">
              Level 6 (Mastering SE) objectives are available for developing internal trainers.
              Navigate to <strong>Level 6</strong> in the pyramid above to view mastery-level learning objectives.
            </p>
          </div>
          <div class="ttt-banner-badge">
            <span class="badge-count">{{ tttObjectives?.length || 16 }}</span>
            <span class="badge-label">competencies</span>
          </div>
        </div> -->

        <!-- Complete Phase 2 Section -->
        <div v-if="mainPyramid" class="complete-phase-section">
          <el-divider />
          <div class="complete-phase-content">
            <div class="complete-phase-info">
              <el-icon :size="32" color="#67C23A"><CircleCheckFilled /></el-icon>
              <div class="complete-phase-text">
                <h4>Learning Objectives Generated Successfully</h4>
                <p>Your organization's learning objectives have been generated based on the competency assessments and selected training strategies.</p>
              </div>
            </div>
            <el-button type="success" size="large" @click="handleCompletePhase" :loading="isCompletingPhase">
              <el-icon><Check /></el-icon>
              Complete Phase 2
            </el-button>
          </div>
        </div>

        <!-- No Data Message -->
        <el-empty v-if="!mainPyramid" description="No learning objectives available">
          <p class="empty-note">Generate learning objectives by completing the prerequisites.</p>
        </el-empty>
      </div>

      <!-- Loading/Error States -->
      <el-empty v-else description="No learning objectives data available" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, User, CircleCheckFilled, Check, Download } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { phase2Task3Api } from '@/api/phase2'
import axios from '@/api/axios'
import PyramidLevelView from './PyramidLevelView.vue'
import RoleBasedObjectivesView from './RoleBasedObjectivesView.vue'

const router = useRouter()
const authStore = useAuthStore()

const props = defineProps({
  objectives: {
    type: Object,
    required: true
  },
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['complete'])

// State for completing phase
const isCompletingPhase = ref(false)

// State for export
const isExporting = ref(false)

// ============================================================
// VIEW SELECTION
// ============================================================
const selectedView = ref('organizational')

// ============================================================
// EXTRACT DATA FROM V5 API STRUCTURE
// ============================================================

// Get pathway info
const pathway = computed(() => {
  return props.objectives?.pathway || 'TASK_BASED'
})

// Check if organization has roles
const hasRoles = computed(() => {
  return props.objectives?.metadata?.has_roles === true ||
         pathway.value?.includes('ROLE')
})

// Get main_pyramid data
const mainPyramid = computed(() => {
  return props.objectives?.data?.main_pyramid || null
})

// Get TTT data (for the summary card)
const tttData = computed(() => {
  const ttt = props.objectives?.data?.train_the_trainer
  if (ttt && typeof ttt === 'object' && Object.keys(ttt).length > 0) {
    // Convert object format to array format if needed
    if (!ttt.competencies && !Array.isArray(ttt)) {
      return {
        competencies: Object.entries(ttt).map(([id, data]) => ({
          competency_id: parseInt(id),
          competency_name: data.competency_name || `Competency ${id}`,
          gap_percentage: data.gap_percentage || 0,
          ...data
        }))
      }
    }
    return ttt
  }
  return null
})

// Check if TTT is enabled
const tttEnabled = computed(() => {
  return tttData.value !== null && Object.keys(tttData.value).length > 0
})

// Get TTT objectives with full data for Level 6 display
const tttObjectives = computed(() => {
  const ttt = props.objectives?.data?.train_the_trainer
  if (!ttt || typeof ttt !== 'object') {
    return null
  }

  // Convert to array format with full competency card structure
  const objectives = []
  for (const [id, data] of Object.entries(ttt)) {
    if (data && typeof data === 'object') {
      objectives.push({
        competency_id: parseInt(id),
        competency_name: data.competency_name || `Competency ${id}`,
        target_level: 6,
        // Don't set current_level - TTT is about mastery development, not gap remediation
        // Setting current_level = target_level prevents the "X -> Y" badge from showing
        current_level: 6,
        status: 'training_required',
        grayed_out: false,
        is_ttt: true, // Flag to identify TTT competencies in the card
        learning_objective: data.objective_text || null,
        users_needing: data.users_needing || 0,
        total_users: data.total_users || 0,
        gap_percentage: data.gap_percentage || 0,
        customized: data.customized || false
      })
    }
  }

  return objectives.length > 0 ? objectives : null
})

// Get API metadata
const apiMetadata = computed(() => {
  return props.objectives?.metadata || {}
})

// Get selected strategies
const selectedStrategies = computed(() => {
  return props.objectives?.metadata?.selected_strategies || []
})

// Get strategy names as a string
const strategyNames = computed(() => {
  if (selectedStrategies.value.length === 0) {
    return 'No strategy selected'
  }
  return selectedStrategies.value
    .map(s => s.strategy_name || s.name)
    .join(', ')
})

// Get validation data
const validationData = computed(() => {
  return props.objectives?.data?.validation || null
})

// ============================================================
// COMPUTED PROPERTIES FOR DISPLAY
// ============================================================

const hasData = computed(() => {
  return mainPyramid.value !== null || props.objectives?.success === true
})

const validationAlertType = computed(() => {
  if (!validationData.value) return 'info'
  if (validationData.value.status === 'OK') return 'success'
  // Use 'info' type for mastery validation - it's informational, not critical
  return 'info'
})

// Calculate totals
const totalCompetencies = computed(() => {
  if (mainPyramid.value?.levels) {
    const uniqueIds = new Set()
    Object.values(mainPyramid.value.levels).forEach(levelData => {
      levelData.competencies?.forEach(c => uniqueIds.add(c.competency_id))
    })
    return uniqueIds.size
  }
  return apiMetadata.value.total_competencies || 16
})

// Count unique competencies that have at least one gap (training required)
const competenciesWithGap = computed(() => {
  if (mainPyramid.value?.levels) {
    const competenciesNeedingTraining = new Set()
    Object.values(mainPyramid.value.levels).forEach(levelData => {
      levelData.competencies?.forEach(c => {
        // Count if this competency needs training at ANY level (not grayed out)
        if (c.status === 'training_required' && !c.grayed_out) {
          competenciesNeedingTraining.add(c.competency_id)
        }
      })
    })
    return competenciesNeedingTraining.size
  }
  return 0
})

const totalGapsToClose = computed(() => {
  if (mainPyramid.value?.levels) {
    let count = 0
    Object.values(mainPyramid.value.levels).forEach(levelData => {
      levelData.competencies?.forEach(c => {
        if (c.status === 'training_required' && !c.grayed_out) {
          count++
        }
      })
    })
    return count
  }
  // Use metadata if available
  const perLevel = mainPyramid.value?.metadata?.active_competencies_per_level
  if (perLevel) {
    return Object.values(perLevel).reduce((sum, n) => sum + n, 0)
  }
  return 0
})

// Create a strategy data object for PyramidLevelView compatibility
const pyramidStrategyData = computed(() => {
  const trainableCompetencies = []

  if (mainPyramid.value?.levels) {
    Object.values(mainPyramid.value.levels).forEach(levelData => {
      levelData.competencies?.forEach(c => {
        if (c.status === 'training_required' && !c.grayed_out) {
          trainableCompetencies.push(c)
        }
      })
    })
  }

  return {
    strategy_name: strategyNames.value,
    trainable_competencies: trainableCompetencies
  }
})

// ============================================================
// METHODS
// ============================================================

const handleCompletePhase = async () => {
  try {
    isCompletingPhase.value = true

    // Mark Phase 2 as complete in the backend
    console.log('[LearningObjectivesView] Marking Phase 2 as complete...')
    await axios.put('/api/organization/phase2-complete')

    // Emit complete event for parent to handle any additional logic
    emit('complete')

    // Show success message and navigate to dashboard
    ElMessage.success('Phase 2 completed successfully! Returning to dashboard...')
    router.push('/app/dashboard')
  } catch (error) {
    console.error('Phase 2 completion error:', error)
    ElMessage.error('Failed to complete Phase 2. Please try again.')
  } finally {
    isCompletingPhase.value = false
  }
}

// Handle Excel export
const handleExport = async () => {
  try {
    isExporting.value = true
    ElMessage.info('Preparing Excel export...')

    await phase2Task3Api.exportObjectives(props.organizationId, 'excel', {
      include_validation: true
    })

    ElMessage.success('Learning objectives exported successfully!')
  } catch (error) {
    console.error('[LearningObjectivesView] Export failed:', error)
    ElMessage.error('Failed to export learning objectives. Please try again.')
  } finally {
    isExporting.value = false
  }
}
</script>

<style scoped>
.learning-objectives-view {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-heading {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* LO Definition Note */
.lo-definition-note {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f4ff 100%);
  border: 1px solid #bae0ff;
  border-radius: 8px;
}

.note-icon {
  flex-shrink: 0;
  color: #1890ff;
  margin-top: 2px;
}

.note-content {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.note-label {
  font-weight: 600;
  color: #1890ff;
  margin-right: 6px;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 16px;
}

.validation-section {
  margin: 0;
}

.validation-content {
  padding-top: 4px;
}

.validation-message {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.validation-recommendations {
  margin-top: 8px;
}

.recommendations-header {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 500;
  color: #409eff;
}

.recommendation-item {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.recommendation-item:last-child {
  margin-bottom: 0;
}

.rec-label {
  font-weight: 600;
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

/* View Toggle */
.view-toggle-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.view-toggle-container {
  display: inline-flex;
  background: #f4f4f5;
  border-radius: 8px;
  padding: 4px;
  gap: 4px;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-toggle-btn:hover {
  background: #e9ecef;
}

.view-toggle-btn.active {
  background: white;
  color: #409EFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.view-toggle-btn svg {
  flex-shrink: 0;
}

/* Quick Stats */
.quick-stats {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 12px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.stat-card.strategy-card {
  align-items: flex-start;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.stat-value.strategy-names {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Pyramid Section */
.pyramid-section {
  margin-top: 8px;
}

/* Role-Based Section */
.role-based-section {
  margin-top: 8px;
}

/* TTT Banner */
.ttt-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fdf6ec 0%, #fef9f3 100%);
  border: 1px solid #e6a23c;
  border-radius: 10px;
  margin-top: 8px;
}

.ttt-banner-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #e6a23c;
  border-radius: 50%;
  color: white;
}

.ttt-banner-content {
  flex: 1;
}

.ttt-banner-title {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #b88230;
}

.ttt-banner-text {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.ttt-banner-text strong {
  color: #e6a23c;
}

.ttt-banner-badge {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.2);
}

.ttt-banner-badge .badge-count {
  font-size: 24px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
}

.ttt-banner-badge .badge-label {
  font-size: 10px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

/* Empty Note */
.empty-note {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

/* Complete Phase Section */
.complete-phase-section {
  margin-top: 24px;
}

.complete-phase-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e0 100%);
  border: 1px solid #b3e19d;
  border-radius: 12px;
}

.complete-phase-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.complete-phase-text h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d5016;
}

.complete-phase-text p {
  margin: 0;
  font-size: 13px;
  color: #5a8a3a;
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .quick-stats {
    grid-template-columns: 1fr;
  }

  .complete-phase-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .complete-phase-info {
    flex-direction: column;
  }
}
</style>
