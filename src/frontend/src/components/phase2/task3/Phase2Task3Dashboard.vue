<template>
  <div class="phase2-task3-dashboard">
    <!-- Page Header -->
    <el-page-header @back="handleBack">
      <template #content>
        <div class="header-content">
          <h1>Learning Objectives</h1>
          <p class="subtitle">Generate learning objectives based on competency assessments</p>
        </div>
      </template>
    </el-page-header>

    <!-- Loading State -->
    <el-card v-if="isLoading" class="loading-card">
      <div style="text-align: center; padding: 40px;">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p style="margin-top: 16px;">Loading Phase 2 Task 3 data...</p>
      </div>
    </el-card>

    <!-- Consolidated Single Page View -->
    <el-card v-else class="main-content-card">
      <div class="consolidated-view">

      <!-- Overview Information Card -->
      <div class="section overview-card">
        <div class="overview-content">
          <div class="overview-icon">
            <el-icon :size="40" color="#409EFF"><InfoFilled /></el-icon>
          </div>
          <div class="overview-text">
            <h3 class="overview-title">About Learning Objectives Generation</h3>
            <p class="overview-description">
              This intelligent system analyzes all completed competency assessments across your organization
              and generates learning objectives tailored to your training needs. The system considers
              your organization's <strong>process maturity level</strong> (from Phase 1), <strong>selected training strategies</strong>,
              and organizational competency gaps to determine the most effective learning path.
            </p>
            <div class="overview-process">
              <div class="process-step">
                <el-icon color="#67C23A"><DocumentChecked /></el-icon>
                <span><strong>Step 1:</strong> Collect assessment data</span>
              </div>
              <div class="process-step">
                <el-icon color="#E6A23C"><TrendCharts /></el-icon>
                <span><strong>Step 2:</strong> Analyze competency gaps</span>
              </div>
              <div class="process-step">
                <el-icon color="#409EFF"><MagicStick /></el-icon>
                <span><strong>Step 3:</strong> Generate targeted objectives</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 1: Assessment Monitoring (Always Visible) -->
      <div class="section-container">
        <h2 class="section-heading">
          <el-icon><DataAnalysis /></el-icon>
          Assessment Monitoring
        </h2>
        <AssessmentMonitor
          :organization-id="organizationId"
          :pathway="pathway"
          :assessment-stats="assessmentStats"
          @refresh="refreshData"
        />
      </div>

      <!-- SECTION 1.5: Existing Training Check (Feature: Ulf's request 11.12.2025) -->
      <div class="section-container">
        <h2 class="section-heading">
          <el-icon><Box /></el-icon>
          Existing Training Check
        </h2>
        <ExistingTrainingsSelector
          :organization-id="organizationId"
          @updated="handleExistingTrainingsUpdated"
        />
      </div>

      <!-- SECTION 2: Organization SE Context (Conditional - Only if Needed) -->
      <div v-if="needsPMT" class="section-container">
        <h2 class="section-heading">
          <el-icon><Setting /></el-icon>
          Organization SE Practices
        </h2>

        <!-- PMT Form -->
        <PMTContextForm
          v-if="!hasPMT || showPMTEdit"
          :organization-id="organizationId"
          :existing-context="pmtContext"
          @saved="handlePMTSaved"
        />

        <!-- SE Practices Summary -->
        <el-card v-else class="pmt-summary-card">
          <template #header>
            <div class="card-header">
              <span>SE Practices Configured</span>
              <el-tag type="success" size="small">Complete</el-tag>
            </div>
          </template>
          <div class="pmt-summary-content">
            <p class="pmt-summary-intro">Your organization's Systems Engineering practices have been captured and will be used to personalize learning objectives.</p>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="Processes">{{ pmtContext?.processes || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Methods">{{ pmtContext?.methods || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Tools">{{ pmtContext?.tools || '—' }}</el-descriptions-item>
            </el-descriptions>
          </div>
          <el-button @click="showPMTEdit = true" size="small">
            <el-icon><Edit /></el-icon>
            Edit SE Practices
          </el-button>
        </el-card>
      </div>

      <!-- SECTION 3: Prerequisites & Generation -->
      <div class="section-container">
        <h2 class="section-heading">
          <el-icon><MagicStick /></el-icon>
          Generate Learning Objectives
        </h2>

        <el-card class="generation-card">
          <!-- Prerequisites Check - New Design -->
          <div v-if="prerequisites" class="prerequisites-grid">
            <div
              class="prerequisite-card"
              :class="{ 'prerequisite-complete': prerequisites.hasAssessments }"
            >
              <div class="prerequisite-icon">
                <el-icon :size="32" :color="prerequisites.hasAssessments ? '#67C23A' : '#909399'">
                  <component :is="prerequisites.hasAssessments ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
                </el-icon>
              </div>
              <div class="prerequisite-content">
                <h4>Competency Assessments</h4>
                <p v-if="assessmentStats">
                  {{ assessmentStats.usersWithAssessments }} / {{ assessmentStats.totalUsers }} users completed
                </p>
                <p v-else>Checking assessment status...</p>
                <el-tag
                  :type="prerequisites.hasAssessments ? 'success' : 'info'"
                  size="small"
                  effect="plain"
                >
                  {{ prerequisites.hasAssessments ? 'Ready' : 'Pending' }}
                </el-tag>
              </div>
            </div>

            <div
              class="prerequisite-card"
              :class="{ 'prerequisite-complete': prerequisites.hasStrategies }"
            >
              <div class="prerequisite-icon">
                <el-icon :size="32" :color="prerequisites.hasStrategies ? '#67C23A' : '#909399'">
                  <component :is="prerequisites.hasStrategies ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
                </el-icon>
              </div>
              <div class="prerequisite-content">
                <h4>Training Strategies</h4>
                <p>{{ selectedStrategiesCount }} {{ selectedStrategiesCount === 1 ? 'strategy' : 'strategies' }} selected</p>
                <el-tag
                  :type="prerequisites.hasStrategies ? 'success' : 'warning'"
                  size="small"
                  effect="plain"
                >
                  {{ prerequisites.hasStrategies ? 'Configured' : 'Not Selected' }}
                </el-tag>
              </div>
            </div>

            <div
              v-if="prerequisites.needsPMT"
              class="prerequisite-card"
              :class="{ 'prerequisite-complete': prerequisites.hasPMT }"
            >
              <div class="prerequisite-icon">
                <el-icon :size="32" :color="prerequisites.hasPMT ? '#67C23A' : '#909399'">
                  <component :is="prerequisites.hasPMT ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
                </el-icon>
              </div>
              <div class="prerequisite-content">
                <h4>SE Practices</h4>
                <p>Organization-specific processes, methods, tools</p>
                <el-tag
                  :type="prerequisites.hasPMT ? 'success' : 'warning'"
                  size="small"
                  effect="plain"
                >
                  {{ prerequisites.hasPMT ? 'Configured' : 'Required' }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- Loading Prerequisites -->
          <div v-else class="prerequisites-loading">
            <el-icon class="is-loading" :size="32"><Loading /></el-icon>
            <p style="margin-top: 16px; color: var(--el-text-color-secondary);">Checking prerequisites...</p>
          </div>

          <el-divider />

          <!-- Generation/Results Section -->
          <div class="generation-section">
            <!-- Generating State with AI Info -->
            <div v-if="isGenerating" class="generating-overlay">
              <div class="generating-content">
                <el-icon class="is-loading generating-icon" :size="48"><Loading /></el-icon>
                <h3>Generating Learning Objectives</h3>
                <p class="generating-message">
                  Our AI is analyzing competency assessments and customizing learning objectives
                  with your organization's processes, methods, and tools.
                </p>
                <p class="generating-note">
                  This may take 30-60 seconds. Please wait...
                </p>
                <el-progress
                  :percentage="100"
                  status="success"
                  :indeterminate="true"
                  :stroke-width="8"
                  style="width: 80%; margin-top: 16px;"
                />
              </div>
            </div>

            <!-- Results Exist State -->
            <template v-else-if="learningObjectives">
              <div class="results-ready-section">
                <div class="results-ready-header">
                  <el-icon :size="32" color="#67C23A"><SuccessFilled /></el-icon>
                  <div class="results-ready-text">
                    <h4>Learning Objectives Ready</h4>
                    <p>Your learning objectives have been generated and are ready to view.</p>
                  </div>
                </div>
                <div class="results-ready-actions">
                  <el-button type="primary" size="large" @click="viewResults">
                    <el-icon><View /></el-icon>
                    View Results
                  </el-button>
                  <el-button
                    type="default"
                    size="small"
                    @click="showGenerationDialog"
                    :disabled="!prerequisites?.readyToGenerate"
                    style="margin-left: 12px;"
                  >
                    <el-icon><Refresh /></el-icon>
                    Regenerate
                  </el-button>
                </div>
                <p class="regenerate-hint">
                  <el-icon><InfoFilled /></el-icon>
                  Regenerate if you've updated assessments, strategies, or company context.
                </p>
              </div>
            </template>

            <!-- No Results Yet State -->
            <template v-else>
              <p style="margin-bottom: 20px; color: var(--el-text-color-regular);">
                Once all prerequisites are met, click the button below to generate learning objectives
                based on your organization's competency assessments and training strategies.
              </p>
              <el-button
                type="primary"
                size="large"
                @click="showGenerationDialog"
                :disabled="!prerequisites?.readyToGenerate"
              >
                <el-icon><MagicStick /></el-icon>
                Generate Learning Objectives
              </el-button>
            </template>
          </div>
        </el-card>
      </div>
      </div>
    </el-card>

    <!-- Generation Confirmation Dialog -->
    <GenerationConfirmDialog
      v-model="showConfirmDialog"
      :assessment-stats="assessmentStats"
      :strategies-count="selectedStrategiesCount"
      :needs-pmt="needsPMT"
      :has-pmt="hasPMT"
      @confirm="handleGenerate"
    />

    <!-- Add Strategy Dialog -->
    <AddStrategyDialog
      v-model="showAddStrategyDialog"
      :strategy-name="recommendedStrategyData?.strategyName || ''"
      :organization-id="organizationId"
      :rationale="recommendedStrategyData?.rationale || ''"
      :gap-summary="recommendedStrategyData?.gapSummary || null"
      :existing-pmt-context="pmtContext"
      @added="handleStrategyAdded"
      @cancelled="handleStrategyDialogCancelled"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/api/axios'
import {
  Loading,
  SuccessFilled,
  CircleClose,
  CircleCheckFilled,
  CircleCloseFilled,
  MagicStick,
  Edit,
  View,
  InfoFilled,
  DocumentChecked,
  TrendCharts,
  DataAnalysis,
  Setting,
  DocumentCopy,
  Refresh,
  Box
} from '@element-plus/icons-vue'
import { usePhase2Task3 } from '@/composables/usePhase2Task3'
import AssessmentMonitor from './AssessmentMonitor.vue'
import PMTContextForm from './PMTContextForm.vue'
import GenerationConfirmDialog from './GenerationConfirmDialog.vue'
import AddStrategyDialog from './AddStrategyDialog.vue'
import ExistingTrainingsSelector from './ExistingTrainingsSelector.vue'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const router = useRouter()

// Store the user's latest assessment ID for back navigation
const userLatestAssessmentId = ref(null)

// Use composable for state management
const {
  isLoading,
  assessmentStats,
  selectedStrategiesCount,
  pmtContext,
  learningObjectives,
  prerequisites,
  pathway,
  fetchData,
  generateObjectives,
  addRecommendedStrategy,
  refreshData
} = usePhase2Task3(props.organizationId)

// Local state
const showConfirmDialog = ref(false)
const showAddStrategyDialog = ref(false)
const showPMTEdit = ref(false)
const recommendedStrategyData = ref(null)
const isGenerating = ref(false)

// Computed properties
const pathwayTagType = computed(() => {
  return pathway.value === 'TASK_BASED' ? 'warning' : 'success'
})

const hasObjectives = computed(() => {
  return learningObjectives.value !== null && Object.keys(learningObjectives.value).length > 0
})

const needsPMT = computed(() => {
  return prerequisites.value?.needsPMT || false
})

const hasPMT = computed(() => {
  return prerequisites.value?.hasPMT || false
})

const prerequisitesStep = computed(() => {
  if (!prerequisites.value) return 0

  let step = 0
  if (prerequisites.value.hasAssessments) step++
  if (prerequisites.value.hasStrategies) step++
  if (prerequisites.value.needsPMT && prerequisites.value.hasPMT) step++

  return step
})

// Fetch user's latest assessment ID for back navigation
const fetchUserLatestAssessment = async () => {
  try {
    const response = await axios.get('/api/latest_competency_overview', {
      params: { organization_id: props.organizationId }
    })

    if (response.data && response.data.assessment_id) {
      userLatestAssessmentId.value = response.data.assessment_id
      console.log('[Phase2Task3Dashboard] User latest assessment ID:', userLatestAssessmentId.value)
    }
  } catch (error) {
    console.error('[Phase2Task3Dashboard] Error fetching user latest assessment:', error)
  }
}

// Methods
const handleBack = () => {
  // Navigate to user's assessment results if available, otherwise to Phase 2
  if (userLatestAssessmentId.value) {
    router.push(`/app/assessments/${userLatestAssessmentId.value}/results`)
  } else {
    router.push('/app/phases/2')
  }
}

const showGenerationDialog = () => {
  showConfirmDialog.value = true
}

const handleGenerate = async () => {
  try {
    isGenerating.value = true
    showConfirmDialog.value = false

    await generateObjectives()

    ElMessage.success('Learning objectives generated successfully!')

    // Navigate to results page
    router.push({
      name: 'Phase2Task3Results',
      params: { orgId: props.organizationId }
    })
  } catch (error) {
    console.error('[Phase2Task3] Generation error:', error)
    ElMessage.error(error.message || 'Failed to generate learning objectives')
  } finally {
    isGenerating.value = false
  }
}

const viewResults = () => {
  // Navigate to the results page
  router.push({
    name: 'Phase2Task3Results',
    params: { orgId: props.organizationId }
  })
}

const handleRegenerate = async () => {
  try {
    isGenerating.value = true
    await generateObjectives({ force: true })
    ElMessage.success('Learning objectives regenerated successfully!')
  } catch (error) {
    console.error('[Phase2Task3] Regeneration error:', error)
    ElMessage.error('Failed to regenerate learning objectives')
  } finally {
    isGenerating.value = false
  }
}

const handlePMTSaved = (savedContext) => {
  pmtContext.value = savedContext
  showPMTEdit.value = false  // Hide the edit form
  ElMessage.success('PMT context saved successfully')
  refreshData()
}

const handleExistingTrainingsUpdated = () => {
  // Refresh prerequisites/data since exclusions changed
  refreshData()
  ElMessage.info('Note: You may need to regenerate learning objectives to apply changes.')
}

const handleExport = (format) => {
  // Export functionality handled by LearningObjectivesView
  console.log('[Phase2Task3] Export requested:', format)
}

const handleRecommendationAction = (recommendation) => {
  console.log('[Phase2Task3] Recommendation action:', recommendation)

  // Check if this is an "add strategy" action
  if (recommendation.action === 'add_strategy' || recommendation.actionType === 'add_strategy') {
    // Extract strategy name from recommendation
    const strategyName = recommendation.strategyName || recommendation.message?.match(/'([^']+)'/)?.[1] || ''

    recommendedStrategyData.value = {
      strategyName,
      rationale: recommendation.rationale || recommendation.message || '',
      gapSummary: recommendation.gapSummary || null
    }

    showAddStrategyDialog.value = true
  }
}

const handleStrategyAdded = async (strategyData) => {
  try {
    console.log('[Phase2Task3] Adding strategy:', strategyData)

    // Call the composable's addRecommendedStrategy method
    await addRecommendedStrategy(strategyData.strategyName, strategyData.pmtContext)

    ElMessage.success(`Strategy "${strategyData.strategyName}" added successfully! Objectives regenerated.`)

    // Close dialog
    showAddStrategyDialog.value = false
    recommendedStrategyData.value = null

    // Refresh data (results will appear automatically in Section 5)
    await refreshData()
  } catch (error) {
    console.error('[Phase2Task3] Error adding strategy:', error)
    ElMessage.error(error.message || 'Failed to add strategy')
    // Keep dialog open on error so user can try again
  }
}

const handleStrategyDialogCancelled = () => {
  showAddStrategyDialog.value = false
  recommendedStrategyData.value = null
}

// Lifecycle
onMounted(async () => {
  console.log('[Phase2Task3] Mounted with organizationId:', props.organizationId)

  // Fetch user's latest assessment for back navigation
  await fetchUserLatestAssessment()

  // Fetch main data
  await fetchData()

  // Single page design shows all sections
  // Results link (Section 4) will automatically appear if objectives exist
})
</script>

<style scoped>
.phase2-task3-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.header-content h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.subtitle {
  color: var(--el-text-color-secondary);
  margin: 0;
  font-size: 14px;
}

.loading-card {
  margin-top: 24px;
}

/* Main Content Card Wrapper */
.main-content-card {
  margin-top: 24px;
}

/* Consolidated single page view */
.consolidated-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Overview Card */
.overview-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-left: 4px solid #409EFF;
  border-radius: 8px;
  padding: 20px 24px;
}

