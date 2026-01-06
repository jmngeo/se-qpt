<template>
  <div class="phase-three">
    <!-- Phase Header -->
    <div class="phase-header">
      <div class="phase-indicator">
        <div class="phase-number">3</div>
        <div class="phase-title">
          <h1>Phase 3: Macro Planning</h1>
          <p>Building Trainings Structure and Plan</p>
        </div>
      </div>

      <!-- Overall Progress -->
      <div class="phase-progress">
        <el-progress
          :percentage="overallProgress"
          :color="progressColors"
          :stroke-width="10"
        />
        <span class="progress-text">{{ overallProgress }}% Complete</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingConfig" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>Loading Phase 3 configuration...</p>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Task Navigation Cards (Dashboard View) -->
      <div v-if="currentTask === 0" class="dashboard-view">
        <div class="tasks-overview">
          <h2>Phase 3 Tasks</h2>
          <p class="tasks-description">
            Complete these three tasks to plan your SE training program structure,
            select learning formats, and generate timeline estimates.
          </p>
        </div>

        <div class="task-cards">
          <!-- Task 1: Training Structure -->
          <div
            class="task-card"
            :class="{
              'completed': taskStatus.task1,
              'active': !taskStatus.task1
            }"
            @click="goToTask(1)"
          >
            <div class="task-icon">
              <el-icon :size="32"><Grid /></el-icon>
            </div>
            <div class="task-content">
              <h3>Task 1: Training Structure</h3>
              <p>Choose how to organize your training program</p>
              <div class="task-status">
                <el-tag v-if="taskStatus.task1" type="success" effect="plain">
                  <el-icon><View /></el-icon> View / Edit
                </el-tag>
                <el-tag v-else type="primary" effect="plain">
                  <el-icon><ArrowRight /></el-icon> Start
                </el-tag>
              </div>
              <div v-if="taskStatus.task1 && selectedView" class="task-result">
                Selected: {{ selectedView === 'competency_level' ? 'Competency-Level Based' : 'Role-Clustered Based' }}
              </div>
            </div>
          </div>

          <!-- Task 2: Learning Formats -->
          <div
            class="task-card"
            :class="{
              'completed': taskStatus.task2,
              'active': taskStatus.task1 && !taskStatus.task2,
              'disabled': !taskStatus.task1 && !taskStatus.task2
            }"
            @click="(taskStatus.task1 || taskStatus.task2) && goToTask(2)"
          >
            <div class="task-icon">
              <el-icon :size="32"><Reading /></el-icon>
            </div>
            <div class="task-content">
              <h3>Task 2: Learning Formats</h3>
              <p>Select learning format for each training module</p>
              <div class="task-status">
                <el-tag v-if="taskStatus.task2" type="success" effect="plain">
                  <el-icon><View /></el-icon> View / Edit
                </el-tag>
                <el-tag v-else-if="taskStatus.task1" type="primary" effect="plain">
                  <el-icon><ArrowRight /></el-icon> Continue
                </el-tag>
                <el-tag v-else type="info" effect="plain">
                  <el-icon><Lock /></el-icon> Locked
                </el-tag>
              </div>
              <div v-if="taskProgress.modulesConfigured > 0" class="task-result">
                {{ taskProgress.modulesConfigured }}/{{ taskProgress.totalModules }} modules configured
              </div>
            </div>
          </div>

          <!-- Task 3: Timeline Planning -->
          <div
            class="task-card"
            :class="{
              'completed': taskStatus.task3,
              'active': taskStatus.task2 && !taskStatus.task3,
              'disabled': !taskStatus.task2 && !taskStatus.task3
            }"
            @click="(taskStatus.task2 || taskStatus.task3) && goToTask(3)"
          >
            <div class="task-icon">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="task-content">
              <h3>Task 3: Timeline Planning</h3>
              <p>View LLM-generated timeline estimates</p>
              <div class="task-status">
                <el-tag v-if="taskStatus.task3" type="success" effect="plain">
                  <el-icon><View /></el-icon> View / Edit
                </el-tag>
                <el-tag v-else-if="taskStatus.task2" type="primary" effect="plain">
                  <el-icon><ArrowRight /></el-icon> Continue
                </el-tag>
                <el-tag v-else type="info" effect="plain">
                  <el-icon><Lock /></el-icon> Locked
                </el-tag>
              </div>
              <div v-if="taskStatus.task3" class="task-result">
                Timeline generated
              </div>
            </div>
          </div>
        </div>

        <!-- Phase 3 Complete Banner -->
        <div v-if="taskStatus.task3" class="phase-complete-banner">
          <div class="complete-banner-content">
            <div class="banner-header">
              <el-icon :size="24" color="#67C23A"><CircleCheckFilled /></el-icon>
              <span class="banner-title">All Tasks Complete</span>
            </div>
            <p>Your training program structure and timeline are ready. Click on any task above to review or modify your selections, or complete Phase 3 to proceed.</p>
            <div class="banner-actions">
              <el-button
                type="success"
                size="large"
                :loading="exporting"
                @click="exportToExcel"
              >
                <el-icon><Download /></el-icon>
                Export to Excel
              </el-button>
              <el-button type="primary" size="large" @click="proceedToPhase4">
                Complete Phase 3 &amp; Proceed
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Task 1 Content -->
      <div v-else-if="currentTask === 1" class="task-content-area">
        <div class="task-header">
          <el-button text @click="backToDashboard">
            <el-icon><ArrowLeft /></el-icon>
            Back to Overview
          </el-button>
          <div class="task-title">
            <span class="task-number">Task 1</span>
            <h2>Choose Training Structure</h2>
          </div>
        </div>

        <el-card class="task-card-content">
          <TrainingStructureSelection
            :organization-id="organizationId"
            @structure-selected="handleStructureSelected"
            @completed="handleTask1Completed"
          />
        </el-card>
      </div>

      <!-- Task 2 Content -->
      <div v-else-if="currentTask === 2" class="task-content-area">
        <div class="task-header">
          <el-button text @click="backToDashboard">
            <el-icon><ArrowLeft /></el-icon>
            Back to Overview
          </el-button>
          <div class="task-title">
            <span class="task-number">Task 2</span>
            <h2>Select Learning Formats</h2>
          </div>
        </div>

        <el-card class="task-card-content">
          <LearningFormatSelection
            :organization-id="organizationId"
            :selected-view="selectedView"
            @back="goToTask(1)"
            @completed="handleTask2Completed"
          />
        </el-card>
      </div>

      <!-- Task 3 Content -->
      <div v-else-if="currentTask === 3" class="task-content-area">
        <div class="task-header">
          <el-button text @click="backToDashboard">
            <el-icon><ArrowLeft /></el-icon>
            Back to Overview
          </el-button>
          <div class="task-title">
            <span class="task-number">Task 3</span>
            <h2>Timeline Planning</h2>
          </div>
        </div>

        <el-card class="task-card-content">
          <TimelinePlanning
            :organization-id="organizationId"
            @back="goToTask(2)"
            @completed="handleTask3Completed"
          />
        </el-card>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Loading, Grid, Reading, Calendar, Check, ArrowRight, ArrowLeft,
  Lock, CircleCheckFilled, View, Download
} from '@element-plus/icons-vue'
import axios from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

