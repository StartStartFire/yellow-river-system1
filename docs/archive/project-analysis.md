# 水库群（梯级）多目标调度模型 —— 项目逆向分析报告

> **分析日期**: 2026-06-21
> **项目路径**: E:/model/yellow_river_project/matlab-model/
> **分析目标**: 对基于 NSGA-II / PAEM 算法的梯级水库多目标优化调度 MATLAB 项目进行完整逆向分析
>
> **⚠️ 快照说明**：本文档为 2026-06-21 的逆向分析快照。此后代码有如下演进（以代码为准，详见 model-specification.md）：
> ① 主函数签名新增第 5 参数 `Pc`（交叉概率，原硬编码 0.9）；
> ② 新增 `evaluate_objective_save_info.m`（返回 22 项评价指标 evaluating 与决策明细 plan_details）、`find_representative_solution.m`、`push_callback_data.m`（回调统一封装）、`http_callback_push.m`；
> ③ 起调水位（LONG_Z_INI_VAL / LIU_Z_INI_VAL）、防凌流量（QMIN_VAL）、年份范围（YEAR_START / YEAR_END）支持 Web 服务动态注入；
> ④ `nsga_2_para` 返回值扩展为 chromosome + evaluating + plan_details。

---

## 一、系统功能说明

### 1.1 项目总体功能

本项目实现了一个 **多年长系列（Y 年）梯级水库联合调度多目标优化模型**。它以**龙羊峡**和**刘家峡**两座黄河上游控制性水库的水位运行过程作为决策变量，通过 NSGA-II（非支配排序遗传算法）或 PAEM（近似评估进化算法）进行多目标进化优化，求解在供水、发电、输沙、生态四个维度上的 Pareto 最优调度方案集。

### 1.2 业务问题

黄河流域上游"龙羊峡—刘家峡"梯级水库群承担着**供水、发电、防凌、调水调沙、生态保障**等多重任务，各目标之间相互冲突。本项目用多目标进化算法搜索 Pareto 前沿，为调度决策者提供量化的方案权衡依据。

### 1.3 核心目标

| 目标编号 | 名称 | 数学表达 | 优化方向 |
|---------|------|---------|---------|
| f1 (M=2/3) | 兰州断面多年平均缺水量 | $\min \frac{1}{Y}\sum_i \sum_j \max(LAN_{i,j} - Q_{liuout_{i,j}} - LIU\_LAN_{i,j}, 0) \cdot xishu_j$ | 最小化 |
| f2 (M=2/3) | 梯级电站群年均发电量 | $\min (-\frac{1}{Y}\sum_i E\_tiji_i)$ | 最小化(取负) |
| f3 (M=3) | 梯级调度系统总协同度 | $\min (-\text{geomean}(\max(0, [H_{water}, H_{ele}, H_{sed}, H_{eco}])))$ | 最小化(取负) |

### 1.4 关键约束条件

| 约束类型 | 具体内容 | 处理方式 |
|---------|---------|---------|
| 水量平衡 | V(t+1) = V(t) + (Qin - Qout)·Δt | 物理方程强制满足 |
| 库容边界 | 龙羊峡 [42.63, 242.9] 亿m³；刘家峡 [6.223, 39.93] 亿m³ | 截断修正 |
| 水位边界 | VarMin/VarMax 由数据文件读取 | 遗传算子裁剪 + 评估修正 |
| 装机容量 | 龙羊峡 ≤128万kW；刘家峡 ≤122.5万kW | 截断+弃水计算 |
| 保证出力 | 龙羊峡 ≥58.7万kW；刘家峡 ≥40万kW（特枯年8折） | 迭代增大出库流量 |
| 生态流量 | 龙羊峡出库 ≥350 m³/s（下限）≤1050 m³/s（上限） | 强制修正决策变量 |
| 防凌流量 | 11月~3月刘家峡出库 ≤[610,420,420,420,420] m³/s | 两库协同蓄泄 |
| 兰州断面需水 | Qliuout ≥ LAN - LIU_LAN | 强制抬升 |
| 调沙规则 | 7月下旬~8月上旬，P≤0.80且库容充足时触发 | 规则驱动 |

