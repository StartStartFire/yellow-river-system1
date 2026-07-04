# 黄河上游水库群调度系统 - PostgreSQL 数据库结构设计

> 版本：V1.0 | 数据库：PostgreSQL 14+ | 基于：黄河流域数据底板数据集V1.1

---

## 目录

1. [数据库与Schema创建](#一数据库与schema创建)
2. [水利工程数据表（eng Schema）](#二水利工程数据表eng-schema)
3. [监测数据表（mon Schema）](#三监测数据表mon-schema)
4. [业务数据表（biz Schema）](#四业务数据表biz-schema)
5. [系统辅助表（sys Schema）](#五系统辅助表sys-schema)
6. [初始化SQL脚本](#六初始化sql脚本)
7. [视图定义](#七视图定义)

---

## 一、数据库与Schema创建

```sql
-- 创建数据库
CREATE DATABASE yellow_river_system
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'zh_CN.UTF-8'
    LC_CTYPE = 'zh_CN.UTF-8'
    TEMPLATE = template0;

-- 连接数据库
\c yellow_river_system;

-- 创建Schema
CREATE SCHEMA IF NOT EXISTS eng;      -- 水利工程（水库、水利枢纽、特征水位、调度规则、关键曲线、机组、闸门）
CREATE SCHEMA IF NOT EXISTS mon;      -- 监测数据（水文站、气象站、实时监控、过程数据、逐月流量、逐日监测）
CREATE SCHEMA IF NOT EXISTS biz;      -- 业务数据（发电统计、模型算法、任务、过程、评价、案例、报表）
CREATE SCHEMA IF NOT EXISTS sys;      -- 系统数据（预警、天气、通知、用户）

-- 启用PostGIS扩展
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

## 二、水利工程数据表（eng Schema）

### 2.1 eng.reservoir_group（水库分组表）

```sql
CREATE TABLE eng.reservoir_group (
    id              SERIAL PRIMARY KEY,
    group_name      VARCHAR(50) NOT NULL,
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### 2.2 eng.hydro_junction（水利枢纽表 - 核心表）

```sql
CREATE TABLE eng.hydro_junction (
    id                  SERIAL PRIMARY KEY,
    dam_id              INTEGER UNIQUE NOT NULL,
    dam_name            VARCHAR(100) NOT NULL,
    dam_type            VARCHAR(30),
    normal_lev          DOUBLE PRECISION,
    total_sto           DOUBLE PRECISION,
    design_sto          DOUBLE PRECISION,
    reg_sto             DOUBLE PRECISION,
    flood_sto           DOUBLE PRECISION,
    installed_capacity  DOUBLE PRECISION,
    unit_count          INTEGER,
    crest_elevation     DOUBLE PRECISION,
    crest_length        DOUBLE PRECISION,
    max_height          DOUBLE PRECISION,
    annual_design_power DOUBLE PRECISION,
    avg_runoff          DOUBLE PRECISION,
    flood_standard      INTEGER,
    reservoir_type      VARCHAR(20),
    dra_system          VARCHAR(100),
    location            VARCHAR(200),
    status              VARCHAR(20) DEFAULT 'normal',
    group_name          VARCHAR(50),
    sort_order          INTEGER DEFAULT 0,
    latitude            DOUBLE PRECISION,
    longitude           DOUBLE PRECISION,
    geom                GEOMETRY(POINT, 4326),
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hj_dam_id ON eng.hydro_junction(dam_id);
CREATE INDEX idx_hj_group ON eng.hydro_junction(group_name, sort_order);
CREATE INDEX idx_hj_geom ON eng.hydro_junction USING GIST(geom);
```

### 2.3 eng.characteristic_level（特征水位表）

```sql
CREATE TABLE eng.characteristic_level (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    level_type      VARCHAR(30) NOT NULL,
    level_value     DOUBLE PRECISION NOT NULL,
    color           VARCHAR(10),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(dam_id, level_type)
);
```

### 2.4 eng.dispatch_rule（调度规则表）

```sql
CREATE TABLE eng.dispatch_rule (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    rule_type       VARCHAR(20) NOT NULL,
    rule_content    TEXT NOT NULL,
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(dam_id, rule_type)
);
```

### 2.5 eng.storage_curve（库容曲线表）

```sql
CREATE TABLE eng.storage_curve (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    water_level     DOUBLE PRECISION NOT NULL,
    storage         DOUBLE PRECISION NOT NULL
);
CREATE INDEX idx_sc_dam ON eng.storage_curve(dam_id);
```

### 2.6 eng.turbine_curve（机组出力曲线表）

```sql
CREATE TABLE eng.turbine_curve (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    water_head      DOUBLE PRECISION NOT NULL,
    power_output    DOUBLE PRECISION NOT NULL
);
CREATE INDEX idx_tc_dam ON eng.turbine_curve(dam_id);
```

### 2.7 eng.gate_curve（泄洪闸过流曲线表）

```sql
CREATE TABLE eng.gate_curve (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    opening         DOUBLE PRECISION NOT NULL,
    flow            DOUBLE PRECISION NOT NULL
);
CREATE INDEX idx_gc_dam ON eng.gate_curve(dam_id);
```

### 2.8 eng.turbine（机组信息表）

```sql
CREATE TABLE eng.turbine (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    unit_name       VARCHAR(20) NOT NULL,
    unit_status     VARCHAR(20) DEFAULT 'stop',
    output          DOUBLE PRECISION DEFAULT 0,
    flow            DOUBLE PRECISION DEFAULT 0,
    gate_open       DOUBLE PRECISION DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

### 2.9 eng.gate（闸门信息表）

```sql
CREATE TABLE eng.gate (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    gate_name       VARCHAR(20) NOT NULL,
    open_percentage DOUBLE PRECISION DEFAULT 0,
    discharge_flow  DOUBLE PRECISION DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 三、监测数据表（mon Schema）

### 3.1 mon.hydro_station（水文站数据表）

```sql
CREATE TABLE mon.hydro_station (
    id              SERIAL PRIMARY KEY,
    station_id      INTEGER UNIQUE NOT NULL,
    sta_code        INTEGER,
    sta_name        VARCHAR(100) NOT NULL,
    sta_class       VARCHAR(50),
    river_name      VARCHAR(100),
    location        VARCHAR(200),
    basin           VARCHAR(50),
    control_area    DOUBLE PRECISION,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    geom            GEOMETRY(POINT, 4326),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### 3.2 mon.realtime_monitoring（实时监控数据表）

```sql
CREATE TABLE mon.realtime_monitoring (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    record_time     TIMESTAMP NOT NULL,
    water_level     DOUBLE PRECISION,
    inflow          DOUBLE PRECISION,
    outflow         DOUBLE PRECISION,
    storage         DOUBLE PRECISION,
    power_output    DOUBLE PRECISION,
    change_level    DOUBLE PRECISION,
    change_inflow   DOUBLE PRECISION,
    change_outflow  DOUBLE PRECISION,
    change_storage  DOUBLE PRECISION,
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_rm_dam_time ON mon.realtime_monitoring(dam_id, record_time);
```

### 3.3 mon.process_data（水情过程数据表）

```sql
CREATE TABLE mon.process_data (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    record_date     DATE NOT NULL,
    record_time     TIME,
    water_level     DOUBLE PRECISION,
    inflow          DOUBLE PRECISION,
    outflow         DOUBLE PRECISION,
    power_output    DOUBLE PRECISION,
    data_type       VARCHAR(20) DEFAULT 'actual',
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_pd_dam_date ON mon.process_data(dam_id, record_date);
COMMENT ON COLUMN mon.process_data.data_type IS 'actual/target/forecast/history_dispatch/future_dispatch';
```

### 3.4 mon.monthly_flow（逐月平均流量表）

```sql
CREATE TABLE mon.monthly_flow (
    id              SERIAL PRIMARY KEY,
    station_id      INTEGER NOT NULL REFERENCES mon.hydro_station(id),
    year            INTEGER NOT NULL,
    month_1 DOUBLE PRECISION, month_2 DOUBLE PRECISION, month_3 DOUBLE PRECISION,
    month_4 DOUBLE PRECISION, month_5 DOUBLE PRECISION, month_6 DOUBLE PRECISION,
    month_7 DOUBLE PRECISION, month_8 DOUBLE PRECISION, month_9 DOUBLE PRECISION,
    month_10 DOUBLE PRECISION, month_11 DOUBLE PRECISION, month_12 DOUBLE PRECISION,
    annual_average  DOUBLE PRECISION,
    UNIQUE(station_id, year)
);
```

### 3.5 mon.daily_monitoring（逐日监测表）

```sql
CREATE TABLE mon.daily_monitoring (
    id              SERIAL PRIMARY KEY,
    station_id      INTEGER NOT NULL REFERENCES mon.hydro_station(id),
    record_date     DATE NOT NULL,
    water_level     DOUBLE PRECISION,
    flow            DOUBLE PRECISION,
    UNIQUE(station_id, record_date)
);
```

---

## 四、业务数据表（biz Schema）

### 4.1 biz.power_statistics（发电统计表）

```sql
CREATE TABLE biz.power_statistics (
    id              SERIAL PRIMARY KEY,
    dam_id          INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    record_date     DATE NOT NULL,
    daily_power     DOUBLE PRECISION,
    monthly_power   DOUBLE PRECISION,
    yearly_power    DOUBLE PRECISION,
    UNIQUE(dam_id, record_date)
);
```

### 4.2 biz.dispatch_model（调度模型表）

```sql
CREATE TABLE biz.dispatch_model (
    id              SERIAL PRIMARY KEY,
    model_name      VARCHAR(50) NOT NULL,
    model_code      VARCHAR(20) UNIQUE,
    description     TEXT,
    version         VARCHAR(20),
    is_active       BOOLEAN DEFAULT TRUE
);
```

### 4.3 biz.optimization_algorithm（优化算法表）

```sql
CREATE TABLE biz.optimization_algorithm (
    id              SERIAL PRIMARY KEY,
    algo_name       VARCHAR(50) NOT NULL,
    algo_code       VARCHAR(20) UNIQUE,
    description     TEXT,
    default_params  JSONB,
    is_active       BOOLEAN DEFAULT TRUE
);
```

### 4.4 biz.dispatch_scenario（调度场景表）

```sql
CREATE TABLE biz.dispatch_scenario (
    id              SERIAL PRIMARY KEY,
    scenario_name   VARCHAR(50) NOT NULL,
    category        VARCHAR(20) NOT NULL,
    description     TEXT,
    default_model_id INTEGER REFERENCES biz.dispatch_model(id)
);
```

### 4.5 biz.task（任务表）

```sql
CREATE TABLE biz.task (
    id                  SERIAL PRIMARY KEY,
    task_name           VARCHAR(200) NOT NULL,
    task_code           VARCHAR(50) UNIQUE,
    scenario_id         INTEGER REFERENCES biz.dispatch_scenario(id),
    status              VARCHAR(20) DEFAULT 'pending',
    start_date          DATE,
    end_date            DATE,
    time_step           VARCHAR(20),
    model_id            INTEGER REFERENCES biz.dispatch_model(id),
    algorithm_id        INTEGER REFERENCES biz.optimization_algorithm(id),
    reservoir_ids       TEXT,
    schedule_targets    TEXT,
    progress            DECIMAL(5,2) DEFAULT 0,
    run_duration        INTEGER DEFAULT 0,
    current_iteration   INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT NOW(),
    started_at          TIMESTAMP,
    completed_at        TIMESTAMP
);
CREATE INDEX idx_task_status ON biz.task(status, created_at);
```

### 4.6 biz.task_algorithm_param（任务算法参数表）

```sql
CREATE TABLE biz.task_algorithm_param (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    param_name      VARCHAR(50) NOT NULL,
    param_value     DOUBLE PRECISION,
    param_min       DOUBLE PRECISION,
    param_max       DOUBLE PRECISION,
    param_desc      VARCHAR(200)
);
```

### 4.7 biz.task_constraint（任务约束表）

```sql
CREATE TABLE biz.task_constraint (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    constraint_type VARCHAR(30) NOT NULL,
    constraint_name VARCHAR(100) NOT NULL,
    min_value       DOUBLE PRECISION,
    max_value       DOUBLE PRECISION,
    unit            VARCHAR(20),
    is_enabled      BOOLEAN DEFAULT TRUE,
    fulfill_status  VARCHAR(20)
);
```

### 4.8 biz.process_log（过程日志表）

```sql
CREATE TABLE biz.process_log (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    log_time        TIMESTAMP NOT NULL,
    log_level       VARCHAR(10) DEFAULT 'INFO',
    iteration       INTEGER,
    message         TEXT,
    current_value   DOUBLE PRECISION
);
CREATE INDEX idx_log_task_time ON biz.process_log(task_id, log_time);
```

### 4.9 biz.process_convergence（收敛曲线表）

```sql
CREATE TABLE biz.process_convergence (
    id                  SERIAL PRIMARY KEY,
    task_id             INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    plan_id             VARCHAR(50) NOT NULL,
    iteration           INTEGER NOT NULL,
    fitness             DOUBLE PRECISION,
    total_objective     DOUBLE PRECISION,
    flood_objective     DOUBLE PRECISION,
    power_objective     DOUBLE PRECISION,
    ecology_objective   DOUBLE PRECISION,
    diversity           DOUBLE PRECISION
);
CREATE INDEX idx_conv_task ON biz.process_convergence(task_id, plan_id, iteration);
```

### 4.10 biz.task_result（任务结果表）

```sql
CREATE TABLE biz.task_result (
    id                      SERIAL PRIMARY KEY,
    task_id                 INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    plan_id                 VARCHAR(50) NOT NULL,
    plan_name               VARCHAR(100),
    total_power             DOUBLE PRECISION,
    avg_discharge           DOUBLE PRECISION,
    min_discharge           DOUBLE PRECISION,
    flood_peak_reduction    DOUBLE PRECISION,
    sediment_discharge      DOUBLE PRECISION,
    ecology_rate            DOUBLE PRECISION,
    composite_score         DOUBLE PRECISION,
    created_at              TIMESTAMP DEFAULT NOW(),
    UNIQUE(task_id, plan_id)
);
```

### 4.11 biz.plan（方案表）

```sql
CREATE TABLE biz.plan (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER REFERENCES biz.task(id) ON DELETE SET NULL,
    plan_name       VARCHAR(100) NOT NULL,
    plan_code       VARCHAR(50) UNIQUE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### 4.12 biz.decision_target（决策目标表）

```sql
CREATE TABLE biz.decision_target (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    plan_id         INTEGER NOT NULL REFERENCES biz.plan(id) ON DELETE CASCADE,
    target_name     VARCHAR(100) NOT NULL,
    status          VARCHAR(20),
    rate            DOUBLE PRECISION,
    actual_value    DOUBLE PRECISION,
    target_value    DOUBLE PRECISION
);
```

### 4.13 biz.water_usage（水量使用表）

```sql
CREATE TABLE biz.water_usage (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES biz.task(id) ON DELETE CASCADE,
    plan_id         INTEGER NOT NULL REFERENCES biz.plan(id) ON DELETE CASCADE,
    usage_type      VARCHAR(50) NOT NULL,
    usage_value     DOUBLE PRECISION,
    usage_percent   DOUBLE PRECISION
);
```

### 4.14 biz.dispatch_case（案例库主表）

```sql
CREATE TABLE biz.dispatch_case (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    tag             VARCHAR(20),
    tag_color       VARCHAR(10),
    case_type       VARCHAR(100),
    reservoirs      VARCHAR(200),
    summary         TEXT,
    status          VARCHAR(20) DEFAULT '已验证',
    score           DECIMAL(5,2),
    score_level     VARCHAR(10),
    creator         VARCHAR(50),
    icon_type       VARCHAR(20),
    is_favorited    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

### 4.15 biz.case_config / case_metric / case_evaluation

```sql
CREATE TABLE biz.case_config (
    id              SERIAL PRIMARY KEY,
    case_id         INTEGER NOT NULL REFERENCES biz.dispatch_case(id) ON DELETE CASCADE,
    config_type     VARCHAR(20) NOT NULL,
    config_key      VARCHAR(100) NOT NULL,
    config_value    TEXT,
    sort_order      INTEGER DEFAULT 0
);

CREATE TABLE biz.case_metric (
    id              SERIAL PRIMARY KEY,
    case_id         INTEGER NOT NULL REFERENCES biz.dispatch_case(id) ON DELETE CASCADE,
    metric_name     VARCHAR(100) NOT NULL,
    metric_value    VARCHAR(50),
    change_text     VARCHAR(50),
    change_type     VARCHAR(20),
    baseline        VARCHAR(20)
);

CREATE TABLE biz.case_evaluation (
    id              SERIAL PRIMARY KEY,
    case_id         INTEGER NOT NULL REFERENCES biz.dispatch_case(id) ON DELETE CASCADE,
    dimension_name  VARCHAR(50) NOT NULL,
    score           DECIMAL(5,2),
    weight          DECIMAL(5,4)
);
```

### 4.16 biz 报表统计表

```sql
CREATE TABLE biz.monthly_operation (
    id                      SERIAL PRIMARY KEY,
    dam_id                  INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    year                    INTEGER NOT NULL,
    month                   INTEGER NOT NULL,
    initial_level           DOUBLE PRECISION, final_level DOUBLE PRECISION,
    max_level DOUBLE PRECISION, min_level DOUBLE PRECISION,
    initial_storage DOUBLE PRECISION, final_storage DOUBLE PRECISION,
    max_storage DOUBLE PRECISION, min_storage DOUBLE PRECISION,
    inflow_month DOUBLE PRECISION, inflow_year DOUBLE PRECISION,
    total_outflow_month DOUBLE PRECISION, total_outflow_year DOUBLE PRECISION,
    power_release_month DOUBLE PRECISION, power_release_year DOUBLE PRECISION,
    eco_release_month DOUBLE PRECISION, eco_release_year DOUBLE PRECISION,
    abandoned_month DOUBLE PRECISION, abandoned_year DOUBLE PRECISION,
    UNIQUE(dam_id, year, month)
);

CREATE TABLE biz.monthly_economic (
    id SERIAL PRIMARY KEY,
    dam_id INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    year INTEGER NOT NULL, month INTEGER NOT NULL,
    installed_total DOUBLE PRECISION, installed_in_service DOUBLE PRECISION, installed_new DOUBLE PRECISION,
    annual_design_power DOUBLE PRECISION, avg_runoff DOUBLE PRECISION, current_year_runoff DOUBLE PRECISION,
    water_use_month DOUBLE PRECISION, water_use_year DOUBLE PRECISION,
    utilization_rate_month DOUBLE PRECISION, utilization_rate_year DOUBLE PRECISION,
    water_supply_month DOUBLE PRECISION, water_supply_year DOUBLE PRECISION,
    flood_storage_design DOUBLE PRECISION, flood_storage_current DOUBLE PRECISION,
    flood_standard INTEGER,
    UNIQUE(dam_id, year, month)
);

CREATE TABLE biz.monthly_power (
    id SERIAL PRIMARY KEY,
    dam_id INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    year INTEGER NOT NULL, month INTEGER NOT NULL,
    power_month DOUBLE PRECISION, power_year DOUBLE PRECISION,
    plan_completion_rate DOUBLE PRECISION,
    water_consumption_month DOUBLE PRECISION, water_consumption_year DOUBLE PRECISION,
    water_consumption_assess DOUBLE PRECISION, assessment_result VARCHAR(10),
    grid_power_month DOUBLE PRECISION, grid_power_year DOUBLE PRECISION,
    utilization_hours_month INTEGER, utilization_hours_year INTEGER,
    remark VARCHAR(100),
    UNIQUE(dam_id, year, month)
);

CREATE TABLE biz.yearly_summary (
    id SERIAL PRIMARY KEY,
    dam_id INTEGER NOT NULL REFERENCES eng.hydro_junction(dam_id),
    year INTEGER NOT NULL,
    initial_year_level DOUBLE PRECISION, final_year_level DOUBLE PRECISION,
    average_year_level DOUBLE PRECISION, max_year_level DOUBLE PRECISION, min_year_level DOUBLE PRECISION,
    total_year_inflow DOUBLE PRECISION, total_year_outflow DOUBLE PRECISION,
    year_power_water DOUBLE PRECISION, year_abandoned_water DOUBLE PRECISION, year_water_supply DOUBLE PRECISION,
    year_power DOUBLE PRECISION, year_avg_consumption DOUBLE PRECISION,
    year_avg_output DOUBLE PRECISION, year_utilization_hours INTEGER,
    assessment_result VARCHAR(10),
    UNIQUE(dam_id, year)
);
```

---

## 五、系统辅助表（sys Schema）

```sql
CREATE TABLE sys.warning (
    id              SERIAL PRIMARY KEY,
    warning_time    TIMESTAMP NOT NULL,
    source          VARCHAR(50),
    level           INTEGER,
    level_name      VARCHAR(10),
    content         TEXT,
    dam_id          INTEGER REFERENCES eng.hydro_junction(dam_id),
    is_resolved     BOOLEAN DEFAULT FALSE
);

CREATE TABLE sys.weather_info (
    id              SERIAL PRIMARY KEY,
    city            VARCHAR(50),
    record_date     DATE,
    weather         VARCHAR(20),
    temp_low        DECIMAL(4,1),
    temp_high       DECIMAL(4,1),
    wind_direction  VARCHAR(10),
    wind_level      INTEGER
);

CREATE TABLE sys.announcement (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    content         TEXT,
    publisher       VARCHAR(50),
    publish_time    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sys.user_info (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    real_name       VARCHAR(50),
    role            VARCHAR(20) DEFAULT 'viewer',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 六、初始化SQL脚本

```sql
-- ===== 1. 水库分组 =====
INSERT INTO eng.reservoir_group (group_name, sort_order) VALUES
    ('龙羊峡以上', 1), ('龙羊峡 — 刘家峡', 2), ('刘家峡以下', 3);

-- ===== 2. 13座水利枢纽 =====
INSERT INTO eng.hydro_junction (dam_id, dam_name, dam_type, normal_lev, total_sto, installed_capacity, unit_count, 
    crest_elevation, crest_length, max_height, annual_design_power, avg_runoff, flood_standard, 
    reservoir_type, dra_system, location, group_name, sort_order, latitude, longitude) VALUES
(1,  '羊曲水库',   '混凝土面板堆石坝', 2702, 36.80, 220,  3, 2720, 280, 150, 12.50, 52,   1000, '年调节水库', '黄河上游', '青海省兴海县', '龙羊峡以上', 1, 35.50, 100.10),
(2,  '班多水库',   '混凝土重力坝',     2622, 34.80, 180,  3, 2640, 180, 120, 9.80,  45,   1000, '年调节水库', '黄河上游', '青海省兴海县', '龙羊峡以上', 2, 35.35, 100.30),
(3,  '茨哈峡水库', '混凝土拱坝',       2562, 33.80, 150,  2, 2580, 160, 110, 8.50,  40,   500,  '年调节水库', '黄河上游', '青海省兴海县', '龙羊峡以上', 3, 35.20, 100.50),
(4,  '玛尔挡水库', '混凝土面板堆石坝', 3282, 32.20, 160,  2, 3300, 220, 210, 9.20,  38,   500,  '年调节水库', '黄河上游', '青海省玛沁县', '龙羊峡以上', 4, 34.50, 100.30),
(5,  '龙羊峡水库', '混凝土重力坝',     2480, 416.80, 1280, 4, 2510, 393, 178, 57.66, 151,  10000,'多年调节水库','黄河上游','青海省共和县','龙羊峡 — 刘家峡',5,36.12,100.90),
(6,  '公伯峡水库', '混凝土双曲拱坝',   1988, 34.50, 750,  5, 2002, 260, 155, 28.50, 85,   1000, '年调节水库', '黄河上游', '青海省化隆县', '龙羊峡 — 刘家峡',6,36.10,102.20),
(7,  '积石峡水库', '混凝土重力坝',     1858, 30.50, 1020, 3, 1868, 210, 138, 32.80, 98,   1000, '年调节水库', '黄河上游', '青海省循化县', '龙羊峡 — 刘家峡',7,35.80,102.60),
(8,  '刘家峡水库', '混凝土双曲拱坝',   1738, 88.60, 1225, 6, 1754, 240, 147, 50.61, 263,  1000, '多年调节水库','黄河上游','甘肃省永靖县','龙羊峡 — 刘家峡',8,35.90,103.30),
(9,  '小峡水库',   '混凝土闸坝',       1498, 0.52,  230,  4, 1510, 250, 45,  10.20, 285,  100,  '日调节水库', '黄河上游', '甘肃省兰州市', '刘家峡以下', 9, 36.10, 103.80),
(10, '大峡水库',   '混凝土闸坝',       1468, 0.49,  210,  4, 1480, 220, 42,  9.50,  280,  100,  '日调节水库', '黄河上游', '甘肃省兰州市', '刘家峡以下', 10, 36.20, 104.00),
(11, '乌金峡水库', '混凝土闸坝',       1438, 0.42,  140,  4, 1450, 200, 38,  6.80,  265,  100,  '日调节水库', '黄河上游', '甘肃省白银市', '刘家峡以下', 11, 36.50, 104.30),
(12, '青铜峡水库', '碾压混凝土重力坝', 1157, 0.65,  272,  8, 1162, 365, 52,  11.06, 315,  100,  '日调节水库', '黄河上游', '宁夏青铜峡市', '刘家峡以下', 12, 37.90, 105.90),
(13, '黑山峡水库', '混凝土重力坝',     1368, 0.36,  120,  2, 1380, 180, 55,  5.50,  245,  500,  '年调节水库', '黄河上游', '甘肃省白银市', '刘家峡以下', 13, 37.00, 104.50);

-- ===== 3. 特征水位 =====
INSERT INTO eng.characteristic_level (dam_id, level_type, level_value, color) VALUES
(5,'check_flood',2505.0,'#C084FC'),(5,'design_flood',2497.0,'#F97316'),(5,'normal',2480.0,'#38BDF8'),(5,'flood_limit',2470.0,'#EAB308'),(5,'dead',2410.0,'#94A3B8'),
(8,'check_flood',1750.0,'#C084FC'),(8,'design_flood',1742.0,'#F97316'),(8,'normal',1738.0,'#38BDF8'),(8,'flood_limit',1735.0,'#EAB308'),(8,'dead',1685.0,'#94A3B8');

-- ===== 4. 调度模型和算法 =====
INSERT INTO biz.dispatch_model (model_name, model_code, description, version) VALUES
    ('水库群优化调度模型', 'LRO', '联动水库优化调度模型', 'v2.3.1'),
    ('多目标优化调度模型', 'MOOP', '多目标优化调度模型', 'v2.2.0'),
    ('实时洪水调度模型', 'RTFD', '实时洪水调度模型', 'v3.0.1');

INSERT INTO biz.optimization_algorithm (algo_name, algo_code, default_params) VALUES
    ('NSGA-II', 'NSGA2', '{"populationSize":200,"iterationCount":500,"crossoverRate":0.9,"mutationRate":0.1}'),
    ('PSO', 'PSO', '{"populationSize":300,"iterationCount":800}'),
    ('NSGA-III', 'NSGA3', '{"populationSize":200,"iterationCount":800}');

-- ===== 5. 水文站 =====
INSERT INTO mon.hydro_station (station_id, sta_code, sta_name, sta_class, river_name, location, basin, control_area, latitude, longitude) VALUES
    (1, 40101100, '唐乃亥站', '国家基本站', '黄河干流', '青海省兴海县唐乃亥乡', '黄河上游', 121972, 35.50, 100.15),
    (2, 40102200, '贵德站',   '国家基本站', '黄河干流', '青海省贵德县',       '黄河上游', 135688, 36.04, 101.43),
    (3, 40103400, '兰州站',   '国家基本站', '黄河干流', '甘肃省兰州市',       '黄河上游', 222551, 36.06, 103.82),
    (4, 40104600, '青铜峡站', '国家基本站', '黄河干流', '宁夏青铜峡市',       '黄河上游', 275010, 37.89, 105.93),
    (5, 40105800, '石嘴山站', '国家基本站', '黄河干流', '宁夏石嘴山市',       '黄河上游', 306388, 39.23, 106.77);
```

---

## 七、视图定义

```sql
-- 水库综合信息视图
CREATE VIEW biz.v_reservoir_full AS
SELECT hj.dam_id, hj.dam_name, hj.dam_type, hj.normal_lev, hj.total_sto,
    hj.installed_capacity, hj.unit_count, hj.crest_elevation, hj.max_height,
    hj.reservoir_type, hj.group_name, hj.sort_order, hj.status,
    hj.latitude, hj.longitude, rm.water_level, rm.inflow, rm.outflow, rm.storage, rm.power_output
FROM eng.hydro_junction hj
LEFT JOIN mon.realtime_monitoring rm ON hj.dam_id = rm.dam_id;

-- 水文站月均流量视图
CREATE VIEW mon.v_monthly_flow AS
SELECT hs.sta_name, hs.river_name, hs.control_area,
    mf.year, mf.month_1,mf.month_2,mf.month_3,mf.month_4,mf.month_5,mf.month_6,
    mf.month_7,mf.month_8,mf.month_9,mf.month_10,mf.month_11,mf.month_12,mf.annual_average
FROM mon.monthly_flow mf JOIN mon.hydro_station hs ON mf.station_id = hs.id;
```

---

## 表清单汇总

| Schema | 表名 | 说明 |
|:---|:---|:---|
| eng | reservoir_group | 水库分组（3组） |
| eng | hydro_junction | 水利枢纽（13座核心表） |
| eng | characteristic_level | 特征水位 |
| eng | dispatch_rule | 调度规则 |
| eng | storage_curve | 库容曲线 |
| eng | turbine_curve | 机组出力曲线 |
| eng | gate_curve | 泄洪闸过流曲线 |
| eng | turbine | 机组信息 |
| eng | gate | 闸门信息 |
| mon | hydro_station | 水文站（5站） |
| mon | realtime_monitoring | 实时监控 |
| mon | process_data | 水情过程数据 |
| mon | monthly_flow | 逐月平均流量 |
| mon | daily_monitoring | 逐日监测 |
| biz | power_statistics | 发电统计 |
| biz | dispatch_model | 调度模型 |
| biz | optimization_algorithm | 优化算法 |
| biz | dispatch_scenario | 调度场景 |
| biz | task | 计算任务 |
| biz | task_algorithm_param | 算法参数 |
| biz | task_constraint | 任务约束 |
| biz | process_log | 过程日志 |
| biz | process_convergence | 收敛曲线 |
| biz | task_result | 任务结果 |
| biz | plan | 方案 |
| biz | decision_target | 决策目标 |
| biz | water_usage | 水量使用 |
| biz | dispatch_case | 案例库 |
| biz | case_config | 案例配置 |
| biz | case_metric | 案例指标 |
| biz | case_evaluation | 案例评价 |
| biz | monthly_operation | 逐月运行报表 |
| biz | monthly_economic | 逐月经济报表 |
| biz | monthly_power | 逐月发电报表 |
| biz | yearly_summary | 年度汇总报表 |
| sys | warning | 预警信息 |
| sys | weather_info | 天气信息 |
| sys | announcement | 通知公告 |
| sys | user_info | 系统用户 |

**总计：4个Schema，39张数据表，2个视图**
