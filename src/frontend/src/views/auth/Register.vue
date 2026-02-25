<template>
  <div class="register-form">
    <!-- Role Selection Cards (shown when no type selected) -->
    <div v-if="!registrationType" class="role-selection">
      <p class="selection-prompt">I am registering as:</p>

      <div class="role-cards">
        <!-- Admin Card -->
        <div class="role-card admin-card" @click="selectRole('admin')">
          <div class="role-card-header">
            <div class="role-icon-wrapper admin-icon">
              <el-icon size="24"><Setting /></el-icon>
            </div>
            <div class="role-header-text">
              <h3 class="role-title">Organization Admin</h3>
              <span class="role-subtitle">Set up and manage SE training</span>
            </div>
            <el-icon class="role-arrow"><ArrowRight /></el-icon>
          </div>
          <div class="role-details">
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>Assess maturity and define roles</span>
            </div>
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>Identify competency gaps</span>
            </div>
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>Design qualification plans</span>
            </div>
          </div>
        </div>

        <!-- Employee Card -->
        <div class="role-card employee-card" @click="selectRole('employee')">
          <div class="role-card-header">
            <div class="role-icon-wrapper employee-icon">
              <el-icon size="24"><User /></el-icon>
            </div>
            <div class="role-header-text">
              <h3 class="role-title">Employee</h3>
              <span class="role-subtitle">Join and complete assessment</span>
            </div>
            <el-icon class="role-arrow"><ArrowRight /></el-icon>
          </div>
          <div class="role-details">
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>Join with organization code</span>
            </div>
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>Complete competency assessment</span>
            </div>
            <div class="role-detail-item">
              <el-icon size="14"><Check /></el-icon>
              <span>View personalized results</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Admin Registration Form -->
    <div v-else-if="registrationType === 'admin'" class="registration-form-container">
      <div class="form-header">
        <button class="back-button" @click="registrationType = null">
          <el-icon><ArrowLeft /></el-icon>
          <span>Back</span>
        </button>
        <div class="form-type-badge admin-badge">
          <el-icon><Setting /></el-icon>
          <span>Admin Registration</span>
        </div>
      </div>

      <el-form
        ref="adminFormRef"
        :model="adminForm"
        :rules="adminRules"
        label-position="top"
        size="large"
        @submit.prevent="handleAdminRegister"
      >
        <el-form-item label="Username" prop="username">
          <el-input
            v-model="adminForm.username"
            placeholder="Choose a unique username"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="adminForm.password"
            type="password"
            placeholder="Choose a strong password"
            size="large"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="adminForm.confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            size="large"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-divider>Organization Details</el-divider>

        <el-form-item label="Organization Name" prop="organizationName">
          <el-input
            v-model="adminForm.organizationName"
            placeholder="Enter your organization name"
            size="large"
            prefix-icon="OfficeBuilding"
          />
        </el-form-item>

        <el-form-item label="Organization Size" prop="organizationSize">
          <el-select
            v-model="adminForm.organizationSize"
            placeholder="Select organization size"
            size="large"
            style="width: 100%"
          >
            <el-option label="Small (< 100 employees)" value="small" />
            <el-option label="Medium (100-1000 employees)" value="medium" />
            <el-option label="Large (1000-10000 employees)" value="large" />
            <el-option label="Enterprise (> 10000 employees)" value="enterprise" />
          </el-select>
        </el-form-item>

        <el-alert
          v-if="authStore.error"
          :title="authStore.error"
          type="error"
          show-icon
          :closable="false"
          class="mb-4"
        />

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            native-type="submit"
            :loading="loading"
            style="width: 100%"
            class="submit-btn admin-submit"
          >
            <span v-if="loading">Creating Account...</span>
            <span v-else>Create Admin Account</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Employee Registration Form -->
    <div v-else-if="registrationType === 'employee'" class="registration-form-container">
      <div class="form-header">
        <button class="back-button" @click="registrationType = null">
          <el-icon><ArrowLeft /></el-icon>
          <span>Back</span>
        </button>
        <div class="form-type-badge employee-badge">
          <el-icon><User /></el-icon>
          <span>Employee Registration</span>
        </div>
      </div>

      <el-form
        ref="employeeFormRef"
        :model="employeeForm"
        :rules="employeeRules"
        label-position="top"
        size="large"
        @submit.prevent="handleEmployeeRegister"
      >
        <el-form-item label="Organization Code" prop="organizationCode">
          <el-input
            v-model="employeeForm.organizationCode"
            placeholder="Enter code from your admin"
            size="large"
            @blur="handleOrgCodeBlur"
            prefix-icon="Key"
          >
            <template #suffix>
              <el-icon v-if="orgCodeVerifying" class="is-loading">
                <Loading />
              </el-icon>
              <el-icon v-else-if="orgCodeValid" style="color: #67c23a">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="orgCodeChecked && !orgCodeValid" style="color: #f56c6c">
                <CircleClose />
              </el-icon>
            </template>
          </el-input>
          <div v-if="orgCodeValid && organizationName" class="org-name-display">
            <el-icon><OfficeBuilding /></el-icon>
            <span>{{ organizationName }}</span>
          </div>
          <div v-if="orgCodeChecked && !orgCodeValid && !orgCodeVerifying" class="org-code-error">
            <span>Invalid organization code. Please check with your admin.</span>
          </div>
        </el-form-item>

        <el-divider>Account Details</el-divider>

        <el-form-item label="Username" prop="username">
          <el-input
            v-model="employeeForm.username"
            placeholder="Choose a unique username"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="employeeForm.password"
            type="password"
            placeholder="Choose a strong password"
            size="large"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="employeeForm.confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            size="large"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-alert
          v-if="authStore.error"
          :title="authStore.error"
          type="error"
          show-icon
          :closable="false"
          class="mb-4"
        />

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            native-type="submit"
            :loading="loading"
            :disabled="!orgCodeValid"
            style="width: 100%"
            class="submit-btn employee-submit"
          >
            <span v-if="loading">Creating Account...</span>
            <span v-else>Create Employee Account</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'