---

## 二、项目目录结构

```
matlab-model/
├── *.m                          # 核心 MATLAB 源文件
├── data.xlsx                    # 输入数据文件（含所有实测/规划数据）
├── NSGA2_progress.jsonl         # NSGA-II 进化过程日志（JSON Lines格式）
├── docs/                        # 技术文档
│   ├── model-specification.md   # 模型技术规格
│   ├── project-analysis.md      # 本分析文档
│   └── scheduling-rules.md      # 调度规则
└── .git/                        # Git 仓库
```

### 2.1 核心文件分类

#### 主控层（入口 + 算法框架）
| 文件 | 功能 |
|------|------|
| `main.m` | **程序入口脚本**：加载数据 → 调用 NSGA-II 或 PAEM |
| `nsga_2_para.m` | NSGA-II 算法主框架：种群 → 进化 → 评价 → 排序 → 替换（签名含 Pc） |
| `PAEM_para.m` | PAEM 算法主框架：近似评价 + 精确评价两阶段（签名含 Pc） |

#### 目标评估层（核心仿真模型）
| 文件 | 功能 |
|------|------|
| `evaluate_objective.m` | **精确评价**：完整 Y 年逐时段仿真，含详细协同度计算 |
| `evaluate_objective_NSGA2.m` | **NSGA-II 评价**：与精确评价逻辑相同，返回计算结果 |
| `evaluate_objective_PAEM.m` | **PAEM 近似评价**：含 K_mut 次随机变异扰动 + 早停机制 |
| `evaluate_objective_save_info.m` | **决策评价（新增）**：额外返回 22 项评价指标（evaluating）与决策明细（plan_details） |

#### 遗传操作层
| 文件 | 功能 |
|------|------|
| `initialize_population.m` | 种群初始化：均匀随机生成 + 汛期水位趋势修正 + 目标评价 |
| `genetic_operator.m` | 遗传算子：SBX 交叉（90%概率）+ 多项式变异（10%概率） |
| `tournament_selection.m` | 二进制锦标赛选择：按 rank 优先、拥挤距离次之 |
| `mutation_one_variable.m` | 单变量多项式变异（PAEM 扰动使用） |

#### 排序与选择层
| 文件 | 功能 |
|------|------|
| `non_domination_sort_mod.m` | 快速非支配排序 + 拥挤距离计算 |
| `replace_chromosome.m` | 精英保留替换：rank + 拥挤距离择优 |
| `find_nondominated_solution.m` | 提取 Pareto 非支配解集（PAEM 内部使用） |
| `find_representative_solution.m` | 选代表性最优解（Pareto 前沿拥挤距离最大个体，回调过程数据用，新增） |

#### 辅助工具层
| 文件 | 功能 |
|------|------|
| `chz1.m` | 一维线性插值（已知 x 求 y，如水位→库容） |
| `chz2.m` | 一维线性插值（已知 y 求 x，如库容→水位） |
| `load_data.m` | Excel 数据加载：特性曲线、来水、需水、边界等（支持年份范围截取） |
| `init_log_file.m` | 日志文件初始化（目录创建 + fopen） |
| `write_json_log.m` | JSON Lines 格式日志写入 |
| `preprocess_results_for_json.m` | 结果预处理（NaN/Inf 转换） |

#### 回调推送层（新增，Web 服务对接）
| 文件 | 功能 |
|------|------|
| `push_callback_data.m` | 回调数据统一封装：汇总指标（progress）+ 代表性解过程数据（process_data），被两个主循环每 10 代调用 |
| `http_callback_push.m` | webwrite HTTP POST 封装（超时 1s、失败静默降级） |

### 2.2 数据结构定义

染色体 `chromosome` 矩阵每行包含（维度 = `V + M + 2`）：

