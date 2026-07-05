## 1. 项目定位

本项目为“黄河上游水库群调度系统”的前端原型开发项目。

当前阶段只开发前端页面，不开发后端接口，不连接数据库，不调用 MATLAB 模型，不实现真实业务计算。

当前目标是：

```text
使用 Vue3 前端技术栈 + 模拟数据，先把系统主要页面跑通。
```

---

## 2. 当前阶段开发目标

当前阶段只做：

```text
1. 前端项目结构
2. 页面路由
3. 顶部导航栏
4. 页面布局
5. 静态 UI 组件
6. 图表展示
7. 地图展示
8. mock 数据展示
9. 页面之间的基础跳转
10. 简单前端状态管理
```

当前阶段不做：

```text
1. 不开发后端接口
2. 不调用真实 API
3. 不连接数据库
4. 不调用 MATLAB
5. 不实现真实文件上传解析
6. 不实现真实 WebSocket
7. 不实现用户登录权限
8. 不实现真实 Excel 导出
9. 不实现真实任务队列
10. 不实现复杂工程部署
```

---

## 3. 技术栈约束

项目固定使用以下技术栈：

```text
Vue 3
Vite
TypeScript
Element Plus
Tailwind CSS
ECharts
Leaflet
Pinia
Vue Router
```

技术用途：

```text
Vue 3：页面开发与组件组织
Vite：前端构建工具
TypeScript：类型约束
Element Plus：表单、按钮、表格、弹窗、步骤条等基础组件
Tailwind CSS：页面布局、间距、颜色、响应式样式
ECharts：折线图、柱状图、雷达图、桑基图、帕累托图等图表
Leaflet：开源地图展示
Pinia：前端状态管理
Vue Router：页面路由
```

未经确认，不允许随意引入：

```text
React
Next.js
Nuxt
Ant Design Vue
Naive UI
D3.js
Mapbox
Cesium
Three.js
后端框架
数据库相关依赖
权限框架
微前端框架
```

如确实需要新增依赖，必须先说明原因。

---

## 4. AI 开发总原则

AI 编程必须遵守以下原则：

```text
1. 不允许一次性生成整个系统。
2. 每次只开发一个明确的小任务。
3. 不允许修改无关文件。
4. 不允许擅自更换技术栈。
5. 不允许提前开发后端接口。
6. 不允许提前接入真实 API。
7. 不允许提前接入数据库。
8. 不允许提前接入 MATLAB。
9. 页面数据优先使用 src/mock/ 中的模拟数据。
10. 页面开发必须参考 docs/page-design/ 中对应页面说明。
11. 优先跑通页面闭环，再逐步补充细节。
12. 任何改动都必须满足模块化、低耦合、可持续维护、可复用四项要求。
13. 修改前先读相关文件，理解上下文；不允许凭名称猜测结构。
```

---

## 5. 代码质量与架构原则

所有代码必须同时满足以下四项要求。每次开发或重构前先对照检查，开发后自查。

### 5.1 模块化

```text
1. 每个文件只承担一个明确职责，禁止"上帝文件"。
2. 单文件超过 400 行必须考虑拆分；超过 600 行强制拆分。
3. mock 文件按业务子模块拆分，使用目录聚合，禁止 999 行单文件聚合。
4. store 按业务流程分组（如 step1State / step2State），不要把所有字段平铺。
5. 页面视图（views）只负责编排，业务逻辑下沉到组件或 utils。
6. 复杂视图拆分为子组件目录，单 View 文件控制在 300 行以内。
```

### 5.2 低耦合

```text
1. 组件之间通过 props 向下传递，通过 emit 向上通知，禁止直接修改父组件状态。
2. 跨组件共享状态走 Pinia store，禁止通过 provide/inject 传递业务数据。
3. mock 数据按页面或子流程拆分文件，引用方直接 import 子模块，不依赖聚合入口。
4. 不允许跨业务模块互相 import 内部组件，公共能力放到 components/common/。
5. 不允许在组件内硬编码其他模块的字段名或枚举值，通过类型或常量导出。
6. store 的 return 保留语义化 key，避免破坏外部引用。
```