// Components
import TrainingStructureSelection from '@/components/phase3/task1/TrainingStructureSelection.vue'
import LearningFormatSelection from '@/components/phase3/task2/LearningFormatSelection.vue'
import TimelinePlanning from '@/components/phase3/task3/TimelinePlanning.vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const loadingConfig = ref(true)
const organizationId = ref(null)
const currentTask = ref(0) // 0 = dashboard, 1-3 = tasks
const selectedView = ref('competency_level')
const exporting = ref(false)
const taskStatus = ref({
  task1: false,
  task2: false,
  task3: false
})
const taskProgress = ref({
  totalModules: 0,
  modulesConfigured: 0
})

// Progress colors
const progressColors = [
  { color: '#F56C6C', percentage: 25 },
  { color: '#E6A23C', percentage: 50 },
  { color: '#409EFF', percentage: 75 },
  { color: '#67C23A', percentage: 100 }
]

// Computed
const overallProgress = computed(() => {
  let progress = 0
  if (taskStatus.value.task1) progress += 33
  if (taskStatus.value.task2) progress += 34
  if (taskStatus.value.task3) progress += 33
  return progress
})

// Methods
const initializeOrganization = async () => {
  // Get organization ID from auth store (like PhaseOne does)
  const orgId = authStore.organizationId

  if (!orgId) {
    console.error('[Phase3] No organization ID found in auth store')
    ElMessage.error('Please log in to access Phase 3')
    loadingConfig.value = false
    return
  }

  organizationId.value = orgId
  await loadPhase3Config()
}

