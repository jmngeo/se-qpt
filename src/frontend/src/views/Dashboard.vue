<template>
  <div class="dashboard">
    <!-- Welcome Header -->
    <div class="dashboard-header">
      <div class="welcome-section">
        <h1 class="welcome-title">Welcome back, {{ authStore.userName }}!</h1>
        <p class="welcome-subtitle">Continue your systems engineering qualification journey</p>
        <div v-if="authStore.isAdmin && organizationCode" class="org-code-badge">
          <el-tag type="info" size="large" effect="plain">
            <span style="font-weight: 600;">Organization Code:</span>
            <span style="font-family: monospace; margin-left: 8px; font-size: 16px; font-weight: bold;">{{ organizationCode }}</span>
          </el-tag>
          <el-tooltip content="Share this code with employees to join your organization" placement="right">
            <el-icon style="margin-left: 8px; cursor: help;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="dashboard-grid">
      <el-row :gutter="24">
        <!-- Left Column -->
        <el-col :span="16">
          <!-- Current Assessment -->
          <el-card class="section-card" v-if="currentAssessment">
            <template #header>
              <div class="card-header">
                <h3>Current Assessment</h3>
                <el-tag :type="getStatusType(currentAssessment.status)">
                  {{ currentAssessment.status }}
                </el-tag>
              </div>
            </template>

            <div class="current-assessment">
              <div class="assessment-info">
                <h4>{{ currentAssessment.type }} Assessment</h4>
                <p>Phase {{ currentAssessment.phase }} • {{ currentAssessment.organization }}</p>

                <div class="progress-section">
                  <div class="progress-header">
                    <span>Progress</span>
                    <span>{{ currentAssessment.progress }}%</span>
                  </div>
                  <el-progress
                    :percentage="currentAssessment.progress"
                    :color="getProgressColor(currentAssessment.progress)"
                  />
                </div>
              </div>

              <div class="assessment-actions">
                <el-button
                  type="primary"
                  @click="continueAssessment(currentAssessment)"
                  v-if="currentAssessment.status !== 'completed'"
                >
                  Continue Assessment
                </el-button>
                <el-button
                  @click="viewResults(currentAssessment)"
                  v-if="currentAssessment.status === 'completed'"
                >
                  View Results
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- Role-Based SE-QPT Workflow -->
          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <h3>{{ workflowTitle }}</h3>
                <el-tag :type="authStore.isAdmin ? 'danger' : 'success'">
                  {{ authStore.isAdmin ? 'Admin' : 'Employee' }}
                </el-tag>
              </div>
            </template>

            <!-- Admin Workflow: Phase 1 Setup + Admin Competency Assessment -->
            <div v-if="authStore.isAdmin" class="admin-workflow">
              <div class="workflow-description">
                <el-alert
                  title="Admin Complete Journey"
                  description="As an organizational admin, complete all phases: prepare SE training foundation (Phase 1), identify requirements and competencies (Phase 2), create macro plan (Phase 3), and develop detailed implementation (Phase 4)."
                  type="info"
                  :closable="false"
                  show-icon
                />
              </div>

              <div class="phases-navigation">
                <div
                  v-for="(phase, index) in adminPhases"
                  :key="index"
                  class="phase-card"
                  :class="{ completed: phase.completed, active: phase.active, disabled: phase.disabled }"
                  @click="!phase.disabled && navigateToPhase(phase.route)"
                >
                  <div class="phase-indicator">
                    <div class="phase-number">{{ index + 1 }}</div>
                    <el-icon v-if="phase.completed" class="completion-icon">
                      <SuccessFilled />
                    </el-icon>
                  </div>

                  <div class="phase-content">
                    <h4 class="phase-title">{{ phase.title }}</h4>
                    <p class="phase-description">{{ phase.description }}</p>

                    <div class="phase-progress" v-if="phase.progress !== undefined">
                      <el-progress
                        :percentage="phase.progress"
                        :show-text="false"
                        :stroke-width="4"
                      />
                    </div>
                  </div>

                  <div class="phase-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </div>

            <!-- Employee Workflow: Organization Context + Personal Assessments -->
            <div v-else class="employee-workflow">
              <div class="workflow-description">
                <el-alert
                  title="Employee Journey"
                  description="View your organization's SE training preparation (Phase 1), then complete your personal competency self-assessment (Phase 2)."
                  type="success"
                  :closable="false"
                  show-icon
                />
              </div>

              <div class="phases-navigation">
                <div
                  v-for="(phase, index) in employeePhases"
                  :key="index"
                  class="phase-card"
                  :class="{ completed: phase.completed, active: phase.active, disabled: phase.disabled }"
                  @click="!phase.disabled && navigateToPhase(phase.route)"
                >
                  <div class="phase-indicator">
                    <div class="phase-number">{{ index + 1 }}</div>
                    <el-icon v-if="phase.completed" class="completion-icon">
                      <SuccessFilled />
                    </el-icon>
                  </div>

                  <div class="phase-content">
                    <h4 class="phase-title">{{ phase.title }}</h4>
                    <p class="phase-description">{{ phase.description }}</p>

                    <div class="phase-progress" v-if="phase.progress !== undefined">
                      <el-progress
                        :percentage="phase.progress"
                        :show-text="false"
                        :stroke-width="4"
                      />
                    </div>
                  </div>

                  <div class="phase-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

        </el-col>

        <!-- Right Column -->
        <el-col :span="8">
          <!-- Quick Stats -->
          <el-card class="section-card">
            <template #header>
              <h3>Your Competency Overview</h3>
            </template>

            <div class="competency-overview">
              <div v-if="competencyStats.length > 0">
                <div
                  v-for="competency in competencyStats"
                  :key="competency.name"
                  class="competency-item"
                >
                  <div class="competency-info">
                    <span class="competency-name">{{ competency.name }}</span>
                    <span class="competency-score">{{ competency.score }}/{{ competency.requiredScore }}</span>
                  </div>
                  <el-progress
                    :percentage="(competency.score / competency.requiredScore) * 100"
                    :show-text="false"
                    :stroke-width="6"
                    :color="getCompetencyColor(competency.score)"
                  />
                  <div class="competency-status">
                    <span class="status-label">
                      {{ competency.gap <= 0 ? 'Proficient' : `Gap: ${competency.gap.toFixed(1)} levels` }}
                    </span>
                  </div>
                </div>

                <el-button type="text" @click="viewAllCompetencies" class="view-all-btn">
                  View All Competencies →
                </el-button>
              </div>

              <div v-else class="no-competencies">
                <el-icon size="48" class="empty-icon"><User /></el-icon>
                <p>Complete Phase 2 to identify competencies and view your profile</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssessmentStore } from '@/stores/assessment'