### 5.3 可持续维护

```text
1. 重复样式必须抽取为全局类（如 .card-header / .header-title-row），禁止散落 :deep() 覆盖。
2. Element Plus 深色主题覆盖集中到 src/styles/element-dark.css，禁止在业务组件内重复 :deep()。
3. 数值格式化逻辑统一调用 src/utils/format.ts，禁止散落 toFixed / toLocaleString。
4. CSS 变量集中定义在 src/styles/variables.css，禁止硬编码 rgba(6,20,42,...) / #8aa0b8 等颜色。
5. 业务组件删除字段前，先全局搜索引用，确认无遗留调用。
6. 每次重构后必须运行 vue-tsc --noEmit 和 vite build 双重验证。
7. 重构成果同步更新 docs/development/AI-WORKLOG.md，记录关键决策与文件索引。
```

### 5.4 可复用性

```text
1. 通用 UI 容器统一使用 src/components/common/PanelCard.vue，新增卡片优先复用。
2. 状态标签统一使用 src/components/common/StatusTag.vue，禁止再写 .status-dot / .status-badge。
3. 图表统一使用 src/components/chart/BaseChart.vue + src/utils/chart.ts 配置工厂。
4. 新增组件前先在 components/common/ 查找是否已有可复用实现。
5. 复用组件如需扩展，优先通过 props / slot 扩展，不复制粘贴相似组件。
6. SelectCard 系列（带 icon + subtitle + badge）保留 .card-base 结构，不强迁到 PanelCard。
```

---

## 6. 文档职责划分

项目文档按职责拆分。

```text
AGENTS.md
```

只写 AI 开发约束、技术栈、开发方式、目录规范、输出要求。

```text
docs/page-design/README.md
```

写全局页面设计规范，例如整体风格、导航栏、通用布局、通用组件。

```text
docs/page-design/01-home.md
docs/page-design/02-basic-data.md
docs/page-design/03-water-condition.md
docs/page-design/04-model-config.md
docs/page-design/05-process-transparent.md
docs/page-design/06-evaluation-decision.md
docs/page-design/07-case-library.md
docs/page-design/08-report-statistics.md
```

分别写每个页面的具体布局、区域划分、交互规则、图表内容和 mock 数据要求。

```text
src/mock/
```

存放每个页面对应的模拟数据。

```text
docs/requirements/system-requirements.md
```

说明系统总体初步功能需求。

```text
docs/development/AI-WORKLOG.md
docs/development/SESSIONS.md
```

说明：
- `AI-WORKLOG.md` — 项目快照（模块状态/设计规范/关键文件），新会话必读
- `SESSIONS.md` — 开发流水账，每次会话记录，滚动保留近 5 次，按需查阅

---

## 7. 推荐项目目录结构

