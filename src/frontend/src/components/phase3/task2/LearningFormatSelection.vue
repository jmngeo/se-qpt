<template>
  <div class="learning-format-selection">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading training modules...</p>
    </div>

    <template v-else>
      <!-- Scaling Info Banner -->
      <el-alert
        v-if="scalingInfo"
        type="info"
        :closable="false"
        class="scaling-banner"
      >
        <template #title>
          <span class="banner-title">
            <el-icon><InfoFilled /></el-icon>
            Participant Estimation
          </span>
        </template>
        <template #default>
          <div class="scaling-content">
            <p>
              Participant counts are <strong>scaled estimates</strong> based on assessment data:
            </p>
            <div class="scaling-details">
              <div class="scaling-item">
                <span class="scaling-label">Assessed Users:</span>
                <span class="scaling-value">{{ scalingInfo.actual_assessed_users }}</span>
              </div>
              <div class="scaling-item">
                <span class="scaling-label">Target Group Size:</span>
                <span class="scaling-value">{{ scalingInfo.target_group_size }}</span>
              </div>
              <div class="scaling-item highlight">
                <span class="scaling-label">Scaling Factor:</span>
                <span class="scaling-value">{{ scalingInfo.scaling_factor?.toFixed(1) }}x</span>
              </div>
            </div>
          </div>
        </template>
      </el-alert>

      <!-- View Type Indicator -->
      <div class="view-indicator">
        <el-tag :type="selectedView === 'role_clustered' ? 'success' : 'primary'" effect="plain" size="large">
          <el-icon><component :is="selectedView === 'role_clustered' ? 'UserFilled' : 'Grid'" /></el-icon>
          {{ selectedView === 'role_clustered' ? 'Role-Clustered View' : 'Competency-Level View' }}
        </el-tag>
        <span v-if="strategyName" class="strategy-badge">
          Strategy: {{ strategyName }}
        </span>
      </div>

      <!-- No Modules Message -->
      <div v-if="modules.length === 0" class="no-modules">
        <el-empty description="No training modules available">
          <template #description>
            <p>No competency gaps requiring training were found.</p>
            <p class="hint">Complete Phase 2 competency assessments to generate training modules.</p>
          </template>
        </el-empty>
      </div>

      <!-- Modules List -->
      <div v-else class="modules-container">
        <!-- Progress Summary -->
        <div class="progress-summary">
          <div class="summary-stat">
            <span class="stat-value">{{ competencyGroups.length }}</span>
            <span class="stat-label">Competencies</span>
          </div>
          <div class="summary-stat">
            <span class="stat-value">{{ modules.length }}</span>
            <span class="stat-label">Modules</span>
          </div>
          <div class="summary-stat">
            <span class="stat-value">{{ confirmedCount }}</span>
            <span class="stat-label">Confirmed</span>
          </div>
          <div class="summary-stat">
            <span class="stat-value">{{ uniqueRolesCount }}</span>
            <span class="stat-label">Roles</span>
          </div>
        </div>

        <!-- Level Legend -->
        <div class="level-legend">
          <span class="legend-title">Competency Levels:</span>
          <div class="legend-items">
            <span class="legend-item"><span class="level-badge">L1</span> Knowing</span>
            <span class="legend-item"><span class="level-badge">L2</span> Understanding</span>
            <span class="legend-item"><span class="level-badge">L4</span> Applying</span>
            <span class="legend-item"><span class="level-badge">L6</span> Mastering</span>
          </div>
        </div>

        <!-- Competency-Level Based View -->
        <div v-if="selectedView === 'competency_level'" class="competency-groups">
          <div
            v-for="group in competencyGroups"
            :key="group.competency_id"
            class="competency-group"
          >
            <!-- Competency Header -->
            <div class="competency-header" @click="toggleCompetency(group.competency_id)">
              <div class="competency-title">
                <el-icon class="expand-icon" :class="{ 'is-expanded': expandedCompetencies.has(group.competency_id) }">
                  <ArrowRight />
                </el-icon>
                <h3>{{ group.competency_name }}</h3>
              </div>
              <div class="competency-meta">
                <el-tag size="small" effect="plain">
                  {{ group.modules.length }} module{{ group.modules.length > 1 ? 's' : '' }}
                </el-tag>
                <el-tag
                  size="small"
                  :type="group.confirmedCount === group.modules.length ? 'success' : 'info'"
                  effect="plain"
                >
                  {{ group.confirmedCount }}/{{ group.modules.length }} confirmed
                </el-tag>
                <div class="level-badges">
                  <span v-for="level in group.levels" :key="level" class="level-badge">
                    L{{ level }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Modules within competency -->
            <el-collapse-transition>
              <div v-show="expandedCompetencies.has(group.competency_id)" class="competency-modules">
                <div
                  v-for="module in group.modules"
                  :key="`${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                  class="module-item"
                  :class="{ 'is-confirmed': module.confirmed }"
                >
                  <div class="module-row" @click="toggleModuleExpand(`${module.competency_id}_${module.target_level}_${module.pmt_type}`)">
                    <div class="module-info">
                      <el-icon class="expand-icon" :class="{ 'is-expanded': expandedModules.has(`${module.competency_id}_${module.target_level}_${module.pmt_type}`) }">
                        <ArrowRight />
                      </el-icon>
                      <span class="module-level">{{ getLevelName(module.target_level) }}</span>
                      <span v-if="module.pmt_type && module.pmt_type !== 'combined'" class="module-pmt">{{ formatPmtType(module.pmt_type) }}</span>
                      <span class="module-participants">
                        <el-icon><User /></el-icon>
                        {{ module.estimated_participants }} participants
                      </span>
                      <span class="module-roles-count">
                        <el-icon><UserFilled /></el-icon>
                        {{ (module.roles_needing_training || []).length }} roles
                      </span>
                    </div>
                    <div class="module-format-select" @click.stop>
                      <div v-if="module.selected_format" class="format-selected" @click="openFormatDialog(module)">
                        <span class="format-name">{{ module.selected_format.short_name }}</span>
                        <el-icon><Check /></el-icon>
                      </div>
                      <el-button v-else size="small" type="primary" plain @click="openFormatDialog(module)">
                        Select Format
                      </el-button>
                    </div>
                  </div>
                  <!-- Expanded module details -->
                  <el-collapse-transition>
                    <div v-show="expandedModules.has(`${module.competency_id}_${module.target_level}_${module.pmt_type}`)" class="module-details">
                      <div class="detail-section">
                        <h5>Roles Needing Training</h5>
                        <div class="roles-list">
                          <el-tag
                            v-for="role in (module.roles_needing_training || [])"
                            :key="role"
                            size="small"
                            effect="plain"
                            type="info"
                          >{{ role }}</el-tag>
                          <span v-if="!(module.roles_needing_training || []).length" class="no-roles">No specific roles</span>
                        </div>
                      </div>
                    </div>
                  </el-collapse-transition>
                </div>
              </div>
            </el-collapse-transition>
          </div>
        </div>

        <!-- Role-Clustered Based View -->
        <div v-else class="role-clusters-view">
          <div
            v-for="cluster in clustersWithCompetencies"
            :key="cluster.id"
            class="cluster-section"
          >
            <!-- Cluster Header -->
            <div class="cluster-header">
              <div class="cluster-title">
                <el-icon :size="24"><UserFilled /></el-icon>
                <h3>{{ cluster.training_program_name }}</h3>
              </div>
              <div class="cluster-meta">
                <el-tag size="small" effect="plain">{{ cluster.role_count }} roles</el-tag>
                <el-tag size="small" type="info" effect="plain">
                  {{ cluster.competencies.length }} competencies
                </el-tag>
              </div>
            </div>

            <!-- Roles list -->
            <div class="cluster-roles-list">
              <el-tag
                v-for="role in cluster.roles?.slice(0, 5)"
                :key="role"
                size="small"
                effect="plain"
                type="info"
              >{{ role }}</el-tag>
              <span v-if="cluster.roles?.length > 5" class="more-roles">
                +{{ cluster.roles.length - 5 }} more
              </span>
            </div>

            <!-- Competencies within cluster -->
            <div class="cluster-competencies">
              <div
                v-for="compGroup in cluster.competencies"
                :key="`${cluster.id}_${compGroup.competency_id}`"
                class="nested-competency-group"
              >
                <div
                  class="nested-competency-header"
                  @click="toggleNestedCompetency(`${cluster.id}_${compGroup.competency_id}`)"
                >
                  <div class="nested-title">
                    <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`${cluster.id}_${compGroup.competency_id}`) }">
                      <ArrowRight />
                    </el-icon>
                    <span>{{ compGroup.competency_name }}</span>
                  </div>
                  <div class="nested-meta">
                    <span class="level-badges">
                      <span v-for="level in compGroup.levels" :key="level" class="level-badge">L{{ level }}</span>
                    </span>
                    <el-tag
                      size="small"
                      :type="compGroup.confirmedCount === compGroup.modules.length ? 'success' : 'info'"
                    >
                      {{ compGroup.confirmedCount }}/{{ compGroup.modules.length }}
                    </el-tag>
                  </div>
                </div>

                <el-collapse-transition>
                  <div
                    v-show="expandedNestedCompetencies.has(`${cluster.id}_${compGroup.competency_id}`)"
                    class="nested-modules"
                  >
                    <div
                      v-for="module in compGroup.modules"
                      :key="`${cluster.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                      class="module-item"
                      :class="{ 'is-confirmed': module.confirmed }"
                    >
                      <div class="module-row" @click="toggleModuleExpand(`${cluster.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`)">
                        <div class="module-info">
                          <el-icon class="expand-icon" :class="{ 'is-expanded': expandedModules.has(`${cluster.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`) }">
                            <ArrowRight />
                          </el-icon>
                          <span class="module-level">{{ getLevelName(module.target_level) }}</span>
                          <span v-if="module.pmt_type && module.pmt_type !== 'combined'" class="module-pmt">{{ formatPmtType(module.pmt_type) }}</span>
                          <span class="module-participants">
                            <el-icon><User /></el-icon>
                            {{ module.estimated_participants }} participants
                          </span>
                          <span class="module-roles-count">
                            <el-icon><UserFilled /></el-icon>
                            {{ (module.roles_needing_training || []).length }} roles
                          </span>
                        </div>
                        <div class="module-format-select" @click.stop>
                          <div v-if="module.selected_format" class="format-selected" @click="openFormatDialog(module)">
                            <span class="format-name">{{ module.selected_format.short_name }}</span>
                            <el-icon><Check /></el-icon>
                          </div>
                          <el-button v-else size="small" type="primary" plain @click="openFormatDialog(module)">
                            Select Format
                          </el-button>
                        </div>
                      </div>
                      <!-- Expanded module details -->
                      <el-collapse-transition>
                        <div v-show="expandedModules.has(`${cluster.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`)" class="module-details">
                          <div class="detail-section">
                            <h5>Roles Needing Training</h5>
                            <div class="roles-list">
                              <el-tag
                                v-for="role in (module.roles_needing_training || [])"
                                :key="role"
                                size="small"
                                effect="plain"
                                type="info"
                              >{{ role }}</el-tag>
                              <span v-if="!(module.roles_needing_training || []).length" class="no-roles">No specific roles</span>
                            </div>
                          </div>
                        </div>
                      </el-collapse-transition>
                    </div>
                  </div>
                </el-collapse-transition>
              </div>
            </div>
          </div>

          <!-- Empty clusters message -->
          <div v-if="clustersWithCompetencies.length === 0" class="no-clusters">
            <el-empty description="No role clusters with training modules found" />
          </div>
        </div>

        <!-- Continue Button -->
        <div class="action-buttons">
          <el-button @click="$emit('back')">
            <el-icon><ArrowLeft /></el-icon>
            Back to Task 1
          </el-button>
          <el-button
            type="primary"
            :disabled="confirmedCount < modules.length"
            @click="$emit('completed')"
          >
            Continue to Task 3
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>

        <p v-if="confirmedCount < modules.length" class="completion-hint">
          Please select and confirm a learning format for all {{ modules.length }} modules to continue.
        </p>
      </div>
    </template>

    <!-- Format Selector Dialog -->
    <FormatSelectorDialog
      v-model="showFormatDialog"
      :module="selectedModule"
      :organization-id="organizationId"
      @selected="handleFormatSelected"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading, InfoFilled, ArrowLeft, ArrowRight, Grid, UserFilled, User, Check
} from '@element-plus/icons-vue'
import axios from '@/api/axios'
import FormatSelectorDialog from './FormatSelectorDialog.vue'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  },
  selectedView: {
    type: String,
    default: 'competency_level'
  }
})

