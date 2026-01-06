<template>
  <div class="timeline-planning">
    <!-- Header Info -->
    <div class="timeline-header">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        <template #title>
          <span class="alert-title">Timeline Planning - Macro-Level Scheduling</span>
        </template>
        <template #default>
          <p>
            SE-QPT Phases 1-3 cover the <strong>Exploration/Needs Assessment</strong> and
            <strong>Design/Planning</strong> phases of the training lifecycle.
            Timeline Planning focuses on scheduling the remaining phases: Development, Pilot, and Rollout.
          </p>
          <p class="note">
            <strong>Note:</strong> These are macro-level estimates based on typical training lifecycle durations.
            Adjust as needed for your organization's specific constraints.
          </p>
        </template>
      </el-alert>

      <!-- Phase Descriptions -->
      <div class="phase-descriptions">
        <h4>Timeline Phases Overview</h4>
        <div class="phase-grid">
          <div class="phase-desc concept">
            <div class="phase-header">
              <span class="phase-icon">1</span>
              <span class="phase-name">Concept Development</span>
            </div>
            <p>Training material development phase. Includes content creation, instructional design, and resource preparation.</p>
            <span class="phase-duration">Typical: 2-4 months</span>
          </div>
          <div class="phase-desc pilot">
            <div class="phase-header">
              <span class="phase-icon">2</span>
              <span class="phase-name">Pilot</span>
            </div>
            <p>Test phase with a small group. Validates content effectiveness and allows refinements before full rollout.</p>
            <span class="phase-duration">Typical: 1-3 months</span>
          </div>
          <div class="phase-desc rollout">
            <div class="phase-header">
              <span class="phase-icon">3</span>
              <span class="phase-name">Initial Implementation</span>
            </div>
            <p>Full rollout to target audience. Training sessions delivered according to the planned schedule.</p>
            <span class="phase-duration">Typical: 6-12 months</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading timeline data...</p>
    </div>

    <!-- No Timeline Yet -->
    <div v-else-if="!hasTimeline && !generating" class="generate-section">
      <div class="generate-card">
        <div class="generate-icon">
          <el-icon :size="64" color="#409EFF"><Calendar /></el-icon>
        </div>
        <h3>Generate Timeline Estimates</h3>
        <p>
          Click the button below to generate LLM-based timeline estimates for your training program.
        </p>

        <!-- Context Summary -->
        <div class="context-summary">
          <h4>Generation will consider:</h4>
          <div class="context-items">
            <div class="context-item">
              <el-icon><Document /></el-icon>
              <span>{{ contextSummary.moduleCount }} training modules</span>
            </div>
            <div class="context-item">
              <el-icon><User /></el-icon>
              <span>{{ contextSummary.targetGroupSize }} target participants ({{ contextSummary.targetGroupRange }})</span>
            </div>
            <div class="context-item">
              <el-icon><Collection /></el-icon>
              <span>{{ contextSummary.formatMix }}</span>
            </div>
            <div class="context-item">
              <el-icon><Star /></el-icon>
              <span>{{ contextSummary.strategy }} strategy</span>
            </div>
          </div>
        </div>

        <el-button
          type="primary"
          size="large"
          :loading="generating"
          @click="generateTimeline"
        >
          <el-icon><MagicStick /></el-icon>
          Generate Timeline Estimates
        </el-button>
      </div>
    </div>

    <!-- Generating State -->
    <div v-else-if="generating" class="generating-state">
      <div class="generating-animation">
        <el-icon class="is-loading" :size="48" color="#409EFF"><Loading /></el-icon>
      </div>
      <h3>Generating Timeline...</h3>
      <p>The AI is analyzing your training program and generating milestone estimates.</p>
      <p class="hint">This may take a few moments.</p>
    </div>

    <!-- Timeline Display -->
    <div v-else-if="hasTimeline && !hasValidMilestones" class="incomplete-timeline">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
      >
        <template #title>Timeline Data Incomplete</template>
        <template #default>
          <p>Some milestone data is missing. Please regenerate the timeline to get complete estimates.</p>
        </template>
      </el-alert>
    </div>

    <div v-else class="timeline-content">
      <!-- Timeline Table -->
      <div class="timeline-table-section">
        <h3 class="section-title">
          <el-icon><Flag /></el-icon>
          Generated Timeline
        </h3>

        <div class="timeline-table-wrapper">
          <table class="timeline-table">
            <thead>
              <tr>
                <th class="col-phase">Phase</th>
                <th class="col-milestone">Milestone</th>
                <th class="col-quarter">Quarter</th>
                <th class="col-date">Est. Date</th>
                <th class="col-duration">Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr class="phase-row development">
                <td class="phase-cell" rowspan="2">
                  <div class="phase-badge development">
                    <span class="phase-icon">1</span>
                    <span class="phase-name">Development</span>
                  </div>
                </td>
                <td>{{ milestones[0]?.milestone_name }}</td>
                <td class="quarter-cell">{{ milestones[0]?.quarter }}</td>
                <td>{{ formatDate(milestones[0]?.estimated_date) }}</td>
                <td rowspan="2" class="duration-cell">
                  <span class="duration-value">{{ calculateDuration(0, 1) }}</span>
                  <span class="duration-label">months</span>
                </td>
              </tr>
              <tr class="phase-row development">
                <td>{{ milestones[1]?.milestone_name }}</td>
                <td class="quarter-cell">{{ milestones[1]?.quarter }}</td>
                <td>{{ formatDate(milestones[1]?.estimated_date) }}</td>
              </tr>
              <tr class="phase-row pilot">
                <td class="phase-cell">
                  <div class="phase-badge pilot">
                    <span class="phase-icon">2</span>
                    <span class="phase-name">Pilot</span>
                  </div>
                </td>
                <td>{{ milestones[2]?.milestone_name }}</td>
                <td class="quarter-cell">{{ milestones[2]?.quarter }}</td>
                <td>{{ formatDate(milestones[2]?.estimated_date) }}</td>
                <td class="duration-cell">
                  <span class="duration-value">{{ calculateDuration(2, 3) }}</span>
                  <span class="duration-label">months</span>
                </td>
              </tr>
              <tr class="phase-row rollout">
                <td class="phase-cell" rowspan="2">
                  <div class="phase-badge rollout">
                    <span class="phase-icon">3</span>
                    <span class="phase-name">Rollout</span>
                  </div>
                </td>
                <td>{{ milestones[3]?.milestone_name }}</td>
                <td class="quarter-cell">{{ milestones[3]?.quarter }}</td>
                <td>{{ formatDate(milestones[3]?.estimated_date) }}</td>
                <td rowspan="2" class="duration-cell">
                  <span class="duration-value">{{ calculateDuration(3, 4) }}</span>
                  <span class="duration-label">months</span>
                </td>
              </tr>
              <tr class="phase-row rollout">
                <td>{{ milestones[4]?.milestone_name }}</td>
                <td class="quarter-cell">{{ milestones[4]?.quarter }}</td>
                <td>{{ formatDate(milestones[4]?.estimated_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- LLM Reasoning -->
        <div v-if="milestones[0]?.generation_reasoning" class="reasoning-section">
          <h4>
            <el-icon><InfoFilled /></el-icon>
            AI Reasoning
          </h4>
          <p>{{ milestones[0]?.generation_reasoning }}</p>
        </div>
      </div>

      <!-- Visual Timeline Bar -->
      <div class="timeline-visual-section">
        <h3 class="section-title">
          <el-icon><DataLine /></el-icon>
          Timeline Overview
        </h3>

        <div class="gantt-chart">
          <div class="gantt-row">
            <div class="gantt-label">Development</div>
            <div class="gantt-bar-container">
              <div class="gantt-bar development" :style="getGanttBarStyle(0, 1)">
                <span>{{ milestones[0]?.quarter }} - {{ milestones[1]?.quarter }}</span>
              </div>
            </div>
          </div>
          <div class="gantt-row">
            <div class="gantt-label">Pilot</div>
            <div class="gantt-bar-container">
              <div class="gantt-bar pilot" :style="getGanttBarStyle(2, 3)">
                <span>{{ milestones[2]?.quarter }} - {{ milestones[3]?.quarter }}</span>
              </div>
            </div>
          </div>
          <div class="gantt-row">
            <div class="gantt-label">Rollout</div>
            <div class="gantt-bar-container">
              <div class="gantt-bar rollout" :style="getGanttBarStyle(3, 4)">
                <span>{{ milestones[3]?.quarter }} - {{ milestones[4]?.quarter }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="timeline-summary">
          <div class="summary-item">
            <span class="summary-label">Total Duration:</span>
            <span class="summary-value">{{ calculateTotalDuration() }} months</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Start:</span>
            <span class="summary-value">{{ milestones[0]?.quarter }} ({{ formatDate(milestones[0]?.estimated_date) }})</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">End:</span>
            <span class="summary-value">{{ milestones[4]?.quarter }} ({{ formatDate(milestones[4]?.estimated_date) }})</span>
          </div>
        </div>
      </div>

      <!-- Generation Context -->
      <div class="generation-context">
        <h3 class="section-title">
          <el-icon><Document /></el-icon>
          Estimates Based On
        </h3>

        <div class="context-grid">
          <div class="context-card">
            <span class="context-value">{{ contextSummary.moduleCount }}</span>
            <span class="context-label">Training Modules</span>
          </div>
          <div class="context-card">
            <span class="context-value">{{ contextSummary.targetGroupSize }}</span>
            <span class="context-label">Target Participants</span>
          </div>
          <div class="context-card">
            <span class="context-value">{{ contextSummary.formatMix }}</span>
            <span class="context-label">Format Mix</span>
          </div>
          <div class="context-card">
            <el-tooltip
              v-if="contextSummary.strategyCount > 1"
              :content="contextSummary.allStrategies.join(', ')"
              placement="top"
            >
              <span class="context-value strategy-multi">{{ contextSummary.strategy }}</span>
            </el-tooltip>
            <span v-else class="context-value">{{ contextSummary.strategy }}</span>
            <span class="context-label">{{ contextSummary.strategyCount > 1 ? 'Strategies' : 'Strategy' }}</span>
          </div>
        </div>

        <p class="sustainment-note">
          <el-icon><Timer /></el-icon>
          Sustainment and continuous improvement continues as an ongoing activity after rollout completion.
        </p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <el-button @click="$emit('back')">
        <el-icon><ArrowLeft /></el-icon>
        Back to Task 2
      </el-button>
      <el-button
        v-if="hasTimeline"
        type="warning"
        :loading="generating"
        @click="regenerateTimeline"
      >
        <el-icon><Refresh /></el-icon>
        Regenerate Timeline
      </el-button>
      <el-button
        v-if="hasTimeline"
        type="success"
        size="large"
        @click="completePhase"
      >
        <el-icon><Check /></el-icon>
        Complete Phase 3
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Loading, Calendar, Document, User, Collection, Star, MagicStick,
  Flag, DataLine, InfoFilled, Timer, ArrowLeft, Check, Refresh
} from '@element-plus/icons-vue'
import axios from '@/api/axios'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['back', 'completed'])

// State
const loading = ref(true)
const generating = ref(false)
const milestones = ref([])
const contextSummary = ref({
  moduleCount: 0,
  targetGroupSize: 0,
  targetGroupRange: 'Unknown',
  formatMix: 'Mixed',
  strategy: 'Not Selected',
  allStrategies: [],
  strategyCount: 0
})

// Computed
const hasTimeline = computed(() => milestones.value.length >= 5)

// Check if all milestones have valid data
const hasValidMilestones = computed(() => {
  if (milestones.value.length < 5) return false
  return milestones.value.every(m => m && m.milestone_name && m.estimated_date)
})

// Safe access to milestones with fallback
const getMilestone = (index) => {
  if (index < 0 || index >= milestones.value.length) {
    return {
      milestone_name: 'Pending',
      quarter: '-',
      estimated_date: null,
      generation_reasoning: null
    }
  }
  return milestones.value[index]
}

const timelinePhases = computed(() => {
  // Calculate phase widths based on milestones
  // Concept Dev: milestones 1-2
  // Pilot: milestones 2-3
  // Rollout: milestones 3-5
  return [
    { type: 'concept', label: 'CONCEPT DEV', width: 25 },
    { type: 'pilot', label: 'PILOT', width: 15 },
    { type: 'rollout', label: 'ROLLOUT / IMPLEMENTATION', width: 60 }
  ]
})

// Methods
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

const calculateDuration = (startIdx, endIdx) => {
  if (!milestones.value[startIdx]?.estimated_date || !milestones.value[endIdx]?.estimated_date) {
    return '-'
  }
  const start = new Date(milestones.value[startIdx].estimated_date)
  const end = new Date(milestones.value[endIdx].estimated_date)
  const months = Math.round((end - start) / (1000 * 60 * 60 * 24 * 30))
  return months
}

const calculateTotalDuration = () => {
  if (!milestones.value[0]?.estimated_date || !milestones.value[4]?.estimated_date) {
    return '-'
  }
  const start = new Date(milestones.value[0].estimated_date)
  const end = new Date(milestones.value[4].estimated_date)
  const months = Math.round((end - start) / (1000 * 60 * 60 * 24 * 30))
  return months
}

const getGanttBarStyle = (startIdx, endIdx) => {
  if (!milestones.value[0]?.estimated_date || !milestones.value[4]?.estimated_date) {
    return { left: '0%', width: '20%' }
  }

  const totalStart = new Date(milestones.value[0].estimated_date)
  const totalEnd = new Date(milestones.value[4].estimated_date)
  const totalDuration = totalEnd - totalStart

  const phaseStart = new Date(milestones.value[startIdx].estimated_date)
  const phaseEnd = new Date(milestones.value[endIdx].estimated_date)

  const leftPercent = ((phaseStart - totalStart) / totalDuration) * 100
  const widthPercent = ((phaseEnd - phaseStart) / totalDuration) * 100

  return {
    left: `${leftPercent}%`,
    width: `${Math.max(widthPercent, 5)}%`
  }
}

const loadTimeline = async () => {
  loading.value = true
  try {
    // Load context from output endpoint first
    const outputResponse = await axios.get(`/api/phase3/output/${props.organizationId}`)
    if (outputResponse.data.success) {
      const data = outputResponse.data
      const summary = data.summary || {}

      // Handle multiple strategies
      const allStrategies = summary.all_strategies || [summary.strategy_name].filter(Boolean)
      const strategyCount = summary.strategy_count || allStrategies.length
      let strategyDisplay = summary.strategy_name || 'Not Selected'
      if (strategyCount > 1) {
        strategyDisplay = `${allStrategies[0]} (+${strategyCount - 1} more)`
      }

      contextSummary.value = {
        moduleCount: summary.module_count || summary.total_modules || 0,
        targetGroupSize: summary.target_group_size || 0,
        targetGroupRange: summary.target_group_range || 'Unknown',
        formatMix: getFormatMixFromSummary(summary.format_distribution),
        strategy: strategyDisplay,
        allStrategies: allStrategies,
        strategyCount: strategyCount
      }
    }

    // Load timeline milestones
    const response = await axios.get(`/api/phase3/timeline/${props.organizationId}`)
    if (response.data.success) {
      milestones.value = response.data.milestones || []
    }
  } catch (error) {
    console.error('Error loading timeline:', error)
    // Don't show error - timeline might not exist yet
  } finally {
    loading.value = false
  }
}

const getFormatMixFromSummary = (formatDistribution) => {
  if (!formatDistribution || Object.keys(formatDistribution).length === 0) {
    return 'Not configured'
  }
  const formatCount = Object.keys(formatDistribution).length
  if (formatCount === 1) {
    return Object.keys(formatDistribution)[0]
  }
  return `${formatCount} formats`
}

const generateTimeline = async () => {
  generating.value = true
  try {
    const response = await axios.post('/api/phase3/generate-timeline', {
      organization_id: props.organizationId
    })

    if (response.data.success) {
      milestones.value = response.data.milestones || []
      ElMessage.success('Timeline generated successfully')
    } else {
      ElMessage.error(response.data.error || 'Failed to generate timeline')
    }
  } catch (error) {
    console.error('Error generating timeline:', error)
    ElMessage.error('Failed to generate timeline. Please try again.')
  } finally {
    generating.value = false
  }
}

const regenerateTimeline = async () => {
  try {
    await ElMessageBox.confirm(
      'This will regenerate the timeline using the latest training program data. The existing timeline will be replaced.',
      'Regenerate Timeline',
      {
        confirmButtonText: 'Regenerate',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await generateTimeline()
  } catch {
    // User cancelled
  }
}

const completePhase = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you ready to complete Phase 3? You can still return to make changes later.',
      'Complete Phase 3',
      {
        confirmButtonText: 'Complete',
        cancelButtonText: 'Cancel',
        type: 'success'
      }
    )

    emit('completed')
  } catch {
    // User cancelled
  }
}

// Initialize
onMounted(() => {
  loadTimeline()
})
</script>

<style scoped>
.timeline-planning {
  padding: 20px;
}

.timeline-header {
  margin-bottom: 24px;
}

.alert-title {
  font-weight: 600;
}

.timeline-header p {
  margin: 0 0 8px 0;
}

.timeline-header .note {
  font-size: 13px;
  color: #909399;
}

/* Phase Descriptions */
.phase-descriptions {
  margin-top: 20px;
  padding: 20px;
  background: #FAFAFA;
  border-radius: 8px;
}

.phase-descriptions h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: #303133;
}

