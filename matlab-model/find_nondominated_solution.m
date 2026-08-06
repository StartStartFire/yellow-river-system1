function nondominated = find_nondominated_solution(x, v, m)
nondominated = [];
original = 1: size(x, 1);

while ~isempty(original)
    flag = true;
    i = original(1);
    original_new = original(2: end);
    to_remove = false(size(original_new));
    
    for jj = 1: length(original_new)
        j = original_new(jj);
        dom_less = 0;
        dom_more = 0;
        
        for k = 1: m
            if x(i, v + k) < x(j, v + k)
                dom_less = dom_less + 1;
            elseif x(i, v + k) > x(j, v + k)
                dom_more = dom_more + 1;
            end
        end
        
        if dom_less > 0 && dom_more == 0
            to_remove(jj) = true;
        elseif dom_less == 0 && dom_more > 0
            flag = false;
            break
        end
    end
    
    % 过滤被标记的解
    original_new = original_new(~to_remove);
    % 添加非支配解
    if flag
        nondominated = [nondominated, i];
    end
    original = original_new;
end
end