const emit = defineEmits(['completed', 'back'])

// State
const loading = ref(true)
const modules = ref([])
const scalingInfo = ref(null)
const strategyName = ref('')
const roleClusters = ref([])
const roleToClusterMap = ref({})
const expandedCompetencies = ref(new Set())
const expandedNestedCompetencies = ref(new Set())
const expandedModules = ref(new Set())
const showFormatDialog = ref(false)
const selectedModule = ref(null)

// Level name mapping
const levelNames = {
  1: 'Knowing',
  2: 'Understanding',
  4: 'Applying',
  6: 'Mastering'
}

const getLevelName = (level) => {
  return levelNames[level] || `Level ${level}`
}

// Computed
const confirmedCount = computed(() => {
  return modules.value.filter(m => m.confirmed).length
})

const uniqueRolesCount = computed(() => {
  const allRoles = new Set()
  modules.value.forEach(m => {
    (m.roles_needing_training || []).forEach(role => allRoles.add(role))
  })
  return allRoles.size
})

// Group modules by competency for Competency-Level view
const competencyGroups = computed(() => {
  const groups = {}

  modules.value.forEach(module => {
    const id = module.competency_id
    if (!groups[id]) {
      groups[id] = {
        competency_id: id,
        competency_name: module.competency_name,
        modules: [],
        levels: new Set()
      }
    }
    groups[id].modules.push(module)
    groups[id].levels.add(module.target_level)
  })

  // Convert to array and sort
  return Object.values(groups)
    .map(g => ({
      ...g,
      levels: Array.from(g.levels).sort((a, b) => a - b),
      confirmedCount: g.modules.filter(m => m.confirmed).length,
      modules: g.modules.sort((a, b) => {
        if (a.target_level !== b.target_level) return a.target_level - b.target_level
        return (a.pmt_type || '').localeCompare(b.pmt_type || '')
      })
    }))
    .sort((a, b) => a.competency_id - b.competency_id)
})

