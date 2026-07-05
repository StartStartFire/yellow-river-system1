# 开发会话记录

> **维护规则**：每次新增记录追加到顶部（`##` 标题行上方），保留最近 **5 条**，超过的自动删除。

---

## 2026-07-05（第三十次） — 设计文档合并为页面速查表

### 完成内容

```text
背景：页面原型已全部开发完成，后续主要是修修改改样式。
     14 个独立的页面设计文档维护成本高，且容易与代码不一致，
     AI 新会话读 8 个大文档反成噪点。

方案 B 执行：
  1. 创建 docs/page-design/pages-reference.md （548 行详细速查表）
     包含：
     - 全站路由映射表（14 个路由 → View 文件）
     - 8 个主页面速查（文件索引、子组件清单、公共组件使用、状态颜色映射、交互说明）
     - 模型配置 6 步流程 + Store 字段速查 + Mock 目录 + 跨步骤联动规则
     - 全站状态颜色速查表（10 种业务状态 → 颜色 → StatusTag 用法）
     - 常用格式化函数速查（8 个函数 + 示例）
     - 跨页面业务流程图

  2. 删除 14 个旧页面设计文档 + 04-model-config/README.md
     包括：
     - 01-home.md / 02-basic-data.md / 03-water-condition.md
     - 04-model-config/ 下 8 个文件（README + 7 步骤文档）
     - 05-process-transparent.md / 06-evaluation-decision.md
     - 07-case-library.md / 08-report-statistics.md

  3. 更新 AGENTS.md 第 9 章
     从"页面设计引用规则（逐页文档）"改为"页面开发参考（代码即真相 + README + 速查表）"

  4. 更新 AGENTS.md 第 20 章
     新会话启动指引第 3 步改为指向 pages-reference.md

  5. 同步更新 AI-WORKLOG.md
     公共能力（必读）新增 pages-reference.md 和 README.md 的索引
     核心决策记录新增"设计文档合并为速查表"
```

### 修改文件

```text
docs/page-design/pages-reference.md           — 新建（548 行）
AGENTS.md                                      — 更新第 9 章、第 20 章
docs/development/AI-WORKLOG.md                 — 更新关键文件索引 + 核心决策记录
docs/page-design/ 下 14 个旧文件                — 全部删除
```

### 验证

```text
文档更新不涉及代码改动，无需构建验证。
已验证 AGENTS.md 章节编号连续、引用路径有效。
```

---

## 2026-07-05（第二十九次） — 架构原则文档升级 + 过程透明页面 bug 修复

### 完成内容

```text
本次会话分两个阶段：架构文档升级 + 运行时 bug 修复。

阶段一：AGENTS.md 规则升级 + AI-WORKLOG.md 同步
  围绕"模块化 / 低耦合 / 可持续维护 / 可复用"四项要求，更新 AGENTS.md：

  1. 第 4 章新增第 12、13 条总原则（四项要求 + 修改前先读文件）
  2. 新增第 5 章「代码质量与架构原则」，分四小节明确：
     - 5.1 模块化（400/600 行阈值、step{n}State 分组、View ≤300 行）
     - 5.2 低耦合（props/emit、直接 import 子模块、禁止跨模块 import）
     - 5.3 可持续维护（样式集中、format.ts、CSS 变量、双重验证）
     - 5.4 可复用性（PanelCard/StatusTag/BaseChart 优先复用）
  3. 第 7 章目录结构对齐实际项目（6 步子目录、mock 子模块拆分、element-dark.css、format.ts）
  4. 第 11 章 mock 约束新增 400 行拆分阈值、直接 import 子模块、linkage.ts
  5. 第 12 章 ELP 约束新增 element-dark.css 集中管理、.dark-table 复用、禁止散落 :deep()
  6. 第 16 章状态管理新增 step{n}State 分组示例和 return 语义化别名约定
  7. 第 18 章 AI 输出要求新增"验证"段，强制 vue-tsc + vite build 双重验证
  8. 第 20 章新会话启动指引新增第 5 条（查阅公共组件/format/variables）
  9. 新增第 21 章「代码复用强化策略」：通用组件清单、复用决策树、扩展而非复制、
     全局样式类清单、格式化工具清单

  同步更新 docs/development/AI-WORKLOG.md：
  - 新增「📋 近期重构成果」章节，表格列出 6 项重构成果
  - 「🎨 当前设计规范」颜色改为变量形式，新增 CSS 变量集中定义、ELP 深色覆盖两行
  - 「🧭 关键文件索引」新增「公共能力（必读）」分组，模型配置按 6 步拆分列出 7 个 mock 子模块
  - 新增「🏗️ 架构原则与核心决策」章节，9 条核心决策记录 + 验证流程

阶段二：过程透明页面 bug 修复
  现象：点击"过程透明"页面打不开，再点其他页面其他页面也不显示。

  根本原因：
  ProcessTransparentView.vue 第 180 行使用了 TECH_CYAN_LIGHT 常量，
  但第 9-11 行 import 语句漏掉了这个常量。
  buildReservoirOption 在 computed 中被调用，组件渲染时抛出
  ReferenceError: TECH_CYAN_LIGHT is not defined，导致组件渲染失败，
  错误冒泡到路由层面使后续路由切换也无法渲染。

  修复：
  1. import 语句补充 TECH_CYAN_LIGHT
  2. status 初始值 'running'（英文）→ '运行中'（中文），与 statusColor 判断逻辑一致
  3. 修复 PanelCard 重构遗留的 :deep() 选择器：
     .panel-header / .panel-title / .panel-body → .section-header / .section-title / .section-body
     让底部 5 个卡片的紧凑样式重新生效

  反思：
  vue-tsc 这次居然没报错（TS 对未导入变量检测不完全可靠），
  印证了 AGENTS.md 第 18 章双重验证的必要性。
  后续涉及 import 改动时，应在浏览器实际打开页面验证渲染正常。
```

