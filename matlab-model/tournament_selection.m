function f = tournament_selection(chromosome, pool_size, tour_size)
% 锦标赛选择函数
% 从种群中选择父代个体，用于遗传算法的交配池构建
% 输入参数:
%   chromosome: 种群矩阵，包含决策变量和目标函数值
%   pool_size: 需要选择的父代个体数量
%   tour_size: 锦标赛大小（每次比较的个体数量）
% 输出参数:
%   f: 选中的父代个体组成的交配池

[pop, element] = size(chromosome);
rank = element - 1;     % 倒数第二列：非支配等级
distance = element;     % 最后一列：拥挤距离

index_pop = 1:pop;
f = zeros(pool_size, element);

for i = 1:pool_size
    % 从剩余索引池中随机选 tour_size 个候选
    candidate = zeros(tour_size, 1);
    for j = 1:tour_size
        if isempty(index_pop)
            index_pop = 1:pop;
            index_pop = setdiff(index_pop, candidate(1:j-1));
        end
        r = randi(length(index_pop));
        candidate(j) = index_pop(r);
        index_pop(r) = [];
    end

    % 比较候选个体的非支配等级和拥挤距离
    c_rank = chromosome(candidate, rank);
    c_dist = chromosome(candidate, distance);

    % 选等级最小的个体；等级相同时选拥挤距离最大的
    [~, best] = min(c_rank);
    ties = find(c_rank == c_rank(best));
    if length(ties) > 1
        [~, idx] = max(c_dist(ties));
        best = ties(idx);
    end

    f(i, :) = chromosome(candidate(best), :);
end

end