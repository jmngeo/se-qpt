<template>
  <el-dialog
    v-model="dialogVisible"
    title="Select Learning Format"
    width="900px"
    :close-on-click-modal="false"
    class="format-selector-dialog"
  >
    <template #header>
      <div class="dialog-header">
        <h3>Select Learning Format</h3>
        <p class="module-context">
          <strong>{{ module?.module_name }}</strong>
          <span class="context-details">
            | Target: Level {{ module?.target_level }}
            | Est. {{ module?.estimated_participants }} participants
          </span>
        </p>
      </div>
    </template>

    <!-- Loading state -->
    <div v-if="loadingFormats" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading formats...</p>
    </div>

    <div v-else class="format-selection-content">
      <!-- Format Grid -->
      <div class="formats-grid">
        <div
          v-for="format in formats"
          :key="format.id"
          class="format-card"
          :class="{
            'selected': selectedFormatId === format.id,
            'evaluating': evaluatingFormatId === format.id
          }"
          @click="selectFormat(format)"
        >
          <span class="format-icon">{{ getFormatEmoji(format.format_key) }}</span>
          <h4 class="format-name">{{ format.short_name }}</h4>

          <!-- Quick suitability preview -->
          <div v-if="formatSuitability[format.id]" class="quick-suitability">
            <span
              v-for="(factor, idx) in ['factor1', 'factor2', 'factor3']"
              :key="idx"
              class="suitability-dot"
              :class="formatSuitability[format.id]?.factors?.[factor]?.status || 'unknown'"
            ></span>
          </div>
        </div>
      </div>

      <!-- Selected Format Details -->
      <div v-if="selectedFormat && currentSuitability" class="selected-format-details">
        <el-divider>Suitability Check</el-divider>

        <div class="format-detail-card">
          <div class="format-info">
            <h4>
              <span class="format-icon-large">{{ getFormatEmoji(selectedFormat.format_key) }}</span>
              {{ selectedFormat.format_name }}
            </h4>
            <p class="format-description">{{ selectedFormat.description }}</p>

            <div class="format-specs">
              <div class="spec-item">
                <span class="spec-label">Max Level:</span>
                <span class="spec-value">{{ selectedFormat.max_level_achievable }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">Participants:</span>
                <span class="spec-value">{{ selectedFormat.participant_min }}-{{ selectedFormat.participant_max || 'unlimited' }}</span>
              </div>
            </div>

            <div class="format-characteristics">
              <el-tag size="small" effect="plain">{{ selectedFormat.mode_of_delivery }}</el-tag>
              <el-tag size="small" effect="plain">{{ selectedFormat.communication_type }}</el-tag>
              <el-tag size="small" effect="plain">{{ selectedFormat.collaboration_type }}</el-tag>
            </div>
          </div>

          <div class="suitability-details">
            <SuitabilityIndicators :suitability="currentSuitability" />
          </div>
        </div>

        <!-- Format pros/cons -->
        <div v-if="selectedFormat.advantages?.length || selectedFormat.disadvantages?.length" class="format-pros-cons">
          <div v-if="selectedFormat.advantages?.length" class="pros">
            <h5>Advantages</h5>
            <ul>
              <li v-for="adv in selectedFormat.advantages" :key="adv">{{ adv }}</li>
            </ul>
          </div>
          <div v-if="selectedFormat.disadvantages?.length" class="cons">
            <h5>Disadvantages</h5>
            <ul>
              <li v-for="dis in selectedFormat.disadvantages" :key="dis">{{ dis }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button
          type="primary"
          :disabled="!selectedFormatId"
          :loading="saving"
          @click="confirmSelection"
        >
          Confirm Selection
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import axios from '@/api/axios'
import SuitabilityIndicators from './SuitabilityIndicators.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  module: {
    type: Object,
    default: () => ({})
  },
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'selected'])

// Dialog visibility
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// State
const loadingFormats = ref(false)
const formats = ref([])
const selectedFormatId = ref(null)
const evaluatingFormatId = ref(null)
const formatSuitability = ref({})
const currentSuitability = ref(null)
const saving = ref(false)

// Selected format object
const selectedFormat = computed(() => {
  return formats.value.find(f => f.id === selectedFormatId.value)
})

// Format emoji mapping (using hex codes stored in DB)
const formatEmojis = {
  seminar: '🎓',
  webinar: '💻',
  coaching: '🎯',
  mentoring: '🤝',
  wbt: '🌐',
  cbt: '💾',
  game_based: '🎮',
  conference: '🎪',
  blended: '🔄',
  self_learning: '📚'
}

const getFormatEmoji = (formatKey) => {
  return formatEmojis[formatKey] || '📖'
}