// Group by cluster -> competency for Role-Clustered view
// Backend now returns cluster-specific modules with cluster_id, so we group by that
const clustersWithCompetencies = computed(() => {
  if (props.selectedView !== 'role_clustered') {
    return []
  }

  // Group modules by their cluster_id (backend provides this for role_clustered view)
  const clusterGroups = {}

  modules.value.forEach(module => {
    const clusterId = module.cluster_id
    if (!clusterId) return  // Skip modules without cluster_id

    if (!clusterGroups[clusterId]) {
      clusterGroups[clusterId] = {
        id: clusterId,
        cluster_name: module.cluster_name,
        training_program_name: module.cluster_name,
        modules: [],
        competencyMap: {}
      }
    }

    clusterGroups[clusterId].modules.push(module)

    // Group by competency within cluster
    const compId = module.competency_id
    if (!clusterGroups[clusterId].competencyMap[compId]) {
      clusterGroups[clusterId].competencyMap[compId] = {
        competency_id: compId,
        competency_name: module.competency_name,
        modules: [],
        levels: new Set()
      }
    }
    clusterGroups[clusterId].competencyMap[compId].modules.push(module)
    clusterGroups[clusterId].competencyMap[compId].levels.add(module.target_level)
  })

  // Convert to array format
  return Object.values(clusterGroups)
    .map(cluster => {
      const competencies = Object.values(cluster.competencyMap)
        .map(g => ({
          ...g,
          levels: Array.from(g.levels).sort((a, b) => a - b),
          confirmedCount: g.modules.filter(m => m.confirmed).length,
          modules: g.modules.sort((a, b) => {
            if (a.target_level !== b.target_level) return a.target_level - b.target_level
            return (a.pmt_type || '').localeCompare(b.pmt_type || '')
          })
        }))
        .sort((a, b) => a.competency_id - b.competency_id)

      // Find matching roleCluster to get roles info
      const matchingRoleCluster = roleClusters.value.find(rc => rc.id === cluster.id)

      return {
        id: cluster.id,
        cluster_name: cluster.cluster_name,
        training_program_name: cluster.training_program_name,
        competencies,
        moduleCount: cluster.modules.length,
        role_count: matchingRoleCluster?.role_count || 0,
        roles: matchingRoleCluster?.roles || []
      }
    })
    .filter(cluster => cluster.competencies.length > 0)
    .sort((a, b) => a.id - b.id)
})

