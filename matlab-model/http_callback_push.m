function http_callback_push(data_type, data)
% http_callback_push - 通过 webwrite 实时推送数据到 Web 服务
% 输入参数:
%   data_type - 'progress'
%   data      - MATLAB 结构体
%
% 通信方式：读取 callback_config.txt 获取推送 URL，
%           通过 webwrite POST JSON 到 Web 服务回调端点。
% 失败行为：try-catch 静默降级，不影响模型运行。

    persistent callback_url
    if isempty(callback_url)
        fid = fopen('callback_config.txt', 'r');
        if fid ~= -1
            callback_url = strtrim(fgets(fid));
            fclose(fid);
        else
            callback_url = 'http://127.0.0.1:18080/cb';
        end
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
