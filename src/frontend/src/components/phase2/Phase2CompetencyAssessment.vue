<template>
  <el-card class="phase2-assessment step-card">
    <template #header>
      <div class="card-header">
        <h2>Phase 2 - Task 2: Competency Self-Assessment</h2>
        <p style="color: #606266; font-size: 14px; margin-top: 8px;">
          Assess your current competency level for the identified SE competencies.
        </p>
      </div>
    </template>

    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Error state -->
    <el-alert
      v-else-if="error"
      type="error"
      :title="error"
      show-icon
      :closable="false"
    />

    <!-- Assessment questions -->
    <div v-else-if="!assessmentComplete" class="survey-container">
      <!-- Guidance Info Box -->
      <div class="info-box survey-guidance-box">
        <div class="info-box-header">
          <el-icon><InfoFilled /></el-icon>
          <h4>How to Complete This Assessment</h4>
        </div>
        <ul class="info-points">
          <li>
            This self-assessment is based on the <strong>INCOSE Systems Engineering Competency Framework</strong>.
            For each of the {{ totalQuestions }} identified competencies, you will see <strong>4 proficiency groups</strong>
            with behavioral indicators describing what someone at that level typically does.
          </li>
          <li>
            <strong>How to rate yourself:</strong> Read the indicators in each group and select the group(s)
            that best describe your <strong>current abilities</strong>. You may select multiple groups if you
            identify with indicators across levels. Select Group 5 if none of the descriptions apply to you.
          </li>
          <li>
            <strong>Why accuracy matters:</strong> Your self-rating is compared to the required competency level
            for your role(s). The gap between your current level and the required level determines which
            training modules will be created in Phase 3. Honest self-assessment leads to a more effective training plan.
          </li>
          <li class="note">
            Data source: Competency indicators from the INCOSE SE Competency Framework.
            Required levels derived from the role-to-competency mapping (Phase 1).
          </li>
        </ul>
      </div>

      <!-- Survey header - Derik's style -->
      <div class="survey-header">
        <h3>Systems Engineering Competency Assessment Survey</h3>

        <div class="question-info">
          <h4 class="question-number">
            Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }}
          </h4>
          <p class="question-text">
            To which of these groups do you identify yourself?
          </p>
        </div>
      </div>

      <!-- Indicator group wrapper - Derik's style -->
      <div class="indicator-group-wrapper">
        <div class="level-cards-container">
          <!-- Groups 1-4: Show actual indicators from competency levels -->
          <el-card
            v-for="(group, index) in currentIndicatorGroups"
            :key="'group-' + (index + 1)"
            :class="['indicator-card', { 'selected': isGroupSelected(index + 1) }]"
            @click="toggleGroup(index + 1)"
            shadow="hover"
          >
            <div class="card-content">
              <div class="group-header">
                <strong class="group-title">Group {{ index + 1 }}</strong>
              </div>
              <hr class="separator-line">

              <!-- Display all indicators for this level -->
              <div class="indicators-list">
                <div
                  v-for="(indicator, i) in group.indicators"
                  :key="i"
                  class="indicator-item"
                >
                  <p class="indicator-text">{{ indicator.indicator_en }}</p>
                  <hr v-if="i < group.indicators.length - 1" class="separator-line">
                </div>
              </div>
              <hr class="separator-line">
            </div>
          </el-card>

          <!-- Group 5: "You do not see yourselves in any of these groups" -->
          <el-card
            :class="['indicator-card', 'none-option', { 'selected': isGroupSelected(5) }]"
            @click="selectNone"
            shadow="hover"
          >
            <div class="card-content">
              <div class="group-header">
                <strong class="group-title">Group 5</strong>
              </div>
              <hr class="separator-line">
              <p class="indicator-text">You do not see yourselves in any of these groups.</p>
              <hr class="separator-line">
            </div>
          </el-card>
        </div>
      </div>

      <!-- Validation message -->
      <el-alert
        v-if="showValidation && selectedGroups.length === 0"
        type="warning"
        :closable="false"
        show-icon
        style="margin-top: 20px;"
      >
        Please select at least one group before proceeding.
      </el-alert>

      <!-- Navigation buttons - Derik's style -->
      <div class="navigation-buttons">
        <el-button
          @click="goBack"
          color="#1976d2"
          size="large"
        >
          Back
        </el-button>

        <el-button
          v-if="currentQuestionIndex < totalQuestions - 1"
          @click="goNext"
          :disabled="selectedGroups.length === 0"
          color="#4CAF50"
          size="large"
        >
          Next
        </el-button>

        <el-button
          v-else
          @click="handleSubmit"
          :disabled="selectedGroups.length === 0"
          :loading="submitting"
          color="#4CAF50"
          size="large"
        >
          Submit Survey
        </el-button>
      </div>
    </div>

    <!-- Assessment complete message (temporary before redirect) -->
    <div v-else class="assessment-complete">
      <el-result
        icon="success"
        title="Assessment Submitted Successfully"
        sub-title="Processing your results..."
      >
        <template #extra>
          <el-progress :percentage="100" status="success" />
        </template>
      </el-result>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, ArrowRight, Check, InfoFilled } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { phase2Task2Api } from '@/api/phase2'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'