import {
  User,
  Setting,
  ArrowRight,
  ArrowLeft,
  Loading,
  CircleCheck,
  CircleClose,
  OfficeBuilding,
  Check
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const registrationType = ref(null)
const loading = ref(false)

const selectRole = (role) => {
  registrationType.value = role
}

// Admin form
const adminFormRef = ref(null)
const adminForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  organizationName: '',
  organizationSize: ''
})

const validatePasswordMatch = (rule, value, callback) => {
  if (value !== adminForm.password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const adminRules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, message: 'Username must be at least 3 characters', trigger: 'blur' },
    { pattern: /^\S+$/, message: 'Username must not contain spaces', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    { validator: validatePasswordMatch, trigger: 'blur' }
  ],
  organizationName: [
    { required: true, message: 'Organization name is required', trigger: 'blur' }
  ],
  organizationSize: [
    { required: true, message: 'Organization size is required', trigger: 'change' }
  ]
}

// Employee form
const employeeFormRef = ref(null)
const employeeForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  organizationCode: ''
})

const orgCodeVerifying = ref(false)
const orgCodeValid = ref(false)
const orgCodeChecked = ref(false)
const organizationName = ref('')

const validateEmployeePasswordMatch = (rule, value, callback) => {
  if (value !== employeeForm.password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const employeeRules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, message: 'Username must be at least 3 characters', trigger: 'blur' },
    { pattern: /^\S+$/, message: 'Username must not contain spaces', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    { validator: validateEmployeePasswordMatch, trigger: 'blur' }
  ],
  organizationCode: [
    { required: true, message: 'Organization code is required', trigger: 'blur' }
  ]
}

