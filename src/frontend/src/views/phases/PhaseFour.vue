<template>
  <div class="phase-four">
    <!-- Phase Header -->
    <div class="phase-header">
      <div class="phase-indicator">
        <div class="phase-number">4</div>
        <div class="phase-title">
          <h1>Phase 4: Micro Planning</h1>
          <p>AVIVA Didactics Planning</p>
        </div>
      </div>

      <!-- Overall Progress -->
      <div class="phase-progress">
        <el-progress
          :percentage="overallProgress"
          :color="progressColors"
          :stroke-width="10"
        />
        <span class="progress-text">{{ overallProgress }}% Complete</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>Loading Phase 4 configuration...</p>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Dashboard View: Task Overview -->
      <div v-if="!activeTask" class="dashboard-view">
        <div class="tasks-overview">
          <h2>Phase 4 Tasks</h2>
          <p class="tasks-description">
            Complete AVIVA didactics planning for your training modules and export the final RFP document.
          </p>
        </div>

        <div class="task-cards">
          <!-- Task 1: AVIVA Didactics -->
          <div
            class="task-card"
            :class="{ 'completed': config.task1_status === 'completed', 'active': config.task1_status !== 'completed' }"
            @click="setActiveTask('aviva')"
          >
            <div class="task-icon">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="task-content">
              <h3>Task 1: AVIVA Didactics</h3>
              <p>Generate didactic plans for each training module</p>
              <div class="task-status">
                <el-tag v-if="config.task1_status === 'completed'" type="success" effect="plain">
                  <el-icon><View /></el-icon> View / Export
                </el-tag>
                <el-tag v-else type="primary" effect="plain">
                  <el-icon><ArrowRight /></el-icon> Start
                </el-tag>
              </div>
              <div v-if="statistics.total_modules > 0" class="task-result">
                {{ statistics.total_modules }} training modules from Phase 3
              </div>
            </div>
          </div>

          <!-- Task 2: RFP Export -->
          <div
            class="task-card"
            :class="{ 'completed': config.task2_status === 'completed', 'active': config.task2_status !== 'completed' }"
            @click="setActiveTask('rfp')"
          >
            <div class="task-icon">
              <el-icon :size="32"><Download /></el-icon>
            </div>
            <div class="task-content">
              <h3>Task 2: RFP Document Export</h3>
              <p>Export comprehensive Request for Proposal document</p>
              <div class="task-status">
                <el-tag v-if="config.task2_status === 'completed'" type="success" effect="plain">
                  <el-icon><View /></el-icon> View / Export
                </el-tag>
                <el-tag v-else type="primary" effect="plain">
                  <el-icon><ArrowRight /></el-icon> Start
                </el-tag>
              </div>
              <div v-if="statistics.total_modules > 0" class="task-result">
                Consolidate all Phase 1-4 data into RFP document
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AVIVA Planning View -->
      <div v-else-if="activeTask === 'aviva'" class="aviva-planning-view">
        <!-- Back Button and Header -->
        <div class="view-header">
          <el-button @click="activeTask = null" text>
            <el-icon><ArrowLeft /></el-icon>
            Back to Overview
          </el-button>
          <h2>AVIVA Didactics Planning</h2>
        </div>

        <!-- No Modules Message -->
        <div v-if="modules.length === 0" class="no-modules">
          <el-empty description="No training modules available">
            <template #description>
              <p>No confirmed training modules were found.</p>
              <p class="hint">Complete Phase 3 module format selection to see modules here.</p>
            </template>
          </el-empty>
        </div>

        <!-- Modules List -->
        <div v-else class="modules-container">
          <!-- Info Section -->
          <div class="info-section">
            <!-- Scaling Info Box -->
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
              </ul>
            </div>

            <!-- Training Programs Info Box (only for role-clustered view) -->
            <div v-if="viewType === 'role_clustered'" class="info-box programs-info-box">
              <div class="info-box-header">
                <el-icon><Suitcase /></el-icon>
                <h4>Training Programs</h4>
              </div>
              <ul class="info-points">
                <li>
                  <strong>SE for Engineers:</strong> Roles needing Applying/Mastering in <em>Technical</em> or <em>Core SE</em> areas.
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

          <!-- Stats Bar -->
          <div class="stats-legend-bar">
            <div class="progress-stats">
              <div class="stat-item">
                <span class="stat-value">{{ modules.length }}</span>
                <span class="stat-label">Modules</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ statistics.total_duration_hours }}h</span>
                <span class="stat-label">Total Duration</span>
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

          <!-- Training Packages View (Role-Clustered) -->
          <div v-if="viewType === 'role_clustered'" class="training-packages-view">
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
                  <h3>{{ pkg.cluster_name }}</h3>
                  <p class="package-subtitle">{{ getPackageSubtitle(pkg.id) }}</p>
                </div>
                <div class="package-stats">
                  <div class="stat">
                    <span class="stat-value">{{ pkg.moduleCount }}</span>
                    <span class="stat-label">Modules</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ pkg.totalDuration }}h</span>
                    <span class="stat-label">Duration</span>
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
                <el-tag v-if="pkg.roles?.length > 6" size="small" type="info">
                  +{{ pkg.roles.length - 6 }} more
                </el-tag>
              </div>

              <!-- Engineers Package: Show Common Base + Pathways -->
              <template v-if="pkg.id === 1 && pkg.hasSubclusters">
                <!-- Common Base Section -->
                <div class="subcluster-section common-base">
                  <div class="subcluster-header">
                    <el-icon><Connection /></el-icon>
                    <h4>Common Base</h4>
                    <span class="subcluster-count">{{ pkg.commonModuleCount }} modules</span>
                    <span class="subcluster-desc">Shared by 2+ engineering roles</span>
                  </div>
                  <div class="subcluster-modules">
                    <template v-for="compGroup in pkg.commonCompetencies" :key="`common_${compGroup.competency_id}`">
                      <div class="module-group">
                        <div class="module-group-header" @click="toggleNestedCompetency(`common_${pkg.id}_${compGroup.competency_id}`)">
                          <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`common_${pkg.id}_${compGroup.competency_id}`) }">
                            <ArrowRight />
                          </el-icon>
                          <span class="group-name">{{ compGroup.competency_name }}</span>
                          <div class="group-meta">
                            <span class="level-badges">
                              <span v-for="level in compGroup.levels" :key="level" class="level-badge small" :class="`l${level}`">
                                {{ getLevelName(level) }}
                              </span>
                            </span>
                            <span class="module-count">{{ compGroup.modules.length }} module(s)</span>
                          </div>
                        </div>
                        <el-collapse-transition>
                          <div v-show="expandedNestedCompetencies.has(`common_${pkg.id}_${compGroup.competency_id}`)" class="module-list">
                            <div
                              v-for="module in compGroup.modules"
                              :key="`common_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                              class="module-item"
                              @click="showModuleDetails(module)"
                            >
                              <div class="module-main">
                                <span class="level-badge" :class="`l${module.target_level}`">{{ getLevelName(module.target_level) }}</span>
                                <span v-if="module.pmt_type !== 'combined'" class="pmt-badge">{{ formatPmtType(module.pmt_type) }}</span>
                                <span class="module-name">{{ module.module_name }}</span>
                              </div>
                              <div class="module-meta">
                                <span class="duration"><el-icon><Clock /></el-icon> {{ module.estimated_duration_hours }}h</span>
                                <span class="participants"><el-icon><User /></el-icon> {{ module.estimated_participants }}</span>
                                <span class="roles-count">{{ module.shared_roles_count || (module.roles_needing_training || []).length }} roles</span>
                              </div>
                            </div>
                          </div>
                        </el-collapse-transition>
                      </div>
                    </template>
                  </div>
                </div>

                <!-- Role-Specific Pathways Section -->
                <div class="subcluster-section pathways">
                  <div class="subcluster-header">
                    <el-icon><Aim /></el-icon>
                    <h4>Role-Specific Pathways</h4>
                    <span class="subcluster-count">{{ pkg.pathwayModuleCount }} modules</span>
                    <span class="subcluster-desc">Specialized for specific roles</span>
                  </div>
                  <div class="subcluster-modules">
                    <template v-for="compGroup in pkg.pathwayCompetencies" :key="`pathway_${compGroup.competency_id}`">
                      <div class="module-group">
                        <div class="module-group-header" @click="toggleNestedCompetency(`pathway_${pkg.id}_${compGroup.competency_id}`)">
                          <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`pathway_${pkg.id}_${compGroup.competency_id}`) }">
                            <ArrowRight />
                          </el-icon>
                          <span class="group-name">{{ compGroup.competency_name }}</span>
                          <div class="group-meta">
                            <span class="level-badges">
                              <span v-for="level in compGroup.levels" :key="level" class="level-badge small" :class="`l${level}`">
                                {{ getLevelName(level) }}
                              </span>
                            </span>
                            <span class="module-count">{{ compGroup.modules.length }} module(s)</span>
                          </div>
                        </div>
                        <el-collapse-transition>
                          <div v-show="expandedNestedCompetencies.has(`pathway_${pkg.id}_${compGroup.competency_id}`)" class="module-list">
                            <div
                              v-for="module in compGroup.modules"
                              :key="`pathway_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                              class="module-item"
                              @click="showModuleDetails(module)"
                            >
                              <div class="module-main">
                                <span class="level-badge" :class="`l${module.target_level}`">{{ getLevelName(module.target_level) }}</span>
                                <span v-if="module.pmt_type !== 'combined'" class="pmt-badge">{{ formatPmtType(module.pmt_type) }}</span>
                                <span class="module-name">{{ module.module_name }}</span>
                              </div>
                              <div class="module-meta">
                                <span class="duration"><el-icon><Clock /></el-icon> {{ module.estimated_duration_hours }}h</span>
                                <span class="participants"><el-icon><User /></el-icon> {{ module.estimated_participants }}</span>
                                <div class="pathway-roles">
                                  <el-tag v-for="role in (module.pathway_roles || module.roles_needing_training || []).slice(0, 2)" :key="role" size="small" type="warning" effect="plain">
                                    {{ role }}
                                  </el-tag>
                                  <span v-if="(module.pathway_roles || module.roles_needing_training || []).length > 2" class="more-roles">
                                    +{{ (module.pathway_roles || module.roles_needing_training || []).length - 2 }}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </el-collapse-transition>
                      </div>
                    </template>
                  </div>
                </div>
              </template>

              <!-- Non-Engineers Packages: Standard competency list -->
              <template v-else>
                <div class="package-competencies">
                  <div
                    v-for="compGroup in pkg.competencies"
                    :key="`${pkg.id}_${compGroup.competency_id}`"
                    class="module-group"
                  >
                    <div class="module-group-header" @click="toggleNestedCompetency(`${pkg.id}_${compGroup.competency_id}`)">
                      <el-icon class="expand-icon" :class="{ 'is-expanded': expandedNestedCompetencies.has(`${pkg.id}_${compGroup.competency_id}`) }">
                        <ArrowRight />
                      </el-icon>
                      <span class="group-name">{{ compGroup.competency_name }}</span>
                      <div class="group-meta">
                        <span class="level-badges">
                          <span v-for="level in compGroup.levels" :key="level" class="level-badge small" :class="`l${level}`">
                            {{ getLevelName(level) }}
                          </span>
                        </span>
                        <span class="module-count">{{ compGroup.modules.length }} module(s)</span>
                      </div>
                    </div>
                    <el-collapse-transition>
                      <div v-show="expandedNestedCompetencies.has(`${pkg.id}_${compGroup.competency_id}`)" class="module-list">
                        <div
                          v-for="module in compGroup.modules"
                          :key="`${pkg.id}_${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                          class="module-item"
                          @click="showModuleDetails(module)"
                        >
                          <div class="module-main">
                            <span class="level-badge" :class="`l${module.target_level}`">{{ getLevelName(module.target_level) }}</span>
                            <span v-if="module.pmt_type !== 'combined'" class="pmt-badge">{{ formatPmtType(module.pmt_type) }}</span>
                            <span class="module-name">{{ module.module_name }}</span>
                          </div>
                          <div class="module-meta">
                            <span class="duration"><el-icon><Clock /></el-icon> {{ module.estimated_duration_hours }}h</span>
                            <span class="participants"><el-icon><User /></el-icon> {{ module.estimated_participants }}</span>
                            <span class="roles-count">{{ (module.roles_needing_training || []).length }} roles</span>
                          </div>
                        </div>
                      </div>
                    </el-collapse-transition>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- Competency-Level Based View -->
          <div v-else class="competency-groups">
            <div
              v-for="group in competencyGroups"
              :key="group.competency_id"
              class="module-group"
            >
              <div class="module-group-header" @click="toggleCompetency(group.competency_id)">
                <el-icon class="expand-icon" :class="{ 'is-expanded': expandedCompetencies.has(group.competency_id) }">
                  <ArrowRight />
                </el-icon>
                <span class="group-name">{{ group.competency_name }}</span>
                <div class="group-meta">
                  <span class="level-badges">
                    <span v-for="level in group.levels" :key="level" class="level-badge small" :class="`l${level}`">
                      {{ getLevelName(level) }}
                    </span>
                  </span>
                  <span class="module-count">{{ group.modules.length }} module(s)</span>
                </div>
              </div>
              <el-collapse-transition>
                <div v-show="expandedCompetencies.has(group.competency_id)" class="module-list">
                  <div
                    v-for="module in group.modules"
                    :key="`${module.competency_id}_${module.target_level}_${module.pmt_type}`"
                    class="module-item"
                    @click="showModuleDetails(module)"
                  >
                    <div class="module-main">
                      <span class="level-badge" :class="`l${module.target_level}`">{{ getLevelName(module.target_level) }}</span>
                      <span v-if="module.pmt_type !== 'combined'" class="pmt-badge">{{ formatPmtType(module.pmt_type) }}</span>
                      <span class="module-name">{{ module.module_name }}</span>
                    </div>
                    <div class="module-meta">
                      <span class="duration"><el-icon><Clock /></el-icon> {{ module.estimated_duration_hours }}h</span>
                      <span class="participants"><el-icon><User /></el-icon> {{ module.estimated_participants }}</span>
                      <span class="roles-count">{{ (module.roles_needing_training || []).length }} roles</span>
                    </div>
                  </div>
                </div>
              </el-collapse-transition>
            </div>
          </div>

          <!-- Export Options Card (Floating) -->
          <div class="export-panel">
            <div class="export-panel-header">
              <div class="export-title">
                <el-icon class="export-icon"><Download /></el-icon>
                <div>
                  <h3>Export AVIVA Plans</h3>
                  <p class="export-subtitle">Generate didactic plans for all training modules</p>
                </div>
              </div>
              <div class="export-stats">
                <div class="stat-pill">
                  <span class="stat-number">{{ modules.length }}</span>
                  <span class="stat-label">Modules</span>
                </div>
                <div class="stat-pill">
                  <span class="stat-number">{{ statistics.total_duration_hours }}h</span>
                  <span class="stat-label">Duration</span>
                </div>
              </div>
            </div>

            <div class="export-panel-body">
              <div class="generation-method-section">
                <label class="section-label">Generation Method</label>
                <div class="method-cards">
                  <div
                    class="method-card"
                    :class="{ 'is-active': generationMethod === 'template' }"
                    @click="generationMethod = 'template'"
                  >
                    <div class="method-icon template-icon">
                      <el-icon :size="24"><Document /></el-icon>
                    </div>
                    <div class="method-info">
                      <span class="method-name">Template Mode</span>
                      <span class="method-desc">Structure with placeholders for manual completion</span>
                    </div>
                    <el-icon v-if="generationMethod === 'template'" class="check-icon"><Check /></el-icon>
                  </div>

                  <div
                    class="method-card"
                    :class="{ 'is-active': generationMethod === 'genai' }"
                    @click="generationMethod = 'genai'"
                  >
                    <div class="method-icon genai-icon">
                      <el-icon :size="24"><MagicStick /></el-icon>
                    </div>
                    <div class="method-info">
                      <span class="method-name">GenAI-Assisted</span>
                      <span class="method-desc">AI generates content based on learning objectives</span>
                    </div>
                    <el-icon v-if="generationMethod === 'genai'" class="check-icon"><Check /></el-icon>
                  </div>
                </div>
              </div>

              <div class="export-action">
                <el-button
                  type="primary"
                  size="large"
                  :loading="generating"
                  :disabled="modules.length === 0"
                  class="export-button"
                  @click="generateAndExport"
                >
                  <el-icon><Download /></el-icon>
                  Export to Excel
                </el-button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- RFP Export View -->
      <div v-else-if="activeTask === 'rfp'" class="rfp-export-view">
        <!-- Back Button and Header -->
        <div class="view-header">
          <el-button @click="activeTask = null" text>
            <el-icon><ArrowLeft /></el-icon>
            Back to Overview
          </el-button>
          <h2>RFP Document Export</h2>
        </div>

        <!-- Loading State -->
        <div v-if="rfpLoading" class="loading-state">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
          <p>Loading RFP data...</p>
        </div>

        <!-- RFP Content -->
        <div v-else class="rfp-content">
          <!-- Summary Cards -->
          <div class="rfp-summary-cards">
            <!-- Organization Card -->
            <div class="summary-card org-card">
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <h3>Organization</h3>
              </div>
              <div class="card-body">
                <div class="stat-row">
                  <span class="stat-label">Name</span>
                  <span class="stat-value">{{ rfpData?.organization?.name || 'N/A' }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">SE Maturity</span>
                  <span class="stat-value">
                    Level {{ rfpData?.organization?.maturity_level || 0 }}/5
                    ({{ rfpData?.organization?.maturity_score?.toFixed(1) || 0 }}/100)
                  </span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Target Group</span>
                  <span class="stat-value">{{ rfpData?.target_group?.size || 0 }} employees</span>
                </div>
              </div>
            </div>

            <!-- Strategy Card -->
            <div class="summary-card strategy-card">
              <div class="card-header">
                <el-icon><Aim /></el-icon>
                <h3>Qualification Strategy</h3>
              </div>
              <div class="card-body">
                <div v-if="rfpData?.strategies?.length">
                  <div v-for="strategy in rfpData.strategies" :key="strategy.id" class="strategy-item">
                    <el-tag :type="strategy.is_primary ? 'primary' : 'info'" effect="plain">
                      {{ strategy.is_primary ? 'Primary' : 'Secondary' }}
                    </el-tag>
                    <span>{{ strategy.name }}</span>
                  </div>
                </div>
                <div v-else class="no-data">No strategy selected</div>
              </div>
            </div>

            <!-- Training Modules Card -->
            <div class="summary-card modules-card">
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <h3>Training Program</h3>
              </div>
              <div class="card-body">
                <div class="stat-row">
                  <span class="stat-label">Total Modules</span>
                  <span class="stat-value">{{ rfpData?.phase3?.summary?.total_modules || 0 }}</span>
                </div>
                <div v-if="rfpData?.phase3?.summary?.format_distribution" class="format-dist">
                  <span class="stat-label">Formats</span>
                  <div class="format-tags">
                    <el-tag
                      v-for="(count, format) in rfpData.phase3.summary.format_distribution"
                      :key="format"
                      size="small"
                      effect="plain"
                    >{{ format }}: {{ count }}</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Data Sections Preview -->
          <div class="rfp-sections">
            <!-- Roles Section -->
            <div class="rfp-section">
              <div class="section-header" @click="toggleRfpSection('roles')">
                <el-icon class="expand-icon" :class="{ 'is-expanded': expandedRfpSections.has('roles') }">
                  <ArrowRight />
                </el-icon>
                <h4>Organization Roles</h4>
                <span class="section-count">{{ rfpData?.roles?.length || 0 }} roles</span>
              </div>
              <el-collapse-transition>
                <div v-show="expandedRfpSections.has('roles')" class="section-content">
                  <el-table v-if="rfpData?.roles?.length" :data="rfpData.roles" size="small" stripe max-height="300">
                    <el-table-column prop="name" label="Role Name" min-width="180" />
                    <el-table-column prop="se_cluster_name" label="SE Cluster" width="180" />
                    <el-table-column prop="training_program" label="Training Program" width="180" />
                  </el-table>
                  <div v-else class="no-data">No roles defined</div>
                </div>
              </el-collapse-transition>
            </div>

            <!-- Existing Trainings Section -->
            <div class="rfp-section">
              <div class="section-header" @click="toggleRfpSection('trainings')">
                <el-icon class="expand-icon" :class="{ 'is-expanded': expandedRfpSections.has('trainings') }">
                  <ArrowRight />
                </el-icon>
                <h4>Existing Trainings</h4>
                <span class="section-count">{{ rfpData?.existing_trainings?.length || 0 }} competencies covered</span>
              </div>
              <el-collapse-transition>
                <div v-show="expandedRfpSections.has('trainings')" class="section-content">
                  <el-table v-if="rfpData?.existing_trainings?.length" :data="rfpData.existing_trainings" size="small" stripe max-height="300">
                    <el-table-column prop="competency_name" label="Competency" min-width="200" />
                    <el-table-column prop="covered_levels" label="Covered Levels" width="200">
                      <template #default="{ row }">
                        <div class="level-tags">
                          <span v-for="level in row.covered_levels" :key="level" class="level-badge small" :class="`l${level}`">
                            {{ getLevelName(level) }}
                          </span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div v-else class="no-data">No existing trainings recorded</div>
                </div>
              </el-collapse-transition>
            </div>

          </div>

          <!-- Export Panel -->
          <div class="export-panel rfp-export-panel">
            <div class="export-panel-header">
              <div class="export-title">
                <el-icon class="export-icon"><Download /></el-icon>
                <div>
                  <h3>Export RFP Document</h3>
                  <p class="export-subtitle">Generate comprehensive Request for Proposal document</p>
                </div>
              </div>
              <div class="export-stats">
                <div class="stat-pill">
                  <span class="stat-number">{{ rfpData?.roles?.length || 0 }}</span>
                  <span class="stat-label">Roles</span>
                </div>
                <div class="stat-pill">
                  <span class="stat-number">{{ rfpData?.phase3?.summary?.total_modules || 0 }}</span>
                  <span class="stat-label">Modules</span>
                </div>
              </div>
            </div>

            <div class="export-panel-body compact">
              <!-- Format Selection - Single Row -->
              <div class="format-row">
                <div
                  class="format-card-compact"
                  :class="{ 'is-active': rfpExportFormat === 'excel' }"
                  @click="rfpExportFormat = 'excel'"
                >
                  <div class="format-icon-sm excel-icon">
                    <el-icon :size="18"><Document /></el-icon>
                  </div>
                  <div class="format-info-compact">
                    <span class="format-name">Excel (.xlsx)</span>
                    <span class="format-desc">Data tables</span>
                  </div>
                </div>

                <div
                  class="format-card-compact genai-card"
                  :class="{ 'is-active': rfpExportFormat === 'word' }"
                  @click="rfpExportFormat = 'word'"
                >
                  <div class="format-icon-sm word-icon">
                    <el-icon :size="18"><Document /></el-icon>
                  </div>
                  <div class="format-info-compact">
                    <span class="format-name">Word (.docx)</span>
                    <span class="format-desc">AI-generated RFP</span>
                  </div>
                  <el-tag size="small" type="warning" effect="plain" class="genai-badge">GenAI</el-tag>
                </div>

                <el-button
                  type="primary"
                  :loading="rfpExporting"
                  class="export-btn-inline"
                  @click="exportRfpDocument"
                >
                  <el-icon><Download /></el-icon>
                  Export
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Module Details Dialog (shared between views) -->
      <el-dialog
        v-model="showDetailsDialog"
        :title="selectedModule?.module_name || 'Module Details'"
        width="750px"
        class="module-details-dialog"
      >
        <div v-if="selectedModule" class="module-details">
          <!-- Module Info -->
          <div class="detail-header">
            <div class="detail-badges">
              <span class="level-badge large" :class="`l${selectedModule.target_level}`">
                {{ getLevelName(selectedModule.target_level) }}
              </span>
              <span v-if="selectedModule.pmt_type !== 'combined'" class="pmt-badge large">
                {{ formatPmtType(selectedModule.pmt_type) }}
              </span>
              <el-tag v-if="selectedModule.learning_format_name" type="success" effect="plain">
                {{ selectedModule.learning_format_name }}
              </el-tag>
            </div>
            <div class="detail-stats">
              <span><el-icon><Clock /></el-icon> {{ selectedModule.estimated_duration_hours }}h duration</span>
              <span><el-icon><User /></el-icon> {{ selectedModule.estimated_participants }} participants</span>
            </div>
          </div>

          <!-- Roles Needing Training -->
          <div class="detail-section">
            <h4>Roles Needing Training</h4>
            <div class="roles-list">
              <el-tag
                v-for="role in (selectedModule.roles_needing_training || [])"
                :key="role"
                effect="plain"
              >{{ role }}</el-tag>
              <span v-if="!(selectedModule.roles_needing_training || []).length" class="no-data">No specific roles</span>
            </div>
          </div>

          <!-- Learning Objective -->
          <div class="detail-section">
            <h4>Learning Objective</h4>
            <div v-if="detailsLoading" class="loading-inline">
              <el-icon class="is-loading"><Loading /></el-icon> Loading...
            </div>
            <p v-else-if="moduleDetails?.learning_objective" class="lo-text">
              {{ moduleDetails.learning_objective }}
            </p>
            <p v-else class="no-data">Learning objective not available</p>
          </div>

          <!-- Content Topics -->
          <div class="detail-section">
            <h4>Content Topics</h4>
            <div v-if="detailsLoading" class="loading-inline">
              <el-icon class="is-loading"><Loading /></el-icon> Loading...
            </div>
            <ul v-else-if="moduleDetails?.content_topics && moduleDetails.content_topics.length" class="topics-list">
              <li v-for="topic in moduleDetails.content_topics" :key="topic">{{ topic }}</li>
            </ul>
            <p v-else class="no-data">Content topics not available</p>
          </div>

          <!-- AVIVA Sequence Preview -->
          <div class="detail-section">
            <h4>AVIVA Sequence Preview</h4>
            <div v-if="detailsLoading" class="loading-inline">
              <el-icon class="is-loading"><Loading /></el-icon> Loading...
            </div>
            <template v-else-if="moduleDetails?.suggested_sequence && moduleDetails.suggested_sequence.length">
              <p class="sequence-summary">
                {{ moduleDetails.suggested_activity_count }} activities over {{ selectedModule.estimated_duration_hours }} hours
              </p>
              <el-table :data="moduleDetails.suggested_sequence" size="small" stripe>
                <el-table-column prop="aviva" label="AVIVA" width="70">
                  <template #default="{ row }">
                    <span class="aviva-letter">{{ row.aviva }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="phase_type" label="Phase" width="120">
                  <template #default="{ row }">
                    <span class="phase-name">{{ formatPhaseName(row.phase_type) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="Duration" width="80">
                  <template #default="{ row }">{{ row.duration }} min</template>
                </el-table-column>
                <el-table-column prop="type" label="Type" width="80">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getTypeTagType(row.type)">
                      {{ row.type }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="method" label="Method" min-width="150">
                  <template #default="{ row }">
                    <span v-if="row.method">{{ row.method }}</span>
                    <span v-else class="no-method">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </template>
            <p v-else class="no-data">AVIVA sequence preview not available</p>
          </div>
        </div>

        <template #footer>
          <el-button @click="showDetailsDialog = false">Close</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import {
  Loading,
  Document,
  Download,
  ArrowRight,
  ArrowLeft,
  View,
  Lock,
  MagicStick,
  Clock,
  User,
  Suitcase,
  Connection,
  Aim,
  TrendCharts,
  Check,
  OfficeBuilding,
  InfoFilled
} from '@element-plus/icons-vue'
import axios from '@/api/axios'

const authStore = useAuthStore()

// State
const loading = ref(true)
const generating = ref(false)
const activeTask = ref(null)
const organizationId = ref(null)
const config = ref({
  task1_status: 'not_started',
  task2_status: 'not_started'
})
const modules = ref([])
const viewType = ref('competency_level')
const scalingInfo = ref(null)
const statistics = ref({
  total_modules: 0,
  total_duration_hours: 0
})
const generationMethod = ref('template')

// UI State
const expandedCompetencies = ref(new Set())
const expandedNestedCompetencies = ref(new Set())

// RFP Export State
const rfpLoading = ref(false)
const rfpExporting = ref(false)
const rfpData = ref(null)
const expandedRfpSections = ref(new Set(['roles']))
const rfpExportFormat = ref('excel')  // 'excel' | 'word' | 'pdf'

// Details dialog
const showDetailsDialog = ref(false)
const selectedModule = ref(null)
const moduleDetails = ref(null)
const detailsLoading = ref(false)

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

const formatPmtType = (pmt) => {
  if (pmt === 'method') return 'Method'
  if (pmt === 'tool') return 'Tool'
  return 'Combined'
}

const formatPhaseName = (phase) => {
  const phaseNames = {
    'arrive': 'Arrive',
    'activate': 'Activate Prior Knowledge',
    'inform': 'Inform',
    'process': 'Process/Practice',
    'evaluate': 'Evaluate',
    'break': 'Break',
    'lunch': 'Lunch Break'
  }
  return phaseNames[phase] || phase
}

const getTypeTagType = (type) => {
  // Type comes as 'Frontal', 'Active', or 'Break' from backend
  if (type === 'Frontal') return 'info'
  if (type === 'Active') return 'success'
  if (type === 'Break') return 'warning'
  return 'info'
}

// Computed
const overallProgress = computed(() => {
  // For now, just show 0% until export is done
  return 0
})

const progressColors = [
  { color: '#909399', percentage: 20 },
  { color: '#E6A23C', percentage: 50 },
  { color: '#409EFF', percentage: 80 },
  { color: '#67C23A', percentage: 100 }
]

const uniqueRolesCount = computed(() => {
  const allRoles = new Set()
  modules.value.forEach(m => {
    (m.roles_needing_training || []).forEach(role => allRoles.add(role))
  })
  return allRoles.size
})

// Group modules by competency for Competency-Level view
const competencyGroups = computed(() => {
  if (viewType.value !== 'competency_level') return []

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

  return Object.values(groups)
    .map(g => ({
      ...g,
      levels: Array.from(g.levels).sort((a, b) => a - b),
      modules: g.modules.sort((a, b) => {
        if (a.target_level !== b.target_level) return a.target_level - b.target_level
        return (a.pmt_type || '').localeCompare(b.pmt_type || '')
      })
    }))
    .sort((a, b) => a.competency_id - b.competency_id)
})

// Group by cluster for Training Packages view (Role-Clustered)
const trainingPackages = computed(() => {
  if (viewType.value !== 'role_clustered') return []

  const clusterGroups = {}

  modules.value.forEach(module => {
    const clusterId = module.cluster_id
    if (!clusterId) return

    if (!clusterGroups[clusterId]) {
      clusterGroups[clusterId] = {
        id: clusterId,
        cluster_name: module.cluster_name,
        modules: [],
        competencyMap: {},
        commonModules: [],
        pathwayModules: [],
        roles: new Set()
      }
    }

    clusterGroups[clusterId].modules.push(module)

    // Collect roles
    ;(module.roles_needing_training || []).forEach(role => {
      clusterGroups[clusterId].roles.add(role)
    })

    // For Engineers cluster (id=1), separate by subcluster
    if (clusterId === 1 && module.subcluster) {
      if (module.subcluster === 'common') {
        clusterGroups[clusterId].commonModules.push(module)
      } else if (module.subcluster === 'pathway') {
        clusterGroups[clusterId].pathwayModules.push(module)
      }
    }

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

  // Helper to create competency group array
  const createCompetencyArray = (modulesArray) => {
    const byComp = {}
    modulesArray.forEach(m => {
      if (!byComp[m.competency_id]) {
        byComp[m.competency_id] = {
          competency_id: m.competency_id,
          competency_name: m.competency_name,
          modules: [],
          levels: new Set()
        }
      }
      byComp[m.competency_id].modules.push(m)
      byComp[m.competency_id].levels.add(m.target_level)
    })
    return Object.values(byComp)
      .map(g => ({
        ...g,
        levels: Array.from(g.levels).sort((a, b) => a - b),
        modules: g.modules.sort((a, b) => {
          if (a.target_level !== b.target_level) return a.target_level - b.target_level
          return (a.pmt_type || '').localeCompare(b.pmt_type || '')
        })
      }))
      .sort((a, b) => a.competency_id - b.competency_id)
  }

  return Object.values(clusterGroups)
    .map(cluster => {
      const competencies = Object.values(cluster.competencyMap)
        .map(g => ({
          ...g,
          levels: Array.from(g.levels).sort((a, b) => a - b),
          modules: g.modules.sort((a, b) => {
            if (a.target_level !== b.target_level) return a.target_level - b.target_level
            return (a.pmt_type || '').localeCompare(b.pmt_type || '')
          })
        }))
        .sort((a, b) => a.competency_id - b.competency_id)

      const hasSubclusters = cluster.id === 1 && (cluster.commonModules.length > 0 || cluster.pathwayModules.length > 0)
      const totalDuration = cluster.modules.reduce((sum, m) => sum + (m.estimated_duration_hours || 0), 0)

      return {
        id: cluster.id,
        cluster_name: cluster.cluster_name,
        competencies,
        moduleCount: cluster.modules.length,
        totalDuration,
        roles: Array.from(cluster.roles),
        hasSubclusters,
        commonCompetencies: hasSubclusters ? createCompetencyArray(cluster.commonModules) : [],
        pathwayCompetencies: hasSubclusters ? createCompetencyArray(cluster.pathwayModules) : [],
        commonModuleCount: cluster.commonModules.length,
        pathwayModuleCount: cluster.pathwayModules.length
      }
    })
    .filter(cluster => cluster.competencies.length > 0)
    .sort((a, b) => a.id - b.id)
})

// UI helpers
const toggleCompetency = (competencyId) => {
  if (expandedCompetencies.value.has(competencyId)) {
    expandedCompetencies.value.delete(competencyId)
  } else {
    expandedCompetencies.value.add(competencyId)
  }
  expandedCompetencies.value = new Set(expandedCompetencies.value)
}

const toggleNestedCompetency = (key) => {
  if (expandedNestedCompetencies.value.has(key)) {
    expandedNestedCompetencies.value.delete(key)
  } else {
    expandedNestedCompetencies.value.add(key)
  }
  expandedNestedCompetencies.value = new Set(expandedNestedCompetencies.value)
}

// Package styling helpers
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

// Methods
const loadConfig = async () => {
  try {
    const response = await axios.get(`/api/phase4/config/${organizationId.value}`)
    if (response.data.success) {
      config.value = response.data.config
    }
  } catch (error) {
    console.error('Error loading Phase 4 config:', error)
  }
}

const loadModules = async () => {
  try {
    const response = await axios.get(`/api/phase4/aviva/modules/${organizationId.value}`)
    if (response.data.success) {
      modules.value = response.data.modules
      viewType.value = response.data.view_type || 'competency_level'
      scalingInfo.value = response.data.scaling_info
      statistics.value = response.data.statistics

      // Expand first few groups by default
      if (viewType.value === 'role_clustered') {
        // Expand first package's groups
        const firstPkg = trainingPackages.value[0]
        if (firstPkg) {
          firstPkg.competencies.slice(0, 3).forEach(comp => {
            expandedNestedCompetencies.value.add(`${firstPkg.id}_${comp.competency_id}`)
          })
          if (firstPkg.hasSubclusters) {
            firstPkg.commonCompetencies.slice(0, 2).forEach(comp => {
              expandedNestedCompetencies.value.add(`common_${firstPkg.id}_${comp.competency_id}`)
            })
          }
        }
      } else {
        // Expand first 3 competency groups
        competencyGroups.value.slice(0, 3).forEach(g => {
          expandedCompetencies.value.add(g.competency_id)
        })
      }
    }
  } catch (error) {
    console.error('Error loading AVIVA modules:', error)
    ElMessage.error('Failed to load training modules')
  }
}

const setActiveTask = (task) => {
  activeTask.value = task
  if (task === 'aviva') {
    loadModules()
  } else if (task === 'rfp') {
    loadRfpData()
  }
}

// RFP Methods
const loadRfpData = async () => {
  rfpLoading.value = true
  try {
    const response = await axios.get(`/api/phase4/rfp/data/${organizationId.value}`)
    if (response.data.success !== false) {
      rfpData.value = response.data.data
    } else {
      ElMessage.error(response.data.error || 'Failed to load RFP data')
    }
  } catch (error) {
    console.error('Error loading RFP data:', error)
    ElMessage.error('Failed to load RFP data')
  } finally {
    rfpLoading.value = false
  }
}

const toggleRfpSection = (section) => {
  if (expandedRfpSections.value.has(section)) {
    expandedRfpSections.value.delete(section)
  } else {
    expandedRfpSections.value.add(section)
  }
  expandedRfpSections.value = new Set(expandedRfpSections.value)
}

const exportRfpDocument = async () => {
  const format = rfpExportFormat.value
  const formatLabel = format === 'excel' ? 'Excel' : 'Word'
  const isGenAI = format === 'word'
  const moduleCount = rfpData.value?.phase3?.summary?.total_modules || 0

  // Different confirm message for GenAI formats
  const confirmMsg = isGenAI
    ? `Generate ${formatLabel} RFP document with AI-generated content?\n\nThis may take 2-5 minutes as AI generates the Core Concept narrative and Module Goals/Contents for ${moduleCount} modules.`
    : `Export comprehensive RFP document to ${formatLabel}?`

  let loadingInstance = null

  try {
    await ElMessageBox.confirm(
      confirmMsg,
      'Confirm Export',
      {
        confirmButtonText: 'Export',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
    )

    rfpExporting.value = true

    // Determine API endpoint and mime type based on format
    let endpoint = '/api/phase4/rfp/export'
    let mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    let defaultExt = 'xlsx'
    let timeout = 60000

    if (format === 'word') {
      endpoint = '/api/phase4/rfp/export-word'
      mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      defaultExt = 'docx'
      timeout = 600000  // 10 minutes for LLM generation
    }

    // Show loading overlay for GenAI formats
    if (isGenAI) {
      loadingInstance = ElLoading.service({
        lock: true,
        text: `Generating AI-enhanced ${formatLabel} document for ${moduleCount} modules... This may take a few minutes.`,
        background: 'rgba(0, 0, 0, 0.7)'
      })
    }

    const response = await axios.post(
      endpoint,
      {
        organization_id: organizationId.value,
        include_llm: true
      },
      {
        responseType: 'blob',
        timeout: timeout
      }
    )

    // Close loading overlay
    if (loadingInstance) loadingInstance.close()

    // Check actual content type
    const actualMimeType = response.headers['content-type'] || mimeType

    // Create download link
    const blob = new Blob([response.data], { type: actualMimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // Get filename from content-disposition header or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `RFP_Export_${new Date().toISOString().slice(0, 10)}.${defaultExt}`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match && match[1]) {
        filename = match[1].replace(/['"]/g, '')
      }
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`RFP document exported successfully as ${formatLabel}`)

  } catch (error) {
    // Close loading overlay on error
    if (loadingInstance) loadingInstance.close()

    if (error !== 'cancel') {
      console.error('Error exporting RFP document:', error)
      ElMessage.error('Failed to export RFP document: ' + (error.response?.data?.error || error.message))
    }
  } finally {
    rfpExporting.value = false
  }
}

const showModuleDetails = async (module) => {
  selectedModule.value = module
  moduleDetails.value = null
  showDetailsDialog.value = true
  detailsLoading.value = true

  try {
    const response = await axios.get(`/api/phase4/aviva/module/${module.id}/preview`)
    if (response.data.success) {
      moduleDetails.value = response.data.module
    }
  } catch (error) {
    console.error('Error loading module details:', error)
  } finally {
    detailsLoading.value = false
  }
}

const generateAndExport = async () => {
  if (modules.value.length === 0) {
    ElMessage.warning('No modules available to export')
    return
  }

  const moduleIds = modules.value.map(m => m.id).filter(id => id)
  if (moduleIds.length === 0) {
    ElMessage.error('No valid module IDs found.')
    return
  }

  const methodLabel = generationMethod.value === 'genai' ? 'AI-generated' : 'template'
  let loadingInstance = null

  try {
    await ElMessageBox.confirm(
      `Generate AVIVA plans for all ${moduleIds.length} modules using ${methodLabel} method and export to Excel?`,
      'Confirm Export',
      {
        confirmButtonText: 'Generate & Export',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
    )

    generating.value = true

    // Show loading message for GenAI (takes longer)
    loadingInstance = generationMethod.value === 'genai'
      ? ElLoading.service({
          lock: true,
          text: `Generating AI content for ${moduleIds.length} modules... This may take a few minutes.`,
          background: 'rgba(0, 0, 0, 0.7)'
        })
      : null

    const response = await axios.post(
      '/api/phase4/aviva/export-fresh',
      {
        organization_id: organizationId.value,
        module_ids: moduleIds,
        generation_method: generationMethod.value
      },
      {
        responseType: 'blob',
        timeout: 300000  // 5 minutes timeout for GenAI generation
      }
    )

    if (loadingInstance) loadingInstance.close()

    // Create download link
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // Get filename from content-disposition header or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `AVIVA_Plans_${new Date().toISOString().slice(0, 10)}.xlsx`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match && match[1]) {
        filename = match[1].replace(/['"]/g, '')
      }
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`Successfully exported ${moduleIds.length} AVIVA plan(s)`)

  } catch (error) {
    if (loadingInstance) loadingInstance.close()
    if (error !== 'cancel') {
      console.error('Error generating AVIVA plans:', error)
      ElMessage.error('Failed to generate AVIVA plans: ' + (error.response?.data?.error || error.message))
    }
  } finally {
    generating.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true

  const orgId = authStore.organizationId

  if (!orgId) {
    console.error('[Phase4] No organization ID found in auth store')
    ElMessage.error('Organization not found. Please log in again.')
    loading.value = false
    return
  }

  organizationId.value = orgId
  console.log('[Phase4] Using organization ID:', organizationId.value)

  await loadConfig()
  await loadModules()
  loading.value = false
})
</script>

<style scoped>
.phase-four {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #607D8B 0%, #455A64 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(69, 90, 100, 0.3);
}

.phase-indicator {
  display: flex;
  align-items: center;
  gap: 24px;
}

.phase-number {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.phase-title h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
  color: white;
}

.phase-title p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
  color: white;
}

.phase-progress {
  text-align: right;
  min-width: 200px;
}

.phase-progress :deep(.el-progress__text) {
  color: white;
}

.phase-progress :deep(.el-progress-bar__outer) {
  background-color: rgba(255, 255, 255, 0.3);
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: white;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-state p {
  margin-top: 16px;
  color: #666;
}

/* Dashboard View */
.dashboard-view {
  animation: fadeIn 0.3s ease;
}

.tasks-overview {
  text-align: center;
  margin-bottom: 32px;
}

.tasks-overview h2 {
  margin: 0 0 8px;
  color: #303133;
}

.tasks-description {
  color: #606266;
  max-width: 600px;
  margin: 0 auto;
}

.task-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.task-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.task-card:hover:not(.disabled) {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.task-card.active {
  border-color: #607D8B;
}

.task-card.completed {
  border-color: #67C23A;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.task-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.task-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #607D8B;
}

.task-card.completed .task-icon {
  background: #67C23A;
  color: white;
}

.task-content h3 {
  margin: 0 0 8px;
  color: #303133;
}

.task-content p {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
}

.task-result {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
}

/* AVIVA Planning View */
.aviva-planning-view {
  animation: fadeIn 0.3s ease;
}

.view-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.view-header h2 {
  margin: 0;
  flex: 1;
}

.no-modules {
  padding: 60px 20px;
  text-align: center;
}

.no-modules .hint {
  color: #909399;
  font-size: 13px;
  margin-top: 8px;
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

.info-box-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.scaling-info-box .info-box-header .el-icon {
  color: #409EFF;
}

.programs-info-box .info-box-header .el-icon {
  color: #67C23A;
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

.info-points li em {
  font-style: normal;
  color: #909399;
}

/* Stats Bar */
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
  gap: 6px;
}

.legend-label {
  font-size: 12px;
  color: #909399;
  margin-right: 4px;
}

/* Level badges with colors */
.level-badge {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.level-badge.l1 { background: #909399; }
.level-badge.l2 { background: #E6A23C; }
.level-badge.l4 { background: #409EFF; }
.level-badge.l6 { background: #67C23A; }

.level-badge.small {
  padding: 2px 6px;
  font-size: 10px;
}

.level-badge.large {
  padding: 4px 12px;
  font-size: 13px;
}

.pmt-badge {
  padding: 2px 8px;
  background: #E4E7ED;
  border-radius: 4px;
  font-size: 11px;
  color: #606266;
}

.pmt-badge.large {
  padding: 4px 12px;
  font-size: 13px;
}

/* Training Packages View */
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

.package-engineers { border-color: #409EFF; }
.package-managers { border-color: #E6A23C; }
.package-partners { border-color: #67C23A; }

.package-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #F5F7FA 0%, #EBEEF5 100%);
}

.header-engineers { background: linear-gradient(135deg, #ECF5FF 0%, #D9ECFF 100%); }
.header-managers { background: linear-gradient(135deg, #FDF6EC 0%, #FAECD8 100%); }
.header-partners { background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%); }

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

.package-engineers .package-icon { color: #409EFF; }
.package-managers .package-icon { color: #E6A23C; }
.package-partners .package-icon { color: #67C23A; }

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

.package-competencies {
  padding: 16px;
}

/* Subcluster Sections */
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

.subcluster-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.subcluster-count {
  font-size: 12px;
  color: #606266;
  background: #F5F7FA;
  padding: 2px 8px;
  border-radius: 4px;
}

.subcluster-desc {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.subcluster-modules {
  padding: 12px 16px;
}

/* Module Groups */
.competency-groups {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.module-group {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  background: white;
  overflow: hidden;
  margin-bottom: 8px;
}

.module-group:last-child {
  margin-bottom: 0;
}

.module-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #FAFAFA;
  cursor: pointer;
  transition: background 0.2s;
}

.module-group-header:hover {
  background: #F5F7FA;
}

.expand-icon {
  transition: transform 0.2s;
  color: #909399;
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
}

.group-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.group-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.level-badges {
  display: flex;
  gap: 4px;
}

.module-count {
  font-size: 12px;
  color: #909399;
}

/* Module List */
.module-list {
  border-top: 1px solid #EBEEF5;
}

.module-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #F5F7FA;
  cursor: pointer;
  transition: background 0.2s;
}

.module-item:last-child {
  border-bottom: none;
}

.module-item:hover {
  background: #F5F7FA;
}

.module-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.module-name {
  font-size: 13px;
  color: #606266;
}

.module-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.module-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pathway-roles {
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-roles {
  font-size: 11px;
  color: #909399;
}

/* Export Panel */
.export-panel {
  position: sticky;
  bottom: 20px;
  margin-top: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.08), 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid #E4E7ED;
  overflow: hidden;
  z-index: 100;
}

.export-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #F5F7FA 0%, #EBEEF5 100%);
  border-bottom: 1px solid #E4E7ED;
}

.export-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.export-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #607D8B 0%, #455A64 100%);
  border-radius: 12px;
  color: white;
  font-size: 24px;
}

.export-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.export-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.export-stats {
  display: flex;
  gap: 12px;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: white;
  border-radius: 10px;
  border: 1px solid #E4E7ED;
  min-width: 70px;
}

.stat-pill .stat-number {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.stat-pill .stat-label {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.export-panel-body {
  padding: 24px;
  display: flex;
  align-items: flex-end;
  gap: 24px;
}

.generation-method-section {
  flex: 1;
}

.section-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.method-cards {
  display: flex;
  gap: 12px;
}

.method-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #FAFAFA;
  border: 2px solid #E4E7ED;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.method-card:hover {
  background: #F5F7FA;
  border-color: #C0C4CC;
}

.method-card.is-active {
  background: linear-gradient(135deg, #F0F7FF 0%, #E6F1FC 100%);
  border-color: #409EFF;
}

.method-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
}

.template-icon {
  background: linear-gradient(135deg, #E6F1FC 0%, #D4E8FA 100%);
  color: #409EFF;
}

.genai-icon {
  background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%);
  color: #67C23A;
}

.method-card.is-active .template-icon {
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  color: white;
}

.method-card.is-active .genai-icon {
  background: linear-gradient(135deg, #67C23A 0%, #529b2e 100%);
  color: white;
}

.method-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.method-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.method-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.method-card .check-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  color: #409EFF;
  font-size: 16px;
}

.export-action {
  flex-shrink: 0;
}

.export-button {
  height: 52px;
  padding: 0 32px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #607D8B 0%, #455A64 100%) !important;
  border: none !important;
  color: white !important;
}

.export-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #546E7A 0%, #37474F 100%) !important;
  color: white !important;
}

.export-button:disabled {
  background: #E4E7ED !important;
  color: #C0C4CC !important;
}

/* Module Details Dialog */
.module-details-dialog .el-dialog__body {
  padding-top: 0;
}

.module-details {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #EBEEF5;
  margin-bottom: 16px;
}

.detail-badges {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-stats {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #606266;
}

.detail-stats span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.roles-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lo-text {
  color: #606266;
  line-height: 1.6;
  background: #F5F7FA;
  padding: 12px;
  border-radius: 6px;
  margin: 0;
}

.topics-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
}

.sequence-summary {
  margin: 0 0 12px;
  font-size: 13px;
  color: #909399;
}

.aviva-letter {
  font-weight: 700;
  color: #409EFF;
}

.phase-name {
  font-size: 12px;
  color: #606266;
}

.no-method {
  color: #C0C4CC;
}

.loading-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
}

.no-data {
  color: #909399;
  font-style: italic;
  font-size: 13px;
  margin: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* RFP Export View Styles */
.rfp-export-view {
  animation: fadeIn 0.3s ease;
}

.rfp-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Summary Cards */
.rfp-summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #E4E7ED;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-card .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: linear-gradient(135deg, #F5F7FA 0%, #EBEEF5 100%);
  border-bottom: 1px solid #E4E7ED;
}

.summary-card .card-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.org-card .card-header { background: linear-gradient(135deg, #ECF5FF 0%, #D9ECFF 100%); }
.org-card .card-header .el-icon { color: #409EFF; }

.strategy-card .card-header { background: linear-gradient(135deg, #FDF6EC 0%, #FAECD8 100%); }
.strategy-card .card-header .el-icon { color: #E6A23C; }

.modules-card .card-header { background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%); }
.modules-card .card-header .el-icon { color: #67C23A; }

.summary-card .card-body {
  padding: 16px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #F5F7FA;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row .stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-row .stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.strategy-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.format-dist {
  padding-top: 8px;
}

.format-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

/* RFP Sections */
.rfp-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 180px; /* Space for sticky export panel */
}

.rfp-section {
  background: white;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  overflow: hidden;
}

.rfp-section .section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #FAFAFA;
  cursor: pointer;
  transition: background 0.2s;
}

.rfp-section .section-header:hover {
  background: #F5F7FA;
}

.rfp-section .section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.section-count {
  font-size: 12px;
  color: #909399;
  background: #F5F7FA;
  padding: 3px 10px;
  border-radius: 4px;
}

.section-content {
  padding: 16px;
  border-top: 1px solid #E4E7ED;
}

.level-tags {
  display: flex;
  gap: 4px;
}

/* Gaps Summary */
.gaps-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gap-stat {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.gap-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  min-width: 70px;
}

.gap-values {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.gap-item {
  font-size: 13px;
  color: #606266;
}

.gap-item strong {
  color: #303133;
}

/* AVIVA Summary */
.aviva-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.aviva-tag {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-count {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

/* RFP Export Panel */
.rfp-export-panel {
  margin-top: 8px;
}

.export-options {
  flex: 1;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.no-data {
  color: #909399;
  font-style: italic;
  font-size: 13px;
  text-align: center;
  padding: 12px;
}

/* Format Selection */
.format-selection-section {
  flex: 1;
  margin-bottom: 16px;
}

.format-selection-section .section-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

/* Compact Export Layout */
.export-panel-body.compact {
  padding: 12px 16px;
}

.format-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.format-card-compact {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #FAFAFA;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
  min-width: 140px;
}

.format-card-compact:hover {
  background: #F5F7FA;
  border-color: #C0C4CC;
}

.format-card-compact.is-active {
  background: linear-gradient(135deg, #F0F7FF 0%, #E6F1FC 100%);
  border-color: #409EFF;
}

.format-card-compact.genai-card {
  position: relative;
}

.genai-badge {
  position: absolute;
  top: -6px;
  right: -4px;
  font-size: 10px;
  padding: 0 4px;
  height: 16px;
  line-height: 14px;
}

.format-icon-sm {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
}

.excel-icon {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  color: #4CAF50;
}

.word-icon {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  color: #2196F3;
}

.format-card-compact.is-active .excel-icon {
  background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
  color: white;
}

.format-card-compact.is-active .word-icon {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  color: white;
}

.format-info-compact {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.format-info-compact .format-name {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
}

.format-info-compact .format-desc {
  font-size: 10px;
  color: #909399;
}

.export-btn-inline {
  flex-shrink: 0;
  height: 44px;
  padding: 0 20px;
}

/* Legacy styles kept for compatibility */
.format-group {
  margin-bottom: 12px;
}

.format-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #FAFAFA;
  border: 2px solid #E4E7ED;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  margin-bottom: 8px;
}

.format-card:hover {
  background: #F5F7FA;
  border-color: #C0C4CC;
}

.format-card.is-active {
  background: linear-gradient(135deg, #F0F7FF 0%, #E6F1FC 100%);
  border-color: #409EFF;
}

.format-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.format-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.format-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.format-desc {
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
}

.format-card .check-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #409EFF;
  font-size: 14px;
}

</style>