// Methods
const formatPmtType = (pmt) => {
  if (pmt === 'method') return 'Method'
  if (pmt === 'tool') return 'Tool'
  return 'Combined'
}

const toggleCompetency = (competencyId) => {
  if (expandedCompetencies.value.has(competencyId)) {
    expandedCompetencies.value.delete(competencyId)
  } else {
    expandedCompetencies.value.add(competencyId)
  }
  expandedCompetencies.value = new Set(expandedCompetencies.value) // Trigger reactivity
}

const toggleNestedCompetency = (key) => {
  if (expandedNestedCompetencies.value.has(key)) {
    expandedNestedCompetencies.value.delete(key)
  } else {
    expandedNestedCompetencies.value.add(key)
  }
  expandedNestedCompetencies.value = new Set(expandedNestedCompetencies.value)
}

const toggleModuleExpand = (key) => {
  if (expandedModules.value.has(key)) {
    expandedModules.value.delete(key)
  } else {
    expandedModules.value.add(key)
  }
  expandedModules.value = new Set(expandedModules.value)
}

// Filter roles to only include those belonging to a specific cluster
const getClusterRoles = (module, clusterId) => {
  const allRoles = module.roles_needing_training || []
  // Filter to only roles that belong to this cluster
  return allRoles.filter(roleName => roleToClusterMap.value[roleName] === clusterId)
}

