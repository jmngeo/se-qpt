<template>
  <div class="learning-format-selection">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading training modules...</p>
    </div>

    <template v-else>
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
        <!-- Info Section -->
        <div class="info-section">
          <!-- Scaled Participant Estimation Info Box -->
          <div v-if="scalingInfo" class="info-box scaling-info-box">
            <div class="info-box-header">
              <el-icon><TrendCharts /></el-icon>
              <h4>Scaled Participant Estimation</h4>
            </div>
            <ul class="info-points">
              <li>
                Only <strong>{{ scalingInfo.actual_assessed_users }} employees</strong> completed the assessment,
                but the target group has <strong>{{ scalingInfo.target_group_size }} employees</strong>.
              </li>
              <li>
                Participant counts are scaled by <strong>{{ scalingInfo.scaling_factor?.toFixed(1) }}x</strong>
                to estimate training needs for the full group.
              </li>
              <li class="note">
                Estimates may vary based on individual competency gaps across the full target group.
              </li>
            </ul>
          </div>

          <!-- Training Programs Info Box (only for role-clustered view) -->
          <div v-if="selectedView === 'role_clustered'" class="info-box programs-info-box">
            <div class="info-box-header">
              <el-icon><Suitcase /></el-icon>
              <h4>Training Programs</h4>
            </div>
            <ul class="info-points">
              <li>
                <strong>SE for Engineers:</strong> Roles needing Applying/Mastering in <em>Technical</em> or <em>Core SE</em> areas.
                Includes Common Base + Role-Specific Pathways.
              </li>
              <li>
                <strong>SE for Managers:</strong> Roles needing Applying/Mastering <em>only</em> in <em>Social/Personal</em> or <em>Management</em> areas.
              </li>
              <li>
                <strong>SE for Interfacing Partners:</strong> Roles needing only Knowing/Understanding level competency.
              </li>
            </ul>
          </div>
        </div>

        <!-- Stats and Legend Bar -->
        <div class="stats-legend-bar">
          <div class="progress-stats">
            <div class="stat-item">
              <span class="stat-value">{{ competencyGroups.length }}</span>
              <span class="stat-label">Competencies</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ modules.length }}</span>
              <span class="stat-label">Modules</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ confirmedCount }}</span>
              <span class="stat-label">Confirmed</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ uniqueRolesCount }}</span>
              <span class="stat-label">Roles</span>
            </div>
          </div>
          <div class="level-legend">
            <span class="legend-label">Levels:</span>
            <span class="legend-item"><span class="level-badge l1">Knowing</span></span>
            <span class="legend-item"><span class="level-badge l2">Understanding</span></span>
            <span class="legend-item"><span class="level-badge l4">Applying</span></span>
            <span class="legend-item"><span class="level-badge l6">Mastering</span></span>
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
                  <span v-for="level in group.levels" :key="level" class="level-badge" :class="`l${level}`">
                    {{ getLevelName(level) }}
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

        <!-- Training Packages View (Role-Clustered) -->
        <div v-else class="training-packages-view">
          <div
            v-for="pkg in trainingPackages"
            :key="pkg.id"
            class="training-package"
            :class="getPackageClass(pkg.id)"
          >
            <!-- Package Header -->
            <div class="package-header" :class="getPackageHeaderClass(pkg.id)">
              <div class="package-icon">
                <el-icon :size="32"><Suitcase /></el-icon>
              </div>
              <div class="package-info">
                <h3>{{ pkg.training_program_name }}</h3>
                <p class="package-subtitle">{{ getPackageSubtitle(pkg.id) }}</p>
              </div>
              <div class="package-stats">
                <div class="stat">
                  <span class="stat-value">{{ pkg.moduleCount }}</span>
                  <span class="stat-label">Modules</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ pkg.role_count }}</span>
                  <span class="stat-label">Roles</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ getPackageConfirmedCount(pkg) }}/{{ pkg.moduleCount }}</span>
                  <span class="stat-label">Confirmed</span>
                </div>
              </div>
            </div>

            <!-- Roles included in this package -->
            <div class="package-roles">
              <span class="roles-label">Roles:</span>
              <el-tag
                v-for="role in pkg.roles?.slice(0, 6)"
                :key="role"
                size="small"
                effect="plain"
              >{{ role }}</el-tag>
              <el-popover
                v-if="pkg.roles?.length > 6"
                placement="bottom"
                :width="300"
                trigger="click"
              >
                <template #reference>
                  <el-tag size="small" type="info" class="more-roles-tag" style="cursor: pointer;">
                    +{{ pkg.roles.length - 6 }} more
                  </el-tag>
                </template>
                <div class="roles-popover">
                  <div class="popover-title">All Roles in Package ({{ pkg.roles.length }})</div>
                  <div class="popover-roles-list">
                    <el-tag
                      v-for="role in pkg.roles"
                      :key="role"
                      size="small"
                      effect="plain"
                    >{{ role }}</el-tag>
                  </div>
                </div>
              </el-popover>
            </div>

            <!-- Engineers Package: Show Common Base + Pathways -->
            <template v-if="pkg.id === 1 && pkg.hasSubclusters">
              <!-- Common Base Section -->
              <div class="subcluster-section common-base">
                <div class="subcluster-header">
                  <el-icon><Connection /></el-icon>
                  <h4>Common Base</h4>
                  <span class="subcluster-desc">Modules shared by 2+ engineering roles (group training opportunities)</span>
                </div>
                <div class="subcluster-modules">
                  <template v-for="compGroup in pkg.commonCompetencies" :key="`common_${compGroup.competency_id}`">
                    <div class="compact-module-group">
                      <div class="compact-competency-name">{{ compGroup.competency_name }}</div>
                      <div class="compact-modules-row">
                        <el-popover
                          v-for="module in compGroup.modules"
                          :key="`common_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                          placement="top"
                          :width="280"
                          trigger="hover"
                        >
                          <template #reference>
                            <div
                              class="compact-module"
                              :class="{ 'is-confirmed': module.confirmed }"
                              @click="openFormatDialog(module)"
                            >
                              <span class="compact-level">{{ getLevelName(module.target_level) }}</span>
                              <span v-if="module.pmt_type !== 'combined'" class="compact-pmt">{{ formatPmtType(module.pmt_type) }}</span>
                              <span class="shared-badge">{{ module.shared_roles_count || (module.roles_needing_training || []).length }} roles</span>
                              <el-icon v-if="module.confirmed" class="confirmed-icon"><Check /></el-icon>
                            </div>
                          </template>
                          <div class="module-tooltip">
                            <div class="tooltip-title">Shared by {{ module.shared_roles_count || (module.roles_needing_training || []).length }} roles:</div>
                            <div class="tooltip-roles">
                              <el-tag v-for="role in (module.roles_needing_training || [])" :key="role" size="small" effect="plain">
                                {{ role }}
                              </el-tag>
                            </div>
                            <div class="tooltip-participants">{{ module.estimated_participants }} estimated participants</div>
                          </div>
                        </el-popover>
                      </div>
                    </div>
                  </template>
                  <div v-if="pkg.commonCompetencies?.length === 0" class="no-common-modules">
                    No shared modules found - all modules are role-specific
                  </div>
                </div>
              </div>

              <!-- Role-Specific Pathways Section -->
              <div class="subcluster-section pathways">
                <div class="subcluster-header">
                  <el-icon><Aim /></el-icon>
                  <h4>Role-Specific Pathways</h4>
                  <span class="subcluster-desc">Specialized modules for specific engineering roles</span>
                </div>
                <div class="pathways-content">
                  <template v-for="compGroup in pkg.pathwayCompetencies" :key="`pathway_${compGroup.competency_id}`">
                    <div class="pathway-module-group">
                      <div class="pathway-competency-header" @click="toggleNestedCompetency(`pathway_${pkg.id}_${compGroup.competency_id}`)">
                        <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`pathway_${pkg.id}_${compGroup.competency_id}`) }">
                          <ArrowRight />
                        </el-icon>
                        <span class="pathway-competency-name">{{ compGroup.competency_name }}</span>
                        <div class="pathway-meta">
                          <span class="level-badges">
                            <span v-for="level in compGroup.levels" :key="level" class="level-badge small" :class="`l${level}`">{{ getLevelName(level) }}</span>
                          </span>
                          <el-tag size="small" :type="compGroup.confirmedCount === compGroup.modules.length ? 'success' : 'info'">
                            {{ compGroup.confirmedCount }}/{{ compGroup.modules.length }}
                          </el-tag>
                        </div>
                      </div>
                      <el-collapse-transition>
                        <div v-show="expandedNestedCompetencies.has(`pathway_${pkg.id}_${compGroup.competency_id}`)" class="pathway-modules">
                          <div
                            v-for="module in compGroup.modules"
                            :key="`pathway_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                            class="module-item pathway-module"
                            :class="{ 'is-confirmed': module.confirmed }"
                          >
                            <div class="module-row">
                              <div class="module-info">
                                <span class="module-level">{{ getLevelName(module.target_level) }}</span>
                                <span v-if="module.pmt_type !== 'combined'" class="module-pmt">{{ formatPmtType(module.pmt_type) }}</span>
                                <span class="module-participants">
                                  <el-icon><User /></el-icon>
                                  {{ module.estimated_participants }}
                                </span>
                                <div class="pathway-roles-indicator">
                                  <el-tag v-for="role in (module.pathway_roles || module.roles_needing_training || []).slice(0, 2)" :key="role" size="small" type="warning" effect="plain">
                                    {{ role }}
                                  </el-tag>
                                  <el-popover
                                    v-if="(module.pathway_roles || module.roles_needing_training || []).length > 2"
                                    placement="top"
                                    :width="280"
                                    trigger="click"
                                  >
                                    <template #reference>
                                      <el-tag size="small" type="info" class="more-roles-tag" style="cursor: pointer;">
                                        +{{ (module.pathway_roles || module.roles_needing_training || []).length - 2 }}
                                      </el-tag>
                                    </template>
                                    <div class="roles-popover">
                                      <div class="popover-title">Roles Needing This Module</div>
                                      <div class="popover-roles-list">
                                        <el-tag
                                          v-for="role in (module.pathway_roles || module.roles_needing_training || [])"
                                          :key="role"
                                          size="small"
                                          effect="plain"
                                          type="warning"
                                        >{{ role }}</el-tag>
                                      </div>
                                    </div>
                                  </el-popover>
                                </div>
                              </div>
                              <div class="module-format-select" @click.stop>
                                <div v-if="module.selected_format" class="format-selected" @click="openFormatDialog(module)">
                                  <span class="format-name">{{ module.selected_format.short_name }}</span>
                                  <el-icon><Check /></el-icon>
                                </div>
                                <el-button v-else size="small" type="primary" plain @click="openFormatDialog(module)">
                                  Select
                                </el-button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </el-collapse-transition>
                    </div>
                  </template>
                  <div v-if="pkg.pathwayCompetencies?.length === 0" class="no-pathway-modules">
                    No role-specific modules - all modules are common
                  </div>
                </div>
              </div>
            </template>

            <!-- Non-Engineers Packages: Standard competency list -->
            <template v-else>
              <div class="package-competencies">
                <div
                  v-for="compGroup in pkg.competencies"
                  :key="`${pkg.id}_${compGroup.competency_id}`"
                  class="nested-competency-group"
                >
                  <div
                    class="nested-competency-header"
                    @click="toggleNestedCompetency(`${pkg.id}_${compGroup.competency_id}`)"
                  >
                    <div class="nested-title">
                      <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`${pkg.id}_${compGroup.competency_id}`) }">
                        <ArrowRight />
                      </el-icon>
                      <span>{{ compGroup.competency_name }}</span>
                    </div>
                    <div class="nested-meta">
                      <span class="level-badges">
                        <span v-for="level in compGroup.levels" :key="level" class="level-badge" :class="`l${level}`">{{ getLevelName(level) }}</span>
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
                      v-show="expandedNestedCompetencies.has(`${pkg.id}_${compGroup.competency_id}`)"
                      class="nested-modules"
                    >
                      <div
                        v-for="module in compGroup.modules"
                        :key="`${pkg.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                        class="module-item"
                        :class="{ 'is-confirmed': module.confirmed }"
                      >
                        <div class="module-row" @click="toggleModuleExpand(`${pkg.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`)">
                          <div class="module-info">
                            <el-icon class="expand-icon" :class="{ 'is-expanded': expandedModules.has(`${pkg.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`) }">
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
                          <div v-show="expandedModules.has(`${pkg.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`)" class="module-details">
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
            </template>
          </div>

          <!-- Empty packages message -->
          <div v-if="trainingPackages.length === 0" class="no-clusters">
            <el-empty description="No training packages with modules found" />
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
  Loading, InfoFilled, ArrowLeft, ArrowRight, Grid, UserFilled, User, Check,
  Suitcase, Connection, Aim, TrendCharts, Right, Warning
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

