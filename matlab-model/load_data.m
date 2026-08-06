function load_data(path_load, flag_xixian)
% 数据加载函数
% 输入参数:
%   path_load: 数据文件路径
%   flag_xixian: 是否考虑西上线、西下线调水 ('全无', '全有', '有上无下', '有下无上')

% 声明全局变量
global LONG_ZQ LONG_ZV LIU_ZQ LIU_ZV LAN_agr LAN_unagr
global Q_eco P canshu LONG_IN LONGLIU_BOUND LONG_LIU LIU_LAN LAN LONGLIU_MIN LONGLIU_MAX Y VarMin VarMax
global YEAR_START YEAR_END BASE_YEAR

%% 基础数据加载
LONG_ZQ = xlsread(path_load, 'LONG-ZQ');%龙羊峡水位和流量
LONG_ZV = xlsread(path_load, 'LONG-ZV');%龙羊峡水位和库容
LIU_ZQ = xlsread(path_load, 'LIU-ZQ');%刘家峡水位和流量
LIU_ZV = xlsread(path_load, 'LIU-ZV');%刘家峡水位和库容

canshu = xlsread(path_load, 'CANSHU');%各个水库群的物理参数

%{
fprintf('各水库参数:\n');
fprintf('  龙羊峡装机容量: %.1f 万kW\n', canshu(1,2));
fprintf('  龙羊峡保证出力: %.1f 万kW\n', canshu(1,1));
fprintf('  刘家峡装机容量: %.1f 万kW\n', canshu(9,2));
fprintf('  刘家峡保证出力: %.1f 万kW\n', canshu(9,1));
%}

% 5,6,7,8月分为上中下旬，其余月份以月为时段，故共一年有20个时段
LONG_IN = xlsread(path_load, 'LONGIN', 'G2:Z55');%龙羊峡水库入流
LONG_LIU = xlsread(path_load, 'LONG-LIU', 'F2:Y55');%龙刘水库区间来水
LIU_LAN = xlsread(path_load, 'LIU-LAN', 'F2:Y55');%刘兰区间来水

% 计算年数
Y = size(LONG_IN, 1); %54年


%% 来水用水数据处理
% 区间用水流量
longliu_water = xlsread(path_load, 'longliu_water', 'B2:U55');%龙刘水库区间用水
liulan_water = xlsread(path_load, 'liulan_water', 'B2:U55');%刘兰区间用水

% 区间来水流量
LONG_LIU = LONG_LIU - longliu_water;
LIU_LAN = LIU_LAN - liulan_water;

% 西上线、西下线调水流量
xixian_up = xlsread(path_load, 'xixian_up', 'B2:U55');%西上线调水流量
xixian_down = xlsread(path_load, 'xixian_down', 'B2:U55');%西下线调水流量

% 根据flag_xixian参数调整来水流量
if isequal(flag_xixian, '全有')
    LONG_IN = LONG_IN + xixian_up;
    LONG_LIU = LONG_LIU + xixian_down;
elseif isequal(flag_xixian, '有上无下')
    LONG_IN = LONG_IN + xixian_up;
elseif isequal(flag_xixian, '有下无上')
    LONG_LIU = LONG_LIU + xixian_down;
end

%% 其他数据加载
LAN = xlsread(path_load, 'LAN', 'F2:Y55');%兰州断面总需水
LAN_unagr = xlsread(path_load, 'LAN-unagr', 'F2:Y55');%兰州断面非农业需水
LAN_agr = xlsread(path_load, 'LAN-agr', 'F2:Y55');%兰州断面农业需水
Q_eco = xlsread(path_load, 'Q_eco', 'F2:Y55');%兰州断面生态需水

% 注意，当计算年数改变时，P的取值也需要改变
P = xlsread(path_load, 'P', 'K2:K55');%来水频率

