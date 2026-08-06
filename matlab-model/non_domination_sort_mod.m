
function f = non_domination_sort_mod(x, M, V,pop)
%对当前种群进行非支配排序，对全体个体，先进行非支配等级排序，再进行拥挤距离排序。
[N,~] = size(x);                                                           %N为种群总的个体数目。
x(:,V+M+1) = zeros(N,1);
present_pop = 0;
front = 1;                                                                 % Initialize the front number to 1.
F(front).f = [];
individual(1:N) = struct('n',[],'p',[]);
%% 非支配排序
% 初始化的种群基于非支配关系进行排序。快速排序算法 [1] 的描述如下：

% 对于主种群 P 中的每个个体 p，执行以下操作：
%   初始化 Sp = []。这个集合将包含所有被 p 支配的个体。
%   初始化 np = 0。这个值表示支配 p 的个体数量。
%   对于 P 中的每个个体 q：
%       * 如果 p 支配 q，则
%           将 q 添加到集合 Sp 中，即 Sp = Sp∪{q}
%       * 否则如果 q 支配 p，则
%           增加 p 的支配计数器，即 np = np + 1
%   如果 np = 0，即没有个体支配 p，则 p 属于第一前沿；将个体 p 的排名设为1，即 prank = 1。
%   通过将 p 添加到第一前沿来更新第一前沿集合，即 F1 = F1∪{p}
% 对主种群 P 中的所有个体执行此操作。
% 初始化前沿计数器为1。i = 1
% 当第 i 个前沿非空时执行以下操作，即 Fi≠[]：
%   Q = []。用于存储第 (i + 1) 个前沿个体的集合。
%   对于前沿 Fi 中的每个个体 p：
%       * 对于 Sp 中的每个个体 q（Sp 是被 p 支配的个体集合）：
%           nq = nq-1，减少个体 q 的支配计数。
%           如果 nq = 0，则后续前沿中的任何个体都不会支配 q。因此，将 qrank 设置为 i + 1。
%           使用个体 q 更新集合 Q，即 Q = Q∪{q}。
%   将前沿计数器增加1。
%   现在集合 Q 是下一个前沿，因此 Fi = Q。
%
% 该算法优于原始的 NSGA ([2])，因为它利用了个体支配的集合（Sp）和
% 支配该个体的个体数量（np）的信息。


for i = 1 : N
    % Number of individuals that dominate this individual
    individual(i).n = 0;
    % Individuals which this individual dominate
    individual(i).p = [];
    for j = 1 : N
        dom_less = 0;
        dom_equal = 0;
        dom_more = 0;
        for k = 1 : M
            if x(i,V+k) < x(j,V+k)
                dom_less = dom_less + 1;
            elseif x(i,V + k) == x(j,V + k)
                dom_equal = dom_equal + 1;
            else
                dom_more = dom_more + 1;
            end
        end
        if dom_less == 0 && dom_equal ~= M
            individual(i).n = individual(i).n + 1;
        elseif dom_more == 0 && dom_equal ~= M
            individual(i).p = [individual(i).p j];
        end
    end
    if individual(i).n == 0
        x(i,M + V + 1) = 1;
        F(front).f = [F(front).f i];
    end
end
% Find the subsequent fronts
while ~isempty(F(front).f)
    
    present_pop = present_pop+length(F(front).f);
    if present_pop >= pop
        x(x(:,V+M+1)==0,:) = [];
        break
    end
    
    Q = zeros(1,N);
    m = 1;
    for i = 1 : length(F(front).f)
        if ~isempty(individual(F(front).f(i)).p)
            for j = 1 : length(individual(F(front).f(i)).p)
                individual(individual(F(front).f(i)).p(j)).n = ...
                    individual(individual(F(front).f(i)).p(j)).n - 1;
                if individual(individual(F(front).f(i)).p(j)).n == 0
                    x(individual(F(front).f(i)).p(j),M + V + 1) = front + 1;
                    Q(m) = individual(F(front).f(i)).p(j);
                    m = m + 1;
                end
            end
        end
    end
    front =  front + 1;
    Q(Q==0) = [];
    F(front).f = Q;
end

%% Crowding distance
%The crowing distance is calculated as below
% For each front Fi, n is the number of individuals.
%   initialize the distance to be zero for all the individuals i.e. Fi(dj ) = 0,
%     where j corresponds to the jth individual in front Fi.
%   for each objective function m
%       * Sort the individuals in front Fi based on objective m i.e. I =
%         sort(Fi,m).
%       * Assign infinite distance to boundary values for each individual
%         in Fi i.e. I(d1) = ∞ and I(dn) = ∞
%       * for k = 2 to (n - 1)
%           I(dk) = I(dk) + (I(k + 1).m - I(k - 1).m)/fmax(m) - fmin(m)
%           I(k).m is the value of the mth objective function of the kth
%             individual in I

% Find the crowding distance for each individual in each front
[~,I] = sort(x(:,M + V + 1));
sorted_based_on_front = x(I,:);
current_index = 0;

for front = 1 : length(F)
    previous_index = current_index + 1;
    y = sorted_based_on_front( (current_index + 1):(current_index + length(F(front).f)),: );
    current_index = current_index + length(F(front).f);
    % Sort each individual based on the objective
    if length(F(front).f) < 3
        y(:,M + V + 2) = Inf;
        z(previous_index:current_index,:) = y(:,1 : M + V + 2);
    else
        for i = 1 : M
            [~, index_of_objectives] = sort(y(:,V + i));
            sorted_based_on_objective = y(index_of_objectives,:);
            f_max = sorted_based_on_objective(length(index_of_objectives), V + i);
            f_min = sorted_based_on_objective(1, V + i);
            y(index_of_objectives(length(index_of_objectives)),M + V + 1 + i) = Inf;
            y(index_of_objectives(1),M + V + 1 + i) = Inf;
            for j = 2 : (length(index_of_objectives) - 1)
                next_obj  = sorted_based_on_objective(j + 1,V + i);
                previous_obj  = sorted_based_on_objective(j - 1,V + i);
                if f_max - f_min == 0
                    y(index_of_objectives(j),M + V + 1 + i) = Inf;
                else
                    y(index_of_objectives(j),M + V + 1 + i) = ...
                        (next_obj - previous_obj)/(f_max - f_min);
                end
            end
        end
        distance = zeros(length(F(front).f),1);
        for i = 1 : M
            distance = distance + y( :,(M+V+1+i) );
        end
        y( :,(M+V+2) ) = distance;
        z(previous_index:current_index,:) = y( :,1 : (M+V+2) );
    end
end
f = z;

end
