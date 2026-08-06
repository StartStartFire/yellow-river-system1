# 评价模型数据产出规格

> 本文档梳理评价模型（`evaluation_system/`）运行结束后产出的全部数据，说明每项数据的结构、来源、以及在前端评价/决策页面的用途。

---

## 一、数据总览

```
NSGA-II / PAEM 运行结束
  │
  ├─ output.evaluating (pop × 22)     → 评价系统输入
  ├─ output.chromosome (pop × V+M+2)  → 决策分析输入
  │
  ▼
POST /evaluate ALL
  │
  ├─ NMFAlgorithm      输出: W, H, ranks, cost_history
  ├─ PPAlgorithm       输出: a, z, ranks, cost_history
  ├─ FuzzyAlgorithm    输出: final_scores, ranks, ahp_weights, first_level_ranking_results
  └─ RankSumTheory     输出: final_ranking, pairwise_rank_sum_results, rank_sum_report
```

---

## 二、评价系统输出数据

### 2.1 NMF（非负矩阵分解布谷鸟搜索）

| 字段 | Python 类型 | 形状 | 说明 |
|------|-----------|------|------|
| `W` | `ndarray` | (22,) | 最优基向量，\|W\|=1 |
| `H` | `ndarray` | (pop,) | 权向量，值越大方案越优 |
| `ranks` | `ndarray` | (pop,) | 排名：0=最优，pop-1=最差 |
| `best_scheme_index` | `int` | — | 最优方案索引（0-based） |
| `best_scheme_score` | `float` | — | 最优方案的 H 值 |
| `best_fitness` | `float` | — | 最终重构误差 \|A-WH\|² |
| `cost_history` | `list[float]` | (500,) | 每代最优适应度，用于收敛曲线图 |
| `execution_time` | `float` | — | 运行耗时（秒） |
| `iterations` | `int` | — | 实际迭代次数（未早停则为 500） |
| `population_size` | `int` | — | 种群大小（默认 100） |
| `dimension` | `int` | — | 问题维度（=22） |

### 2.2 PP（投影寻踪布谷鸟搜索）

| 字段 | Python 类型 | 形状 | 说明 |
|------|-----------|------|------|
| `a` | `ndarray` | (22,) | 最优投影方向向量，\|a\|=1 |
| `z` | `ndarray` | (pop,) | 投影值，值越大方案越优 |
| `ranks` | `ndarray` | (pop,) | 排名：0=最优 |
| `best_scheme_index` | `int` | — | 最优方案索引 |
| `best_scheme_score` | `float` | — | 最优方案的 z 值 |
| `best_fitness` | `float` | — | 最终投影质量 Q，越小越好 |
| `cost_history` | `list[float]` | (500,) | 每代最优适应度，用于收敛曲线图 |
| `execution_time` | `float` | — | 运行耗时（秒） |
| `iterations` | `int` | — | 实际迭代次数 |
| `population_size` | `int` | — | 种群大小 |
| `dimension` | `int` | — | 问题维度 |

### 2.3 AHP-Fuzzy（AHP 模糊综合评价）

| 字段 | Python 类型 | 形状 | 说明 |
|------|-----------|------|------|
| `final_scores` | `ndarray` | (pop,) | 综合得分，越大越优 |
| `ranks` | `ndarray` | (pop,) | 排名：0=最优 |
| `best_scheme_index` | `int` | — | 最优方案索引 |
| `best_scheme_score` | `float` | — | 最优方案的得分 |
| `ahp_weights` | `ndarray` | (5,) | 5 个子系统的 AHP 权重 |
| `consistency_info` | `dict` | — | 一致性检验 { CI, CR, max_eigenvalue, is_consistent } |
| `execution_time` | `float` | — | 运行耗时（秒，通常 <0.01s） |
| `first_level_results` | `dict` | — | 一级评价结果（得分） |
| `first_level_ranking_results` | `dict` | — | 一级评价结果（含排名） |

#### first_level_ranking_results 结构

