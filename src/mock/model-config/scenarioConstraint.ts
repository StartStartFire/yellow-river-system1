/**
 * Step 5: 场景约束 Mock 数据
 */
import type {
  ScenarioConstraintState,
  ScenarioParam,
  ConstraintItem,
} from '@/types/model'

export const scenarioConstraintState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 4,
    scenarioType: 'typical',
    scenarioDescription:
      '典型场景基于历史调度经验与水文条件组合，用于评估不同调度策略下的系统响应。适用于常规调度方案的模拟与优化分析。',
    params: {
      westRoute: 'all',
      sedimentFlow: '1800',
      sedimentRequirement: 'min',
      ecologicalFlow: '200',
      icePreventionFlow: '200',
    },
  } as ScenarioConstraintState,
}

export const scenarioTypeOptions = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'typical',
      name: '典型场景',
      description: '基于历史调度经验与水文条件组合形成的预设场景',
    },
    {
      id: 'custom',
      name: '自定义场景',
      description: '由用户自行定义调度场景和约束参数',
    },
  ],
}

export const scenarioParams = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'westRoute',
      name: '西线调水',
      value: 'all',
      options: [
        { label: '无', value: 'none' },
        { label: '上线', value: 'upper' },
        { label: '下线', value: 'lower' },
        { label: '上线+下线', value: 'all' },
      ],
    },
    {
      id: 'sedimentFlow',
      name: '调沙流量',
      value: '1800',
      options: [
        { label: '1600 m³/s', value: '1600' },
        { label: '1800 m³/s', value: '1800' },
        { label: '2000 m³/s', value: '2000' },
        { label: '自定义', value: 'custom' },
      ],
    },
    {
      id: 'sedimentRequirement',
      name: '冲沙流量要求',
      value: 'min',
      options: [
        { label: '不考虑', value: 'none' },
        { label: '满足最小冲沙流量', value: 'min' },
        { label: '满足推荐冲沙流量', value: 'recommended' },
        { label: '自定义冲沙流量', value: 'custom' },
      ],
    },
    {
      id: 'ecologicalFlow',
      name: '下游生态流量',
      value: '200',
      options: [
        { label: '80 m³/s', value: '80' },
        { label: '100 m³/s', value: '100' },
        { label: '150 m³/s', value: '150' },
        { label: '200 m³/s', value: '200' },
        { label: '250 m³/s', value: '250' },
        { label: '300 m³/s', value: '300' },
      ],
    },
    {
      id: 'icePreventionFlow',
      name: '防凌流量',
      value: '200',
      options: [
        { label: '100 m³/s', value: '100' },
        { label: '150 m³/s', value: '150' },
        { label: '200 m³/s', value: '200' },
        { label: '250 m³/s', value: '250' },
        { label: '300 m³/s', value: '300' },
      ],
    },
  ] as ScenarioParam[],
}

export const constraintList = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'level',
      name: '水库水位约束',
      description: '龙羊峡水库、刘家峡水库、青铜峡水库',
      status: 'configured',
    },
    {
      id: 'flow',
      name: '流量过程约束',
      description: '下游控制断面流量满足过程要求',
      status: 'configured',
    },
    {
      id: 'flood',
      name: '防洪安全约束',
      description: '水库汛限水位约束，洪水期防洪安全',
      status: 'configured',
    },
    {
      id: 'power',
      name: '发电约束',
      description: '满足发电任务要求，保证电站出力',
      status: 'configured',
    },
    {
      id: 'sediment',
      name: '泥沙冲淤约束',
      description: '满足最小冲沙流量要求',
      status: 'configured',
    },
    {
      id: 'ecology',
      name: '生态流量约束',
      description: '下游生态流量不低于最小生态需水',
      status: 'configured',
    },
    {
      id: 'engineering',
      name: '工程运行约束',
      description: '泵站、闸门等工程运行状态约束',
      status: 'configured',
    },
    {
      id: 'balance',
      name: '水量平衡约束',
      description: '系统水量平衡，满足水资源可利用量',
      status: 'configured',
    },
  ] as ConstraintItem[],
}
