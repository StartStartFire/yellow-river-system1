# 黄河上游水库群调度系统 — 数据库设计文档

> **状态：设计文档（尚未实施）**。当前阶段前端不连接数据库（见 frontend-service/CLAUDE.md「当前阶段不做」），本文档仅作为未来建库的设计参考。
>
> 本文档用于指导 AI 构建数据库，包含完整的建表 DDL、设计决策、数据流向和验证清单。
> 设计目标：低耦合、可持续维护、可复用。

---

## 一、总体架构

数据库按三层组织，层间单向依赖（下层不引用上层）：

```
┌─────────────────────────────────────────┐
│  第三层：调度流水线                        │
│  config_session / simulation_task        │
│  simulation_result / evaluation_result   │
│  case_record                            │
│          ↓ FK 单向引用                    │
├─────────────────────────────────────────┤
│  第二层：业务配置（静态模板）               │
│  dispatch_model / optimization_algorithm  │
│  model_algorithm_compatibility           │
│  algorithm_parameter                     │
│  dispatch_objective / constraint_template │
│  scenario_template                      │
│          ↓ FK 单向引用                    │
├─────────────────────────────────────────┤
│  第一层：数据底座（运行时数据）             │
│  reservoir（主数据）                      │
│  reservoir_time_series（时序宽表）         │
│  turbine / gate / turbine_snapshot       │
│  gate_snapshot                          │
│  warning_record / announcement           │
│  weather_record                         │
└─────────────────────────────────────────┘
```

**关键原则**：
1. 所有运行时数据只依赖 `reservoir_id`，不与业务表耦合
2. 多层配置模板独立存在，配置会话只做引用
3. 案例库用 JSON 快照，不关联流水线表（防止级联删除）
4. 指标新增 = 宽表加列，不需要改任何业务表结构

---

## 二、第一层：数据底座

### 2.1 水库主数据表

水库主数据是"几十年不变"的静态信息，所有其他表通过 `reservoir_id` 引用它。

```sql
CREATE TABLE reservoir (
  id        INTEGER       PRIMARY KEY,
  code      VARCHAR(10)   NOT NULL UNIQUE,
  name      VARCHAR(30)   NOT NULL,
  lat       FLOAT         NOT NULL,
  lng       FLOAT         NOT NULL,
  river_section VARCHAR(20) NOT NULL,   -- 龙羊峡以上 / 龙羊峡-刘家峡 / 刘家峡以下
  sort_order INTEGER       NOT NULL DEFAULT 0,

  -- 大坝属性
  dam_type          VARCHAR(20),
  crest_elevation   FLOAT,              -- 坝顶高程 (m)
  crest_length      FLOAT,              -- 坝顶长度 (m)
  max_height        FLOAT,              -- 最大坝高 (m)

  -- 特征水位
  check_flood_level   FLOAT,            -- 校核洪水位 (m)
  design_flood_level  FLOAT,            -- 设计洪水位 (m)
  normal_level        FLOAT,            -- 正常蓄水位 (m)
  flood_limit_level   FLOAT,            -- 汛限水位 (m)
  dead_level          FLOAT,            -- 死水位 (m)

  -- 库容参数
  total_capacity          FLOAT,        -- 总库容 (亿m³)
  active_capacity         FLOAT,        -- 兴利库容 (亿m³)
  flood_control_capacity  FLOAT,        -- 防洪库容 (亿m³)
  dead_capacity           FLOAT,        -- 死库容 (亿m³)

  -- 装机参数
  installed_capacity_total    FLOAT,    -- 总装机容量 (万kW)
  installed_capacity_service  FLOAT,    -- 在役装机 (万kW)
  annual_design_power         FLOAT,    -- 年设计发电量 (亿kW·h)
  turbine_count               INTEGER,  -- 机组台数
  gate_count                  INTEGER,  -- 闸门孔数

  -- 元数据
  status      VARCHAR(10) NOT NULL DEFAULT 'active',
  description TEXT,
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 2.2 水库时序数据表（宽表方案）

**水位、流量、库容、出力全部存一个表**，是系统最核心的数据表。

> 设计决策（对照其他方案）：
> - ❌ 每种指标一张表 → JOIN 地狱，加指标要建新表，不可维护
> - ❌ Key-Value 窄表 → 1 条真实记录 = 10 行存储，类型不安全
> - ✅ 宽表 → 加指标 = 加列；所有页面复用同一张表；一行就是一个时刻的完整快照

```sql
CREATE TABLE reservoir_time_series (
  id            BIGSERIAL    PRIMARY KEY,
  reservoir_id  INTEGER      NOT NULL REFERENCES reservoir(id),
  time          TIMESTAMP    NOT NULL,
  granularity   VARCHAR(10)  NOT NULL DEFAULT 'daily',  -- hourly | daily | monthly | yearly

  -- 水位
  water_level     FLOAT,       -- 坝前水位 (m)
  tailwater_level FLOAT,       -- 尾水位 (m)

  -- 流量
  inflow        FLOAT,         -- 入库流量 (m³/s)
  outflow       FLOAT,         -- 出库流量 (m³/s)
  turbine_flow  FLOAT,         -- 机组过流流量 (m³/s)

  -- 库容
  storage       FLOAT,         -- 当前库容 (亿m³)
  storage_rate  FLOAT,         -- 库容率 (%)

  -- 出力
  active_power    FLOAT,       -- 有功出力 (MW)
  reactive_power  FLOAT,       -- 无功出力 (Mvar)
  daily_power     FLOAT,       -- 日发电量 (万kW·h)

  CONSTRAINT uq_reservoir_time UNIQUE (reservoir_id, time, granularity)
);

