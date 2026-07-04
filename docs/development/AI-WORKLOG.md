# AI 项目快照

读我了解项目当前状态——模块在哪、怎么跑、关键文件在哪、当前设计参数是什么。

---

## 🏃 运行项目

```bash
npm run dev
```

技术栈：**Vue 3 + Vite + TypeScript + Element Plus + Tailwind CSS + ECharts + Leaflet + Pinia + Vue Router**

所有业务数据来自 `src/mock/`，不接后端、不接数据库、不接 MATLAB。

---

## 📊 模块完成状态

| 序号 | 模块 | 状态 | 说明 |
|------|------|:----:|------|
| 1 | 项目初始化 | ✅ | Vite + Vue3 + TS + ELP + Tailwind + ECharts + Leaflet + Pinia |
| 2 | 路由配置 | ✅ | 13 个路由（8 主页面 + 6 模型配置子页面） |
| 3 | 顶部导航栏 | ✅ | 半透明玻璃态，蓝青色高亮，`backdrop-filter: blur(12px)` |
| 4 | 首页 | ✅ | 全屏地图背景 + 水库点位 + 左右渐变浮层面板（可收起） |
| 5 | 基础数据 | ✅ | 13 水库选择 + 断面图 + 基础信息 + 关键曲线 + 工情 |
| 6 | 水调水情 | ✅ | 入流/水位/出力/出流四页签，时间范围+水库筛选 |
| 7 | 模型配置 | ✅ | 6 步流程：调度场景 → 调度主体 → 模型数据 → 模型算法 → 场景配置 → 配置汇总 |
| 8 | 过程透明 | ✅ | 方案切换 + 6 图表 + 进度模拟 + 底部摘要 |
| 9 | 评价决策 | ✅ | Tab 导航（评价分析 / 决策分析），雷达图+桑基图+帕累托+排名 |
| 10 | 案例库 | ✅ | 7 案例（7 种图标）+ 筛选 + 详情页签 + 过程预览 |
| 11 | 报表统计 | ✅ | 逐月/逐年报表切换、多级表头、5 水库完整数据 |

---

## 🔀 模型配置 6 步流程

| 步骤 | 路由 | 页面 | 核心功能 |
|:----:|------|------|----------|
| 1 | /model-config/dispatch-scenario | 调度场景 | 3 大场景卡片 + 9 子选项 |
| 2 | /model-config/dispatch-subject | 调度主体 | 时段步长频率 + 水库选择 |
| 3 | /model-config/model-data | 模型数据 | 数据目录 + 图表/表格 |
| 4 | /model-config/model-algorithm | 模型算法 | 模型+算法+参数 + 调度目标+约束 |
| 5 | /model-config/scenario-constraint | 场景配置 | 场景类型 + 参数设置 |
| 6 | /model-config/config-summary | 配置汇总 | 方案列表 + 图表 + 一键运行 |

步骤联动通过 `src/stores/modelConfig.ts` 串联。Mock 数据在 `src/mock/modelConfig.ts`。

---

## 🎨 当前设计规范

| 参数 | 值 |
|------|-----|
| 全局背景图 | `public/background/background.png`（`fixed` + `cover`） |
| 页面面板背景 | `rgba(6, 20, 42, 0.92)` **不含 `backdrop-filter`** |
| 导航栏 | `rgba(6, 20, 42, 0.85)` + `backdrop-filter: blur(12px)` |
| 主色 | `#00afff` |
| 强调色 | `#00e5ff` |
| 正文文字 | `#e0e6ed` / `#c0c8d4` |
| 辅助文字 | `#8aa0b8`（Tailwind `tech-muted`） |
| placeholder | `#6e8a9e` |
| 分割线 | `.h-divider` / `.v-divider` 发光渐变 |
| 字体渲染 | `subpixel-antialiased`（Windows 亚像素） |
| 面板风格 | 统一面板 + 发光分割线（无独立圆角卡片） |
| 首页面板 | 渐变半透明：边缘 `0.92` → 中心方向 `0.25` |

---

## 🧭 关键文件索引

### 模型配置（6 步流程）

| 文件 | 用途 |
|------|------|
| `src/stores/modelConfig.ts` | 6 步联动核心 Pinia Store |
| `src/mock/modelConfig.ts` | 模型配置全量 mock（场景/联动/约束映射） |
| `src/components/model-config/ModelConfigFooter.vue` | 底部公用操作栏（取消/保存/下一步） |
| `src/components/model-config/ModelConfigStepBar.vue` | 步骤条组件（支持 5/6 步切换） |

### 首页

| 文件 | 用途 |
|------|------|
| `src/views/home/HomeView.vue` | 面板收起/展开控制入口 |
| `src/components/home/BasinMapPanel.vue` | Leaflet 地图全屏背景 |
| `src/components/home/ReservoirMonitorPanel.vue` | 水情监控面板 |
| `src/components/home/PowerStatisticsPanel.vue` | 发电统计面板 |
| `src/components/home/WaterLevelChart.vue` | 水位过程线 ECharts |
| `src/components/home/LoadChart.vue` | 负荷过程线 ECharts |
| `src/components/home/WarningPanel.vue` | 预警信息列表 |

### 基础数据

| 文件 | 用途 |
|------|------|
| `src/mock/basicData.ts` | 13 座水库全量 mock（含关键曲线） |
| `src/components/basic-data/ReservoirSidebar.vue` | 水库列表选择 |
| `src/components/basic-data/BaseInfoPanel.vue` | 工程属性 + 调度规则 |
| `src/components/basic-data/KeyCurvesPanel.vue` | 库容/出力/过流曲线 |
| `src/components/basic-data/EngineeringInfo.vue` | 工情信息（机组+闸门） |
| `src/components/chart/ReservoirSectionGraph.vue` | 水库断面示意图 |

### 通用

| 文件 | 用途 |
|------|------|
| `src/styles/index.css` | 全局样式 + `:root:root` Element Plus CSS 变量覆盖 |
| `tailwind.config.js` | 颜色定义（`tech-*` 系列） |
| `src/layouts/MainLayout.vue` | 顶部导航栏 + 页面容器 |
| `src/components/common/PanelCard.vue` | 通用分区面板（透明背景 + 发光分割线） |
| `docs/page-design/04-model-config/README.md` | 模型配置模块总设计文档 |

> **流水账历史**：`docs/development/SESSIONS.md`（每次会话记录，保留近 5 次）
