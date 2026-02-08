<template>
  <div class="competency-results">
    <div v-if="loading" class="loading-container">
      <el-loading
        element-loading-text="Analyzing your assessment results..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      />
      <div class="progress-messages">
        <p class="loading-message">Our AI is generating a personalized assessment for you.</p>
      </div>
    </div>

    <div v-else class="results-content">
      <!-- Results Header -->
      <div class="results-header">
        <h2 class="results-title">Your SE Competency Assessment Results</h2>
        <p class="results-subtitle">
          Based on your responses across {{ competencyData.length }} competency areas
        </p>
      </div>

      <!-- Guidance Info Box -->
      <div class="info-box gap-analysis-guidance-box">
        <div class="info-box-header">
          <el-icon><InfoFilled /></el-icon>
          <h4>Understanding Your Gap Analysis</h4>
        </div>
        <ul class="info-points">
          <li>
            The results below show the <strong>gap between your current competency level</strong> (from the self-assessment)
            <strong>and the required level</strong> for your selected role(s). Competencies marked <strong>"Below Target"</strong>
            indicate areas where training is needed.
          </li>
          <li>
            <strong>How to read the radar chart:</strong> The <span style="color:#67c23a;font-weight:600;">green area</span> represents
            your current levels, and the <span style="color:#f56c6c;font-weight:600;">red outline</span> shows the required levels.
            Where the red extends beyond the green, there is a competency gap.
          </li>
          <li>
            <strong>What happens next:</strong> Competency gaps identified here will be used to generate
            <strong>Learning Objectives</strong> (Phase 2, Task 4) and subsequently to build
            <strong>training modules</strong> in Phase 3. An AI generates personalized feedback for each competency
            to help you understand your strengths and areas for improvement.
          </li>
          <li class="note">
            Data sources: Self-assessment scores (this phase), required competency levels from
            the role-competency matrix (Phase 1), AI-generated feedback per competency area.
          </li>
        </ul>
      </div>

      <!-- Assessment Summary -->
      <div class="summary-cards">
        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon size="32" color="#67c23a"><TrophyBase /></el-icon>
            </div>
            <div class="summary-content">
              <h3>Overall Score</h3>
              <p class="summary-value">{{ overallScore.toFixed(1) }}%</p>
              <p class="summary-desc">{{ getScoreDescription(overallScore) }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="summary-card" v-if="selectedRoles.length > 0">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon size="32" color="#e6a23c"><UserFilled /></el-icon>
            </div>
            <div class="summary-content">
              <h3>Selected {{ selectedRoles.length > 1 ? 'Roles' : 'Role' }}</h3>
              <p class="summary-value">{{ selectedRoles.length }}</p>
              <p class="summary-desc role-names">{{ getRoleNames() }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon">
              <el-icon size="32" color="#409eff"><DataBoard /></el-icon>
            </div>
            <div class="summary-content">
              <h3>Competencies Assessed</h3>
              <p class="summary-value">{{ competencyData.length }}</p>
              <p class="summary-desc">Across {{ uniqueAreas.length}} areas</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Competency Areas Selection -->
      <el-card class="chart-section">
        <template #header>
          <div class="chart-header">
            <h3>Competency Overview</h3>
            <p>Select competency areas to view detailed results</p>
          </div>
        </template>

        <div class="area-selection">
          <div class="area-chips">
            <el-tag
              v-for="area in uniqueAreas"
              :key="area"
              :type="selectedAreas.includes(area) ? 'primary' : 'info'"
              :effect="selectedAreas.includes(area) ? 'dark' : 'plain'"
              @click="toggleAreaSelection(area)"
              class="area-chip"
              size="large"
            >
              {{ area }}
            </el-tag>
          </div>
        </div>

        <!-- Radar Chart -->
        <div class="chart-container">
          <div v-if="chartData && filteredCompetencyData.length > 0" class="radar-chart">
            <Radar :data="chartData" :options="chartOptions" />
          </div>
          <div v-else class="chart-placeholder">
            <el-icon size="64" color="#c0c4cc"><DataBoard /></el-icon>
            <p>Select competency areas to view radar chart</p>
            <p class="chart-note">Visual representation of your competency levels across selected areas</p>
          </div>
        </div>
      </el-card>

      <!-- Detailed Competency Results -->
      <el-card class="competency-details">
        <template #header>
          <h3>Detailed Competency Analysis</h3>
        </template>

        <div class="competency-areas">
          <div
            v-for="area in filteredAreas"
            :key="area.name"
            class="area-section"
          >
            <div class="area-header">
              <h4 class="area-title">{{ area.name }}</h4>
              <el-tag :type="getAreaScoreType(area.averageScore)" size="large">
                {{ area.averageScore.toFixed(1) }}% {{ selectedRoles.length > 0 ? 'of your SE role requirements in this area' : 'Average in this area' }}
              </el-tag>
            </div>

            <div class="competencies-grid">
              <div
                v-for="competency in area.competencies"
                :key="competency.id"
                class="competency-item"
              >
                <div class="competency-header">
                  <h5 class="competency-name">{{ competency.name }}</h5>
                </div>

                <!-- Competency Levels Display -->
                <div class="competency-levels">
                  <div class="level-info">
                    <span class="level-label">Your Level:</span>
                    <span class="level-value current-level">{{ competency.scoreText }}</span>
                  </div>
                  <div class="level-info">
                    <span class="level-label">Required Level:</span>
                    <span class="level-value required-level">{{ competency.requiredText }}</span>
                  </div>
                  <div class="level-info">
                    <span class="level-label">Status:</span>
                    <el-tag
                      :type="competency.status === 'exceeded' ? 'success' : (competency.status === 'met' ? 'success' : 'warning')"
                      :effect="competency.status === 'below' ? 'dark' : 'light'"
                      size="small"
                    >
                      {{ competency.status === 'exceeded' ? 'Exceeded' : (competency.status === 'met' ? 'Met' : 'Below Target') }}
                    </el-tag>
                  </div>
                </div>

                <div class="competency-progress">
                  <el-progress
                    :percentage="competency.percentage > 100 ? 100 : competency.percentage"
                    :color="getProgressColor(competency.percentage)"
                    :stroke-width="8"
                  />
                  <p class="progress-label">
                    {{ competency.percentage }}% of required level
                    <span v-if="competency.percentage > 100" class="exceeded-note">
                      ({{ competency.percentage - 100 }}% above target)
                    </span>
                  </p>
                </div>

                <div class="competency-feedback">
                  <div v-if="competency.strengths" class="feedback-section">
                    <p class="feedback-label">Strengths:</p>
                    <p class="feedback-text">{{ competency.strengths }}</p>
                  </div>
                  <div v-if="competency.improvements" class="feedback-section">
                    <p class="feedback-label">
                      {{ competency.status === 'below' ? 'Areas for Improvement:' : 'Status:' }}
                    </p>
                    <p class="feedback-text">{{ competency.improvements }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Action Buttons -->
      <div class="actions">
        <el-button @click="retakeAssessment" size="large" type="warning">
          Retake Competency Assessment
        </el-button>
        <el-button @click="exportResults" size="large" type="info">
          <el-icon><Download /></el-icon>
          Export Results
        </el-button>
        <el-button v-if="authStore.isAdmin" type="primary" @click="goToLearningObjectives" size="large">
          Proceed to Learning Objectives
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {
  TrophyBase,
  DataBoard,
  UserFilled,
  Download,
  InfoFilled
} from '@element-plus/icons-vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  RadarController,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { useAuthStore } from '@/stores/auth'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  RadarController,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
)

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Props - Make assessmentData optional for persistent URL mode
const props = defineProps({
  assessmentData: {
    type: Object,
    required: false,
    default: null
  }
})

// Emits
const emit = defineEmits(['back', 'continue'])

// State
const loading = ref(true)
const selectedAreas = ref([])
const competencyData = ref([])
const maxScores = ref([])
const selectedRoles = ref([])  // Store selected roles for display

// Chart data for radar visualization
const chartData = ref(null)
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Competency Assessment Results',
      font: {
        size: 16,
        weight: 'bold'
      }
    },
    legend: {
      position: 'bottom',
      labels: {
        padding: 20,
        usePointStyle: true
      }
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          return `${context.dataset.label}: ${context.parsed.r}/6 (${Math.round((context.parsed.r/6)*100)}%)`
        }
      }
    }
  },
  scales: {
    r: {
      angleLines: {
        display: true
      },
      suggestedMin: 0,
      suggestedMax: 6,
      ticks: {
        stepSize: 1,
        callback: function(value) {
          const labels = ['0', '1 - Aware', '2 - Understanding', '3', '4 - Applying', '5', '6 - Mastering']
          return labels[value] || value
        }
      },
      pointLabels: {
        font: {
          size: 11
        },
        callback: function(label) {
          // Truncate long labels
          return label.length > 20 ? label.substring(0, 17) + '...' : label
        }
      }
    }
  }
})