const loadPhase3Config = async () => {
  loadingConfig.value = true
  try {
    const response = await axios.get(`/api/phase3/config/${organizationId.value}`)

    if (response.data.success) {
      const config = response.data.config

      // Set task completion status
      taskStatus.value = {
        task1: config.task1_completed || false,
        task2: config.task2_completed || false,
        task3: config.task3_completed || false
      }

      selectedView.value = config.selected_view || 'competency_level'

      // Load module progress if Task 1 is done
      if (taskStatus.value.task1) {
        await loadModuleProgress()
      }
    }
  } catch (error) {
    console.error('Error loading Phase 3 config:', error)
    ElMessage.error('Failed to load Phase 3 configuration')
  } finally {
    loadingConfig.value = false
  }
}

const loadModuleProgress = async () => {
  try {
    const response = await axios.get(`/api/phase3/training-modules/${organizationId.value}`)
    if (response.data.success) {
      const modules = response.data.modules || []
      taskProgress.value = {
        totalModules: modules.length,
        modulesConfigured: modules.filter(m => m.confirmed).length
      }
    }
  } catch (error) {
    console.error('Error loading module progress:', error)
  }
}

const goToTask = (taskNumber) => {
  currentTask.value = taskNumber
}

const backToDashboard = () => {
  currentTask.value = 0
  loadPhase3Config() // Refresh status
}

const handleStructureSelected = (view) => {
  selectedView.value = view
}

const handleTask1Completed = () => {
  taskStatus.value.task1 = true
  goToTask(2)
}

const handleTask2Completed = async () => {
  try {
    // Mark Task 2 as completed in the backend
    await axios.post(`/api/phase3/complete-task2/${organizationId.value}`)
    taskStatus.value.task2 = true
    goToTask(3)
  } catch (error) {
    console.error('Error completing Task 2:', error)
    // Still allow navigation even if API fails
    taskStatus.value.task2 = true
    goToTask(3)
  }
}

const handleTask3Completed = () => {
  taskStatus.value.task3 = true
  ElMessage.success('Timeline generated successfully!')
  backToDashboard()
}

const exportToExcel = async () => {
  if (!organizationId.value) {
    ElMessage.error('Organization not loaded')
    return
  }

  exporting.value = true
  try {
    ElMessage.info('Preparing Excel export...')

    const response = await axios.get(
      `/api/phase3/export/${organizationId.value}`,
      { responseType: 'blob' }
    )

    // Get filename from Content-Disposition header or generate default
    let filename = null
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // Fallback filename
    if (!filename) {
      const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      filename = `Phase3_MacroPlanning_${timestamp}.xlsx`
    }

    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    ElMessage.success('Export completed successfully!')
  } catch (error) {
    console.error('Error exporting Phase 3:', error)
    if (error.response?.status === 400) {
      ElMessage.warning('Please complete all Phase 3 tasks before exporting.')
    } else {
      ElMessage.error('Failed to export. Please try again.')
    }
  } finally {
    exporting.value = false
  }
}