import { usePhaseProgression } from '@/composables/usePhaseProgression'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Stores and router
const router = useRouter()
const authStore = useAuthStore()
const assessmentStore = useAssessmentStore()

// Phase progression - must be initialized at top level for reactivity
const { canAccessPhase, getPhaseStatus, getPhaseTitle, getPhaseDescription, checkPhaseCompletion } = usePhaseProgression()

// State
const competencyStats = ref([])
const organizationCode = ref(null)
const phaseDataLoaded = ref(false) // Track when phase completion data is loaded

// Computed
const currentAssessment = computed(() => {
  return assessmentStore.inProgressAssessments[0] || null
})

// Role-based workflow computed properties
const workflowTitle = computed(() => {
  return authStore.isAdmin ? 'Admin Complete Workflow' : 'Employee Assessment Journey'
})

const adminPhases = computed(() => {
  // Force re-computation when phase data is loaded
  console.log('[Dashboard] Computing adminPhases, phaseDataLoaded:', phaseDataLoaded.value)
  if (!phaseDataLoaded.value) return []

  console.log('[Dashboard] Computing adminPhases with canAccessPhase(2):', canAccessPhase(2))

  return [
    {
      title: getPhaseTitle(1),
      description: getPhaseDescription(1),
      completed: getPhaseStatus(1) === 'completed',
      active: getPhaseStatus(1) === 'available',
      progress: 0,
      route: '/app/phases/1',
      disabled: false
    },
    {
      title: getPhaseTitle(2),
      description: getPhaseDescription(2),
      completed: getPhaseStatus(2) === 'completed',
      active: getPhaseStatus(2) === 'available',
      progress: 0,
      route: '/app/phases/2',
      disabled: !canAccessPhase(2)
    },
    {
      title: getPhaseTitle(3),
      description: getPhaseDescription(3),
      completed: getPhaseStatus(3) === 'completed',
      active: getPhaseStatus(3) === 'available',
      progress: undefined,
      route: '/app/phases/3',
      disabled: !canAccessPhase(3)
    },
    {
      title: getPhaseTitle(4),
      description: getPhaseDescription(4),
      completed: getPhaseStatus(4) === 'completed',
      active: getPhaseStatus(4) === 'available',
      progress: undefined,
      route: '/app/phases/4',
      disabled: !canAccessPhase(4)
    }
  ]
})

const employeePhases = computed(() => {
  // Force re-computation when phase data is loaded
  if (!phaseDataLoaded.value) return []

  // Employees only see Phases 1 and 2 (Phases 3-4 are admin-only)
  return [
    {
      title: 'Organization SE Training Preparation',
      description: 'View organizational SE maturity, identified roles, and training strategy',
      completed: getPhaseStatus(1) === 'completed',
      active: getPhaseStatus(1) === 'available',
      progress: undefined,
      route: '/app/phases/1',
      disabled: false
    },
    {
      title: 'Competency Self-Assessment',
      description: 'Complete your personal competency assessment and view your results',
      completed: getPhaseStatus(2) === 'completed',
      active: getPhaseStatus(2) === 'available',
      progress: 0,
      route: '/app/phases/2',
      disabled: !canAccessPhase(2)
    }
  ]
})

