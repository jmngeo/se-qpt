<template>
  <el-card class="phase2-role-selection step-card">
    <template #header>
      <div class="card-header">
        <h2>Phase 2 - Task 1: Select Roles for Competency Assessment</h2>
        <p style="color: #606266; font-size: 14px; margin-top: 8px;">
          Select the SE roles that will participate in the competency assessment.
          These roles were identified during Phase 1.
        </p>
      </div>
    </template>

    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- Error state -->
    <el-alert
      v-else-if="error"
      type="error"
      :title="error"
      show-icon
      :closable="false"
    />

    <!-- No roles found -->
    <el-alert
      v-else-if="!loading && identifiedRoles.length === 0"
      type="warning"
      title="No Roles Found"
      :closable="false"
      show-icon
    >
      <p>No SE roles were identified during Phase 1 for this organization.</p>
      <p style="margin-top: 8px;">Please complete Phase 1 first.</p>
    </el-alert>

    <!-- Role selection grid -->
    <div v-else>
      <!-- Guidance Info Box -->
      <div class="info-box role-assessment-guidance-box">
        <div class="info-box-header">
          <el-icon><InfoFilled /></el-icon>
          <h4>About Role-Based Assessment</h4>
        </div>
        <ul class="info-points">
          <li>
            The roles below were <strong>identified in Phase 1</strong> during the organization profile setup.
            Each role has been mapped to standardized <strong>SE role clusters</strong> (e.g., System Engineer, Project Manager)
            which define the required competency levels for that role.
          </li>
          <li>
            <strong>Select the roles</strong> that should participate in the competency assessment.
            The system will calculate which SE competencies are required and at what proficiency level,
            based on the combined requirements of all selected roles.
          </li>
          <li>
            After selection, you will proceed to a <strong>self-assessment survey</strong> where you rate your
            current competency level against the role requirements. The gap between current and required levels
            will drive the training plan in later phases.
          </li>
          <li class="note">
            Data source: Organization roles from Phase 1, Task 2. Role-to-competency mapping based on
            the INCOSE Systems Engineering Competency Framework.
          </li>
        </ul>
      </div>

      <!-- Selection toolbar -->
      <div class="selection-toolbar">
        <div class="selection-count">
          <strong>Roles selected:</strong> {{ selectedRoleIds.length }} / {{ identifiedRoles.length }}
        </div>
        <div class="selection-actions">
          <el-button
            text
            size="small"
            @click="selectAll"
          >
            Select All
          </el-button>
          <el-button
            text
            size="small"
            @click="deselectAll"
          >
            Deselect All
          </el-button>
        </div>
      </div>

      <!-- Role cards grid -->
      <div class="roles-grid">
        <div
          v-for="role in identifiedRoles"
          :key="role.id"
          :class="['role-card', { 'selected': selectedRoleIds.includes(role.id) }]"
          @click="toggleRole(role.id)"
        >
          <div class="role-header">
            <h4 class="role-name">
              {{ role.orgRoleName || role.standardRoleName }}
            </h4>
            <el-icon v-if="selectedRoleIds.includes(role.id)" class="selected-icon">
              <Check />
            </el-icon>
          </div>

          <!-- Show description if available -->
          <p v-if="role.role_description || role.description" class="role-description">
            {{ role.role_description || role.description }}
          </p>

          <!-- Show standard role mapping if this is a custom role with a standard mapping -->
          <p v-if="role.standardRoleName && role.identificationMethod !== 'STANDARD'"
             class="role-mapping"
             style="font-size: 12px; color: #909399; margin-top: 4px;">
            Based on: {{ role.standardRoleName }}
          </p>
        </div>
      </div>

      <!-- Validation message -->
      <el-alert
        v-if="showValidation && selectedRoleIds.length === 0"
        type="error"
        :closable="false"
        show-icon
        style="margin-top: 20px;"
      >
        Please select at least one role to continue.
      </el-alert>

      <!-- Actions -->
      <div class="step-actions" style="margin-top: 32px;">
        <el-button @click="handleBack">
          Back to Phase 1
        </el-button>
        <el-button
          type="primary"
          :disabled="selectedRoleIds.length === 0"
          :loading="calculating"
          @click="handleCalculateCompetencies"
        >
          Calculate Necessary Competencies
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowRight, Check, InfoFilled } from '@element-plus/icons-vue'
import { phase2Task1Api } from '@/api/phase2'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'