const openFormatDialog = (module) => {
  selectedModule.value = module
  showFormatDialog.value = true
}

const loadData = async () => {
  loading.value = true
  try {
    // Pass view_type to get appropriate modules (cluster-specific for role_clustered)
    const viewType = props.selectedView || 'competency_level'
    const modulesResponse = await axios.get(
      `/api/phase3/training-modules/${props.organizationId}?view_type=${viewType}`
    )

    if (modulesResponse.data.success) {
      modules.value = modulesResponse.data.modules || []
      scalingInfo.value = modulesResponse.data.scaling_info
      strategyName.value = modulesResponse.data.strategy_name

      // Expand all competencies by default
      modules.value.forEach(m => {
        expandedCompetencies.value.add(m.competency_id)
      })
    }

    // Load role clusters for role-clustered view (for display info)
    if (props.selectedView === 'role_clustered') {
      const clustersResponse = await axios.get(`/api/phase3/training-clusters/${props.organizationId}/distribution`)
      if (clustersResponse.data.success) {
        const distribution = clustersResponse.data.distribution || []
        roleClusters.value = distribution.map(d => ({
          id: d.cluster_id,
          cluster_name: d.cluster_name,
          training_program_name: d.training_program_name,
          role_count: d.role_count,
          roles: d.role_titles || []
        }))

        // Build role -> cluster mapping
        const mapping = {}
        for (const cluster of roleClusters.value) {
          if (cluster.roles) {
            for (const roleName of cluster.roles) {
              mapping[roleName] = cluster.id
            }
          }
        }
        roleToClusterMap.value = mapping

        // Expand all nested competencies by default
        roleClusters.value.forEach(cluster => {
          modules.value.forEach(m => {
            expandedNestedCompetencies.value.add(`${cluster.id}_${m.competency_id}`)
          })
        })
      }
    }
  } catch (error) {
    console.error('Error loading training modules:', error)
    ElMessage.error('Failed to load training modules')
  } finally {
    loading.value = false
  }
}