// Group by cluster -> competency for Role-Clustered view (Training Packages)
// Backend now returns cluster-specific modules with cluster_id and subcluster info
const trainingPackages = computed(() => {
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
        competencyMap: {},
        // For Engineers: separate common vs pathway modules
        commonModules: [],
        pathwayModules: []
      }
    }

    clusterGroups[clusterId].modules.push(module)

    // For Engineers cluster (id=1), separate by subcluster
    if (clusterId === 1 && module.subcluster) {
      if (module.subcluster === 'common') {
        clusterGroups[clusterId].commonModules.push(module)
      } else if (module.subcluster === 'pathway') {
        clusterGroups[clusterId].pathwayModules.push(module)
      }
    }

    // Group by competency within cluster (for standard view)
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

      // For Engineers: Create competency groups for common and pathway modules
      const hasSubclusters = cluster.id === 1 && (cluster.commonModules.length > 0 || cluster.pathwayModules.length > 0)

      let commonCompetencies = []
      let pathwayCompetencies = []

      if (hasSubclusters) {
        // Group common modules by competency
        const commonByComp = {}
        cluster.commonModules.forEach(m => {
          if (!commonByComp[m.competency_id]) {
            commonByComp[m.competency_id] = {
              competency_id: m.competency_id,
              competency_name: m.competency_name,
              modules: [],
              levels: new Set()
            }
          }
          commonByComp[m.competency_id].modules.push(m)
          commonByComp[m.competency_id].levels.add(m.target_level)
        })
        commonCompetencies = Object.values(commonByComp)
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

        // Group pathway modules by competency
        const pathwayByComp = {}
        cluster.pathwayModules.forEach(m => {
          if (!pathwayByComp[m.competency_id]) {
            pathwayByComp[m.competency_id] = {
              competency_id: m.competency_id,
              competency_name: m.competency_name,
              modules: [],
              levels: new Set()
            }
          }
          pathwayByComp[m.competency_id].modules.push(m)
          pathwayByComp[m.competency_id].levels.add(m.target_level)
        })
        pathwayCompetencies = Object.values(pathwayByComp)
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
      }

      return {
        id: cluster.id,
        cluster_name: cluster.cluster_name,
        training_program_name: cluster.training_program_name,
        competencies,
        moduleCount: cluster.modules.length,
        role_count: matchingRoleCluster?.role_count || 0,
        roles: matchingRoleCluster?.roles || [],
        // Engineers subcluster data
        hasSubclusters,
        commonCompetencies,
        pathwayCompetencies,
        commonModuleCount: cluster.commonModules.length,
        pathwayModuleCount: cluster.pathwayModules.length
      }
    })
    .filter(cluster => cluster.competencies.length > 0)
    .sort((a, b) => a.id - b.id)
})

