function [log_fid, log_to_file, log_file] = init_log_file(log_file, mode, base_dir)
% init_log_file - 初始化日志文件，返回文件标识符和状态
% 输入参数：
%   log_file - 日志文件路径或文件名（可选，默认为'pso_progress.json'）
%   mode - 文件打开模式（可选，默认为'w'，支持'w'覆盖模式和'a'追加模式）
%   base_dir - 基础目录（可选，默认为空，如提供则在该目录下创建文件）
% 输出参数：
%   log_fid - 文件标识符（1表示标准输出）
%   log_to_file - 是否成功创建文件（true/false）
%   log_file - 实际使用的日志文件路径

% 设置默认参数
if nargin < 1 || isempty(log_file)
    log_file = 'pso_progress.jsonl';
end

if nargin < 2 || isempty(mode)
    mode = 'w';
end

% 处理基础目录
if nargin >= 3 && ~isempty(base_dir)
    % 确保目录存在
    if ~exist(base_dir, 'dir')
        try
            mkdir(base_dir);
            fprintf('创建目录成功: %s\n', base_dir);
        catch ME
            warning('无法创建目录 %s: %s', base_dir, ME.message);
        end
    end
    % 构建完整文件路径
    log_file = fullfile(base_dir, log_file);
end

% 创建日志文件
try
    log_fid = fopen(log_file, mode);
    if log_fid == -1
        warning('无法打开日志文件 %s，将输出到命令窗口', log_file);
        log_to_file = false;
        log_fid = 1; % 使用标准输出
    else
        log_to_file = true;
        %fprintf('日志文件已打开: %s\n', log_file);
    end
catch ME

    fprintf('日志文件操作失败: %s', ME.message);
    log_to_file = false;
    log_fid = 1;
end


end