// Computed properties
const uniqueAreas = computed(() => {
  return [...new Set(competencyData.value.map(comp => comp.area))]
})

const filteredAreas = computed(() => {
  const areas = {}

  competencyData.value
    .filter(comp => selectedAreas.value.length === 0 || selectedAreas.value.includes(comp.area))
    .forEach(comp => {
      if (!areas[comp.area]) {
        areas[comp.area] = {
          name: comp.area,
          competencies: [],
          totalScore: 0,
          count: 0
        }
      }
      areas[comp.area].competencies.push(comp)
      areas[comp.area].totalScore += comp.percentage
      areas[comp.area].count++
    })

  // Calculate average scores for each area
  // Note: totalScore already includes uncapped percentages from line 334
  // For consistency, we'll recalculate with capped percentages
  Object.values(areas).forEach(area => {
    const cappedTotal = area.competencies.reduce((sum, comp) => {
      return sum + Math.min(comp.percentage, 100)
    }, 0)
    area.averageScore = cappedTotal / area.count
  })

  return Object.values(areas)
})

const overallScore = computed(() => {
  if (competencyData.value.length === 0) return 0
  // Cap each competency percentage at 100% for overall score calculation
  // This prevents inflated averages when users exceed requirements
  const total = competencyData.value.reduce((sum, comp) => {
    const cappedPercentage = Math.min(comp.percentage, 100)
    return sum + cappedPercentage
  }, 0)
  return total / competencyData.value.length
})

