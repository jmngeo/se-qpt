import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/api/axios'

/**
 * Phase progression composable to manage sequential phase access
 */
export function usePhaseProgression() {
  // Phase completion status
  const phaseCompletionStatus = ref({
    phase1: false,
    phase2: false,
    phase3: false,
    phase4: false
  })

  // Check if phase data exists in localStorage or database
  const checkPhaseCompletion = async () => {
    try {
      // Get user info from localStorage
      const userStr = localStorage.getItem('user')
      const user = userStr ? JSON.parse(userStr) : null
      const userId = user?.id
      const userRole = user?.role

      console.log('[usePhaseProgression] Checking phase completion for:', { userId, userRole })

      let phase1Complete = false
      let phase2Complete = false
      let phase3Complete = false

      // For both admins and employees, check database first (source of truth)
      try {
        // Get organization code from localStorage (stored during login)
        const orgCode = localStorage.getItem('user_organization_code')
        const orgId = localStorage.getItem('user_organization_id')

        // Build query params
        const params = orgCode ? `?code=${orgCode}` : (orgId ? `?id=${orgId}` : '')

        const response = await axios.get(`/api/organization/dashboard${params}`)
        phase1Complete = response.data.organization?.phase1_completed || false
        phase2Complete = response.data.organization?.phase2_completed || false
        phase3Complete = response.data.organization?.phase3_completed || false
        console.log('[usePhaseProgression] Phase 1 check from database:', phase1Complete)
        console.log('[usePhaseProgression] Phase 2 check from database:', phase2Complete)
        console.log('[usePhaseProgression] Phase 3 check from database:', phase3Complete)
        console.log('[usePhaseProgression] Organization data:', response.data.organization)
      } catch (error) {
        console.warn('[usePhaseProgression] Failed to check organization phase completion:', error)
        // Fallback to localStorage check
        const phase1Data = userId
          ? localStorage.getItem(`se-qpt-phase1-data-user-${userId}`) || localStorage.getItem('se-qpt-phase1-data')
          : localStorage.getItem('se-qpt-phase1-data')
        phase1Complete = !!phase1Data

        const phase2Data = userId
          ? localStorage.getItem(`se-qpt-phase2-data-user-${userId}`) || localStorage.getItem('se-qpt-phase2-data')
          : localStorage.getItem('se-qpt-phase2-data')
        phase2Complete = !!phase2Data

        const phase3Data = userId
          ? localStorage.getItem(`se-qpt-phase3-data-user-${userId}`) || localStorage.getItem('se-qpt-phase3-data')
          : localStorage.getItem('se-qpt-phase3-data')
        phase3Complete = !!phase3Data

        console.log('[usePhaseProgression] Phase 1 fallback to localStorage:', phase1Complete)
        console.log('[usePhaseProgression] Phase 2 fallback to localStorage:', phase2Complete)
        console.log('[usePhaseProgression] Phase 3 fallback to localStorage:', phase3Complete)
      }

      // Check Phase 4 from localStorage for now (can be migrated to database later)
      const phase4Data = userId
        ? localStorage.getItem(`se-qpt-phase4-data-user-${userId}`) || localStorage.getItem('se-qpt-phase4-data')
        : localStorage.getItem('se-qpt-phase4-data')

      phaseCompletionStatus.value = {
        phase1: phase1Complete,
        phase2: phase2Complete,
        phase3: phase3Complete,
        phase4: !!phase4Data
      }

      console.log('[usePhaseProgression] Updated phase completion status:', phaseCompletionStatus.value)
      return phaseCompletionStatus.value
    } catch (error) {
      console.error('Error checking phase completion:', error)
      return {
        phase1: false,
        phase2: false,
        phase3: false,
        phase4: false
      }
    }
  }

  // Check if a specific phase can be accessed (synchronous - uses cached status)
  const canAccessPhase = (phaseNumber) => {
    const completionStatus = phaseCompletionStatus.value

    switch (phaseNumber) {
      case 1:
        return true // Phase 1 is always accessible
      case 2:
        return completionStatus.phase1
      case 3:
        return completionStatus.phase1 && completionStatus.phase2
      case 4:
        return completionStatus.phase1 && completionStatus.phase2 && completionStatus.phase3
      default:
        return false
    }
  }

  // Get the next available phase (synchronous - uses cached status)
  const getNextAvailablePhase = () => {
    const completionStatus = phaseCompletionStatus.value

    if (!completionStatus.phase1) return 1
    if (!completionStatus.phase2) return 2
    if (!completionStatus.phase3) return 3
    if (!completionStatus.phase4) return 4
    return 4 // All phases completed, stay on phase 4
  }

  // Get phase completion percentage
  const getOverallProgress = computed(() => {
    const completedPhases = Object.values(phaseCompletionStatus.value).filter(Boolean).length
    return Math.round((completedPhases / 4) * 100)
  })

  // Get phase status for UI display (synchronous - uses cached status)
  const getPhaseStatus = (phaseNumber) => {
    const completionStatus = phaseCompletionStatus.value
    const phaseKey = `phase${phaseNumber}`

    if (completionStatus[phaseKey]) {
      return 'completed'
    } else if (canAccessPhase(phaseNumber)) {
      return 'available'
    } else {
      return 'locked'
    }
  }

  // Navigation guard function
  const beforePhaseNavigation = async (to, from, next) => {
    // Refresh phase completion status before navigation
    await checkPhaseCompletion()

    const phaseNumber = parseInt(to.params.phase || to.path.split('/').pop())

    if (isNaN(phaseNumber) || phaseNumber < 1 || phaseNumber > 4) {
      next('/app/phases/1')
      return
    }

    if (canAccessPhase(phaseNumber)) {
      next()
    } else {
      const nextAvailable = getNextAvailablePhase()
      ElMessage.warning(`Please complete Phase ${nextAvailable - 1} before accessing Phase ${phaseNumber}`)
      next(`/app/phases/${nextAvailable}`)
    }
  }

  // Mark phase as completed
  const markPhaseCompleted = (phaseNumber) => {
    const phaseKey = `phase${phaseNumber}`
    phaseCompletionStatus.value[phaseKey] = true
  }

  // Reset all progress (for testing/admin purposes)
  const resetProgress = () => {
    localStorage.removeItem('se-qpt-phase1-data')
    localStorage.removeItem('se-qpt-phase2-data')
    localStorage.removeItem('se-qpt-phase3-data')
    localStorage.removeItem('se-qpt-phase4-data')

    phaseCompletionStatus.value = {
      phase1: false,
      phase2: false,
      phase3: false,
      phase4: false
    }

    ElMessage.success('Progress reset successfully')
  }

  // Get phase titles
  const getPhaseTitle = (phaseNumber) => {
    const titles = {
      1: 'Prepare SE Training',
      2: 'Identify Requirements and Competencies',
      3: 'Macro Planning',
      4: 'Micro Planning'
    }
    return titles[phaseNumber] || `Phase ${phaseNumber}`
  }

  // Get phase descriptions
  const getPhaseDescription = (phaseNumber) => {
    const descriptions = {
      1: 'Assess SE maturity, identify roles, and select training strategy',
      2: 'Define competencies, formulate learning objectives, and identify gaps',
      3: 'Select learning modules and qualification formats',
      4: 'Create detailed implementation concept and timeline'
    }
    return descriptions[phaseNumber] || `Complete Phase ${phaseNumber}`
  }

  return {
    phaseCompletionStatus,
    checkPhaseCompletion,
    canAccessPhase,
    getNextAvailablePhase,
    getOverallProgress,
    getPhaseStatus,
    beforePhaseNavigation,
    markPhaseCompleted,
    resetProgress,
    getPhaseTitle,
    getPhaseDescription
  }
}