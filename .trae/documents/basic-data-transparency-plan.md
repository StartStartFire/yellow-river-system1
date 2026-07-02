# 基础数据页面半透明化方案

## 目标

将基础数据页面及子组件从"纯色覆盖背景"改为半透明，让全局背景图能够穿透显示。

## 当前状态

| 文件 | 元素 | 当前透明度 | 效果 |
|------|------|-----------|------|
| [BasicDataView.vue#L101](file:///f:/CodeExercise/yellow-river-system1/src/views/basic-data/BasicDataView.vue#L101) | `.basic-data-view` | `rgba(6,20,42,0.88)` | 页面级几乎不透明，完全遮住背景图 |
| [BaseInfoPanel.vue#L86](file:///f:/CodeExercise/yellow-river-system1/src/components/basic-data/BaseInfoPanel.vue#L86) | `.section` | `rgba(6,30,70,0.5)` | 工程属性/调度规则分区有独立背景+边框+圆角 |
| [BaseInfoPanel.vue#L148](file:///f:/CodeExercise/yellow-river-system1/src/components/basic-data/BaseInfoPanel.vue#L148) | `.rule-card` | `rgba(17,37,54,0.4)` | 调度规则卡片有独立背景+边框+圆角 |
| [EngineeringInfo.vue#L181](file:///f:/CodeExercise/yellow-river-system1/src/components/basic-data/EngineeringInfo.vue#L181) | `.summary-bar` | `rgba(6,30,70,0.95)` | 工情摘要栏几乎不透明 |
| [KeyCurvesPanel.vue#L312](file:///f:/CodeExercise/yellow-river-system1/src/components/basic-data/KeyCurvesPanel.vue#L312) | `.curve-section` | `rgba(6,30,70,0.5)` | 曲线分区有独立背景 |
| [ReservoirSidebar.vue](file:///f:/CodeExercise/yellow-river-system1/src/components/basic-data/ReservoirSidebar.vue) | `.reservoir-sidebar` | `transparent` | 已经是透明，保持不变 |

## 修改方案

### 1. BasicDataView.vue — 降低页面级面板不透明度

```css
/* 改前 */
background: rgba(6, 20, 42, 0.88);

/* 改后 */
background: rgba(6, 20, 42, 0.65);
```

### 2. BaseInfoPanel.vue — 去除 `.section` 的独立卡片样式

- 移除 `background: rgba(6, 30, 70, 0.5)`
- 移除 `border: 1px solid rgba(50, 150, 255, 0.12)`
- 移除 `border-radius: 14px`
- 移除 `backdrop-filter`
- 改用底部分割线分隔两个 section
- `.section-header` 背景改为 `transparent`
- `.rule-card` 降低背景不透明度 → `rgba(17, 37, 54, 0.18)`，去除边框改用微弱底部分割线

### 3. EngineeringInfo.vue — `.summary-bar` 大幅降低不透明度

```css
/* 改前 */
background: rgba(6, 30, 70, 0.95);

/* 改后 */
background: rgba(6, 30, 70, 0.35);
```

### 4. KeyCurvesPanel.vue — `.curve-section` 去除独立背景

- 移除 `background: rgba(6, 30, 70, 0.5)`
- 保持透明

## 不改动的部分

- ReservoirSidebar — 已经是 `transparent`
- ECharts 图表 tooltip 的 `rgba(6, 30, 70, 0.9)` — tooltip 需要保持可读性，不改
- SectionChart（水库断面图）— 需要检查其背景设置

## 验证

1. 启动 `npm run dev`，打开基础数据页面
2. 确认全局背景图能透过页面看到
3. 确认文字和图表的可读性不受影响
4. 切换水库、切换 Tab，确认各子页面均正常
