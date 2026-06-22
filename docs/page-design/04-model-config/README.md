# 模型配置模块页面设计总说明

## 1. 模块定位

模型配置模块用于完成模型计算任务的前置配置，是系统核心流程的起点。

本模块只负责配置本次模型计算所需的数据、基础规则、模型算法、场景配置，并在配置确认后进入过程透明模块。

---

## 2. 模型配置五步流程

模型配置模块采用五步流程：

```text
模型数据 → 基础配置 → 模型算法 → 场景配置 → 配置汇总
```

对应页面如下：

```text
Step 1：模型数据
Step 2：基础配置
Step 3：模型算法
Step 4：场景配置
Step 5：配置汇总
```

推荐页面文档结构：

```text
docs/page-design/04-model-config/
├─ README.md
├─ 01-model-data.md
├─ 02-basic-config.md
├─ 03-model-algorithm.md
├─ 04-scenario-constraint.md
└─ 05-config-summary.md
```

------

## 3. 五个步骤的职责边界

### Step 1：模型数据

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
docs/page-design/model-config/01-model-data.md
```

------

### Step 2：基础配置

用于设置本次调度计算的基础规则和工程目标。

主要包括：

```text
调度周期（含总时段数统计）
方案名称
水库组合（当前仅支持龙刘组合、龙刘黑组合）
调度目标（当前支持防洪/兴利/生态/输沙/多能互补 5 项）
约束条件设置（可编辑开关弹窗）
```

该步骤决定后续可选模型和算法范围。

对应文档：

```text
docs/page-design/model-config/02-basic-config.md
```

------

### Step 3：模型算法

用于选择调度模型、优化算法和算法参数。

主要包括：

```text
模型选择
算法选择
参数配置
参数说明
```

模型和算法需要与 Step 2 中选择的调度周期保持匹配。

对应文档：

```text
docs/page-design/model-config/03-model-algorithm.md
```

------

### Step 4：场景配置

用于配置本次计算所采用的业务场景和场景参数。

主要包括：

```text
场景类型（典型场景/自定义场景）
场景描述
场景参数（西线调水、调沙流量、骨干工程、冲沙流量、生态流量）
```

**注意：约束条件配置已移至 Step 2 弹窗中编辑，Step 4 不再展示约束条件卡片。**

当前阶段只做前端状态配置和 mock 展示，不做真实约束冲突校验。

对应文档：

```text
docs/page-design/model-config/04-scenario-constraint.md
```

------

### Step 5：配置汇总

用于汇总展示前四步配置内容，并确认是否开始计算。

主要包括：

```text
配置方案列表（搜索、筛选、新增）
方案详情弹窗（展示 Store 中前四步配置摘要）
右侧预计计算信息（时间预估、方案数量、模型分布、算法分布）
一键运行、导出配置
```

当前阶段点击"一键运行"后，只生成前端 mock taskId，并跳转到过程透明页面，不调用真实接口。

对应文档：

```text
docs/page-design/model-config/05-config-summary.md
```

------

## 4. 页面之间的流程关系

模型配置五个页面按固定顺序流转：

```text
/model-config/model-data
        ↓
/model-config/basic-config
        ↓
/model-config/model-algorithm
        ↓
/model-config/scenario-constraint
        ↓
/model-config/config-summary
        ↓
/process-transparent
```

推荐路由：

```text
/model-config/model-data
/model-config/basic-config
/model-config/model-algorithm
/model-config/scenario-constraint
/model-config/config-summary
```

------

## 5. 步骤切换规则

### 5.1 默认入口

进入模型配置模块时，默认进入：

```text
/model-config/model-data
```

即默认展示 Step 1：模型数据。

### 5.2 下一步规则

每个步骤页面底部都使用公用组件 `ModelConfigFooter.vue`：

```text
Step 1：取消 / 保存 / 下一步
Step 2-4：取消 / 上一步 / 保存 / 下一步
Step 5：上一步 / 一键运行 / 导出配置
```

所有按钮居中排列，通过分隔线区分。

### 5.3 保存与取消交互规则

所有步骤的"保存"和"取消"按钮统一采用弹窗确认方式：

```text
保存按钮：
1. 点击后弹出确认弹窗，提示用户确认保存当前配置。
2. 弹窗提供"取消"和"确认保存"两个按钮。
3. 确认后保存当前步骤的前端状态，可写入 Pinia store。
4. 不调用后端接口。

