<template>
  <div class="login-form">
    <el-form @submit.prevent="handleLogin" :model="loginForm" label-position="top" size="large">
      <el-form-item label="Username" required>
        <el-input
          v-model="loginForm.usernameOrEmail"
          placeholder="Enter your username"
          size="large"
        />
      </el-form-item>

      <el-form-item label="Password" required>
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="Enter your password"
          size="large"
          show-password
        />
      </el-form-item>

      <!-- Error Display -->
      <el-form-item v-if="authStore.error">
        <el-alert
          :title="authStore.error"
          type="error"
          show-icon
          :closable="false"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          @click="handleLogin"
          :loading="loading"
          style="width: 100%"
        >
          <span v-if="loading">Logging in...</span>
          <span v-else>Sign In</span>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const loginForm = reactive({
  usernameOrEmail: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    console.log('Login attempt:', loginForm)

    const result = await authStore.login({
      usernameOrEmail: loginForm.usernameOrEmail,
      password: loginForm.password
    })

    console.log('Login result:', result)

    if (result && result.success) {
      const redirectPath = router.currentRoute.value.query.redirect || '/app/dashboard'
      console.log('Redirecting to:', redirectPath)

      // Reset loading state BEFORE redirect to prevent overlay from persisting
      loading.value = false

      // Use setTimeout to ensure all UI updates (toast, loading state) are complete
      // before triggering the redirect. This prevents browser bfcache from caching
      // the page with the loading overlay visible.
      setTimeout(() => {
        // Use replace() instead of href to prevent bfcache issues
        window.location.replace(redirectPath)
      }, 100)
    } else {
      console.error('Login failed - no success in result:', result)
      loading.value = false
    }
  } catch (error) {
    console.error('Login error:', error)
    loading.value = false
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
}
</style>