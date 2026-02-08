<template>
  <el-card class="derik-task-selector">
    <template #header>
      <div class="card-header">
        <h2 class="section-title">Task-Based Assessment</h2>
        <p class="section-description">Describe your tasks and responsibilities to automatically map to SE roles</p>
      </div>
    </template>

    <!-- Guidance Info Box -->
    <div class="info-box task-assessment-guidance-box">
      <div class="info-box-header">
        <el-icon><InfoFilled /></el-icon>
        <h4>About Task-Based Assessment</h4>
      </div>
      <ul class="info-points">
        <li>
          In this step, you describe your <strong>daily tasks and responsibilities</strong> across three categories.
          An AI model analyzes your descriptions and maps them to <strong>ISO 15288 systems engineering processes</strong>,
          determining which SE processes you are involved in and at what level of involvement (Responsible, Supporting, or Designing).
        </li>
        <li>
          <strong>Why this matters:</strong> The identified processes determine which of the 16 SE competencies you need
          to be assessed on. Detailed, specific task descriptions lead to more accurate competency identification
          and a more meaningful assessment.
        </li>
        <li>
          After the analysis, you can <strong>review and edit</strong> the identified processes before proceeding
          to the competency self-assessment survey.
        </li>
        <li class="note">
          Data flow: Your task descriptions (this step) &rarr; AI-identified ISO processes &rarr;
          Competency requirements (next step) &rarr; Self-assessment survey.
        </li>
      </ul>
    </div>

    <div class="task-form">
      <!-- Tasks Responsible For -->
      <div class="form-group">
        <label class="form-label">Tasks you are responsible for</label>
        <el-input
          v-model="tasksResponsibleFor"
          type="textarea"
          :rows="6"
          placeholder="Describe the primary tasks for which you are responsible..."
          class="task-input"
        />
      </div>

      <!-- Tasks You Support -->
      <div class="form-group">
        <label class="form-label">Tasks that you support</label>
        <el-input
          v-model="tasksYouSupport"
          type="textarea"
          :rows="6"
          placeholder="Describe tasks you provide support for..."
          class="task-input"
        />
      </div>

      <!-- Tasks You Define and Improve -->
      <div class="form-group">
        <label class="form-label">Tasks and processes that you define or design</label>
        <el-input
          v-model="tasksDefineAndImprove"
          type="textarea"
          :rows="6"
          placeholder="Describe tasks and processes you are involved in defining or designing..."
          class="task-input"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <el-loading
        element-loading-text="Analyzing your tasks and responsibilities..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      />
      <div class="progress-messages">
        <p class="loading-message">{{ loadingMessage }}</p>
        <el-progress
          :percentage="progressPercentage"
          :stroke-width="8"
          color="#67c23a"
        />
      </div>
    </div>

    <!-- Results Display -->
    <div v-if="!isLoading && processResult.length > 0" class="results-section">
      <div class="results-header">
        <h3 class="results-title">Identified ISO Processes</h3>
        <div class="results-actions">
          <el-button
            v-if="!isEditing"
            type="primary"
            plain
            size="small"
            @click="enterEditMode"
          >
            <el-icon><Edit /></el-icon>
            Edit Selection
          </el-button>
          <el-button
            v-if="isEditing"
            type="warning"
            plain
            size="small"
            @click="reAnalyzeTasks"
          >
            <el-icon><Refresh /></el-icon>
            Re-analyze Tasks
          </el-button>
        </div>
      </div>

      <!-- Editable Process Grid -->
      <div class="processes-grid">
        <div
          v-for="(process, index) in displayedProcesses"
          :key="process.process_name"
          class="process-card"
          :class="{
            'process-card-disabled': isEditing && !process.selected,
            'process-card-modified': process.modified
          }"
        >
          <div class="process-header">
            <!-- Selection checkbox (only in edit mode) -->
            <el-checkbox
              v-if="isEditing"
              v-model="process.selected"
              @change="markModified(index)"
              class="process-checkbox"
            />
            <h4 class="process-name">{{ process.process_name }}</h4>

            <!-- Involvement dropdown (edit mode) OR tag (view mode) -->
            <el-select
              v-if="isEditing && process.selected"
              v-model="process.involvement"
              size="small"
              class="involvement-select"
              @change="markModified(index)"
            >
              <el-option
                v-for="opt in involvementOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <el-tag
              v-else
              :type="getInvolvementType(process.involvement)"
              size="small"
            >
              {{ process.involvement }}
            </el-tag>
          </div>
          <p class="process-description" v-if="process.description">
            {{ process.description }}
          </p>
        </div>
      </div>

      <!-- Add More Processes (Edit Mode only) -->
      <div v-if="isEditing" class="add-more-section">
        <el-collapse>
          <el-collapse-item title="Add More Processes" name="addMore">
            <div class="add-processes-search">
              <el-input
                v-model="searchQuery"
                placeholder="Search ISO processes..."
                :prefix-icon="Search"
                clearable
              />
            </div>
            <div v-if="availableProcesses.length > 0" class="available-processes-grid">
              <div
                v-for="isoProcess in availableProcesses"
                :key="isoProcess.id"
                class="available-process-item"
                @click="addProcess(isoProcess)"
              >
                <span class="process-name-small">{{ isoProcess.name }}</span>
                <el-icon class="add-icon"><Plus /></el-icon>
              </div>
            </div>
            <div v-else class="no-processes-message">
              <p v-if="searchQuery">No processes match your search.</p>
              <p v-else>All processes have been added.</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- Edit Mode Actions -->
      <div v-if="isEditing" class="edit-actions">
        <el-button @click="cancelEdit">Cancel</el-button>
        <el-button
          type="primary"
          :loading="isConfirming"
          :disabled="!hasModifications"
          @click="confirmSelection"
        >
          Confirm Selection ({{ selectedCount }} processes)
        </el-button>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions">
      <el-button
        v-if="!isLoading && processResult.length === 0"
        type="primary"
        size="large"
        @click="analyzeTasksAndProceed"
        :disabled="!hasValidInput"
      >
        Analyze Tasks & Proceed
      </el-button>

      <el-button
        v-if="!isLoading && processResult.length > 0"
        type="success"
        size="large"
        @click="proceedToAssessment"
      >
        Proceed to Competency Assessment
      </el-button>
    </div>

    <!-- Validation Dialog -->
    <el-dialog
      v-model="showValidationDialog"
      title="Validation Error"
      width="30%"
    >
      <p>{{ validationMessage }}</p>
      <template #footer>
        <el-button type="primary" @click="showValidationDialog = false">
          OK
        </el-button>
      </template>
    </el-dialog>

    <!-- Error Dialog -->
    <el-dialog
      v-model="showErrorDialog"
      title="Error"
      width="30%"
    >
      <p>{{ errorMessage }}</p>
      <template #footer>
        <el-button type="primary" @click="showErrorDialog = false">
          OK
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Refresh, Plus, Search, InfoFilled, Aim, Document as DocumentIcon } from '@element-plus/icons-vue'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  },
  username: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['tasksAnalyzed'])

