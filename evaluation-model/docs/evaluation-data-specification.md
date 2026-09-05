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

  "radar": {
    "indicators": [
      { "name": "NMF", "max": 5246.93 },
      { "name": "PP", "max": 908.31 },
      { "name": "AHP_FUZZY", "max": 661.60 }
    ],
    "plans": [
      { "plan": "方案1", "values": [5246.93, 908.31, 661.60] },
      { "plan": "方案2", "values": [5201.15, 897.42, 655.10] }
    ]
  },

  "raw_indicators": {
    "subsystems": [
      { "name": "水子系统", "indices": [0, 1, 2, 3, 4, 5] },
      { "name": "沙子系统", "indices": [6, 7] },
      { "name": "能子系统", "indices": [8, 9, 10, 11, 12] },
      { "name": "灾子系统", "indices": [13, 14, 15] },
      { "name": "生态子系统", "indices": [16, 17, 18, 19, 20, 21] }
    ],
    "schemes": [
      { "plan": "方案1", "values": [8.80, 27.78, 0.007, ...] }
    ]
  }
}
```

### 3.1 排名表格行说明

| 行 | rank 字段 | scores 字段 | 页面呈现 |
|----|-----------|------------|---------|
| NMF / PP / AHP_FUZZY | 各算法排名数组（0=最优） | 该算法的评分值（越大越好） | 得分 + 进度条 |
| ALL | 序号总和整合排名数组（0=最优） | null | 排名徽章（🥇🥈🥉）展示每个方案的整合名次 |

### 3.2 收敛曲线说明

- `convergence.NMF` — NMF 算法的适应度历史（重构误差 \|A-WH\|²），约 500 个点
- `convergence.PP` — PP 算法的适应度历史（投影质量 Q），约 500 个点
- 两条曲线 Y 轴尺度不同，通常用独立 Y 轴或分图展示
- 曲线呈**下降趋势**：迭代越深，适应度越小（越优）

### 3.3 算法得分雷达图与原始指标说明

- `radar.indicators` — 3 个评价算法（NMF / PP / AHP_FUZZY）各为一个轴，max 取该算法得分的最大值
- `radar.plans` — 按 ALL 整合排名取前 10 个方案，每个方案一条多边形（三轴得分）
- `raw_indicators` — 前 10 名方案的 22 项原始评价指标（`original_data_matrix` 对应行），`subsystems` 给出指标 → 5 子系统的分组索引，供桑基图等使用

---

## 四、前端页面数据映射

### 4.1 评价分析页面

| 图表位置 | 图表类型 | 数据来源 | 数据字段 |
|---------|---------|---------|---------|
| 雷达图 | 算法得分雷达图 | NMF / PP / AHP_FUZZY 得分 | `radar.indicators` + `radar.plans` |
| 桑基图 | 评价指标桑基图 | 前 10 名方案原始指标 | `raw_indicators.schemes` + `raw_indicators.subsystems` |
| 收敛曲线 | 算法收敛曲线 | NMF / PP | `convergence.NMF / convergence.PP` |
| 排名表格 | 排名表 | 全部算法 + 整合 | `rankings[*]` |

### 4.2 决策分析页面

> 决策分析页面数据来自 `GET /decision/{job_id}`（MATLAB `plan_details`，非评价系统产出）。方案排序与评价分析页一致（已评价时按 ALL 整合排名）。

| 位置 | 内容 | 数据来源 | 来源字段 |
|------|------|---------|---------|
| 左列 | 目标满足情况 | 决策方案明细 | `plans[].targets.*` |
| 中列 | 过程曲线（水位/流量/出力） | 决策方案明细 | `plans[].level_long / level_liu / qout_long / qout_liu / power_long / power_liu` |
| 右列 | 水量使用流向图 | 决策方案明细 | `plans[].water_usage.*` |

#### 决策分析可用数据字段（plans[] 每项）

```
plans[i]
├── index:        int                种群中的原始索引（1-based）
├── label:        string             按排名标注的方案名（方案1=最优）
├── objectives:   (M,)               目标函数值
├── level_long:   (V/2,)             龙羊峡逐时段水位
├── level_liu:    (V/2,)             刘家峡逐时段水位
├── qout_long:    (V/2,)             龙羊峡出库流量
├── qout_liu:     (V/2,)             刘家峡出库流量
├── power_long:   (V/2,)             龙羊峡出力
├── power_liu:    (V/2,)             刘家峡出力
│
├── targets                          各目标满足率 (0~100)
│   ├── power:       发电
│   ├── ecology:     生态
│   ├── irrigation:  农业
│   ├── domestic:    工业生活
│   ├── spill:       不弃水
│   └── sediment:    调沙
│
├── water_usage                      分类水量分配（亿 m³）
│   ├── power / ecology / irrigation / domestic / spill / sediment
│
└── coordination                     子系统多年平均有序度
    ├── h_water / h_ele / h_sed / h_eco
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

### 5.4 GET /decision/{job_id}

```
响应: { job_id, status, algorithm, evaluated, year_start, year_end, plans: [...], message }
plans: 按排名排序的前 10 个方案明细（见 4.2 节字段）
evaluated: 是否按 ALL 整合排名排序（false = 按 Pareto rank + 拥挤距离）
```

---

## 六、注意事项

1. **NMF 和 PP 结果非确定性**：每次运行产出略有差异（布谷鸟搜索随机初始化+Levy flight 随机步长），AHP-Fuzzy 结果完全确定
2. **收敛曲线全量传给前端**（约 500 个点，无截断）
3. **雷达图与原始指标只有 ALL 方法返回**（单算法模式仅有该算法自身的 radar）；子系统原始指标来自 `original_data_matrix`
4. **ALL 的 scores 为 null**：ALL 是整合排名，不产生评分，前端直接展示名次徽章
5. **评价结果有幂等性**：同一个 evaluating 矩阵跑两次 ALL，结果默认缓存不会重复计算（需手动清除或覆盖）