```text
project-root/
├─ AGENTS.md
├─ package.json
├─ vite.config.ts
├─ tsconfig.json
├─ tailwind.config.js
├─ index.html
│
├─ docs/
│  ├─ requirements/
│  │  └─ system-requirements.md
│  │
│  ├─ development/
│  │  ├─ AI-WORKLOG.md                  # 项目快照，新会话必读
│  │  └─ SESSIONS.md                    # 开发流水账，滚动保留近 5 次
│  │
│  └─ page-design/
│     ├─ README.md
│     ├─ 01-home.md
│     ├─ 02-basic-data.md
│     ├─ 03-water-condition.md
│     ├─ 04-model-config/
│     │  ├─ README.md                    # 模型配置模块总说明，只写六步流程关系
│     │  ├─ 01-dispatch-scenario.md      # Step 1 调度场景
│     │  ├─ 02-dispatch-subject.md       # Step 2 调度主体
│     │  ├─ 03-model-data.md             # Step 3 模型数据
│     │  ├─ 04-model-algorithm.md        # Step 4 模型算法
│     │  ├─ 05-scenario-constraint.md    # Step 5 场景约束
│     │  └─ 06-config-summary.md         # Step 6 配置汇总
│     ├─ 05-process-transparent.md
│     ├─ 06-evaluation-decision.md
│     ├─ 07-case-library.md
│     └─ 08-report-statistics.md
│
├─ public/
│  ├─ map/
│  └─ background/                        # 全局背景图
│
└─ src/
   ├─ main.ts
   ├─ App.vue
   │
   ├─ router/
   │  └─ index.ts                        # 8 主页面 + 6 模型配置子页面
   │
   ├─ stores/
   │  ├─ app.ts                          # 全局导航 / 当前水库
   │  └─ modelConfig.ts                  # 模型配置 6 步流程状态（step1State ~ step6State）
   │
   ├─ layouts/
   │  └─ MainLayout.vue
   │
   ├─ components/
   │  ├─ common/                         # 跨模块复用组件
   │  │  ├─ PanelCard.vue                # 统一面板容器（accent / header-actions 插槽）
   │  │  └─ StatusTag.vue                # 统一状态标签（preset / label+color / pulse）
   │  ├─ chart/
   │  │  └─ BaseChart.vue                # ECharts 包装组件
   │  ├─ home/                           # 首页专用子组件
   │  ├─ basic-data/                     # 基础数据专用子组件
   │  ├─ model-config/                   # 模型配置专用子组件
   │  │  ├─ common/                      # 模型配置模块内复用（ConfirmActionDialog）
   │  │  ├─ dispatch-scenario/
   │  │  ├─ dispatch-subject/            # 注：实际目录在 views，组件可放此处
   │  │  ├─ model-data/
   │  │  ├─ model-algorithm/
   │  │  ├─ scenario-constraint/
   │  │  └─ config-summary/
   │  ├─ evaluation-decision/
   │  └─ case-library/
   │
   ├─ views/
   │  ├─ home/
   │  ├─ basic-data/
   │  ├─ water-condition/
   │  ├─ model-config/                   # 6 个子路由视图，每个独立目录
   │  │  ├─ dispatch-scenario/
   │  │  ├─ dispatch-subject/
   │  │  ├─ model-data/
   │  │  ├─ model-algorithm/
   │  │  ├─ scenario-constraint/
   │  │  └─ config-summary/
   │  ├─ process-transparent/
   │  ├─ evaluation-decision/
   │  ├─ case-library/
   │  └─ report-statistics/
   │
   ├─ mock/
   │  ├─ home.ts
   │  ├─ basicData.ts
   │  ├─ waterCondition.ts
   │  ├─ model-config/                   # 模型配置 mock 按子模块拆分
   │  │  ├─ dispatchScenario.ts
   │  │  ├─ dispatchSubject.ts
   │  │  ├─ modelData.ts
   │  │  ├─ modelAlgorithm.ts
   │  │  ├─ scenarioConstraint.ts
   │  │  ├─ configSummary.ts
   │  │  └─ linkage.ts                   # 跨步骤联动映射
   │  ├─ processTransparent.ts
   │  ├─ evaluationDecision.ts
   │  ├─ caseLibrary.ts
   │  └─ reportStatistics.ts
   │
   ├─ types/
   │  ├─ common.ts
   │  ├─ reservoir.ts
   │  ├─ model.ts
   │  ├─ process.ts
   │  └─ evaluation.ts
   │
   ├─ styles/
   │  ├─ index.css                       # Tailwind 入口 + 全局卡片/分割线类
   │  ├─ variables.css                   # CSS 变量集中定义（颜色 / rgb 三元组）
   │  └─ element-dark.css                # Element Plus 深色主题统一覆盖
   │
   └─ utils/
      ├─ chart.ts                        # ECharts 配置工厂（tooltip / axis / grid / 系列）
      ├─ format.ts                       # 数值格式化（formatNumber / formatLevel / ...）
      ├─ evaluationCharts.ts             # 评价决策图表专用配置
      └─ caseLibrary.ts                  # 案例库专用辅助
```

---

## 8. 页面开发顺序

页面建议按以下顺序开发：