// State
const tasksResponsibleFor = ref('')
const tasksYouSupport = ref('')
const tasksDefineAndImprove = ref('')
const isLoading = ref(false)
const loadingMessage = ref('')
const progressPercentage = ref(0)
const processResult = ref([])
const showValidationDialog = ref(false)
const showErrorDialog = ref(false)
const validationMessage = ref('')
const errorMessage = ref('')

// === Process Selection State (Edit Mode) ===
const editableProcesses = ref([])           // Working copy for editing
const isEditing = ref(false)                // Toggle edit mode
const allIsoProcesses = ref([])             // Full list of 30 processes
const searchQuery = ref('')                 // Search filter for add dialog
const isConfirming = ref(false)             // Loading state during confirm
const hasModifications = ref(false)         // Track if user made changes

// Involvement level options
const involvementOptions = [
  { value: 'Responsible', label: 'Responsible', numericValue: 2 },
  { value: 'Supporting', label: 'Supporting', numericValue: 1 },
  { value: 'Designing', label: 'Designing', numericValue: 4 }
]

// Computed
const hasValidInput = computed(() => {
  return tasksResponsibleFor.value.trim() ||
         tasksYouSupport.value.trim() ||
         tasksDefineAndImprove.value.trim()
})

const filteredProcessResult = computed(() => {
  return processResult.value.filter(process =>
    process.involvement !== "Not performing"
  )
})

