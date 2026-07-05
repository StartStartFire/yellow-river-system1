# AI 项目快照

读我了解项目当前状态——模块在哪、怎么跑、关键文件在哪、当前设计参数是什么。

---

## 🏃 运行项目

```bash
npm run dev
```

技术栈：**Vue 3 + Vite + TypeScript + Element Plus + Tailwind CSS + ECharts + Leaflet + Pinia + Vue Router**

所有业务数据来自 `src/mock/`，不接后端、不接数据库、不接 MATLAB。

---

## � 近期重构成果（架构优化轮次）

本轮重构围绕"模块化 / 低耦合 / 可持续维护 / 可复用"四项要求展开，共完成 6 个问题：

| # | 问题 | 成果 |
|---|------|------|
| 1 | `app.ts` 重复 Reservoir 类型 | 改用 `ReservoirBrief`，删除本地接口 |
| 2 | `mock/modelConfig.ts` 999 行单文件 | 拆分 7 个子模块 + `linkage.ts`，删除聚合入口 |
| 3 | `stores/modelConfig.ts` 字段平铺 | 改用 `step1State` ~ `step6State` 分组，删除 12 个未使用导出 |
| 4 | `.card-header` 样式散落重复 | 抽取 5 个全局类到 `index.css` |
| 5 | 数值格式化散落 | 新建 `utils/format.ts`（9 函数），迁移 60+ 处调用 |
| 6 | PanelCard / StatusTag 复用率低 | 扩展 props + 插槽，迁移 3 个组件，删除重复 CSS |

附带：`legacyBasicConfig` 迁移到 `step2State`，3 个组件改用新字段；Element Plus `:deep()` 散落覆盖集中到 `element-dark.css`，清理 19 个文件约 690 行重复样式。

> 详细规则见 `AGENTS.md` 第 5 章「代码质量与架构原则」和第 21 章「代码复用强化策略」。

---

## �📊 模块完成状态

| 序号 | 模块 | 状态 | 说明 |
|------|------|:----:|------|
| 1 | 项目初始化 | ✅ | Vite + Vue3 + TS + ELP + Tailwind + ECharts + Leaflet + Pinia |
| 2 | 路由配置 | ✅ | 13 个路由（8 主页面 + 6 模型配置子页面） |
| 3 | 顶部导航栏 | ✅ | 半透明玻璃态，蓝青色高亮，`backdrop-filter: blur(12px)` |
| 4 | 首页 | ✅ | 全屏地图背景 + 水库点位 + 左右渐变浮层面板（可收起） |
| 5 | 基础数据 | ✅ | 13 水库选择 + 断面图 + 基础信息 + 关键曲线 + 工情 |
| 6 | 水调水情 | ✅ | 入流/水位/出力/出流四页签，时间范围+水库筛选 |
| 7 | 模型配置 | ✅ | 6 步流程：调度场景 → 调度主体 → 模型数据 → 模型算法 → 场景配置 → 配置汇总 |
| 8 | 过程透明 | ✅ | 方案切换 + 6 图表 + 进度模拟 + 底部摘要 |
| 9 | 评价决策 | ✅ | Tab 导航（评价分析 / 决策分析），雷达图+桑基图+帕累托+排名 |
| 10 | 案例库 | ✅ | 7 案例（7 种图标）+ 筛选 + 详情页签 + 过程预览 |
| 11 | 报表统计 | ✅ | 逐月/逐年报表切换、多级表头、5 水库完整数据 |

---

## 🔀 模型配置 6 步流程

| 步骤 | 路由 | 页面 | 核心功能 |
|:----:|------|------|----------|
| 1 | /model-config/dispatch-scenario | 调度场景 | 3 大场景卡片 + 9 子选项 |
| 2 | /model-config/dispatch-subject | 调度主体 | 时段步长频率 + 水库选择 |
| 3 | /model-config/model-data | 模型数据 | 数据目录 + 图表/表格 |
| 4 | /model-config/model-algorithm | 模型算法 | 模型+算法+参数 + 调度目标+约束 |
| 5 | /model-config/scenario-constraint | 场景配置 | 场景类型 + 参数设置 |
| 6 | /model-config/config-summary | 配置汇总 | 方案列表 + 图表 + 一键运行 |

步骤联动通过 `src/stores/modelConfig.ts` 串联（采用 `step1State` ~ `step6State` 分组）。Mock 数据拆分到 `src/mock/model-config/` 目录，引用方直接 import 子模块文件。

---

## 🎨 当前设计规范

| 参数 | 值 |
|------|-----|
| 全局背景图 | `public/background/background.png`（`fixed` + `cover`） |
| 页面面板背景 | `rgba(6, 20, 42, 0.92)` **不含 `backdrop-filter`** |
| 导航栏 | `rgba(6, 20, 42, 0.85)` + `backdrop-filter: blur(12px)` |
| 主色 | `var(--tech-blue)` = `#00afff` |
| 强调色 | `var(--tech-cyan)` = `#00e5ff` |
| 正文文字 | `#e0e6ed` / `#c0c8d4` |
| 辅助文字 | `var(--tech-text-secondary)` = `#8aa0b8` |
| placeholder | `#6e8a9e` |
| 分割线 | `.h-divider` / `.v-divider` 发光渐变 |
| 字体渲染 | `subpixel-antialiased`（Windows 亚像素） |
| 面板风格 | 统一面板 + 发光分割线（无独立圆角卡片） |
| 首页面板 | 渐变半透明：边缘 `0.92` → 中心方向 `0.25` |
| CSS 变量 | 集中定义于 `src/styles/variables.css`（含 `--tech-blue-rgb` 三元组） |
| ELP 深色覆盖 | 集中于 `src/styles/element-dark.css`（7 类组件） |