const proceedToPhase4 = async () => {
  try {
    // Mark Phase 3 as complete in the backend
    console.log('[PhaseThree] Marking Phase 3 as complete...')
    await axios.put('/api/organization/phase3-complete')
    ElMessage.success('Phase 3 completed successfully!')
    router.push('/app/dashboard')
  } catch (error) {
    console.error('Error completing Phase 3:', error)
    ElMessage.error('Failed to complete Phase 3. Please try again.')
  }
}

// Initialize
onMounted(async () => {
  // Ensure auth is loaded
  if (!authStore.isAuthenticated) {
    await authStore.checkAuth()
  }
  await initializeOrganization()
})
</script>

<style scoped>
.phase-three {
  min-height: calc(100vh - 120px);
  padding: 24px;
  background: #f5f7fa;
}

.phase-three > * {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

/* Phase Header - Matching Phase 1 design */
.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #26A69A 0%, #00897B 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.3);
}

.phase-indicator {
  display: flex;
  align-items: center;
  gap: 24px;
}

.phase-number {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.phase-title h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
  color: white;
}

.phase-title p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
  color: white;
}

.phase-progress {
  text-align: right;
  min-width: 200px;
}

.phase-progress :deep(.el-progress__text) {
  color: white;
}

.phase-progress :deep(.el-progress-bar__outer) {
  background-color: rgba(255, 255, 255, 0.3);
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-weight: 500;
  color: white;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;
}

.loading-state p {
  margin-top: 16px;
}

/* Dashboard View */
.dashboard-view {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.tasks-overview {
  text-align: center;
  margin-bottom: 32px;
}

.tasks-overview h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.tasks-description {
  margin: 0;
  color: #606266;
  max-width: 600px;
  margin: 0 auto;
}

/* Task Cards - Matching Phase 1 card styling */
.task-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.task-card {
  padding: 24px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.task-card:hover:not(.disabled) {
  border-color: #26A69A;
  box-shadow: 0 4px 16px rgba(0, 137, 123, 0.15);
  transform: translateY(-2px);
}

.task-card.active {
  border-color: #26A69A;
  background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);
}

.task-card.completed {
  border-color: #67C23A;
  background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%);
}

.task-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.task-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #6c757d;
}

.task-card.active .task-icon {
  background: linear-gradient(135deg, #26A69A 0%, #00897B 100%);
  color: white;
}

.task-card.completed .task-icon {
  background: #67C23A;
  color: white;
}

.task-content h3 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
}

.task-content p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #6c757d;
}

.task-status {
  margin-bottom: 8px;
}

.task-result {
  font-size: 12px;
  color: #6c757d;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

/* Phase Complete Banner */
.phase-complete-banner {
  margin-top: 24px;
}

.complete-banner-content {
  padding: 24px;
  background: white;
  border: 1px solid #e9ecef;
  border-left: 4px solid #67C23A;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.banner-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.banner-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.complete-banner-content p {
  margin: 0 0 16px 0;
  color: #6c757d;
  font-size: 14px;
}

.banner-actions {
  display: flex;
  gap: 12px;
}

/* Task Content Area - Matching Phase 1 step-card styling */
.task-content-area {
  animation: fadeIn 0.3s ease;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-number {
  padding: 6px 14px;
  background: linear-gradient(135deg, #26A69A 0%, #00897B 100%);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.task-title h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.task-card-content {
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.task-card-content :deep(.el-card__body) {
  padding: 24px;
}

/* Responsive - Matching Phase 1 responsive patterns */
@media (max-width: 900px) {
  .task-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .phase-three {
    padding: 16px;
  }

  .phase-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .phase-indicator {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .phase-title h1 {
    font-size: 1.5rem;
  }

  .phase-progress {
    width: 100%;
    text-align: center;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .task-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