const props = defineProps({
  assessmentId: {
    type: Number,
    required: true
  },
  competencies: {
    type: Array,
    required: true
  },
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['complete', 'back'])

const authStore = useAuthStore()

// State
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const showValidation = ref(false)
const assessmentComplete = ref(false)

// Questions data
const currentQuestionIndex = ref(0)
const answers = ref([]) // Stores { competency_id, selected_groups, current_level }
const currentIndicatorsByLevel = ref([]) // Stores indicators for current competency
const allIndicatorData = ref({}) // Cache all indicator data

// Current question state
const selectedGroups = ref([])

// Computed properties
const totalQuestions = computed(() => props.competencies.length)

const currentCompetency = computed(() => {
  return props.competencies[currentQuestionIndex.value] || {}
})

const currentIndicatorGroups = computed(() => {
  if (!currentIndicatorsByLevel.value || currentIndicatorsByLevel.value.length === 0) {
    return []
  }

  // Backend returns levels as numeric strings: "1", "2", "3", "4"
  // Map them to Groups 1-4 with proper labels
  const levelOrder = ['1', '2', '3', '4']
  const levelNames = ['Know', 'Understand', 'Apply', 'Master']

  return levelOrder.map((levelNum, index) => {
    const levelData = currentIndicatorsByLevel.value.find(l => l.level === levelNum || l.level === parseInt(levelNum))
    return {
      groupNumber: index + 1,
      level: levelNum,
      levelName: levelNames[index],
      indicators: levelData?.indicators || []
    }
  })
})

/**
 * Lifecycle: Bulk load all indicators on mount - Derik's pattern
 */
onMounted(async () => {
  if (props.competencies && props.competencies.length > 0) {
    await loadAllCompetencyIndicators()
    setCurrentCompetencyData()
    loadSavedAnswer()
  }
})

/**
 * Bulk load all competency indicators at once - Derik's pattern
 * This ensures fast transitions between questions
 */
const loadAllCompetencyIndicators = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('[Phase2 Assessment] Bulk loading indicators for', props.competencies.length, 'competencies')

    // Fetch indicators for all competencies in parallel
    const indicatorPromises = props.competencies.map(async (comp) => {
      try {
        const response = await fetch(
          `/api/get_competency_indicators_for_competency/${comp.competencyId}`
        )

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        return { competencyId: comp.competencyId, data }
      } catch (err) {
        console.error(`[Phase2 Assessment] Error loading indicators for competency ${comp.competencyId}:`, err)
        return { competencyId: comp.competencyId, data: [] }
      }
    })

    const results = await Promise.all(indicatorPromises)

    // Cache all indicator data
    results.forEach(({ competencyId, data }) => {
      allIndicatorData.value[competencyId] = data
    })

    console.log('[Phase2 Assessment] All indicators loaded:', Object.keys(allIndicatorData.value).length, 'competencies')
    toast.success('Assessment questions loaded successfully')
  } catch (err) {
    console.error('[Phase2 Assessment] Error bulk loading indicators:', err)
    error.value = 'Failed to load assessment questions'
    toast.error('Failed to load assessment questions')
  } finally {
    loading.value = false
  }
}

/**
 * Set current competency data from cache - Derik's pattern
 */
const setCurrentCompetencyData = () => {
  const competencyId = currentCompetency.value.competencyId

  if (!competencyId) {
    console.warn('[Phase2 Assessment] No competency ID available')
    return
  }

  // Get cached data
  if (allIndicatorData.value[competencyId]) {
    currentIndicatorsByLevel.value = allIndicatorData.value[competencyId]
    console.log(`[Phase2 Assessment] Set indicators for competency ${competencyId}:`, currentIndicatorsByLevel.value)
    console.log(`[Phase2 Assessment] Current indicator groups computed:`, currentIndicatorGroups.value)
  } else {
    console.warn(`[Phase2 Assessment] No cached data found for competency ${competencyId}`)
    currentIndicatorsByLevel.value = []
  }
}