| 列范围 | 内容 | 说明 |
|-------|------|------|
| 1 : 20×Y | 龙羊峡逐时段水位 | 长系列54年×20时段=1080维 |
| 20×Y+1 : 40×Y | 刘家峡逐时段水位 | 同上，1080维 |
| V+1 : V+M | 目标函数值 | f1(缺水) / f2(发电) / f3(协同度) |
| V+M+1 | 非支配排序等级(rank) | 1为最优前沿 |
| V+M+2 | 拥挤距离(crowding distance) | 越大越分散 |

---

## 三、模块划分与调用关系图

### 3.1 调用链（缩进表示嵌套调用层级）

```
main.m  [程序入口]
├── load_data()
│   ├── xlsread() × 多次 → 读取 data.xlsx 各表
│   └── 生成全局变量: VarMin, VarMax, LONG_IN, LAN, ...
│
├── nsga_2_para(pop, iterate, M, Q_sediment, Pc)
│   ├── init_log_file() → 打开日志文件
│   ├── initialize_population()
│   │   ├── unifrnd() → 随机生成水位
│   │   ├── 汛期水位趋势修正逻辑
│   │   ├── evaluate_objective() ← 精确评价每个个体
│   │   └── non_domination_sort_mod()
│   │       ├── 快速非支配排序
│   │       └── 拥挤距离计算
│   │
│   ├── 进化主循环 for i = 1:iterate
│   │   ├── tournament_selection() → 选择父代
│   │   ├── genetic_operator()
│   │   │   ├── SBX 模拟二进制交叉 (90%)
│   │   │   └── 多项式变异 (10%)
│   │   ├── evaluate_objective_NSGA2() → 评价子代
│   │   │   ├── chz1() / chz2() 线性插值
│   │   │   ├── 水量平衡计算
│   │   │   ├── 防凌/生态/需水/调沙规则处理
│   │   │   ├── 14座梯级电站出力计算
│   │   │   └── 协同度序参量计算 (M=3)
│   │   ├── non_domination_sort_mod()
│   │   └── replace_chromosome()
│
├── PAEM_para(pop, iterate, K_mut, M, Q_sediment, Pc)
│   ├── [同上框架，但评价函数不同]
│   ├── evaluate_objective_PAEM() ← 近似评价
│   │   ├── mutation_one_variable() → K_mut 次随机扰动
│   │   ├── 完整仿真循环（与 NSGA2 类似）
│   │   └── find_nondominated_solution() → 扰动后选非支配
│   ├── [进化循环]
│   └── evaluate_objective() → 最终精确评价
│       └── [比较近似+精确差异]
```

### 3.2 模块层次图

```
┌─────────────────────────────────────────────────────┐
│                    用户入口层                         │
│                   main.m                             │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│   NSGA-II 主控    │    │   PAEM 主控           │
│  nsga_2_para.m   │    │  PAEM_para.m          │
└────────┬─────────┘    └──────────┬───────────┘
         │                         │
         ▼                         ▼
┌──────────────────────────────────────────────┐
│           遗传操作与进化控制层                 │
│  initialize_population.m                     │
│  tournament_selection.m                      │
│  genetic_operator.m                          │
│  mutation_one_variable.m                     │
└────────────────────┬─────────────────────────┘
                     ▼
┌──────────────────────────────────────────────┐
│           多目标排序与选择层                   │
│  non_domination_sort_mod.m                   │
│  replace_chromosome.m                        │
│  find_nondominated_solution.m                │
└────────────────────┬─────────────────────────┘
                     ▼
┌──────────────────────────────────────────────┐
│         核心仿真评价层（最核心模块）            │
│  evaluate_objective.m    (精确评价)           │
│  evaluate_objective_NSGA2.m (NSGA-II评价)     │
│  evaluate_objective_PAEM.m (PAEM近似评价)     │
└────────────────────┬─────────────────────────┘
                     ▼
┌──────────────────────────────────────────────┐
│           工程计算与辅助工具层                 │
│  chz1.m / chz2.m (线性插值)                 │
│  load_data.m (数据加载)                      │
│  init_log_file.m / write_json_log.m         │
│  preprocess_results_for_json.m              │
└──────────────────────────────────────────────┘
```

---

## 四、数据流分析