// Methods
const continueAssessment = (assessment) => {
  router.push(`/app/assessments/${assessment.uuid}/take`)
}

const viewResults = (assessment) => {
  router.push(`/app/assessments/${assessment.uuid}`)
}

const navigateToPhase = (route) => {
  if (route && !route.includes('undefined')) {
    router.push(route)
  }
}

const viewAllCompetencies = () => {
  router.push('/app/phases/2')
}

const getStatusType = (status) => {
  const statusMap = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const getProgressColor = (progress) => {
  if (progress < 30) return '#f56c6c'
  if (progress < 70) return '#e6a23c'
  return '#67c23a'
}

const getCompetencyColor = (score) => {
  if (score < 2) return '#f56c6c'
  if (score < 3.5) return '#e6a23c'
  return '#67c23a'
}


const loadDashboardData = async () => {
  // Load assessments
  // TODO: Temporarily disabled for MVP - await assessmentStore.fetchAssessments()

  // Initialize empty arrays - real data will come from actual assessments
  competencyStats.value = []

  // Refresh phase completion status (especially important for employees)
  console.log('[Dashboard] onMounted - starting phase check')
  phaseDataLoaded.value = false

  await checkPhaseCompletion()
  console.log('[Dashboard] onMounted - phase check complete, setting phaseDataLoaded to true')
  phaseDataLoaded.value = true // Trigger computed properties to update

  // Fetch organization code from localStorage (stored during registration)
  // This works for both admin and employee users
  const storedOrgCode = localStorage.getItem('user_organization_code')
  if (storedOrgCode) {
    organizationCode.value = storedOrgCode
  }

  // Fetch latest competency overview
  try {
    // Get token from localStorage (auth store doesn't restore it on page load)
    const token = localStorage.getItem('se_qpt_token') || authStore.token
    console.log('[Dashboard] Fetching competency overview, token exists:', !!token)

    if (token) {
      console.log('[Dashboard] Making request to /api/latest_competency_overview')
      const response = await fetch('/api/latest_competency_overview', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      console.log('[Dashboard] Response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('[Dashboard] Competency overview loaded:', data)

        // Map backend data to display format
        competencyStats.value = data.competencies.map(comp => ({
          name: comp.competency_name,
          score: comp.current_score,
          requiredScore: comp.required_score,
          area: comp.competency_area,
          gap: comp.gap
        }))

        console.log('[Dashboard] Competency stats set:', competencyStats.value)
      } else {
        const errorText = await response.text()
        console.error('[Dashboard] Error response:', response.status, errorText)
      }
    } else {
      console.warn('[Dashboard] No auth token available for competency overview')
    }
  } catch (error) {
    console.error('[Dashboard] Error loading competency overview:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.welcome-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.welcome-subtitle {
  color: #6c757d;
  font-size: 1.1rem;
}

.dashboard-grid {
  gap: 24px;
}

.section-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.current-assessment {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.assessment-info {
  flex: 1;
}

.assessment-info h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.assessment-info p {
  margin: 0 0 20px 0;
  color: #6c757d;
}

.progress-section {
  margin-top: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #6c757d;
}

.workflow-description {
  margin-bottom: 24px;
}

.phases-navigation {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.phase-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.phase-card:hover {
  border-color: #409eff;
  background: #f8f9fa;
}

.phase-card.completed {
  border-color: #67c23a;
  background: #f0f9f2;
}

.phase-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.phase-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f5f5f5;
}

.phase-card.disabled:hover {
  border-color: #e9ecef;
  background: #f5f5f5;
}

.phase-indicator {
  position: relative;
  flex-shrink: 0;
}

.phase-number {
  width: 48px;
  height: 48px;
  background: #e9ecef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #6c757d;
}

.phase-card.active .phase-number {
  background: #409eff;
  color: white;
}

.phase-card.completed .phase-number {
  background: #67c23a;
  color: white;
}

.completion-icon {
  position: absolute;
  top: -4px;
  right: -4px;
  background: white;
  border-radius: 50%;
  color: #67c23a;
  font-size: 20px;
}

.phase-content {
  flex: 1;
}

.phase-title {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.phase-description {
  margin: 0 0 12px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.phase-progress {
  margin-top: 12px;
}

.phase-arrow {
  color: #6c757d;
  flex-shrink: 0;
}


.competency-overview {
  min-height: 200px;
}

.competency-item {
  margin-bottom: 20px;
}

.competency-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.competency-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.competency-score {
  font-weight: 600;
  color: #409eff;
  font-size: 0.9rem;
}

.competency-status {
  margin-top: 4px;
  text-align: right;
}

.status-label {
  font-size: 0.75rem;
  color: #909399;
  font-style: italic;
}

.view-all-btn {
  margin-top: 16px;
  color: #409eff;
  font-size: 0.9rem;
}

.no-competencies {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.no-competencies p {
  margin-bottom: 16px;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }

  .current-assessment {
    flex-direction: column;
    gap: 16px;
  }
}
</style>