取消按钮：
1. 点击后弹出确认弹窗，提示"确认取消当前操作？取消后当前页面的更改将不会保存"。
2. 弹窗提供"继续编辑"和"确认取消"两个按钮。
3. 确认取消后关闭弹窗，可返回上一页或不处理。
4. 不清空真实数据，不调用接口。
```

### 5.4 步骤条状态

五个页面顶部都应展示统一的流程步骤条：

```text
1 模型数据
2 基础配置
3 模型算法
4 场景配置
5 配置汇总
```

要求：

```text
1. 当前步骤高亮。
2. 已完成步骤显示完成状态。
3. 未完成步骤显示未激活状态。
4. 步骤之间使用箭头或连接线表达流程关系。
5. 页面切换时，步骤条状态同步更新。
```

------

## 6. 数据流转关系

五个步骤之间通过 Pinia store（`src/stores/modelConfig.ts`）串联配置数据。

Store 结构：

```text
currentStep               // 当前步骤 1-5
stepCompleted[]           // 各步骤是否已完成

modelData: {              // Step 1
  activeMenuId
  dateRange
  selectedDataIds
}

basicConfig: {            // Step 2
  startTime, endTime, timeStep, scheduleFrequency
  schemeName, selectedReservoirGroup, selectedObjectives
  constraintEnabled       // 约束开关数组
}

modelAlgorithm: {         // Step 3
  selectedModel, selectedAlgorithm
  parameters              // { populationSize, iterationCount, ... }
}

scenarioConstraint: {     // Step 4
  scenarioType, scenarioDescription
  params                  // { westRoute, sedimentFlow, ... }
}
```

数据流转关系：

```text
Step 1 模型数据
    ↓ 写入 Store（modelData.dateRange → Step 2 预填起止时间）
    ↓ 点击"下一步"或"保存"时自动写入 Store

Step 2 基础配置
    ↓ 写入 Store（basicConfig.* → 联动 Step 3 模型筛选、Step 4 参数关联）
    ↓ 水库组合切换 → 自动检查 Step 3 模型兼容性，不兼容则自动切换
    ↓ 时间步长切换 → 自动建议 Step 3 算法参数（种群规模、迭代次数）
    ↓ 调度目标选择 → 影响 Step 4 场景参数高亮标记

Step 3 模型算法
    ↓ 写入 Store（modelAlgorithm.* → 联动 Step 4 上下文、Step 5 摘要）
    ↓ 模型列表受 Step 2 水库组合过滤
    ↓ 算法列表受所选模型过滤

Step 4 场景配置
    ↓ 写入 Store（scenarioConstraint.* → Step 5 摘要）
    ↓ 关联 Step 2 调度目标，高亮相关参数

Step 5 配置汇总
    ↓ 从 Store 读取前四步配置，展示摘要
    ↓ 生成 mock taskId，跳转过程透明
```

当前阶段所有展示数据来自：

```text
src/mock/modelConfig.ts
src/stores/modelConfig.ts
```

不调用任何后端接口。

------

## 7. 当前阶段开发边界

### 7.1 当前阶段允许实现

```text
1. 五步页面路由
2. 五步流程步骤条
3. 每个步骤的页面 UI
4. 每个步骤的 mock 数据展示
5. 页面之间的前端跳转
6. 表单状态的前端暂存（Pinia）
7. 配置汇总页面的 mock 汇总
8. 点击开始计算后跳转过程透明页面
9. 底部操作栏公用组件
10. 约束条件在 Step 2 弹窗中可编辑开关
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