// Handlers
const handleAdminRegister = async () => {
  if (!adminFormRef.value) return

  await adminFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const result = await authStore.registerAdmin({
        username: adminForm.username,
        password: adminForm.password,
        organizationName: adminForm.organizationName,
        organizationSize: adminForm.organizationSize
      })

      if (result.success) {
        toast.success('Admin registration successful! Please log in.')
        router.push('/auth/login')
      }
    } catch (error) {
      console.error('Admin registration failed:', error)
    } finally {
      loading.value = false
    }
  })
}

const handleEmployeeRegister = async () => {
  if (!employeeFormRef.value) return

  await employeeFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const result = await authStore.registerEmployee({
        username: employeeForm.username,
        password: employeeForm.password,
        organizationCode: employeeForm.organizationCode
      })

      if (result.success) {
        toast.success('Registration successful! Please log in.')
        router.push('/auth/login')
      }
    } catch (error) {
      console.error('Employee registration failed:', error)
    } finally {
      loading.value = false
    }
  })
}

const handleOrgCodeBlur = async () => {
  if (!employeeForm.organizationCode) {
    orgCodeChecked.value = false
    orgCodeValid.value = false
    organizationName.value = ''
    return
  }

  orgCodeVerifying.value = true
  orgCodeChecked.value = true

  try {
    const result = await authStore.verifyOrgCode(employeeForm.organizationCode)
    orgCodeValid.value = result.valid
    organizationName.value = result.organization_name || ''
  } catch (error) {
    orgCodeValid.value = false
    organizationName.value = ''
  } finally {
    orgCodeVerifying.value = false
  }
}

</script>

<style scoped>
.register-form {
  width: 100%;
}

/* Role Selection */
.role-selection {
  text-align: center;
}

.selection-prompt {
  color: #606266;
  font-size: 15px;
  margin-bottom: 20px;
  font-weight: 500;
}

.role-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-card {
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: left;
}

.role-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.admin-card:hover {
  border-color: #e6a23c;
  background: #fffbf5;
}

.employee-card:hover {
  border-color: #409eff;
  background: #f5faff;
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.admin-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f5a623 100%);
  color: white;
}

.employee-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.role-header-text {
  flex: 1;
  min-width: 0;
}

.role-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.role-subtitle {
  font-size: 13px;
  color: #909399;
}

.role-arrow {
  color: #c0c4cc;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.admin-card:hover .role-arrow {
  color: #e6a23c;
  transform: translateX(4px);
}

.employee-card:hover .role-arrow {
  color: #409eff;
  transform: translateX(4px);
}

.role-details {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.role-detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.role-detail-item .el-icon {
  color: #c0c4cc;
}

.admin-card:hover .role-detail-item .el-icon {
  color: #e6a23c;
}

.employee-card:hover .role-detail-item .el-icon {
  color: #409eff;
}

/* Form Header */
.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: #f5f7fa;
  color: #409eff;
}

.form-type-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.admin-badge {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.employee-badge {
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

/* Form Styles */
.registration-form-container {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.mb-4 {
  margin-bottom: 16px;
}

.org-name-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
}

.org-code-error {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 6px;
  color: #f56c6c;
  font-size: 13px;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

.admin-submit {
  background: linear-gradient(135deg, #e6a23c 0%, #f5a623 100%);
  border: none;
}

.admin-submit:hover {
  background: linear-gradient(135deg, #cf8d2e 0%, #e09510 100%);
}

.employee-submit {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
}

.employee-submit:hover {
  background: linear-gradient(135deg, #3a8ee6 0%, #5ca8f5 100%);
}

/* Element Plus Overrides */
:deep(.el-divider__text) {
  color: #909399;
  font-size: 13px;
  background: #fff;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

/* Responsive */
@media (max-width: 600px) {
  .role-details {
    flex-direction: column;
    gap: 4px;
  }

  .form-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .form-type-badge {
    align-self: flex-start;
  }
}
</style>
