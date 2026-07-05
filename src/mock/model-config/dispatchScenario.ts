/**
 * Step 1: 调度场景 Mock 数据
 */
import type { DispatchScenarioCategory } from '@/types/model'

export const dispatchScenarioCategories: DispatchScenarioCategory[] = [
  {
    id: 'multi-year',
    name: '多年的中长期调度',
    icon: 'calendar',
    description: '以年为单位的长期调度规划，统筹多目标水资源配置，适用于年度调度方案编制与中长期水资源优化分配',
    subOptions: [
      {
        id: 'multi-objective',
        name: '多目标优化调度',
        description: '综合考虑防洪、发电、生态、供水等多目标协同优化',
        linkedObjectives: ['flood-control', 'power-generation', 'ecology'],
      },
    ],
  },
  {
    id: 'critical-period',
    name: '年内关键期调度',
    icon: 'wave',
    description: '针对年内特定关键时期制定精细化调度方案，满足各时期差异化调度需求',
    subOptions: [
      {
        id: 'flood',
        name: '防洪期',
        description: '主汛期防洪调度，控制水库水位保障防洪安全',
        linkedObjectives: ['flood-control'],
      },
      {
        id: 'ice',
        name: '防凌期',
        description: '凌汛期防凌调度，控制下泄流量防止冰塞冰坝',
        linkedObjectives: ['flood-control'],
      },
      {
        id: 'supply',
        name: '供水期',
        description: '供水保障调度，保障城乡生活与工农业供水安全',
        linkedObjectives: ['power-generation'],
      },
      {
        id: 'sediment-period',
        name: '调水调沙',
        description: '水沙联合调度，利用洪水过程输沙减淤',
        linkedObjectives: ['sediment'],
      },
    ],
  },
  {
    id: 'realtime',
    name: '实时调度',
    icon: 'lightning',
    description: '基于实时水情和预报信息的应急响应与精细调度，应对突发水情沙情变化',
    subOptions: [
      {
        id: 'ice-sediment',
        name: '凌峰水沙调度',
        description: '凌汛期水沙过程调控，协调防凌与输沙关系',
        linkedObjectives: ['flood-control', 'sediment'],
      },
      {
        id: 'cross-section',
        name: '断面输沙调度',
        description: '控制断面输沙率，保障下游河道输沙效率',
        linkedObjectives: ['sediment'],
      },
      {
        id: 'reach',
        name: '区间冲淤调度',
        description: '控制河段冲淤平衡，减少库区与河道淤积',
        linkedObjectives: ['sediment'],
      },
      {
        id: 'multi-energy',
        name: '多能互补',
        description: '协调水电与风光等新能源，提高多能互补综合效益',
        linkedObjectives: ['multi-energy'],
      },
    ],
  },
]
