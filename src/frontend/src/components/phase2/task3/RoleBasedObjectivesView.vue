<template>
  <div class="role-based-objectives-view">
    <!-- Styled Info Banner -->
    <div class="view-info-banner">
      <div class="banner-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      </div>
      <div class="banner-content">
        <h4 class="banner-title">Role-Based Analysis</h4>
        <p class="banner-description">
          View competency gaps organized by role. Each role shows aggregated training needs
          across all assigned users with recommended training approaches.
        </p>
      </div>
    </div>

    <!-- Role Cards -->
    <div v-if="rolesList.length > 0" class="roles-container">
      <div class="roles-list">
        <div
          v-for="role in rolesList"
          :key="role.roleId"
          class="role-card"
          :class="{ 'expanded': expandedRole === role.roleId }"
        >
          <!-- Role Card Header -->
          <div class="role-card-header" @click="toggleRole(role.roleId)">
            <div class="role-main-info">
              <div class="role-icon" :class="{ 'has-gaps': role.competenciesWithGaps > 0 }">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div class="role-title-section">
                <h3 class="role-name">{{ role.roleName }}</h3>
                <span class="role-users-badge">{{ role.totalUsers }} users</span>
              </div>
            </div>
            <div class="role-quick-stats">
              <div v-if="role.competenciesWithGaps === 0" class="quick-stat achieved">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span class="stat-text">Complete</span>
              </div>
              <div class="expand-icon" :class="{ 'rotated': expandedRole === role.roleId }">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Role Card Content (Expandable) -->
          <div v-show="expandedRole === role.roleId" class="role-card-content">
            <!-- TODO: DELETE THIS SECTION - "Recommended Training Approach" is no longer needed.
                 This feature was part of earlier design but is now superseded by Phase 3 Learning Format Selection.
                 Marked for deletion on 2026-01-18. Remove this entire block and related CSS/JS once confirmed. -->
            <!-- HIDDEN: Training Method Recommendation
            <div v-if="role.trainingRecommendation" class="training-recommendation">
              <div class="recommendation-header">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                <span>Recommended Training Approach</span>
              </div>
              <div class="recommendation-body">
                <h5 class="method-name">{{ role.trainingRecommendation.method }}</h5>
                <p class="method-rationale">{{ role.trainingRecommendation.rationale }}</p>
                <span class="cost-badge" :class="getCostClass(role.trainingRecommendation.cost_level)">
                  Cost: {{ role.trainingRecommendation.cost_level }}
                </span>
              </div>
            </div>
            END HIDDEN -->

            <!-- Competencies List -->
            <div v-if="getUniqueCompetencies(role.competencies).length > 0" class="competencies-section">
              <h5 class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                Competencies Requiring Training
              </h5>
              <div class="competency-cards">
                <div
                  v-for="comp in getUniqueCompetencies(role.competencies)"
                  :key="comp.competency_id"
                  class="competency-item"
                >
                  <div class="competency-main">
                    <span class="competency-name">{{ comp.competency_name }}</span>
                    <div class="level-badges">
                      <span
                        v-for="level in comp.levels_needed"
                        :key="level"
                        class="level-badge"
                        :class="'level-' + level"
                      >
                        {{ getLevelName(level) }}
                      </span>
                    </div>
                  </div>
                  <div class="competency-users">
                    <span class="users-needing">{{ comp.users_needing }}</span>
                    <span class="users-separator">/</span>
                    <span class="users-total">{{ comp.total_users }}</span>
                    <span class="users-label">users need training</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- No Gaps Message -->
            <div v-else class="no-gaps-message">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <p>All competencies achieved for this role</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Roles Message -->
    <div v-else class="no-roles-message">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <line x1="23" y1="11" x2="17" y2="11"/>
      </svg>
      <h4>No Role Data Available</h4>
      <p>This view requires role assignments to display role-based training objectives.</p>
      <p class="hint">Ensure users are assigned to roles in Phase 1 Task 2.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  objectives: {
    type: Object,
    required: true
  },
  organizationId: {
    type: Number,
    required: true
  }
})

// Expanded role state (single role expanded at a time)
const expandedRole = ref(null)

// Toggle role expansion
const toggleRole = (roleId) => {
  if (expandedRole.value === roleId) {
    expandedRole.value = null
  } else {
    expandedRole.value = roleId
  }
}