### 修改文件

```text
AGENTS.md                                              — 新增第 5、21 章，更新第 4/7/11/12/16/18/20 章
docs/development/AI-WORKLOG.md                         — 新增重构成果、架构原则章节，更新设计规范和文件索引
src/views/process-transparent/ProcessTransparentView.vue — 修复 TECH_CYAN_LIGHT 未导入 bug + status 初始值 + :deep() 选择器
```

### 验证

```text
npx vue-tsc --noEmit   ✅ 通过
npx vite build         ✅ 通过（12.94s）
```

---

## 2026-07-03（第二十八次） — 全局字体颜色全面提亮

### 完成内容

```text
全局字体颜色全面提亮 — 解决深色背景上文字对比度不足、看不清楚的问题：

1. 全局颜色变量更新：
   - tech-muted（Tailwind）：#7a8fa3 → #8aa0b8
   - --el-text-color-secondary（Element Plus）：#7a8fa3 → #8aa0b8
   - --el-text-color-placeholder（Element Plus）：#5a6f83 → #6e8a9e

2. 全项目硬编码颜色替换（24 个 Vue 组件/视图文件）：
   - #7a8fa3 → #8aa0b8（约 150 处）
   - #5a6f83 → #6e8a9e（约 35 处）
   - 覆盖所有 scoped CSS 样式块和 ECharts 图表配置中的文字颜色

3. 修改文件（25 个）：
   tailwind.config.js、src/styles/index.css、PanelCard.vue、ModelConfigStepBar.vue、
   ModelConfigFooter.vue、HomeFooterBar.vue、BasinMapPanel.vue、HomeView.vue、
   WaterConditionView.vue、BasicDataView.vue、ReportStatisticsView.vue、
   CaseLibraryView.vue、EvaluationDecisionView.vue、ProcessTransparentView.vue、
   ConfigSummaryView.vue、ScenarioConstraintView.vue、DispatchSubjectView.vue、
   ModelAlgorithmView.vue、ModelDataView.vue、DispatchScenarioView.vue、
   ReservoirSectionGraph.vue、KeyCurvesPanel.vue、EngineeringInfo.vue、
   ReservoirMonitorPanel.vue、WaterLevelChart.vue、WarningPanel.vue、
   LoadChart.vue、PowerStatisticsPanel.vue、ReservoirSidebar.vue、
   ProcessChart.vue、MetricCards.vue
```

---

## 2026-07-03（第二十七次） — 首页面板透明度 + 渐变优化

### 完成内容

```text
首页面板透明度 + 渐变优化：

1. 首页侧边面板添加不透明背景：
   - .side-panel 新增 background: rgba(6, 20, 42, 0.92)
   - 解决面板块（z-index:1）被底层地图（z-index:0）穿透的问题
   - 图表和表格文字不再与地图底图叠加，清晰可辨

2. 侧边面板改为渐变半透明：
   - 左面板：linear-gradient(90deg, rgba-right不透明 → rgba-left透明 0.25)
   - 右面板：linear-gradient(270deg, rgba-left不透明 → rgba-right透明 0.25)
   - 面板边缘不透明保证文字可读，面向地图中心方向逐渐透明过渡

修改文件：
  src/views/home/HomeView.vue — .side-panel/.left-panel/.right-panel 样式更新
```

---

## 2026-07-03（第二十六次） — 修复页面模糊

### 完成内容

```text
修复页面模糊（糊糊的）问题 — 系统性调整透明度、模糊效果和字体渲染：

1. 字体渲染修复：
   - body 从 antialiased（灰度抗锯齿）改为 subpixel-antialiased（亚像素渲染）
   - Windows 上文字笔画更饱满清晰

2. backdrop-filter blur 层层叠加修复：
   - 全项目原有 25 处 backdrop-filter: blur()，高斯模糊多层级叠加导致背景图失真
   - 移除所有页面级 blur(16px)（13 个视图文件）
   - 移除子组件冗余 blur（筛选栏、地图工具、popup 等 8 处）
   - MainLayout 导航栏 blur 从 20px → 12px（唯一保留的模糊层）
   - 全项目仅剩 1 处 backdrop-filter（MainLayout 导航栏）

3. 页面背景透明度统一提高：
   - 所有页面 .xxx-view 背景从 0.65 / 0.88 → 统一 0.92
   - MainLayout 导航栏透明度从 0.72 → 0.85
   - 全局 .page-panel 透明度同步更新
   - 背景图穿透减少，图表和文字更清晰

修改文件（15 个）：
  src/styles/index.css、src/layouts/MainLayout.vue、
  src/views/basic-data/BasicDataView.vue、WaterConditionView.vue、HomeView.vue、
  DispatchScenarioView.vue、ModelDataView.vue、ModelAlgorithmView.vue、
  DispatchSubjectView.vue、ScenarioConstraintView.vue、ConfigSummaryView.vue、
  ProcessTransparentView.vue、EvaluationDecisionView.vue、CaseLibraryView.vue、
  ReportStatisticsView.vue、BasinMapPanel.vue、HomeFooterBar.vue
```

---

```
