/**
 * Step 2: 调度主体 Mock 数据
 *
 * 包含水库列表、预设组合、场景到调度主体的预填映射、场景约束。
 */
import type { ReservoirNameMap, ReservoirIdName } from '@/types/reservoir'
import type {
  SubjectReservoirGroup,
  ScenarioToSubjectDefault,
  ScenarioCategoryConstraint,
} from '@/types/model'

/** 水库ID → 显示名称映射 */
export const reservoirNameMap: ReservoirNameMap = {
  longyangxia: '龙羊峡水库',
  liujiaxia: '刘家峡水库',
  qingtongxia: '青铜峡水库',
  gongboxia: '公伯峡水库',
  jishixia: '积石峡水库',
  yangqu: '羊曲水库',
  banduo: '班多水库',
  cihaxia: '茨哈峡水库',
  maerdang: '玛尔挡水库',
  xiaoxia: '小峡水库',
  daxia: '大峡水库',
  wujinxia: '乌金峡水库',
  heishanxia: '黑山峡水库',
}

/** 所有可选水库列表 */
export const allReservoirs: ReservoirIdName[] = [
  { id: 'longyangxia', name: '龙羊峡水库' },
  { id: 'liujiaxia', name: '刘家峡水库' },
  { id: 'qingtongxia', name: '青铜峡水库' },
  { id: 'gongboxia', name: '公伯峡水库' },
  { id: 'jishixia', name: '积石峡水库' },
  { id: 'yangqu', name: '羊曲水库' },
  { id: 'banduo', name: '班多水库' },
  { id: 'cihaxia', name: '茨哈峡水库' },
  { id: 'maerdang', name: '玛尔挡水库' },
  { id: 'xiaoxia', name: '小峡水库' },
  { id: 'daxia', name: '大峡水库' },
  { id: 'wujinxia', name: '乌金峡水库' },
  { id: 'heishanxia', name: '黑山峡水库' },
]

/** 预设水库组合（含"全部水库"） */
export const subjectReservoirGroups: SubjectReservoirGroup[] = [
  {
    id: 'long-liu',
    name: '龙刘组合',
    reservoirIds: ['longyangxia', 'liujiaxia'],
    description: '龙羊峡+刘家峡',
  },
  {
    id: 'long-liu-hei',
    name: '龙刘黑组合',
    reservoirIds: ['longyangxia', 'liujiaxia', 'heishanxia'],
    description: '龙羊峡+刘家峡+黑山峡',
  },
  {
    id: 'all',
    name: '全部水库',
    reservoirIds: ['longyangxia', 'liujiaxia', 'qingtongxia', 'gongboxia', 'jishixia', 'yangqu', 'banduo', 'cihaxia', 'maerdang', 'xiaoxia', 'daxia', 'wujinxia', 'heishanxia'],
    description: '13 座水库',
  },
]

/** Step 1 场景 → Step 2 调度主体预填映射 */
export const scenarioToSubjectDefaults: Record<string, ScenarioToSubjectDefault> = {
  'multi-objective': {
    startTime: '2025-01-01', endTime: '2025-12-31',
    timeStep: '每月', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia', 'qingtongxia', 'gongboxia', 'jishixia'],
  },
  'flood': {
    startTime: '2025-06-01', endTime: '2025-09-30',
    timeStep: '每月', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia'],
  },
  'ice': {
    startTime: '2025-12-01', endTime: '2026-02-28',
    timeStep: '每月', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia'],
  },
  'supply': {
    startTime: '2025-03-01', endTime: '2025-06-30',
    timeStep: '每旬', scheduleFrequency: '每旬一次',
    reservoirIds: ['longyangxia', 'liujiaxia'],
  },
  'sediment-period': {
    startTime: '2025-07-01', endTime: '2025-08-31',
    timeStep: '每旬', scheduleFrequency: '每旬一次',
    reservoirIds: ['longyangxia', 'liujiaxia'],
  },
  'ice-sediment': {
    startTime: '2025-12-10', endTime: '2026-01-10',
    timeStep: '每日', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia'],
  },
  'cross-section': {
    startTime: '2025-07-01', endTime: '2025-07-31',
    timeStep: '每日', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia', 'qingtongxia'],
  },
  'reach': {
    startTime: '2025-08-01', endTime: '2025-08-31',
    timeStep: '每日', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia', 'qingtongxia', 'gongboxia', 'jishixia'],
  },
  'multi-energy': {
    startTime: '2025-06-01', endTime: '2025-06-30',
    timeStep: '每日', scheduleFrequency: '每月一次',
    reservoirIds: ['longyangxia', 'liujiaxia', 'qingtongxia', 'gongboxia', 'jishixia'],
  },
}

/** 场景大类ID → 时间/步长约束 */
export const scenarioCategoryConstraints: Record<string, ScenarioCategoryConstraint> = {
  'multi-year': { maxDays: 365 * 5, allowedTimeSteps: ['每旬', '每月'], defaultTimeStep: '每月' },
  'critical-period': { maxDays: 365, allowedTimeSteps: ['每旬', '每月'], defaultTimeStep: '每月' },
  'realtime': { maxDays: 31, allowedTimeSteps: ['每日'], defaultTimeStep: '每日' },
}
