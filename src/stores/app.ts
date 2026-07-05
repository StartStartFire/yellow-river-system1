import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ReservoirBrief } from '@/types/reservoir'

export type NavModule =
  | 'home'
  | 'basic-data'
  | 'water-condition'
  | 'model-config'
  | 'process-transparent'
  | 'evaluation-decision'
  | 'case-library'
  | 'report-statistics'

export const useAppStore = defineStore('app', () => {
  // 当前导航模块
  const activeModule = ref<NavModule>('home')

  // 当前选中的水库
  const selectedReservoir = ref<ReservoirBrief | null>(null)

  // 当前选中的方案
  const selectedScenario = ref<string>('')

  // 设置当前导航模块
  const setActiveModule = (module: NavModule) => {
    activeModule.value = module
  }

  // 设置当前选中的水库
  const setSelectedReservoir = (reservoir: ReservoirBrief | null) => {
    selectedReservoir.value = reservoir
  }

  // 设置当前选中的方案
  const setSelectedScenario = (scenario: string) => {
    selectedScenario.value = scenario
  }

  return {
    activeModule,
    selectedReservoir,
    selectedScenario,
    setActiveModule,
    setSelectedReservoir,
    setSelectedScenario
  }
})
