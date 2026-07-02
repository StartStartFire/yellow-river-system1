# 模型配置模块页面设计总说明

## 1. 模块定位

模型配置模块用于完成模型计算任务的前置配置，是系统核心流程的起点。

本模块只负责配置本次模型计算所需的调度场景、调度主体、模型数据、模型算法、场景配置，并在配置确认后进入过程透明模块。

---

## 2. 模型配置六步流程

模型配置模块采用六步流程：

```text
调度场景 → 调度主体 → 模型数据 → 模型算法 → 场景配置 → 配置汇总
```

对应页面如下：

```text
Step 1：调度场景   — 选择调度目的与业务场景
Step 2：调度主体   — 选择水库、时段与周期
Step 3：模型数据   — 上传与选择水文数据
Step 4：模型算法   — 选择模型、算法、调度目标与约束条件
Step 5：场景配置   — 配置约束条件与参数
Step 6：配置汇总   — 确认配置并开始计算
```

页面文档结构：

```text
docs/page-design/04-model-config/
├─ README.md                       ← 本文件
├─ 01-dispatch-scenario.md         ← Step 1 调度场景
├─ 02-dispatch-subject.md          ← Step 2 调度主体
├─ 01-model-data.md                ← Step 3 模型数据
├─ 04-model-algorithm.md           ← Step 4 模型算法
├─ 04-scenario-constraint.md       ← Step 5 场景配置
└─ 05-config-summary.md            ← Step 6 配置汇总
```

---

## 3. 六个步骤的职责边界

### Step 1：调度场景

用于选择本次调度的目的和业务场景类型。以调度目的/业务为驱动，取代原先以模型数据为起点的流程。

主要包括：

```text
三大场景大类：
  - 多年的中长期调度：多目标优化调度
  - 年内关键期调度：防洪期、防凌期、供水期、调水调沙
  - 实时调度：凌峰水沙调度、断面输沙调度、区间冲淤调度、多能互补
```

选择后自动联动后续步骤（调度目标、时间范围、推荐步长等）。

对应文档：
```text
docs/page-design/04-model-config/01-dispatch-scenario.md
```

---

### Step 2：调度主体

用于确定本次调度计算的时间范围、计算步长、调度频率以及参与调度的水库。

主要包括：

```text
调度时段：起止时间
时间步长：每日 / 每旬 / 每月（受场景大类约束）
调度频率：每月一次 / 每旬一次 / 每周一次 / 不限制
总时段数：自动计算
水库选择：预设组合（龙刘/龙刘黑/全部）或弹窗自定义多选
```

对应文档：
```text
docs/page-design/04-model-config/02-dispatch-subject.md
```

---

### Step 3：模型数据

用于选择、上传、查看和管理模型计算所需的输入数据。

主要包括：

```text
入库与水位
西线调水数据
水位上下限
兰州断面需水数据
龙刘区间用水数据
来水频率
```

当前阶段只做前端 mock 展示，不做真实 Excel 上传、解析、校验和入库。

对应文档：
```text
docs/page-design/04-model-config/01-model-data.md
```

---

### Step 4：模型算法

用于选择调度模型、优化算法、算法参数，同时配置本次计算的调度目标和约束条件。

主要包括：

```text
左侧：
  - 调度模型选择（联动水库组合过滤）
  - 优化算法选择（联动模型过滤）
  - 算法参数设置（列表+详情编辑）
右侧：
  - 调度目标选择（多选分区，从 Step 1 联动预填）
  - 约束条件设置（弹窗中开关+数值编辑）
```

对应文档：
```text
docs/page-design/04-model-config/04-model-algorithm.md
```

---

### Step 5：场景配置

用于配置本次计算所采用的业务场景和场景参数。

主要包括：

```text
场景类型（典型场景/自定义场景）
场景描述
场景参数（西线调水、调沙流量、骨干工程、冲沙流量、生态流量）
```

对应文档：
```text
docs/page-design/04-model-config/04-scenario-constraint.md
```

---

### Step 6：配置汇总

用于汇总展示前五步配置内容，并确认是否开始计算。

主要包括：

```text
配置方案列表（搜索、筛选、新增）
方案详情弹窗（读取 Store 中前五步配置摘要）
右侧预计计算信息（时间预估、方案数量、模型分布、算法分布）
一键运行、导出配置
```

对应文档：
```text
docs/page-design/04-model-config/05-config-summary.md
```

---

## 4. 页面之间的流程关系

模型配置六个页面按固定顺序流转：

```text
/model-config/dispatch-scenario
        ↓
/model-config/dispatch-subject
        ↓
/model-config/model-data
        ↓
/model-config/model-algorithm
        ↓
/model-config/scenario-constraint
        ↓
/model-config/config-summary
        ↓
/process-transparent
```

---

## 5. 步骤切换规则

### 5.1 默认入口

进入模型配置模块时，默认进入：

```text
/model-config/dispatch-scenario
```

即默认展示 Step 1：调度场景。

### 5.2 下一步规则

每个步骤页面底部都使用公用组件 `ModelConfigFooter.vue`：

