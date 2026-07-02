# 移除断面示意图深蓝色背景

## 目标

移除基础数据页面"水库断面"示意图区域的深蓝色背景 `#061a3a`，让它变为透明，与页面其他区域保持一致。

## 当前状态

[ReservoirSectionGraph.vue#L366](file:///f:/CodeExercise/yellow-river-system1/src/components/chart/ReservoirSectionGraph.vue#L366) `.graph-wrap` 设置了 `background: #061a3a;`，这是一个纯深蓝色背景块，覆盖住了页面面板的透明效果。

## 修改方案

### ReservoirSectionGraph.vue — `.graph-wrap` 背景透明化

```css
/* 改前 */
.graph-wrap {
  ……
  background: #061a3a;
  ……
}

/* 改后 */
.graph-wrap {
  ……
  background: transparent;
  ……
}
```

## 不改动的部分

- SVG 内部的水体渐变、标注节点背景等 — 这些是图表内容本身，不是背景板
- `params-bar` 底栏 — 已经使用半透明背景 `rgba(0, 175, 255, 0.05)`
- 断面 PNG 图片 (`/map/section-bg.png`) — 这是断面轮廓图，是内容的一部分

## 修改文件

- `src/components/chart/ReservoirSectionGraph.vue` — 1 处 CSS 修改

## 验证

1. 打开基础数据页面，选中"水库断面" Tab
2. 确认断面图容器背景透明，页面背景图可透过
3. 断面图的水体、标注、坐标轴等元素显示正常