const handleFormatSelected = async (selection) => {
  // Use selectedModule to find the correct module
  if (!selectedModule.value) return

  // For role_clustered view, also match by cluster_id
  const moduleIndex = modules.value.findIndex(m => {
    const basicMatch = m.competency_id === selectedModule.value.competency_id &&
                       m.target_level === selectedModule.value.target_level &&
                       m.pmt_type === selectedModule.value.pmt_type

    // If module has cluster_id, also match on that
    if (selectedModule.value.cluster_id) {
      return basicMatch && m.cluster_id === selectedModule.value.cluster_id
    }
    return basicMatch
  })

  if (moduleIndex !== -1) {
    // Create a new array to ensure Vue reactivity
    const updatedModules = [...modules.value]
    updatedModules[moduleIndex] = {
      ...updatedModules[moduleIndex],
      selected_format_id: selection.formatId,
      selected_format: selection.format,
      suitability: selection.suitability,
      confirmed: true
    }
    modules.value = updatedModules
  }

  if (confirmedCount.value === modules.value.length) {
    ElMessage.success('All modules configured! You can now continue to Task 3.')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.learning-format-selection {
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

/* Scaling Banner */
.scaling-banner {
  margin-bottom: 20px;
}

.banner-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.scaling-content p {
  margin: 0 0 12px 0;
}

.scaling-details {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.scaling-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.scaling-label {
  font-size: 13px;
  color: #606266;
}

.scaling-value {
  font-weight: 600;
  color: #303133;
}

.scaling-item.highlight .scaling-value {
  color: #409EFF;
  font-size: 16px;
}

/* View Indicator */
.view-indicator {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #F5F7FA;
  border-radius: 8px;
}

.view-indicator .el-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.strategy-badge {
  font-size: 13px;
  color: #E6A23C;
  font-weight: 500;
}

/* Progress Summary */
.progress-summary {
  display: flex;
  gap: 24px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #F5F7FA 0%, #E4E7ED 100%);
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Level Legend */
.level-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #FAFAFA;
  border: 1px solid #EBEEF5;
  border-radius: 6px;
  margin-bottom: 20px;
}

.legend-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.legend-items {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.legend-item .level-badge {
  font-size: 10px;
  padding: 2px 6px;
}

/* Competency Groups */
.competency-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.competency-group {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  background: white;
  overflow: hidden;
}

.competency-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #FAFAFA;
  cursor: pointer;
  transition: background 0.2s;
}

.competency-header:hover {
  background: #F5F7FA;
}

.competency-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.competency-title h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.expand-icon {
  transition: transform 0.2s;
  color: #909399;
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
}

.competency-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-badges {
  display: flex;
  gap: 4px;
}

.level-badge {
  padding: 2px 8px;
  background: #409EFF;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.competency-modules {
  border-top: 1px solid #EBEEF5;
}

/* Module Item (container for row + details) */
.module-item {
  border-bottom: 1px solid #F5F7FA;
}

.module-item:last-child {
  border-bottom: none;
}

.module-item.is-confirmed > .module-row {
  background: linear-gradient(to right, #F0F9EB 0%, white 30%);
}

/* Module Row */
.module-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.module-row:hover {
  background: #FAFAFA;
}

.module-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.module-level {
  font-weight: 600;
  color: #409EFF;
  min-width: 60px;
}

.module-pmt {
  padding: 2px 10px;
  background: #E4E7ED;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.module-participants {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.module-roles-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.more-roles {
  font-size: 11px;
  color: #909399;
}

/* Module Details (expandable section) */
.module-details {
  padding: 12px 16px 16px 40px;
  background: #FAFAFA;
  border-top: 1px dashed #E4E7ED;
}

.detail-section h5 {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.roles-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.roles-list .el-tag {
  margin: 0;
}

.no-roles {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

.module-format-select {
  min-width: 140px;
  text-align: right;
}

.format-selected {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #F0F9EB;
  border: 1px solid #67C23A;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.format-selected:hover {
  background: #E1F3D8;
}

.format-selected .format-name {
  font-size: 13px;
  color: #67C23A;
  font-weight: 500;
}

.format-selected .el-icon {
  color: #67C23A;
}

/* Role Clusters View */
.role-clusters-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.cluster-section {
  border: 2px solid #EBEEF5;
  border-radius: 12px;
  background: white;
  overflow: hidden;
}

.cluster-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #ECF5FF 0%, #F0F7FF 100%);
  border-bottom: 1px solid #D4E8FC;
}

.cluster-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cluster-title .el-icon {
  color: #409EFF;
}

.cluster-title h3 {
  margin: 0;
  font-size: 17px;
  color: #303133;
}

.cluster-meta {
  display: flex;
  gap: 8px;
}

.cluster-roles-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  background: #FAFAFA;
  border-bottom: 1px solid #EBEEF5;
}

.cluster-competencies {
  padding: 12px;
}

/* Nested Competency Groups */
.nested-competency-group {
  margin-bottom: 8px;
  border: 1px solid #EBEEF5;
  border-radius: 6px;
  overflow: hidden;
}

.nested-competency-group:last-child {
  margin-bottom: 0;
}

.nested-competency-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #F5F7FA;
  cursor: pointer;
}

.nested-competency-header:hover {
  background: #EBEEF5;
}

.nested-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.nested-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nested-modules {
  border-top: 1px solid #EBEEF5;
  background: white;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.completion-hint {
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-top: 12px;
}

.no-modules, .no-clusters {
  padding: 40px 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .progress-summary {
    flex-wrap: wrap;
    justify-content: center;
  }

  .module-row {
    flex-wrap: wrap;
    gap: 10px;
  }

  .module-info {
    flex-basis: 100%;
  }

  .module-roles-compact {
    flex-basis: 50%;
  }

  .module-format-select {
    flex-basis: 50%;
  }
}
</style>
