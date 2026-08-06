function f = tournament_selection(chromosome, pool_size, tour_size)
% 锦标赛选择函数
% 从种群中选择父代个体，用于遗传算法的交配池构建
% 输入参数:
%   chromosome: 种群矩阵，包含决策变量和目标函数值
%   pool_size: 需要选择的父代个体数量
%   tour_size: 锦标赛大小（每次比较的个体数量）
% 输出参数:
%   f: 选中的父代个体组成的交配池

%% 输入验证和初始化
[pop, element] = size(chromosome);
if isempty(chromosome)
    error('tournament_selection: 输入种群为空（pop==0）。');
end

% 确定非支配等级和拥挤距离在染色体中的位置
% 倒数第二列是非支配等级信息
rank = element - 1;
% 最后一列是拥挤距离信息
distance = element;

% 初始化候选个体索引池
index_pop = 1:pop;  % 使用冒号运算符代替循环，更简洁高效

% 初始化输出矩阵
f = zeros(pool_size, element);

%% 执行锦标赛选择
for i = 1:pool_size
    % 重置候选个体数组
    candidate = zeros(tour_size, 1);
    
    % 随机选择候选个体
    for j = 1:tour_size
        % 检查是否还有可选的个体
        if isempty(index_pop)
            % 如果索引池为空，重新初始化并排除已选中的候选个体
            index_pop = 1:pop;
            index_pop = setdiff(index_pop, candidate(1:j-1));  % 使用setdiff更高效
            
            % 检查重新初始化后是否仍有足够个体
            if isempty(index_pop)
                error('没有足够的个体可供选择。种群规模: %d, 已选个体数: %d', pop, j-1);
            end
        end
        
        % 随机选择一个候选个体
        r = randi(length(index_pop));  % 使用randi代替复杂的随机数生成
        candidate(j) = index_pop(r);
        index_pop(r) = [];  % 从候选池中移除已选个体
    end
    
    % 验证候选个体的有效性（可选，因为已通过索引池确保有效性）
    if any(candidate < 1 | candidate > pop)
        error('候选个体索引无效。');
    end
    
    % 收集候选个体的非支配等级和拥挤距离信息
    c_obj_rank = chromosome(candidate, rank);
    c_obj_distance = chromosome(candidate, distance);
    
    % 找出非支配等级最低的候选个体
    min_rank = min(c_obj_rank);
    min_candidate = find(c_obj_rank == min_rank);
    
    % 安全检查：确保min_candidate不为空
    if isempty(min_candidate)
        % 如果为空，选择第一个候选个体
        selected_idx = candidate(1);
    else
        % 如果有多个个体具有相同的最低等级，选择拥挤距离最大的个体
        if length(min_candidate) > 1
            % 计算min_candidate对应的拥挤距离
            valid_min_candidate = min_candidate;
            valid_distances = c_obj_distance(valid_min_candidate);
            
            % 安全检查：确保valid_distances不为空
            if isempty(valid_distances)
                % 如果没有有效距离，选择第一个min_candidate
                selected_idx = candidate(min_candidate(1));
            else
                max_distance = max(valid_distances);
                max_candidate = find(valid_distances == max_distance);
                
                % 安全检查：确保max_candidate不为空
                if isempty(max_candidate)
                    % 如果为空，选择第一个min_candidate
                    selected_idx = candidate(min_candidate(1));
                else
                    % 如果仍有多个个体，选择第一个
                    if length(max_candidate) > 1
                        max_candidate = max_candidate(1);
                    end
                    
                    % 获取最终的个体索引
                    selected_idx = candidate(min_candidate(max_candidate));
                end
            end
        else
            % 只有一个最优等级的个体
            selected_idx = candidate(min_candidate(1));
        end
    end
    
    % 安全检查：确保selected_idx有效
    if isempty(selected_idx) || selected_idx < 1 || selected_idx > size(chromosome, 1)
        % 如果无效，选择第一个候选个体
        selected_idx = candidate(1);
    end
    
    % 将选中的个体添加到交配池
    f(i, :) = chromosome(selected_idx, :);

end