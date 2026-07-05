# 页面设计总览规范（UI Design Specification）

## 全局导航

首页 / 基础数据 / 水调水情 / 模型配置 / 过程透明 / 评价决策 / 案例库 / 报表统计

## 通用布局

- 顶部系统栏（半透明毛玻璃）
- 顶部导航栏（半透明毛玻璃，`background: rgba(6,20,42,0.85); backdrop-filter: blur(12px)`）
- 页面主体内容区（统一深色半透明面板，`background: rgba(6,20,42,0.92)`，**无 backdrop-filter**）
- **统一面板 + 发光分割线**布局风格：所有页面使用单一统一的半透明面板作为内容背景，各功能区域之间使用 1px 发光渐变分割线分隔，取消独立的浮动圆角卡片
- 图表区留白充足
- 不做密集数据大屏

## 通用组件

> 详见 `AGENTS.md` 第 21 章「代码复用强化策略」和第 21.2 节复用决策树。新增 UI 块前必须先查阅公共组件清单，优先复用，禁止复制粘贴相似组件。

- **分区面板 `PanelCard`**（`src/components/common/PanelCard.vue`）：统一面板容器，支持 `accent` 强调条 + `header-icon` / `header-actions` 插槽。所有卡片场景优先使用，禁止再手写 `.card-flat` / `.card-header`。
- **状态标签 `StatusTag`**（`src/components/common/StatusTag.vue`）：统一状态指示，支持 `status` 预设（normal/warning/abnormal）或 `label`+`color`+`pulse` 自定义。禁止再写 `.status-dot` / `.status-badge`。
- **图表包装 `BaseChart`**（`src/components/chart/BaseChart.vue`）：ECharts 统一包装组件，通过 `option` prop 传入配置。配合 `src/utils/chart.ts` 配置工厂使用。
- 发光分割线（`.h-divider` / `.v-divider`，`linear-gradient` 渐变分割线）
- 行内 Tab 按钮（`.tab-pill`，下划线高亮风格，不再使用圆角矩形边框）
- 筛选区
- 数据表格（统一使用 `.dark-table` 类名复用全局表格样式）
- 折叠面板

> 全局样式类清单见 `AGENTS.md` 第 21.4 节；格式化工具清单见第 21.5 节。

## 全局风格

- 深色写实科技风
- 中国水利调度主题的智慧水库群调度系统高保真后台大屏/专业科研平台界面
- 蓝青色高亮
- 16:9 宽屏布局
- 适配 1920×1080
- 顶部统一导航栏

- 专业、严谨、清晰。
- 页面采用真实可落地的 Web UI 设计。

突出：

- 数据可视化
- 流域地图
- 水位流量曲线
- 调度分析图表
- 监测卡片
- 状态标签
- 表格与图形结合

整体风格统一。

布局规整。

图表区留白充足

不做密集数据大屏

具有中国水利信息化平台、智慧调度中心、科研分析系统的视觉特征。

------

## 负向约束规范

禁止出现以下风格：

```text
手机APP界面
插画风
二次元
游戏UI
赛博朋克
强霓虹风
科幻驾驶舱
未来舱概念设计
夸张3D场景
过度发光
过度装饰
非真实图表
英文主界面
金融系统风格
医疗系统风格
交通系统风格
海洋主题
山水国画风
卡通元素
水滴卡通图标
```

## 色彩体系

### 主背景

```css
#021B3F
#082B55
#0A2D4D
```

要求：

1. 不允许使用大面积纯白背景。
2. 不允许使用浅色普通后台背景。

------

### 主色

```css
#00AFFF
```

用途：

- 主按钮
- 导航高亮
- 地图元素

------

### 强调色

```css
#00E5FF
```

用途：

- 图表重点曲线
- GIS河流

------

### 材质体系

### 面板风格

采用：

```text
统一深色半透明面板
轻玻璃拟态（全局背景图穿透）
```

页面级统一面板参数（应用至 `.page-panel` 或页面根容器）：

```css
background: rgba(6, 20, 42, 0.92);
/* 不设 backdrop-filter、不设 border、不设 border-radius、不设 box-shadow */
```

**说明**：已从“浮动独立圆角卡片”风格全线迁移为“统一面板 + 发光分割线”风格。每个页面最外层使用单一统一的 `.page-panel` 半透明背景，各功能区域之间仅用 1px 发光渐变分割线（`.h-divider` / `.v-divider`）分隔，不再使用独立的圆角边框卡片。**首页仍保持全屏地图背景 + 半透明玻璃浮层的例外方案**，其侧边面板参数见首页设计文档。

------

### 分区风格（替代原卡片风格）

当前使用**分区面板 + 发光分割线**替代传统的独立边框卡片。

分区内标题：

```css
/* 小写标签，大写字母间距 */
font-size: 12px; font-weight: 600;
color: #8aa0b8; letter-spacing: 0.8px;
text-transform: uppercase;
/* 不设背景、不设边框 */
```

分区要求：

1. 标题区用小写大写标签，轻量低调。
2. 内容区留白充足。
3. 分区之间用发光分割线分隔，不设独立卡片边框。
4. 不允许强霓虹发光。

------

### 分割线风格（替代原边框风格）

采用发光渐变分割线代替传统的实色边框：