CREATE INDEX idx_rts_reservoir_time ON reservoir_time_series (reservoir_id, time, granularity);
```

**granularity 字段说明**：

| granularity | 用途 | 每条记录代表 |
|-------------|------|-------------|
| `hourly` | 水调水情页面的过程曲线（历史/预报/调度线） | 该小时的数据 |
| `daily` | 首页水位过程线、负荷过程线、发电统计（日发电量） | 该日的日数据 |
| `monthly` | 报表统计-月度运行情况、经济指标、发电考核 | 该月的月数据 |
| `yearly` | 报表统计-年度汇总 | 该年的年数据 |

**数据量估算**（15 座水库）：daily 粒度每年约 15 × 365 = 5,475 行，10 年的 daily 数据仅约 5.5 万行，无需分区。

**查询示例**：

```sql
-- 首页水位过程线（龙羊峡近7天）
SELECT time, water_level
FROM reservoir_time_series
WHERE reservoir_id = 1 AND time BETWEEN '2025-07-09' AND '2025-07-15'
  AND granularity = 'daily'
ORDER BY time;

-- 首页发电统计（龙羊峡日/月/年）
SELECT
  MAX(CASE WHEN time = CURRENT_DATE THEN daily_power END) AS daily_power,
  SUM(daily_power) FILTER (WHERE date_trunc('month', time) = date_trunc('month', CURRENT_DATE)) AS monthly_power,
  SUM(daily_power) FILTER (WHERE date_trunc('year', time) = date_trunc('year', CURRENT_DATE)) AS yearly_power
FROM reservoir_time_series
WHERE reservoir_id = 1 AND granularity = 'daily';

-- 水调水情过程曲线（龙羊峡入库流量，含 hourly 粒度）
SELECT time, inflow
FROM reservoir_time_series
WHERE reservoir_id = 1 AND time BETWEEN '2025-07-01' AND '2025-07-15'
  AND granularity = 'hourly'
ORDER BY time;
```

### 2.3 机组 / 闸门主数据

```sql
CREATE TABLE turbine (
  id            INTEGER PRIMARY KEY,
  reservoir_id  INTEGER NOT NULL REFERENCES reservoir(id),
  name          VARCHAR(20) NOT NULL,
  rated_output  FLOAT,                -- 额定出力 (kW)
  rated_flow    FLOAT,                -- 额定流量 (m³/s)
  sort_order    INTEGER DEFAULT 0
);