/**
 * Load saved answer for current question (if exists)
 */
const loadSavedAnswer = () => {
  const competencyId = currentCompetency.value.competencyId
  const savedAnswer = answers.value.find(a => a.competency_id === competencyId)

  if (savedAnswer) {
    selectedGroups.value = [...savedAnswer.selected_groups]
  } else {
    selectedGroups.value = []
  }
}

/**
 * Save current answer before navigating
 */
const saveCurrentAnswer = () => {
  const competencyId = currentCompetency.value.competencyId
  const currentLevel = calculateScore(selectedGroups.value)

  // Remove existing answer for this competency
  answers.value = answers.value.filter(a => a.competency_id !== competencyId)

  // Add new answer
  if (selectedGroups.value.length > 0) {
    answers.value.push({
      competency_id: competencyId,
      selected_groups: [...selectedGroups.value],
      current_level: currentLevel
    })
  }
}

/**
 * Calculate competency score from selected groups
 * Based on Derik's mapping: Group 1→1, Group 2→2, Group 3→4, Group 4→6, Group 5→0
 */
const calculateScore = (groups) => {
  if (groups.length === 0 || groups.includes(5)) return 0

  const maxGroup = Math.max(...groups.filter(g => g !== 5))

  if (maxGroup === 1) return 1       // kennen
  else if (maxGroup === 2) return 2  // verstehen
  else if (maxGroup === 3) return 4  // anwenden
  else if (maxGroup === 4) return 6  // beherrschen
  else return 0
}

/**
 * Toggle group selection
 */
const toggleGroup = (groupNumber) => {
  // If Group 5 is selected, deselect it when selecting 1-4
  if (selectedGroups.value.includes(5)) {
    selectedGroups.value = []
  }

  const index = selectedGroups.value.indexOf(groupNumber)
  if (index > -1) {
    selectedGroups.value.splice(index, 1)
  } else {
    selectedGroups.value.push(groupNumber)
  }
}

/**
 * Select "None of these" (Group 5)
 */
const selectNone = () => {
  // Deselect all other groups and select Group 5
  selectedGroups.value = [5]
}

/**
 * Check if a group is selected
 */
const isGroupSelected = (groupNumber) => {
  return selectedGroups.value.includes(groupNumber)
}

/**
 * Navigate to previous question
 */
const goBack = () => {
  if (currentQuestionIndex.value > 0) {
    // Regular back navigation between questions
    saveCurrentAnswer()
    currentQuestionIndex.value--
    setCurrentCompetencyData()
    loadSavedAnswer()
    showValidation.value = false
  } else {
    // At first question - go back to Necessary Competencies page
    emit('back')
  }
}

/**
 * Navigate to next question
 */
const goNext = () => {
  if (selectedGroups.value.length === 0) {
    showValidation.value = true
    toast.warning('Please select at least one group')
    return
  }

  saveCurrentAnswer()

  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++
    setCurrentCompetencyData()
    loadSavedAnswer()
    showValidation.value = false
  }
}

/**
 * Submit assessment
 */