```text
1. 创建 Vue3 + Vite + TypeScript 基础项目
2. 配置 Element Plus
3. 配置 Tailwind CSS
4. 配置 Vue Router
5. 配置 Pinia
6. 创建 MainLayout 和顶部导航栏
7. 创建 mock 数据目录
8. 开发首页
9. 开发基础数据页面
10. 开发模型配置页面
11. 开发过程透明页面
12. 开发评价决策页面
13. 开发水调水情页面
14. 开发案例库页面
15. 开发报表统计页面
16. 统一优化样式和组件
```

每次只允许开发其中一个任务，不允许一次性全部开发。

---

## 9. 页面开发参考

页面原型已开发完成。修修改改样式时，参考以下资源：

```text
1. 代码即真相：以实际 .vue 源码文件为准，不要凭空想象页面结构。
2. 全局设计规范：docs/page-design/README.md（颜色、布局、通用组件、状态体系）。
3. 页面速查表：docs/page-design/pages-reference.md（路由映射、状态颜色、联动规则）。
4. 所有 mock 数据：src/mock/ 目录，按页面/子模块拆分。
```

不再使用逐页的独立设计文档（已删除）。开发时不允许凭记忆猜测页面结构，必须先读实际代码。

---

## 10. 全局页面风格约束

所有页面统一采用：

```text
深色写实科技风
中国智慧水利科研平台风格
蓝青色高亮
专业后台界面
16:9 宽屏布局
适配 1920×1080 分辨率
```

页面设计要求：

```text
1. 不做浅色普通后台风格。
2. 不做卡通插画风。
3. 不做过度科幻风。
4. 不把所有图表直接铺满页面。
5. 不做密密麻麻的数据大屏。
6. 保持模块边界清晰。
7. 保持图表区域完整。
8. 保持页面留白。
9. 优先使用卡片、标签页、折叠面板组织内容。
```

---

## 11. mock 数据约束

当前阶段所有业务数据都来自前端 mock 文件。

mock 数据位置：

```text
src/mock/
```

要求：

```text
1. 页面中不允许硬编码大量业务数据。
2. 图表数据必须从 mock 文件读取。
3. 表格数据必须从 mock 文件读取。
4. 地图点位数据必须从 mock 文件读取。
5. mock 数据字段要接近未来接口字段。
6. mock 数据要方便后期替换成接口调用。
7. 单个 mock 文件超过 400 行必须按子模块拆分到目录。
8. 拆分后引用方直接 import 子模块文件，不再保留聚合入口。
9. 跨子模块的联动映射放到单独的 linkage.ts 文件。
```

mock 拆分示例（模型配置模块）：

```text
src/mock/model-config/
├─ dispatchScenario.ts      # Step 1 数据
├─ dispatchSubject.ts       # Step 2 数据
├─ modelData.ts             # Step 3 数据
├─ modelAlgorithm.ts        # Step 4 数据
├─ scenarioConstraint.ts    # Step 5 数据
├─ configSummary.ts         # Step 6 数据
└─ linkage.ts               # 跨步骤联动映射（水库组合→模型 等）
```

引用方式：

```ts
// ✅ 正确：直接 import 子模块
import { dispatchModels } from '@/mock/model-config/modelAlgorithm'

// ❌ 禁止：通过聚合入口引入
import { dispatchModels } from '@/mock/modelConfig'  // 不再使用
```

数据示例：

```ts
export const reservoirOverviewMock = {
  code: 200,
  message: 'success',
  data: {
    reservoirList: [
      {
        id: 'longyangxia',
        name: '龙羊峡水库',
        waterLevel: 2472.35,
        inflow: 1250,
        outflow: 1180,
        storage: 247.58,
        status: 'normal',
      },
    ],
  },
}
```

---

## 12. Element Plus 使用约束

Element Plus 主要用于基础交互组件。

允许使用：

```text
el-button
el-card
el-table
el-tabs
el-select
el-option
el-date-picker
el-input
el-form
el-form-item
el-steps
el-step
el-dialog
el-drawer
el-collapse
el-collapse-item
el-tag
el-progress
el-tooltip
```

要求：

