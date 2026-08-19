function output = nsga_2_para(pop, iterate, M, Q_sediment, Pc)
% NSGA-II参数优化主函数
% 输入参数:
%   pop: 种群大小
%   iterate: 进化代数
%   M: 目标函数数量
%   Q_sediment: 调沙流量
%   Pc: 交叉概率（0~1），用于 genetic_operator

% 输出参数:
%   output: 包含优化结果的结构体，包括chromosome_acc字段

%% 初始化日志文件
% 使用init_log_file函数，指定文件路径、写入模式和目录

% 初始化进化进度的JSON日志文件
log_dir = '';  % 使用当前目录，也可以设置为'json_logs'保持一致
[json_fid, log_to_file, ~] = init_log_file('NSGA2_progress.jsonl','w', log_dir);


%% ========== 参数设置 ==========
% 声明全局变量
global Y VarMin VarMax
global BASE_YEAR

% 设置算法参数
nVar = 20 * Y * 2;  % 决策变量数量：20个时段 * 2个水库（龙羊峡和刘家峡）
V = nVar;           % 决策变量数量别名
min_range = VarMin;  % 决策变量下限
max_range = VarMax;  % 决策变量上限

%% ========== 种群初始化 ==========

% 初始化种群
chromosome = initialize_population(pop, M ,Q_sediment);

%% ========== 进化过程 ==========

% 从初始种群中，选择适当个体，作为父代种群，并进行复制、交叉、变异
for i = 1 : iterate
    %% ========== 父代种群选择 ==========
    % 二进制锦标赛法选择父代
    % 选择标准：非支配等级（先）和拥挤距离（后）的比较→随机选择两个个体进行比较
    pool = fix(pop / 2);                     % 交配池大小，通常取初始种群规模的一半
    tour = 2;                                % 锦标赛规模，取值任意
    parent_chromosome = tournament_selection(chromosome, pool, tour);
    % 二进制锦标赛法选择标准：非支配等级低（先）+拥挤距离大（后）→优选目标

    %% ========== 遗传操作 ==========
    % 遗传操作参数设置
    mu = 20;                                 % 模拟二进制交叉算子(SBX)分配系数
    mum = 20;                                % 多项式变异算子(PM)分配系数
    
    % 生成子代种群
    offspring_chromosome = genetic_operator(parent_chromosome, M, V, mu, mum, min_range, max_range, Pc);

    %% ========== 子代种群评价 ==========
    % 子代种群评价
    offspring_all = [];
    for j = 1: size(offspring_chromosome, 1)
        offspring_all = [offspring_all; evaluate_objective_NSGA2(offspring_chromosome(j, 1: V) , V, M, Q_sediment)];
    end
    offspring_chromosome = offspring_all;
    
    %% ========== 种群合并与选择 ==========
    % 创建媒介种群：当前进化代数下的，初始种群和子代种群的直接组合，不增删任何个体
    [main_pop, ~] = size(chromosome);
    [offspring_pop, ~] = size(offspring_chromosome);
    intermediate_chromosome(1:main_pop, 1:M+V) = chromosome(1:main_pop, 1:M+V);
    intermediate_chromosome(main_pop + 1 : main_pop + offspring_pop, 1:M+V) = offspring_chromosome;

    % 媒介种群的非支配排序
    intermediate_chromosome = non_domination_sort_mod(intermediate_chromosome, M, V, pop);

    % 从媒介种群中选择新种群
    % 选择标准：非支配等级小（先）+拥挤距离（大）→优选目标
    chromosome = replace_chromosome(intermediate_chromosome, M, V, pop);

    %% ========== 进度显示与日志记录 ==========
    % 显示进度（每 5 代）
    if ~mod(i, 5)
        clc
        fprintf('Running completed %d / %d \n', i, iterate);
    end

    % 记录日志（每代写入 JSONL，保持完整记录）
    current_time = datestr(now, 'yyyy-mm-dd HH:MM:SS');
    json_data = struct();
    json_data.iteration = i;
    json_data.timestamp = current_time;
    json_data.objective_values = abs(chromosome(:, (V + 1): (V + M)));
    json_data.progress_percent = round((double(i) / double(iterate)) * 100, 2);
    write_json_log(json_data, json_fid);

    % 每 10 代推送一次汇总指标 + 过程数据
    if ~mod(i, 10) || i == iterate
        push_callback_data('all', chromosome, pop, V, M, ...
            i, current_time, json_data.progress_percent, ...
            @evaluate_objective_NSGA2, {Q_sediment});
    end
