<template>
  <div class="suitability-indicators" :class="{ 'compact': compact }">
    <!-- Compact mode: Just dots -->
    <template v-if="compact">
      <div class="indicator-dots">
        <span
          v-for="(factor, index) in factors"
          :key="index"
          class="indicator-dot"
          :class="factor.status"
          :title="factor.label + ': ' + factor.message"
        ></span>
      </div>
    </template>

    <!-- Full mode: Detailed display -->
    <template v-else>
      <div class="indicator-list">
        <div
          v-for="(factor, index) in factors"
          :key="index"
          class="indicator-item"
          :class="factor.status"
        >
          <div class="indicator-icon">
            <span class="status-dot" :class="factor.status"></span>
          </div>
          <div class="indicator-content">
            <div class="indicator-label">{{ factor.label }}</div>
            <div class="indicator-message">{{ factor.message }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  suitability: {
    type: Object,
    default: () => ({})
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const factors = computed(() => {
  if (!props.suitability || !props.suitability.factors) {
    return []
  }

  const f = props.suitability.factors
  return [
    {
      label: 'Participants',
      status: f.factor1?.status || 'unknown',
      message: f.factor1?.message || 'Not evaluated'
    },
    {
      label: 'Level Achievable',
      status: f.factor2?.status || 'unknown',
      message: f.factor2?.message || 'Not evaluated'
    },
    {
      label: 'Strategy Fit',
      status: f.factor3?.status || 'unknown',
      message: f.factor3?.message || 'Not evaluated'
    }
  ]
})
</script>

<style scoped>
.suitability-indicators {
  display: flex;
  flex-direction: column;
}

/* Compact mode - just dots */
.indicator-dots {
  display: flex;
  gap: 6px;
  align-items: center;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #909399;
}

.indicator-dot.green {
  background: #67C23A;
}

.indicator-dot.yellow {
  background: #E6A23C;
}

.indicator-dot.red {
  background: #F56C6C;
}

.indicator-dot.unknown {
  background: #C0C4CC;
}

/* Full mode - detailed list */
.indicator-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.indicator-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #F5F7FA;
  border-radius: 8px;
  border-left: 3px solid #C0C4CC;
}

.indicator-item.green {
  background: #F0F9EB;
  border-left-color: #67C23A;
}

.indicator-item.yellow {
  background: #FDF6EC;
  border-left-color: #E6A23C;
}

.indicator-item.red {
  background: #FEF0F0;
  border-left-color: #F56C6C;
}

.indicator-icon {
  flex-shrink: 0;
  padding-top: 2px;
}

.status-dot {
  display: block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #C0C4CC;
}

.status-dot.green {
  background: #67C23A;
}

.status-dot.yellow {
  background: #E6A23C;
}

.status-dot.red {
  background: #F56C6C;
}

.indicator-content {
  flex: 1;
  min-width: 0;
}

.indicator-label {
  font-weight: 600;
  font-size: 13px;
  color: #303133;
  margin-bottom: 2px;
}

.indicator-message {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}
</style>
