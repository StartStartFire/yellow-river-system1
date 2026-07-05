/**
 * Step 4: 模型算法 Mock 数据
 *
 * 包含调度目标、约束汇总、模型/算法列表、算法参数定义。
 */
import type {
  DispatchObjective,
  ConstraintSummaryData,
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
      id: 'flood-control',
      name: '防洪安全',
      description: '保障水库防洪安全，控制水位与下泄流量',
      icon: 'shield',
    },
    {
      id: 'power-generation',
      name: '兴利发电',
      description: '优化发电出力，提高综合经济效益',
      icon: 'flash',
    },
    {
      id: 'ecology',
      name: '生态保护',
      description: '保障生态流量，维护下游生态环境',
      icon: 'leaf',
    },
    {
      id: 'sediment',
      name: '输沙调度',
      description: '优化水沙过程，减少库区淤积，保障冲沙效果',
      icon: 'sand',
    },
    {
      id: 'multi-energy',
      name: '多能互补',
      description: '协调水电与风光等新能源，提高多能互补综合效益',
      icon: 'sync',
    },
  ] as DispatchObjective[],
}

export const constraintSummary = {
  code: 200,
  message: 'success',
  data: {
    count: 12,
    description: '约束条件将影响调度方案的可行性与优化结果',
    constraints: [
      { name: '水位上限约束', min: 2450, max: 2600, unit: 'm' },
      { name: '水位下限约束', min: 2420, max: 2580, unit: 'm' },
      { name: '汛限水位约束', min: 2450, max: 2590, unit: 'm' },
      { name: '最小生态流量约束', min: 200, max: 500, unit: 'm³/s' },
      { name: '最大发电出力约束', min: 800, max: 3200, unit: 'MW' },
      { name: '最小下泄流量约束', min: 300, max: 1200, unit: 'm³/s' },
      { name: '冲沙流量约束', min: 800, max: 3000, unit: 'm³/s' },
      { name: '库容边界约束', min: 50, max: 580, unit: '亿m³' },
      { name: '入库流量边界约束', min: 500, max: 4000, unit: 'm³/s' },
      { name: '出库流量边界约束', min: 300, max: 3500, unit: 'm³/s' },
      { name: '水量平衡约束', min: 0, max: 100, unit: '%' },
      { name: '梯级协同约束', min: 0, max: 24, unit: 'h' },
    ],
  } as ConstraintSummaryData,
}

export const modelAlgorithmState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 3,
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
  } as ModelAlgorithmState,
}

export const dispatchModels = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'lro',
      name: '水库群优化调度模型',
      supportedAlgorithms: ['nsga2', 'pso'],
    },
    {
      id: 'multi_objective_stress',
      name: '多目标协同胁迫模型',
      supportedAlgorithms: ['nsga2', 'pso'],
    },
    {
      id: 'multi_objective_dispatch',
      name: '多目标优化调度模型',
      supportedAlgorithms: ['paem'],
    },
    {
      id: 'water_sediment_realtime',
      name: '水沙实时调度模型',
      supportedAlgorithms: ['nsga3'],
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
      paramIds: ['populationSize', 'iterationCount', 'crossoverRate', 'mutationRate', 'eliteRate', 'crowdingFactor'],
    },
    {
      id: 'pso',
      name: 'PSO 粒子群优化算法',
      paramIds: ['populationSize', 'iterationCount', 'inertiaWeight', 'cognitiveFactor', 'socialFactor'],
    },
    {
      id: 'paem',
      name: 'PAEM 逐步逼近评价方法',
      paramIds: ['iterationCount', 'convergenceThreshold', 'approximationStep'],
    },
    {
      id: 'nsga3',
      name: 'NSGA-III 多目标遗传算法',
      paramIds: ['populationSize', 'iterationCount', 'crossoverRate', 'mutationRate', 'eliteRate', 'divisionNumber'],
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
      min: 50,
      max: 1000,
      step: 10,
      description: '种群规模越大，搜索更充分，结果更稳定，但计算耗时增加；种群规模越小，计算更快，但容易遗漏优良解。',
    },
    {
      id: 'iterationCount',
      name: '迭代次数',
      value: 500,
      min: 100,
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
      description: '交叉概率越高，种群探索能力更强；交叉概率越低，解集变化较慢，可能影响搜索效率。',
    },
    {
      id: 'mutationRate',
      name: '变异概率 Pm',
      value: 0.1,
      min: 0.01,
      max: 0.3,
      step: 0.01,
      description: '变异概率越高，跳出局部最优能力更强，但过高会导致结果波动；变异概率越低，结果更稳定，但探索不足。',
    },
    {
      id: 'eliteRate',
      name: '精英保留比例',
      value: 0.05,
      min: 0.01,
      max: 0.2,
      step: 0.01,
      description: '精英保留比例越高，保留优良解更多，但可能降低种群多样性；精英保留比例越低，多样性更高，但优良解可能丢失。',
    },
    {
      id: 'crowdingFactor',
      name: '拥挤度因子',
      value: 2.0,
      min: 1.0,
      max: 3.0,
      step: 0.1,
      description: '拥挤度因子用于控制解集分布的均匀性，数值越大越强调解集分散性，数值越小越强调局部收敛效果。',
    },
    {
      id: 'inertiaWeight',
      name: '惯性权重 w',
      value: 0.8,
      min: 0.2,
      max: 1.2,
      step: 0.05,
      description: '惯性权重控制粒子保持当前速度的程度，越大越利于全局搜索，越小越利于局部精细搜索。',
    },
    {
      id: 'cognitiveFactor',
      name: '个体学习因子 c₁',
      value: 1.5,
      min: 0.5,
      max: 3.0,
      step: 0.1,
      description: '个体学习因子控制粒子向自身历史最优位置学习的程度，越大越强调个体经验。',
    },
    {
      id: 'socialFactor',
      name: '社会学习因子 c₂',
      value: 1.5,
      min: 0.5,
      max: 3.0,
      step: 0.1,
      description: '社会学习因子控制粒子向群体全局最优位置学习的程度，越大越强调群体经验。',
    },
    {
      id: 'convergenceThreshold',
      name: '收敛阈值 ε',
      value: 0.001,
      min: 0.0001,
      max: 0.01,
      step: 0.0001,
      description: '收敛阈值决定算法何时停止迭代，阈值越小精度越高但耗时越长，阈值越大收敛越快但精度降低。',
    },
    {
      id: 'approximationStep',
      name: '逼近步长 Δ',
      value: 0.01,
      min: 0.001,
      max: 0.1,
      step: 0.001,
      description: '逼近步长控制每次迭代的逼近幅度，步长越小精度越高但收敛慢，步长越大收敛快但可能跳过最优解。',
    },
    {
      id: 'divisionNumber',
      name: '参考点划分数 H',
      value: 10,
      min: 4,
      max: 30,
      step: 1,
      description: '参考点划分数决定目标空间切分粒度，划分越多解集分布越均匀，但计算量显著增大。',
    },
  ] as AlgorithmParameter[],
}
