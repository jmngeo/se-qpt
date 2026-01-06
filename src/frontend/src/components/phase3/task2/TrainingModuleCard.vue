<template>
  <div class="training-module-card" :class="{ 'confirmed': module.confirmed }">
    <!-- Roles header -->
    <div class="module-roles">
      <el-tag
        v-for="role in displayRoles"
        :key="role"
        size="small"
        effect="plain"
        type="info"
      >{{ role }}</el-tag>
      <span v-if="rolesNeeding.length > 3" class="more-roles">
        +{{ rolesNeeding.length - 3 }} more
      </span>
    </div>

    <!-- Module content -->
    <div class="module-content">
      <div class="module-info">
        <h4 class="module-name">{{ module.module_name }}</h4>
        <div class="module-meta">
          <span class="participants">
            <el-icon><User /></el-icon>
            Est. {{ module.estimated_participants || 0 }} participants
          </span>
          <span class="target-level">
            <el-icon><Medal /></el-icon>
            Target: L{{ module.target_level }} ({{ getLevelName(module.target_level) }})
          </span>
        </div>
      </div>

      <div class="module-format">
        <!-- Format selection button/display -->
        <div v-if="module.selected_format" class="selected-format">
          <div class="format-display" @click="openFormatSelector">
            <span class="format-emoji">{{ getFormatEmoji(module.selected_format.format_key) }}</span>
            <span class="format-name">{{ module.selected_format.short_name }}</span>
            <el-icon class="edit-icon"><Edit /></el-icon>
          </div>

          <!-- Suitability indicators -->
          <div v-if="module.suitability" class="suitability-preview">
            <SuitabilityIndicators :suitability="module.suitability" :compact="true" />
          </div>

          <!-- Confirmed badge -->
          <el-tag v-if="module.confirmed" type="success" size="small" effect="dark">
            <el-icon><Check /></el-icon> Confirmed
          </el-tag>
        </div>

        <div v-else class="no-format">
          <el-button type="primary" plain @click="openFormatSelector">
            <el-icon><Setting /></el-icon>
            Select Format
          </el-button>
        </div>
      </div>
    </div>

    <!-- Format Selector Dialog -->
    <FormatSelectorDialog
      v-model="showFormatDialog"
      :module="module"
      :organization-id="organizationId"
      @selected="handleFormatSelected"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { User, Medal, Edit, Setting, Check } from '@element-plus/icons-vue'
import SuitabilityIndicators from './SuitabilityIndicators.vue'
import FormatSelectorDialog from './FormatSelectorDialog.vue'

const props = defineProps({
  module: {
    type: Object,
    required: true
  },
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['formatSelected'])

const showFormatDialog = ref(false)

// Use roles_needing_training from backend
const rolesNeeding = computed(() => {
  return props.module.roles_needing_training || []
})

const displayRoles = computed(() => {
  return rolesNeeding.value.slice(0, 3)
})

const levelNames = {
  1: 'Knowing',
  2: 'Understanding',
  4: 'Applying',
  6: 'Mastering'
}

const getLevelName = (level) => {
  return levelNames[level] || `Level ${level}`
}

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

const openFormatSelector = () => {
  showFormatDialog.value = true
}

const handleFormatSelected = (selection) => {
  emit('formatSelected', {
    moduleId: props.module.id,
    competencyId: props.module.competency_id,
    targetLevel: props.module.target_level,
    pmtType: props.module.pmt_type,
    ...selection
  })
}
</script>

<style scoped>
.training-module-card {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.2s ease;
}

.training-module-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.training-module-card.confirmed {
  border-color: #67C23A;
  background: linear-gradient(to right, #F0F9EB 0%, white 50%);
}

/* Roles header */
.module-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #EBEEF5;
}

.more-roles {
  font-size: 12px;
  color: #909399;
  align-self: center;
}

/* Module content */
.module-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.module-info {
  flex: 1;
  min-width: 0;
}

.module-name {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.module-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.module-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.module-meta .el-icon {
  color: #909399;
}

/* Format section */
.module-format {
  flex-shrink: 0;
  text-align: right;
}

.selected-format {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.format-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #F5F7FA;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.format-display:hover {
  background: #ECF5FF;
}

.format-emoji {
  font-size: 20px;
}

.format-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.edit-icon {
  color: #409EFF;
  font-size: 14px;
}

.suitability-preview {
  padding: 4px 8px;
  background: #FAFAFA;
  border-radius: 4px;
}

.no-format {
  padding: 4px 0;
}

/* Responsive */
@media (max-width: 600px) {
  .module-content {
    flex-direction: column;
  }

  .module-format {
    width: 100%;
    text-align: left;
  }

  .selected-format {
    align-items: flex-start;
  }
}
</style>
