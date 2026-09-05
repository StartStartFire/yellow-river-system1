# AI 工作日志

> 最近 3 条完成任务，新记录插入顶部，超出时删除最旧记录。
> 每步完成后按此模板追加记录，方便后续会话快速了解进展。

---

## [11] 决策分析全链路 + 回调统一封装 + 文档全面同步

**日期**: 2026-09-05
**原因**: 打通"优化结果 → 评价 → 决策分析"闭环；回调逻辑收敛为统一封装；文档与代码全面对齐
**涉及文件**:
- `matlab-model/evaluate_objective_save_info.m` — **增强**：返回 22 项评价指标（evaluating）与决策明细（plan_details：过程曲线/目标满足率/水量分配/协同度）
- `matlab-model/nsga_2_para.m` — **修改**：结束后逐个体生成 evaluating + plan_details，返回值扩展为三元组
- `matlab-model/push_callback_data.m` — **新增**：回调统一封装（progress 汇总指标 + process_data 全年份过程数据，含 start_year/coordination/constraint 字段），两个主循环每 10 代调用
- `backend-service/app/services/matlab.py` — **修改**：提取 evaluating/plan_details；年份范围（YEAR_START/YEAR_END）、起调水位、防凌流量动态注入
- `backend-service/app/api/jobs.py` — **新增**：GET /decision/{job_id} 决策方案明细端点（前 10 方案，已评价按 ALL 整合排名、未评价按 Pareto rank + 拥挤距离排序）
- `frontend-service/src/api/index.ts` — **新增**：postEvaluate / getEvaluateResult / getDecisionPlans（base URL 按 hostname 动态拼接）
- `frontend-service/src/views/evaluation-decision/` — **对接**：评价分析 + 决策分析 Tab 接真实 API（mock 仅作无 job_id/失败回退）
- 各子项目 docs/ — **修订**：API 文档补 /decision；清理"全 Mock""17 个 sheet""F 盘路径""MATLAB 未推送 process_data"等过时表述

**验证**:
- POST /run → WS 实时推送 → POST /evaluate（ALL）→ GET /decision 全链路跑通 ✓
- 决策分析页方案编号与评价分析页排名一致 ✓
- 文档 grep 校验：过时关键词（F 盘路径/17 个 sheet/进度模拟等）零残留 ✓

---

## [10] MATLAB 评价函数增强 + 约束参数动态注入

**日期**: 2026-08-03
**原因**: 新增 `evaluate_objective_save_info.m`，支持运行时动态传入约束参数
**涉及文件**:
- `matlab-model/evaluate_objective_save_info.m` — **新增**：带详细过程结果返回的评价函数（nargout>1 返回水位/流量/出力/协同度等完整过程数据）
- `matlab-model/load_data.m` — **修改**：支持 YEAR_START/YEAR_END 年份范围截取逻辑，可按年份切片加载数据
- `matlab-model/nsga_2_para.m` — **修改**：适配新评价函数调用方式
- `matlab-model/PAEM_para.m` — **修改**：同上
- `backend-service/app/services/matlab.py` — **修改**：新增约束参数动态注入（起调水位、防凌流量、年份范围），通过 `eng.eval()` 设置全局变量后调用 load_data
- `backend-service/app/schemas/job.py` — **修改**：RunRequest 新增 `year_start`/`year_end`/`initial_water_level_*`/`ice_prevention_flows` 字段
- `backend-service/app/core/executor.py` — **修改**：TaskConfig 同步新增约束参数字段

**验证**:
- 年份范围截取：指定 year_start=2000, year_end=2010 时 load_data 只加载该范围数据 ✓
- 起调水位动态注入：LONG_Z_INI_VAL / LIU_Z_INI_VAL 全局变量传入 ✓
- 防凌流量动态注入：QMIN_VAL 全局变量传入 ✓
- evaluate_objective_save_info 返回完整 results 结构体（含 Long/Liu/N/liuzhou/ecology/coordination） ✓

---

## [9] Web 服务模块化重构 + 评价系统集成

**日期**: 2026-07-16
**原因**: 系统集成阶段功能扩展，提升服务架构质量，增加方案评价排名能力
**涉及文件**:
- `backend-service/app/` — **重构**：扁平 7 文件结构拆分为 `api/`（5 路由）、`core/`（5 核心模块）、`schemas/`（5 Pydantic 模型）、`services/`（MATLAB Engine 封装）
- `evaluation-model/` — **新增**：独立评价系统模块，含 NMF/PP/AHP_FUZZY 三种算法 + RankSumTheory 序号总和整合
- `backend-service/app/main.py` — **重写**：lifespan 生命周期 + 按模块注册路由
- `backend-service/app/config.py` — **修改**：新增 CORS origins 配置
- `backend-service/app/api/evaluate.py` — **新增**：POST /evaluate、GET /evaluate/{job_id} 端点
- `backend-service/app/schemas/evaluate.py` — **新增**：EvaluateRequest/EvaluateResponse Pydantic 模型
- `backend-service/docs/api-reference.md` — **新增**：完整 API 参考文档
- `backend-service/docs/backend-architecture.md` — **新增**：后端架构梳理文档
- `evaluation-model/docs/evaluation-data-specification.md` — **新增**：评价系统数据产出规格文档

**验证**:
- /health 返回 engine=ready ✓
- POST /evaluate 三种算法（NMF/PP/AHP_FUZZY）+ ALL 整合模式均返回排名 ✓
- GET /evaluate/{job_id} 缓存查询正常 ✓
- CORS 跨域 localhost:3000 正常 ✓
