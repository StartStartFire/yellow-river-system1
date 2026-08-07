function http_callback_push(data_type, data)
% http_callback_push - 通过 webwrite 实时推送数据到 Web 服务
% 输入参数:
%   data_type - 'progress'
%   data      - MATLAB 结构体
%
% 失败行为：try-catch 静默降级，不影响模型运行。

    persistent callback_url
    if isempty(callback_url)
        callback_url = 'http://127.0.0.1:18080/cb';
    end

    try
        payload = struct();
        payload.type = data_type;
        payload.data = data;

        options = weboptions('MediaType', 'application/json', ...
                             'Timeout', 1, ...
                             'ContentType', 'text');
        webwrite(callback_url, payload, options);
    catch
        % 静默降级：Web 服务未就绪不影响模型
    end
end