```text
1. Element Plus 默认样式需要适配深色主题。
2. 不允许直接使用普通白色后台风格。
3. 表格、表单、弹窗要与系统深色风格统一。
4. 按钮颜色以蓝青色为主。
5. 深色主题覆盖集中到 src/styles/element-dark.css，分类管理（Dialog / Button / Input / Select / Table / DatePicker / Popper）。
6. 业务组件内禁止散落 :deep() 重复覆盖通用样式；仅允许写组件特有的 :deep() 微调。
7. 表格统一使用 .dark-table 类名复用全局表格样式。
```

---

## 13. ECharts 使用约束

ECharts 用于业务图表。

允许图表类型：

```text
折线图
柱状图
面积图
雷达图
桑基图
饼图
水量流向图
帕累托散点图
排名条形图
组合图
```

图表要求：

```text
1. 每个图表必须有标题。
2. 每个图表必须有单位。
3. 每个图表必须有 tooltip。
4. 每个图表必须有图例。
5. 图表颜色符合深色科技风。
6. 图表数据来自 mock 文件。
7. 图表组件尽量可复用。
```

建议封装公共组件：

```text
src/components/chart/BaseChart.vue
```

---

## 14. Leaflet 使用约束

Leaflet 用于首页或水库空间展示。

允许实现：

```text
1. 黄河上游流域底图展示
2. 水库点位标注
3. 水库名称标签
4. 点击水库点位弹出信息窗
5. 地图缩放和平移
6. 图层开关的 UI 原型
```

暂不实现：

```text
1. 不接真实 GIS 服务。
2. 不做复杂三维地形。
3. 不做 Cesium 三维地图。
4. 不做复杂空间分析。
```

地图点位数据放在：

```text
src/mock/home.ts
```

---

## 15. 路由约束

推荐路由：

```text
/
/home
/basic-data
/water-condition
/model-config
/process-transparent
/evaluation-decision
/case-library
/report-statistics
```

页面名称与导航名称保持一致：

```text
首页 → /home
基础数据 → /basic-data
水调水情 → /water-condition
模型配置 → /model-config
过程透明 → /process-transparent
评价决策 → /evaluation-decision
案例库 → /case-library
报表统计 → /report-statistics
```

---

## 16. 状态管理约束

Pinia 只做轻量状态管理。

允许存储：

```text
1. 当前导航模块
2. 当前选中的水库
3. 当前模型配置步骤
4. 当前模拟任务状态
5. 当前选中的方案
```

当前阶段不做：

```text
1. 用户权限状态
2. token 管理
3. 后端会话状态
4. 大量业务数据缓存
```

状态分组约定（以 modelConfig store 为例）：

```ts
// ✅ 推荐：按业务流程分组
const step1State = ref({
  categoryId: '',
  subOptionId: '',
  scenarioName: '',
})

const step2State = ref({
  startTime: '',
  endTime: '',
  selectedReservoirIds: [] as string[],
})

// ❌ 禁止：所有字段平铺，难维护
const categoryId = ref('')
const subOptionId = ref('')
const scenarioName = ref('')
const startTime = ref('')
const endTime = ref('')
```

return 时保留语义化 key 供外部使用：

```ts
return {
  currentStep,
  step1State,
  step2State,
  // 语义化别名（向后兼容）
  scenarioName: computed(() => step1State.value.scenarioName),
}
```

---

## 17. 命名规范

组件文件：

```text
PascalCase，例如 BaseChart.vue
```

页面目录：

```text
kebab-case，例如 model-config
```

mock 文件：

```text
camelCase，例如 modelConfig.ts
```

类型文件：

```text
camelCase，例如 reservoir.ts
```

常用变量命名：

```text
水库：reservoir
模型：model
调度周期：period
方案：scenario
任务：task
评价：evaluation
决策：decision
过程：process
```

---

## 18. AI 每次任务输出要求

每次完成代码后，AI 必须输出：

```md
## 本次完成内容

-

## 修改文件

-

## 验证

-

## 下一步建议

-
```

不允许只给代码、不说明修改内容。

涉及代码改动的任务必须运行验证：

