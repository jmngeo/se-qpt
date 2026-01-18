<template>
  <el-dialog
    v-model="dialogVisible"
    title="Select Learning Format"
    width="1100px"
    :close-on-click-modal="false"
    class="format-selector-dialog"
  >
    <template #header>
      <div class="dialog-header">
        <div class="header-title">
          <el-icon class="header-icon"><Collection /></el-icon>
          <h3>Select Learning Format</h3>
        </div>
        <div class="module-info-card">
          <div class="module-name">{{ module?.module_name }}</div>
          <div class="module-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ module?.estimated_participants }} participants
            </span>
          </div>
        </div>
      </div>
    </template>

    <!-- Loading state -->
    <div v-if="loadingFormats" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>Loading learning formats...</p>
    </div>

    <div v-else class="format-selection-content">
      <!-- Format Grid -->
      <div class="formats-section">
        <div class="section-label">Choose a format:</div>
        <div class="formats-grid">
          <div
            v-for="format in formats"
            :key="format.id"
            class="format-card"
            :class="{
              'selected': selectedFormatId === format.id,
              'evaluating': evaluatingFormatId === format.id,
              'has-suitability': formatSuitability[format.id]
            }"
            @click="selectFormat(format)"
          >
            <div class="format-icon-wrapper">
              <span class="format-icon">{{ getFormatEmoji(format.format_key) }}</span>
            </div>
            <h4 class="format-name">{{ format.short_name }}</h4>

            <!-- Quick suitability preview -->
            <div v-if="formatSuitability[format.id]" class="quick-suitability">
              <span
                v-for="(factor, idx) in ['factor1', 'factor2', 'factor3']"
                :key="idx"
                class="suitability-dot"
                :class="formatSuitability[format.id]?.factors?.[factor]?.status || 'unknown'"
                :title="getSuitabilityLabel(formatSuitability[format.id]?.factors?.[factor]?.status)"
              ></span>
            </div>
            <div v-else class="loading-dots">
              <span></span><span></span><span></span>
            </div>

            <!-- Selected checkmark -->
            <div v-if="selectedFormatId === format.id" class="selected-badge">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Format Details -->
      <div v-if="selectedFormat" class="selected-format-details">
        <div class="details-header">
          <span class="format-icon-large">{{ getFormatEmoji(selectedFormat.format_key) }}</span>
          <div class="details-title">
            <h4>{{ selectedFormat.format_name }}</h4>
            <p class="format-description">{{ selectedFormat.description }}</p>
            <p v-if="getSeSuitability(selectedFormat.format_key)" class="se-relevance">
              <span class="se-label">SE Relevance:</span>
              {{ getSeSuitability(selectedFormat.format_key) }}
            </p>
          </div>
        </div>

        <div class="details-content">
          <!-- Format Specs -->
          <div class="specs-card">
            <div class="spec-row">
              <div class="spec-item">
                <el-icon><Aim /></el-icon>
                <div class="spec-text">
                  <span class="spec-label">Max Achievable Level</span>
                  <span class="spec-value">{{ getLevelName(selectedFormat.max_level_achievable) }}</span>
                </div>
              </div>
              <div class="spec-item">
                <el-icon><User /></el-icon>
                <div class="spec-text">
                  <span class="spec-label">Participant Range</span>
                  <span class="spec-value">{{ selectedFormat.participant_min }} - {{ selectedFormat.participant_max || 'Unlimited' }}</span>
                </div>
              </div>
            </div>
            <div class="characteristics-row">
              <el-tag size="small" type="info" effect="plain">{{ selectedFormat.mode_of_delivery }}</el-tag>
              <el-tag size="small" type="info" effect="plain">{{ selectedFormat.communication_type }}</el-tag>
              <el-tag size="small" type="info" effect="plain">{{ selectedFormat.collaboration_type }}</el-tag>
            </div>
          </div>

          <!-- Suitability Check -->
          <div v-if="currentSuitability" class="suitability-card">
            <div class="suitability-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>Suitability Analysis</span>
            </div>
            <SuitabilityIndicators :suitability="currentSuitability" />
          </div>
        </div>

        <!-- Format pros/cons -->
        <div v-if="selectedFormat.advantages?.length || selectedFormat.disadvantages?.length" class="pros-cons-section">
          <div v-if="selectedFormat.advantages?.length" class="pros-card">
            <div class="card-header pros-header">
              <el-icon><CircleCheck /></el-icon>
              <span>Advantages</span>
            </div>
            <ul>
              <li v-for="adv in selectedFormat.advantages" :key="adv">{{ adv }}</li>
            </ul>
          </div>
          <div v-if="selectedFormat.disadvantages?.length" class="cons-card">
            <div class="card-header cons-header">
              <el-icon><Warning /></el-icon>
              <span>Considerations</span>
            </div>
            <ul>
              <li v-for="dis in selectedFormat.disadvantages" :key="dis">{{ dis }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- No selection prompt -->
      <div v-else class="no-selection-prompt">
        <el-icon :size="48"><Pointer /></el-icon>
        <p>Select a learning format above to see details and suitability analysis</p>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false" size="large">Cancel</el-button>
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedFormatId"
          :loading="saving"
          @click="confirmSelection"
        >
          <el-icon><Check /></el-icon>
          Confirm Selection
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading, Check, User, Collection, Aim, DataAnalysis,
  CircleCheck, Warning, Pointer
} from '@element-plus/icons-vue'
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

