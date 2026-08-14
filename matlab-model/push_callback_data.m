function push_callback_data(data_type, chromosome, pop, V, M, ...
    iteration, current_time, progress_percent, evaluate_func, eval_extra_args)
% push_callback_data - 统一的回调推送封装
% 向 http_callback_push 发送 progress 和 process_data 两种消息
%
% 输入参数:
%   data_type        - 'all' 同时推送两种, 'progress' 仅推送汇总指标
%   chromosome       - 当前种群矩阵 pop x (V+M+2)
%   pop              - 种群大小
%   V                - 决策变量维度
%   M                - 目标函数个数
%   iteration        - 当前代数
%   current_time     - 时间戳字符串
%   progress_percent - 进度百分比
%   evaluate_func    - 函数句柄，如 @evaluate_objective_NSGA2
%   eval_extra_args  - cell 数组，evaluate_func 在 (best_x, V, M) 之后的额外参数

global Y BASE_YEAR

% 汇总指标
obj_values = abs(chromosome(:, (V + 1):(V + M)));

summary_data = struct();
summary_data.iteration = iteration;
summary_data.timestamp = current_time;
summary_data.progress_percent = progress_percent;
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

% 如果需要同时推送过程数据
if strcmp(data_type, 'all')
    best_idx = find_representative_solution(chromosome, pop, V, M);
    best_x = chromosome(best_idx, 1:V);

    % 调用对应的 evaluate 函数获取 results
    % 签名: evaluate_func(x, V, M, eval_extra_args{:})
    [~, results] = evaluate_func(best_x, V, M, eval_extra_args{:});

    n_years = Y;
    year_start = Y - n_years + 1;

    process_data = struct();
    process_data.iteration = iteration;
    process_data.timestamp = current_time;
    process_data.start_year = year_start + BASE_YEAR - 1;

    sidx = (year_start - 1) * 20 + 1;
    eidx = Y * 20;

    long_x = best_x(1:V/2);
    liu_x = best_x(V/2+1:V);
    process_data.longyang_level = long_x(sidx:eidx)';
    process_data.liujia_level = liu_x(sidx:eidx)';

    yr = year_start:Y;
    process_data.longyang_outflow = reshape(results.Long.Qout(yr, :)', 1, []);
    process_data.liujia_outflow = reshape(results.Liu.Qout(yr, :)', 1, []);
    process_data.longyang_power = reshape(results.N.Ntii_long(yr, :)', 1, []);
    process_data.liujia_power = reshape(results.N.Ntii_liu(yr, :)', 1, []);
    process_data.total_power = reshape(results.N.Etii_longliu(yr, :)', 1, []);
    process_data.water_shortage = reshape(results.liuzhou.Qshortage(yr, :)', 1, []);

    % 子系统协调度
    process_data.coordination = struct();
    process_data.coordination.h_water = mean(results.coordination.h_water);
    process_data.coordination.h_ele = mean(results.coordination.h_ele);
    process_data.coordination.h_sed = mean(results.coordination.h_sed);
    process_data.coordination.h_eco = mean(results.coordination.h_eco);

    % 约束满足率
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
