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
        obj_values = abs(chromosome(:, (V + 1):(V + M)));

        % ===== 汇总指标（progress，走 WebSocket） =====
        summary_data = struct();
        summary_data.iteration = i;
        summary_data.timestamp = current_time;
        summary_data.progress_percent = json_data.progress_percent;
        summary_data.best_objectives = min(obj_values, [], 1);
        summary_data.avg_objectives = mean(obj_values, 1);
        summary_data.objective_std = std(obj_values, 0, 1);
        summary_data.pareto_size = sum(chromosome(:, V+M+1) == 1);
        summary_data.avg_crowding_distance = mean(chromosome(:, V+M+2));

        pareto_mask = (chromosome(:, V+M+1) == 1);
        if any(pareto_mask)
            summary_data.pareto_objectives = obj_values(pareto_mask, :);
        else
            summary_data.pareto_objectives = [];
        end

        http_callback_push('progress', summary_data);

        % ===== 过程数据（process_data，WS + 后端存储） =====
        best_idx = find_representative_solution(chromosome, pop, V, M);
        best_x = chromosome(best_idx, 1:V);

        [~, results] = evaluate_objective_NSGA2(best_x, V, M, Q_sediment);

        n_years = min(10, Y);
        year_start = Y - n_years + 1;

        process_data = struct();
        process_data.iteration = i;
        process_data.timestamp = current_time;
        process_data.start_year = year_start + BASE_YEAR - 1;  % 数据起始年份

        sidx = (year_start - 1) * 20 + 1;
        eidx = Y * 20;

        % 龙羊峡水位（决策变量前 V/2 列）
        long_x = best_x(1:V/2);
        process_data.longyang_level = long_x(sidx:eidx)';

        % 刘家峡水位（决策变量后 V/2 列）
        liu_x = best_x(V/2+1:V);
        process_data.liujia_level = liu_x(sidx:eidx)';

        % 过程数据（用 results 中存储的完整矩阵，取最近 n_years 年）
        yr = year_start:Y;
        process_data.longyang_outflow = reshape(results.Long.Qout(yr, :)', 1, []);
        process_data.liujia_outflow = reshape(results.Liu.Qout(yr, :)', 1, []);
        process_data.longyang_power = reshape(results.N.Ntii_long(yr, :)', 1, []);
        process_data.liujia_power = reshape(results.N.Ntii_liu(yr, :)', 1, []);
        process_data.total_power = reshape(results.N.Etii_longliu(yr, :)', 1, []);
        process_data.water_shortage = reshape(results.liuzhou.Qshortage(yr, :)', 1, []);

        % 子系统协调度（多年平均有序度）
        process_data.coordination = struct();
        process_data.coordination.h_water = mean(results.coordination.h_water);
        process_data.coordination.h_ele = mean(results.coordination.h_ele);
        process_data.coordination.h_sed = mean(results.coordination.h_sed);
        process_data.coordination.h_eco = mean(results.coordination.h_eco);

        % 约束满足率（基于最优个体的全系列统计）
        Qs = results.liuzhou.Qshortage;
        water_guarantee = mean(sum(Qs == 0, 2) / 20);
        eco_guarantee = mean(results.ecology.eco_rate);
        power_ok_long = sum(results.N.Ntii_long(:) >= 58.7 | results.N.Ntii_long(:) < 0.1) / numel(results.N.Ntii_long);
        power_ok_liu = sum(results.N.Ntii_liu(:) >= 40 | results.N.Ntii_liu(:) < 0.1) / numel(results.N.Ntii_liu);
        combined = (water_guarantee + eco_guarantee + power_ok_long + power_ok_liu) / 4;

        process_data.constraint = struct();
        process_data.constraint.water_guarantee = round(water_guarantee * 100, 1);
        process_data.constraint.eco_guarantee = round(eco_guarantee * 100, 1);
        process_data.constraint.power_guarantee = round((power_ok_long + power_ok_liu) / 2 * 100, 1);
        process_data.constraint.combined_rate = round(combined * 100, 1);

        http_callback_push('process_data', process_data);
    end
end


%% 关闭日志文件

% 关闭进化过程的JSON日志文件
fclose(json_fid);


%% ========== 结果输出与比较 ==========

% 对所有个体计算评价指标（22项指标矩阵，用于评价系统）
evaluating_matrix = zeros(pop, 22);
for i = 1:pop
    [~, info] = evaluate_objective_save_info(chromosome(i, 1:V), V, M, Q_sediment);
    evaluating_matrix(i, :) = info.evaluating;
end

% 标量结构体返回值
output = struct();
output.chromosome = chromosome;
output.evaluating = evaluating_matrix;

end