```json
{
  "water": {
    "name": "水子系统",
    "scores": [62.3, 58.1, 70.5, ...],    // (pop,) 各方案得分
    "ranking": [1, 2, 0, ...],             // (pop,) 各方案排名（0=最优）
    "sorted_indices": [2, 0, 1, ...],      // 按得分降序的方案索引
    "best_scheme_index": 2,                // 最优方案
    "best_scheme_score": 70.5,             // 最优得分
    "weights": [0.3, 0.3, 0.1, 0.1, 0.1, 0.1],  // 子系统内指标权重
    "indices": [0, 1, 2, 3, 4, 5]         // 对应的 evaluating 列索引
  },
  "sand":    { "name": "沙子系统", ... },
  "energy":  { "name": "能子系统", ... },
  "disaster":{ "name": "灾子系统", ... },
  "ecology": { "name": "生态子系统", ... }
}
```

### 2.4 排名整合（RankSumTheory）

| 字段 | 类型 | 形状 | 说明 |
|------|------|------|------|
| `final_ranking` | `ndarray` | (pop,) | 序号总和理论的最终排名（0=最优） |
| `all_rankings` | `dict` | — | {NMF: (pop,), PP: (pop,), AHP_FUZZY: (pop,)} 三种算法的原始排名 |
| `pairwise_rank_sum_results` | `dict` | — | 两两组合排名 {NMF-PP, NMF-AHP_FUZZY, PP-AHP_FUZZY, ALL} |
| `rank_sum_report` | `dict` | — | 每方案的详细排名报告 |

#### rank_sum_report 结构

```json
{
  "ranking_method": "rank_sum_theory",
  "total_algorithms": 3,
  "total_schemes": 15,
  "scheme_details": [
    {
      "scheme_index": 0,
      "final_rank": 1,
      "rank_sum": 5,
      "algorithm_ranks": { "NMF": 2, "PP": 1, "AHP_FUZZY": 2 }
    }
  ],
  "best_scheme": 4,
  "worst_scheme": 12,
  "rank_sums": [5, 7, 10, ...]
}
```

---

## 三、前端缓存数据结构

后端 `_build_evaluation_cache` 将上述 numpy 数据转为 JSON，统一缓存格式：

```json
{
  "method": "ALL",
  "status": "success",

  "rankings": [
    {
      "algorithm": "NMF",
      "ranks": [3, 1, 2, 5, 0, 4],
      "scores": [195.9, 215.5, 283.8, ...],
      "execution_time": 3.36
    },
    {
      "algorithm": "PP",
      "ranks": [3, 1, 2, 5, 0, 4],
      "scores": [258.0, 166.5, 166.6, ...],
      "execution_time": 5.79
    },
    {
      "algorithm": "AHP_FUZZY",
      "ranks": [3, 1, 2, 5, 0, 4],
      "scores": [39.5, 51.2, 58.8, ...],
      "execution_time": 0.001
    },
    {
      "algorithm": "ALL",
      "ranks": [3, 1, 2, 5, 0, 4],
      "scores": null,
      "execution_time": null
    }
  ],

  "convergence": {
    "NMF": [120000, 118500, 117200, ..., 96500],
    "PP": [0.008, 0.006, 0.005, ..., 0.00048]
  },

  "subsystem": {
    "water":    { "name": "水子系统", "scores": [62.3, 58.1, ...], "ranking": [1, 2, ...] },
    "sand":     { "name": "沙子系统", "scores": [45.8, 52.3, ...], "ranking": [2, 1, ...] },
    "energy":   { "name": "能子系统", "scores": [71.2, 68.4, ...], "ranking": [1, 2, ...] },
    "disaster": { "name": "灾子系统", "scores": [55.6, 61.2, ...], "ranking": [2, 1, ...] },
    "ecology":  { "name": "生态子系统", "scores": [48.9, 53.7, ...], "ranking": [2, 1, ...] }
  }
}
```

### 3.1 排名表格行说明

| 行 | rank 字段 | scores 字段 | 页面呈现 |
|----|-----------|------------|---------|
| NMF / PP / AHP_FUZZY | 1, 2, 3 | 该算法的评分值（越大越好） | 得分 + 进度条 |
| ALL | -1 | null | 排名徽章（🥇🥈🥉）展示每个方案的整合名次 |

### 3.2 收敛曲线说明