.overview-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.overview-icon {
  flex-shrink: 0;
  background: #E8F4FF;
  padding: 12px;
  border-radius: 8px;
}

.overview-text {
  flex: 1;
}

.overview-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #1E293B;
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-description {
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 16px 0;
  color: #475569;
}

.overview-process {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.process-step {
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: #334155;
  border: 1px solid #E2E8F0;
}

.overview-card :deep(.el-alert) {
  margin-top: 0;
}

/* Section Container */
.section-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Section Heading */
.section-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #EBEEF5;
}

.section-heading .el-icon {
  font-size: 24px;
  color: #409EFF;
}

/* PMT Summary Card with visual indicator */
.pmt-summary-card {
  border-left: 4px solid var(--el-color-success);
  background: linear-gradient(135deg, #f0f9eb 0%, #fafafa 100%);
}

.pmt-summary-content {
  margin-bottom: 16px;
}

.pmt-summary-intro {
  margin-bottom: 16px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Prerequisites Grid */
.prerequisites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.prerequisite-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: #F5F7FA;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.prerequisite-card.prerequisite-complete {
  background: #F0F9FF;
  border-color: #67C23A;
}

.prerequisite-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.prerequisite-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prerequisite-content {
  flex: 1;
  min-width: 0;
}

.prerequisite-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.prerequisite-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

/* Generation section styling */
.generation-section {
  text-align: center;
  padding: 24px 0;
}

.generation-section p {
  margin-bottom: 16px;
  color: var(--el-text-color-secondary);
}

/* Generating Overlay */
.generating-overlay {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4ff 100%);
  border: 2px solid #409EFF;
  border-radius: 12px;
  padding: 40px 24px;
}