// Extract role data from objectives
const rolesList = computed(() => {
  const roles = []
  const pyramidData = props.objectives?.data?.main_pyramid

  if (!pyramidData?.levels) {
    return roles
  }

  // Collect role data from gap_data in competencies
  const roleMap = new Map()

  Object.values(pyramidData.levels).forEach(levelData => {
    levelData.competencies?.forEach(comp => {
      if (comp.gap_data?.roles) {
        Object.entries(comp.gap_data.roles).forEach(([roleId, roleData]) => {
          if (!roleMap.has(roleId)) {
            roleMap.set(roleId, {
              roleId,
              roleName: roleData.role_name,
              totalUsers: roleData.total_users || 0,
              usersNeedingTrainingSum: 0,
              gapPercentageSum: 0,
              competencyCount: 0,
              uniqueCompetencies: new Set(),
              trainingRecommendations: [],
              competencies: []
            })
          }

          const role = roleMap.get(roleId)

          // Only add if this competency has gaps for this role
          if (roleData.levels_needed?.length > 0) {
            // Track unique competencies (same competency may appear at multiple levels)
            const isNewCompetency = !role.uniqueCompetencies.has(comp.competency_id)
            role.uniqueCompetencies.add(comp.competency_id)

            role.competencies.push({
              competency_id: comp.competency_id,
              competency_name: comp.competency_name,
              target_level: comp.target_level,
              median_level: roleData.median_level,
              mean_level: roleData.mean_level,
              users_needing: roleData.users_needing_training,
              total_users: roleData.total_users,
              gap_percentage: roleData.gap_percentage,
              levels_needed: roleData.levels_needed,
              variance: roleData.variance
            })

            // Aggregate stats only for unique competencies
            if (isNewCompetency) {
              role.usersNeedingTrainingSum += roleData.users_needing_training || 0
              role.gapPercentageSum += roleData.gap_percentage || 0
              role.competencyCount++
            }

            // Collect all training recommendations for aggregate calculation
            if (roleData.training_recommendation) {
              role.trainingRecommendations.push(roleData.training_recommendation)
            }
          }
        })
      }
    })
  })

  // Post-process: calculate averages and determine aggregate training method
  return Array.from(roleMap.values())
    .filter(r => r.totalUsers > 0)
    .map(r => {
      const uniqueCompCount = r.uniqueCompetencies.size
      return {
        roleId: r.roleId,
        roleName: r.roleName,
        totalUsers: r.totalUsers,
        usersNeedingTraining: uniqueCompCount > 0
          ? Math.round(r.usersNeedingTrainingSum / uniqueCompCount)
          : 0,
        gapPercentage: uniqueCompCount > 0
          ? Math.round(r.gapPercentageSum / uniqueCompCount)
          : 0,
        competenciesWithGaps: uniqueCompCount,
        trainingRecommendation: determineAggregateTrainingMethod(r.trainingRecommendations, r.gapPercentageSum / uniqueCompCount),
        competencies: r.competencies
      }
    })
    .sort((a, b) => b.competenciesWithGaps - a.competenciesWithGaps)
})

// Determine aggregate training method based on all recommendations for a role
const determineAggregateTrainingMethod = (recommendations, avgGapPercentage) => {
  if (!recommendations || recommendations.length === 0) {
    return null
  }

  // Count method occurrences
  const methodCounts = {}
  recommendations.forEach(rec => {
    const method = rec.method || 'Unknown'
    methodCounts[method] = (methodCounts[method] || 0) + 1
  })

  // Find most common method
  let maxCount = 0
  let mostCommonMethod = null
  Object.entries(methodCounts).forEach(([method, count]) => {
    if (count > maxCount) {
      maxCount = count
      mostCommonMethod = method
    }
  })

  // Find the recommendation that matches
  const matchingRec = recommendations.find(r => r.method === mostCommonMethod)

  // Create aggregate rationale
  const uniqueMethods = Object.keys(methodCounts).length
  let rationale = matchingRec?.rationale || ''

  if (uniqueMethods > 1) {
    rationale = `Most competencies (${maxCount}/${recommendations.length}) suggest this approach. Average gap: ${Math.round(avgGapPercentage)}%`
  }

  return {
    method: mostCommonMethod,
    rationale: rationale,
    cost_level: matchingRec?.cost_level || 'Medium',
    icon: matchingRec?.icon || 'mdi-school'
  }
}

// Get unique competencies (deduplicate by competency_id, keep highest target)
const getUniqueCompetencies = (competencies) => {
  const compMap = new Map()

  competencies.forEach(comp => {
    const existing = compMap.get(comp.competency_id)
    if (!existing || comp.target_level > existing.target_level) {
      compMap.set(comp.competency_id, comp)
    }
  })

  return Array.from(compMap.values()).sort((a, b) =>
    a.competency_name.localeCompare(b.competency_name)
  )
}

// Helper functions
const getRecommendationType = (costLevel) => {
  if (costLevel === 'Low') return 'success'
  if (costLevel === 'Medium') return 'warning'
  return 'info'
}

const getCostTagType = (costLevel) => {
  if (costLevel === 'Low') return 'success'
  if (costLevel === 'Medium') return 'warning'
  if (costLevel === 'Low to Medium') return 'info'
  return ''
}