### 4.1 数据流图（文字描述）

```
┌──────────────────┐     xlsread()     ┌────────────────────┐
│   data.xlsx       │ ──────────────→  │ load_data (数据加载器)│
│  ┌──────────────┐ │                  └────────┬───────────┘
│  │ LONG-ZV/ZQ   │ │                           │
│  │ LIU-ZV/ZQ    │ │                           ▼
│  │ LONGIN       │ │           ┌───────────────────────────┐
│  │ LONG-LIU     │ │           │     全局变量(Globals)      │
│  │ LIU-LAN      │ │           │  LONG_IN, LONG_LIU, ...   │
│  │ LAN          │ │           │  VarMin, VarMax, Y, P     │
│  │ LAN-unagr    │ │           │  LONG_ZV, LIU_ZV, ...     │
│  │ Q_eco        │ │           └───────────────────────────┘
│  │ P            │ │                        │
│  │ LONGLIU-BOUND│ │                        ▼
│  │ longliu_water │ │           ┌───────────────────────────┐
│  │ liulan_water │ │           │    决策变量 x (水位)       │
│  │ xixian_up/down│           │  前20×Y: 龙羊峡水位        │
│  └──────────────┘ │           │  后20×Y: 刘家峡水位        │
└──────────────────┘            │  (由遗传算法生成/变异)      │
                                └───────────┬───────────────┘
                                            ▼
                  ┌─────────────────────────────────────────┐
                  │        evaluate_objective* 系列函数       │
                  │  逐时段仿真 → 水量平衡 → 出力计算 → 协同度  │
                  └───────────┬─────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
          ┌──────────────┐     ┌────────────────────┐
          │ 目标函数值     │     │  详细仿真结果        │
          │ f_obj(1..M)   │     │  Vlong, Vliu       │
          │ (优化驱动)    │     │  Qlongout, Qliuout │
          └───────┬──────┘     │  14座电站出力        │
                  │            │  ...               │
                  ▼            └─────────┬──────────┘
          ┌──────────────┐              │
          │ NSGA-II/PAEM │              ▼
          │ Pareto 前沿  │    ┌────────────────────┐
          │ chromosome   │    │  JSON 日志文件      │
          └──────────────┘    │ NSGA2_progress.jsonl│
                              └────────────────────┘
```

### 4.2 输入数据详解

**数据源**: `data.xlsx` Excel 工作簿

| 工作表名 | 内容 | 维度 | 用途 |
|---------|------|------|------|
| `LONG-ZV` | 龙羊峡水位-库容曲线 | N×2 | chz1/chz2 插值用 |
| `LONG-ZQ` | 龙羊峡水位-流量曲线 | N×2 | 下游水位插值 |
| `LIU-ZV` | 刘家峡水位-库容曲线 | N×2 | chz1/chz2 插值用 |
| `LIU-ZQ` | 刘家峡水位-流量曲线 | N×2 | 下游水位插值 |
| `LONGIN` | 龙羊峡入库流量 | Y×20 | 天然来水 |
| `LONG-LIU` | 龙-刘区间来水 | Y×20 | 区间入流 |
| `LIU-LAN` | 刘-兰区间来水 | Y×20 | 区间入流 |
| `LAN` | 兰州断面总需水 | Y×20 | 供水目标需求 |
| `LAN-unagr` | 兰州非农业需水 | Y×20 | 工业生活需水 |
| `LAN-agr` | 兰州农业需水 | Y×20 | 农业需水 |
| `Q_eco` | 兰州断面生态需水 | Y×20 | 生态目标需求 |
| `P` | 来水频率 | Y×1 | 丰枯判断 |
| `LONGLIU-BOUND` | 龙刘水位上下限 | 40×2 | 决策变量边界 |
| `CANSHU` | 水库群物理参数 | — | 备用 |
| `longliu_water` | 龙刘区间用水 | Y×20 | 净来水修正 |
| `liulan_water` | 刘兰区间用水 | Y×20 | 净来水修正 |
| `xixian_up` | 西上线调水 | Y×20 | 调水修正 |
| `xixian_down` | 西下线调水 | Y×20 | 调水修正 |