// === Process Selection Computed Properties ===
const displayedProcesses = computed(() => {
  if (isEditing.value) {
    return editableProcesses.value
  }
  return filteredProcessResult.value.map(p => ({ ...p, selected: true }))
})

const availableProcesses = computed(() => {
  // Normalize process names by removing " process" suffix for comparison
  const normalizeProcessName = (name) => {
    let normalized = name.toLowerCase().trim()
    if (normalized.endsWith(' process')) {
      normalized = normalized.slice(0, -8)  // Remove " process" suffix
    }
    return normalized
  }

  const selectedNames = new Set(
    editableProcesses.value
      .filter(p => p.selected)
      .map(p => normalizeProcessName(p.process_name))
  )

  let available = allIsoProcesses.value.filter(
    p => !selectedNames.has(normalizeProcessName(p.name))
  )

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    available = available.filter(p =>
      p.name.toLowerCase().includes(query) ||
      (p.description && p.description.toLowerCase().includes(query))
    )
  }

  return available
})

const selectedCount = computed(() => {
  return editableProcesses.value.filter(p => p.selected).length
})

// Methods
const setDefaultValues = () => {
  if (!tasksResponsibleFor.value.trim()) {
    tasksResponsibleFor.value = 'Not responsible for any tasks'
  }
  if (!tasksYouSupport.value.trim()) {
    tasksYouSupport.value = 'Not supporting any tasks'
  }
  if (!tasksDefineAndImprove.value.trim()) {
    tasksDefineAndImprove.value = 'Not designing any tasks'
  }
}

const validateInput = () => {
  setDefaultValues()
  const allDefaults = [
    tasksResponsibleFor.value.trim(),
    tasksYouSupport.value.trim(),
    tasksDefineAndImprove.value.trim()
  ].every(task =>
    task === 'Not responsible for any tasks' ||
    task === 'Not supporting any tasks' ||
    task === 'Not designing any tasks'
  )

  if (allDefaults) {
    validationMessage.value = 'Please provide at least one valid task description.'
    showValidationDialog.value = true
    return false
  }

  return true
}

const simulateProgress = () => {
  const messages = [
    'Analyzing your tasks and responsibilities...',
    'Understanding your involvement in different ISO processes...',
    'Leveraging our AI model to map your tasks to ISO standards...',
    'Finalizing the ISO processes you are performing...'
  ]

  let index = 0
  let progress = 0
  loadingMessage.value = messages[index]
  progressPercentage.value = 25

  const interval = setInterval(() => {
    index++
    progress += 25

    if (index < messages.length) {
      loadingMessage.value = messages[index]
      progressPercentage.value = progress
    } else {
      clearInterval(interval)
      progressPercentage.value = 100
    }
  }, 2000) // Update every 2 seconds
}

const analyzeTasksAndProceed = async () => {
  if (!validateInput()) return

  errorMessage.value = ''

  // Create combined task description for analysis
  const taskDescription = [
    tasksResponsibleFor.value,
    tasksYouSupport.value,
    tasksDefineAndImprove.value
  ].filter(task =>
    task &&
    task !== 'Not responsible for any tasks' &&
    task !== 'Not supporting any tasks' &&
    task !== 'Not designing any tasks'
  ).join('\n\n')

  try {
    isLoading.value = true
    simulateProgress()

    console.log('[DerikTaskSelector] Calling /api/findProcesses with username:', props.username)

    // Call the /findProcesses endpoint (stores data in DB and populates competency matrix)
    const response = await fetch('/api/findProcesses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: props.username,
        organizationId: props.organizationId,
        tasks: {
          responsible_for: tasksResponsibleFor.value.split('\n').filter(t => t.trim()),
          supporting: tasksYouSupport.value.split('\n').filter(t => t.trim()),
          designing: tasksDefineAndImprove.value.split('\n').filter(t => t.trim())
        }
      })
    })

    if (response.ok) {
      const data = await response.json()
      // The response format from /findProcesses is: {status: "success", processes: [{process_name, involvement}, ...]}
      processResult.value = data.processes || []
      console.log('Identified processes:', processResult.value)
      console.log('Full API response:', data)
    } else {
      throw new Error('Failed to identify processes')
    }
  } catch (error) {
    console.error('Failed to analyze tasks:', error)
    errorMessage.value = 'Failed to analyze your tasks. Please refine your task descriptions and try again.'
    showErrorDialog.value = true
  } finally {
    isLoading.value = false
    progressPercentage.value = 0
  }
}

