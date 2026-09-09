# AI 工作日志

> 最近 3 条完成任务，新记录插入顶部，超出时删除最旧记录。
> 每步完成后按此模板追加记录，方便后续会话快速了解进展。

---

## [12] 文档治理：必读路径 + 归档 + 三项合并

**日期**: 2026-09-07
**原因**: 文档达 22 份、同一事实多处复制导致持续过时（[11] 一次修订 ~100 处），需结构性治理而非逐处修补；原则：一个事实只活在一处，代码可推断的信息不写文档
**涉及文件**:
- `CLAUDE.md` — **新增「AI 会话必读路径」**（三层：全局必读 2 份 → 按域必读 → 按需查阅）与「新增文档规则」3 条（AI 从代码读不到的知识才写 / 可数事实不写死 / 一处维护跨档用链接）；目录树与文档索引同步
- `docs/archive/` — **新增目录**，归档 6 份：model-run-integration / process-transparent-plan / data-flow（已实施计划）、SESSIONS（历史流水账）、database-design（未实施设计）、project-analysis（技术债已提取）
- `frontend-service/CLAUDE.md` — §20 启动指引瘦身为前端域必读（全局路径指回根 CLAUDE）；§21.2 端点表删改为指向 api-reference 的链接
- `frontend-service/docs/requirements/system-requirements.md` — **纯需求化**：删头部状态、各模块"数据来源"行、§5.1 来源列、§6 开发边界，新增「文档职责说明」节
- `frontend-service/docs/development/SNAPSHOT.md` — 顶部声明定位为前端接入状态唯一出处
- `backend-service/docs/backend-architecture.md` — **重写 280 → 68 行**：删目录树/模块职责表/端点表（与代码及 api-reference 重复），保留 POST /run 与 POST /evaluate 执行链路、设计决策（为什么）、新增「已知边界」
- `matlab-model/docs/model-specification.md` — **新增 §11 已知问题与技术债**（numel bug、三份 ~550 行重复仿真循环、全局变量副作用、PAEM 早停缺陷等，自 project-analysis 提取，位置以搜索关键词定位）
- `README.md` / `docs/project-nav.md` / `SNAPSHOT.md` — 引用修复共 11 处指向归档路径；修复归档产生的 1 处相对路径断链

**验证**:
- 22 份 → 13 份现行 + 6 份归档，每类信息单一权威出处 ✓
- 3 轮 grep 扫描（旧路径 / 旧锚点 / 过时关键词）零残留 ✓
- requirements 无状态类表述；backend-architecture 5 节结构完整；断链深扫通过 ✓

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