- `convergence.NMF` — NMF 算法的适应度历史（重构误差 \|A-WH\|²），约 500 个点
- `convergence.PP` — PP 算法的适应度历史（投影质量 Q），约 500 个点
- 两条曲线 Y 轴尺度不同，通常用独立 Y 轴或分图展示
- 曲线呈**下降趋势**：迭代越深，适应度越小（越优）

### 3.3 子系统得分说明

- 5 个子系统各有一组 `(pop,)` 的得分数组
- 由 AHP-Fuzzy 一级评价产生（NMF 和 PP 不产生子系统级别的数据）
- 前端雷达图的 5 个轴对应 5 个子系统，每个方案是一条多边形

---

## 四、前端页面数据映射

### 4.1 评价分析页面

| 图表位置 | 图表类型 | 数据来源 | 数据字段 |
|---------|---------|---------|---------|
| 左上 | 子系统得分雷达图 | AHP-Fuzzy 一级评价 | `subsystem.<key>.scores` |
| 右上 | 评价指标桑基图 | 静态框架（R1-R22 → 5子系统 → 优劣） | 不依赖数据 |
| 左下 | 算法收敛曲线 | NMF / PP | `convergence.NMF / convergence.PP` |
| 右下 | 排名表格 | 全部算法 + 整合 | `rankings[*]` |

### 4.2 决策分析页面

> 当前决策分析页面数据来自 MATLAB 模拟结果（`process_data`），非评价系统产出

| 位置 | 内容 | 数据来源 | 来源字段 |
|------|------|---------|---------|
| 左列 | 目标满足情况 | 过程透明数据 | `process_data.constraint.*` |
| 中列 | 过程曲线（水位/流量/出力） | 过程透明数据 | `process_data.*_level / *_outflow / *_power` |
| 右列 | 水量使用流向图 | 过程透明数据 | 需从 results 中计算 |

#### 决策分析可用数据字段

```
process_data
├── longyang_level:  (n_periods,)    龙羊峡水位
├── liujia_level:    (n_periods,)    刘家峡水位
├── longyang_outflow:(n_periods,)    龙羊峡下泄流量
├── liujia_outflow:  (n_periods,)    刘家峡下泄流量
├── longyang_power:  (n_periods,)    龙羊峡出力
├── liujia_power:    (n_periods,)    刘家峡出力
├── total_power:     (n_periods,)    梯级总出力
├── water_shortage:  (n_periods,)    缺水
│
├── coordination
│   ├── h_water:  float    水资源子系统有序度
│   ├── h_ele:    float    发电子系统有序度
│   ├── h_sed:    float    输沙子系统有序度
│   └── h_eco:    float    生态子系统有序度
│
└── constraint
    ├── water_guarantee: float (0-100)   供水保证率
    ├── eco_guarantee:   float (0-100)   生态保证率
    ├── power_guarantee: float (0-100)   发电保证率
    └── combined_rate:   float (0-100)   综合约束满足率
```

---

## 五、API 端点

### 5.1 POST /evaluate

```
请求: { job_id: string, method: "NMF" | "PP" | "AHP_FUZZY" | "ALL" }
响应: EvaluateResponse (见 backend-service/app/schemas/evaluate.py)

缓存: 结果存入 JobRecord.evaluation_result
```

### 5.2 GET /evaluate/{job_id}

```
未评价时: { job_id, status: "not_evaluated", message: "尚未进行评价" }
已评价时: { job_id, status: "evaluated", ...EvaluateDetails }
```

### 5.3 GET /results/{job_id}

```
响应: { job_id, status, algorithm, chromosome, evaluating, ... }
evaluating: pop × 22 的 list[list[float|null]]
```

---

## 六、注意事项

1. **NMF 和 PP 结果非确定性**：每次运行产出略有差异（布谷鸟搜索随机初始化+Levy flight 随机步长），AHP-Fuzzy 结果完全确定
2. **收敛曲线只在前 200 个点传给前端**（`ch.slice(0, 200)`），减少网络传输量
3. **子系统得分只有 ALL 和 AHP_FUZZY 方法返回**：NMF 和 PP 单独调用时不产生子系统数据
4. **ALL 的 scores 为 null**：ALL 是整合排名，不产生评分，前端直接展示名次徽章
5. **评价结果有幂等性**：同一个 evaluating 矩阵跑两次 ALL，结果默认缓存不会重复计算（需手动清除或覆盖）