end


%% 关闭日志文件

% 关闭进化过程的JSON日志文件
fclose(json_fid);


%% ========== 结果输出与比较 ==========

% 对所有个体计算评价指标（22项指标矩阵，用于评价系统）
% 同时保存每个个体的决策分析明细（过程曲线/目标满足度/水量分配）
% 注意：MATLAB Engine 只能返回标量结构体，故 plan_details 打包为标量结构体（字段为 pop×n 矩阵）
evaluating_matrix = zeros(pop, 22);
objectives_mat = zeros(pop, M);
level_long_mat = zeros(pop, V/2);
level_liu_mat = zeros(pop, V/2);
qout_long_mat = zeros(pop, V/2);
qout_liu_mat = zeros(pop, V/2);
power_long_mat = zeros(pop, V/2);
power_liu_mat = zeros(pop, V/2);
targets_mat = zeros(pop, 6);
water_usage_mat = zeros(pop, 6);
coordination_mat = zeros(pop, 4);
for i = 1:pop
    [~, info] = evaluate_objective_save_info(chromosome(i, 1:V), V, M, Q_sediment);
    evaluating_matrix(i, :) = info.evaluating;
    objectives_mat(i, :) = reshape(info.objectives, 1, []);
    level_long_mat(i, :) = reshape(info.individual(1:V/2), 1, []);
    level_liu_mat(i, :) = reshape(info.individual(V/2+1:V), 1, []);
    qout_long_mat(i, :) = reshape(info.Long.Qout', 1, []);
    qout_liu_mat(i, :) = reshape(info.Liu.Qout', 1, []);
    power_long_mat(i, :) = reshape(info.N.Ntii_long', 1, []);
    power_liu_mat(i, :) = reshape(info.N.Ntii_liu', 1, []);
    targets_mat(i, :) = [info.targets.power, info.targets.ecology, info.targets.irrigation, ...
        info.targets.domestic, info.targets.spill, info.targets.sediment];
    water_usage_mat(i, :) = [info.water_usage.power, info.water_usage.ecology, info.water_usage.irrigation, ...
        info.water_usage.domestic, info.water_usage.spill, info.water_usage.sediment];
    coordination_mat(i, :) = [info.coordination.h_water, info.coordination.h_ele, ...
        info.coordination.h_sed, info.coordination.h_eco];
end

% 决策分析明细（标量结构体，字段为矩阵，兼容 MATLAB Engine 返回值转换）
plan_details = struct();
plan_details.index = (1:pop)';
plan_details.objectives = objectives_mat;
plan_details.level_long = level_long_mat;
plan_details.level_liu = level_liu_mat;
plan_details.qout_long = qout_long_mat;
plan_details.qout_liu = qout_liu_mat;
plan_details.power_long = power_long_mat;
plan_details.power_liu = power_liu_mat;
% targets/water_usage 列顺序: [power, ecology, irrigation, domestic, spill, sediment]
plan_details.targets = targets_mat;
plan_details.water_usage = water_usage_mat;
% coordination 列顺序: [h_water, h_ele, h_sed, h_eco]
plan_details.coordination = coordination_mat;

% 标量结构体返回值
output = struct();
output.chromosome = chromosome;
output.evaluating = evaluating_matrix;
output.plan_details = plan_details;

end