**注**: `Y` 为年数（当前 54 年，数据覆盖 **1970—2023 年**），每年 20 个时段（5-8月分旬，其余按月）。

### 4.3 输出数据

| 输出 | 格式 | 位置 | 内容 |
|------|------|------|------|
| NSGA-II 进化过程日志 | JSON Lines (.jsonl) | `NSGA2_progress.jsonl` | 每代所有个体的目标值、进度百分比 |
| PAEM 进化过程日志 | JSON (单文件) | `PAEM_progress.json` | PAEM 进化过程 |
| nsga_2_para 返回值 | MATLAB struct | 工作区 | `output.chromosome` Pareto 解集 + `output.evaluating`（pop×22 评价指标）+ `output.plan_details`（决策明细） |
| PAEM_para 返回值 | MATLAB struct | 工作区 | `output.chromosome_acc` 精确评价解集 |
| 回调推送 | HTTP POST | Web 服务 /cb | 每 10 代 progress 汇总指标 + process_data 过程数据（经 push_callback_data.m） |

---

## 五、算法分析

### 5.1 NSGA-II（主算法）

**架构**：标准 NSGA-II [Deb et al., 2002]

| 组件 | 实现细节 |
|------|---------|
| 编码 | 实数编码（水位值），维度 V = 20 × Y × 2 ≈ 2160 |
| 初始化 | 均匀随机 [VarMin, VarMax] + 汛期水位上升趋势修正 |
| 选择 | 二进制锦标赛（tour=2）：rank 优先 → 拥挤距离次之 |
| 交叉 | SBX（模拟二进制交叉），η_c=20，概率 0.9 |
| 变异 | 多项式变异，η_m=20，概率 0.1 |
| 排序 | 快速非支配排序 O(MN²) |
| 替换 | 精英保留：低 rank 优先 → 拥挤距离大优先 |
| 种群规模 | 15（当前配置偏小） |
| 进化代数 | 20（当前配置偏小） |

### 5.2 PAEM（近似评价算法，学术对比实验用）

PAEM 是 NSGA-II 框架的变体，仅用于学术对比实验，核心区别：

1. **近似评价**：`evaluate_objective_PAEM` 对每个个体生成 K_mut 个变异版本做局部搜索
2. **随机扰动**：随机选择一年一时段，对决策变量做单变量多项式变异
3. **早停机制**：当状态变量和决策变量变化小于 accuracy 阈值时提前结束该年计算
4. **精确后评价**：进化结束后，对最终种群调用 `evaluate_objective` 做精确评价
5. **输出比较**：计算近似解与精确解的相对误差

### 5.3 协同度计算（M=3 时启用）

四维子系统有序度加权：

| 子系统 | 序参量 | 权重(年) | 权重(多年) |
|-------|--------|---------|-----------|
| **供水 H_water** | 工业生活保证率(0.1) + 农业关键期缺水深度(0.25) + 农业关键期总缺水(0.25) + 非关键期保证率(0.20) + 非关键期总缺水(0.20) | 加权和 | 算术平均 / Y |
| **发电 H_ele** | 防凌期保证率(0.2) + 防凌期平均出力(0.2) + 非防凌期保证率(0.3) + 非防凌期平均出力(0.3) | 加权和 | 算术平均 / Y |
| **输沙 H_sed** | 调沙流量有序度(0.6) + 调沙历时有序度(0.4) | 加权和 | 0.8×均值 + 0.2×频率有序度 |
| **生态 H_eco** | 生态保证率(0.4) + 一次脉冲(0.3) + 多次脉冲(0.3) | 加权和 | 算术平均 / Y |

**总协同度**: `H_tiji = geomean(max(0, [H_water, H_ele, H_sed, H_eco]))`

### 5.4 梯级电站群出力模型

龙羊峡—刘家峡之间的 **14 座梯级水电站**：

