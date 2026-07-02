# 修复首页面板透明度问题

## 摘要

首页侧边面板（水库监控、发电统计、水位变化、负荷曲线、告警信息）没有背景色，完全透明，导致地图底图穿透面板，图表和文字看不清楚。

---

## 问题诊断

### 当前渲染层级

| 层级 | 元素 | 背景 | z-index |
|------|------|------|---------|
| 1 | `.home-view` | `rgba(6,20,42,0.92)` | - |
| 2 | `.map-background`（Leaflet 地图） | 无 | 0 |
| 3 | `.side-panel`（面板块容器） | **无背景（透明）** | 1 |
| 4 | `PanelCard`（各个面板组件） | `transparent`（默认） | - |

### 根本原因

`.side-panel` 在 [HomeView.vue:L84-L95](file:///f:/CodeExercise/yellow-river-system1/src/views/home/HomeView.vue#L84-L95) 中没有设置 `background`，且其内部的 `PanelCard` 组件也默认 `transparent`。结果：

- 地图层（z-index: 0）的像素直接穿透面板块（z-index: 1）显示
- ECharts 图表、表格文字与地图底图叠加后对比度严重不足
- 即使 `.home-view` 有不透明背景，但面板块高于地图（`position: absolute; z-index: 1`），所以面板区域内地图层仍然可见

---

## 修改方案

### 唯一修改：给 `.side-panel` 添加背景色

**文件**：`src/views/home/HomeView.vue`

**位置**：`.side-panel` 样式块（第 84-95 行）

**修改**：在 `.side-panel` 中添加 `background: rgba(6, 20, 42, 0.92);`

```css
.side-panel {
  position: absolute;
  top: 8px;
  bottom: 8px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 24%;
  background: rgba(6, 20, 42, 0.92);
  transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**效果**：
- 面板块获得不透明背景，地图不再穿透
- 图表和文字清晰可见
- 面板之间保留透明分隔（由 PanelCard 的分割线处理）

---

## 涉及文件

| 文件 | 改动 |
|------|------|
| `src/views/home/HomeView.vue` | `.side-panel` 添加 `background: rgba(6, 20, 42, 0.92);` |

---

## 验证方式

1. 启动 `npm run dev`，打开首页
2. 点击右侧"展开面板"按钮
3. 确认左右两侧面板有深色不透明背景
4. 确认表格数据、图表的文字和线条清晰可辨
5. 确认地图在面板之间仍然正常显示