---

## 🧭 关键文件索引

### 公共能力（必读）

| 文件 | 用途 |
|------|------|
| `src/components/common/PanelCard.vue` | 统一面板容器，支持 `accent` 强调条 + `header-icon` / `header-actions` 插槽 |
| `src/components/common/StatusTag.vue` | 统一状态标签，支持 `status` 预设或 `label`+`color`+`pulse` 自定义 |
| `src/components/chart/BaseChart.vue` | ECharts 包装组件 |
| `src/utils/format.ts` | 数值格式化工具（9 个函数：formatNumber / formatLevel / ...） |
| `src/utils/chart.ts` | ECharts 配置工厂（baseTooltip / baseCategoryXAxis / createGrid / ...） |
| `src/styles/variables.css` | CSS 变量集中定义 |
| `src/styles/element-dark.css` | Element Plus 深色主题统一覆盖 |
| `src/styles/index.css` | Tailwind 入口 + 全局卡片/分割线类（.card-base / .card-header / .header-title-row 等） |

### 模型配置（6 步流程）

| 文件 | 用途 |
|------|------|
| `src/stores/modelConfig.ts` | 6 步联动核心 Pinia Store（step1State ~ step6State 分组） |
| `src/mock/model-config/dispatchScenario.ts` | Step 1 调度场景 mock |
| `src/mock/model-config/dispatchSubject.ts` | Step 2 调度主体 mock |
| `src/mock/model-config/modelData.ts` | Step 3 模型数据 mock |
| `src/mock/model-config/modelAlgorithm.ts` | Step 4 模型算法 mock |
| `src/mock/model-config/scenarioConstraint.ts` | Step 5 场景约束 mock |
| `src/mock/model-config/configSummary.ts` | Step 6 配置汇总 mock |
| `src/mock/model-config/linkage.ts` | 跨步骤联动映射（水库组合→模型 等） |
| `src/components/model-config/ModelConfigFooter.vue` | 底部公用操作栏（取消/保存/下一步） |
| `src/components/model-config/ModelConfigStepBar.vue` | 步骤条组件（支持 5/6 步切换） |
| `src/components/model-config/common/ConfirmActionDialog.vue` | 模型配置模块内复用确认弹窗 |

### 首页

| 文件 | 用途 |
|------|------|
| `src/views/home/HomeView.vue` | 面板收起/展开控制入口 |
| `src/components/home/BasinMapPanel.vue` | Leaflet 地图全屏背景 |
| `src/components/home/ReservoirMonitorPanel.vue` | 水情监控面板 |
| `src/components/home/PowerStatisticsPanel.vue` | 发电统计面板 |
| `src/components/home/WaterLevelChart.vue` | 水位过程线 ECharts |
| `src/components/home/LoadChart.vue` | 负荷过程线 ECharts |
| `src/components/home/WarningPanel.vue` | 预警信息列表 |

### 基础数据

| 文件 | 用途 |
|------|------|
| `src/mock/basicData.ts` | 13 座水库全量 mock（含关键曲线） |
| `src/components/basic-data/ReservoirSidebar.vue` | 水库列表选择 |
| `src/components/basic-data/BaseInfoPanel.vue` | 工程属性 + 调度规则 |
| `src/components/basic-data/KeyCurvesPanel.vue` | 库容/出力/过流曲线 |
| `src/components/basic-data/EngineeringInfo.vue` | 工情信息（机组+闸门，使用 StatusTag） |
| `src/components/chart/ReservoirSectionGraph.vue` | 水库断面示意图 |

### 其他

| 文件 | 用途 |
|------|------|
| `src/layouts/MainLayout.vue` | 顶部导航栏 + 页面容器 |
| `tailwind.config.js` | 颜色定义（`tech-*` 系列） |
| `docs/page-design/04-model-config/README.md` | 模型配置模块总设计文档 |

> **流水账历史**：`docs/development/SESSIONS.md`（每次会话记录，保留近 5 次）

---

## 🏗️ 架构原则与核心决策

四项要求：**模块化 / 低耦合 / 可持续维护 / 可复用**。详见 `AGENTS.md` 第 5 章。

### 核心决策记录

| 决策 | 原因 | 影响范围 |
|------|------|----------|
| mock 按子模块拆分 + 直接 import | 避免 999 行单文件聚合，降低耦合 | `src/mock/model-config/` |
| store 使用 `step{n}State` 分组 | 业务流程清晰，便于演进 | `src/stores/modelConfig.ts` |
| 样式集中到 `element-dark.css` | 消除散落 `:deep()` 重复覆盖 | `src/styles/element-dark.css` + 19 个 Vue 文件 |
| CSS 变量集中到 `variables.css` | 禁止硬编码颜色，便于主题调整 | 全局 |
| 数值格式化集中到 `utils/format.ts` | 禁止散落 `toFixed` / `toLocaleString` | 60+ 处调用 |
| PanelCard 扩展 accent + 插槽 | 强化复用，避免复制相似卡片 | 11 处使用 |
| StatusTag 扩展 label/color/pulse | 统一状态指示，替代 `.status-dot` | 3 处使用 |
| SelectCard 系列不迁 PanelCard | header 结构差异大，强迁破坏布局 | ModelSelectCard / AlgorithmSelectCard / ObjectiveSelectCard |
| 删除 `legacyBasicConfig` | 旧字段已迁移到 `step2State`，避免双轨 | 3 个组件 |

### 验证流程

涉及代码改动的任务必须通过：

```bash
npx vue-tsc --noEmit   # 类型检查
npx vite build         # 生产构建
```

两者均通过才算任务完成。

---