const getCostClass = (costLevel) => {
  if (costLevel === 'Low') return 'cost-low'
  if (costLevel === 'Medium') return 'cost-medium'
  if (costLevel === 'High') return 'cost-high'
  return 'cost-default'
}

const getProgressColor = (percentage) => {
  if (percentage >= 70) return '#F56C6C'
  if (percentage >= 40) return '#E6A23C'
  return '#67C23A'
}

const getLevelTagType = (level) => {
  const types = {
    1: 'info',
    2: 'success',
    4: 'warning',
    6: 'danger'
  }
  return types[level] || ''
}

// Map level numbers to user-friendly names
const getLevelName = (level) => {
  const names = {
    1: 'Knowing',
    2: 'Understanding',
    4: 'Applying',
    6: 'Mastering'
  }
  return names[level] || `Level ${level}`
}
</script>

<style scoped>
.role-based-objectives-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Info Banner */
.view-info-banner {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fc 100%);
  border: 1px solid #d0e3f0;
  border-radius: 12px;
}

.banner-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 10px;
  color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.banner-content {
  flex: 1;
}

.banner-title {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a3353;
}

.banner-description {
  margin: 0;
  font-size: 13px;
  color: #5a7a9a;
  line-height: 1.5;
}

/* Roles Container */
.roles-container {
  background: transparent;
}

.roles-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Role Card */
.role-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.role-card:hover {
  border-color: #d0d7de;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.role-card.expanded {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.12);
}

/* Role Card Header */
.role-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.role-card-header:hover {
  background: #fafbfc;
}

.role-main-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.role-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: #f5f7fa;
  border-radius: 10px;
  color: #909399;
  transition: all 0.2s ease;
}

.role-icon.has-gaps {
  background: #fff7e6;
  color: #E6A23C;
}

.role-title-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.role-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.role-users-badge {
  font-size: 12px;
  color: #909399;
}

.role-quick-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.quick-stat.gaps {
  background: #fff7e6;
  color: #D48806;
}

.quick-stat.gaps .stat-number {
  font-weight: 700;
  font-size: 15px;
}

.quick-stat.achieved {
  background: #f0f9eb;
  color: #67C23A;
}

.expand-icon {
  display: flex;
  align-items: center;
  color: #909399;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* Role Card Content */
.role-card-content {
  padding: 0 20px 20px;
  border-top: 1px solid #f0f2f5;
  background: #fafbfc;
}

/* Role Summary Stats */
.role-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 16px 0;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 12px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.summary-stat.highlight {
  background: #fff7e6;
  border-color: #ffd591;
}

.summary-stat .stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.summary-stat.highlight .stat-value {
  color: #D48806;
}

.summary-stat .stat-label {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* Training Recommendation */
.training-recommendation {
  margin: 16px 0;
  background: white;
  border-radius: 10px;
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f5f7fa;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.recommendation-body {
  padding: 16px;
}

.method-name {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.method-rationale {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.cost-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.cost-badge.cost-low {
  background: #f0f9eb;
  color: #67C23A;
}

.cost-badge.cost-medium {
  background: #fdf6ec;
  color: #E6A23C;
}

.cost-badge.cost-high {
  background: #fef0f0;
  color: #F56C6C;
}

.cost-badge.cost-default {
  background: #f5f7fa;
  color: #909399;
}

/* Competencies Section */
.competencies-section {
  margin-top: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.competency-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.competency-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.competency-item:hover {
  border-color: #d0d7de;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.competency-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.competency-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.level-badges {
  display: flex;
  gap: 4px;
}

.level-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.level-badge.level-1 {
  background: #e6f7ff;
  color: #1890ff;
}

.level-badge.level-2 {
  background: #f0f9eb;
  color: #67C23A;
}

.level-badge.level-4 {
  background: #fff7e6;
  color: #E6A23C;
}

.level-badge.level-6 {
  background: #f9f0ff;
  color: #722ED1;
}

.competency-users {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  flex-shrink: 0;
}

.users-needing {
  font-weight: 700;
  color: #E6A23C;
}

.users-separator {
  color: #c0c4cc;
}

.users-total {
  color: #606266;
}

.users-label {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

/* No Gaps Message */
.no-gaps-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 20px;
  text-align: center;
  color: #67C23A;
}

.no-gaps-message p {
  margin: 12px 0 0 0;
  font-size: 14px;
  color: #67C23A;
  font-weight: 500;
}

/* No Roles Message */
.no-roles-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
  text-align: center;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
}

.no-roles-message svg {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.no-roles-message h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.no-roles-message p {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.no-roles-message .hint {
  margin-top: 12px;
  font-size: 13px;
  color: #1890ff;
}

/* Responsive */
@media (max-width: 768px) {
  .role-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .role-quick-stats {
    width: 100%;
    justify-content: space-between;
  }

  .role-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .competency-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .competency-users {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
