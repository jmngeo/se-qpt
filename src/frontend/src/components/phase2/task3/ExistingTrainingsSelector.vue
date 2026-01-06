<template>
  <el-card class="existing-trainings-card" v-loading="isLoading">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon :size="20" color="#409EFF"><Box /></el-icon>
          <span class="header-title">Existing Training Check</span>
        </div>
        <el-tag v-if="selectedCount > 0" type="info" size="small">
          {{ selectedCount }} excluded
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
        Check for existing training programs
      </template>
      <p class="alert-description">
        Please check if there are certain trainings that already exist in your
        organization for the listed competencies. These will not be considered
        for new training development and will be marked as "Training Exists".
      </p>
    </el-alert>

    <!-- Competency Selection Grid -->
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
        {{ selectedCount }} competenc{{ selectedCount === 1 ? 'y' : 'ies' }} will be excluded
        from training requirements (including all levels: Knowing, Understanding, Applying).
      </span>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Check, InfoFilled } from '@element-plus/icons-vue'
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
const isLoading = ref(false)
const isSaving = ref(false)

// Computed
const selectedCount = computed(() => selectedIds.value.size)

const hasChanges = computed(() => {
  if (selectedIds.value.size !== originalIds.value.size) return true
  for (const id of selectedIds.value) {
    if (!originalIds.value.has(id)) return true
  }
  return false
})

// Methods
const isSelected = (id) => selectedIds.value.has(id)

const toggleCompetency = (id) => {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  selectedIds.value = newSet
}

const clearAll = () => {
  selectedIds.value = new Set()
}

const fetchData = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(
      `/api/phase2/existing-trainings/${props.organizationId}`
    )

    if (response.data.success) {
      competencies.value = response.data.data.all_competencies || []
      const existingIds = response.data.data.existing_training_competencies || []
      selectedIds.value = new Set(existingIds)
      originalIds.value = new Set(existingIds)
      console.log('[ExistingTrainings] Loaded:', {
        competencies: competencies.value.length,
        existingIds: existingIds
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

    const response = await axios.put(
      `/api/phase2/existing-trainings/${props.organizationId}`,
      {
        competency_ids: Array.from(selectedIds.value)
      }
    )

    if (response.data.success) {
      originalIds.value = new Set(selectedIds.value)
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
  line-height: 1.5;
  color: #606266;
}

.competency-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
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
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 6px;
  font-size: 13px;
  color: #e6a23c;
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
}
</style>
