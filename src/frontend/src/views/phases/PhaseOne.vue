<template>
  <div class="phase-one">
    <!-- Phase Header -->
    <div class="phase-header" :class="{ 'employee-header': isEmployeeView }">
      <div class="phase-indicator">
        <div class="phase-number">1</div>
        <div class="phase-title">
          <h1 v-if="isEmployeeView">Phase 1: Organization SE Training Preparation</h1>
          <h1 v-else>Phase 1: Prepare SE Training</h1>
          <p v-if="isEmployeeView">View your organization's SE maturity, identified roles, and training strategy</p>
          <p v-else>Assess SE maturity, identify roles, and select training strategy</p>
        </div>
      </div>

      <div class="phase-progress" v-if="!isEmployeeView">
        <el-progress
          :percentage="overallProgress"
          :color="progressColor"
          :stroke-width="8"
        />
        <span class="progress-text">{{ overallProgress }}% Complete</span>
      </div>
    </div>

    <!-- Phase Steps (Admin Only) -->
    <div class="phase-steps" v-if="!isEmployeeView">
      <el-steps :active="currentStep - 1" align-center finish-status="success">
        <el-step title="Maturity Assessment" description="Assess SE maturity level" />
        <el-step title="Roles & Responsibilities" description="Identify roles and responsibilities" />
        <el-step title="Strategy Selection" description="Select training strategy" />
        <el-step title="Review & Confirm" description="Review and complete Phase 1" />
      </el-steps>
    </div>

    <!-- Employee Information Banner -->
    <div class="employee-info-banner" v-if="isEmployeeView">
      <el-alert
        title="Organization SE Training Preparation"
        description="This page shows your organization's Phase 1 results completed by your administrator. These include SE maturity level, identified roles, and selected training strategy."
        type="info"
        show-icon
        :closable="false"
      />
    </div>

    <!-- Step Content -->
    <div class="step-content">
      <!-- Employee View: Phase 1 Results (Same as Admin Review Screen) -->
      <div v-if="isEmployeeView" class="employee-results-view">
        <div class="review-summary">
          <!-- Organization Overview Card -->
          <el-card class="results-card overview-card">
            <template #header>
              <div class="overview-header">
                <el-icon :size="24" color="#1976D2"><OfficeBuilding /></el-icon>
                <h4>Organization Overview</h4>
              </div>
            </template>
            <div class="organization-overview">
              <div class="org-icon-wrapper">
                <div class="org-icon-circle">
                  <el-icon :size="48" color="#1976D2"><OfficeBuilding /></el-icon>
                </div>
              </div>
              <div class="org-info-section">
                <div class="org-name-display">
                  <h2 class="org-name-large">{{ organizationForm.organizationName || 'Your Organization' }}</h2>
                </div>
                <div class="org-size-display">
                  <el-icon :size="18" color="#606266"><User /></el-icon>
                  <span class="size-label">Organization Size:</span>
                  <span class="size-value">{{ getOrganizationSizeLabel(organizationForm.organizationSize) }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Assessment Results -->
          <div class="assessment-results">
            <!-- Row 1: Maturity and Strategy side by side -->
            <div class="results-row-top">
              <!-- Maturity Assessment Results -->
              <el-card class="results-card maturity-card">
                <template #header>
                  <h4>Systems Engineering Maturity Level</h4>
                </template>
                <div class="maturity-results">
                  <div v-if="maturityResults" class="maturity-score-display-vertical">
                    <!-- Circle on top -->
                    <div class="score-circle-centered">
                      <el-progress
                        type="circle"
                        :percentage="Math.round(maturityResults.finalScore)"
                        :width="140"
                        :stroke-width="10"
                        :color="maturityResults.maturityColor"
                      >
                        <template #default>
                          <span style="font-size: 32px; font-weight: bold; color: #303133;">
                            {{ maturityResults.finalScore }}
                          </span>
                          <span style="font-size: 14px; color: #909399; display: block;">/100</span>
                        </template>
                      </el-progress>
                    </div>

                    <!-- Level info below circle -->
                    <div class="maturity-level-info">
                      <h3 :style="{ color: maturityResults.maturityColor }">
                        Level {{ maturityResults.maturityLevel }}: {{ maturityResults.maturityName }}
                      </h3>
                      <p class="level-description">
                        {{ maturityResults.maturityDescription }}
                      </p>
                    </div>

                    <!-- Level meter -->
                    <div class="level-meter">
                      <div class="meter-labels">
                        <span class="meter-label">Initial</span>
                        <span class="meter-label">Developing</span>
                        <span class="meter-label">Defined</span>
                        <span class="meter-label">Managed</span>
                        <span class="meter-label">Optimized</span>
                      </div>
                      <el-progress
                        :percentage="(maturityResults.maturityLevel / 5) * 100"
                        :color="maturityResults.maturityColor"
                        :stroke-width="12"
                        :show-text="false"
                      />
                    </div>

                    <!-- Field scores -->
                    <div class="field-scores-grid">
                      <div class="field-score-item">
                        <span class="field-label">Rollout Scope</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.rolloutScope || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">SE Roles & Processes</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.seRolesProcesses || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">SE Mindset</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.seMindset || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">Knowledge Base</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.knowledgeBase || 0 }}/100</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- Training Strategy Selection Results -->
              <el-card v-if="phase1StrategyData" class="results-card strategy-card">
                <template #header>
                  <h4>Selected Training Strategies</h4>
                </template>
                <div class="strategy-results">
                  <!-- Strategy Count Summary -->
                  <div class="strategy-count-summary-new">
                    <div class="count-badge">
                      <span class="count-number">{{ phase1StrategyData.count }}</span>
                      <span class="count-text">{{ phase1StrategyData.count === 1 ? 'Strategy' : 'Strategies' }}</span>
                    </div>
                  </div>

                  <!-- Strategies List -->
                  <div class="strategies-list-review">
                    <div
                      v-for="(strategy, index) in phase1StrategyData.strategies"
                      :key="`strategy-review-${index}`"
                      class="strategy-review-item-simple"
                    >
                      <!-- Strategy Name -->
                      <h5 class="strategy-name-simple">{{ strategy.strategyName }}</h5>
                    </div>
                  </div>

                  <!-- User Preference -->
                  <div v-if="phase1StrategyData.userPreference" class="user-preference-display">
                    <el-alert type="info" :closable="false" show-icon>
                      <template #title>Secondary Strategy Preference</template>
                      Selected: <strong>{{ formatStrategyName(phase1StrategyData.userPreference) }}</strong>
                    </el-alert>
                  </div>

                  <!-- Next Steps -->
                  <div class="next-steps">
                    <el-alert
                      title="What's Next?"
                      description="Based on these selected training strategies, learning objectives and qualification formats will be generated in Phase 2."
                      type="success"
                      show-icon
                      :closable="false"
                    />
                  </div>
                </div>
              </el-card>
            </div>

            <!-- Row 2: Roles & Target Group (full width) -->
            <div class="results-row-bottom">
              <!-- Identified SE Roles & Target Group Size -->
              <el-card v-if="phase1RolesData && phase1TargetGroupData" class="results-card roles-card">
                <template #header>
                  <h4>Identified SE Roles & Target Group Size</h4>
                </template>
                <div class="roles-results">
                  <!-- Roles Count Summary -->
                  <div class="roles-count-summary">
                    <span class="count-label">{{ phase1RolesData.count }} SE {{ phase1RolesData.count === 1 ? 'Role' : 'Roles' }} Identified</span>
                  </div>

                  <!-- Roles List (if roles exist) -->
                  <div v-if="phase1RolesData.count > 0" class="roles-list-review">
                    <ul class="roles-list">
                      <li
                        v-for="(role, index) in phase1RolesData.roles"
                        :key="`role-review-${index}`"
                        class="role-list-item"
                      >
                        <span class="role-bullet">•</span>
                        <span class="role-name">{{ getRoleName(role) }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- No Roles Note (TASK_BASED pathway) -->
                  <div v-else class="no-roles-note">
                    <el-alert
                      title="No Defined SE Roles"
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      Based on your organization's maturity level, specific SE roles have not yet been defined.
                    </el-alert>
                  </div>

                  <!-- Target Group Size -->
                  <div class="target-group-display">
                    <div class="target-group-inline">
                      <span class="target-label">Target Group Size for Training:</span>
                      <span class="target-size-value-inline">{{ phase1TargetGroupData.label || phase1TargetGroupData.size_range }}</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin View: Assessment Flow -->
      <div v-else class="admin-assessment-flow">
        <!-- Step 1: Organization Information (Hidden for direct navigation) -->
        <el-card v-if="currentStep === 0" class="step-card">
          <template #header>
            <h3>Organization Information</h3>
          </template>

          <el-form :model="organizationForm" :rules="organizationRules" ref="organizationFormRef" label-width="180px">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="Organization Name" prop="organizationName" required>
                  <el-input
                    v-model="organizationForm.organizationName"
                    placeholder="Loading organization name..."
                    readonly
                    disabled
                  />
                  <template #extra>
                    <span style="font-size: 12px; color: #909399;">Organization name from registration</span>
                  </template>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="Organization Size" prop="organizationSize" required>
                  <el-select
                    v-model="organizationForm.organizationSize"
                    placeholder="Select organization size"
                    style="width: 100%"
                  >
                    <el-option label="Small (< 100 employees)" value="small" />
                    <el-option label="Medium (100-1000 employees)" value="medium" />
                    <el-option label="Large (1000-10000 employees)" value="large" />
                    <el-option label="Enterprise (> 10000 employees)" value="enterprise" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <div class="step-actions">
            <el-button type="primary" @click="nextStep" :loading="loading">
              Continue to Maturity Assessment
            </el-button>
          </div>
        </el-card>

        <!-- Step 2: Maturity Assessment -->
        <el-card v-if="currentStep === 1" class="step-card">
          <template #header>
            <div class="card-header">
              <h3>Task 1: Assess SE Maturity Level</h3>
            </div>
          </template>

          <!-- Show Assessment Form -->
          <div v-if="!showMaturityResults">
            <MaturityAssessment
              :existing-data="maturityAnswers"
              @maturity-calculated="handleMaturityCalculated"
              @data-changed="handleMaturityDataChanged"
            />
          </div>

          <!-- Show Results -->
          <div v-else>
            <MaturityResults
              :results="maturityResults"
              @back-to-assessment="resetMaturityAssessment"
              @proceed-to-task2="proceedToRoleIdentification"
            />
          </div>
        </el-card>

        <!-- Step 2: Roles & Responsibilities -->
        <div v-if="currentStep === 2">
          <RoleIdentification
            v-if="maturityResults"
            :maturity-data="maturityResults"
            :existing-roles="phase1RolesData"
            :existing-target-group="phase1TargetGroupData"
            @complete="handleRoleIdentificationComplete"
            @back="previousStep"
          />
          <el-alert
            v-else
            title="Please Complete Maturity Assessment First"
            description="Maturity assessment must be completed before identifying SE roles."
            type="warning"
            show-icon
            :closable="false"
          />
        </div>

        <!-- Step 3: Training Strategy Selection -->
        <div v-if="currentStep === 3">
          <StrategySelection
            v-if="maturityResults && phase1TargetGroupData"
            :maturity-data="maturityResults"
            :target-group-data="phase1TargetGroupData"
            :roles-data="phase1RolesData || []"
            :existing-strategies="phase1StrategyData"
            @complete="handleStrategyComplete"
            @back="previousStep"
          />
          <el-alert
            v-else
            title="Please Complete Previous Steps First"
            description="Maturity assessment and role identification must be completed before selecting training strategies."
            type="warning"
            show-icon
            :closable="false"
          >
            <div style="margin-top: 12px; display: flex; gap: 8px;">
              <el-button v-if="!maturityResults" type="primary" @click="currentStep = 1">
                Go to Task 1: Maturity Assessment
              </el-button>
              <el-button v-if="maturityResults && !phase1TargetGroupData" type="primary" @click="currentStep = 2">
                Go to Task 2: Role Identification
              </el-button>
            </div>
          </el-alert>
        </div>

        <!-- Step 4: Review & Confirm -->
        <el-card v-if="currentStep === 4" class="step-card">
        <template #header>
          <h3>Review & Confirm Phase 1</h3>
        </template>

        <div class="review-summary">
          <!-- Organization Overview Card -->
          <el-card class="results-card overview-card">
            <template #header>
              <div class="overview-header">
                <el-icon :size="24" color="#1976D2"><OfficeBuilding /></el-icon>
                <h4>Organization Overview</h4>
              </div>
            </template>
            <div class="organization-overview">
              <div class="org-icon-wrapper">
                <div class="org-icon-circle">
                  <el-icon :size="48" color="#1976D2"><OfficeBuilding /></el-icon>
                </div>
              </div>
              <div class="org-info-section">
                <div class="org-name-display">
                  <h2 class="org-name-large">{{ organizationForm.organizationName || 'Your Organization' }}</h2>
                </div>
                <div class="org-size-display">
                  <el-icon :size="18" color="#606266"><User /></el-icon>
                  <span class="size-label">Organization Size:</span>
                  <span class="size-value">{{ getOrganizationSizeLabel(organizationForm.organizationSize) }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Assessment Results (reorganized layout) -->
          <div class="assessment-results">
            <!-- Row 1: Maturity and Strategy side by side -->
            <div class="results-row-top">
              <!-- Maturity Assessment Results -->
              <el-card class="results-card maturity-card">
                <template #header>
                  <h4>Systems Engineering Maturity Level</h4>
                </template>
                <div class="maturity-results">
                  <div v-if="maturityResults" class="maturity-score-display-vertical">
                    <!-- Circle on top -->
                    <div class="score-circle-centered">
                      <el-progress
                        type="circle"
                        :percentage="Math.round(maturityResults.finalScore)"
                        :width="140"
                        :stroke-width="10"
                        :color="maturityResults.maturityColor"
                      >
                        <template #default>
                          <span style="font-size: 32px; font-weight: bold; color: #303133;">
                            {{ maturityResults.finalScore }}
                          </span>
                          <span style="font-size: 14px; color: #909399; display: block;">/100</span>
                        </template>
                      </el-progress>
                    </div>

                    <!-- Level info below circle -->
                    <div class="maturity-level-info">
                      <h3 :style="{ color: maturityResults.maturityColor }">
                        Level {{ maturityResults.maturityLevel }}: {{ maturityResults.maturityName }}
                      </h3>
                      <p class="level-description">
                        {{ maturityResults.maturityDescription }}
                      </p>
                    </div>

                    <!-- Level meter -->
                    <div class="level-meter">
                      <div class="meter-labels">
                        <span class="meter-label">Initial</span>
                        <span class="meter-label">Developing</span>
                        <span class="meter-label">Defined</span>
                        <span class="meter-label">Managed</span>
                        <span class="meter-label">Optimized</span>
                      </div>
                      <el-progress
                        :percentage="(maturityResults.maturityLevel / 5) * 100"
                        :color="maturityResults.maturityColor"
                        :stroke-width="12"
                        :show-text="false"
                      />
                    </div>

                    <!-- Field scores -->
                    <div class="field-scores-grid">
                      <div class="field-score-item">
                        <span class="field-label">Rollout Scope</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.rolloutScope || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">SE Roles & Processes</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.seRolesProcesses || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">SE Mindset</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.seMindset || 0 }}/100</span>
                      </div>
                      <div class="field-score-item">
                        <span class="field-label">Knowledge Base</span>
                        <span class="field-value">{{ maturityResults.fieldScores?.knowledgeBase || 0 }}/100</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- Task 3: Training Strategy Selection Results -->
              <el-card v-if="phase1StrategyData" class="results-card strategy-card">
                <template #header>
                  <h4>Selected Training Strategies</h4>
                </template>
                <div class="strategy-results">
                  <!-- Strategy Count Summary -->
                  <div class="strategy-count-summary-new">
                    <div class="count-badge">
                      <span class="count-number">{{ phase1StrategyData.count }}</span>
                      <span class="count-text">{{ phase1StrategyData.count === 1 ? 'Strategy' : 'Strategies' }}</span>
                    </div>
                  </div>

                  <!-- Strategies List -->
                  <div class="strategies-list-review">
                    <div
                      v-for="(strategy, index) in phase1StrategyData.strategies"
                      :key="`strategy-review-${index}`"
                      class="strategy-review-item-simple"
                    >
                      <!-- Strategy Name -->
                      <h5 class="strategy-name-simple">{{ strategy.strategyName }}</h5>
                    </div>
                  </div>

                  <!-- User Preference -->
                  <div v-if="phase1StrategyData.userPreference" class="user-preference-display">
                    <el-alert type="info" :closable="false" show-icon>
                      <template #title>Your Secondary Strategy Preference</template>
                      You selected: <strong>{{ formatStrategyName(phase1StrategyData.userPreference) }}</strong>
                    </el-alert>
                  </div>

                  <!-- Next Steps -->
                  <div class="next-steps">
                    <el-alert
                      title="What's Next?"
                      description="Based on your selected training strategies, learning objectives and qualification formats will be generated in the next phase."
                      type="success"
                      show-icon
                      :closable="false"
                    />
                  </div>
                </div>
              </el-card>
            </div>

            <!-- Row 2: Roles & Target Group (full width) -->
            <div class="results-row-bottom">
              <!-- Task 2: Identified SE Roles & Target Group Size -->
              <el-card v-if="phase1RolesData && phase1TargetGroupData" class="results-card roles-card">
                <template #header>
                  <h4>Identified SE Roles & Target Group Size</h4>
                </template>
                <div class="roles-results">
                  <!-- Roles Count Summary -->
                  <div class="roles-count-summary">
                    <span class="count-label">{{ phase1RolesData.count }} SE {{ phase1RolesData.count === 1 ? 'Role' : 'Roles' }} Identified</span>
                  </div>

                  <!-- Roles List (if roles exist) -->
                  <div v-if="phase1RolesData.count > 0" class="roles-list-review">
                    <ul class="roles-list">
                      <li
                        v-for="(role, index) in phase1RolesData.roles"
                        :key="`role-review-${index}`"
                        class="role-list-item"
                      >
                        <span class="role-bullet">•</span>
                        <span class="role-name">{{ getRoleName(role) }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- No Roles Note (TASK_BASED pathway) -->
                  <div v-else class="no-roles-note">
                    <el-alert
                      title="No Defined SE Roles"
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      Based on your organization's maturity level, specific SE roles have not yet been defined.
                    </el-alert>
                  </div>

                  <!-- Target Group Size -->
                  <div class="target-group-display">
                    <div class="target-group-inline">
                      <span class="target-label">Target Group Size for Training:</span>
                      <span class="target-size-value-inline">{{ phase1TargetGroupData.label || phase1TargetGroupData.size_range }}</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>

        <div class="completion-message">
          <el-alert
            title="Phase 1 Complete!"
            description="You have successfully completed the maturity assessment and strategy selection. You can review your results, retake the assessment if needed, or proceed to Phase 2."
            type="success"
            show-icon
            :closable="false"
          />
        </div>

        <div class="step-actions">
          <el-button @click="retakeAssessment" plain>
            Retake Assessment
          </el-button>
          <div style="flex: 1"></div>
          <el-button type="primary" @click="completePhase" :loading="loading">
            <el-icon><Check /></el-icon>
            Complete Phase 1
          </el-button>
        </div>
      </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Plus, View, User, OfficeBuilding } from '@element-plus/icons-vue'
import { assessmentApi } from '@/api/assessment'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'
import QuestionnaireComponent from '@/components/common/QuestionnaireComponent.vue'
import OrganizationResultsCard from '@/components/phases/OrganizationResultsCard.vue'
import MaturityAssessment from '@/components/phase1/task1/MaturityAssessment.vue'
import MaturityResults from '@/components/phase1/task1/MaturityResults.vue'
import RoleIdentification from '@/components/phase1/task2/RoleIdentification.vue'
import StrategySelection from '@/components/phase1/task3/StrategySelection.vue'
import phase1Api from '@/api/phase1'

const router = useRouter()
const authStore = useAuthStore()

// State
const currentStep = ref(1) // Start directly at maturity assessment since org info is from registration
const loading = ref(false)
const organizationFormRef = ref()
const organizationForm = ref({
  organizationName: '',
  organizationSize: ''
})

const maturityQuestionnaire = ref(null)
const archetypeQuestionnaire = ref(null)
const maturityCompleted = ref(false)
const archetypeCompleted = ref(false)
const maturityResponse = ref(null)
const archetypeResponse = ref(null)
const freshComputedArchetype = ref(null)
const organizationData = ref(null)

// New maturity assessment data
const maturityAnswers = ref(null)
const maturityResults = ref(null)
const showMaturityResults = ref(false)

// Phase 1 Task 2: Role Identification data
const phase1RolesData = ref(null)
const phase1TargetGroupData = ref(null)

// Phase 1 Task 3: Training Strategy data
const phase1StrategyData = ref(null)
const strategyCompleted = ref(false)

// Computed properties for role-based UI
const isEmployeeView = computed(() => authStore.user?.role === 'employee')

// Form validation rules
const organizationRules = {
  organizationName: [
    { required: true, message: 'Organization name is required', trigger: 'blur' }
  ],
  organizationSize: [
    { required: true, message: 'Organization size is required', trigger: 'change' }
  ]
}


// Computed properties
const overallProgress = computed(() => {
  // Progress: Step 1 = 0%, Step 2 = 25%, Step 3 = 50%, Step 4 = 75%, Complete = 100%
  return Math.round(((currentStep.value - 1) / 4) * 100)
})

const progressColor = computed(() => {
  if (overallProgress.value < 30) return '#f56c6c'
  if (overallProgress.value < 70) return '#e6a23c'
  return '#67c23a'
})

const calculatedMaturityLevel = computed(() => {
  if (!maturityResponse.value || maturityResponse.value.total_score === null || maturityResponse.value.total_score === undefined) {
    return null
  }

  const score = maturityResponse.value.total_score
  // RMS algorithm returns score on 0-5 scale (12 BRETZ questions in 4 sections)
  const maxScore = 5.0
  const percentage = (score / maxScore) * 100

  if (percentage >= 80) return 'Optimizing'     // 80-100%: 4.0-5.0 points
  if (percentage >= 60) return 'Defined'       // 60-79%:  3.0-3.9 points
  if (percentage >= 40) return 'Managed'       // 40-59%:  2.0-2.9 points
  if (percentage >= 20) return 'Performed'     // 20-39%:  1.0-1.9 points
  return 'Initial'                             // 0-19%:   0.0-0.9 points
})

const selectedArchetype = computed(() => {
  console.log('selectedArchetype computed property called')
  console.log('archetypeResponse.value:', archetypeResponse.value)
  console.log('freshComputedArchetype.value:', freshComputedArchetype.value)

  // Use the fresh computed archetype first (just received from SE-QPT API)
  let computed = freshComputedArchetype.value

  // Fallback to database-loaded computed archetype if fresh one isn't available
  if (!computed && archetypeResponse.value && archetypeResponse.value.computed_archetype) {
    computed = archetypeResponse.value.computed_archetype
  }

  // Use the computed archetype from backend if available
  if (computed) {
    console.log('selectedArchetype computed property called with:', computed)
    console.log('requires_dual_processing:', computed.requires_dual_processing)
    console.log('secondary:', computed.secondary)

    // Handle dual selection display
    if (computed.requires_dual_processing && computed.secondary) {
      console.log('Using DUAL archetype display')
      return {
        name: `${computed.name} + ${computed.secondary}`,
        description: computed.rationale || 'SE-QPT dual archetype selection for low maturity organizations.',
        characteristics: [
          `Selection Type: ${computed.selection_type} (Primary + Secondary)`,
          `Customization Level: ${computed.customization_level} company-specific`,
          `Processing Type: ${computed.processing_type}`,
          `Primary: ${computed.name}`,
          `Secondary: ${computed.secondary}`,
          'Computed using SE-QPT dual selection logic'
        ],
        isDual: true,
        primary: computed.name,
        secondary: computed.secondary
      }
    } else {
      // Single selection display
      return {
        name: computed.name,
        description: computed.rationale || 'SE-QPT computed archetype based on maturity and scope analysis.',
        characteristics: [
          `Selection Type: ${computed.selection_type || 'single'}`,
          `Customization Level: ${computed.customization_level} company-specific`,
          `Processing Type: ${computed.processing_type || 'high_intensity_rag'}`,
          'Computed using SE-QPT Bretz model scoring'
        ],
        isDual: false,
        primary: computed.name,
        secondary: null
      }
    }
  }

  // Fallback to manual selection if no computed archetype
  if (!archetypeResponse.value || !archetypeResponse.value.responses) {
    return null
  }

  const archetypeSelectionResponse = archetypeResponse.value.responses['4']
  if (!archetypeSelectionResponse) {
    return null
  }

  // SE-QPT compliant archetype mapping
  const archetypes = {
    'A': {
      name: 'Common Basic Understanding',
      description: 'Create shared SE awareness across stakeholders.',
      characteristics: [
        'Low customization level',
        'Standardized learning objectives',
        'Broad organizational awareness'
      ]
    },
    'B': {
      name: 'Needs-based Project-oriented Training',
      description: 'Role-specific training for project contexts.',
      characteristics: [
        'High customization level',
        'Company-specific learning objectives',
        'Project-focused application'
      ]
    },
    'C': {
      name: 'Continuous Support',
      description: 'Ongoing coaching and improvement support.',
      characteristics: [
        'High customization level',
        'Continuous improvement focus',
        'Advanced competency development'
      ]
    },
    'D': {
      name: 'SE for Managers',
      description: 'Executive-level SE understanding and change management.',
      characteristics: [
        'Low customization level',
        'Management-focused content',
        'Strategic SE implementation'
      ]
    }
  }

  return archetypes[archetypeSelectionResponse] || {
    name: 'Common Basic Understanding',
    description: 'Default SE-QPT archetype for unclear scoring patterns.',
    characteristics: ['Low customization level', 'Standardized approach']
  }
})


// Methods
const nextStep = async () => {
  if (currentStep.value === 0) {
    if (await validateOrganizationForm()) {
      currentStep.value++
    }
  } else if (currentStep.value === 1) {
    if (maturityCompleted.value) {
      await loadArchetypeQuestionnaire()
      currentStep.value++
    }
  } else if (currentStep.value === 2) {
    if (archetypeCompleted.value) {
      // Don't load from database here - we already have fresh data from completion handlers
      // Only load organization data for the review page
      await loadOrganizationData()
      currentStep.value++
    }
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// Handle role identification completion
const handleRoleIdentificationComplete = (data) => {
  console.log('[PhaseOne] Role identification complete:', data)
  console.log('[PhaseOne] data.roles structure:', JSON.stringify(data.roles, null, 2))
  console.log('[PhaseOne] data.roles.roles:', data.roles?.roles)
  console.log('[PhaseOne] data.roles.count:', data.roles?.count)

  // Store the role identification data
  // IMPORTANT: data.roles is { roles: [...], count: N }
  // So after assignment, phase1RolesData.value = { roles: [...], count: N }
  // Template expects phase1RolesData.roles (the array)
  phase1RolesData.value = data.roles

  console.log('[PhaseOne] After assignment - phase1RolesData.value:', phase1RolesData.value)
  console.log('[PhaseOne] phase1RolesData.value.roles length:', phase1RolesData.value?.roles?.length)

  // Normalize target group data structure to match what we expect from API
  // data.targetGroup has { sizeData, targetGroupId } structure
  if (data.targetGroup && data.targetGroup.sizeData) {
    phase1TargetGroupData.value = {
      size_range: data.targetGroup.sizeData.range,
      size_category: data.targetGroup.sizeData.category,
      estimated_count: data.targetGroup.sizeData.value,
      targetGroupId: data.targetGroup.targetGroupId,
      label: data.targetGroup.sizeData.label
    }
  } else {
    phase1TargetGroupData.value = data.targetGroup
  }

  console.log('[PhaseOne] After assignment - phase1TargetGroupData.value:', phase1TargetGroupData.value)

  // Show success message
  ElMessage({
    message: `Successfully identified ${data.roles.count} SE role(s) and selected target group size`,
    type: 'success',
    duration: 3000
  })

  // Auto-advance to next step (Strategy Selection)
  currentStep.value = 3
}

// Handle strategy selection completion
const handleStrategyComplete = (data) => {
  console.log('[PhaseOne] Strategy selection complete:', data)

  // Store the strategy data
  phase1StrategyData.value = data
  strategyCompleted.value = true

  // Show success message
  ElMessage({
    message: `${data.count} training ${data.count === 1 ? 'strategy' : 'strategies'} selected successfully`,
    type: 'success',
    duration: 3000
  })

  // Auto-advance to Review step
  currentStep.value = 4
}

const validateOrganizationForm = async () => {
  try {
    await organizationFormRef.value.validate()
    return true
  } catch (error) {
    return false
  }
}

// New maturity assessment handlers
const handleMaturityCalculated = async ({ answers, results }) => {
  try {
    console.log('[Phase1] Maturity calculated:', { answers, results })
    maturityAnswers.value = answers
    maturityResults.value = results
    showMaturityResults.value = true
    maturityCompleted.value = true

    // Auto-save to database
    if (authStore.organizationId) {
      try {
        const response = await phase1Api.maturity.save(authStore.organizationId, answers, results)
        console.log('[Phase1] Maturity save response:', response)

        // Attach the ID to maturityResults for use in Task 2 and Task 3
        if (response?.id) {
          maturityResults.value = {
            ...results,
            id: response.id,
            strategyInputs: {
              seProcessesValue: answers.seRolesProcesses,
              rolloutScopeValue: answers.rolloutScope,
              seMindsetValue: answers.seMindset,
              knowledgeBaseValue: answers.knowledgeBase
            }
          }
          console.log('[Phase1] Maturity ID attached:', response.id)
        }

        ElMessage.success('Maturity assessment saved successfully!')
      } catch (error) {
        console.error('[Phase1] Failed to save maturity:', error)
        ElMessage.warning('Assessment completed but not saved - you can continue')
      }
    }
  } catch (error) {
    console.error('[Phase1] Failed to process maturity:', error)
    ElMessage.error('Failed to process maturity assessment')
  }
}

const handleMaturityDataChanged = (data) => {
  console.log('[Phase1] Maturity data changed:', data)
  maturityAnswers.value = data
}

const resetMaturityAssessment = () => {
  showMaturityResults.value = false
}

const proceedToRoleIdentification = () => {
  // Proceed to step 2 (Role Identification)
  currentStep.value = 2
}

const onMaturityCompleted = async (response) => {
  try {
    maturityCompleted.value = true
    // Use the response data directly - it already has total_score and responses calculated
    maturityResponse.value = response
    console.log('Maturity completed with score:', response.total_score)
    ElMessage.success('Maturity assessment completed!')
  } catch (error) {
    console.error('Failed to process maturity response:', error)
    maturityResponse.value = response // fallback
  }
}

const onMaturityProgress = (progress) => {
  // Handle progress updates if needed
}

const onArchetypeCompleted = async (response) => {
  try {
    archetypeCompleted.value = true

    // Use the response data directly - it already has total_score and responses calculated
    console.log('Archetype completed with responses:', response.responses)

    // Compute SE-QPT archetype using backend logic
    try {
      // CRITICAL: Pass maturity_responses containing MAT_04 and MAT_05 for routing
      const archetypeComputationResponse = await axios.post('/api/seqpt/phase1/archetype-selection', {
        assessment_uuid: response.assessment_uuid,
        responses: response.responses || {},
        maturity_responses: maturityResponse.value?.responses || {},  // Pass maturity responses for MAT_04/MAT_05 routing
        company_preference: response.responses?.company_preference
      })

      if (archetypeComputationResponse.status === 200) {
        const computationResult = archetypeComputationResponse.data

        // Add computed archetype info to the response
        response.computed_archetype = {
          name: computationResult.archetype.name,
          secondary: computationResult.archetype.secondary,
          customization_level: computationResult.archetype.customization_level,
          selection_type: computationResult.archetype.selection_type,
          processing_type: computationResult.archetype.processing_type,
          requires_dual_processing: computationResult.archetype.requires_dual_processing,
          rationale: computationResult.archetype.rationale
        }

        console.log('Frontend received computed archetype:', response.computed_archetype)

        // Store the fresh computed archetype in reactive variable for immediate UI update
        freshComputedArchetype.value = response.computed_archetype

        ElMessage.success(`Training strategy computed: ${computationResult.archetype.name}`)
      } else {
        console.warn('Failed to compute archetype, using fallback')
        ElMessage.warning('Strategy selection completed (using fallback)')
      }
    } catch (archetypeError) {
      console.warn('Archetype computation failed:', archetypeError)
      ElMessage.warning('Strategy selection completed (computation unavailable)')
    }

    archetypeResponse.value = response
  } catch (error) {
    console.error('Failed to process archetype response:', error)
    archetypeResponse.value = response // fallback
    ElMessage.error('Failed to complete strategy selection')
  }
}

const onArchetypeProgress = (progress) => {
  // Handle progress updates if needed
}


const getOrganizationSizeLabel = (value) => {
  const sizeMap = {
    small: 'Small (< 100 employees)',
    medium: 'Medium (100-1000 employees)',
    large: 'Large (1000-10000 employees)',
    enterprise: 'Enterprise (> 10000 employees)'
  }
  return sizeMap[value] || value
}

const getMaturityLevelType = (level) => {
  const typeMap = {
    'Initial': 'danger',
    'Performed': 'warning',
    'Managed': 'info',
    'Defined': 'primary',
    'Optimizing': 'success'
  }
  return typeMap[level] || 'info'
}

const getMaturityLevelDescription = (level) => {
  const descriptions = {
    'Initial': 'Basic processes exist but are unpredictable and reactive. Success depends on individual effort.',
    'Performed': 'Processes are performed but often ad hoc. Projects meet their basic requirements.',
    'Managed': 'Processes are planned, monitored, and controlled. Projects follow defined procedures.',
    'Defined': 'Processes are well-defined, standardized, and integrated across the organization.',
    'Optimizing': 'Focus on continuous process improvement through quantitative feedback and innovation.'
  }
  return descriptions[level] || 'Maturity level assessment pending.'
}

const getMaturityPercentage = () => {
  if (!maturityResponse.value || maturityResponse.value.total_score === null || maturityResponse.value.total_score === undefined) {
    return 0
  }
  const score = maturityResponse.value.total_score
  // RMS algorithm returns score on 0-5 scale (12 BRETZ questions in 4 sections)
  const maxScore = 5.0
  return (score / maxScore) * 100
}

const getMaturityProgressColor = () => {
  const percentage = getMaturityPercentage()
  if (percentage >= 80) return '#67c23a' // green
  if (percentage >= 60) return '#409eff' // blue
  if (percentage >= 40) return '#e6a23c' // orange
  if (percentage >= 20) return '#f56c6c' // red
  return '#f56c6c'
}

const getMaturityExplanation = (level) => {
  const explanations = {
    'Initial': 'Your organization is beginning its SE journey. Focus on establishing basic processes and building awareness.',
    'Performed': 'SE practices exist but need more consistency. Work on standardizing successful approaches.',
    'Managed': 'Good foundation of SE practices. Focus on integration and measurement.',
    'Defined': 'Strong SE capabilities. Ready for advanced techniques and organization-wide adoption.',
    'Optimizing': 'Excellent SE maturity. Focus on innovation and continuous improvement.'
  }
  return explanations[level] || 'Maturity assessment data unavailable.'
}

const getArchetypeDescription = (archetype) => {
  const descriptions = {
    'Common Basic Understanding': 'Create shared SE awareness across all organizational stakeholders.',
    'Needs-based Project-oriented Training': 'Role-specific training tailored to project contexts and requirements.',
    'Continuous Support': 'Ongoing coaching and improvement support for advanced SE practices.',
    'SE for Managers': 'Executive-level SE understanding and strategic change management.',
    'Orientation in Pilot Project': 'Focused SE implementation through targeted pilot projects.'
  }
  return descriptions[archetype] || 'This training strategy focuses on building appropriate SE capabilities for your organization.'
}

const getArchetypeCharacteristics = (archetype) => {
  const characteristics = {
    'Common Basic Understanding': [
      'Broad organizational awareness',
      'Standardized learning objectives',
      'Low customization level',
      'Foundation building focus'
    ],
    'Needs-based Project-oriented Training': [
      'Role-specific training approach',
      'High customization level',
      'Project-focused application',
      'Company-specific learning objectives'
    ],
    'Continuous Support': [
      'Ongoing coaching model',
      'High customization level',
      'Continuous improvement focus',
      'Advanced competency development'
    ],
    'SE for Managers': [
      'Management-focused content',
      'Strategic SE implementation',
      'Low customization level',
      'Executive-level understanding'
    ],
    'Orientation in Pilot Project': [
      'Pilot project approach',
      'High customization level',
      'Focused implementation',
      'Practical experience focus'
    ]
  }
  return characteristics[archetype] || [
    'Tailored to organizational needs',
    'Systematic capability building',
    'Progressive skill development'
  ]
}

const loadMaturityQuestionnaire = async () => {
  try {
    loading.value = true
    const response = await assessmentApi.getQuestionnaire(1) // SE Maturity Assessment
    maturityQuestionnaire.value = response.data // API returns questionnaire directly
  } catch (error) {
    ElMessage.error('Failed to load maturity assessment questionnaire')
  } finally {
    loading.value = false
  }
}

const loadArchetypeQuestionnaire = async () => {
  try {
    loading.value = true

    // Extract MAT_04 value to filter archetype questions based on maturity level
    const mat04Value = maturityResponse.value?.responses?.MAT_04

    console.log('[ARCHETYPE LOAD] MAT_04 value for filtering:', mat04Value)

    // Pass MAT_04 as query parameter to backend for question filtering
    const url = mat04Value !== undefined
      ? `/api/questionnaires/2?mat_04=${mat04Value}`
      : '/api/questionnaires/2'

    const response = await axios.get(url)
    archetypeQuestionnaire.value = response.data // API returns questionnaire directly

    console.log('[ARCHETYPE LOAD] Received', response.data.questions?.length, 'questions')
  } catch (error) {
    console.error('[ARCHETYPE LOAD] Error:', error)
    ElMessage.error('Failed to load strategy selection questionnaire')
  } finally {
    loading.value = false
  }
}

const loadLatestMaturityAssessment = async () => {
  try {
    const orgId = authStore.organizationId
    if (!orgId) {
      console.log('[Phase1] No organization ID - skipping maturity load')
      return
    }

    console.log('[Phase1] Loading latest maturity assessment for org:', orgId)
    const response = await phase1Api.maturity.get(orgId)

    if (response.exists && response.data) {
      console.log('[Phase1] Found existing maturity assessment:', response.data)

      // API returns nested structure: data.answers and data.results
      const answers = response.data.answers || {}
      const results = response.data.results || {}

      // Reconstruct answers from saved data (use new nested structure)
      const savedAnswers = {
        rolloutScope: answers.rolloutScope,
        seRolesProcesses: answers.seRolesProcesses,
        seMindset: answers.seMindset,
        knowledgeBase: answers.knowledgeBase
      }

      // Reconstruct results from saved data (use new nested structure)
      const savedResults = {
        id: response.data.id, // Include the maturity ID for Task 2
        rawScore: results.rawScore,
        balancePenalty: results.balancePenalty,
        finalScore: results.finalScore,
        maturityLevel: results.maturityLevel,
        maturityName: results.maturityName,
        maturityColor: results.maturityColor || getMaturityColor(results.maturityLevel),
        maturityDescription: results.maturityDescription || getMaturityDescription(results.maturityName),
        balanceScore: results.balanceScore,
        profileType: results.profileType,
        fieldScores: results.fieldScores || {
          rolloutScope: 0,
          seRolesProcesses: 0,
          seMindset: 0,
          knowledgeBase: 0
        },
        weakestField: results.weakestField || { field: '', value: 0 },
        strongestField: results.strongestField || { field: '', value: 0 },
        strategyInputs: results.strategyInputs || {
          seProcessesValue: answers.seRolesProcesses,
          rolloutScopeValue: answers.rolloutScope,
          seMindsetValue: answers.seMindset,
          knowledgeBaseValue: answers.knowledgeBase
        }
      }

      // Set the data
      maturityAnswers.value = savedAnswers
      maturityResults.value = savedResults
      maturityCompleted.value = true
      showMaturityResults.value = true

      console.log('[Phase1] Loaded maturity data successfully')
      console.log('[Phase1] maturityResults.value:', JSON.stringify(maturityResults.value, null, 2))
      console.log('[Phase1] savedResults object:', savedResults)
    } else {
      console.log('[Phase1] No existing maturity assessment found')
    }
  } catch (error) {
    console.error('[Phase1] Failed to load latest maturity:', error)
  }
}

// Load latest Task 3 data (strategies)
const loadLatestTask3Data = async () => {
  try {
    const orgId = authStore.organizationId
    if (!orgId) {
      console.log('[Phase1] No organization ID - skipping Task 3 data load')
      return
    }

    console.log('[Phase1] Loading latest Task 3 data for org:', orgId)

    try {
      const strategiesResponse = await axios.get(`/api/phase1/strategies/${orgId}/latest`)
      console.log('[Phase1] Strategy API response:', strategiesResponse.data)

      if (strategiesResponse.data.success && strategiesResponse.data.count > 0) {
        // API returns 'data' not 'strategies'
        phase1StrategyData.value = {
          strategies: strategiesResponse.data.data,  // Fixed: API returns data.data
          count: strategiesResponse.data.count,
          userPreference: strategiesResponse.data.userPreference,
          decisionPath: strategiesResponse.data.decisionPath,
          reasoning: strategiesResponse.data.reasoning
        }
        strategyCompleted.value = true
        console.log('[Phase1] Loaded existing strategies:', phase1StrategyData.value.count, 'strategies')
      } else {
        console.log('[Phase1] No existing strategies found (count:', strategiesResponse.data.count, ')')
        strategyCompleted.value = false
      }
    } catch (strategyError) {
      console.log('[Phase1] Strategy API error:', strategyError.message, strategyError.response?.status)
      strategyCompleted.value = false
    }
  } catch (error) {
    console.error('[Phase1] Failed to load Task 3 data:', error)
  }
}

// Load latest Task 2 data (roles and target group)
const loadLatestTask2Data = async () => {
  try {
    const orgId = authStore.organizationId
    if (!orgId) {
      console.log('[Phase1] No organization ID - skipping Task 2 data load')
      return
    }

    console.log('[Phase1] Loading latest Task 2 data for org:', orgId)

    // Load roles
    try {
      const rolesResponse = await axios.get(`/api/phase1/roles/${orgId}/latest`)
      console.log('[Phase1] Roles API response:', rolesResponse.data)

      if (rolesResponse.data.success && rolesResponse.data.count > 0) {
        // API returns 'data' not 'roles'
        phase1RolesData.value = {
          roles: rolesResponse.data.data,  // Fixed: API returns data.data
          count: rolesResponse.data.count,
          maturityId: rolesResponse.data.maturityId
        }
        console.log('[Phase1] Loaded existing roles:', phase1RolesData.value.count, 'roles')
        console.log('[Phase1] First role data structure:', phase1RolesData.value.roles[0])
      } else {
        console.log('[Phase1] No existing roles found (count:', rolesResponse.data.count, ')')
      }
    } catch (rolesError) {
      console.log('[Phase1] Roles API error:', rolesError.message, rolesError.response?.status)
    }

    // Load target group
    try {
      const targetGroupResponse = await axios.get(`/api/phase1/target-group/${orgId}`)
      console.log('[Phase1] Target group API response:', targetGroupResponse.data)

      if (targetGroupResponse.data.success && targetGroupResponse.data.data) {
        const tg = targetGroupResponse.data.data // API returns data.data
        // Handle both snake_case and camelCase field names
        phase1TargetGroupData.value = {
          size_range: tg.range || tg.sizeRange || tg.size_range,
          size_category: tg.category || tg.sizeCategory || tg.size_category,
          estimated_count: tg.value || tg.estimatedCount || tg.estimated_count,
          label: tg.label,
          maturityId: tg.maturityId || tg.maturity_id
        }
        console.log('[Phase1] Loaded existing target group:', phase1TargetGroupData.value.size_range)
      } else {
        console.log('[Phase1] No existing target group found')
      }
    } catch (targetError) {
      console.log('[Phase1] Target group API error:', targetError.message, targetError.response?.status)
    }

  } catch (error) {
    console.error('[Phase1] Failed to load Task 2 data:', error)
  }
}

// Helper functions for maturity colors and descriptions
const getMaturityColor = (level) => {
  const colors = {
    1: '#DC2626',
    2: '#F59E0B',
    3: '#EAB308',
    4: '#10B981',
    5: '#059669'
  }
  return colors[level] || '#909399'
}

const getMaturityDescription = (name) => {
  const descriptions = {
    'Initial': 'Organization has minimal or no Systems Engineering capability.',
    'Developing': 'Organization is beginning to adopt SE practices in isolated areas.',
    'Defined': 'SE processes and roles are formally defined and documented.',
    'Managed': 'SE is systematically implemented company-wide with quantitative management.',
    'Optimized': 'SE excellence achieved with continuous optimization.'
  }
  return descriptions[name] || ''
}

// Strategy helper methods
const getStrategyPriorityType = (priority) => {
  const typeMap = {
    'PRIMARY': 'primary',
    'SECONDARY': 'info',
    'SUPPLEMENTARY': 'success'
  }
  return typeMap[priority] || 'info'
}

const formatStrategyName = (strategyId) => {
  if (!strategyId) return ''

  // Convert snake_case to Title Case
  return strategyId
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const formatSizeCategory = (category) => {
  if (!category) return ''

  // Map category to readable format
  const categoryMap = {
    'SMALL': 'Small Organization',
    'MEDIUM': 'Medium Organization',
    'LARGE': 'Large Organization',
    'ENTERPRISE': 'Enterprise Organization'
  }

  return categoryMap[category] || category
}

const getRoleName = (role) => {
  // standardRoleName is the SE role cluster name (e.g., "Customer", "Project Manager")
  // orgRoleName is the organization-specific name entered by user
  const standardName = role.standardRoleName || role.standard_role_name
  const orgName = role.orgRoleName || role.org_role_name

  // If both exist, show both: "Customer (baka)"
  if (standardName && orgName) {
    return `${standardName} (${orgName})`
  }

  // Otherwise just show whichever is available
  return standardName || orgName || role.role_name || role.roleName || role.name || 'Unnamed Role'
}

const loadLatestResponses = async () => {
  try {
    loading.value = true
    console.log('Loading latest responses for review...')

    // Get current user data from auth store
    const userId = authStore.userId
    const userRole = authStore.user?.role

    console.log('Current user:', { userId, userRole })

    if (!userId) {
      console.warn('No user ID available - user may need to log in again')
      return
    }

    // For employees, load organization-wide Phase 1 results (completed by admin)
    // For admins, load their own responses
    let responsesData
    try {
      if (userRole === 'employee') {
        console.log('Employee user - loading organization-wide Phase 1 results...')
        // Use organization dashboard endpoint to get completed assessments
        const orgResponse = await axios.get('/api/organization/dashboard')
        if (orgResponse.data.organization.maturity_score && orgResponse.data.organization.selected_archetype) {
          // Create mock response data for employees based on org-wide results
          // maturity_score in database is now stored as percentage (0-100)
          const maturityPercentage = orgResponse.data.organization.maturity_score
          const rawScore = (maturityPercentage / 100) * 5.0 // Convert percentage to raw score (0-5 RMS scale)

          responsesData = {
            responses: [
              {
                questionnaire_type: 'maturity',
                status: 'completed',
                uuid: 'org-maturity-result',
                total_score: rawScore, // Convert percentage to raw score for questionnaire response
                completed_at: new Date().toISOString(),
                responses: {} // Organization level doesn't store individual responses
              },
              {
                questionnaire_type: 'archetype',
                status: 'completed',
                uuid: 'org-archetype-result',
                completed_at: new Date().toISOString(),
                responses: {},
                computed_archetype: JSON.stringify({
                  name: orgResponse.data.organization.selected_archetype,
                  description: 'Organization-wide training strategy selected by administrator',
                  characteristics: [
                    'Organization-level selection',
                    'Applies to all employees',
                    'Based on organizational maturity assessment'
                  ]
                })
              }
            ]
          }
          console.log('Created employee view from organization data:', responsesData)
        } else {
          console.log('No organization-wide Phase 1 results found')
          responsesData = { responses: [] }
        }
      } else {
        console.log('Admin user - loading personal responses...')
        // Always load fresh data from database - don't use localStorage to avoid stale data
        // IMPORTANT: Always use the user ID from JWT verification, not from auth store
        // This ensures we request data for the actual authenticated user
        const response = await assessmentApi.getUserQuestionnaireResponses(userId)
        responsesData = response.data
        console.log('Admin responses:', responsesData)
      }
    } catch (verifyError) {
      console.error('Failed to load responses:', verifyError)
      return
    }

    // Find the latest completed maturity and archetype responses
    // Handle both direct array and object with responses property
    const responses = responsesData.responses || responsesData.questionnaire_responses || responsesData
    const latestMaturityResponse = responses.find(r =>
      r.questionnaire_type === 'maturity' && r.status === 'completed'
    )
    const latestArchetypeResponse = responses.find(r =>
      r.questionnaire_type === 'archetype' && r.status === 'completed'
    )

    console.log('Found maturity response:', latestMaturityResponse)
    console.log('Found archetype response:', latestArchetypeResponse)

    if (latestMaturityResponse) {
      // Use the response data directly - it already has all the info we need
      maturityResponse.value = {
        ...latestMaturityResponse,
        total_score: latestMaturityResponse.total_score,
        responses: latestMaturityResponse.responses || {}
      }
      maturityCompleted.value = true
      console.log('Loaded complete maturity data:', maturityResponse.value)
    }

    if (latestArchetypeResponse) {
      // Use the response data directly - it already has all the info we need
      archetypeResponse.value = {
        ...latestArchetypeResponse,
        responses: latestArchetypeResponse.responses || {}
      }
      archetypeCompleted.value = true
      console.log('Loaded complete archetype data:', archetypeResponse.value)

      // Parse computed archetype if it's a string
      if (latestArchetypeResponse.computed_archetype) {
        try {
          const computedArchetype = typeof latestArchetypeResponse.computed_archetype === 'string'
            ? JSON.parse(latestArchetypeResponse.computed_archetype)
            : latestArchetypeResponse.computed_archetype

          freshComputedArchetype.value = computedArchetype
          console.log('Found saved computed archetype:', computedArchetype)
        } catch (e) {
          console.warn('Failed to parse computed archetype:', e)
        }
      } else {
        console.log('No computed archetype found in database - will display manually selected archetype as fallback')
      }
    }

  } catch (error) {
    console.error('Failed to load latest responses:', error)
    ElMessage.error('Failed to load latest responses for review')
  } finally {
    loading.value = false
  }
}

const fetchCompleteResponseData = async (responseUuid, questionnaireId) => {
  try {
    // Handle mock organization-level responses for employees
    if (responseUuid === 'org-maturity-result') {
      // Get organization data for maturity result
      const orgResponse = await axios.get('/api/organization/dashboard')
      const orgData = orgResponse.data.organization
      return {
        uuid: responseUuid,
        questionnaire_id: 1,
        status: 'completed',
        total_score: orgData.maturity_score * 15, // Convert normalized score back to raw
        score_percentage: orgData.maturity_score * 100,
        completion_percentage: 100,
        completed_at: new Date().toISOString(),
        responses: {} // Organization level doesn't store individual responses
      }
    }

    if (responseUuid === 'org-archetype-result') {
      // Get organization data for archetype result
      const orgResponse = await axios.get('/api/organization/dashboard')
      const orgData = orgResponse.data.organization
      return {
        uuid: responseUuid,
        questionnaire_id: 2,
        status: 'completed',
        total_score: 5, // Strategy completion score
        score_percentage: 100,
        completion_percentage: 100,
        completed_at: new Date().toISOString(),
        responses: {},
        computed_archetype: {
          name: orgData.selected_archetype,
          description: 'Organization-wide training strategy selected by administrator',
          characteristics: [
            'Organization-level selection',
            'Applies to all employees',
            'Based on organizational maturity assessment'
          ]
        }
      }
    }

    // Regular API call for admin users or real responses
    const response = await assessmentApi.getResponse(responseUuid)
    const responseData = response.data

    // The API response should include questionnaire_response with question_responses array
    const questionnairResponseData = responseData.questionnaire_response || responseData

    // Convert question responses to the format our algorithms expect
    const responses = {}
    if (questionnairResponseData.question_responses && Array.isArray(questionnairResponseData.question_responses)) {
      questionnairResponseData.question_responses.forEach(qr => {
        responses[qr.question_id.toString()] = qr.response_value
      })
    }

    return {
      uuid: questionnairResponseData.uuid,
      questionnaire_id: questionnairResponseData.questionnaire_id,
      user_id: questionnairResponseData.user_id,
      status: questionnairResponseData.status,
      total_score: questionnairResponseData.total_score,
      score_percentage: questionnairResponseData.score_percentage,
      completion_percentage: questionnairResponseData.completion_percentage,
      completed_at: questionnairResponseData.completed_at,
      responses: responses,
      computed_archetype: questionnairResponseData.computed_archetype
    }
  } catch (error) {
    console.error('Error fetching complete response data:', error)
    // Return minimal structure as fallback
    return {
      uuid: responseUuid,
      total_score: 0,
      responses: {}
    }
  }
}

const retakeAssessment = async () => {
  try {
    // Confirm with user
    await ElMessageBox.confirm(
      'You can review and modify your Phase 1 assessment responses. Your existing answers will be prefilled and can be updated. New responses will replace the old ones only after you save each task.',
      'Retake Phase 1 Assessment',
      {
        confirmButtonText: 'Yes, Retake',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
    )

    console.log('[Phase1] Retake assessment initiated - keeping prefilled data')

    // DON'T clear the data - keep it prefilled for editing
    // maturityAnswers, maturityResults, phase1RolesData, phase1TargetGroupData, phase1StrategyData
    // All stay populated so the user can see and edit their previous responses

    // Keep showMaturityResults true so results are visible
    showMaturityResults.value = true

    // Reset completion flags so user can save again after editing
    maturityCompleted.value = false
    strategyCompleted.value = false
    archetypeCompleted.value = false

    // Reset to step 1 to let user edit from the beginning
    currentStep.value = 1

    console.log('[Phase1] Reset to step 1 with prefilled data:', {
      maturityAnswers: maturityAnswers.value,
      roles: phase1RolesData.value?.count,
      targetGroup: phase1TargetGroupData.value?.size_range,
      strategies: phase1StrategyData.value?.count
    })

    ElMessage.success('You can now retake the Phase 1 assessment with your previous answers prefilled')
  } catch (error) {
    // User cancelled
    if (error !== 'cancel') {
      console.error('Error initiating retake:', error)
    }
  }
}

const completePhase = async () => {
  try {
    loading.value = true

    // Get user ID from auth store
    const userId = authStore.userId

    if (!userId) {
      ElMessage.error('User ID not found. Please login again.')
      return
    }

    // Validate that we have the required data
    // Check for Phase 1 Task 1 (Maturity) and Task 3 (Strategy Selection) completion
    // Check actual data existence instead of just completion flags to support partial retakes
    const hasMaturityData = maturityResults.value && maturityResults.value.id
    const hasStrategyData = phase1StrategyData.value && phase1StrategyData.value.strategies && phase1StrategyData.value.strategies.length > 0

    if (!hasMaturityData || !hasStrategyData) {
      const missingTasks = []
      if (!hasMaturityData) missingTasks.push('Task 1 (Maturity Assessment)')
      if (!hasStrategyData) missingTasks.push('Task 3 (Strategy Selection)')

      ElMessage.error(`Please complete ${missingTasks.join(' and ')} before proceeding.`)
      return
    }

    if (!organizationForm.value.organizationName) {
      ElMessage.warning('Organization information appears to be missing. Attempting to reload...')
      await loadOrganizationData()
    }

    // Store organization info and Phase 1 assessment data for Phase 2
    const phaseData = {
      organization: organizationForm.value,
      maturity: {
        answers: maturityAnswers.value,
        results: maturityResults.value
      },
      roles: phase1RolesData.value,
      targetGroup: phase1TargetGroupData.value,
      strategies: phase1StrategyData.value,
      completedAt: new Date().toISOString()
    }

    console.log('Storing Phase 1 data:', phaseData)

    // Store in user-specific localStorage key
    localStorage.setItem(`se-qpt-phase1-data-user-${userId}`, JSON.stringify(phaseData))

    // Update organization database to mark Phase 1 as complete
    try {
      console.log('Attempting to save Phase 1 completion to database...')

      // Get organization code from localStorage
      const orgCode = localStorage.getItem('user_organization_code')

      // Get primary strategy for database storage
      const primaryStrategy = phase1StrategyData.value?.strategies?.find(s => s.priority === 'PRIMARY')

      console.log('Request data:', {
        maturity_score: maturityResults.value?.finalScore,
        selected_strategies: phase1StrategyData.value?.count || 0,
        primary_strategy: primaryStrategy?.strategyName,
        organization_size: organizationForm.value?.organizationSize,
        organization_code: orgCode
      })
      const response = await axios.put('/api/organization/phase1-complete', {
        maturity_score: maturityResults.value?.finalScore,  // Final maturity score (0-100)
        maturity_level: maturityResults.value?.maturityLevel, // Maturity level (1-5)
        selected_strategies: phase1StrategyData.value?.count || 0,
        primary_strategy: primaryStrategy?.strategyName,
        organization_size: organizationForm.value?.organizationSize,
        organization_code: orgCode,
        maturity_data: maturityResults.value,
        roles_data: phase1RolesData.value,
        target_group_data: phase1TargetGroupData.value,
        strategies_data: phase1StrategyData.value
      })
      console.log('Phase 1 completion saved to database', response.data)
    } catch (dbError) {
      console.error('Failed to save Phase 1 completion to database:', dbError)
      console.error('Error response:', dbError.response)
      // Don't block user flow even if database save fails
    }

    ElMessage.success('Phase 1 completed successfully! Returning to dashboard...')
    router.push('/app/dashboard')
  } catch (error) {
    console.error('Phase 1 completion error:', error)
    ElMessage.error('Failed to complete Phase 1. Please try again.')
  } finally {
    loading.value = false
  }
}

// Load organization data from backend
const loadOrganizationData = async () => {
  try {
    // Get organization code from localStorage (stored during login)
    const orgCode = localStorage.getItem('user_organization_code')
    const orgId = localStorage.getItem('user_organization_id')

    if (!orgCode && !orgId) {
      console.warn('No organization code or ID found in localStorage')
      return
    }

    // Build query params
    const params = orgCode ? `?code=${orgCode}` : (orgId ? `?id=${orgId}` : '')

    // Fetch organization details using dashboard endpoint
    const orgResponse = await axios.get(`/api/organization/dashboard${params}`)
    const orgData = orgResponse.data.organization

    if (orgData) {
      // Populate the organization form with real data
      organizationForm.value = {
        organizationName: orgData.name || '',
        organizationSize: orgData.organization_size || orgData.size || ''
      }
      console.log('Loaded organization data:', organizationForm.value)
    }
  } catch (error) {
    console.error('Error loading organization data:', error)
    // Keep default empty values if loading fails
  }
}

// Check if Phase 1 is already complete in database
const checkPhase1Completion = async () => {
  try {
    const orgId = authStore.organizationId
    if (!orgId) {
      console.log('[Phase1] No organization ID - Phase 1 not complete')
      return false
    }

    console.log('[Phase1] Checking Phase 1 completion for org:', orgId)

    // Check each task completion status
    try {
      // Check maturity assessment
      const maturityResponse = await axios.get(`/api/phase1/maturity/${orgId}/latest`)
      const hasMaturity = maturityResponse.data.exists && maturityResponse.data.data

      // Check target group (replaces hasRoles check for low maturity orgs)
      // All orgs (low and high maturity) must select a target group
      const targetGroupResponse = await axios.get(`/api/phase1/target-group/${orgId}`)
      const hasTargetGroup = targetGroupResponse.data.success && targetGroupResponse.data.data

      // Check strategies selection
      const strategiesResponse = await axios.get(`/api/phase1/strategies/${orgId}/latest`)
      const hasStrategies = strategiesResponse.data.success && strategiesResponse.data.count > 0

      // Phase 1 is complete when all three tasks are done:
      // Task 1: Maturity Assessment (hasMaturity)
      // Task 2: Role Identification + Target Group Selection (hasTargetGroup)
      // Task 3: Strategy Selection (hasStrategies)
      // Note: Low maturity orgs don't define roles, but they DO select target group
      const isComplete = hasMaturity && hasTargetGroup && hasStrategies
      console.log('[Phase1] Phase 1 completion check result:', {
        hasMaturity,
        hasTargetGroup,
        hasStrategies,
        isComplete
      })

      return isComplete
    } catch (checkError) {
      console.error('[Phase1] Error checking task completion:', checkError)
      return false
    }
  } catch (error) {
    console.error('[Phase1] Error checking Phase 1 completion:', error)
    return false
  }
}

// Load organization data for employee view
const loadOrganizationResults = async () => {
  try {
    loading.value = true
    console.log('Loading organization results for employee view...')

    // Get organization code from localStorage (employee has it from login)
    const orgCode = localStorage.getItem('user_organization_code')
    if (!orgCode) {
      throw new Error('Organization code not found. Please log in again.')
    }

    // Get organization dashboard data
    const orgResponse = await axios.get('/api/organization/dashboard', {
      params: { code: orgCode }
    })
    const orgData = orgResponse.data.organization

    if (orgData) {
      // Check if Phase 1 is completed by checking if maturity_score exists
      const phase1Completed = orgData.phase1_completed || (orgData.maturity_score !== null && orgData.selected_archetype !== null)

      organizationData.value = {
        name: orgData.name || orgData.organization_name,
        size: orgData.size || orgData.organization_size,
        maturityScore: orgData.maturity_score,
        selectedArchetype: orgData.selected_archetype,
        secondaryArchetype: orgData.secondary_archetype,
        completedDate: orgData.phase1_completed_at || new Date().toISOString(),
        employeeCount: orgData.employee_count || 0,
        assessmentStatus: phase1Completed ? 'completed' : 'pending'
      }

      console.log('Loaded organization data for employee:', organizationData.value)
    } else {
      console.warn('No organization data found')
      organizationData.value = {
        name: 'Your Organization',
        assessmentStatus: 'pending',
        message: 'Phase 1 assessment has not been completed by your administrator yet.'
      }
    }
  } catch (error) {
    console.error('Error loading organization results:', error)
    organizationData.value = {
      name: 'Your Organization',
      assessmentStatus: 'error',
      message: 'Unable to load organization assessment data. Please contact your administrator.'
    }
  } finally {
    loading.value = false
  }
}

// Watch currentStep to debug Review page display issues
watch(currentStep, (newStep, oldStep) => {
  console.log(`[PhaseOne] Step changed from ${oldStep} to ${newStep}`)

  if (newStep === 4) {
    // Landing on Review page
    console.log('[PhaseOne] === REVIEW PAGE (Step 4) ===')
    console.log('[PhaseOne] phase1RolesData.value:', phase1RolesData.value)
    console.log('[PhaseOne] phase1RolesData.value?.roles:', phase1RolesData.value?.roles)
    console.log('[PhaseOne] phase1RolesData.value?.count:', phase1RolesData.value?.count)
    console.log('[PhaseOne] phase1TargetGroupData.value:', phase1TargetGroupData.value)
    console.log('[PhaseOne] maturityResults.value:', maturityResults.value)
    console.log('[PhaseOne] phase1StrategyData.value:', phase1StrategyData.value)
  }
})

// Lifecycle
onMounted(async () => {
  try {
    console.log('[Phase1] Component mounting...')

    // Ensure auth store is initialized
    if (!authStore.isAuthenticated) {
      console.log('[Phase1] Authenticating user...')
      await authStore.checkAuth()
    }

    console.log('[Phase1] User authenticated:', {
      userId: authStore.userId,
      role: authStore.user?.role,
      orgId: authStore.organizationId
    })

    // Different initialization for employees vs admins
    if (isEmployeeView.value) {
      console.log('[Phase1] Initializing employee view...')
      await loadOrganizationResults()

      // Also load all Phase 1 data for employee to view
      console.log('[Phase1] Loading Phase 1 data for employee view...')
      await loadOrganizationData()
      await loadLatestMaturityAssessment()
      await loadLatestTask2Data()
      await loadLatestTask3Data()
    } else {
      console.log('[Phase1] Initializing admin view...')

      // Check if Phase 1 is already complete in database
      const isPhase1Complete = await checkPhase1Completion()
      console.log('[Phase1] Phase 1 completion status:', isPhase1Complete)

      // Load organization data first to pre-fill organization name
      await loadOrganizationData()

      if (isPhase1Complete) {
        console.log('[Phase1] Phase 1 already complete - loading all saved data...')
        // Load all saved Phase 1 data
        await loadLatestMaturityAssessment()
        await loadLatestTask2Data()
        await loadLatestTask3Data()
        // Note: loadLatestResponses is for old questionnaire system, not needed for Phase 1

        // Go directly to Review step
        console.log('[Phase1] Navigating to Review & Confirm (step 4)')
        currentStep.value = 4
        archetypeCompleted.value = true
      } else {
        console.log('[Phase1] Phase 1 not complete - loading partial data...')
        // Load latest maturity assessment if exists
        await loadLatestMaturityAssessment()
        // Load latest Task 2 data (roles and target group) if exists
        await loadLatestTask2Data()
        // Load latest Task 3 data (strategies) if exists
        await loadLatestTask3Data()
        await loadMaturityQuestionnaire()
        // Note: loadLatestResponses is for old questionnaire system, not needed for Phase 1
        // Phase 1 data is loaded by the specific loaders above
        // After loading responses, determine the appropriate step
        await determineCurrentStep()
      }
    }

    console.log('[Phase1] Initialization complete. Current step:', currentStep.value)
  } catch (error) {
    console.error('[Phase1] Error initializing Phase One:', error)
  }
})

// Helper function to determine what step user should be on based on completion status
const determineCurrentStep = async () => {
  // Check completion status of all tasks
  const hasMaturity = maturityCompleted.value || (maturityResults.value && maturityResults.value.id)
  const hasTargetGroup = phase1TargetGroupData.value && phase1TargetGroupData.value.size_range
  const hasStrategies = strategyCompleted.value

  // Check if roles were identified (needed for STANDARD pathway)
  const hasRoles = phase1RolesData.value && phase1RolesData.value.roles?.length > 0

  // Determine if org uses STANDARD pathway (seProcessesValue >= 3)
  const seProcessesValue = maturityResults.value?.strategyInputs?.seProcessesValue || 0
  const isStandardPathway = seProcessesValue >= 3

  // Task 2 is fully complete when:
  // - TASK_BASED pathway: only target group needed (roles are skipped)
  // - STANDARD pathway: target group AND roles must be identified
  const isTask2Complete = hasTargetGroup && (!isStandardPathway || hasRoles)

  console.log('[Phase1] Determining step - maturity:', hasMaturity, 'targetGroup:', hasTargetGroup, 'strategies:', hasStrategies, 'roles:', hasRoles, 'standardPathway:', isStandardPathway, 'task2Complete:', isTask2Complete)

  // Determine appropriate step based on completion
  if (hasMaturity && isTask2Complete && hasStrategies) {
    // All tasks completed - show Review & Confirm step
    console.log('[Phase1] All tasks complete - going to Review (step 4)')
    currentStep.value = 4
    await loadOrganizationData()
    // Set old archetype completion for backward compatibility
    archetypeCompleted.value = true
  } else if (hasMaturity && isTask2Complete) {
    // Maturity and Task 2 complete, need strategies
    console.log('[Phase1] Maturity and Task 2 complete - going to Strategy Selection (step 3)')
    currentStep.value = 3
  } else if (hasMaturity) {
    // Only maturity complete, need role identification / target group
    console.log('[Phase1] Only maturity complete - going to Role Identification (step 2)')
    currentStep.value = 2
  } else {
    // Start at maturity assessment
    console.log('[Phase1] Starting at Maturity Assessment (step 1)')
    currentStep.value = 1
  }

  console.log(`[Phase1] Determined current step: ${currentStep.value}`)
}
</script>

<style scoped>
.phase-one {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #FFCA28 0%, #FFB300 100%);
  border-radius: 12px;
  color: #212121;
  box-shadow: 0 4px 12px rgba(255, 179, 0, 0.3);
}

.employee-info-banner {
  margin-bottom: 24px;
}

.employee-results-view {
  min-height: 400px;
}

.admin-assessment-flow {
  /* Existing admin flow styles */
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
}

.phase-title p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.phase-progress {
  text-align: right;
  min-width: 200px;
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-weight: 500;
}

.phase-steps {
  margin-bottom: 32px;
}

.step-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e9ecef;
}

.assessment-intro {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.assessment-intro p {
  margin: 0 0 8px 0;
  color: #6c757d;
}

.category-section {
  margin-bottom: 40px;
  padding: 24px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.category-title {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
}

.category-description {
  margin: 0 0 24px 0;
  color: #6c757d;
}

.question-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.question-content {
  flex: 1;
  margin-right: 24px;
}

.question-title {
  margin: 0 0 8px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
}

.question-description {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.question-rating {
  flex-shrink: 0;
}

.maturity-summary {
  margin-top: 32px;
}

.selection-intro {
  margin-bottom: 32px;
  text-align: center;
}

.recommended-badge {
  margin-top: 16px;
}

.archetypes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.archetype-card {
  position: relative;
  padding: 24px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.archetype-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.archetype-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.archetype-card.recommended {
  border-color: #67c23a;
  background: #f0f9f2;
}

.archetype-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.archetype-name {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.recommended-icon {
  color: #67c23a;
  font-size: 20px;
}

.archetype-description {
  margin: 0 0 20px 0;
  color: #6c757d;
  line-height: 1.5;
}

.archetype-details {
  margin-bottom: 16px;
}

.detail-item {
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.detail-item strong {
  color: #2c3e50;
  margin-right: 8px;
}

.archetype-focus {
  margin-bottom: 16px;
}

.selection-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.archetype-details-panel {
  margin-top: 32px;
}

.detailed-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.info-section h5 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
}

.info-section p {
  margin: 0 0 16px 0;
  color: #6c757d;
}

.info-section ul {
  margin: 0;
  padding-left: 20px;
  color: #6c757d;
}

.info-section li {
  margin-bottom: 8px;
}

.review-summary {
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Results Card Styling */
.results-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.results-card h4 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

/* Organization Overview */
.overview-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.overview-header h4 {
  margin: 0;
}

.organization-overview {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 16px 0;
}

.org-icon-wrapper {
  flex-shrink: 0;
}

.org-icon-circle {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
  border: 3px solid #1976D2;
}

.org-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.org-name-display {
  padding: 0;
}

.org-name-large {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1976D2;
  letter-spacing: -0.5px;
}

.org-size-display {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #1976D2;
}

.size-label {
  font-size: 1rem;
  color: #606266;
  font-weight: 600;
}

.size-value {
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 700;
}

/* Responsive adjustments for Organization Overview */
@media (max-width: 768px) {
  .organization-overview {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .org-icon-circle {
    width: 80px;
    height: 80px;
  }

  .org-name-large {
    font-size: 1.5rem;
  }
}

/* Assessment Results Layout */
.assessment-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Top row: Maturity and Strategy side by side */
.results-row-top {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 768px) {
  .results-row-top {
    grid-template-columns: 1fr 1fr;
  }

  .maturity-score-display {
    justify-content: flex-start;
  }
}

/* Bottom row: Roles full width */
.results-row-bottom {
  width: 100%;
}

/* Maturity Results */
.maturity-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.maturity-score-display-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.score-circle-centered {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.maturity-level-info {
  text-align: center;
  width: 100%;
  padding: 0 16px;
}

.maturity-level-info h3 {
  margin: 0 0 12px 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.level-description {
  margin: 0;
  color: #6c757d;
  line-height: 1.6;
  font-size: 0.95rem;
}

.level-meter {
  width: 100%;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.meter-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.meter-label {
  font-size: 0.75rem;
  color: #606266;
  font-weight: 600;
  text-align: center;
  flex: 1;
}

.field-scores-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
  padding: 0 8px;
}

.field-score-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #1976D2;
}

.field-label {
  font-size: 0.85rem;
  color: #606266;
  font-weight: 600;
}

.field-value {
  font-size: 1.1rem;
  color: #1976D2;
  font-weight: 700;
}

.score-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.score-item .label {
  color: #6c757d;
  font-size: 0.9rem;
}

.score-item .value {
  color: #2c3e50;
  font-weight: 600;
}

/* Archetype Results */
.archetype-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.archetype-selection {
  text-align: center;
}

.archetype-badge {
  margin-bottom: 16px;
}

.archetype-description {
  margin-bottom: 20px;
}

.archetype-description p {
  margin: 0;
  color: #6c757d;
  line-height: 1.6;
  font-size: 1rem;
}

.archetype-characteristics {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

.archetype-characteristics h5 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
}

.archetype-characteristics ul {
  margin: 0;
  padding-left: 20px;
  color: #6c757d;
}

.archetype-characteristics li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.summary-section {
  margin-bottom: 32px;
}

.summary-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.1rem;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.summary-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-item {
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.summary-item strong {
  color: #2c3e50;
  margin-right: 8px;
}

.maturity-overview {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
}

.score-value {
  font-size: 2rem;
  font-weight: 700;
  color: #409eff;
}

.score-label {
  color: #6c757d;
}

.maturity-level {
  font-weight: 600;
  color: #2c3e50;
}

.category-scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.category-score {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
}

.category-name {
  color: #2c3e50;
}

.category-value {
  font-weight: 600;
  color: #409eff;
}

.archetype-summary {
  text-align: left;
}

.archetype-name-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.archetype-name-summary h5 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

.archetype-key-info {
  margin-top: 16px;
}

.key-info-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.key-info-item strong {
  display: block;
  margin-bottom: 4px;
  color: #2c3e50;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.key-info-item span {
  color: #6c757d;
  font-size: 0.9rem;
}

.completion-message {
  margin-bottom: 32px;
}

.assessment-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.assessment-status,
.archetype-status {
  display: flex;
  justify-content: center;
}

.response-details {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.response-details p {
  margin: 8px 0;
  font-size: 14px;
}

.response-details p:last-child {
  margin-bottom: 0;
}

.archetype-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.maturity-result {
  margin-top: 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.maturity-level h5 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1rem;
}

.level-display {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.level-description {
  font-size: 14px;
  color: #6c757d;
  line-height: 1.5;
  text-align: center;
  margin: 0;
}

.archetype-result {
  margin-top: 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.archetype-selection h5 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1rem;
}

.archetype-display {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.archetype-description {
  font-size: 14px;
  color: #6c757d;
  line-height: 1.5;
  text-align: center;
  margin: 0 0 16px 0;
}

.archetype-characteristics {
  margin-top: 12px;
}

.archetype-characteristics h6 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.archetype-characteristics ul {
  margin: 0;
  padding-left: 20px;
  color: #6c757d;
}

.archetype-characteristics li {
  margin-bottom: 4px;
  font-size: 13px;
}

.maturity-score-summary {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  padding: 16px;
}

.score-circle-container {
  flex-shrink: 0;
}

.maturity-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 400px;
  text-align: left;
}

.score-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-item-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.score-item-inline .label {
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.score-item-inline .value {
  color: #2c3e50;
  font-weight: 600;
  font-size: 1rem;
}

/* Roles Review Styles */
.roles-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.roles-count-summary {
  padding: 16px 0 8px 0;
  border-bottom: 2px solid #e0e0e0;
}

.count-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1976D2;
}

.roles-list-review {
  padding: 8px 0;
}

.no-roles-note {
  padding: 12px 0;
  margin: 8px 0;
}

.roles-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 768px) {
  .roles-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1200px) {
  .roles-list {
    grid-template-columns: repeat(3, 1fr);
  }
}

.role-list-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-left: 3px solid #1976D2;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.role-list-item:hover {
  background: #e3f2fd;
  border-left-color: #0d47a1;
  transform: translateX(4px);
}

.role-bullet {
  font-size: 1.5rem;
  color: #1976D2;
  line-height: 1.4;
  font-weight: bold;
}

.role-name {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.6;
}

.target-group-display {
  padding: 20px;
  border-top: 2px solid #e0e0e0;
  margin-top: 8px;
}

.target-group-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.target-label {
  font-size: 1rem;
  font-weight: 600;
  color: #606266;
}

.target-size-value-inline {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1976D2;
  padding: 4px 16px;
  background: #e3f2fd;
  border-radius: 6px;
  border: 2px solid #1976D2;
}

/* Strategy Review Styles */
.strategy-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* New Strategy Count Design */
.strategy-count-summary-new {
  margin-bottom: 24px;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
}

.count-number {
  font-size: 28px;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.count-text {
  font-size: 15px;
  font-weight: 500;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Strategy List */
.strategies-list-review {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Simplified Strategy Item Design */
.strategy-review-item-simple {
  padding: 14px 18px;
  background: #ffffff;
  border: 2px solid #e4e7ed;
  border-left: 4px solid #409eff;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.strategy-review-item-simple:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}

.strategy-name-simple {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  line-height: 1.4;
}

.strategy-review-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.strategy-review-details h5 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.4;
}

.strategy-warning-small {
  margin-top: 4px;
}

.user-preference-display {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .phase-one {
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

  .archetypes-grid {
    grid-template-columns: 1fr;
  }

  .question-item {
    flex-direction: column;
    gap: 16px;
  }

  .detailed-info {
    grid-template-columns: 1fr;
  }

  .maturity-overview {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .strategy-review-item {
    flex-direction: column;
  }
}
</style>