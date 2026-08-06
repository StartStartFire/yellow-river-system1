function write_json_log(log_data, log_fid, preprocess_data)
% write_json_log - 以 JSON Lines (NDJSON) 格式写入日志
%
% 每次写入一行独立的 JSON 对象，适合 Python 后端实时流式读取。
%
% 输入参数：
%   log_data         - 包含日志数据的结构体
%   log_fid          - 文件标识符（例如 fopen 返回值，1 表示标准输出）
%   preprocess_data  - 是否预处理数据（可选，默认 true）
%
% 输出参数：
%   无
%
% 说明：
%   1. 输出格式为 JSON Lines：每行一个 JSON 对象
%   2. 不使用 JSON 数组包裹，不需要 close_json_log
%   3. 适合 Python 使用 readline() 持续读取
%
% 示例：
%   log_fid = fopen('log.jsonl', 'a');
%   write_json_log(data1, log_fid);
%   write_json_log(data2, log_fid);
%   fclose(log_fid);

    % 默认参数
    if nargin < 3 || isempty(preprocess_data)
        preprocess_data = true;
    end

    % 基本校验
    if nargin < 2
        error('write_json_log:NotEnoughInputs', ...
            '至少需要提供 log_data 和 log_fid 两个参数。');
    end

    if ~isstruct(log_data)
        error('write_json_log:InvalidInputType', ...
            'log_data 必须是结构体。');
    end

    if ~isscalar(log_fid) || log_fid < 1
        error('write_json_log:InvalidFileId', ...
            'log_fid 必须是有效的文件标识符。');
    end

    % 复制，避免修改原始数据
    processed_data = log_data;


    % 预处理
    if preprocess_data
        processed_data = preprocess_results_for_json(processed_data);
    end

    % 编码并写入
    try
        json_str = jsonencode(processed_data);

        % JSON Lines: 一条记录一行
        fprintf(log_fid, '%s\n', json_str);

    catch ME
        % 错误信息尽量输出到标准错误/命令行
        warning('write_json_log:EncodeOrWriteFailed', ...
            'JSON 日志写入失败: %s', ME.message);
        if log_fid == 1
            fprintf('原始数据:\n');
            disp(log_data);
        end
    end
end