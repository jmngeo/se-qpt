<template>
  <el-card class="existing-trainings-card" v-loading="isLoading">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon :size="20" color="#409EFF"><Box /></el-icon>
          <span class="header-title">Existing Training Check</span>
        </div>
        <el-tag v-if="selectedCount > 0" type="info" size="small">
          {{ selectedCount }} competenc{{ selectedCount === 1 ? 'y' : 'ies' }} selected
        </el-tag>
      </div>
    </template>

    <!-- Info Banner -->
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="info-alert"
    >
      <template #title>
        2-Step Existing Training Check
      </template>
      <p class="alert-description">
        <strong>Step 1:</strong> Select competencies for which your organization already has training programs.<br>
        <strong>Step 2:</strong> For each selected competency, specify which levels are covered by the existing training.
      </p>
    </el-alert>

    <!-- Step 1: Competency Selection Grid -->
    <div class="section-header">
      <span class="step-badge">Step 1</span>
      <span class="section-title">Select competencies with existing training</span>
    </div>
    <div class="competency-grid">
      <div
        v-for="comp in competencies"
        :key="comp.id"
        class="competency-item"
        :class="{ 'is-selected': isSelected(comp.id) }"
        @click="toggleCompetency(comp.id)"
      >
        <el-checkbox
          :model-value="isSelected(comp.id)"
          @change="toggleCompetency(comp.id)"
          @click.stop
        />
        <div class="competency-info">
          <span class="competency-name">{{ comp.name }}</span>
          <span class="competency-area">{{ comp.area || 'Systems Engineering' }}</span>
        </div>
      </div>
    </div>

    <!-- Step 2: Level Selection for Selected Competencies -->
    <div v-if="selectedCount > 0" class="level-selection-section">
      <div class="section-header">
        <span class="step-badge">Step 2</span>
        <span class="section-title">Specify covered levels for each competency</span>
      </div>
      <div class="level-selection-list">
        <div
          v-for="compId in Array.from(selectedIds)"
          :key="compId"
          class="level-selection-item"
        >
          <div class="comp-header">
            <el-icon><Document /></el-icon>
            <span class="comp-name">{{ getCompetencyName(compId) }}</span>
          </div>
          <div class="level-checkboxes">
            <el-checkbox-group v-model="competencyLevels[compId]" @change="onLevelsChange(compId)">
              <el-checkbox :value="1" class="level-checkbox">
                <span class="level-label">Knowing</span>
                <span class="level-desc">(Level 1)</span>
              </el-checkbox>
              <el-checkbox :value="2" class="level-checkbox">
                <span class="level-label">Understanding</span>
                <span class="level-desc">(Level 2)</span>
              </el-checkbox>
              <el-checkbox :value="4" class="level-checkbox">
                <span class="level-label">Applying</span>
                <span class="level-desc">(Level 4)</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions-row">
      <el-button size="small" text @click="clearAll" :disabled="selectedCount === 0">
        Clear All
      </el-button>
      <el-button
        type="primary"
        size="small"
        @click="saveSelections"
        :loading="isSaving"
        :disabled="!hasChanges"
      >
        <el-icon><Check /></el-icon>
        Save Selections
      </el-button>
    </div>

    <!-- Note about impact -->
    <div v-if="selectedCount > 0" class="impact-note">
      <el-icon><InfoFilled /></el-icon>
      <span>
        Only the selected levels for each competency will be excluded from training requirements.
        Unselected levels will still be generated as learning objectives.
      </span>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Check, InfoFilled, Document } from '@element-plus/icons-vue'
import axios from '@/api/axios'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

// State
const competencies = ref([])
const selectedIds = ref(new Set())
const originalIds = ref(new Set())
const competencyLevels = reactive({})  // {competencyId: [1, 2, 4]}
const originalLevels = ref({})  // For tracking changes
const isLoading = ref(false)
const isSaving = ref(false)

// Computed
const selectedCount = computed(() => selectedIds.value.size)

const hasChanges = computed(() => {
  // Check if selected IDs changed
  if (selectedIds.value.size !== originalIds.value.size) return true
  for (const id of selectedIds.value) {
    if (!originalIds.value.has(id)) return true
  }
  for (const id of originalIds.value) {
    if (!selectedIds.value.has(id)) return true
  }

  // Check if levels changed for any selected competency
  for (const compId of selectedIds.value) {
    const currentLevels = competencyLevels[compId] || []
    const originalCompLevels = originalLevels.value[compId] || [1, 2, 4]

    if (currentLevels.length !== originalCompLevels.length) return true
    const sortedCurrent = [...currentLevels].sort()
    const sortedOriginal = [...originalCompLevels].sort()
    for (let i = 0; i < sortedCurrent.length; i++) {
      if (sortedCurrent[i] !== sortedOriginal[i]) return true
    }
  }

  return false
})