```text
Step 1-5：取消 / 上一步（Step 2 起） / 保存 / 下一步
Step 6：上一步 / 一键运行 / 导出配置（独立底部）
```

所有按钮居中排列，通过分隔线区分。

### 5.3 步骤条状态

六个页面顶部都应展示统一的流程步骤条：

```text
1 调度场景 → 2 调度主体 → 3 模型数据 → 4 模型算法 → 5 场景配置 → 6 配置汇总
```

要求：

```text
1. 当前步骤高亮
2. 已完成步骤显示完成状态
3. 未完成步骤显示未激活状态
4. 步骤之间使用连接线表达流程关系
5. 页面切换时，步骤条状态同步更新
```

---

## 6. 数据流转关系

六个步骤之间通过 Pinia store（`src/stores/modelConfig.ts`）串联配置数据。

Store 结构：

```text
currentStep               // 当前步骤 1-6
stepCompleted[]           // 各步骤是否已完成

dispatchScenario: {       // Step 1
  categoryId, subOptionId
}

dispatchSubject: {        // Step 2
  startTime, endTime, timeStep, scheduleFrequency
  selectedReservoirIds, selectedGroupId
}

modelData: {              // Step 3
  activeMenuId, dateRange, selectedDataIds
}

basicConfig: {            // Step 4（部分）+ 旧版兼容
  selectedObjectives, constraintEnabled
  // ... 旧字段兼容
}

modelAlgorithm: {         // Step 4
  selectedModel, selectedAlgorithm, parameters
}

scenarioConstraint: {     // Step 5
  scenarioType, scenarioDescription, params
}
```

数据流转关系：

```text
Step 1 调度场景
    ↓ 联动调度目标到 Step 4
    ↓ 联动时间范围/步长到 Step 2

Step 2 调度主体
    ↓ 水库组合联动 Step 4 模型过滤
    ↓ 时间范围/步长联动 Step 3 模型数据

Step 3 模型数据
    ↓ 时间范围联动 Step 4

Step 4 模型算法
    ↓ 模型/算法传递到 Step 6 摘要
    ↓ 目标+约束写入 basicConfig

Step 5 场景配置
    ↓ 写入 Store 供 Step 6 展示

Step 6 配置汇总
    ↓ 读取前五步配置展示摘要
    ↓ 生成 mock taskId，跳转过程透明
```

当前阶段所有展示数据来自：

```text
src/mock/modelConfig.ts
src/stores/modelConfig.ts
```

不调用任何后端接口。

---

## 7. 当前阶段开发边界

### 7.1 当前阶段允许实现

```text
1. 六步页面路由
2. 六步流程步骤条
3. 每个步骤的页面 UI
4. 每个步骤的 mock 数据展示
5. 页面之间的前端跳转
6. 表单状态的前端暂存（Pinia）
7. 配置汇总页面的 mock 汇总
8. 点击开始计算后跳转过程透明页面
9. 底部操作栏公用组件
10. 约束条件在弹窗中可编辑开关
```

### 7.2 当前阶段不实现

```text
1. 不开发后端接口
2. 不调用真实 API
3. 不连接数据库
4. 不调用 MATLAB
5. 不实现真实 Excel 上传
6. 不解析真实 Excel 文件
7. 不做真实模板下载
8. 不做真实模型计算
9. 不做真实任务队列
10. 不做复杂权限控制
```

---

## 8. 统一页面结构要求

六个步骤页面都应保持统一结构：

```text
顶部系统栏
顶部导航栏
模型配置六步流程条
当前步骤主体内容
底部操作按钮（公用 ModelConfigFooter 或独立底部）
```

统一视觉要求：

```text
1. 当前导航"模型配置"高亮
2. 当前步骤在流程条中高亮
3. 页面背景、分区、按钮、图表风格保持一致
4. 表单、表格、图表都必须适配深色主题
5. 不做浅色普通后台风格
6. 不做密集数据大屏
7. 不一次性展示过多信息
```

---

## 9. 与其他模块的关系

模型配置模块是核心业务流程的起点。

流程关系为：

```text
模型配置
    ↓
过程透明
    ↓
评价决策
```

其中：

```text
模型配置：负责配置计算任务
过程透明：负责展示任务运行过程
评价决策：负责展示计算结果和评价分析
```

当前阶段中，模型配置模块点击"开始计算"后，只跳转到过程透明页面，并传递 mock taskId。

不接真实计算任务。

---

## 10. 设计变更记录

### 10.1 六步流程重构（2026-06-27）

原五步流程（模型数据 → 基础配置 → 模型算法 → 场景配置 → 配置汇总）重构为六步流程：

```text
Step 1：调度场景   ← 新增
Step 2：调度主体   ← 由原基础配置中的水库/时段部分独立
Step 3：模型数据   ← 原 Step 1
Step 4：模型算法   ← 原 Step 3 + 原基础配置中的目标/约束
Step 5：场景配置   ← 原 Step 4
Step 6：配置汇总   ← 原 Step 5
```

已删除的旧文件：
- `src/views/model-config/basic-config/BasicConfigView.vue`（旧 Step 2）
- `docs/page-design/04-model-config/02-basic-config.md`
- `docs/page-design/04-model-config/03-model-algorithm.md`