```text
1. 类型检查：npx vue-tsc --noEmit
2. 生产构建：npx vite build
```

两者均通过才算任务完成。任一失败必须修复后再次输出"修改文件"和"验证"。

---

## 19. 最重要原则

当前阶段只做一件事：

```text
先用前端模拟数据把页面跑通。
```

---

## 20. 新会话启动指引

每次新开 AI 会话时，AI 应先执行以下步骤恢复上下文：

```text
1. 阅读 docs/development/AI-WORKLOG.md
   → 了解项目当前快照：模块状态、设计规范参数、关键文件索引、核心设计决策

2. 如需追溯近期改动原因，按需打开 docs/development/SESSIONS.md
   → 查看最近 5 次会话记录（完成内容 + 修改文件列表）

3. 如需了解页面结构、路由映射、状态颜色、联动规则，查阅 docs/page-design/pages-reference.md

4. 所有页面数据来自 src/mock/，所有业务计算均为前端模拟

5. 涉及公共组件 / 格式化 / 样式时，先查阅 src/components/common/、src/utils/format.ts、src/styles/variables.css
```

---

## 21. 代码复用强化策略

为提升可复用性，以下公共能力已建立，新增代码必须优先复用。

### 21.1 通用组件清单

| 组件 | 路径 | 用途 | 扩展点 |
|------|------|------|--------|
| PanelCard | `src/components/common/PanelCard.vue` | 统一面板容器 | `accent` 强调条 / `header-icon` / `header-actions` 插槽 |
| StatusTag | `src/components/common/StatusTag.vue` | 状态标签 | `status` 预设（normal/warning/abnormal）或 `label`+`color`+`pulse` 自定义 |
| BaseChart | `src/components/chart/BaseChart.vue` | ECharts 包装 | 通过 `option` prop 传入完整配置 |

### 21.2 复用决策树

新增 UI 块时按以下顺序判断：

```text
1. 是面板容器吗？→ 用 PanelCard
2. 含状态指示（圆点 + 文字）吗？→ 用 StatusTag
3. 是图表吗？→ 用 BaseChart + utils/chart.ts 配置工厂
4. 是表格吗？→ 用 el-table + .dark-table 全局类
5. 是 SelectCard（icon + subtitle + badge）吗？→ 用 .card-base + .card-header 全局类
6. 以上都不是？→ 新建组件，放到对应业务子目录
```

### 21.3 扩展而非复制

复用组件如需新能力，优先扩展 props / slot，禁止复制粘贴相似组件。

```vue
<!-- ✅ 正确：通过插槽扩展 PanelCard -->
<PanelCard accent title="配置汇总">
  <template #header-actions>
    <el-button>新增</el-button>
  </template>
  <Table />
</PanelCard>

<!-- ❌ 禁止：复制一份 PanelCard 改名 ConfigCard -->
```

### 21.4 全局样式类清单

以下类已定义在 `src/styles/index.css`，禁止在业务组件内重复定义：

```text
.page-panel            # 页面级统一面板
.section-label         # 分区标题
.h-divider / .v-divider  # 发光分割线
.card-base             # 带边框卡片容器
.card-flat             # 不带边框卡片容器
.card-header           # 卡片头部行
.header-title-row      # 带强调色条的标题行
.header-accent-line    # 强调色条
.header-title          # 卡片标题
.inline-bar            # 行内 Tab/筛选条
.tab-pill              # 行内 Tab 按钮
```

### 21.5 格式化工具清单

以下函数已定义在 `src/utils/format.ts`，禁止散落 `toFixed` / `toLocaleString`：

```text
formatNumber(value, digits, fallback)       # 通用数字格式化
formatThousands(value, digits, fallback)    # 千分位
formatPercent(value, digits, fallback)      # 百分比
formatWithUnit(value, unit, digits)         # 带单位
formatLevel(value)                          # 水位（2位小数）
formatFlow(value)                           # 流量（1位小数）
formatStorage(value)                        # 库容（2位小数）
formatPower(value)                          # 发电量（千分位整数）
formatScore(value)                          # 评价得分（3位小数）
```

---