// Keep old name as alias for backward compatibility
const clustersWithCompetencies = trainingPackages

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

// Training Package helper methods
const getPackageClass = (pkgId) => {
  switch (pkgId) {
    case 1: return 'package-engineers'
    case 2: return 'package-managers'
    case 3: return 'package-partners'
    default: return ''
  }
}

const getPackageHeaderClass = (pkgId) => {
  switch (pkgId) {
    case 1: return 'header-engineers'
    case 2: return 'header-managers'
    case 3: return 'header-partners'
    default: return ''
  }
}

const getPackageSubtitle = (pkgId) => {
  switch (pkgId) {
    case 1: return 'Technical & Core competencies at Applying/Mastering levels'
    case 2: return 'Management & Social competencies focus'
    case 3: return 'Basic awareness (Knowing/Understanding) modules'
    default: return ''
  }
}

const getPackageConfirmedCount = (pkg) => {
  return pkg.competencies.reduce((sum, comp) => sum + comp.confirmedCount, 0)
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

/* Info Section */
.info-section {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.info-box {
  flex: 1;
  background: #F8F9FA;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 12px 16px;
}

.info-box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-box-header .el-icon {
  font-size: 16px;
}

.scaling-info-box .info-box-header .el-icon {
  color: #409EFF;
}

.programs-info-box .info-box-header .el-icon {
  color: #67C23A;
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

.info-points li:last-child {
  margin-bottom: 0;
}

.info-points li strong {
  color: #303133;
}

.info-points li em {
  font-style: normal;
  color: #909399;
}

.info-points li.note {
  color: #909399;
  font-style: italic;
}

/* Stats and Legend Bar */
.stats-legend-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #F5F7FA;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  margin-bottom: 16px;
}

.progress-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-item .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
}

.level-legend {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-label {
  font-size: 12px;
  color: #909399;
  margin-right: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
}

.legend-item .level-badge {
  font-size: 10px;
  padding: 2px 8px;
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

/* Level-specific colors */
.level-badge.l1 { background: #909399; }  /* Knowing - Gray */
.level-badge.l2 { background: #E6A23C; }  /* Understanding - Orange */
.level-badge.l4 { background: #409EFF; }  /* Applying - Blue */
.level-badge.l6 { background: #67C23A; }  /* Mastering - Green */

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

/* ==========================================
   Training Packages View (Role-Clustered)
   ========================================== */
.training-packages-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.training-package {
  border: 2px solid #DCDFE6;
  border-radius: 16px;
  background: white;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Package Color Variants */
.package-engineers {
  border-color: #409EFF;
}

.package-managers {
  border-color: #E6A23C;
}

.package-partners {
  border-color: #67C23A;
}

/* Package Header */
.package-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #F5F7FA 0%, #EBEEF5 100%);
}

.header-engineers {
  background: linear-gradient(135deg, #ECF5FF 0%, #D9ECFF 100%);
}

.header-managers {
  background: linear-gradient(135deg, #FDF6EC 0%, #FAECD8 100%);
}

.header-partners {
  background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%);
}

.package-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.package-engineers .package-icon {
  color: #409EFF;
}

.package-managers .package-icon {
  color: #E6A23C;
}

.package-partners .package-icon {
  color: #67C23A;
}

.package-info {
  flex: 1;
}

.package-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.package-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.package-stats {
  display: flex;
  gap: 20px;
}

.package-stats .stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.package-stats .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.package-stats .stat-label {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
}

/* Package Roles */
.package-roles {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #FAFAFA;
  border-bottom: 1px solid #EBEEF5;
}

.roles-label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-right: 4px;
}

/* Package Competencies (standard view) */
.package-competencies {
  padding: 16px;
}

/* Subcluster Sections (Engineers package) */
.subcluster-section {
  margin: 16px;
  border: 1px solid #EBEEF5;
  border-radius: 12px;
  overflow: hidden;
}

.subcluster-section.common-base {
  border-color: #B3D8FF;
  background: #F5FAFF;
}

.subcluster-section.pathways {
  border-color: #FAECD8;
  background: #FFFDF5;
}

.subcluster-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: white;
  border-bottom: 1px solid #EBEEF5;
}

.common-base .subcluster-header {
  background: linear-gradient(to right, #ECF5FF 0%, white 100%);
}

.pathways .subcluster-header {
  background: linear-gradient(to right, #FDF6EC 0%, white 100%);
}

.subcluster-header .el-icon {
  color: #409EFF;
}

.pathways .subcluster-header .el-icon {
  color: #E6A23C;
}

.subcluster-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.subcluster-desc {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

/* Compact Module Display (Common Base) */
.subcluster-modules {
  padding: 12px 16px;
}

.compact-module-group {
  margin-bottom: 12px;
}

.compact-module-group:last-child {
  margin-bottom: 0;
}

.compact-competency-name {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.compact-modules-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.compact-module {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.compact-module:hover {
  border-color: #409EFF;
  background: #ECF5FF;
}

.compact-module.is-confirmed {
  border-color: #67C23A;
  background: #F0F9EB;
}

.compact-level {
  font-weight: 600;
  color: #409EFF;
  font-size: 11px;
  background: #ECF5FF;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.compact-pmt {
  font-size: 11px;
  color: #909399;
  padding: 1px 6px;
  background: #F5F7FA;
  border-radius: 3px;
}

.compact-participants {
  font-size: 11px;
  color: #606266;
}

.compact-module .confirmed-icon {
  color: #67C23A;
  font-size: 14px;
}

.no-common-modules, .no-pathway-modules {
  padding: 16px;
  text-align: center;
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

/* Pathway Module Groups */
.pathways-content {
  padding: 8px;
}

.pathway-module-group {
  margin-bottom: 8px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  overflow: hidden;
}

.pathway-module-group:last-child {
  margin-bottom: 0;
}

.pathway-competency-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #FAFAFA;
  cursor: pointer;
}

.pathway-competency-header:hover {
  background: #F5F7FA;
}

.pathway-competency-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.pathway-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pathway-modules {
  border-top: 1px solid #EBEEF5;
  background: white;
}

.pathway-module {
  border-bottom: 1px solid #F5F7FA;
}

.pathway-module:last-child {
  border-bottom: none;
}

.pathway-roles-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
}

.level-badge.small {
  padding: 1px 5px;
  font-size: 10px;
}

/* Roles Popover Styles */
.more-roles-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.more-roles-tag:hover {
  background-color: #409EFF;
  color: white;
  border-color: #409EFF;
}

.roles-popover {
  max-height: 300px;
  overflow-y: auto;
}

.popover-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #EBEEF5;
}

.popover-roles-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.popover-roles-list .el-tag {
  margin: 0;
}

/* Shared Badge for Common Base modules */
.shared-badge {
  font-size: 10px;
  color: #909399;
  background: #F5F7FA;
  padding: 2px 6px;
  border-radius: 10px;
  white-space: nowrap;
}

.compact-module.is-confirmed .shared-badge {
  background: #E1F3D8;
  color: #67C23A;
}

/* Module Tooltip (hover info for Common Base modules) */
.module-tooltip {
  padding: 4px 0;
}

.tooltip-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.tooltip-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tooltip-roles .el-tag {
  margin: 0;
}

.tooltip-participants {
  font-size: 12px;
  color: #909399;
  padding-top: 8px;
  border-top: 1px solid #EBEEF5;
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