const getInvolvementType = (involvement) => {
  switch (involvement) {
    case 'Leading': return 'danger'
    case 'Contributing': return 'warning'
    case 'Supporting': return 'info'
    default: return 'success'
  }
}

const proceedToAssessment = () => {
  if (filteredProcessResult.value.length === 0) {
    ElMessage({
      type: 'warning',
      message: 'No processes identified with your current tasks. This will result in 0 required competencies. Please refine your task descriptions and click "Analyze Tasks" again to get better results.',
      duration: 6000,
      showClose: true
    })
    // Don't return - allow user to see "0 competencies" result and go back to edit
  }

  emit('tasksAnalyzed', {
    type: 'task-based',
    tasks: {
      responsible_for: tasksResponsibleFor.value,
      supporting: tasksYouSupport.value,
      designing: tasksDefineAndImprove.value
    },
    processes: filteredProcessResult.value
  })
}

// === Process Selection Methods (Edit Mode) ===

/**
 * Enter edit mode - create working copy of processes
 */
const enterEditMode = () => {
  // Deep copy processResult to editableProcesses
  editableProcesses.value = processResult.value
    .filter(p => p.involvement !== 'Not performing')
    .map(p => ({
      ...p,
      selected: true,
      modified: false,
      original_involvement: p.involvement
    }))
  isEditing.value = true
  hasModifications.value = false

  // Fetch all ISO processes for "Add More" section
  fetchAllIsoProcesses()
}

/**
 * Fetch all 30 ISO processes from database
 */
const fetchAllIsoProcesses = async () => {
  try {
    const response = await fetch('/api/iso-processes')
    if (response.ok) {
      const data = await response.json()
      allIsoProcesses.value = data.processes
      console.log('[DerikTaskSelector] Fetched', data.total, 'ISO processes')
    }
  } catch (error) {
    console.error('[DerikTaskSelector] Failed to fetch ISO processes:', error)
  }
}

/**
 * Mark process as modified (for visual feedback)
 */
const markModified = (index) => {
  editableProcesses.value[index].modified = true
  hasModifications.value = true
}

/**
 * Add a process from the "Add More" list
 */
const addProcess = (isoProcess) => {
  editableProcesses.value.push({
    process_name: isoProcess.name,
    involvement: 'Supporting', // Default to Supporting
    description: isoProcess.description,
    selected: true,
    modified: true,
    iso_process_id: isoProcess.id
  })
  hasModifications.value = true
  ElMessage.success(`Added: ${isoProcess.name}`)
}

/**
 * Cancel edit mode - discard changes
 */
const cancelEdit = () => {
  editableProcesses.value = []
  isEditing.value = false
  hasModifications.value = false
  searchQuery.value = ''
}

/**
 * Re-analyze tasks with original LLM
 */
const reAnalyzeTasks = async () => {
  cancelEdit()
  processResult.value = []
  await analyzeTasksAndProceed()
}

/**
 * Confirm selection - call backend to update
 */
