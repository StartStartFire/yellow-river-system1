function chromosome = initialize_population(pop, M, Q_sediment)
% 种群初始化函数
% 初始化种群时，每个个体的决策变量（水库水位）在 VarMin 和 VarMax 之间随机生成。
% 生成后，根据模型约束条件（如汛期水位上升趋势）对决策变量进行修正。
% 最后，调用 evaluate_objective 函数计算每个个体的目标函数值。
% 初始化完成后，对种群进行非支配排序，为后续的遗传操作（选择、交叉、变异）奠定基础。
%
% 输入参数:
%   pop: 种群大小，即初始个体的数量
%   M: 目标函数数量，用于多目标优化问题的目标个数
%   Q_sediment: 入库输沙量数据，用于计算水库泥沙淤积相关目标
%
% 输出参数:
%   chromosome: 初始化、评估并排序后的种群矩阵
%               矩阵大小为 pop × (V + M + 2)，每行代表一个个体
%               前V列为决策变量（水库水位），中间M列为目标函数值
%               倒数第二列为非支配排序等级，最后一列为拥挤距离

% 声明全局变量
% Y: 优化时段的总年数（本系统中为54年）
% VarMin: 决策变量（水库水位）的下限向量
% VarMax: 决策变量（水库水位）的上限向量
global Y VarMin VarMax

% 计算决策变量数量2160
V = 20 * Y * 2;

%% 初始化种群矩阵
% 预分配 chromosome 矩阵，大小为 pop × (V + M)
% 前V列存储决策变量（各水库各时段的水位），后M列存储目标函数值
chromosome = zeros(pop, V + M);
VarSize = [1 V];  % 单个决策变量向量的维度，用于生成随机数

%% 对种群中的每个个体进行初始化
for i = 1 : pop
    % 在水库水位的上下界内随机生成决策变量值
    % unifrnd 在 [VarMin, VarMax] 范围内生成均匀分布的随机数
    % 为第i个个体的V个决策变量（各水库各时段水位）赋初值
    chromosome(i, 1:V) = unifrnd(VarMin, VarMax, VarSize);
    
    % 对随机生成的水位进行约束处理（汛期应蓄水）
    % 水库汛期（每年前7个时段）水位应呈上升趋势，以满足防洪和蓄水要求
    for j = 0 : Y-1  % 遍历每一年（共Y年）
        for m = 1 : 7  % 汛期时段（每年第1-7个时段，每月2个时段）
            % 龙羊峡水库每年的汛期水位应呈上升趋势
            %前20*Y列为龙羊峡水库数据，后20*Y列为刘家峡水库数据
            % 检查第j年第m时段的水位是否大于第m+1时段
            % 若不满足上升趋势，则将后一时段水位调整为前一时刻加随机增量
            if chromosome(i, 20*j + m) > chromosome(i, 20*j + m + 1)
                chromosome(i, 20*j + m + 1) = chromosome(i, 20*j + m) + unifrnd(0, 2, 1);
            end
            
            % 刘家峡水库每年的汛期水位应呈上升趋势
            % 前20*Y列为龙羊峡水库数据，后20*Y列为刘家峡水库数据
            % 索引偏移：龙羊峡时段索引 + 20*Y 得到刘家峡对应时段索引
            if chromosome(i, 20*j + m + 20*Y) > chromosome(i, 20*Y + 20*j + m + 1)
                chromosome(i, 20*Y + 20*j + m + 1) = chromosome(i, 20*Y + 20*j + m) + unifrnd(0, 2, 1);
            end
        end
    end
    
    % 评估目标函数，它包含了完整的初始种群，每一行代表一个个体，包含决策变量和计算出的目标函数值。
    % 预分配 chromosome_all 矩阵，避免每次循环动态扩展
    if i == 1
        % 第一次迭代时初始化 chromosome_all
        chromosome_all = zeros(pop, V + M);
    end
    % 对第i个个体进行目标函数评估，结果存入 chromosome_all 第i行
    chromosome_all(i, :) = evaluate_objective(chromosome(i, :), V, M, Q_sediment);
end

% 将评估后的完整种群赋值给 chromosome
% 此时 chromosome 包含所有个体的决策变量和目标函数值
chromosome = chromosome_all;

%% 初始种群的非支配排序
% 进行初始种群的非支配排序，返回两个值：非支配排序等级、拥挤距离。
% 并将这两个值添加到染色体中。
chromosome = non_domination_sort_mod(chromosome, M, V, pop);

end