const filteredCompetencyData = computed(() => {
  return competencyData.value.filter(comp =>
    selectedAreas.value.length === 0 || selectedAreas.value.includes(comp.area)
  )
})

// Methods
const processAssessmentData = async () => {
  try {
    loading.value = true

    let user_scores, max_scores, feedback_list, apiSelectedRoles, type

    // Check if we have an assessment_id from route params (persistent URL mode)
    const assessmentId = route.params.id

    if (assessmentId) {
      // Mode 1: Fetch by assessment_id from new API endpoint (persistent URL)
      console.log('Fetching results by assessment ID:', assessmentId)

      const response = await axios.get(`/api/assessment/${assessmentId}/results`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      const data = response.data
      user_scores = data.user_scores
      max_scores = data.max_scores
      feedback_list = data.feedback_list
      apiSelectedRoles = data.selected_roles_data || []
      type = data.assessment?.assessment_type

      console.log('Received from new authenticated API:', data)
    } else if (props.assessmentData && props.assessmentData.assessment_id) {
      // Mode 2: Fetch by assessment_id from new API (immediate results after submission)
      const assessmentIdFromProps = props.assessmentData.assessment_id
      const propRoles = props.assessmentData.selectedRoles || []
      const propType = props.assessmentData.type

      console.log('Fetching results by assessment ID from props:', assessmentIdFromProps)

      const response = await axios.get(`/api/assessment/${assessmentIdFromProps}/results`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      const data = response.data
      user_scores = data.user_scores
      max_scores = data.max_scores
      feedback_list = data.feedback_list
      apiSelectedRoles = data.selected_roles_data || propRoles || []
      type = data.assessment?.assessment_type || propType

      console.log('Received from new authenticated API (props mode):', data)
    } else {
      throw new Error('No assessment ID or assessment data provided')
    }

    // Store max scores for chart
    maxScores.value = max_scores || []

    // Create feedback map for quick lookup
    const feedbackMap = {}
    if (feedback_list && feedback_list.length > 0) {
      feedback_list.forEach(areaFeedback => {
        if (areaFeedback.feedbacks) {
          areaFeedback.feedbacks.forEach(fb => {
            feedbackMap[fb.competency_name] = {
              strengths: fb.user_strengths,
              improvements: fb.improvement_areas
            }
          })
        }
      })
    }

    // Helper function to map database survey levels to display levels
    // Database stores: 0, 1, 2, 3, 4
    // Display needs: 0, 1, 2, 4, 6
    const mapDatabaseLevelToDisplay = (dbLevel) => {
      const mapping = {
        0: 0,  // Not familiar
        1: 1,  // Aware
        2: 2,  // Understanding
        3: 4,  // Applying
        4: 6   // Mastering
      }
      return mapping[dbLevel] ?? dbLevel
    }

    // Store selected roles for display (using the apiSelectedRoles variable from API)
    selectedRoles.value = apiSelectedRoles || []

    // Map backend data to component format
    competencyData.value = user_scores.map(score => {
      // Find the required score for this competency
      const maxScoreEntry = max_scores.find(ms => ms.competency_id === score.competency_id)
      const rawRequiredScore = maxScoreEntry?.max_score ?? 6

      // Handle both database level values (0,1,2,3,4) and display score values (0,1,2,4,6)
      // Some old assessments may have database levels, newer ones have display scores
      const requiredScore = (rawRequiredScore === 3) ? 4 : rawRequiredScore

      // Calculate percentage based on required level (can exceed 100%)
      // Special case: If required=0 (not required), show 100% to avoid division by zero
      const percentage = requiredScore === 0 ? 100 : Math.round((score.score / requiredScore) * 100)

      // Determine if user meets, exceeds, or is below required level
      // Special case: If required=0 (not required), always show as 'met' with neutral feedback
      let status = 'below'
      if (requiredScore === 0) {
        status = 'met' // Competency not required for this role
      } else if (score.score >= requiredScore) {
        status = score.score > requiredScore ? 'exceeded' : 'met'
      }

      let scoreText = 'Not assessed'

      // Get LLM-generated feedback from backend or fallback to basic text
      const feedback = feedbackMap[score.competency_name] || {}
      const strengths = feedback.strengths || ''

      // Only show improvement areas if below required level
      let improvements = ''
      if (status === 'below' && feedback.improvements && feedback.improvements !== 'N/A') {
        improvements = feedback.improvements
      } else if (status === 'met') {
        improvements = 'You have met your target competency level for this role.'
      } else if (status === 'exceeded') {
        improvements = 'You have exceeded your target competency level for this role. Excellent work!'
      }

      // Map Derik's levels to descriptive text
      switch (score.score) {
        case 0:
          scoreText = 'Not familiar'
          break
        case 1:
          scoreText = 'Aware'
          break
        case 2:
          scoreText = 'Understanding'
          break
        case 4:
          scoreText = 'Applying'
          break
        case 6:
          scoreText = 'Mastering'
          break
        default:
          scoreText = `Level ${score.score}`
      }

      // Map required score to descriptive text
      // Handle both database levels (3) and display scores (4) for "Applying"
      let requiredText = 'Not specified'
      switch (requiredScore) {
        case 0:
          requiredText = 'Not Required'
          break
        case 1:
          requiredText = 'Aware'
          break
        case 2:
          requiredText = 'Understanding'
          break
        case 3:  // Database level for Applying (legacy data)
        case 4:  // Display score for Applying
          requiredText = 'Applying'
          break
        case 6:
          requiredText = 'Mastering'
          break
        default:
          requiredText = `Level ${requiredScore}`
      }

      return {
        id: score.competency_id,
        name: score.competency_name,  // From database
        area: score.competency_area,   // From database
        score: score.score,
        percentage: percentage,
        scoreText: scoreText,
        requiredScore: requiredScore,
        requiredText: requiredText,
        status: status,
        strengths: strengths,
        improvements: improvements
      }
    })

    // Select all areas by default
    selectedAreas.value = [...uniqueAreas.value]

    // Generate initial chart data
    updateChartData()

  } catch (error) {
    console.error('Error fetching assessment results:', error)
    ElMessage.error('Failed to load assessment results from server')
  } finally {
    loading.value = false
  }
}

const updateChartData = () => {
  if (filteredCompetencyData.value.length === 0) {
    chartData.value = null
    return
  }

  const labels = filteredCompetencyData.value.map(comp => comp.name)
  const userData = filteredCompetencyData.value.map(comp => comp.score)

  // Get required scores from backend data (matching Derik's implementation)
  const requiredData = filteredCompetencyData.value.map(comp => {
    const maxScore = maxScores.value.find(ms => ms.competency_id === comp.id)
    // Use nullish coalescing (??) to handle 0 as a valid value
    return maxScore?.max_score ?? 6
  })

  chartData.value = {
    labels: labels,
    datasets: [
      {
        label: 'User Score',  // ✅ Match Derik's label
        backgroundColor: 'rgba(103, 194, 58, 0.2)',
        borderColor: 'rgba(103, 194, 58, 1)',
        pointBackgroundColor: 'rgba(103, 194, 58, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        data: userData
      },
      {
        label: 'Required Score',  // ✅ Match Derik's label
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        data: requiredData  // ✅ Real required scores from role matrix
      }
    ]
  }
}

const toggleAreaSelection = (area) => {
  const index = selectedAreas.value.indexOf(area)
  if (index === -1) {
    selectedAreas.value.push(area)
  } else {
    selectedAreas.value.splice(index, 1)
  }
  // Update chart data when areas are toggled
  updateChartData()
}

const getScoreType = (score) => {
  if (score >= 5) return 'success'
  if (score >= 3) return 'warning'
  return 'danger'
}

const getAreaScoreType = (score) => {
  if (score >= 70) return 'success'
  if (score >= 50) return 'warning'
  return 'danger'
}

const getProgressColor = (percentage) => {
  if (percentage >= 100) return '#67c23a'  // Green for meeting/exceeding requirements
  if (percentage >= 80) return '#95d475'   // Light green for close to meeting
  if (percentage >= 60) return '#e6a23c'   // Orange for moderate progress
  if (percentage >= 40) return '#f89c53'   // Light orange for some progress
  return '#f56c6c'                         // Red for significant gap
}

const getScoreDescription = (score) => {
  if (score >= 100) return 'Exceeding your SE role requirements'
  if (score >= 90) return 'Meeting your SE role requirements'
  if (score >= 80) return 'Very close to your SE role requirements'
  if (score >= 70) return 'Good progress towards your SE role requirements'
  if (score >= 60) return 'Moderate progress towards your SE role requirements'
  if (score >= 50) return 'Some progress towards your SE role requirements'
  return 'Significant development needed for your SE role requirements'
}

const getRoleNames = () => {
  if (!selectedRoles.value || selectedRoles.value.length === 0) return 'None selected'
  return selectedRoles.value.map(role => role.name || role.role_name || 'Unknown Role').join(', ')
}

const exportResults = async () => {
  try {
    // Show loading message
    const loadingMessage = ElMessage.info({
      message: 'Generating PDF... Please wait.',
      duration: 0
    })

    // Create PDF document (A4 size: 210mm x 297mm)
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    // PDF layout constants
    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    const margin = 20
    const maxWidth = pageWidth - (2 * margin)
    let currentY = margin

    // Helper function to add new page if needed
    const checkAddPage = (spaceNeeded) => {
      if (currentY + spaceNeeded > pageHeight - margin) {
        doc.addPage()
        currentY = margin
        return true
      }
      return false
    }

    // Helper function to wrap text
    const wrapText = (text, maxWidth) => {
      return doc.splitTextToSize(text, maxWidth)
    }

    // 1. Add Title
    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.text('SE Competency Assessment Results', pageWidth / 2, currentY, { align: 'center' })
    currentY += 12

    // 2. Add Date and Overall Score
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    const currentDate = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
    doc.text(`Assessment Date: ${currentDate}`, margin, currentY)
    currentY += 7

    doc.setFontSize(12)
    doc.setFont('helvetica', 'bold')
    doc.text(`Overall Score: ${overallScore.value.toFixed(1)}%`, margin, currentY)
    doc.setFont('helvetica', 'normal')
    doc.text(`(${getScoreDescription(overallScore.value)})`, margin + 45, currentY)
    currentY += 10

    // 3. Capture and add radar chart
    const chartElement = document.querySelector('.radar-chart canvas')
    if (chartElement && filteredCompetencyData.value.length > 0) {
      try {
        const canvas = await html2canvas(chartElement, {
          scale: 2,
          backgroundColor: '#ffffff',
          logging: false
        })

        const imgData = canvas.toDataURL('image/png')
        const imgWidth = maxWidth * 0.8
        const imgHeight = (canvas.height * imgWidth) / canvas.width

        checkAddPage(imgHeight + 15)

        doc.setFontSize(14)
        doc.setFont('helvetica', 'bold')
        doc.text('Competency Overview', margin, currentY)
        currentY += 8

        const imgX = (pageWidth - imgWidth) / 2
        doc.addImage(imgData, 'PNG', imgX, currentY, imgWidth, imgHeight)
        currentY += imgHeight + 10
      } catch (error) {
        console.warn('Could not capture radar chart:', error)
      }
    }

    // 4. Add detailed competency breakdown by area
    checkAddPage(20)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('Detailed Competency Analysis', margin, currentY)
    currentY += 10

    // Group competencies by area and process each
    for (const area of filteredAreas.value) {
      checkAddPage(30)

      // Area header
      doc.setFontSize(14)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(41, 98, 255) // Blue color
      doc.text(area.name, margin, currentY)
      doc.setTextColor(0, 0, 0) // Reset to black

      doc.setFontSize(10)
      doc.setFont('helvetica', 'italic')
      doc.text(`Average: ${area.averageScore.toFixed(1)}%`, margin + 80, currentY)
      currentY += 8

      // Draw separator line
      doc.setDrawColor(200, 200, 200)
      doc.line(margin, currentY, pageWidth - margin, currentY)
      currentY += 5

      // Process each competency in this area
      for (const competency of area.competencies) {
        checkAddPage(35)

        // Competency name
        doc.setFontSize(11)
        doc.setFont('helvetica', 'bold')
        doc.text(competency.name, margin + 5, currentY)
        currentY += 6

        // Levels info
        doc.setFontSize(9)
        doc.setFont('helvetica', 'normal')
        doc.text(`Your Level: ${competency.scoreText}`, margin + 10, currentY)
        doc.text(`Required: ${competency.requiredText}`, margin + 70, currentY)

        // Status with color
        const statusText = competency.status === 'exceeded' ? 'Exceeded' :
                          (competency.status === 'met' ? 'Met' : 'Below Target')
        const statusColor = competency.status === 'exceeded' || competency.status === 'met' ?
                           [103, 194, 58] : [230, 162, 60] // Green or Orange
        doc.setTextColor(...statusColor)
        doc.text(`Status: ${statusText}`, margin + 120, currentY)
        doc.setTextColor(0, 0, 0)
        currentY += 6

        // Progress bar
        const barWidth = 60
        const barHeight = 3
        const progressWidth = (Math.min(competency.percentage, 100) / 100) * barWidth

        // Background bar
        doc.setFillColor(240, 240, 240)
        doc.rect(margin + 10, currentY, barWidth, barHeight, 'F')

        // Progress bar
        const progressColor = competency.percentage >= 100 ? [103, 194, 58] :
                             competency.percentage >= 75 ? [64, 158, 255] :
                             competency.percentage >= 50 ? [230, 162, 60] : [245, 108, 108]
        doc.setFillColor(...progressColor)
        doc.rect(margin + 10, currentY, progressWidth, barHeight, 'F')

        doc.setFontSize(8)
        doc.text(`${competency.percentage}%`, margin + 75, currentY + 2.5)
        currentY += 7

        // Feedback sections
        if (competency.strengths) {
          checkAddPage(20)
          doc.setFontSize(9)
          doc.setFont('helvetica', 'bold')
          doc.text('Strengths:', margin + 10, currentY)
          currentY += 4

          doc.setFont('helvetica', 'normal')
          doc.setFontSize(8)
          const strengthLines = wrapText(competency.strengths, maxWidth - 15)
          strengthLines.forEach(line => {
            checkAddPage(5)
            doc.text(line, margin + 12, currentY)
            currentY += 4
          })
          currentY += 2
        }

        if (competency.improvements) {
          checkAddPage(20)
          doc.setFontSize(9)
          doc.setFont('helvetica', 'bold')
          const improvementLabel = competency.status === 'below' ?
                                  'Areas for Improvement:' : 'Status:'
          doc.text(improvementLabel, margin + 10, currentY)
          currentY += 4

          doc.setFont('helvetica', 'normal')
          doc.setFontSize(8)
          const improvementLines = wrapText(competency.improvements, maxWidth - 15)
          improvementLines.forEach(line => {
            checkAddPage(5)
            doc.text(line, margin + 12, currentY)
            currentY += 4
          })
          currentY += 2
        }

        currentY += 5 // Spacing between competencies
      }

      currentY += 5 // Spacing between areas
    }

    // Add footer with generation info
    const totalPages = doc.internal.pages.length - 1
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i)
      doc.setFontSize(8)
      doc.setTextColor(150, 150, 150)
      doc.text(
        `Generated by SE-QPT | Page ${i} of ${totalPages}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      )
    }

    // Save the PDF
    const timestamp = new Date().getTime()
    const filename = `SE_Competency_Assessment_${timestamp}.pdf`
    doc.save(filename)

    // Close loading message and show success
    loadingMessage.close()
    ElMessage.success('PDF exported successfully!')

  } catch (error) {
    console.error('Error generating PDF:', error)
    ElMessage.error('Failed to generate PDF. Please try again.')
  }
}

const proceedToNextStep = () => {
  emit('continue', {
    competencyResults: competencyData.value,
    overallScore: overallScore.value,
    recommendedRole: recommendedRole.value,
    selectedAreas: selectedAreas.value
  })
}

const goToLearningObjectives = () => {
  // Navigate to Phase 2 Task 3 Admin (Dashboard) page
  // The component automatically uses the user's organization_id
  router.push({ name: 'Phase2Task3Admin' })
}

const retakeAssessment = () => {
  console.log('[CompetencyResults] Retake button clicked, navigating to Phase 2...')

  // Navigate back to Phase 2 landing page with fresh=true query parameter
  // This tells Phase 2 to skip the auto-redirect and start a new assessment

  // IMPORTANT: Use window.location.href to force a full page reload
  // This ensures the component is completely unmounted and remounted with fresh state,
  // even if the user is already on /app/phases/2?fresh=true
  const targetUrl = '/app/phases/2?fresh=true'

  ElMessage.info('Starting new competency assessment...')

  // Force full page reload to ensure fresh component state
  window.location.href = targetUrl
}

// Lifecycle
onMounted(() => {
  processAssessmentData()
})
</script>

<style scoped>
.competency-results {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  min-height: 300px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-messages {
  margin-top: 20px;
  text-align: center;
}

.loading-message {
  font-size: 1.1rem;
  color: #409eff;
  margin-bottom: 10px;
}

/* Guidance Info Box */
.info-box {
  background: #F8F9FA;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
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

.gap-analysis-guidance-box {
  background: #FDF6EC;
  border-color: #FAECD8;
}

.gap-analysis-guidance-box .info-box-header .el-icon {
  color: #E6A23C;
}

.results-header {
  text-align: center;
  margin-bottom: 30px;
}

.results-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.results-subtitle {
  color: #6c7b7f;
  font-size: 1.1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  border-radius: 12px;
  overflow: hidden;
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 10px;
}

.summary-icon {
  margin-right: 20px;
}

.summary-content h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.summary-value {
  font-size: 1.8rem;
  font-weight: 600;
  color: #409eff;
  margin: 0;
}

.summary-desc {
  color: #6c7b7f;
  margin: 4px 0 0 0;
  font-size: 0.9rem;
}

.role-names {
  color: #606266;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-header {
  text-align: center;
}

.chart-header h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.chart-header p {
  color: #6c7b7f;
  margin: 0;
}

.area-selection {
  margin: 20px 0;
}

.area-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.area-chip {
  cursor: pointer;
  transition: all 0.3s ease;
}

.area-chip:hover {
  transform: translateY(-2px);
}

.chart-container {
  margin: 30px 0;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 400px;
  position: relative;
}

.chart-placeholder {
  text-align: center;
  color: #c0c4cc;
}

.chart-placeholder p {
  margin: 10px 0 0 0;
  font-size: 1.1rem;
}

.chart-note {
  font-size: 0.9rem !important;
  color: #909399 !important;
}

.competency-details {
  margin-bottom: 30px;
}

.area-section {
  margin-bottom: 30px;
}

.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.area-title {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.competencies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.competency-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid #409eff;
}

.competency-header {
  margin-bottom: 15px;
}

.competency-name {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.competency-levels {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 15px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.level-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.level-label {
  font-size: 0.85rem;
  color: #606266;
  font-weight: 500;
}

.level-value {
  font-size: 0.9rem;
  font-weight: 600;
}

.current-level {
  color: #409eff;
}

.required-level {
  color: #e6a23c;
}

.competency-progress {
  margin-bottom: 8px;
}

.progress-label {
  margin-top: 6px;
  font-size: 0.85rem;
  color: #606266;
  text-align: center;
}

.exceeded-note {
  color: #67c23a;
  font-weight: 600;
}

.competency-feedback {
  margin-top: 15px;
}

.feedback-section {
  margin-bottom: 10px;
}

.feedback-label {
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
  font-size: 0.9rem;
}

.feedback-text {
  color: #6c7b7f;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .competencies-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
    gap: 15px;
  }

  .area-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>