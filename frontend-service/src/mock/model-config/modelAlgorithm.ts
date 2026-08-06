/**
 * Step 4: 模型算法 Mock 数据
 *
 * 包含调度目标、约束汇总、模型/算法列表、算法参数定义。
 * active 标记的条目是当前可用的，placeholder 是占位（后续阶段开放）。
 */
import type {
  DispatchObjective,
  ModelAlgorithmState,
  DispatchModel,
  OptimizationAlgorithm,
  AlgorithmParameter,
} from '@/types/model'

export const dispatchObjectives = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'water-shortage',
      name: '缺水量',
      description: '兰州断面多年平均缺水量最小化',
      icon: 'water',
    },
    {
      id: 'power-generation',
      name: '发电量',
      description: '梯级电站群年均发电量最大化',
      icon: 'flash',
    },
    {
      id: 'coordination',
      name: '协同度',
      description: '梯级调度系统总协同度最大化',
      icon: 'sync',
    },
  ] as DispatchObjective[],
}

export const modelAlgorithmState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 3,
    selectedModel: 'stress',
    selectedAlgorithm: 'nsga2',
    parameters: {
      populationSize: 200,
      iterationCount: 500,
      crossoverRate: 0.9,
    },
  } as ModelAlgorithmState,
}

export const dispatchModels = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'stress',
      name: '多目标协同胁迫调度模型',
      supportedAlgorithms: ['nsga2', 'paem'],
      status: 'active',
    },
    {
      id: 'lro',
      name: '水库群优化调度模型',
      supportedAlgorithms: ['nsga2'],
      status: 'placeholder',
    },
    {
      id: 'multi_objective_dispatch',
      name: '多目标优化调度模型',
      supportedAlgorithms: ['paem'],
      status: 'placeholder',
    },
    {
      id: 'water_sediment_realtime',
      name: '水沙实时调度模型',
      supportedAlgorithms: ['nsga3'],
      status: 'placeholder',
    },
  ] as DispatchModel[],
}

export const optimizationAlgorithms = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'nsga2',
      name: 'NSGA-II 多目标遗传算法',
      paramIds: ['populationSize', 'iterationCount', 'crossoverRate'],
      status: 'active',
    },
    {
      id: 'paem',
      name: 'PAEM 逐步逼近评价方法',
      paramIds: ['populationSize', 'iterationCount', 'crossoverRate', 'kMut'],
      status: 'active',
    },
    {
      id: 'pso',
      name: 'PSO 粒子群优化算法',
      paramIds: [],
      status: 'placeholder',
    },
    {
      id: 'nsga3',
      name: 'NSGA-III 多目标遗传算法',
      paramIds: [],
      status: 'placeholder',
    },
  ] as OptimizationAlgorithm[],
}

export const algorithmParameters = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'populationSize',
      name: '种群规模',
      value: 200,
      min: 10,
      max: 1000,
      step: 10,
      description: '种群规模越大，搜索更充分，但计算耗时增加；种群规模越小，计算更快，但容易遗漏优良解。',
    },
    {
      id: 'iterationCount',
      name: '迭代次数',
      value: 500,
      min: 50,
      max: 2000,
      step: 50,
      description: '迭代次数越大，收敛更充分，但运行时间更长；迭代次数越小，运行更快，但可能未充分收敛。',
    },
    {
      id: 'crossoverRate',
      name: '交叉概率 Pc',
      value: 0.9,
      min: 0.5,
      max: 1.0,
      step: 0.01,
      description: '交叉概率越高，种群探索能力更强，但过高可能破坏优良解；交叉概率越低，解集变化较慢。',
    },
    {
      id: 'kMut',
      name: '变异参数 K_mut',
      value: 50,
      min: 10,
      max: 200,
      step: 5,
      description: 'PAEM 算法专用变异参数，控制近似评价中的变异强度。值越大变异幅度越大，值越小搜索越精细。',
    },
  ] as AlgorithmParameter[],
}
