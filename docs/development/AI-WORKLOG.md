
# AI 编程工作记录（AI-WORKLOG）

本文档用于记录当前项目开发进度，方便在新开 AI 会话时快速恢复上下文。

------

## 1. 当前已完成内容

| 序号 | 模块       | 完成情况        | 说明 |
| ---- | ---------- | --------------- | ---- |
| 1    | 项目初始化 | 已完成          | Vue3 + Vite + TS + Element Plus + Tailwind CSS + ECharts + Leaflet + Pinia |
| 2    | 路由配置   | 已完成          | 8 个路由：home, basic-data, water-condition, model-config, process-transparent, evaluation-decision, case-library, report-statistics |
| 3    | 顶部导航栏 | 已完成          | 深色科技风，蓝青色高亮，支持路由跳转 |
| 4    | 首页       | 已完成          | 地图展示 + 水库点位 + 概览指标卡片 + 水情简报 |
| 5    | 基础数据   | 已完成          | 水库选择 + 断面示意图 + 基础信息 + 过程数据表格 + 机组工况 |
| 6    | 水调水情   | 未开始          | 骨架页面 |
| 7    | 模型配置   | Step 1~3 已完成 | Step 1 模型数据页面 + Step 2 基础配置页面 + Step 3 模型算法页面 |
| 8    | 过程透明   | 未开始          | 骨架页面 |
| 9    | 评价决策   | 未开始          | 骨架页面 |
| 10   | 案例库     | 未开始          | 骨架页面 |
| 11   | 报表统计   | 未开始          | 骨架页面 |

### 已完成模块详细说明

**首页（HomeView）**：全功能完成。包含流域地图（Leaflet）、水库水位卡片、水情简报表格、实时指标展示。

**基础数据（BasicDataView）**：核心功能完成。包含：
- 水库选择切换（5 个水库：龙羊峡、刘家峡、公伯峡、积石峡、青铜峡）
- 水库断面示意图（ReservoirSectionGraph.vue）— 深水科技风，含特征水位线、当前水位高亮、水流标注、工程参数栏
- 基础信息（3 组卡片：工程属性、特征水位、调度规则），5 个水库各有独立数据
- 过程数据表格（水位/入库/出库趋势）
- 机组工况列表（运行/停机/检修状态）

------

## 2. 最近一次开发记录

### 开发时间

```text
2026-06-12（第六次）
```

### 本次完成内容

```text
1. 模型配置 Step 3「模型算法」页面全功能开发完成（ModelAlgorithmView.vue）：
   - 步骤条联动：Step 1→Step 2→Step 3，支持点击已完成步骤返回
   - 调度模型选择：Element Plus 下拉框，4 种模型可选，默认"水库群优化调度模型"
   - 优化算法选择：模型联动，切换模型时自动过滤算法，默认"NSGA-II 多目标遗传算法"
   - 算法参数设置：6 个参数卡片（3×2 网格布局），含滑块+数值输入框双向联动
     - 种群规模（50-1000，默认200）
     - 迭代次数（100-2000，默认500）
     - 交叉概率 Pc（0.50-1.00，默认0.90）
     - 变异概率 Pm（0.01-0.30，默认0.10）
     - 精英保留比例（0.01-0.20，默认0.05）
     - 拥挤度因子（1.00-3.00，默认2.00）
   - 参数说明 Tooltip：鼠标悬浮问号图标显示参数说明文字
   - 滑块+数值联动：拖动滑块同步更新数值，手动输入同步更新滑块，step 取整
   - Element Plus 滑块深色适配（按钮/轨道/进度条颜色）
   - 底部操作栏：取消（确认弹窗）/ 上一步 / 保存（确认弹窗）/ 下一步
2. 补充 Step 3 mock 数据（modelConfig.ts）：
   - modelAlgorithmState / dispatchModels / optimizationAlgorithms / algorithmParameters
```

### 本次未完成内容

```text
1. 模型配置 Step 4~5 仅创建骨架页面，未实现具体功能
2. 其他页面（水调水情、过程透明、评价决策、案例库、报表统计）未开始
```

------

## 3. 下一步开发任务

下一步优先做：

```text
任务名称：模型配置 Step 4「场景约束」页面开发
```

任务目标：

```text
1. 参考 docs/page-design/04-model-config/04-scenario-constraint.md 开发 Step 4 页面
2. 在 src/mock/modelConfig.ts 中补充 Step 4 的 mock 数据
3. 实现步骤条联动（Step 3 → Step 4）
4. 保持深色科技风统一风格
```

不允许修改：

```text
1. 不修改技术栈
2. 不修改全局导航顺序
3. 不修改无关页面
4. 不接真实接口
```

其它候选任务（按优先级排序）：

```text
任务 1：开发模型配置 Step 4「场景约束」页面
任务 2：开发模型配置 Step 5「配置汇总」页面
任务 3：开发水调水情页面
```

------

## 4. 当前重要约束

开发必须参考：

```text
AGENTS.md
docs/requirements/system-requirements.md
docs/page-design/README.md
docs/page-design/PAGE-DOC-GUIDE.md
docs/page-design/具体页面.md
```

开发原则：

```text
1. 每次只做一个小任务
2. 不一次性生成整个系统
3. 不修改无关文件
4. 页面数据来自 src/mock/
5. 页面风格统一遵循 docs/page-design/README.md
6. 页面功能边界遵循 docs/requirements/system-requirements.md
```

技术栈固定：

```text
Vue 3 + Vite + TypeScript + Element Plus + Tailwind CSS + ECharts + Leaflet + Pinia + Vue Router
不允许随意引入 React / Ant Design Vue / D3.js / Mapbox / Cesium / Three.js 等
```

------

## 5. 当前项目运行方式

```bash
npm run dev
```

### 关键文件

```text
src/components/chart/ReservoirSectionGraph.vue                    -- 断面示意图组件
src/mock/basicData.ts                                              -- 基础数据 mock（含 5 个水库全量数据）
src/mock/modelConfig.ts                                            -- 模型配置 mock 数据
src/views/basic-data/BasicDataView.vue                             -- 基础数据页面
src/views/model-config/model-data/ModelDataView.vue                -- 模型配置 Step 1 页面
src/views/model-config/basic-config/BasicConfigView.vue            -- 模型配置 Step 2 页面
src/views/model-config/model-algorithm/ModelAlgorithmView.vue      -- 模型配置 Step 3 页面（本次新增）
src/components/model-config/ModelConfigStepBar.vue                 -- 模型配置步骤条组件
src/components/basic-data/BaseInfoPanel.vue                        -- 基础信息卡片组件
src/styles/index.css                                               -- 全局样式（:root:root CSS 变量覆盖）
docs/development/AI-WORKLOG.md                                     -- 本文件
```
