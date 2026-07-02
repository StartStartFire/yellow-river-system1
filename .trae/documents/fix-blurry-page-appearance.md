# 修复页面模糊（糊糊的）问题

## 摘要

页面出现"糊糊的"视觉感受，需要系统性调整透明度和模糊效果，提升页面清晰度和可读性。

---

## 问题诊断

经过全面检查，共发现 **4 个导致模糊的根本原因**：

### 原因 1：backdrop-filter blur 层层叠加

当前代码中存在 **25 处** `backdrop-filter: blur()`。渲染层级为：

| 层级 | 位置 | blur 值 | 透明度 |
|------|------|---------|--------|
| 1 | `html` 全局背景图 | 无 | - |
| 2 | `body` | 无 | transparent |
| 3 | `MainLayout` 导航栏 | **20px** | 0.72 |
| 4 | 页面视图 .xxx-view | **16px** | 0.65~0.88 |
| 5 | 子组件（筛选栏等） | **6~14px** | 各异 |

**问题**：浏览器会先对第 3 层的 blur(20px) 模糊整个视口，然后在第 4 层再对已经模糊后的图片做 blur(16px)，导致背景图经过两次高斯模糊，严重丢失细节。

### 原因 2：页面背景透明度太低

- 水调水情页面：`rgba(6, 20, 42, 0.65)` → 35% 的背景图透出
- 基础数据页面：`rgba(6, 20, 42, 0.65)` → 35% 的背景图透出
- 其他页面：`rgba(6, 20, 42, 0.88)` → 12% 透出

大量的背景图像素穿透半透明层，与 ECharts 图表、文字混在一起，产生"脏感"和"浑浊感"。

### 原因 3：antialiased 字体渲染在 Windows 上不适用

[src/styles/index.css:L41](file:///f:/CodeExercise/yellow-river-system1/src/styles/index.css#L41) 中 `body` 使用了 Tailwind 的 `antialiased` class，它在 macOS 上启用灰度抗锯齿使文字更细更好看，但在 **Windows 上会导致文字发虚、笔画变细、辨识度下降**。

### 原因 4：文字颜色对比度不足

大量文字使用 `#7a8fa3`（中等灰蓝）和 `#5a6f83`（暗灰蓝），在深色半透明背景上对比度不够，进一步加剧了"看不清"的感觉。

---

## 修改方案

### 步骤 1：移除 body 的 antialiased，改用 subpixel-antialiased

**文件**：`src/styles/index.css`

**修改**：将 `@apply m-0 min-h-screen antialiased;` 改为 `@apply m-0 min-h-screen subpixel-antialiased;`

**效果**：Windows 上使用亚像素渲染，文字笔画更饱满清晰。

---

### 步骤 2：提高所有页面背景不透明度

**文件**：各页面视图文件的 `<style scoped>` 部分

**修改**：将所有页面的 `.xxx-view` 背景透明度从 `0.65` / `0.88` 统一提高到 `0.92`：

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `src/views/basic-data/BasicDataView.vue:L101` | `0.65` | `0.92` |
| `src/views/water-condition/WaterConditionView.vue:L332` | `0.65` | `0.92` |
| `src/views/home/HomeView.vue:L67` | `0.88` | `0.92` |
| `src/views/model-config/dispatch-scenario/DispatchScenarioView.vue:L342` | `0.88` | `0.92` |
| `src/views/model-config/model-data/ModelDataView.vue:L462` | `0.88` | `0.92` |
| `src/views/model-config/model-algorithm/ModelAlgorithmView.vue:L487` | `0.88` | `0.92` |
| `src/views/model-config/dispatch-subject/DispatchSubjectView.vue:L597` | `0.88` | `0.92` |
| `src/views/model-config/scenario-constraint/ScenarioConstraintView.vue:L285` | `0.88` | `0.92` |
| `src/views/model-config/config-summary/ConfigSummaryView.vue:L799` | `0.88` | `0.92` |
| `src/views/process-transparent/ProcessTransparentView.vue:L534` | `0.88` | `0.92` |
| `src/views/evaluation-decision/EvaluationDecisionView.vue:L871` | `0.88` | `0.92` |
| `src/views/case-library/CaseLibraryView.vue:L607` | `0.88` | `0.92` |
| `src/views/report-statistics/ReportStatisticsView.vue:L444` | `0.88` | `0.92` |

**同时**，将 MainLayout 导航栏透明度也提高：`0.72` → `0.85`

---

### 步骤 3：降低 backdrop-filter blur 值，移除子组件冗余 blur

**原则**：blur 只在一层生效，避免叠加。

**MainLayout 导航栏**（`src/layouts/MainLayout.vue:L63`）：
- blur 从 `20px` → `12px`
- 这是整个页面唯一的全局模糊层

**所有页面视图**：移除页面级 `.xxx-view` 上的 `backdrop-filter: blur(16px)`，因为导航栏已有模糊覆盖。改为纯色半透明背景即可。

**子组件**（筛选栏等）：移除第 5 层的 blur，这些 blur 叠加在页面 blur 之上，只会让内容更模糊。

---

### 步骤 4（可选）：略微提高文字颜色

将全局 muted 文字颜色从 `#7a8fa3` 提高为 `#8ea0b4`，将 `#5a6f83` 提高为 `#6a7f93`，增强可读性。此改动影响面大，作为可选步骤。

---

## 涉及文件清单

| 文件 | 改动类型 |
|------|----------|
| `src/styles/index.css` | 修改 `antialiased` → `subpixel-antialiased` |
| `src/layouts/MainLayout.vue` | 调整导航栏 blur 和透明度 |
| `src/views/basic-data/BasicDataView.vue` | 提高透明度 + 移除 blur |
| `src/views/water-condition/WaterConditionView.vue` | 提高透明度 + 移除 blur |
| `src/views/home/HomeView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/dispatch-scenario/DispatchScenarioView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/model-data/ModelDataView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/model-algorithm/ModelAlgorithmView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/dispatch-subject/DispatchSubjectView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/scenario-constraint/ScenarioConstraintView.vue` | 提高透明度 + 移除 blur |
| `src/views/model-config/config-summary/ConfigSummaryView.vue` | 提高透明度 + 移除 blur |
| `src/views/process-transparent/ProcessTransparentView.vue` | 提高透明度 + 移除 blur |
| `src/views/evaluation-decision/EvaluationDecisionView.vue` | 提高透明度 + 移除 blur |
| `src/views/case-library/CaseLibraryView.vue` | 提高透明度 + 移除 blur |
| `src/views/report-statistics/ReportStatisticsView.vue` | 提高透明度 + 移除 blur |

---

## 验证方式

1. 启动 `npm run dev`，打开浏览器分别浏览各页面
2. 确认文字笔画清晰、不再发虚
3. 确认页面背景图仍然可见但不抢眼
4. 确认 ECharts 图表线条和文字清晰
5. 确认半透明玻璃态效果仍然保留（仅导航栏处）
