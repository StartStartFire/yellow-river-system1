# 黄河上游水库群调度系统

黄河上游水库群联合调度科研分析平台，覆盖**基础数据、模型配置、过程透明、评价决策、案例库、报表统计**等业务场景。

当前阶段为前端原型，所有数据来自 `src/mock/`，不接后端、不接数据库、不调用 MATLAB。

## 技术栈

| 技术 | 用途 |
|------|------|
| Vue 3 + TypeScript | 页面与组件开发 |
| Vite | 构建工具 |
| Element Plus | 表单、表格、弹窗、步骤条等 UI 组件 |
| Tailwind CSS | 页面布局与样式 |
| ECharts | 折线图、雷达图、桑基图、帕累托图等 |
| Leaflet | 流域地图展示 |
| Pinia | 前端状态管理 |
| Vue Router | 页面路由 |

## 运行

```bash
npm install
npm run dev
```

类型检查与构建：

```bash
npx vue-tsc --noEmit
npx vite build
```

## 页面

| 模块 | 路由 | 说明 |
|------|------|------|
| 首页 | `/home` | 流域地图 + 水库监控 + 发电统计 + 预警 |
| 基础数据 | `/basic-data` | 13 座水库属性、断面、工情、关键曲线 |
| 水调水情 | `/water-condition` | 实际运行数据与调令对比 |
| 模型配置 | `/model-config` | 6 步流程：调度场景 → 调度主体 → 模型数据 → 模型算法 → 场景配置 → 配置汇总 |
| 过程透明 | `/process-transparent` | 任务运行过程展示（曲线、日志、进度模拟） |
| 评价决策 | `/evaluation-decision` | 多方案评价 + 单方案决策（雷达图、桑基图） |
| 案例库 | `/case-library` | 历史案例检索、查看、复现 |
| 报表统计 | `/report-statistics` | 逐月/逐年报表 |

## 文档

| 文档 | 说明 |
|------|------|
| `AGENTS.md` | AI 开发约束（必读） |
| `docs/page-design/README.md` | 全局设计规范（颜色、布局、组件） |
| `docs/page-design/pages-reference.md` | 页面速查表（路由映射、状态颜色、联动规则） |
| `docs/requirements/system-requirements.md` | 系统需求文档（模块分类、流程关系、数据边界） |
| `docs/development/AI-WORKLOG.md` | 项目快照（新会话恢复上下文用） |
| `docs/development/SESSIONS.md` | 开发流水账（最近 5 次会话） |