------

## 8. 统一页面结构要求

五个步骤页面都应保持统一结构：

```text
顶部系统栏
顶部导航栏
模型配置五步流程条
当前步骤主体内容
底部操作按钮（公用 ModelConfigFooter 组件）
```

统一视觉要求：

```text
1. 当前导航"模型配置"高亮。
2. 当前步骤在流程条中高亮。
3. 页面背景、卡片、按钮、图表风格保持一致。
4. 表单、表格、图表都必须适配深色主题。
5. 不做浅色普通后台风格。
6. 不做密集数据大屏。
7. 不一次性展示过多信息。
```

------

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

------

## 10. 已解决的问题和设计决策

### 10.1 底部操作栏公用化

Step 1～4 的底部取消/保存/上一步/下一步按钮提取为 `ModelConfigFooter.vue` 公用组件，居中排列。
Step 5 保持独立底部（上一步 / 一键运行 / 导出配置），同样居中排列。

### 10.2 约束条件职责归并

原 Step 2 中约束条件卡片为只读，Step 4 也展示约束条件卡片。
**改为**：约束条件编辑移至 Step 2 弹窗中（带 el-switch 开关），Step 4 删除约束条件卡片，只关注场景参数配置。

### 10.3 建立 Pinia 模型配置 Store

新建 `src/stores/modelConfig.ts`，串联五个步骤的配置数据，支持跨步骤读取和后续联动。

### 10.4 Step 5 详情弹窗改为配置摘要

Step 5 的"详情"弹窗从展示 mock 方案数据改为读取 Store 中前四步的实时配置摘要，按步骤分区块展示。

### 10.5 步骤间数据联动

建立了五步之间的数据联动机制，核心实现位于 `src/stores/modelConfig.ts`：

#### 联动链路

```text
Step 1 → Step 2
  · 模型数据的时间范围 → 自动填入基础配置的起止时间
  · 点击"下一步"时自动写入 Store，Step 2 onMounted 时读取

Step 2 → Step 3
  · 水库组合切换 → 检查 Step 3 当前模型是否兼容
    （如龙刘组合不支持水沙实时调度模型，自动切换到 LRO）
  · 时间步长切换 → 建议对应的算法参数默认值
    （每日→种群200/迭代500，每旬→150/300，每月→100/200）
  · 调度目标 → 关联 Step 4 的场景参数，高亮"关联"标记

Step 2 → Step 4
  · 调度目标关联的场景参数在 Step 4 高亮显示并标记"关联"标签
  · 生态保护→下游生态流量、冲沙流量要求
  · 输沙调度→调沙流量、冲沙流量要求

Step 3 → Step 4
  · 所选模型名称传递到 Step 4 的上下文提示
```

#### 数据源

联动数据定义在 `src/mock/modelConfig.ts`：

```text
reservoirGroupModelMap      // 水库组合 → 兼容模型ID列表
timeStepParamSuggestions    // 时间步长 → 建议算法参数
objectiveRelevantParams     // 调度目标 → 关联场景参数ID
modelLabelMap               // 模型ID → 中文名称
algorithmLabelMap           // 算法ID → 中文名称
```

#### 实现方式

所有联动逻辑不依赖后端接口，纯前端实现：

```text
1. Store 中定义 computed 属性：compatibleModels、compatibleAlgorithms
2. Store 中定义联动方法：ensureCompatibleModelOnGroupChange、applyTimeStepToAlgorithmParams、syncBasicConfigFromModelData
3. 各步骤页面在关键交互事件中调用 Store 联动方法
4. 页面加载时（onMounted）从 Store 读取前一步传入的数据
5. "下一步"按钮自动将当前配置写入 Store
```

#### 视觉反馈

```text
Step 3：模型选择下拉框下方显示"当前水库组合「龙刘组合」可用的模型"提示
Step 4：场景参数列表中与调度目标关联的参数显示蓝色边框和"关联"标签
Step 4：顶部显示当前调度目标名称
```
