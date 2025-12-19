<template>
  <div class="auth-layout">
    <!-- Background Pattern -->
    <div class="auth-background">
      <div class="pattern-overlay"></div>
    </div>

    <!-- Main Content -->
    <div class="auth-container">
      <!-- Header -->
      <div class="auth-header">
        <router-link to="/" class="logo-link">
          <el-icon class="logo-icon" size="40">
            <School />
          </el-icon>
          <div class="logo-text">
            <h1 class="app-name">SE-QPT Platform</h1>
            <p class="app-tagline">Systems Engineering Qualification Planning Tool</p>
          </div>
        </router-link>
      </div>

      <!-- Content Card -->
      <div class="auth-content">
        <el-card class="auth-card" shadow="always">
          <div class="card-header">
            <h2 class="card-title">{{ pageTitle }}</h2>
            <p class="card-subtitle">{{ pageSubtitle }}</p>
          </div>

          <!-- Main Content Slot -->
          <div class="card-body">
            <router-view v-slot="{ Component }">
              <transition name="slide-fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>

          <!-- Footer Links -->
          <div class="card-footer">
            <div class="auth-links">
              <router-link
                v-if="$route.name === 'Login'"
                to="/auth/register"
                class="auth-link"
              >
                Don't have an account? Register here
              </router-link>
              <router-link
                v-if="$route.name === 'Register'"
                to="/auth/login"
                class="auth-link"
              >
                Already have an account? Sign in
              </router-link>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Features Section -->
      <div class="features-section">
        <div class="features-grid">
          <div class="feature-item">
            <el-icon class="feature-icon" size="32">
              <TrendCharts />
            </el-icon>
            <h3 class="feature-title">4-Phase Methodology</h3>
            <p class="feature-description">
              Structured approach to systems engineering qualification planning
            </p>
          </div>

          <div class="feature-item">
            <el-icon class="feature-icon" size="32">
              <MagicStick />
            </el-icon>
            <h3 class="feature-title">AI-Powered Objectives</h3>
            <p class="feature-description">
              RAG-LLM system generates company-specific learning objectives
            </p>
          </div>

          <div class="feature-item">
            <el-icon class="feature-icon" size="32">
              <UserFilled />
            </el-icon>
            <h3 class="feature-title">Competency Assessment</h3>
            <p class="feature-description">
              Comprehensive evaluation of systems engineering competencies
            </p>
          </div>

          <div class="feature-item">
            <el-icon class="feature-icon" size="32">
              <Calendar />
            </el-icon>
            <h3 class="feature-title">Personalized Plans</h3>
            <p class="feature-description">
              Tailored qualification plans based on assessment results
            </p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="auth-footer">
        <div class="footer-content">
          <div class="footer-copyright">
            <p class="thesis-credit">
              Master Thesis Project - Systems Engineering Qualification Planning Tool
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-content">
          <el-icon class="loading-spinner" size="48">
            <Loading />
          </el-icon>
          <p class="loading-text">Please wait...</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  School,
  TrendCharts,
  MagicStick,
  UserFilled,
  Calendar,
  Loading
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

// Use computed to properly sync loading state with auth store
const loading = computed(() => authStore.loading)

// Handle bfcache restoration - ensure loading state is reset when page is restored
const handlePageShow = (event) => {
  // If page is restored from bfcache (persisted = true), reset loading state
  if (event.persisted) {
    console.log('[AuthLayout] Page restored from bfcache, resetting loading state')
    // Force reset the auth store loading state
    authStore.loading = false
  }
}

onMounted(() => {
  // Listen for pageshow event to handle bfcache restoration
  window.addEventListener('pageshow', handlePageShow)

  // Also ensure loading is false on mount (prevents stuck overlay)
  if (authStore.loading) {
    console.log('[AuthLayout] Resetting stuck loading state on mount')
    authStore.loading = false
  }
})

onUnmounted(() => {
  window.removeEventListener('pageshow', handlePageShow)
})

// Computed
const pageTitle = computed(() => {
  const titles = {
    Login: 'Welcome Back',
    Register: 'Create Account'
  }
  return titles[route.name] || 'Authentication'
})

const pageSubtitle = computed(() => {
  const subtitles = {
    Login: 'Sign in to access your SE-QPT dashboard',
    Register: 'Join the SE-QPT platform to start your qualification journey'
  }
  return subtitles[route.name] || 'Please authenticate to continue'
})
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

.auth-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  z-index: -2;
}

.pattern-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 2px, transparent 2px),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 2px, transparent 2px);
  background-size: 60px 60px;
  background-position: 0 0, 30px 30px;
  opacity: 0.5;
  z-index: -1;
}

.auth-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.auth-header {
  padding: 32px 24px 24px 24px;
  text-align: center;
}

.logo-link {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: white;
  transition: transform 0.3s ease;
}

.logo-link:hover {
  transform: translateY(-2px);
}

.logo-icon {
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.logo-text {
  text-align: left;
}

.app-name {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.app-tagline {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.auth-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 800px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.auth-card :deep(.el-card__body) {
  padding: 32px 48px;
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.card-subtitle {
  margin: 0;
  color: #606266;
  font-size: 15px;
  line-height: 1.4;
}

.card-body {
  margin-bottom: 24px;
}

.card-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

.auth-links {
  margin-bottom: 16px;
}

.auth-link {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.auth-link:hover {
  color: #337ecc;
  text-decoration: underline;
}

.features-section {
  padding: 48px 24px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.features-grid {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 32px;
}

.feature-item {
  text-align: center;
  color: white;
}

.feature-icon {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 16px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.feature-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.feature-description {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.auth-footer {
  padding: 32px 24px;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.footer-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.footer-link:hover {
  color: white;
}

.footer-copyright {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.4;
}

.thesis-credit {
  margin-top: 4px;
  font-style: italic;
  opacity: 0.8;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.loading-content {
  text-align: center;
  color: white;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-text {
  margin: 0;
  font-size: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .auth-header {
    padding: 24px 16px 16px 16px;
  }

  .logo-link {
    flex-direction: column;
    gap: 12px;
  }

  .logo-text {
    text-align: center;
  }

  .app-name {
    font-size: 24px;
  }

  .auth-content {
    padding: 16px;
  }

  .auth-card {
    max-width: 100%;
  }

  .card-title {
    font-size: 20px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .footer-links {
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .auth-header {
    padding: 16px;
  }

  .app-name {
    font-size: 20px;
  }

  .app-tagline {
    font-size: 13px;
  }

  .features-section {
    padding: 32px 16px;
  }

  .feature-title {
    font-size: 16px;
  }

  .feature-description {
    font-size: 13px;
  }

  .footer-links {
    flex-direction: column;
    gap: 8px;
  }
}
</style>