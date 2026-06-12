
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
| 7    | 模型配置   | Step 1 已完成   | 模型数据页面（5 步流程中的 Step 1） |
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
2026-06-12（第四次）
```

### 本次完成内容

```text
1. Mock 数据格式标准化：所有 mock 文件（home.ts, basicData.ts）统一为 { code, message, data } API 响应格式，所有消费组件已同步更新
2. 文档更新：01-home.md、02-basic-data.md 中的 mock 数据示例更新为统一格式
3. 模型配置 Step 1「模型数据页面」全功能开发完成：
   - 5 步流程步骤条（ModelConfigStepBar.vue）
   - 左侧可折叠数据目录（调度输入/原始表格两组菜单，SVG 图标）
   - 右侧 ECharts 双轴折线面积图（入库流量左轴 + 水位右轴）
   - 右侧 Element Plus 深色表格（原始表格数据）
   - 顶部操作栏（上传数据、下载模板按钮）
   - 底部操作栏（取消、保存、下一步按钮）
   - 菜单切换时图表/表格联动
4. 修复 CSS 层叠问题：
   - Element Plus 日期选择器白色背景 → 通过 :root:root CSS 变量覆盖
   - 表格单元格白色背景 → 通过 :root:root 覆盖 --el-table-row-bg-color 等变量
   - 输入框边框白色 → Element Plus 使用 box-shadow inset 而非 border，需同时设置 box-shadow: none
   - 全局 @layer 内规则被 Element Plus 无层叠 CSS 覆盖，改用 :root:root 双倍 specificity 绕过
5. Bug 修复：表格切换到图表时图表空白 → 切换为非图表类型时 dispose 销毁实例而非 clear
```

### 本次未完成内容

```text
1. 模型配置 Step 2~5 未开发
2. Element Plus 弹框组件（如日期选择器下拉面板）的深色适配可能需要进一步处理
3. 其他页面（水调水情、过程透明、评价决策、案例库、报表统计）未开始
```

------

## 3. 下一步开发任务

下一步优先做：

```text
任务名称：模型配置 Step 2「基础配置」页面开发
```

任务目标：

```text
1. 参考 docs/page-design/04-model-config/02-basic-config.md 开发 Step 2 页面
2. 在 src/mock/modelConfig.ts 中补充 Step 2 的 mock 数据
3. 实现步骤条联动（Step 1 → Step 2）
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
任务 1：开发模型配置 Step 2「基础配置」页面
任务 2：开发模型配置 Step 3「模型算法」页面
任务 3：开发模型配置 Step 4「场景约束」页面
任务 4：开发模型配置 Step 5「配置汇总」页面
任务 5：开发水调水情页面
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
src/components/model-config/ModelConfigStepBar.vue                 -- 模型配置步骤条组件
src/components/basic-data/BaseInfoPanel.vue                        -- 基础信息卡片组件
src/styles/index.css                                               -- 全局样式（:root:root CSS 变量覆盖）
docs/development/AI-WORKLOG.md                                     -- 本文件
```