水平分割线 `.h-divider`：

```css
height: 1px;
background: linear-gradient(
  90deg,
  transparent 0%,
  rgba(0, 175, 255, 0.15) 15%,
  rgba(0, 212, 255, 0.30) 50%,
  rgba(0, 175, 255, 0.15) 85%,
  transparent 100%
);
```

垂直分割线 `.v-divider`：

```css
width: 1px;
background: linear-gradient(
  180deg,
  transparent 0%,
  rgba(0, 175, 255, 0.15) 15%,
  rgba(0, 212, 255, 0.30) 50%,
  rgba(0, 175, 255, 0.15) 85%,
  transparent 100%
);
```

禁止：

```text
粗重描边
强霓虹发光
独立卡片边框
圆角容器边框

------

## GIS地图规范

地图是系统核心视觉中心。

------

### 📌 当前阶段方案（当前阶段适用）

当前为前端原型开发阶段，地图采用：


Leaflet（开源 JavaScript 地图库）
```

数据来源：

```text
src/mock/home.ts（mock 点位数据）
```

当前阶段实现范围：

```text
1. 黄河上游流域底图展示（使用免费开源底图）
2. 水库点位标注（mock 数据）
3. 水库名称标签
4. 点击水库点位弹出信息窗
5. 地图缩放和平移
6. 图层开关的 UI 原型
```

------

## 图表规范

统一采用：

```text
ECharts
```

------

### 图表类型

#### 过程线

用于：

```text
水位
流量
出力
负荷
```

------

#### 柱状图

用于：

```text
发电统计
指标评价
方案对比
```

------

#### 雷达图

用于：

```text
调度评价
综合评分
多目标表现
```

------

#### Sankey图

用于：

```text
水量平衡分析
来水去向分析
发电、生态、灌溉、生活、弃水流向展示
```

## 数据状态体系

> 优先使用 `StatusTag` 组件的预设状态渲染（`status` prop），自定义场景使用 `label`+`color`+`pulse` 模式。详见 AGENTS.md 第 21 章。

### 正常（StatusTag status="normal"）

```css
#00FF88
```

标签：

```text
正常
在线
运行中
```

------

### 预警（StatusTag status="warning"）

```css
#FFAA00
```

标签：

```text
关注
预警
风险
```

------

### 异常（StatusTag status="abnormal"）

```css
#FF4D4F
```

标签：

```text
异常
告警
超限
```

------

## 组件设计规范

统一组件库：

```text
Element Plus
```

### Element Plus 深色主题 CSS 变量

项目通过 `src/styles/index.css` 的 `:root:root` 块全局覆盖 Element Plus CSS 变量。
开发新页面时必须确保以下变量已正确设置，否则组件会回退到浅色主题默认值。

**必须覆盖的文字颜色变量**（最容易遗漏）：

```css
--el-text-color-primary: #e0e6ed;     /* 标题/强调 */
--el-text-color-regular: #c0c8d4;     /* 正文/输入框值 */
--el-text-color-secondary: #8aa0b8;   /* 辅助说明 */
--el-text-color-placeholder: #6e8a9e; /* placeholder */
--el-text-color-disabled: #4a5f73;    /* 禁用态 */
```

**必须覆盖的背景变量**：

```css
--el-fill-color-blank: transparent;   /* 输入框背景（透明继承父级卡片） */
--el-fill-color: #0d1f36;            /* 下拉菜单等填充 */
--el-fill-color-light: #0f2340;      /* hover 态等浅填充 */
--el-input-bg-color: transparent;     /* 输入框背景 */
```

**常见问题速查**：

| 现象 | 根因 | 解决 |
|------|------|------|
| 输入框是灰黑色块 | `--el-fill-color-blank` 不透明 | 改为 `transparent` |
| 文字灰蒙蒙看不清 | `--el-text-color-regular` 未覆盖 | 设为 `#c0c8d4` |
| ElMessage 出现在底部 | 命令式调用 CSS 未加载 | `main.ts` 显式 import message CSS |

---

### 通用组件

#### 数据卡片

用于：

```text
监测指标
统计指标
调度结果
```

------

#### 状态标签

统一使用 `StatusTag` 组件（`src/components/common/StatusTag.vue`）：

```text
预设模式：status="normal" / "warning" / "abnormal"
自定义模式：label="运行中" color="#00ff88" :pulse="true"
```

用于：

```text
正常
预警
异常
运行中
已完成
已终止
```

禁止再手写 `.status-dot` / `.status-badge` 等自定义状态样式。

------

#### 图表容器

统一：

```text
标题
单位
图例
操作区
图表区
```

------

#### GIS信息窗

统一：

```text
名称
属性
状态
时间
```

------

## 动效规范

允许：

```text
数字滚动
面板淡入
曲线动画
Marker脉冲
表格滚动
公告滚动
```

------

限制：

```text
禁止大面积粒子动画
禁止炫酷转场
禁止强烈发光
禁止复杂3D动画
```

------

## 页面层级规范

一级页面：

```text
首页
基础数据
水调水情
模型配置
过程透明
评价决策
案例库
```

------

二级页面：

按照业务模块展开。

统一保持：

```text
顶部导航一致
配色一致
面板一致
图表一致
地图一致
```