const handleSubmit = async () => {
  // Validate current question
  if (selectedGroups.value.length === 0) {
    showValidation.value = true
    toast.warning('Please select at least one group')
    return
  }

  // Save current answer
  saveCurrentAnswer()

  // Validate all questions answered
  if (answers.value.length !== totalQuestions.value) {
    toast.warning(`Please answer all ${totalQuestions.value} questions`)
    return
  }

  // Show confirmation dialog
  try {
    await ElMessageBox.confirm(
      'You have answered all questions. Once submitted, you cannot modify your answers. Do you want to proceed with the submission?',
      'Confirm Submission',
      {
        confirmButtonText: 'Submit Assessment',
        cancelButtonText: 'Review Answers',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
  } catch (action) {
    // User clicked cancel or closed dialog
    if (action === 'cancel') {
      toast.info('You can navigate back to review your answers')
    }
    return
  }

  submitting.value = true

  try {
    console.log('[Phase2 Assessment] Submitting answers:', answers.value)

    const response = await phase2Task2Api.submitAssessment(
      props.assessmentId,
      answers.value
    )

    if (response.success) {
      console.log('[Phase2 Assessment] Submission successful')
      toast.success('Assessment submitted successfully!')

      assessmentComplete.value = true

      // Emit completion event with results after a short delay
      setTimeout(() => {
        emit('complete', {
          assessmentId: props.assessmentId,
          results: response.results,
          summary: response.summary
        })
      }, 1500)
    }
  } catch (err) {
    console.error('[Phase2 Assessment] Error submitting assessment:', err)
    toast.error('Failed to submit assessment')
    assessmentComplete.value = false
  } finally {
    submitting.value = false
  }
}

/**
 * Get level name from numeric value
 */
const getLevelName = (level) => {
  const mapping = {
    0: 'Not Relevant',
    1: 'Know',
    2: 'Understand',
    4: 'Apply',
    6: 'Master'
  }
  return mapping[level] || `Level ${level}`
}

/**
 * Get tag type based on competency area
 */
const getAreaTagType = (area) => {
  const mapping = {
    'Core': 'primary',
    'Social / Personal': 'success',
    'Management': 'warning',
    'Technical': 'danger'
  }
  return mapping[area] || 'info'
}
</script>

<style scoped>
.phase2-assessment {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.loading-container {
  padding: 20px;
}

/* Guidance Info Box */
.info-box {
  background: #F8F9FA;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.info-box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-box-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.info-points {
  margin: 0;
  padding-left: 20px;
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
}

.info-points li {
  margin-bottom: 4px;
}

.info-points li strong {
  color: #303133;
}

.info-points li.note {
  color: #909399;
  font-style: italic;
}

.survey-guidance-box {
  background: #F0F9EB;
  border-color: #E1F3D8;
}

.survey-guidance-box .info-box-header .el-icon {
  color: #67C23A;
}

/* Survey container - Derik's style */
.survey-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  position: relative;
}

.survey-header {
  text-align: center;
  margin-bottom: 2rem;
}

.survey-header h3 {
  color: #303133;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.question-info {
  margin-top: 1.5rem;
}

.question-number {
  color: #303133;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.question-text {
  color: #606266;
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

/* Outer wrapper for all indicator cards - Derik's style */
.indicator-group-wrapper {
  background: #F8F9FA;
  border: 1px solid #EBEEF5;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.level-cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 cards per row: Groups 1-3 in row 1, 4-5 in row 2 */
  gap: 1rem;
  width: 100%;
}

/* Individual indicator cards - Derik's exact styling */
.indicator-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #DCDFE6 !important;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  background: white;
}

.indicator-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  border-color: #409EFF !important;
}

.indicator-card.selected {
  border: 3px solid #4CAF50 !important;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4);
  background: #F8FFF8;
}

.indicator-card.none-option.selected {
  border-color: #E6A23C !important;
  box-shadow: 0 4px 20px rgba(230, 162, 60, 0.4);
  background: #FDF6EC;
}

.card-content {
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.group-header {
  text-align: center;
  margin-bottom: 1rem;
}

.group-title {
  color: #303133;
  font-size: 1.1rem;
  font-weight: bold;
  text-transform: uppercase;
}

/* Styling for separator lines - Derik's green */
.separator-line {
  border: 0;
  height: 1px;
  background: #4CAF50;
  margin: 0.75rem 0;
  width: 100%;
}

.indicators-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.indicator-item {
  margin-bottom: 0.5rem;
}

.indicator-text {
  color: #606266;
  font-size: 0.9rem;
  line-height: 1.4;
  text-align: left;
  margin: 0.5rem 0;
}

/* Navigation buttons - Derik's style */
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
}

.navigation-buttons .el-button {
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  font-size: 1rem;
}

/* Back button styling */
.navigation-buttons .el-button:first-child {
  background-color: #1976d2;
}

.navigation-buttons .el-button:first-child:hover {
  background-color: #1565c0;
}

/* Next/Submit button styling */
.navigation-buttons .el-button:last-child {
  background-color: #4CAF50;
}

.navigation-buttons .el-button:last-child:hover {
  background-color: #45a049;
}

.navigation-buttons .el-button:disabled {
  background-color: #DCDFE6;
  color: #909399;
}

/* Assessment complete */
.assessment-complete {
  padding: 40px;
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .level-cards-container {
    grid-template-columns: 1fr;
  }

  .navigation-buttons {
    flex-direction: column;
    gap: 1rem;
  }

  .survey-header h3 {
    font-size: 1.5rem;
  }

  .question-number {
    font-size: 1.2rem;
  }

  .indicator-group-wrapper {
    padding: 1rem;
  }
}
</style>
