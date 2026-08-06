% 辅助函数：预处理结果结构体，确保数据格式适合JSON
function processed_results = preprocess_results_for_json(results)
    processed_results = results;
    
    % 处理多维数组，确保它们在JSON中正确表示
    fields_to_process = fieldnames(processed_results);
    for i = 1:length(fields_to_process)
        field_name = fields_to_process{i};
        field_value = processed_results.(field_name);
        
        % 递归处理嵌套结构体
        if isstruct(field_value)
            processed_results.(field_name) = preprocess_results_for_json(field_value);
        % 处理特殊数据类型
        elseif isnan(field_value)
            processed_results.(field_name) = 'NaN';
        elseif isinf(field_value)
            if field_value > 0
                processed_results.(field_name) = 'Infinity';
            else
                processed_results.(field_name) = '-Infinity';
            end
        end
    end
end