// Load formats when dialog opens
watch(dialogVisible, async (visible) => {
  if (visible) {
    selectedFormatId.value = props.module?.selected_format_id || null
    currentSuitability.value = null
    await loadFormats()

    // If module already has a format, load its suitability
    if (selectedFormatId.value) {
      await evaluateFormat(selectedFormatId.value)
    }
  }
})

const loadFormats = async () => {
  loadingFormats.value = true
  try {
    const response = await axios.get('/api/phase3/learning-formats')
    if (response.data.success) {
      formats.value = response.data.formats

      // Pre-evaluate all formats for quick preview
      await evaluateAllFormats()
    }
  } catch (error) {
    console.error('Error loading formats:', error)
    ElMessage.error('Failed to load learning formats')
  } finally {
    loadingFormats.value = false
  }
}

const evaluateAllFormats = async () => {
  // Evaluate each format in parallel for quick preview
  const promises = formats.value.map(async (format) => {
    try {
      const response = await axios.post('/api/phase3/evaluate-format', {
        organization_id: props.organizationId,
        competency_id: props.module.competency_id,
        target_level: props.module.target_level,
        format_id: format.id,
        participant_count: props.module.estimated_participants || 0
      })

      if (response.data.success) {
        formatSuitability.value[format.id] = response.data
      }
    } catch (error) {
      console.error(`Error evaluating format ${format.id}:`, error)
    }
  })

  await Promise.all(promises)
}

const selectFormat = async (format) => {
  selectedFormatId.value = format.id
  await evaluateFormat(format.id)
}

const evaluateFormat = async (formatId) => {
  evaluatingFormatId.value = formatId
  try {
    // Use cached result if available
    if (formatSuitability.value[formatId]) {
      currentSuitability.value = formatSuitability.value[formatId]
      return
    }

    const response = await axios.post('/api/phase3/evaluate-format', {
      organization_id: props.organizationId,
      competency_id: props.module.competency_id,
      target_level: props.module.target_level,
      format_id: formatId,
      participant_count: props.module.estimated_participants || 0
    })

    if (response.data.success) {
      currentSuitability.value = response.data
      formatSuitability.value[formatId] = response.data
    }
  } catch (error) {
    console.error('Error evaluating format:', error)
  } finally {
    evaluatingFormatId.value = null
  }
}

const confirmSelection = async () => {
  if (!selectedFormatId.value) return

  saving.value = true
  try {
    const response = await axios.post('/api/phase3/select-format', {
      organization_id: props.organizationId,
      competency_id: props.module.competency_id,
      target_level: props.module.target_level,
      pmt_type: props.module.pmt_type,
      format_id: selectedFormatId.value,
      estimated_participants: props.module.estimated_participants,
      confirmed: true,
      cluster_id: props.module.cluster_id || null  // For role_clustered view
    })

    if (response.data.success) {
      ElMessage.success('Format selected successfully')
      emit('selected', {
        formatId: selectedFormatId.value,
        format: selectedFormat.value,
        suitability: currentSuitability.value
      })
      dialogVisible.value = false
    }
  } catch (error) {
    console.error('Error saving format selection:', error)
    ElMessage.error('Failed to save format selection')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.format-selector-dialog :deep(.el-dialog__header) {
  padding-bottom: 10px;
  border-bottom: 1px solid #EBEEF5;
}

.dialog-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.module-context {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.context-details {
  color: #909399;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.format-selection-content {
  max-height: 60vh;
  overflow-y: auto;
}

/* Format Grid */
.formats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.format-card {
  padding: 16px 12px;
  border: 2px solid #EBEEF5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.format-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.format-card.selected {
  border-color: #409EFF;
  background: #ECF5FF;
}

.format-card.evaluating {
  opacity: 0.7;
}

.format-icon {
  font-size: 28px;
}

.format-name {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.quick-suitability {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.suitability-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #C0C4CC;
}

.suitability-dot.green {
  background: #67C23A;
}

.suitability-dot.yellow {
  background: #E6A23C;
}

.suitability-dot.red {
  background: #F56C6C;
}

/* Selected Format Details */
.selected-format-details {
  padding-top: 16px;
}

.format-detail-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
}

.format-info h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.format-icon-large {
  font-size: 24px;
}

.format-description {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.format-specs {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: white;
  border-radius: 6px;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.spec-label {
  font-size: 12px;
  color: #909399;
}

.spec-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.format-characteristics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.format-characteristics .el-tag {
  text-transform: capitalize;
}

/* Pros/Cons */
.format-pros-cons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 16px;
}

.format-pros-cons h5 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #303133;
}

.format-pros-cons ul {
  margin: 0;
  padding-left: 18px;
}

.format-pros-cons li {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.pros h5 {
  color: #67C23A;
}

.cons h5 {
  color: #F56C6C;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Responsive */
@media (max-width: 900px) {
  .formats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .format-detail-card {
    grid-template-columns: 1fr;
  }

  .format-pros-cons {
    grid-template-columns: 1fr;
  }
}
</style>