%% 年份范围截取（可选，由 Web 服务通过全局变量 YEAR_START/YEAR_END 控制）
% 不设置年份范围时使用 Excel 全部年份，保持原有行为
if ~isempty(YEAR_START) && ~isempty(YEAR_END)
    % 行索引：Excel 第 1 行数据对应 1970 年，第 N 行对应 (1969+N) 年
    row_start = YEAR_START - 1969;
    row_end   = YEAR_END - 1969;

    fprintf('截取年份范围: %d ~ %d (数据行 %d ~ %d)\n', YEAR_START, YEAR_END, row_start, row_end);

    % 截取所有年相关矩阵（统一为 row_start:row_end 行范围）
    LONG_IN  = LONG_IN(row_start:row_end, :);
    LONG_LIU = LONG_LIU(row_start:row_end, :);
    LIU_LAN  = LIU_LAN(row_start:row_end, :);
    LAN      = LAN(row_start:row_end, :);
    LAN_unagr = LAN_unagr(row_start:row_end, :);
    LAN_agr  = LAN_agr(row_start:row_end, :);
    Q_eco    = Q_eco(row_start:row_end, :);
    P        = P(row_start:row_end, :);

    % 更新年数（后续 VarMin/VarMax、目标函数循环均依赖 Y）
    Y = size(LONG_IN, 1);
    fprintf('截取后年数 Y = %d\n', Y);

    % 记录实际数据起始年份（供 nsga_2_para/PAEM_para 计算图表横坐标标签）
    BASE_YEAR = YEAR_START;
else
    % 未截取年份范围：Excel 数据固定从 1970 年开始
    BASE_YEAR = 1970;
end

LONGLIU_BOUND = xlsread(path_load, 'LONGLIU-BOUND', 'B2:C41');
LONGLIU_MIN = LONGLIU_BOUND(:, 1);  % 龙刘各月水位下限
LONGLIU_MAX = LONGLIU_BOUND(:, 2);  % 龙刘各月水位上限

%% 决策变量边界设置
% 龙羊峡水库水位边界
temp1 = LONGLIU_MIN(1:20);  % 取龙羊峡水库的各月水位下限
temp1 = repmat(temp1, Y, 1); % 复制成Y个年份为一列的长系列水位下限过程 20*54=1080

temp2 = LONGLIU_MAX(1:20);  % 取龙羊峡水库的各月水位上限
temp2 = repmat(temp2, Y, 1);% 复制成Y个年份为一列的长系列水位上限过程 20*54=1080

%{
% 显示temp1的格式信息
fprintf('temp1变量格式信息:\n');
fprintf('  维度: %d x %d\n', size(temp1, 1), size(temp1, 2));
fprintf('  数据类型: %s\n', class(temp1));
fprintf('  前5行内容示例:\n');
for i = 1:min(5, size(temp1, 1))
    fprintf('    第%d行: %.2f\n', i, temp1(i, 1));
end
%}


% 刘家峡水库水位边界
temp3 = LONGLIU_MIN(21:40); % 取刘家峡水库的各月水位下限
temp3 = repmat(temp3, Y, 1);

temp4 = LONGLIU_MAX(21:40); % 取刘家峡水库的各月水位上限
temp4 = repmat(temp4, Y, 1);

% 设置决策变量上下界
VarMin = [temp1; temp3]'; % Lower Bound of Variables 行向量,1080*2=2160
VarMax = [temp2; temp4]'; % Upper Bound of Variables

%{
% 显示决策变量信息
fprintf('决策变量信息:\n');
fprintf('  变量维度: %d\n', size(VarMin));
fprintf('  龙羊峡水位范围: [%.1f, %.1f] m\n', min(temp1), max(temp2));
fprintf('  刘家峡水位范围: [%.1f, %.1f] m\n', min(temp3), max(temp4));
%}
% 显示变量维度信息
%fprintf('VarMin维度: %s\n', mat2str(size(VarMin)));
%fprintf('VarMax维度: %s\n', mat2str(size(VarMax)));
fprintf('数据加载成功!\n')
end