| 电站 | 装机(万kW) | 出力公式 |
|------|-----------|---------|
| 龙羊峡 | 128 | 8.6 × H_long × Q_longout / 10000 |
| 拉西瓦 | 280 | 8.3 × 205 × (Q_longout+LONG_LIU) / 10000 |
| 尼那 | 16 | 8 × 15 × (Q_longout+LONG_LIU) / 10000 |
| 李家峡 | 160 | 8.3 × 122 × (Q_longout+LONG_LIU) / 10000 |
| 积石峡 | 102 | 8.3 × 66 × (Q_longout+LONG_LIU) / 10000 |
| 直岗拉卡 | 19 | 8.2 × 12.5 × (Q_longout+LONG_LIU) / 10000 |
| 康扬 | 30 | 8.2 × 18.7 × (Q_longout+LONG_LIU) / 10000 |
| 公伯峡 | 150 | 8.3 × 99.3 × (Q_longout+LONG_LIU) / 10000 |
| 苏只 | 22 | 8.3 × 16 × (Q_longout+LONG_LIU) / 10000 |
| 刘家峡 | 122.5 | 8.6 × H_liu × Q_liuout / 10000 |
| 盐锅峡 | 40 | 7.9 × 38 × (Q_liuout+LIU_LAN) / 10000 |
| 八盘峡 | 18 | 8.3 × 18 × (Q_liuout+LIU_LAN) / 10000 |
| 小峡 | 23 | 8.3 × 13.8 × (Q_liuout+LIU_LAN) / 10000 |
| 大峡 | 30 | 8.3 × 24 × (Q_liuout+LIU_LAN) / 10000 |
| 青铜峡 | 30 | 8.3 × 16 × (Q_liuout+LIU_LAN) / 10000 |

---

## 六、工程风险分析

### 6.1 硬编码参数

| 位置 | 参数 | 数值 | 风险 |
|------|------|------|------|
| `evaluate_objective*.m` | 龙羊峡起调水位 | 2580 m | 默认值，可经全局变量 LONG_Z_INI_VAL 动态注入 |
| `evaluate_objective*.m` | 刘家峡起调水位 | 1720 m | 默认值，可经全局变量 LIU_Z_INI_VAL 动态注入 |
| `evaluate_objective*.m` | 龙羊峡死/满库容 | 42.63 / 242.9 亿m³ | 硬编码在水库调度逻辑中 |
| `evaluate_objective*.m` | 刘家峡死/满库容 | 6.223 / 39.93 亿m³ | 同上 |
| `evaluate_objective*.m` | 防凌流量 Qmin | [610,420,420,420,420] | 默认值，可经全局变量 QMIN_VAL 动态注入；仅5个时段，索引j-8 |
| `evaluate_objective*.m` | 防凌期龙羊峡出库 | 550 m³/s | 固定值 |
| `evaluate_objective*.m` | 生态流量下限 | 350 m³/s | 固定阈值 |
| `evaluate_objective*.m` | 生态流量上限 | 1050 m³/s | 固定阈值 |
| `evaluate_objective*.m` | 保证出力特枯折扣 | 0.8 | 硬编码折扣系数 |
| `evaluate_objective*.m` | 保证出力 P 阈值 | 0.75 | 来水频率分界点 |
| `evaluate_objective*.m` | 调沙流量 | 1350 / 1800~2200 | 龙羊峡1350，目标区间固定 |
| `evaluate_objective*.m` | 14座电站出力公式系数 | 各不等的8.0~8.6 | 水能系数硬编码 |
| `evaluate_objective*.m` | 装机容量 | 各电站固定值 | 扩建需改代码 |
| `evaluate_objective*.m` | SBX 分配系数 mu | 20 | 遗传参数 |
| `evaluate_objective*.m` | 多项式变异系数 mum | 20 | 遗传参数 |
| `nsga_2_para.m` / `genetic_operator.m` | 交叉概率 Pc | 0.9（默认） | 已参数化：Pc 经主函数签名传入 |
| `nsga_2_para.m` | 进化代数 | 20 (由调用方传参) | 当前配置过低 |
| `nsga_2_para.m` | 种群规模 | 15 (由调用方传参) | 当前配置过低 |
| `evaluate_objective*` | 时段转换系数 xishu | 20个固定值 | 对应时段划分硬编码 |
| `evaluate_objective*` | 天数 t | 20个固定值 | 对应时段划分硬编码 |
| `evaluate_objective*` | 农业关键期时段索引 | [1 2 5 15 16 18] | 业务规则硬编码 |
| `evaluate_objective*` | 非关键期时段索引 | [3 4 6:9 13 14 17 19 20] | 同上 |
| `evaluate_objective*` | 防凌期时段范围 | j>8 && j<14 | 固定时段窗口 |
| `evaluate_objective*` | 调沙期时段 | j==3 \|\| j==4 | 固定7月下旬~8月上旬 |
| `evaluate_objective*` | 10月预腾防凌 | j==8, Qliuout=700 | 固定规则 |
| `evaluate_objective*` | 刘家峡最大过机流量 | 1200 m³/s | 固定限值 |
| `evaluate_objective*` | 协同度权重向量 | [0.1,0.25,0.25,0.20,0.20] 等 | 权重可调但硬编码 |
| `evaluate_objective*` | 有序度分母(阈值) | 26.63, 41.56, 1164 等 | 固定理想值/极值 |
| `initialize_population.m` | 汛期时段范围 | 1:7 | 固定前7个时段 |
| `initialize_population.m` | 汛期水位增量上限 | 2m | 随机增量边界 |

