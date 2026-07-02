# 水调水情页面半透明化

## 目标

将水调水情页面的 `background: rgba(6, 20, 42, 0.88)` 降低为半透明，让全局背景图能够穿透显示，与基础数据页面保持一致的半透明效果。

## 当前状态

[WaterConditionView.vue#L332](file:///f:/CodeExercise/yellow-river-system1/src/views/water-condition/WaterConditionView.vue#L332) `.water-condition-view` 设置为 `rgba(6,20,42,0.88)`，几乎不透明。其他子元素（`.filter-bar`、`.chart-card`）已经是 `transparent`。

## 修改方案

### WaterConditionView.vue — 降低页面级面板不透明度

```css
/* 改前 */
background: rgba(6, 20, 42, 0.88);

/* 改后 */
background: rgba(6, 20, 42, 0.65);
```

与基础数据页面使用相同的不透明度值 `0.65`。

## 修改文件

- `src/views/water-condition/WaterConditionView.vue` — 1 处 CSS 修改

## 验证

1. 打开水调水情页面
2. 确认全局背景图能透过页面看到
3. 确认图表（ECharts，`backgroundColor: transparent`）和图例文字可读性正常
4. 确认筛选栏、Tab 按钮、工具按钮显示正常