.generating-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.generating-icon {
  color: #409EFF;
}

.generating-content h3 {
  margin: 8px 0 0 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.generating-message {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  max-width: 500px;
  margin: 0;
}

.generating-note {
  font-size: 13px;
  color: #909399;
  margin: 0;
  font-style: italic;
}

/* Prerequisites loading state */
.prerequisites-loading {
  text-align: center;
  padding: 40px 20px;
}

/* Results Link Card - Compact */
.results-link-card-compact {
  border-left: 4px solid var(--el-color-success);
  background: #f0f9eb;
  border-radius: 8px;
  padding: 16px 20px;
}

.results-link-content-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.results-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.results-text {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* Results Ready Section - New consolidated design */
.results-ready-section {
  text-align: center;
  padding: 20px 0;
}

.results-ready-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.results-ready-text h4 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.results-ready-text p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.results-ready-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.regenerate-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .overview-content {
    flex-direction: column;
  }

  .overview-icon {
    align-self: center;
  }

  .prerequisites-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    font-size: 18px;
  }

  .overview-title {
    font-size: 16px;
  }

  .overview-description {
    font-size: 13px;
  }

  .overview-card :deep(.el-card__body) {
    padding: 16px;
  }

  .overview-process {
    gap: 12px;
  }

  .process-step {
    font-size: 12px;
    padding: 6px 10px;
  }
}
</style>
