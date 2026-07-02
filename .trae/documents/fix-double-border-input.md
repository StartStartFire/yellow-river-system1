# 修复输入框双边框问题

## 问题

方案名称输入框显示两条边框，因为：

- 全局 [index.css#L170](file:///f:/CodeExercise/yellow-river-system1/src/styles/index.css#L170) `.el-input__wrapper` 已有 `box-shadow: 0 0 0 1px rgba(0, 175, 255, 0.2) !important`（外阴影=外边框）
- 局部 [DispatchScenarioView.vue#L385](file:///f:/CodeExercise/yellow-river-system1/src/views/model-config/dispatch-scenario/DispatchScenarioView.vue#L385) `.name-input :deep(.el-input__wrapper)` 又叠加了 `box-shadow: ... inset !important`（内阴影=内边框）

内外各一层 = 双边框。

## 修改方案

移除 `.name-input :deep(.el-input__wrapper)` 中的 `box-shadow`，让它继承全局样式即可。

```css
/* 改前 */
.name-input :deep(.el-input__wrapper) {
  background: transparent !important;
  box-shadow: 0 0 0 1px rgba(0, 175, 255, 0.2) inset !important;
}

/* 改后 */
.name-input :deep(.el-input__wrapper) {
  background: transparent !important;
}
```

## 修改文件

- `src/views/model-config/dispatch-scenario/DispatchScenarioView.vue` — 删除 1 行 CSS