### 6.2 全局变量

| 变量 | 类型 | 读写位置 | 风险说明 |
|------|------|---------|---------|
| `Y` | 年数 | 全局读写 | 数据加载 → 所有评估函数，无保护 |
| `VarMin`, `VarMax` | 边界 | 全局读写 | 多个函数依赖，可被意外修改 |
| `LONG_ZV/ZQ`, `LIU_ZV/ZQ` | 插值表 | 全局只读 | 所有 chz1/chz2 调用依赖 |
| `LONG_IN`, `LONG_LIU`, `LIU_LAN` | 来水数据 | 全局只读 | 所有评估函数依赖 |
| `LAN`, `LAN_unagr` | 需水数据 | 全局只读 | 供水目标计算依赖 |
| `Q_eco` | 生态需水 | 全局只读 | 生态目标计算依赖 |
| `P` | 来水频率 | 全局只读 | 丰枯判断依赖 |

**风险**: MATLAB 全局变量在函数工作区中可被任意修改，无访问控制。  
多个评估函数共享同一组全局变量，`evaluate_objective_NSGA2` 中直接回写决策变量 `x` 并修改 `VarMax` 用于索引访问。

### 6.3 重复逻辑

| 重复内容 | 出现位置 | 代码行数 | 说明 |
|---------|---------|---------|------|
| 主仿真循环 | evaluate_objective, evaluate_objective_NSGA2, evaluate_objective_PAEM | ~550 行 × 3 | 三份几乎相同的长循环，最小差异（JSON 日志/PAEM扰动） |
| 库容截断代码段 | 三个评估函数中各出现 8~10 次 | ~15 行/段 | 龙羊峡/刘家峡"小于死库容/大于满库容"的截断逻辑完全重复 |
| 14座电站出力计算 | 三个评估函数 | ~15 行/函数 | 完全相同 |
| 协同度计算 | 三个评估函数 | ~120 行/函数 | 完全相同 |
| JSON日志写入 | evaluate_objective_NSGA2 和 PAEM | ~50 行 | 独立实现的文件写入而非复用 write_json_log |

### 6.4 隐藏依赖

1. **数据文件位置硬编码**: `load_data('data.xlsx', ...)` 使用相对路径，依赖于运行目录
2. **Excel 表结构依赖**: 各工作表名称、单元格范围（如 `'G45:Z46'`）在代码中硬编码
3. **chz1/chz2 插值函数健壮性**: 边界外直接返回端点值（flag=0 但不处理），可能导致计算偏差
4. **时序耦合**: 各年通过起调水位 `LONG_Z_INI(i+1)=x(j+(i-1)*20)` 串联，形成链条式状态依赖，不能并行计算
5. **决策变量回写副作用**: 评估函数内修改输入参数 `x`（MATLAB 按值传递，但对调用者无影响，仅为内部使用），但修改 `VarMax` 索引访问可能导致边界越界

