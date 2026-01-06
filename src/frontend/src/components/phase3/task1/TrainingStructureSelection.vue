<template>
  <div class="training-structure-selection">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading training structure options...</p>
    </div>

    <!-- Low Maturity: Auto-selected Competency-Level View -->
    <div v-else-if="!showViewSelector" class="auto-selected-view">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        <template #title>
          <span class="alert-title">Training Structure: Competency-Level Based</span>
        </template>
        <template #default>
          <p>
            Based on your organization's maturity level ({{ maturityLevel }}),
            training modules are organized by <strong>competency and level</strong>.
            This approach brings together all roles that need the same competency training.
          </p>
        </template>
      </el-alert>

      <div class="selected-structure-card">
        <div class="structure-icon">
          <el-icon :size="48" color="#409EFF"><Grid /></el-icon>
        </div>
        <div class="structure-info">
          <h3>Competency-Level Based Training</h3>
          <p>Training is organized by competency and level, bringing all roles together.</p>
          <div class="structure-example">
            <strong>Example:</strong> "Requirements Definition - Level 2 - Tool"
            <br>
            <span class="example-detail">Participants: Requirements Engineers, System Architects, Project Managers</span>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <el-button type="primary" @click="confirmSelection('competency_level')">
          Continue to Task 2
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- High Maturity: Show View Selection Question -->
    <div v-else class="view-selection-question">
      <div class="question-header">
        <el-icon :size="28" color="#E6A23C"><QuestionFilled /></el-icon>
        <h2>How do you want to structure your training program?</h2>
      </div>
      <p class="question-description">
        Your organization has high SE maturity (Level {{ maturityLevel }}) with defined roles.
        Choose how you want to organize the training modules:
      </p>

      <div class="view-options">
        <!-- Option 1: Competency-Level Based -->
        <div
          class="view-option-card"
          :class="{ 'selected': selectedView === 'competency_level' }"
          @click="selectedView = 'competency_level'"
        >
          <div class="option-header">
            <el-icon :size="36" color="#409EFF"><Grid /></el-icon>
            <div class="option-selection">
              <el-radio v-model="selectedView" label="competency_level" size="large">
                <span class="sr-only">Select Competency-Level Based</span>
              </el-radio>
            </div>
          </div>

          <h3>Competency-Level Based</h3>
          <p class="option-description">
            Training by competency and level - bring all roles together who need the same competency training.
          </p>

          <div class="option-details">
            <div class="detail-item">
              <strong>Best for:</strong> Efficient delivery of common competency needs
            </div>
            <div class="detail-item">
              <strong>Example:</strong> "Requirements Definition - Level 2 - Tool"
            </div>
            <div class="detail-item">
              <strong>Participants:</strong> Multiple roles in same training session
            </div>
          </div>

          <div class="option-pros">
            <el-tag type="success" size="small" effect="plain">Cost Effective</el-tag>
            <el-tag type="success" size="small" effect="plain">Cross-role Learning</el-tag>
            <el-tag type="success" size="small" effect="plain">Standardized Content</el-tag>
          </div>
        </div>

        <!-- Option 2: Role-Clustered Based -->
        <div
          class="view-option-card"
          :class="{ 'selected': selectedView === 'role_clustered' }"
          @click="selectedView = 'role_clustered'"
        >
          <div class="option-header">
            <el-icon :size="36" color="#67C23A"><UserFilled /></el-icon>
            <div class="option-selection">
              <el-radio v-model="selectedView" label="role_clustered" size="large">
                <span class="sr-only">Select Role-Clustered Based</span>
              </el-radio>
            </div>
          </div>

          <h3>Role-Clustered Based</h3>
          <p class="option-description">
            Training by role groups - organize training programs for specific role clusters with multiple competencies.
          </p>

          <div class="option-details">
            <div class="detail-item">
              <strong>Best for:</strong> Role-specific development programs
            </div>
            <div class="detail-item">
              <strong>Example:</strong> "SE for Engineers" program
            </div>
            <div class="detail-item">
              <strong>Contains:</strong> Multiple competency modules per role cluster
            </div>
          </div>

          <div class="option-pros">
            <el-tag type="success" size="small" effect="plain">Role-Tailored</el-tag>
            <el-tag type="success" size="small" effect="plain">Career Development</el-tag>
            <el-tag type="success" size="small" effect="plain">Team Cohesion</el-tag>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedView"
          :loading="saving"
          @click="confirmSelection(selectedView)"
        >
          Confirm Selection & Continue
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading, Grid, UserFilled, ArrowRight, QuestionFilled
} from '@element-plus/icons-vue'
import axios from '@/api/axios'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['completed', 'structureSelected'])

// State
const loading = ref(true)
const saving = ref(false)
const showViewSelector = ref(false)
const maturityLevel = ref(1)
const hasRoles = ref(false)
const selectedView = ref('')
const currentSelection = ref('')

// Load training structure options
const loadStructureOptions = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/phase3/training-structure/${props.organizationId}`)

    if (response.data.success) {
      showViewSelector.value = response.data.show_view_selector
      maturityLevel.value = response.data.maturity_level
      hasRoles.value = response.data.has_roles
      currentSelection.value = response.data.selected_view || 'competency_level'
      selectedView.value = currentSelection.value

      // If already completed, emit the selection
      if (response.data.task_completed) {
        emit('structureSelected', currentSelection.value)
      }
    }
  } catch (error) {
    console.error('Error loading structure options:', error)
    ElMessage.error('Failed to load training structure options')
  } finally {
    loading.value = false
  }
}

// Confirm selection and save
const confirmSelection = async (view) => {
  saving.value = true
  try {
    const response = await axios.post(`/api/phase3/training-structure/${props.organizationId}`, {
      selected_view: view
    })

    if (response.data.success) {
      ElMessage.success('Training structure selected')
      emit('structureSelected', view)
      emit('completed')
    }
  } catch (error) {
    console.error('Error saving structure selection:', error)
    ElMessage.error('Failed to save training structure selection')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadStructureOptions()
})
</script>

<style scoped>
.training-structure-selection {
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container p {
  margin-top: 16px;
}

/* Auto-selected view styles */
.auto-selected-view {
  max-width: 800px;
  margin: 0 auto;
}

.alert-title {
  font-weight: 600;
  font-size: 15px;
}

.selected-structure-card {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 24px;
  margin-top: 24px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
  border-radius: 12px;
  border: 1px solid #d4e8fc;
}

.structure-icon {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.structure-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.structure-info p {
  margin: 0 0 16px 0;
  color: #606266;
}

.structure-example {
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
}

.example-detail {
  color: #909399;
  font-size: 13px;
}

/* View selection question styles */
.view-selection-question {
  max-width: 1000px;
  margin: 0 auto;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.question-header h2 {
  margin: 0;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.question-description {
  color: #606266;
  font-size: 15px;
  margin-bottom: 32px;
  padding-left: 40px;
}

.view-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.view-option-card {
  padding: 24px;
  border: 2px solid #DCDFE6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.view-option-card:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.view-option-card.selected {
  border-color: #409EFF;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.option-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.view-option-card h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.option-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.option-details {
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  margin-bottom: 16px;
}

.detail-item {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item strong {
  color: #303133;
}

.option-pros {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .view-options {
    grid-template-columns: 1fr;
  }

  .selected-structure-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .question-description {
    padding-left: 0;
  }
}
</style>
