function f = genetic_operator(parent_chromosome, M, V, mu, mum, l_limit, u_limit, Pc)


[N,~] = size(parent_chromosome);
p = 1;
% Flags used to set if crossover and mutation were actually performed. 
% was_crossover = 1 or was_mutation = 1;
child_chromosome = zeros(2*N,V+M);
for i = 1 : N
    if rand(1) < Pc
        % With 90% probability perform crossover
        % Select the first parent
        parent_1 = round(N*rand(1));
        if parent_1 == 0
            parent_1 = 1;
        end
        % Select the second parent
        parent_2 = round(N*rand(1));
        if parent_2 == 0
            parent_2 = 1;
        end
        % Make sure both the parents are not the same.
        %while isequal(parent_chromosome(parent_1,:),parent_chromosome(parent_2,:))
        while parent_1 == parent_2    
            parent_2 = round(N*rand(1));
            if parent_2 == 0
                parent_2 = 1;
            end
        end
        % Get the chromosome information for each randomly selected
        % parents
        parent_1 = parent_chromosome(parent_1,1:V);
        parent_2 = parent_chromosome(parent_2,1:V);
        % Perform corssover for each decision variable in the chromosome.
        child_1 = zeros(1,V+M);   
        child_2 = zeros(1,V+M);
        u = zeros(1,V);
        bq = zeros(1,V);          
        for j = 1 : V
            % SBX (Simulated Binary Crossover).
            % For more information about SBX refer the enclosed pdf file.
            % Generate a random number
            u(j) = rand(1);
            if u(j) <= 0.5
                bq(j) = (2*u(j))^(1/(mu+1));
            else
                bq(j) = (1/(2*(1 - u(j))))^(1/(mu+1));
            end
            % Generate the jth element of first child
            child_1(j) = 0.5*( ((1 + bq(j))*parent_1(j)) + (1 - bq(j))*parent_2(j) );
            % Generate the jth element of second child
            child_2(j) = 0.5*( ((1 - bq(j))*parent_1(j)) + (1 + bq(j))*parent_2(j) );
            % Make sure that the generated element is within the specified
            % decision space else set it to the appropriate extrema.
            if child_1(j) > u_limit(j)
                child_1(j) = u_limit(j);
            elseif child_1(j) < l_limit(j)
                child_1(j) = l_limit(j);
            end
            if child_2(j) > u_limit(j)
                child_2(j) = u_limit(j);
            elseif child_2(j) < l_limit(j)
                child_2(j) = l_limit(j);
            end
        end

        was_crossover = 1;
        was_mutation = 0;
    else
    
        parent_3 = round(N*rand(1));
        if parent_3 == 0
            parent_3 = 1;
        end
        % Get the chromosome information for the randomly selected parent.
        parent_3 = parent_chromosome(parent_3,1:V);
        % Perform mutation on eact element of the selected parent.
        
        child_3 = zeros(1,V + M);   
        r = zeros(1,V);
        delta = zeros(1,V);        
        for j = 1 : V
            r(j) = rand(1);
            if r(j) < 0.5
                delta(j) = (2*r(j))^(1/(mum+1)) - 1;
            else
                delta(j) = 1 - (2*(1 - r(j)))^(1/(mum+1));
            end
            % Generate the corresponding child element.
            child_3(j) = parent_3(j) + delta(j) * (u_limit(j) - l_limit(j));     
            % Make sure that the generated element is within the decision
            % space.
            if child_3(j) > u_limit(j)
                child_3(j) = u_limit(j);
            elseif child_3(j) < l_limit(j)
                child_3(j) = l_limit(j);
            end
        end
       
        was_mutation = 1;
        was_crossover = 0;
    end
    
    if was_crossover
        child_chromosome(p,:) = child_1;
        child_chromosome(p+1,:) = child_2;
        p = p + 2;
    elseif was_mutation
        child_chromosome(p,:) = child_3;
        p = p + 1;
    end
end
index = sum(abs(child_chromosome'))==0;
child_chromosome(index,:) = [];
f = child_chromosome;

end