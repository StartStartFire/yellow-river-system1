# 模型配置 StepBar 和 Footer 半透明化

## 目标

将模型配置页面中的顶部步骤条（ModelConfigStepBar）和底部操作栏（ModelConfigFooter）的深蓝色背景改为半透明，让全局背景图能够穿透显示。

## 当前状态

| 组件 | 选择器 | 当前值 |
|------|--------|--------|
| [ModelConfigStepBar.vue#L56](file:///f:/CodeExercise/yellow-river-system1/src/components/model-config/ModelConfigStepBar.vue#L56) | `.step-bar` (inline style) | `background: rgba(6, 30, 70, 0.85)` |
| [ModelConfigFooter.vue#L76](file:///f:/CodeExercise/yellow-river-system1/src/components/model-config/ModelConfigFooter.vue#L76) | `.model-config-footer` | `background: rgba(6, 30, 70, 0.85)` |

两者都保留了 `border: 1px solid rgba(50, 150, 255, 0.35)` 和 `border-radius: 12px` 作为视觉结构，不需要改动。

## 修改方案

### 1. ModelConfigStepBar.vue — inline style 背景透明化

```html
<!-- 改前 -->
style="background: rgba(6, 30, 70, 0.85); border: 1px solid rgba(50, 150, 255, 0.35); border-radius: 12px;"

<!-- 改后 -->
style="background: rgba(6, 30, 70, 0.35); border: 1px solid rgba(50, 150, 255, 0.35); border-radius: 12px;"
```

### 2. ModelConfigFooter.vue — CSS 背景透明化

```css
/* 改前 */
.model-config-footer {
  background: rgba(6, 30, 70, 0.85);
  ...
}

/* 改后 */
.model-config-footer {
  background: rgba(6, 30, 70, 0.35);
  ...
}
```

## 不改动的部分

- 边框、圆角保持不变，维持视觉边界
- StepBar 内步骤圆圈（active/completed/pending）保持不变
- Footer 按钮样式保持不变
- 6 个步骤视图的页面级 `background` 不在此次修改范围内

## 修改文件

- `src/components/model-config/ModelConfigStepBar.vue` — 1 处 inline style
- `src/components/model-config/ModelConfigFooter.vue` — 1 处 CSS

## 验证

1. 打开任意模型配置步骤页面
2. 确认 StepBar 和 Footer 背景半透明，全局背景图可透过
3. 确认 StepBar 步骤圆圈、连接线、文字清晰可读
4. 确认 Footer 按钮正常显示
