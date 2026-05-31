import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NavModule =
  | 'home'
  | 'basic-data'
  | 'water-condition'
  | 'model-config'
  | 'process-transparent'
  | 'evaluation-decision'
  | 'case-library'
  | 'report-statistics'

export interface Reservoir {
  id: string
  name: string
  waterLevel: number
  inflow: number
  outflow: number
  storage: number
}

export const useAppStore = defineStore('app', () => {
  // 当前导航模块
  const activeModule = ref<NavModule>('home')

  // 当前选中的水库
  const selectedReservoir = ref<Reservoir | null>(null)

  // 当前选中的方案
  const selectedScenario = ref<string>('')

  // 设置当前导航模块
  const setActiveModule = (module: NavModule) => {
    activeModule.value = module
  }

  // 设置当前选中的水库
  const setSelectedReservoir = (reservoir: Reservoir | null) => {
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
