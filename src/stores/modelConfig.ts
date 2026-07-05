import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  reservoirGroupModelMap,
  scenarioModelMap,
  scenarioSubOptionModelMap,
  timeStepParamSuggestions,
  objectiveRelevantParams,
  modelLabelMap,
  algorithmLabelMap,
} from '@/mock/model-config/linkage'
import { dispatchModels, optimizationAlgorithms } from '@/mock/model-config/modelAlgorithm'

/**
 * 模型配置 Pinia Store
 * 串联五个步骤的配置数据，支持跨步骤联动
 */
export const useModelConfigStore = defineStore('modelConfig', () => {
  // ==================== 当前步骤 ====================
  const currentStep = ref(1)

  // ==================== Step 1: 调度场景（新） ====================
  const dispatchScenario = ref({
    categoryId: '',    // 选中的大类ID: 'multi-year' | 'critical-period' | 'realtime'
    subOptionId: '',   // 选中的子选项ID
    scenarioName: '',  // 方案名称
  })

  // ==================== Step 2: 调度主体（新） ====================
  const dispatchSubject = ref({
    startTime: '',
    endTime: '',
    timeStep: '每日',
    scheduleFrequency: '不限制',
    selectedReservoirIds: [] as string[],
    selectedGroupId: '',  // 预设组合ID，空=自定义
  })

  // ==================== Step 1: 调度数据 ====================
  const modelData = ref({
    activeMenuId: 'inflow-level',
    dateRange: ['2025-05-19', '2025-05-25'] as [string, string],
    // 预留：后续改为勾选参与计算的数据项
    selectedDataIds: [] as string[],
  })

  // ==================== Step 2: 基础配置 ====================
  const basicConfig = ref({
    startTime: '2025-05-16',
    endTime: '2025-05-26',
    timeStep: '每日',
    scheduleFrequency: '每月一次',
    schemeName: '',
    selectedReservoirGroup: 'long-liu',
    selectedObjectives: ['flood-control'] as string[],
    constraintEnabled: [] as boolean[],
  })

  // ==================== Step 3: 模型算法 ====================
  const modelAlgorithm = ref({
    selectedModel: 'lro',
    selectedAlgorithm: 'nsga2',
    parameters: {
      populationSize: 200,
      iterationCount: 500,
      crossoverRate: 0.9,
      mutationRate: 0.1,
      eliteRate: 0.05,
      crowdingFactor: 2.0,
    } as Record<string, number>,
  })

  // ==================== Step 4: 场景约束 ====================
  const scenarioConstraint = ref({
    scenarioType: 'typical',
    scenarioDescription: '',
    params: {
      westRoute: 'all',
      sedimentFlow: '1800',
      sedimentRequirement: 'min',
      ecologicalFlow: '200',
      icePreventionFlow: '200',
    } as Record<string, string>,
  })

  // ==================== 步骤完成状态 ====================
  const stepCompleted = ref<boolean[]>([false, false, false, false, false, false])

  // ==================== 计算属性 ====================

  /** 已完成步骤数 */
  const completedCount = computed(() => stepCompleted.value.filter(Boolean).length)

  /** 是否所有步骤都已完成 */
  const allCompleted = computed(() => stepCompleted.value.every(Boolean))

  /** 当前步骤标题（新 6 步流程） */
  const stepTitles = ['调度场景', '调度主体', '调度数据', '模型算法', '场景配置', '配置汇总']

  /** 旧 5 步流程标题（兼容旧页面） */
  const oldStepTitles = ['调度数据', '基础配置', '模型算法', '场景配置', '配置汇总']

  const currentStepTitle = computed(() => stepTitles[currentStep.value - 1] || '')

  // ==================== 步骤间联动计算属性 ====================

  /** 当前水库组合兼容的模型ID列表（Step 2 → Step 3） */
  const compatibleModelIds = computed(() => {
    const groupId = basicConfig.value.selectedReservoirGroup
    return reservoirGroupModelMap[groupId] || ['lro']
  })

  /** 当前水库组合兼容的模型选项列表（带名称） */
  const compatibleModels = computed(() => {
    const allModels = dispatchModels.data || []
    const ids = compatibleModelIds.value
    return allModels.filter(m => ids.includes(m.id))
  })

  /** 当前模型兼容的算法列表（Step 3 内部联动） */
  const compatibleAlgorithms = computed(() => {
    const allAlgos = optimizationAlgorithms.data || []
    const models = dispatchModels.data || []
    const model = models.find(m => m.id === modelAlgorithm.value.selectedModel)
    if (!model) return allAlgos
    return allAlgos.filter(a => model.supportedAlgorithms.includes(a.id))
  })

  /** 当前算法是否与模型兼容 */
  const isAlgorithmCompatible = computed(() => {
    return compatibleAlgorithms.value.some(a => a.id === modelAlgorithm.value.selectedAlgorithm)
  })

  /** 根据时间步长建议的参数值（Step 2 → Step 3） */
  const suggestedParamsByTimeStep = computed(() => {
    return timeStepParamSuggestions[basicConfig.value.timeStep] || timeStepParamSuggestions['每日']
  })

  /** 当前调度目标关联的场景参数ID（Step 2 → Step 4） */
  const relevantScenarioParamIds = computed(() => {
    const ids = new Set<string>()
    basicConfig.value.selectedObjectives.forEach(objId => {
      const relevant = objectiveRelevantParams[objId]
      if (relevant) relevant.forEach(id => ids.add(id))
    })
    return ids
  })

  /** 模型中文名 */
  const modelDisplayName = computed(() => {
    return modelLabelMap[modelAlgorithm.value.selectedModel] || modelAlgorithm.value.selectedModel
  })

  /** 算法中文名 */
  const algorithmDisplayName = computed(() => {
    return algorithmLabelMap[modelAlgorithm.value.selectedAlgorithm] || modelAlgorithm.value.selectedAlgorithm
  })

  // ==================== 步骤操作 ====================

  /** 设置当前步骤 */
  const setStep = (step: number) => {
    if (step >= 1 && step <= 6) {
      currentStep.value = step
    }
  }

  /** 标记步骤已完成 */
  const markStepCompleted = (step: number) => {
    if (step >= 1 && step <= 6) {
      stepCompleted.value[step - 1] = true
    }
  }

  /** 重置所有步骤完成状态 */
  const resetSteps = () => {
    stepCompleted.value = [false, false, false, false, false, false]
  }

  // ==================== 步骤间联动方法 ====================

  /** 从 Step 1 调度数据同步时间范围到 Step 2 */
  const syncBasicConfigFromModelData = () => {
    if (modelData.value.dateRange && modelData.value.dateRange.length === 2) {
      basicConfig.value.startTime = modelData.value.dateRange[0]
      basicConfig.value.endTime = modelData.value.dateRange[1]
    }
  }

  /** 切换水库组合时，确保当前选中的模型仍然兼容，否则自动切换到第一个兼容模型 */
  const ensureCompatibleModelOnGroupChange = (newGroupId: string) => {
    const oldGroupId = basicConfig.value.selectedReservoirGroup
    basicConfig.value.selectedReservoirGroup = newGroupId

    // 检查当前模型是否兼容新组合
    const compatibleIds = reservoirGroupModelMap[newGroupId] || ['lro']
    if (!compatibleIds.includes(modelAlgorithm.value.selectedModel)) {
      // 自动切换到第一个兼容模型
      modelAlgorithm.value.selectedModel = compatibleIds[0]
    }

    // 检查算法兼容性
    const models = dispatchModels.data || []
    const model = models.find(m => m.id === modelAlgorithm.value.selectedModel)
    if (model && !model.supportedAlgorithms.includes(modelAlgorithm.value.selectedAlgorithm)) {
      if (model.supportedAlgorithms.length > 0) {
        modelAlgorithm.value.selectedAlgorithm = model.supportedAlgorithms[0]
      }
    }
  }

  /** 切换调度目标时，返回受影响场景参数ID列表 */
  const getAffectedScenarioParamIds = () => {
    const ids = new Set<string>()
    basicConfig.value.selectedObjectives.forEach(objId => {
      const relevant = objectiveRelevantParams[objId]
      if (relevant) relevant.forEach(id => ids.add(id))
    })
    return Array.from(ids)
  }

  /** 切换时间步长时，返回建议的参数调整 */
  const getSuggestedParamsForTimeStep = (newTimeStep: string) => {
    return timeStepParamSuggestions[newTimeStep] || null
  }

  /** 应用时间步长建议参数到 Step 3 */
  const applyTimeStepToAlgorithmParams = (newTimeStep: string) => {
    const suggestions = timeStepParamSuggestions[newTimeStep]
    if (suggestions) {
      Object.entries(suggestions).forEach(([key, value]) => {
        if (key in modelAlgorithm.value.parameters) {
          modelAlgorithm.value.parameters[key] = value
        }
      })
    }
  }

  // ==================== Step 1 操作（调度场景）====================
  const setDispatchScenario = (data: Partial<typeof dispatchScenario.value>) => {
    Object.assign(dispatchScenario.value, data)
  }

  /**
   * 根据子选项ID联动调度目标
   * 从 dispatchScenarioCategories 中查找对应的 linkedObjectives
   */
  const syncObjectivesFromScenario = (subOptionId: string) => {
    const scenarioObjectiveMap: Record<string, string[]> = {
      'multi-objective': ['flood-control', 'power-generation', 'ecology'],
      'flood': ['flood-control'],
      'ice': ['flood-control'],
      'supply': ['power-generation'],
      'sediment-period': ['sediment'],
      'ice-sediment': ['flood-control', 'sediment'],
      'cross-section': ['sediment'],
      'reach': ['sediment'],
      'multi-energy': ['multi-energy'],
    }
    const objectives = scenarioObjectiveMap[subOptionId] || []
    basicConfig.value.selectedObjectives = objectives
  }

  /**
   * 根据场景联动模型选择
   * 从 scenarioModelMap 和 scenarioSubOptionModelMap 中查找兼容模型
   */
  const syncModelFromScenario = (categoryId: string, subOptionId: string) => {
    // 优先使用子选项的推荐模型
    const recommendedModel = scenarioSubOptionModelMap[subOptionId]
    if (recommendedModel) {
      modelAlgorithm.value.selectedModel = recommendedModel
    } else {
      // 否则使用大类兼容的模型列表中的第一个
      const compatibleIds = scenarioModelMap[categoryId] || ['lro']
      modelAlgorithm.value.selectedModel = compatibleIds[0]
    }

    // 联动算法：检查当前算法是否与新模型兼容
    const allModels = dispatchModels.data || []
    const model = allModels.find(m => m.id === modelAlgorithm.value.selectedModel)
    if (model && !model.supportedAlgorithms.includes(modelAlgorithm.value.selectedAlgorithm)) {
      if (model.supportedAlgorithms.length > 0) {
        modelAlgorithm.value.selectedAlgorithm = model.supportedAlgorithms[0]
      }
    }
  }

  // ==================== Step 2 操作（调度主体）====================
  const setDispatchSubject = (data: Partial<typeof dispatchSubject.value>) => {
    Object.assign(dispatchSubject.value, data)
  }

  // ==================== Step 1 操作（调度场景）====================
  const setModelData = (data: Partial<typeof modelData.value>) => {
    Object.assign(modelData.value, data)
  }

  // ==================== Step 2 操作 ====================
  const setBasicConfig = (data: Partial<typeof basicConfig.value>) => {
    Object.assign(basicConfig.value, data)
  }

  const setConstraintEnabled = (enabled: boolean[]) => {
    basicConfig.value.constraintEnabled = enabled
  }

  // ==================== Step 3 操作 ====================
  const setModelAlgorithm = (data: Partial<typeof modelAlgorithm.value>) => {
    Object.assign(modelAlgorithm.value, data)
  }

  const setAlgorithmParam = (key: string, value: number) => {
    modelAlgorithm.value.parameters[key] = value
  }

  // ==================== Step 4 操作 ====================
  const setScenarioConstraint = (data: Partial<typeof scenarioConstraint.value>) => {
    Object.assign(scenarioConstraint.value, data)
  }

  const setScenarioParam = (key: string, value: string) => {
    scenarioConstraint.value.params[key] = value
  }

  // ==================== 重置 ====================
  /** 重置所有配置 */
  const resetAll = () => {
    currentStep.value = 1
    dispatchScenario.value = {
      categoryId: '',
      subOptionId: '',
    }
    dispatchSubject.value = {
      startTime: '',
      endTime: '',
      timeStep: '每日',
      scheduleFrequency: '不限制',
      selectedReservoirIds: [],
      selectedGroupId: '',
    }
    modelData.value = {
      activeMenuId: 'inflow-level',
      dateRange: ['2025-05-19', '2025-05-25'],
      selectedDataIds: [],
    }
    basicConfig.value = {
      startTime: '2025-05-16',
      endTime: '2025-05-26',
      timeStep: '每日',
      scheduleFrequency: '每月一次',
      schemeName: '',
      selectedReservoirGroup: 'long-liu',
      selectedObjectives: ['flood-control'],
      constraintEnabled: [],
    }
    modelAlgorithm.value = {
      selectedModel: 'lro',
      selectedAlgorithm: 'nsga2',
      parameters: {
        populationSize: 200,
        iterationCount: 500,
        crossoverRate: 0.9,
        mutationRate: 0.1,
        eliteRate: 0.05,
        crowdingFactor: 2.0,
      },
    }
    scenarioConstraint.value = {
      scenarioType: 'typical',
      scenarioDescription: '',
      params: {
        westRoute: 'all',
        sedimentFlow: '1800',
        sedimentRequirement: 'min',
        ecologicalFlow: '200',
        icePreventionFlow: '200',
      },
    }
    resetSteps()
  }

  return {
    // 状态
    currentStep,
    dispatchScenario,
    dispatchSubject,
    modelData,
    basicConfig,
    modelAlgorithm,
    scenarioConstraint,
    stepCompleted,

    // 计算属性
    completedCount,
    allCompleted,
    currentStepTitle,
    stepTitles,
    oldStepTitles,

    // 步骤间联动计算属性
    compatibleModelIds,
    compatibleModels,
    compatibleAlgorithms,
    isAlgorithmCompatible,
    suggestedParamsByTimeStep,
    relevantScenarioParamIds,
    modelDisplayName,
    algorithmDisplayName,

    // 步骤操作
    setStep,
    markStepCompleted,
    resetSteps,

    // 步骤间联动方法
    syncBasicConfigFromModelData,
    ensureCompatibleModelOnGroupChange,
    getAffectedScenarioParamIds,
    getSuggestedParamsForTimeStep,
    applyTimeStepToAlgorithmParams,

    // Step 1（调度场景）
    setDispatchScenario,
    syncObjectivesFromScenario,
    syncModelFromScenario,

    // Step 2（调度主体）
    setDispatchSubject,

    // Step 1（调度数据）
    setModelData,

    // Step 2
    setBasicConfig,
    setConstraintEnabled,

    // Step 3
    setModelAlgorithm,
    setAlgorithmParam,

    // Step 4
    setScenarioConstraint,
    setScenarioParam,

    // 重置
    resetAll,
  }
})