const props = defineProps({
  organizationId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['next', 'back'])

const authStore = useAuthStore()
const identifiedRoles = ref([])
const selectedRoleIds = ref([])
const organizationName = ref('')
const loading = ref(false)
const calculating = ref(false)
const showValidation = ref(false)
const error = ref(null)

// Fetch identified roles on mount
onMounted(async () => {
  await fetchIdentifiedRoles()
})

/**
 * Fetch Phase 1 identified roles
 */
const fetchIdentifiedRoles = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await phase2Task1Api.getIdentifiedRoles(props.organizationId)

    if (response.success && response.exists) {
      identifiedRoles.value = response.data
      organizationName.value = response.organizationName
      console.log(`[Phase2] Loaded ${identifiedRoles.value.length} roles for org ${props.organizationId}`)
    } else {
      identifiedRoles.value = []
      console.warn('[Phase2] No roles found for organization')
    }
  } catch (err) {
    console.error('[Phase2] Error fetching roles:', err)
    error.value = err.response?.data?.error || 'Failed to load roles. Please try again.'
    toast.error('Failed to load roles')
  } finally {
    loading.value = false
  }
}

/**
 * Toggle role selection
 */
const toggleRole = (roleId) => {
  const index = selectedRoleIds.value.indexOf(roleId)
  if (index > -1) {
    selectedRoleIds.value.splice(index, 1)
  } else {
    selectedRoleIds.value.push(roleId)
  }
}

/**
 * Select all roles
 */
const selectAll = () => {
  selectedRoleIds.value = identifiedRoles.value.map(r => r.id)
}

/**
 * Deselect all roles
 */
const deselectAll = () => {
  selectedRoleIds.value = []
}

/**
 * Calculate necessary competencies and proceed to next step
 */
const handleCalculateCompetencies = async () => {
  if (selectedRoleIds.value.length === 0) {
    showValidation.value = true
    toast.warning('Please select at least one role')
    return
  }

  calculating.value = true
  showValidation.value = false

  try {
    console.log('[Phase2] Calculating competencies for roles:', selectedRoleIds.value)

    const response = await phase2Task1Api.calculateCompetencies(
      props.organizationId,
      selectedRoleIds.value
    )

    if (response.success) {
      console.log(`[Phase2] Calculated ${response.count} necessary competencies`)

      toast.success(`Found ${response.count} necessary competencies`)

      // Get full role objects for selected IDs
      const selectedRolesData = identifiedRoles.value.filter(role =>
        selectedRoleIds.value.includes(role.id)
      )

      console.log('[Phase2] Selected roles data:', selectedRolesData)
      console.log('[Phase2] First role properties:', selectedRolesData[0])

      // Emit to parent with competency data
      emit('next', {
        competencies: response.competencies,
        selectedRoles: selectedRolesData,
        organizationId: props.organizationId
      })
    }
  } catch (err) {
    console.error('[Phase2] Error calculating competencies:', err)
    toast.error('Failed to calculate competencies')
  } finally {
    calculating.value = false
  }
}

/**
 * Go back to Phase 1
 */
const handleBack = () => {
  emit('back')
}
</script>

<style scoped>
.phase2-role-selection {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.loading-container {
  padding: 20px;
}

/* Guidance Info Box */
.info-box {
  background: #F8F9FA;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
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

.info-points li.note {
  color: #909399;
  font-style: italic;
}

.role-assessment-guidance-box {
  background: #ECF5FF;
  border-color: #D9ECFF;
}

.role-assessment-guidance-box .info-box-header .el-icon {
  color: #409EFF;
}

.selection-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.selection-count {
  font-size: 14px;
  color: #606266;
}

.selection-actions {
  display: flex;
  gap: 8px;
}

/* Grid layout */
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 20px;
}

/* Role card - Derik's style */
.role-card {
  border: 2px solid #EBEEF5;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.role-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.role-card.selected {
  border-color: #409EFF;
  background: #F0F7FF;
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.role-name {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.selected-icon {
  color: #409EFF;
  font-size: 20px;
  flex-shrink: 0;
}

.role-description {
  color: #606266;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

/* Actions */
.step-actions {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

/* Responsive */
@media (max-width: 768px) {
  .roles-grid {
    grid-template-columns: 1fr;
  }

  .selection-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