.phase-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.phase-desc {
  padding: 16px;
  border-radius: 8px;
  background: white;
  border-left: 4px solid #E4E7ED;
}

.phase-desc.concept { border-left-color: #67C23A; }
.phase-desc.pilot { border-left-color: #E6A23C; }
.phase-desc.rollout { border-left-color: #409EFF; }

.phase-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.phase-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #E4E7ED;
  color: #606266;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phase-desc.concept .phase-icon { background: #67C23A; color: white; }
.phase-desc.pilot .phase-icon { background: #E6A23C; color: white; }
.phase-desc.rollout .phase-icon { background: #409EFF; color: white; }

.phase-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.phase-desc p {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.phase-duration {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

/* Incomplete Timeline */
.incomplete-timeline {
  padding: 40px 20px;
  text-align: center;
}

/* Generate Section */
.generate-section {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.generate-card {
  max-width: 600px;
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #F5F7FA 0%, #E4E7ED 100%);
  border-radius: 16px;
}

.generate-icon {
  margin-bottom: 20px;
}

.generate-card h3 {
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #303133;
}

.generate-card > p {
  margin: 0 0 24px 0;
  color: #606266;
}

.context-summary {
  text-align: left;
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 24px;
}

.context-summary h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.context-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.context-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.context-item .el-icon {
  color: #409EFF;
}

/* Generating State */
.generating-state {
  text-align: center;
  padding: 60px 20px;
}

.generating-animation {
  margin-bottom: 20px;
}

.generating-state h3 {
  margin: 0 0 12px 0;
  color: #303133;
}

.generating-state p {
  margin: 0 0 8px 0;
  color: #606266;
}

.generating-state .hint {
  font-size: 13px;
  color: #909399;
}

/* Timeline Content */
.timeline-content {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #303133;
}

/* Milestones */
.milestones-section {
  margin-bottom: 32px;
}

.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}

.milestone-item {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  position: relative;
}

.milestone-item::before {
  content: '';
  position: absolute;
  left: 18px;
  top: 50px;
  bottom: -10px;
  width: 2px;
  background: #E4E7ED;
}

.milestone-item:last-child::before {
  display: none;
}

.milestone-marker {
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.marker-number {
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.milestone-item.start .milestone-marker { background: #67C23A; }
.milestone-item.concept-end .milestone-marker { background: #409EFF; }
.milestone-item.pilot .milestone-marker { background: #E6A23C; }
.milestone-item.rollout-start .milestone-marker { background: #F56C6C; }
.milestone-item.rollout-end .milestone-marker { background: #909399; }

.milestone-content {
  flex: 1;
}

.milestone-name {
  margin: 0 0 6px 0;
  font-size: 16px;
  color: #303133;
}

.milestone-description {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #606266;
}

.milestone-dates {
  display: flex;
  gap: 16px;
}

.quarter {
  font-weight: 600;
  color: #409EFF;
}

.date {
  color: #909399;
}

/* Timeline Visualization */
.timeline-visualization {
  margin-bottom: 32px;
  padding: 24px;
  background: #F5F7FA;
  border-radius: 12px;
}

.timeline-bar {
  position: relative;
  margin-bottom: 20px;
}

.timeline-track {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
}

.timeline-phase {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.timeline-phase.concept { background: #67C23A; }
.timeline-phase.pilot { background: #E6A23C; }
.timeline-phase.rollout { background: #409EFF; }

.timeline-markers {
  position: relative;
  height: 30px;
  margin-top: 8px;
}

.marker {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
}

.marker-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #303133;
  margin: 0 auto 4px;
}

.marker-label {
  font-size: 10px;
  color: #606266;
}

.timeline-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #606266;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-item.concept .legend-color { background: #67C23A; }
.legend-item.pilot .legend-color { background: #E6A23C; }
.legend-item.rollout .legend-color { background: #409EFF; }

/* Generation Context */
.generation-context {
  padding: 24px;
  background: white;
  border: 1px solid #EBEEF5;
  border-radius: 12px;
}

.context-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.context-card {
  text-align: center;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
}

.context-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.context-value.strategy-multi {
  cursor: help;
  text-decoration: underline dotted;
  text-underline-offset: 3px;
}

.context-label {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sustainment-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 0;
  padding: 12px;
  background: #FDF6EC;
  border-radius: 6px;
  font-size: 13px;
  color: #E6A23C;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

/* Timeline Table Section */
.timeline-table-section {
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border: 1px solid #EBEEF5;
  border-radius: 12px;
}

.timeline-table-wrapper {
  overflow-x: auto;
}

.timeline-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.timeline-table th,
.timeline-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #EBEEF5;
}

.timeline-table th {
  background: #F5F7FA;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #606266;
}

.timeline-table th.col-phase { width: 140px; }
.timeline-table th.col-milestone { width: auto; }
.timeline-table th.col-quarter { width: 100px; }
.timeline-table th.col-date { width: 120px; }
.timeline-table th.col-duration { width: 100px; text-align: center; }

.timeline-table tbody tr {
  transition: background-color 0.2s;
}

.timeline-table tbody tr:hover {
  background-color: #FAFAFA;
}

.phase-cell {
  vertical-align: middle;
}

.phase-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #F5F7FA;
}

.phase-badge .phase-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.phase-badge .phase-name {
  font-size: 13px;
  font-weight: 600;
}

.phase-badge.development { background: rgba(103, 194, 58, 0.1); }
.phase-badge.development .phase-icon { background: #67C23A; }
.phase-badge.development .phase-name { color: #67C23A; }

.phase-badge.pilot { background: rgba(230, 162, 60, 0.1); }
.phase-badge.pilot .phase-icon { background: #E6A23C; }
.phase-badge.pilot .phase-name { color: #E6A23C; }

.phase-badge.rollout { background: rgba(64, 158, 255, 0.1); }
.phase-badge.rollout .phase-icon { background: #409EFF; }
.phase-badge.rollout .phase-name { color: #409EFF; }

.quarter-cell {
  font-weight: 600;
  color: #303133;
}

.duration-cell {
  text-align: center;
  vertical-align: middle;
  background: #FAFAFA;
}

.duration-cell .duration-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #409EFF;
}

.duration-cell .duration-label {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
}

/* Reasoning Section */
.reasoning-section {
  padding: 16px 20px;
  background: #F0F9FF;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.reasoning-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #409EFF;
}

.reasoning-section p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}

/* Gantt Chart */
.timeline-visual-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #F5F7FA;
  border-radius: 12px;
}

.gantt-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.gantt-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.gantt-label {
  width: 100px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  text-align: right;
}

.gantt-bar-container {
  flex: 1;
  height: 36px;
  background: #E4E7ED;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.gantt-bar {
  position: absolute;
  height: 100%;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  font-weight: 600;
  min-width: 80px;
  transition: all 0.3s ease;
}

.gantt-bar.development { background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%); }
.gantt-bar.pilot { background: linear-gradient(135deg, #E6A23C 0%, #ebb563 100%); }
.gantt-bar.rollout { background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%); }

.gantt-bar:hover {
  transform: scaleY(1.1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* Timeline Summary */
.timeline-summary {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 13px;
  color: #909399;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* Responsive */
@media (max-width: 900px) {
  .phase-grid {
    grid-template-columns: 1fr;
  }

  .timeline-summary {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .gantt-label {
    width: 80px;
    font-size: 11px;
  }
}

@media (max-width: 768px) {
  .context-items {
    grid-template-columns: 1fr;
  }

  .context-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .timeline-legend {
    flex-direction: column;
    align-items: center;
  }

  .phase-label {
    font-size: 9px;
  }
}
</style>