### 6.5 其他风险

1. **种群规模过小**（pop=15）：对于 2160 维的高维优化问题，15 个个体远不足以覆盖 Pareto 前沿
2. **进化代数过少**（iterate=20）：在如此高维的搜索空间中，20 代远未收敛
3. **`numel` 误用**: `evaluate_objective_NSGA2.m:617`、`evaluate_objective.m:616`、`evaluate_objective_PAEM.m:439` 三处 `numel(Qshortage_eco(i,:), Qshortage_eco(i,:)==0)` 语法不正确，`numel` 不接受条件参数，该行实际不会计算生态保证率
4. **`find` 误用**: 协同度计算中多处使用 `length(find(condition))` 而非 `sum(condition)`，效率低下但逻辑正确
5. **PAEM 精度控制缺陷**: `flag_s` 和 `flag_d` 循环内只在第一轮判断后 break，但 `i_start` 从随机年起始而非从头，可能导致状态变量未初始化
6. **结果浮点精度**: `abs(chromosome(:, (V + 1): (V + M)))` 在 NSGA-II 日志中取绝对值，可能掩盖负号问题

---

## 七、后续开发建议

### 7.1 架构重构（高优先级）

1. **消除三重代码重复**：将 `evaluate_objective_NSGA2.m` 和 `evaluate_objective_PAEM.m` 中与 `evaluate_objective.m` 相同的约550行仿真逻辑抽取为共享函数，三份评价函数只保留差异部分（日志格式、PAEM扰动、精度控制等）。

2. **全局变量 → 参数化**：将全局变量封装为结构体或使用 MATLAB `handle` 类传递，消除全局变量副作用风险。

3. **硬编码参数外移**：
   - 水库物理参数（死库容、满库容、装机容量、保证出力等）→ 配置文件或 Excel 专用工作表
   - 时段划分参数（xishu, t）→ 从数据文件读取
   - 协同度权重 → 从配置文件读取

### 7.2 算法增强（中优先级）

4. **增大搜索规模**：当前 pop=15, iterate=20 对 2160 维问题过于保守。建议 pop≥100, iterate≥500。

5. **增加约束处理多样性**：当前主要依赖截断修复，对高维问题搜索效率低。可引入：
   - ε-约束法
   - 自适应罚函数
   - 约束支配原则（如 CDP）

6. **PAEM 精度控制修正**：修复状态变量未初始化和早停判断逻辑缺陷。

### 7.3 工程化改进（中优先级）

7. **统一日志系统**：三份评价函数的 JSON 日志写入全部复用 `write_json_log.m`，消除各函数内部的独立文件操作代码。

8. **数据驱动**：使用 MATLAB `table` 或 `containers.Map` 替代原始 Excel 读取，支持 CSV/JSON 等多种格式输入。

9. **单元测试框架**：为关键计算（水量平衡、出力公式、有序度计算）编写测试用例。

### 7.4 质量保障（低优先级）

10. **修复 `numel` bug**：`evaluate_objective_NSGA2.m:617` 等三处（见 6.5 第 3 条）修复生态保证率计算。

11. **优化性能**：对 2160 维 × 20 代 × 15 个体的逐时段仿真，考虑向量化和预分配优化，避免循环内动态数组增长。

---

## 八、技术栈与依赖

| 项目 | 内容 |
|------|------|
| 语言 | MATLAB（R2019b+，使用 `jsonencode`） |
| 数据格式 | Excel (.xlsx) 输入，JSON/JSONL 输出 |
| 核心算法 | NSGA-II + PAEM（自研变体） |
| 外部依赖 | 无第三方工具箱（仅使用 MATLAB 内置函数） |
| 运行方式 | 直接运行 `main.m` |

---

*本文档为逆向分析结果，仅描述代码实际行为，不修改任何源代码。*