// Methods
const isSelected = (id) => selectedIds.value.has(id)

const getCompetencyName = (id) => {
  const comp = competencies.value.find(c => c.id === id)
  return comp ? comp.name : `Competency ${id}`
}

const toggleCompetency = (id) => {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
    // Clean up levels when deselecting
    delete competencyLevels[id]
  } else {
    newSet.add(id)
    // Initialize with all levels selected by default
    competencyLevels[id] = [1, 2, 4]
  }
  selectedIds.value = newSet
}

const onLevelsChange = (compId) => {
  // Ensure at least one level is selected
  if (!competencyLevels[compId] || competencyLevels[compId].length === 0) {
    // If user tries to deselect all, keep level 1
    competencyLevels[compId] = [1]
    ElMessage.warning('At least one level must be selected')
  }
}

const clearAll = () => {
  selectedIds.value = new Set()
  Object.keys(competencyLevels).forEach(key => {
    delete competencyLevels[key]
  })
}

const fetchData = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(
      `/api/phase2/existing-trainings/${props.organizationId}`
    )

    if (response.data.success) {
      competencies.value = response.data.data.all_competencies || []
      const existingTrainings = response.data.data.existing_trainings_detail || []

      // Build selected IDs and levels from existing data
      const ids = new Set()
      const levels = {}

      existingTrainings.forEach(training => {
        ids.add(training.competency_id)
        // covered_levels is already parsed as array in to_dict()
        const coveredLevels = training.covered_levels || [1, 2, 4]
        levels[training.competency_id] = [...coveredLevels]
        competencyLevels[training.competency_id] = [...coveredLevels]
      })

      selectedIds.value = ids
      originalIds.value = new Set(ids)
      originalLevels.value = JSON.parse(JSON.stringify(levels))

      console.log('[ExistingTrainings] Loaded:', {
        competencies: competencies.value.length,
        existingTrainings: existingTrainings.length,
        levels: levels
      })
    }
  } catch (error) {
    console.error('[ExistingTrainings] Fetch error:', error)
    ElMessage.error('Failed to load existing trainings data')
  } finally {
    isLoading.value = false
  }
}

const saveSelections = async () => {
  try {
    isSaving.value = true

    // Build trainings array with level info
    const trainings = Array.from(selectedIds.value).map(compId => ({
      competency_id: compId,
      covered_levels: competencyLevels[compId] || [1, 2, 4]
    }))

    const response = await axios.put(
      `/api/phase2/existing-trainings/${props.organizationId}`,
      { trainings }
    )

    if (response.data.success) {
      // Update original values
      originalIds.value = new Set(selectedIds.value)
      originalLevels.value = JSON.parse(JSON.stringify(competencyLevels))

      ElMessage.success('Existing training selections saved')
      emit('updated')
    }
  } catch (error) {
    console.error('[ExistingTrainings] Save error:', error)
    ElMessage.error('Failed to save selections')
  } finally {
    isSaving.value = false
  }
}

// Lifecycle
onMounted(fetchData)
</script>

<style scoped>
.existing-trainings-card {
  border-left: 4px solid #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.info-alert {
  margin-bottom: 20px;
}

.alert-description {
  margin: 8px 0 0 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.step-badge {
  background: #409EFF;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.competency-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.competency-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.competency-item:hover {
  background: #ecf5ff;
  border-color: #409EFF;
}

.competency-item.is-selected {
  background: #e6f7ff;
  border-color: #409EFF;
}

.competency-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.competency-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.competency-area {
  font-size: 12px;
  color: #909399;
}

/* Step 2: Level Selection */
.level-selection-section {
  background: #f8fafc;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.level-selection-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-selection-item {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 16px;
}

.comp-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #303133;
}

.comp-header .el-icon {
  color: #409EFF;
}

.comp-name {
  font-weight: 600;
  font-size: 14px;
}

.level-checkboxes {
  padding-left: 24px;
}

.level-checkboxes :deep(.el-checkbox-group) {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.level-checkbox {
  margin-right: 0 !important;
}

.level-label {
  font-weight: 500;
  color: #303133;
}

.level-desc {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.impact-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 16px 0 0 0;
  padding: 12px 16px;
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 6px;
  font-size: 13px;
  color: #67c23a;
  line-height: 1.5;
}

.impact-note .el-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .competency-grid {
    grid-template-columns: 1fr;
  }

  .header-title {
    font-size: 14px;
  }

  .level-checkboxes :deep(.el-checkbox-group) {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