const confirmSelection = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('Please select at least one process to proceed.')
    return
  }

  try {
    isConfirming.value = true

    // Prepare updated processes for backend
    const updatedProcesses = editableProcesses.value
      .filter(p => p.selected)
      .map(p => ({
        process_name: p.process_name,
        involvement: p.involvement
      }))

    console.log('[DerikTaskSelector] Confirming selection:', updatedProcesses)

    // Call backend endpoint
    const response = await fetch('/api/updateProcessSelection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: props.username,
        organizationId: props.organizationId,
        processes: updatedProcesses
      })
    })

    if (response.ok) {
      const data = await response.json()

      // Update local state with confirmed selection
      processResult.value = data.processes

      ElMessage.success('Process selection updated successfully')

      // Exit edit mode
      isEditing.value = false
      hasModifications.value = false
      editableProcesses.value = []
      searchQuery.value = ''
    } else {
      throw new Error('Failed to update process selection')
    }
  } catch (error) {
    console.error('[DerikTaskSelector] Failed to confirm selection:', error)
    ElMessage.error('Failed to update selection. Please try again.')
  } finally {
    isConfirming.value = false
  }
}
</script>

<style scoped>
.derik-task-selector {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  text-align: left;
}

.card-header .section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.card-header .section-description {
  color: #606266;
  font-size: 14px;
  margin: 0;
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

.task-assessment-guidance-box {
  background: #ECF5FF;
  border-color: #D9ECFF;
}

.task-assessment-guidance-box .info-box-header .el-icon {
  color: #409EFF;
}

.task-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1rem;
}

.task-input {
  width: 100%;
}

/* Custom scrollbar styling for textareas */
.task-input :deep(textarea) {
  scrollbar-width: thin;
  scrollbar-color: #409eff #f5f7fa;
}

.task-input :deep(textarea::-webkit-scrollbar) {
  width: 8px;
}

.task-input :deep(textarea::-webkit-scrollbar-track) {
  background: #f5f7fa;
  border-radius: 4px;
}

.task-input :deep(textarea::-webkit-scrollbar-thumb) {
  background: #409eff;
  border-radius: 4px;
}

.task-input :deep(textarea::-webkit-scrollbar-thumb:hover) {
  background: #337ecc;
}

.loading-container {
  min-height: 200px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 40px 0;
}

.progress-messages {
  margin-top: 20px;
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.loading-message {
  font-size: 1.1rem;
  color: #409eff;
  margin-bottom: 15px;
  font-weight: 500;
}

.results-section {
  margin-bottom: 30px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #67c23a;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 8px;
}

.processes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.process-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  border-left: 4px solid #67c23a;
}

.process-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.process-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
  margin: 0;
  flex: 1;
  margin-right: 12px;
}

.process-description {
  color: #6c7b7f;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

.role-card {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border: 2px dashed #409eff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.role-card:hover {
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  transform: translateY(-2px);
}

.role-card-title {
  font-weight: 600;
  font-size: 1.2rem;
  color: #409eff;
  margin-bottom: 8px;
}

.role-card-text {
  color: #5c6b75;
  line-height: 1.6;
}

.actions {
  text-align: center;
}

/* === Process Selection Edit Mode Styles === */

.process-checkbox {
  margin-right: 12px;
}

.involvement-select {
  width: 130px;
  flex-shrink: 0;
}

.process-card-disabled {
  opacity: 0.5;
  border-left-color: #dcdfe6 !important;
}

.process-card-modified {
  border-left-color: #e6a23c !important;
  background: linear-gradient(to right, rgba(230, 162, 60, 0.05), transparent);
}

.add-more-section {
  margin-top: 24px;
  border: 1px dashed #67c23a;
  border-radius: 8px;
  overflow: hidden;
}

.add-more-section :deep(.el-collapse-item__header) {
  padding: 12px 16px;
  font-weight: 600;
  color: #67c23a;
  background: rgba(103, 194, 58, 0.05);
}

.add-more-section :deep(.el-collapse-item__content) {
  padding: 16px;
}

.add-processes-search {
  margin-bottom: 16px;
}

.available-processes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.available-process-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.available-process-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
}

.process-name-small {
  font-size: 0.9rem;
  color: #606266;
}

.add-icon {
  color: #67c23a;
  font-size: 16px;
}

.no-processes-message {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.no-processes-message p {
  margin: 0;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>