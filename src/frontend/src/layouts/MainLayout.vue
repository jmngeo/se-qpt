<template>
  <div class="main-layout">
    <!-- Header -->
    <el-header class="main-header">
      <div class="header-content">
        <!-- Logo and Title -->
        <div class="header-left">
          <router-link to="/app/dashboard" class="logo-link">
            <el-icon class="logo-icon" size="32">
              <School />
            </el-icon>
            <span class="app-title">SE-QPT Platform</span>
          </router-link>
        </div>

        <!-- Navigation Menu -->
        <div class="header-center">
          <el-menu
            :default-active="activeRoute"
            mode="horizontal"
            class="main-navigation"
            :ellipsis="false"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/app/dashboard">
              <el-icon><Odometer /></el-icon>
              <span>Dashboard</span>
            </el-menu-item>

            <el-sub-menu index="phases">
              <template #title>
                <el-icon><Guide /></el-icon>
                <span>SE-QPT Phases</span>
              </template>
              <el-menu-item index="/app/phases/1">Phase 1: Prepare SE Training</el-menu-item>
              <el-menu-item index="/app/phases/2">Phase 2: Identify Competencies</el-menu-item>
              <el-menu-item v-if="authStore.isAdmin" index="/app/phases/3">Phase 3: Macro Planning</el-menu-item>
              <el-menu-item v-if="authStore.isAdmin" index="/app/phases/4">Phase 4: Micro Planning</el-menu-item>
            </el-sub-menu>

            <!-- Plans button hidden for now - will be used in Phase 4
            <el-menu-item index="/app/plans">
              <el-icon><Calendar /></el-icon>
              <span>Plans</span>
            </el-menu-item>
            -->

            <el-menu-item v-if="authStore.isAdmin" index="objectives" @click="goToObjectives">
              <el-icon><Aim /></el-icon>
              <span>Objectives</span>
            </el-menu-item>

            <el-sub-menu index="matrix" v-if="authStore.isAdmin">
              <template #title>
                <el-icon><Grid /></el-icon>
                <span>Matrix Config</span>
              </template>
              <el-menu-item index="/admin/matrix/role-process">Role-Process Matrix</el-menu-item>
              <el-menu-item index="/admin/matrix/process-competency">Process-Competency Matrix</el-menu-item>
            </el-sub-menu>

            <!-- Admin dropdown removed - placeholder pages not implemented
            <el-sub-menu index="admin" v-if="authStore.isAdmin">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>Admin</span>
              </template>
              <el-menu-item index="/admin/dashboard">Admin Dashboard</el-menu-item>
              <el-menu-item index="/admin/users">User Management</el-menu-item>
              <el-menu-item index="/admin/competencies">Competencies</el-menu-item>
              <el-menu-item index="/admin/modules">Modules</el-menu-item>
              <el-menu-item index="/admin/reports">Reports</el-menu-item>
            </el-sub-menu>
            -->
          </el-menu>
        </div>

        <!-- User Menu -->
        <div class="header-right">
          <!-- User Info -->
          <div class="user-info">
            <el-avatar :size="32" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="user-name">{{ authStore.userName }}</span>
          </div>

          <!-- Logout Button -->
          <el-button
            type="info"
            plain
            @click="handleLogout"
            class="logout-button"
          >
            <el-icon><SwitchButton /></el-icon>
            <span>Logout</span>
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- Main Content Area -->
    <el-container class="main-container">

      <!-- Main Content -->
      <el-main class="main-content">
        <!-- Page Header -->
        <div class="page-header" v-if="showPageHeader">
          <div class="page-header-content">
            <div class="page-title-section">
              <h1 class="page-title">{{ pageTitle }}</h1>
              <p class="page-subtitle" v-if="pageSubtitle">{{ pageSubtitle }}</p>
            </div>
            <div class="page-actions">
              <slot name="page-actions"></slot>
            </div>
          </div>
        </div>

        <!-- Breadcrumb -->
        <el-breadcrumb class="page-breadcrumb" v-if="breadcrumbItems.length > 0">
          <el-breadcrumb-item
            v-for="item in breadcrumbItems"
            :key="item.path"
            :to="item.to || undefined"
          >
            {{ item.text }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <!-- Main Content Slot -->
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Stores
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()


// Computed
const activeRoute = computed(() => route.path)

const pageTitle = computed(() => {
  return route.meta?.title || 'SE-QPT Platform'
})

const pageSubtitle = computed(() => {
  return route.meta?.subtitle || ''
})

const showPageHeader = computed(() => {
  return route.meta?.showHeader !== false
})

const breadcrumbItems = computed(() => {
  const items = []
  const pathSegments = route.path.split('/').filter(Boolean)

  // Hide breadcrumb for phase routes and dashboard
  if (pathSegments.includes('phases') || pathSegments.includes('dashboard')) {
    return []
  }

  let currentPath = ''
  for (const segment of pathSegments) {
    currentPath += `/${segment}`

    // Skip 'app' and 'admin' segments
    if (segment === 'app' || segment === 'admin') continue

    const routeName = segment.charAt(0).toUpperCase() + segment.slice(1)
    items.push({
      text: routeName,
      path: currentPath,
      to: currentPath
    })
  }

  return items
})


// Methods
const handleMenuSelect = (index) => {
  // Skip navigation for custom-handled menu items
  if (index === 'objectives') return

  if (index !== route.path) {
    router.push(index)
  }
}

const goToObjectives = () => {
  // Navigate to Phase 2 Task 3 Admin (Dashboard) page
  // The component automatically uses the user's organization_id
  router.push({ name: 'Phase2Task3Admin' })
}

const handleLogout = () => {
  authStore.logout().then(() => {
    router.push('/auth/login')
  })
}



// Watch for route changes to update breadcrumbs
watch(route, () => {
  // Could trigger additional logic here
}, { immediate: true })
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #409eff;
}

.logo-icon {
  margin-right: 12px;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  overflow-x: auto;
  overflow-y: hidden;
}

.main-navigation {
  border-bottom: none;
  flex-wrap: nowrap;
}

.main-navigation .el-menu-item,
.main-navigation .el-sub-menu__title {
  height: 60px;
  line-height: 60px;
  border-bottom: 2px solid transparent;
}

.main-navigation .el-menu-item.is-active {
  border-bottom-color: #409eff;
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}


.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
}

.user-name {
  font-weight: 500;
  color: #2c3e50;
}

.logout-button {
  height: 36px;
}

.main-container {
  flex: 1;
  overflow: hidden;
}


.main-content {
  background: #f5f7fa;
  overflow-y: auto;
  padding: 0;
}

.page-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 24px;
  margin-bottom: 24px;
}

.page-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.page-subtitle {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.page-breadcrumb {
  padding: 0 24px;
  margin-bottom: 16px;
}

.content-wrapper {
  padding: 0 24px 24px 24px;
  min-height: calc(100vh - 200px);
}


.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .header-center {
    display: none;
  }


  .content-wrapper {
    padding: 0 16px 16px 16px;
  }

  .page-header {
    padding: 16px;
    margin-bottom: 16px;
  }

  .page-breadcrumb {
    padding: 0 16px;
  }
}
</style>