CREATE TABLE gate (
  id            INTEGER PRIMARY KEY,
  reservoir_id  INTEGER NOT NULL REFERENCES reservoir(id),
  name          VARCHAR(20) NOT NULL,
  sort_order    INTEGER DEFAULT 0
);
```

### 2.4 机组 / 闸门实时快照

机组闸门快照独立于水库时序表，因为更新频率可能不同（机组可秒级）。

```sql
CREATE TABLE turbine_snapshot (
  id          BIGSERIAL PRIMARY KEY,
  turbine_id  INTEGER NOT NULL REFERENCES turbine(id),
  time        TIMESTAMP NOT NULL,
  status      VARCHAR(10) NOT NULL DEFAULT 'running',  -- running | stop | maintenance
  output      FLOAT,           -- 当前出力 (kW)
  flow        FLOAT,           -- 当前过流 (m³/s)
  gate_open   FLOAT,           -- 导叶开度 (%)
  UNIQUE (turbine_id, time)
);

CREATE INDEX idx_ts_turbine_time ON turbine_snapshot (turbine_id, time);

CREATE TABLE gate_snapshot (
  id               BIGSERIAL PRIMARY KEY,
  gate_id          INTEGER NOT NULL REFERENCES gate(id),
  time             TIMESTAMP NOT NULL,
  open_percentage  FLOAT,       -- 开度 (%)
  discharge_flow   FLOAT,       -- 泄流量 (m³/s)
  UNIQUE (gate_id, time)
);

