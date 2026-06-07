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
```

---

## 6. 文档职责划分

项目文档按职责拆分。

```text
Claude.md
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
│  └─ page-design/
│     ├─ README.md
│     ├─ 01-home.md
│     ├─ 02-basic-data.md
│     ├─ 03-water-condition.md
│     ├─ 04-model-config.md
│     ├─ 05-process-transparent.md
│     ├─ 06-evaluation-decision.md
│     ├─ 07-case-library.md
│     └─ 08-report-statistics.md
│
├─ public/
│  └─ map/
│
└─ src/
   ├─ main.ts
   ├─ App.vue
   │
   ├─ router/
   │  └─ index.ts
   │
   ├─ stores/
   │  ├─ app.ts
   │  └─ task.ts
   │
   ├─ layouts/
   │  └─ MainLayout.vue
   │
   ├─ components/
   │  ├─ common/
   │  ├─ chart/
   │  ├─ map/
   │  └─ panel/
   │
   ├─ views/
   │  ├─ home/
   │  ├─ basic-data/
   │  ├─ water-condition/
   │  ├─ model-config/
   │  ├─ process-transparent/
   │  ├─ evaluation-decision/
   │  ├─ case-library/
   │  └─ report-statistics/
   │
   ├─ mock/
   │  ├─ home.ts
   │  ├─ basicData.ts
   │  ├─ waterCondition.ts
   │  ├─ modelConfig.ts
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
   │  ├─ index.css
   │  ├─ variables.css
   │  └─ theme.css
   │
   └─ utils/
      ├─ chart.ts
      ├─ date.ts
      └─ format.ts
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

## 9. 页面设计引用规则

开发页面时，必须参考对应页面设计文档。

对应关系如下：

```text
首页 → docs/page-design/01-home.md
基础数据 → docs/page-design/02-basic-data.md
水调水情 → docs/page-design/03-water-condition.md
模型配置 → docs/page-design/04-model-config.md
过程透明 → docs/page-design/05-process-transparent.md
评价决策 → docs/page-design/06-evaluation-decision.md
案例库 → docs/page-design/07-case-library.md
报表统计 → docs/page-design/08-report-statistics.md
```

例如，开发模型配置页面时，允许参考：

```text
docs/page-design/README.md
docs/page-design/04-model-config.md
src/mock/modelConfig.ts
```

不允许同时开发其他页面。

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
```

示例：

```ts
export const reservoirList = [
  {
    id: 'longyangxia',
    name: '龙羊峡',
    waterLevel: 2598.42,
    inflow: 835,
    outflow: 720,
    storage: 186.5,
  },
]
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

## 下一步建议

-
```

不允许只给代码、不说明修改内容。

---

## 19. 最重要原则

当前阶段只做一件事：

```text
先用前端模拟数据把页面跑通。
```
