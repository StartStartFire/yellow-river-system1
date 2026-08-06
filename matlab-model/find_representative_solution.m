function best_idx = find_representative_solution(chromosome, pop, V, M)
% find_representative_solution - 从种群中选出代表性最优解
% 输入参数:
%   chromosome - 种群矩阵（pop × (V+M+2)），最后两列为 rank 和拥挤距离
%   pop        - 种群大小
%   V          - 决策变量维度
%   M          - 目标函数数量
% 输出参数:
%   best_idx   - 代表性个体的行索引
%
% 选出策略：Pareto 前沿（rank==1）中发电量最大的个体
% （发电量 f2 为负值，最小值对应最大发电量）

    rank_col = V + M + 1;

    % 找出 Pareto 前沿上的个体（rank==1）
    pareto_mask = (chromosome(:, rank_col) == 1);
    pareto_indices = find(pareto_mask);

    if isempty(pareto_indices)
        % 极端情况：没有 rank=1 的个体，选 f2 最小的（发电量最大）
        [~, best_idx] = min(chromosome(:, V + 2));
        return;
    end

    % 在 Pareto 前沿个体中选发电量最大的（f2 值最小）
    f2_values = chromosome(pareto_indices, V + 2);
    [~, min_f2_idx] = min(f2_values);
    best_idx = pareto_indices(min_f2_idx);
end