CREATE INDEX idx_gs_gate_time ON gate_snapshot (gate_id, time);
```

### 2.5 预警 / 公告 / 天气（轻量独立表）

```sql
CREATE TABLE warning_record (
  id                    BIGSERIAL PRIMARY KEY,
  time                  TIMESTAMP NOT NULL DEFAULT NOW(),
  type                  VARCHAR(20) NOT NULL,   -- 水位超警 / 流量超警 / 设备异常 / 降雨预警 / 调度通知
  level                 SMALLINT NOT NULL,       -- 1=最高 2=高 3=中 4=低
  content               TEXT NOT NULL,
  target_reservoir_id   INTEGER REFERENCES reservoir(id),
  created_at            TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE announcement (
  id         BIGSERIAL PRIMARY KEY,
  time       TIMESTAMP NOT NULL DEFAULT NOW(),
  content    TEXT NOT NULL
);

CREATE TABLE weather_record (
  id           BIGSERIAL PRIMARY KEY,
  time         TIMESTAMP NOT NULL DEFAULT NOW(),
  city         VARCHAR(20) NOT NULL,
  weather      VARCHAR(20),          -- 晴 / 阴 / 小雨 / 大雨
  temperature  VARCHAR(20),          -- 如 "18~26℃"
  wind         VARCHAR(30),          -- 如 "西北风 2级"
  created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 三、第二层：业务配置（静态模板）

这些是"知识库"表，存储模型/算法/约束的定义，修改这些表不影响历史数据。

```sql
CREATE TABLE dispatch_model (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  description TEXT
);

CREATE TABLE optimization_algorithm (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  description TEXT
);

-- 模型与算法多对多兼容关系
CREATE TABLE model_algorithm_compatibility (
  model_id     INTEGER NOT NULL REFERENCES dispatch_model(id),
  algorithm_id INTEGER NOT NULL REFERENCES optimization_algorithm(id),
  PRIMARY KEY (model_id, algorithm_id)
);

-- 算法参数模板
CREATE TABLE algorithm_parameter (
  id             INTEGER PRIMARY KEY,
  algorithm_id   INTEGER NOT NULL REFERENCES optimization_algorithm(id),
  name           VARCHAR(50) NOT NULL,
  default_value  FLOAT NOT NULL,
  min_value      FLOAT NOT NULL,
  max_value      FLOAT NOT NULL,
  step           FLOAT NOT NULL DEFAULT 1,
  description    TEXT
);

CREATE TABLE dispatch_objective (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(30) NOT NULL,
  description TEXT
);

CREATE TABLE constraint_template (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  description TEXT,
  category    VARCHAR(20),           -- level / flow / power / ecology / sediment
  min_value   FLOAT,
  max_value   FLOAT,
  unit        VARCHAR(10)
);

CREATE TABLE scenario_template (
  id          INTEGER PRIMARY KEY,
  name        VARCHAR(50) NOT NULL,
  category    VARCHAR(20) NOT NULL,  -- multi-year | critical-period | realtime
  description TEXT
);
```

---

## 四、第三层：调度流水线

### 4.1 配置会话

一次完整的 6 步模型配置的聚合结果。

```sql
CREATE TABLE config_session (
  id                BIGSERIAL PRIMARY KEY,
  name              VARCHAR(100) NOT NULL,
  model_id          INTEGER REFERENCES dispatch_model(id),
  algorithm_id      INTEGER REFERENCES optimization_algorithm(id),
  scenario_type     VARCHAR(20),
  start_time        DATE,
  end_time          DATE,
  time_step         VARCHAR(10),
  reservoir_ids     JSONB,                  -- 选择的水库ID列表
  parameters        JSONB NOT NULL DEFAULT '{}',  -- 算法参数值快照
  objectives        JSONB NOT NULL DEFAULT '[]',  -- 调度目标ID列表快照
  constraints       JSONB NOT NULL DEFAULT '{}',  -- 约束参数值快照
  status            VARCHAR(10) NOT NULL DEFAULT 'draft',  -- draft | ready | running
  created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 4.2 模拟任务

```sql
CREATE TABLE simulation_task (
  id                  BIGSERIAL PRIMARY KEY,
  config_session_id   INTEGER NOT NULL REFERENCES config_session(id),
  status              VARCHAR(10) NOT NULL DEFAULT 'pending',  -- pending | running | completed | failed
  progress            SMALLINT DEFAULT 0,        -- 0-100
  elapsed_time        VARCHAR(20),
  estimated_time      VARCHAR(20),
  convergence_data    JSONB,                     -- 收敛曲线 {iterations[], fitness[]}
  objective_trend     JSONB,                     -- 目标趋势
  diversity_data      JSONB,                     -- 种群多样性
  process_logs        JSONB,                     -- 运行日志
  started_at          TIMESTAMP,
  completed_at        TIMESTAMP,
  created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 4.3 模拟结果

```sql
CREATE TABLE simulation_result (
  id            BIGSERIAL PRIMARY KEY,
  task_id       INTEGER NOT NULL REFERENCES simulation_task(id),
  reservoir_id  INTEGER NOT NULL REFERENCES reservoir(id),
  result_type   VARCHAR(20) NOT NULL,            -- water_level | discharge | power_output
  series_data   JSONB NOT NULL,                  -- [{time, optimal, forecast, history}, ...]
  created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 4.4 评价结果

```sql
CREATE TABLE evaluation_result (
  id                     BIGSERIAL PRIMARY KEY,
  task_id                INTEGER NOT NULL REFERENCES simulation_task(id),
  radar_data             JSONB,                  -- 雷达图数据
  sankey_data            JSONB,                  -- 桑基图数据
  pareto_data            JSONB,                  -- 帕累托数据
  ranking_data           JSONB,                  -- 排名数据
  target_satisfaction    JSONB,                  -- 目标满足
  water_usage_flow       JSONB,                  -- 水量流向
  created_at             TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 4.5 案例库

案例是"已完成方案的档案"，用 JSON 快照独立存在，不关联流水线表。

```sql
CREATE TABLE case_record (
  id                 BIGSERIAL PRIMARY KEY,
  title              VARCHAR(200) NOT NULL,
  tag                VARCHAR(20),
  case_type          JSONB NOT NULL DEFAULT '[]',
  reservoirs         JSONB NOT NULL DEFAULT '[]',
  score              FLOAT,
  status             VARCHAR(10) NOT NULL DEFAULT '已验证',  -- 已验证 | 已归档
  config_snapshot    JSONB NOT NULL DEFAULT '{}',     -- 配置摘要快照
  metrics            JSONB NOT NULL DEFAULT '[]',     -- 关键指标
  process_charts     JSONB NOT NULL DEFAULT '{}',     -- 过程图表数据
  evaluation_snapshot JSONB NOT NULL DEFAULT '{}',    -- 评价维度快照
  history_result     JSONB NOT NULL DEFAULT '{}',     -- 历史结果
  task_id            INTEGER REFERENCES simulation_task(id),  -- 可选关联
  creator            VARCHAR(30),
  created_at         TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 五、数据流向总览

```
reservoir ───────────────────────────────────────────────────────┐
  │ 1:N                                                          │
  ├── reservoir_time_series  ← 水位/流量/库容/出力（所有页面）      │
  ├── turbine ── turbine_snapshot  ← 基础数据-工情信息              │
  ├── gate ── gate_snapshot      ← 基础数据-工情信息               │
  ├── warning_record              ← 首页-预警列表                  │
  └── ...                                                         │
                                                                   │
dispatch_model ──┐                                                 │
optimization_algorithm ──┤                                         │
dispatch_objective ──┤                                             │
scenario_template ──┤                                              │
constraint_template ──┼──→ config_session ──→ simulation_task     │
algorithm_parameter ──┘       │                    │              │
                              │                    ├── simulation_result
                              │                    ├── evaluation_result
                              │                    └── case_record
                              │
                              └── reservoir_ids (JSONB) → reservoir
```

**重要规则**：
- `case_record` 不 FK 依赖 `config_session`（会话可能被删，案例应独立留存），只可选 FK 关联 `simulation_task`
- `config_session` 中的 `reservoir_ids` / `parameters` / `objectives` / `constraints` 用 JSONB 快照存储，不拆关联表
- 过程曲线、评价结论用 JSONB 存储（因为它们是计算结果，不需要做聚合查询）

---

## 六、建库后验证清单

建完所有表后，按以下顺序验证：

1. **主数据完整性**
   ```sql
   SELECT COUNT(*) FROM reservoir;   -- 应为 15（或实际水库数）
   ```

2. **外键级联**
   ```sql
   -- 尝试插入一条不存在的 reservoir_id，应报错
   INSERT INTO reservoir_time_series (reservoir_id, time, granularity, water_level)
   VALUES (999, NOW(), 'daily', 100);
   -- 预期：ERROR: foreign key violation
   ```

3. **唯一约束**
   ```sql
   -- 同水库、同时间、同粒度不能重复
   INSERT INTO reservoir_time_series (reservoir_id, time, granularity) VALUES (1, '2025-07-01', 'daily');
   INSERT INTO reservoir_time_series (reservoir_id, time, granularity) VALUES (1, '2025-07-01', 'daily');
   -- 预期：第二条报错
   ```

4. **查询覆盖**
   ```sql
   -- 验证首页水位过程线可查
   SELECT time, water_level FROM reservoir_time_series
   WHERE reservoir_id = 1 AND granularity = 'daily'
   ORDER BY time DESC LIMIT 7;

   -- 验证发电统计可查
   SELECT reservoir_id, SUM(daily_power) FROM reservoir_time_series
   WHERE granularity = 'daily'
   GROUP BY reservoir_id;
   ```

---

## 七、完整建表顺序

按依赖关系从下往上执行（先建被引用表，再建引用表）：

```
 1. reservoir
 2. turbine, gate
 3. reservoir_time_series
 4. turbine_snapshot, gate_snapshot
 5. warning_record, announcement, weather_record
 6. dispatch_model, optimization_algorithm
 7. model_algorithm_compatibility
 8. algorithm_parameter
 9. dispatch_objective, constraint_template, scenario_template
10. config_session
11. simulation_task
12. simulation_result
13. evaluation_result
14. case_record
```

---

> **AI 执行说明**：按以上顺序和 DDL 逐一执行 `CREATE TABLE` 语句即可完成建库。建完后跑第六节的验证 SQL。后续填充 mock 数据时，先填 `reservoir`，再填 `reservoir_time_series`，顺序同上。
