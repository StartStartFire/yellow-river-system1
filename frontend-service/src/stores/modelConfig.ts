import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  reservoirGroupModelMap,
  scenarioModelMap,
  scenarioSubOptionModelMap,
  objectiveRelevantParams,
  modelLabelMap,
  algorithmLabelMap,
} from '@/mock/model-config/linkage'
import { dispatchModels, optimizationAlgorithms } from '@/mock/model-config/modelAlgorithm'

/**
 * 模型配置 Pinia Store
 *
 * 串联 6 个步骤的配置数据，支持跨步骤联动：
 *   Step 1 调度场景 → Step 2 调度主体 → Step 3 调度数据
 *   → Step 4 模型算法 → Step 5 场景约束 → Step 6 配置汇总
 *
 * 当前阶段：对接"多目标协同胁迫调度模型"（stress），
 * 其他模型/场景标记为 placeholder 占位。
 */
export const useModelConfigStore = defineStore('modelConfig', () => {
  // ==================== 全局步骤状态 ====================
  const currentStep = ref(1)
  const stepCompleted = ref<boolean[]>([false, false, false, false, false, false])

  // ==================== Step 1: 调度场景 ====================
  const step1State = ref({
    categoryId: '',    // 选中的大类ID: 'multi-year' | 'critical-period' | 'realtime'
    subOptionId: '',   // 选中的子选项ID
    scenarioName: '',  // 方案名称
  })

  // ==================== Step 2: 调度主体 ====================
  const step2State = ref({
    startTime: '',
    endTime: '',
    timeStep: '每日',
    scheduleFrequency: '不限制',
    selectedReservoirIds: [] as string[],
    selectedGroupId: '',  // 预设组合ID，空=自定义
  })

  // ==================== Step 3: 调度数据 ====================
  const step3State = ref({
    activeMenuId: 'inflow-level',
    dateRange: ['2025-05-19', '2025-05-25'] as [string, string],
    // 预留：后续改为勾选参与计算的数据项
    selectedDataIds: [] as string[],
  })

  // ==================== Step 4: 模型算法 ====================
  const step4State = ref({
    selectedModel: 'stress',
    selectedAlgorithm: 'nsga2',
    selectedObjectives: ['water-shortage', 'power-generation'] as string[],
    parameters: {
      populationSize: 15,
      iterationCount: 30,
      crossoverRate: 0.9,
      // mutationRate/eliteRate/crowdingFactor 已废弃删除
    } as Record<string, number>,
    // 约束参数
    initialWaterLevelLongyangxia: null as number | null,  // 龙羊峡起调水位(m)
    initialWaterLevelLiujiaxia: null as number | null,    // 刘家峡起调水位(m)
    icePreventionFlows: null as number[] | null,           // 防凌流量 [11月,12月,1月,2月,3月](m³/s)
  })

  // ==================== Step 5: 场景约束 ====================
  const step5State = ref({
    scenarioType: 'typical',
    scenarioDescription: '',
    params: {
      westRoute: 'all',
      sedimentFlow: '1800',
      // sedimentRequirement/ecologicalFlow/icePreventionFlow 当前阶段暂不处理
    } as Record<string, string>,
  })

  // ==================== 计算属性 ====================

  /** 已完成步骤数 */
  const completedCount = computed(() => stepCompleted.value.filter(Boolean).length)

  /** 是否所有步骤都已完成 */
  const allCompleted = computed(() => stepCompleted.value.every(Boolean))

  /** 当前步骤标题（新 6 步流程） */
  const stepTitles = ['调度场景', '调度主体', '调度数据', '模型算法', '场景配置', '配置汇总']
  const currentStepTitle = computed(() => stepTitles[currentStep.value - 1] || '')

  /**
   * 根据选中的目标数量计算 M 值
   * 协同胁迫模型：2 个目标 → M=2，3 个目标 → M=3
   */
  const computedMValue = computed(() => {
    return step4State.value.selectedObjectives.length
  })

  // ==================== 步骤间联动计算属性 ====================

  /** 当前水库组合兼容的模型选项列表（Step 2 → Step 4） */
  const compatibleModels = computed(() => {
    const groupId = step2State.value.selectedGroupId
    const compatibleIds = reservoirGroupModelMap[groupId] || ['stress']
    const allModels = dispatchModels.data || []
    return allModels.filter(m => compatibleIds.includes(m.id))
  })

  /** 当前调度目标关联的场景参数ID（Step 4 → Step 5） */
  const relevantScenarioParamIds = computed(() => {
    const ids = new Set<string>()
    step4State.value.selectedObjectives.forEach(objId => {
      const relevant = objectiveRelevantParams[objId]
      if (relevant) relevant.forEach(id => ids.add(id))
    })
    return ids
  })

  /** 模型中文名 */
  const modelDisplayName = computed(() => {
    return modelLabelMap[step4State.value.selectedModel] || step4State.value.selectedModel
  })

  /** 算法中文名 */
  const algorithmDisplayName = computed(() => {
    return algorithmLabelMap[step4State.value.selectedAlgorithm] || step4State.value.selectedAlgorithm
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

  // ==================== Step 1 操作（调度场景）====================

  const setDispatchScenario = (data: Partial<typeof step1State.value>) => {
    Object.assign(step1State.value, data)
  }

  /**
   * 根据子选项ID联动调度目标
   * 当前只处理 multi-objective → 缺水量/发电量/协同度
   */
  const syncObjectivesFromScenario = (subOptionId: string) => {
    const scenarioObjectiveMap: Record<string, string[]> = {
      'multi-objective': ['water-shortage', 'power-generation', 'coordination'],
    }
    const objectives = scenarioObjectiveMap[subOptionId] || []
    // 默认勾选前两个
    step4State.value.selectedObjectives = objectives.length >= 2
      ? objectives.slice(0, 2)
      : objectives
  }

  /**
   * 根据场景联动模型选择
   * 从 scenarioModelMap 和 scenarioSubOptionModelMap 中查找兼容模型
   */
  const syncModelFromScenario = (categoryId: string, subOptionId: string) => {
    // 优先使用子选项的推荐模型
    const recommendedModel = scenarioSubOptionModelMap[subOptionId]
    if (recommendedModel) {
      step4State.value.selectedModel = recommendedModel
    } else {
      const compatibleIds = scenarioModelMap[categoryId] || ['stress']
      step4State.value.selectedModel = compatibleIds[0] || 'stress'
    }

    // 联动算法：检查当前算法是否与新模型兼容
    const allModels = dispatchModels.data || []
    const model = allModels.find(m => m.id === step4State.value.selectedModel)
    if (model && !model.supportedAlgorithms.includes(step4State.value.selectedAlgorithm)) {
      if (model.supportedAlgorithms.length > 0) {
        step4State.value.selectedAlgorithm = model.supportedAlgorithms[0]
      }
    }
  }

  /**
   * 根据场景联动调度主体（Step 1 → Step 2）
   * 当前只处理 multi-year/multi-objective → 预设龙羊峡+刘家峡，日期可修改
   */
  const syncSubjectFromScenario = (categoryId: string, subOptionId: string) => {
    if (categoryId === 'multi-year' && subOptionId === 'multi-objective') {
      step2State.value = {
        startTime: '1970',
        endTime: '2023',
        timeStep: '20时段/年',
        scheduleFrequency: '无',
        selectedReservoirIds: ['longyangxia', 'liujiaxia'],
        selectedGroupId: 'long-liu',
      }
    }
    // 其他场景暂不处理（保持现有值）
  }

  // ==================== Step 2 操作（调度主体）====================

  const setDispatchSubject = (data: Partial<typeof step2State.value>) => {
    Object.assign(step2State.value, data)
  }

  // ==================== Step 3 操作（调度数据）====================

  const setModelData = (data: Partial<typeof step3State.value>) => {
    Object.assign(step3State.value, data)
  }

  // ==================== Step 4 操作（模型算法）====================

  const setModelAlgorithm = (data: Partial<typeof step4State.value>) => {
    // 合并传入的数据
    Object.assign(step4State.value, data)

    // 切换到 PAEM 时自动添加 kMut 参数
    if (data.selectedAlgorithm === 'paem' && step4State.value.parameters.kMut === undefined) {
      step4State.value.parameters = {
        ...step4State.value.parameters,
        kMut: 50,
      }
    }

    // 切换到 NSGA-II 时自动移除 kMut 参数
    if (data.selectedAlgorithm === 'nsga2') {
      const { kMut, ...rest } = step4State.value.parameters
      step4State.value.parameters = rest
    }
  }

  const setAlgorithmParam = (key: string, value: number) => {
    step4State.value.parameters[key] = value
  }

  // ==================== Step 5 操作（场景约束）====================

  const setScenarioConstraint = (data: Partial<typeof step5State.value>) => {
    Object.assign(step5State.value, data)
  }

  const setScenarioParam = (key: string, value: string) => {
    step5State.value.params[key] = value
  }

  // ==================== 重置 ====================

  /** 重置所有配置 */
  const resetAll = () => {
    currentStep.value = 1
    step1State.value = {
      categoryId: '',
      subOptionId: '',
      scenarioName: '',
    }
    step2State.value = {
      startTime: '',
      endTime: '',
      timeStep: '每日',
      scheduleFrequency: '不限制',
      selectedReservoirIds: [],
      selectedGroupId: '',
    }
    step3State.value = {
      activeMenuId: 'inflow-level',
      dateRange: ['2025-05-19', '2025-05-25'],
      selectedDataIds: [],
    }
    step4State.value = {
      selectedModel: 'stress',
      selectedAlgorithm: 'nsga2',
      selectedObjectives: ['water-shortage', 'power-generation'],
      parameters: {
        populationSize: 15,
        iterationCount: 30,
        crossoverRate: 0.9,
      },
    }
    step5State.value = {
      scenarioType: 'typical',
      scenarioDescription: '',
      params: {
        westRoute: 'all',
        sedimentFlow: '1800',
      },
    }
    resetSteps()
  }

  return {
    // 状态（return key 保留语义化命名，避免破坏外部引用）
    currentStep,
    stepCompleted,
    dispatchScenario: step1State,
    dispatchSubject: step2State,
    modelData: step3State,
    modelAlgorithm: step4State,
    scenarioConstraint: step5State,

    // 计算属性
    completedCount,
    allCompleted,
    currentStepTitle,
    stepTitles,
    computedMValue,

    // 步骤间联动计算属性
    compatibleModels,
    relevantScenarioParamIds,
    modelDisplayName,
    algorithmDisplayName,

    // 步骤操作
    setStep,
    markStepCompleted,
    resetSteps,

    // Step 1（调度场景）
    setDispatchScenario,
    syncObjectivesFromScenario,
    syncModelFromScenario,
    syncSubjectFromScenario,

    // Step 2（调度主体）
    setDispatchSubject,

    // Step 3（调度数据）
    setModelData,

    // Step 4（模型算法）
    setModelAlgorithm,
    setAlgorithmParam,

    // Step 5（场景约束）
    setScenarioConstraint,
    setScenarioParam,

    // 重置
    resetAll,
  }
})
