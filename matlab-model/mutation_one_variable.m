function child = mutation_one_variable(parent, mum, l_limit, u_limit)
% Perform mutation on eact element of the selected parent.
r = rand(1);
if r < 0.5
    delta = (2*r)^(1/(mum+1)) - 1;
else
    delta = 1 - (2*(1 - r))^(1/(mum+1));
end
% Generate the corresponding child element.
child = parent + delta * (u_limit - l_limit);     
% Make sure that the generated element is within the decision space.
child = min(max(child, l_limit), u_limit);
end