// SE Suitability Descriptions from Sachin Kumar's thesis
// Source: "Identifying suitable learning formats for Systems Engineering" (2023)
const seSuitabilityDescriptions = {
  seminar: 'Highly suitable for building commitment and transdisciplinary collaboration in SE teams. Best for awareness-centered approaches focusing on interdisciplinary exchange.',
  webinar: 'Balanced format for general SE education with moderate effectiveness across all characteristics. Good for reaching distributed teams when in-person training is not feasible.',
  coaching: 'Excellent for mindset change and building individual commitment to SE. Ideal for supporting the transition from component-oriented to systems-oriented thinking.',
  mentoring: 'Excellent for mindset transformation and commitment building through experienced guidance. Best for developing future SE leaders and ensuring knowledge transfer.',
  wbt: 'Excellent for delivering comprehensive, holistic SE knowledge and stakeholder-specific content. Best combined with interactive formats to build commitment.',
  cbt: 'Best suited for delivering stakeholder-specific SE content at individual pace. Not recommended for mindset change or building team commitment.',
  game_based: 'Highly effective for transdisciplinary team building and SE awareness. Ideal as a starting point for SE introduction in interdisciplinary teams with low entry barriers.',
  conference: 'Useful for exposure to new SE ideas and networking. Limited effectiveness for deep SE characteristic development due to restricted interaction time.',
  blended: 'The most comprehensive and effective format for SE qualification. Recommended as the primary approach for developing all SE characteristics through combined online and in-person methods.',
  self_learning: 'Effective for individual study of holistic SE knowledge. Should be combined with interactive formats to develop commitment and transdisciplinary skills.'
}

const getSeSuitability = (formatKey) => {
  return seSuitabilityDescriptions[formatKey] || null
}

// Level name mapping
const getLevelName = (level) => {
  const names = {
    1: 'Knowing',
    2: 'Understanding',
    4: 'Applying',
    6: 'Mastering'
  }
  return names[level] || `Level ${level}`
}

// Suitability label mapping
const getSuitabilityLabel = (status) => {
  const labels = {
    green: 'Good fit',
    yellow: 'Acceptable',
    red: 'Not recommended'
  }
  return labels[status] || 'Evaluating...'
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
  padding: 20px 24px 16px;
  border-bottom: 1px solid #EBEEF5;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F7 100%);
}

.format-selector-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.format-selector-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid #EBEEF5;
  background: #FAFAFA;
}

/* Header */
.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 24px;
  color: #409EFF;
}

.header-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.module-info-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: white;
  border-radius: 8px;
  border: 1px solid #E4E7ED;
}

.module-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.module-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.meta-item .el-icon {
  color: #909399;
}

/* Loading */
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
  font-size: 14px;
}

/* Content */
.format-selection-content {
  max-height: 58vh;
  overflow-y: auto;
}

/* Format Section */
.formats-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
}

/* Format Grid */
.formats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.format-card {
  position: relative;
  padding: 16px 10px 12px;
  border: 2px solid #E4E7ED;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.format-card:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.format-card.selected {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ECF5FF 0%, #E8F4FF 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.format-card.evaluating {
  opacity: 0.6;
}

.format-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F7FA;
  border-radius: 12px;
  margin-bottom: 4px;
}

.format-card.selected .format-icon-wrapper {
  background: white;
}

.format-icon {
  font-size: 26px;
}

.format-name {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  line-height: 1.3;
}

.quick-suitability {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-top: 4px;
}

.suitability-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #DCDFE6;
  transition: all 0.2s;
}

.suitability-dot.green { background: #67C23A; }
.suitability-dot.yellow { background: #E6A23C; }
.suitability-dot.red { background: #F56C6C; }

.loading-dots {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #DCDFE6;
  animation: pulse 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

.selected-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.4);
}

/* Selected Format Details */
.selected-format-details {
  background: #F8FAFC;
  border: 1px solid #E4E7ED;
  border-radius: 12px;
  padding: 20px;
}

.details-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #EBEEF5;
  margin-bottom: 16px;
}

.format-icon-large {
  font-size: 40px;
  background: white;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.details-title h4 {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.format-description {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.se-relevance {
  margin: 8px 0 0 0;
  padding: 8px 12px;
  font-size: 12px;
  color: #303133;
  line-height: 1.5;
  background: linear-gradient(135deg, #E8F4FD 0%, #F0F7FF 100%);
  border-left: 3px solid #409EFF;
  border-radius: 0 6px 6px 0;
}

.se-label {
  font-weight: 600;
  color: #409EFF;
  margin-right: 4px;
}

.details-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Specs Card */
.specs-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #EBEEF5;
}

.spec-row {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.spec-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex: 1;
}

.spec-item > .el-icon {
  font-size: 18px;
  color: #409EFF;
  margin-top: 2px;
}

.spec-text {
  display: flex;
  flex-direction: column;
}

.spec-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}

.spec-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.characteristics-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid #EBEEF5;
}

.characteristics-row .el-tag {
  text-transform: capitalize;
}

/* Suitability Card */
.suitability-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #EBEEF5;
}

.suitability-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.suitability-header .el-icon {
  color: #409EFF;
}

/* Pros/Cons */
.pros-cons-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
}

.pros-card, .cons-card {
  background: white;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #EBEEF5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.pros-header {
  color: #67C23A;
}

.cons-header {
  color: #E6A23C;
}

.pros-card ul, .cons-card ul {
  margin: 0;
  padding-left: 18px;
}

.pros-card li, .cons-card li {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
}

/* No Selection */
.no-selection-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #C0C4CC;
  text-align: center;
}

.no-selection-prompt p {
  margin-top: 12px;
  font-size: 14px;
  color: #909399;
}

/* Footer */
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

  .details-content {
    grid-template-columns: 1fr;
  }

  .pros-cons-section {
    grid-template-columns: 1fr;
  }
}
</style>
