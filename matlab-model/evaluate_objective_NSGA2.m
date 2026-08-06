function [X_F, results] = evaluate_objective_NSGA2(x, V, M, Q_sediment)
% NSGA2算法目标函数评估：计算梯级水库联合调度的多目标函数值
% 输入参数:
%   x - 决策变量向量，包含龙羊峡和刘家峡的水位过程
%   V - 决策变量维度
%   M - 目标函数数量(2或3)
%   Q_sediment - 调沙流量
% 输出参数:
%   X_F - 包含决策变量和目标函数值的向量

% 声明全局变量：水库特性曲线、需水数据、生态流量等
global LONG_ZQ LONG_ZV LIU_ZQ LIU_ZV LAN_unagr
global Q_eco P LONG_IN LONG_LIU LIU_LAN LAN Y VarMax

% 约束参数（由 Web 服务通过全局变量注入）
global LONG_Z_INI_VAL LIU_Z_INI_VAL QMIN_VAL


% ========== 初始化参数 ==========
% 龙羊峡和刘家峡起调水位初始化
LONG_Z_INI = zeros(Y, 1);
LIU_Z_INI = zeros(Y, 1);
if ~isempty(LONG_Z_INI_VAL)
    LONG_Z_INI(1) = LONG_Z_INI_VAL;
else
    LONG_Z_INI(1) = 2580;  % 默认龙羊峡起调水位2580m
end
if ~isempty(LIU_Z_INI_VAL)
    LIU_Z_INI(1) = LIU_Z_INI_VAL;
else
    LIU_Z_INI(1) = 1720;   % 默认刘家峡起调水位1720m
end

% 调沙和防凌标记初始化
m=0;  % 当前年份标记
k=0;  % 调沙年数累计

% 防凌流量约束(11月、12月、1月、2月、3月)
if ~isempty(QMIN_VAL) && length(QMIN_VAL) == 5
    Qmin = QMIN_VAL;
else
    Qmin = [610,420,420,420,420];   

% 时段转换系数：0.0087552为旬，0.0262656为月 (m?/s与亿m?转换)
xishu=[0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,...
       0.0087552,0.0262656,0.0262656,0.0262656,0.0262656,...
       0.0262656,0.0262656,0.0262656,0.0262656,0.0087552,...
       0.0087552,0.0087552,0.0087552,0.0087552,0.0087552];

% 各时段对应的天数
t=[10,10,11,10,10,11,30,31,30,31,31,27,31,30,10,10,11,10,10,10];

% ========== 初始化变量矩阵 ==========
% 水库状态变量
Zlongxia = zeros(Y,20);  % 龙羊峡下游水位
Hlong=zeros(Y,20);       % 龙羊峡水头
Zliuxia=zeros(Y,20);    % 刘家峡下游水位
Hliu=zeros(Y,20);       % 刘家峡水头

% 出力变量
Etii_Long=zeros(Y,20);  % 龙羊峡出力
Etii_liu=zeros(Y,20);   % 刘家峡出力

% 缺水变量
qshortage=zeros(Y,20);  % 各时段缺水量
Qshortage=zeros(Y,20);  % 各时段缺水深度
L_water=zeros(Y,20);    % 生活用水缺水

% 调沙标记
f=zeros(Y,1);  % 标记长系列调节过程中进行调沙的年份，若当年进行了调沙则f(i)=1,否则f(i)=0

% ========== 初始化协同度计算相关变量 ==========
% 供水目标变量
T_Q_shortage1=zeros(Y,1);      % 农业关键期最大缺水深度
water_rate1=zeros(Y,1);        % 工业、生活用水保证率
d_T_Q_shortage1=zeros(Y,1);    % 农业关键期最大缺水深度的有序度
d_water_rate1=zeros(Y,1);      % 工业、生活用水保证率的有序度
water_rate2=zeros(Y,1);        % 农业非关键期供水保证率
d_water_rate2=zeros(Y,1);      % 农业非关键期供水保证率的有序度
T_Q_shortage2=zeros(Y,1);      % 农业非关键期总缺水量
d_T_Q_shortage2=zeros(Y,1);    % 农业非关键期总缺水量的有序度
T_Q_shortage_agr=zeros(Y,1);   % 农业关键时期总缺水量
d_T_Q_shortage_agr=zeros(Y,1); % 农业关键时期总缺水量的有序度
water_rate3=zeros(Y,1);        % 农业(非关键期)用水保证率
d_water_rate3=zeros(Y,1);       % 农业(非关键期)用水保证率的有序度
h_water=zeros(Y,1);            % 供水子系统有序度

% 发电目标变量
ele_rate1=zeros(Y,1);          % 防凌期发电保证率
d_ele_rate1=zeros(Y,1);        % 防凌期发电保证率的有序度
Ntiji_1=zeros(Y,1);           % 防凌期梯级水库平均出力
d_Ntiji_1=zeros(Y,1);         % 防凌期梯级水库平均出力的有序度
ele_rate2=zeros(Y,1);          % 非防凌期发电保证率
d_ele_rate2=zeros(Y,1);        % 非防凌期发电保证率的有序度
Ntiji_2=zeros(Y,1);           % 非防凌期梯级水库平均出力
d_Ntiji_2=zeros(Y,1);         % 非防凌期梯级水库平均出力的有序度
h_ele=zeros(Y,1);             % 发电子系统有序度

% 输沙目标变量
Q_sed=zeros(Y,1);             % 调沙时期的平均流量
d_Q_sed=zeros(Y,1);           % 调沙流量有序度
t_sed=zeros(Y,1);             % 调沙历时
d_t_sed=zeros(Y,1);           % 调沙历时的有序度
h_sed=zeros(Y,1);             % 输沙子系统有序度

% 生态目标变量
eco_rate=zeros(Y,1);          % 生态供水保证率
d_eco_rate=zeros(Y,1);        % 生态保证率的有序度
L_eco=zeros(Y,1);             % 生态脉冲次数
d_L_eco=zeros(Y,1);           % 多次生态脉冲的有序度
L_eco1=zeros(Y,1);            % 一次生态脉冲标记
d_L_eco1=zeros(Y,1);          % 一次生态脉冲的有序度
h_eco=zeros(Y,1);             % 生态子系统有序度

% 传统多目标函数变量
M_water=zeros(Y,1);           % 供水目标
T_Q_shortage=zeros(Y,1);      % 总缺水量
W_sed=zeros(Y,1);             % 总输沙水量
E_tiji=zeros(Y,1);            % 总发电量

X_F = x(1: V);

% ========== 主循环：梯级水库联合调度计算 ==========
for i=1:Y % Y是总年数，以下开始计算部分
    for j = 1:20   % 一年中的时段数，主要以月为时段，其中5、6、7、8四个月均分为上中下三个旬
        
        % ========== 第一个时段特殊处理 ==========
        if j == 1   % 第一个时段7月上，由于第一个时段的初水位（即起调水位）为给定值，与其他时段不同，故将第一个时段单独编写程序
            Vlong(i,j)= chz1(LONG_ZV,LONG_Z_INI(i)); % 插值函数注解： chz1仅用于已知水位插值库容；chz2用于已知库容插值水位或已知下泄流量插值下游水位
            Vliu(i,j)= chz1(LIU_ZV,LIU_Z_INI(i));
        end
        
        % ========== 龙羊峡水库调度计算 ==========
        % 计算时段末库容
        Vlong(i,j+1) = chz1(LONG_ZV,x(j+(i-1)*20));    % 时段末库容，亿方
        
        % 计算下泄流量
        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);  % 下泄流量，库容与流量换算系数：0.0262656为月；0.0087552为旬 m3/s
        Qqs_long(i,j)=0; % 初始化弃水流量
        
        % ========== 防凌期特殊处理 ==========
        if j>8 && j<14 % 防凌期(9月-次年1月)
            Qlongout(i,j) =550; % 防凌期龙羊峡按照保证出力发电 无西线时为（500~600）
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            
            % 检查库容约束
            if Vlong(i,j+1) < 42.63 % 小于死库容
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            elseif Vlong(i,j+1) > 242.9 % 大于满库容
                Vlong(i,j+1) = 242.9;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            end
            x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
        end
        
        % ========== 生态流量约束处理 ==========
        if Qlongout(i,j)<350 % 因龙羊峡出库小于丰水年所对应的适宜生态流量350而对决策变量x(j+(i-1)*20)进行修正
            Qlongout(i,j)=550; % 有西线时是（800~1000），无西线时是（600~800）
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            
            % 检查库容约束
            if Vlong(i,j+1) < 42.63 % 小于死库容
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            elseif Vlong(i,j+1) > 242.9 % 大于满库容
                Vlong(i,j+1) = 242.9;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            end
            x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
        elseif Qlongout(i,j)>1050 % 流量上限约束
            Qlongout(i,j)=550;
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            
            % 检查库容约束
            if Vlong(i,j+1) < 42.63 % 小于死库容
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            elseif Vlong(i,j+1) > 242.9 % 大于满库容
                Vlong(i,j+1) = 242.9;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
            end
            x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
        end
        
        % ========== 龙羊峡水头和出力计算 ==========
        % 计算下游水位
        Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
        
        % 计算水头
        if j==1
            Hlong(i,j) =0.5*(x(j+(i-1)*20)+LONG_Z_INI(i)) -Zlongxia(i,j);
        else
            Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
        end
        
        % 计算出力
        Ntii_long(i,j) = 8.6 * (Hlong(i,j)- 0) * Qlongout(i,j)/10000; % 单位万千瓦
        
        % 出力约束处理
        if Ntii_long(i,j) > 128 % 装机容量约束
            Ntii_long(i,j) = 128;
            Qqs_long(i,j)=Qlongout(i,j)-Ntii_long(i,j) *10000/8.6/(Hlong(i,j)- 0); % 弃水流量
        elseif Ntii_long(i,j) <58.7 && Vlong(i,j)>100 % 保证出力约束
            % 以10为一个步长逐渐增大龙羊峡出库流量，直至满足保证出力要求
            for n=1:100
                Qlongout(i,j)=Qlongout(i,j)+10*n;
                Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                
                % 检查库容约束
                if Vlong(i,j+1) < 42.63 % 小于死库容
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                elseif Vlong(i,j+1) > 242.9 % 大于满库容
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                end
                
                x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
                Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
                
                % 重新计算水头
                if j==1
                    Hlong(i,j) =0.5*(x(j+(i-1)*20)+LONG_Z_INI(i)) -Zlongxia(i,j);
                else
                    Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                end
                
                % 重新计算出力
                Ntii_long(i,j) = 8.6 * (Hlong(i,j)-0) * Qlongout(i,j)/10000; % 单位万千瓦
                
                % 检查是否满足出力要求
                if P(i)<0.75 % 非特枯水年
                    if Ntii_long(i,j)>=58.7
                        break % 跳出循环
                    end
                else % 特枯水年
                    if Ntii_long(i,j)>=58.7*0.8 % 来水频率为90%以上的特枯水年按8折发电
                        break % 跳出循环
                    end
                end
            end
        end
        % ========== 刘家峡水库调度计算 ==========
        % 计算时段末库容（基于决策变量水位）
        Vliu(i,j+1) = chz1(LIU_ZV,x(j+20*Y+(i-1)*20));  % 月初库容，亿方
        
        % 计算下泄流量
        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);  % 下泄流量，m3/s
        
        % 需水约束处理：确保满足兰州断面需水要求
        if Qliuout(i,j) < LAN(i,j)-LIU_LAN(i,j)
            Qliuout(i,j) = LAN(i,j)-LIU_LAN(i,j); % 按兰州断面需水下泄
        end
        
        Qqs_liu(i,j) = 0; % 初始化弃水流量
        
        % 防凌期预腾库容处理（10月份）
        if j==8 % 10月预腾防凌库容
            Qliuout(i,j) = 700; % 无西线一期时由于1990至2015序列来水过于偏枯，10月不宜腾过多防凌库容
        end
        
        % 流量约束处理
        if Qliuout(i,j) < 350 % 因刘家峡出库小于350而对决策变量进行修正
            Qliuout(i,j) = LAN(i,j)-LIU_LAN(i,j); % 按兰州断面需水下泄
        elseif Qliuout(i,j) > 1200 % 最大过机流量限制
            Qliuout(i,j) = LAN(i,j)-LIU_LAN(i,j); % 按兰州断面需水下泄
        end
        
        % 重新计算库容（考虑流量约束调整后的影响）
        Vliu(i,j+1) = (Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
        
        % 库容约束检查与处理
        if Vliu(i,j+1) < 6.223 % 小于死库容
            Vliu(i,j+1) = 6.223;
            Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
        elseif Vliu(i,j+1) > 39.93 % 大于满库容
            Vliu(i,j+1) = 39.93;
            Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
        end
        
        % 更新决策变量（水位）
        x(j+20*Y+(i-1)*20) = chz2(LIU_ZV, Vliu(i,j+1));
        
        % 计算下游水位
        Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
        
        % 计算水头（区分第一个时段和后续时段）
        if j==1
            Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+LIU_Z_INI(i)) - Zliuxia(i,j);
        else
            Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
        end
        
        % 计算出力（考虑水头损失3m）
        Ntii_liu(i,j) = 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000; % 单位：万千瓦
        
        % ========== 出力约束处理 ==========
        if Ntii_liu(i,j) > 122.5 % 超过装机容量
            Ntii_liu(i,j) = 122.5; % 按装机容量限制出力
            Qqs_liu(i,j) = Qliuout(i,j)-Ntii_liu(i,j)*10000/8.6/(Hliu(i,j)- 0); % 计算弃水流量
        elseif Ntii_liu(i,j) < 40 % 低于保证出力
            % 通过增大出库流量来满足保证出力要求
            for n=1:100
                Qliuout(i,j) = Qliuout(i,j)+10*n; % 以10为步长逐渐增大出库流量
                
                % 重新计算库容
                Vliu(i,j+1) = (Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
                
                % 库容约束检查
                if Vliu(i,j+1) < 6.223 % 小于死库容
                    Vliu(i,j+1) = 6.223;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                elseif Vliu(i,j+1) > 39.93 % 大于满库容
                    Vliu(i,j+1) = 39.93;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                end
                
                % 更新决策变量和计算参数
                x(j+20*Y+(i-1)*20) = chz2(LIU_ZV, Vliu(i,j+1));
                Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
                
                % 重新计算水头
                if j==1
                    Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+LIU_Z_INI(i)) - Zliuxia(i,j);
                else
                    Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                end
                
                % 重新计算出力
                Ntii_liu(i,j) = 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000; % 水头损失为3m
                
                % 检查是否满足出力要求
                if P(i) < 0.75 % 非特枯水年
                    if Ntii_liu(i,j) >= 40
                        break % 跳出循环
                    end
                else % 特枯水年
                    if Ntii_liu(i,j) >= 40*0.8 % 来水频率为75%以上的枯水年按8折发电
                        break % 跳出循环
                    end
                end
            end
        end
        % ========== 调沙期处理（7月下旬和8月上旬） ==========
        if j==3|| j==4  % 调沙月份
            % 判断是否为偏丰及以上水年，并判断龙、刘水库是否有足够库容冲沙
            if P(i)<=0.80 && Vlong(i,j)>85 && Vliu(i,j)>18 
                % ========== 龙羊峡调沙处理 ==========
                Qlongout(i,j) = 1350; % 7月下旬刘家峡水位较低，故龙羊峡按最小调沙流量下泄，剩余调沙水量由刘家峡补充
                Vlong(i,j+1) = Vlong(i,j)-(Qlongout(i,j)-LONG_IN(i,j))*xishu(j);
                
                % 检查库容约束
                if Vlong(i,j+1) < 42.63 % 小于死库容
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                elseif Vlong(i,j+1) > 242.9 % 大于满库容
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                end
                
                % 更新决策变量和计算相关参数
                x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
                Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
                Hlong(i,j) = 0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) - Zlongxia(i,j);
                Ntii_long(i,j) = 128; % 调沙期间出力按装机满发
                Qqs_long(i,j) = Qlongout(i,j) - 1050;
                
                % ========== 刘家峡调沙处理 ==========
                Qliuout(i,j) = Q_sediment - LIU_LAN(i,j); % 要使调沙流量在1800-2200之间
                Vliu(i,j+1) = Vliu(i,j)-(Qliuout(i,j)-Qlongout(i,j)-LONG_LIU(i,j))*xishu(j); % 注意：刘家峡水库可能跌破死库容
                
                % 检查库容约束
                if Vliu(i,j+1) < 6.223 % 小于死库容
                    Vliu(i,j+1) = 6.223;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                elseif Vliu(i,j+1) > 39.93 % 大于满库容
                    Vliu(i,j+1) = 39.93;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                end
                
                % 更新决策变量和计算相关参数
                x(j+20*Y+(i-1)*20) = chz2(LIU_ZV,Vliu(i,j+1));
                Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                Ntii_liu(i,j) = 122.5; % 调沙期间出力按装机满发
                Qqs_liu(i,j) = Qliuout(i,j) - 1200;
                
                % 更新调沙标记
                f(i) = 1; % 记第i年是否调水调沙
                k = k+1; % 记长系列调沙的总年数
            end
        end
        %%%%%%%%%%%%%%防凌期特殊流量判断%%%%%%%%%%%%
        if j>8 && j<14
            if Qliuout(i,j) >Qmin(j-8) %防凌流量约束判断
                temp1= chz1(LIU_ZV,x(j+20*Y+(i-1)*20));%刘家峡本时段末库容
                temp2= chz1(LIU_ZV,VarMax(j+20*Y+(i-1)*20));%刘家峡本时段库容上限
                %temp2= 39.93;%刘家峡本时段库容上限
                temp3=(Qliuout(i,j) -Qmin(j-8))*xishu(j)-(temp2-temp1);%判断如果刘家峡独立存蓄“超出防凌流量”的那部分水量（而不是下泄），是否会超过刘家峡的时段水位上限
                if temp3>0%刘家峡蓄满后还有无法存蓄的水量，两种思路：1、刘家峡存不下的水由龙羊峡来存（减小龙羊峡出库）；2、在上一时段让刘家峡多放，以腾库容（在本程序中没有体现）
                    temp11=chz1(LONG_ZV,x(j+(i-1)*20));%龙羊峡本时段初库容
                    temp22=chz1(LONG_ZV,VarMax(j-1+(i-1)*20));%龙羊峡本时段库容上限
                    temp33=temp22-temp11;%龙羊峡空余的库容
                    if temp33>temp3  %龙有足够库容可以接纳多余水量（通过减小龙羊峡出库流量来实现）
                        Vlong(i,j+1)=Vlong(i,j+1)+temp3;
                        x(j+(i-1)*20)=chz2(LONG_ZV,Vlong(i,j+1));
                        Qlongout(i,j)=Qlongout(i,j)-temp3/xishu(j);
                        Qliuout(i,j) =Qmin(j-8);
                        x(j+20*Y+(i-1)*20)=VarMax(j+20*Y+(i-1)*20);%如果刘家峡水位达到上限水位
                        Vliu(i,j+1) =chz1(LIU_ZV,x(j+20*Y+(i-1)*20));
                    else%此时刘家峡已蓄满，而龙羊峡仍不可以完全接纳多余的水量
                        Vlong(i,j+1)=Vlong(i,j+1)+temp33;%让龙羊峡的库容等于上限库容，即让龙羊峡蓄满
                        x(j+(i-1)*20)=VarMax(j+(i-1)*20);
                        Qlongout(i,j)=Qlongout(i,j)-temp33/xishu(j);
                        Qliuout(i,j) =Qmin(j-8)+(temp3-temp33)/xishu(j);%两个水库都已蓄满，只能超出防凌流量
                        x(j+20*Y+(i-1)*20)=VarMax(j+20*Y+(i-1)*20);
                        Vliu(i,j+1) =chz1(LIU_ZV,x(j+20*Y+(i-1)*20));
                    end
                else
                    Vliu(i,j+1)=Vliu(i,j+1)+(Qliuout(i,j)-Qmin(j-8))*xishu(j);
                    Qliuout(i,j) =Qmin(j-8);
                    x(j+20*Y+(i-1)*20)=chz2(LIU_ZV,Vliu(i,j+1));
                end
                Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));%龙羊峡出力计算与判断
                Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                Ntii_long(i,j)= 8.6 * (Hlong(i,j)-0) * Qlongout(i,j)/10000;%水头损失2.5m
                Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));%刘家峡出力计算与判断
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                Ntii_liu(i,j) = 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%水头损失为3m
            end
        end
        % ========== 梯级水电站出力计算 ==========
        % ========== 拉西瓦水电站出力计算 ==========
        Ntii_laxiwa(i,j) = 8.3*205*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 拉西瓦水电站的出力
        if Ntii_laxiwa(i,j) > 280
            Ntii_laxiwa(i,j) = 280; % 限制在装机容量280万千瓦以内
        end
        
        % ========== 尼那水电站出力计算 ==========
        Ntii_nina(i,j) = 8*15*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 尼那水电站的出力
        if Ntii_nina(i,j) > 16
            Ntii_nina(i,j) = 16; % 限制在装机容量16万千瓦以内
        end
        
        % ========== 李家峡水电站出力计算 ==========
        Ntii_lijiaxia(i,j) = 8.3*122*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 李家峡水电站的出力
        if Ntii_lijiaxia(i,j) > 160
            Ntii_lijiaxia(i,j) = 160; % 限制在装机容量160万千瓦以内
        end
        
        % ========== 积石峡水电站出力计算 ==========
        Ntii_jishixia(i,j) = 8.3*66*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 积石峡水电站的出力
        if Ntii_jishixia(i,j) > 102
            Ntii_jishixia(i,j) = 102; % 限制在装机容量102万千瓦以内
        end
        
        % ========== 直岗拉卡水电站出力计算 ==========
        Ntii_zhiganglaka(i,j) = 8.2*12.5*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 直岗拉卡水电站的出力
        if Ntii_zhiganglaka(i,j) > 19
            Ntii_zhiganglaka(i,j) = 19; % 限制在装机容量19万千瓦以内
        end
        
        % ========== 康扬水电站出力计算 ==========
        Ntii_kangyang(i,j) = 8.2*18.7*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 康扬水电站的出力
        if Ntii_kangyang(i,j) > 30
            Ntii_kangyang(i,j) = 30; % 限制在装机容量30万千瓦以内
        end
        
        % ========== 公伯峡水电站出力计算 ==========
        Ntii_gongboxia(i,j) = 8.3*99.3*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 公伯峡水电站的出力
        if Ntii_gongboxia(i,j) > 150
            Ntii_gongboxia(i,j) = 150; % 限制在装机容量150万千瓦以内
        end
        
        % ========== 苏只水电站出力计算 ==========
        Ntii_suzhi(i,j) = 8.3*16*(Qlongout(i,j)+LONG_LIU(i,j))/10000; % 苏只水电站的出力
        if Ntii_suzhi(i,j) > 22
            Ntii_suzhi(i,j) = 22; % 限制在装机容量22万千瓦以内
        end
        
        % ========== 盐锅峡水电站出力计算 ==========
        Ntii_yanguoxia(i,j) = 7.9*38*(Qliuout(i,j)+LIU_LAN(i,j))/10000; % 盐锅峡水电站的出力
        if Ntii_yanguoxia(i,j) > 40
            Ntii_yanguoxia(i,j) = 40; % 限制在装机容量40万千瓦以内
        end
        
        % ========== 八盘峡水电站出力计算 ==========
        Ntii_bapanxia(i,j) = 8.3*18*(Qliuout(i,j)+LIU_LAN(i,j))/10000; % 八盘峡水电站的出力
        if Ntii_bapanxia(i,j) > 18
            Ntii_bapanxia(i,j) = 18; % 限制在装机容量18万千瓦以内
        end
        
        % ========== 小峡水电站出力计算 ==========
        Ntii_xiaoxia(i,j) = 8.3*13.8*(Qliuout(i,j)+LIU_LAN(i,j))/10000; % 小峡水电站的出力
        if Ntii_xiaoxia(i,j) > 23
            Ntii_xiaoxia(i,j) = 23; % 限制在装机容量23万千瓦以内
        end
        
        % ========== 大峡水电站出力计算 ==========
        Ntii_daxia(i,j) = 8.3*24*(Qliuout(i,j)+LIU_LAN(i,j))/10000; % 大峡水电站的出力
        if Ntii_daxia(i,j) > 30
            Ntii_daxia(i,j) = 30; % 限制在装机容量30万千瓦以内
        end
        
        % ========== 青铜峡水电站出力计算 ==========
        Ntii_qingtongxia(i,j) = 8.3*16*(Qliuout(i,j)+LIU_LAN(i,j))/10000; % 青铜峡水电站的出力
        if Ntii_qingtongxia(i,j) > 30
            Ntii_qingtongxia(i,j) = 30; % 限制在装机容量30万千瓦以内
        end
        
        % ========== 梯级水电站总发电量计算 ==========
        Etii_longliu(i,j) = (Ntii_long(i,j)+ Ntii_liu(i,j)+Ntii_laxiwa(i,j)+Ntii_nina(i,j)+...
                             Ntii_lijiaxia(i,j)+ Ntii_zhiganglaka(i,j)+ Ntii_kangyang(i,j)+...
                             Ntii_gongboxia(i,j)+Ntii_suzhi(i,j)+Ntii_yanguoxia(i,j)+...
                             Ntii_bapanxia(i,j)+Ntii_xiaoxia(i,j)+Ntii_daxia(i,j)+...
                             Ntii_qingtongxia(i,j)) * t(j) * 24 * 10^(-4); % 单位为亿千瓦时
        
        % ========== 刘家峡入库流量计算 ==========
        Qliuin(i,j) = Qlongout(i,j)+LONG_LIU(i,j);
        
        % 重新给下一年的起调水位赋值（即上年年末水位）
        if j==20
            LONG_Z_INI(i+1) = x(j+(i-1)*20);
            LIU_Z_INI(i+1) = x(j+20*Y+(i-1)*20);
        end
    end
    
    % ========== 协同度计算开始 ==========
    
    % ========== 供水目标的关键利益与非关键利益序参量计算 ==========
    % 全年各时段工业、生活、河道外生态的缺水量计算
    qshortage1(i,:) = (LAN_unagr(i,1:20)-Qliuout(i,1:20)-LIU_LAN(i,1:20)).*xishu(1:20);
    Qshortage1(i,:) = max(qshortage1(i,:),0); % 每个时段的兰州工业、生活、河道外生态缺水量，亿m3
    water_rate1(i) = length(find(Qshortage1(i,:)==0))/20; % 供水目标中工业、生活用水保证率
    d_water_rate1(i) = (water_rate1(i)-0)/(1-0); % 供水目标中工业、生活用水保证率的有序度
    
    % 农业关键时期缺水量计算（5上、5中、6上、7上、7中、8中）
    qshortage_agr(i,:) = (LAN(i,[1 2 5 15 16 18])-Qliuout(i,[1 2 5 15 16 18])-LIU_LAN(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18]);
    Qshortage_agr(i,:) = max(qshortage_agr(i,:),0); % 农业关键时期各时段缺水量
    T_Q_shortage_agr(i) = sum(Qshortage_agr(i,:)); % 农业关键时期总缺水量
    d_T_Q_shortage_agr(i) = (26.63-T_Q_shortage_agr(i))/(26.63-0); % 农业关键时期总缺水量的有序度
    
    % 农业关键时期最大缺水深度计算
    T_Q_shortage1(i) = max(Qshortage_agr(i,:)./((LAN(i,[1 2 5 15 16 18])-LAN_unagr(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18])));
    d_T_Q_shortage1(i) = (1-T_Q_shortage1(i))/(1-0); % 供水目标中农业关键时期相对缺水深度的有序度
    
    % 农业非关键期缺水量计算
    qshortage2(i,:) = (LAN(i,[3 4 6:9 13 14 17 19 20])-Qliuout(i,[3 4 6:9 13 14 17 19 20])-LIU_LAN(i,[3 4 6:9 13 14 17 19 20])).*xishu([3 4 6:9 13 14 17 19 20]);
    Qshortage2(i,:) = max(qshortage2(i,:),0); % 供水目标中农业非关键期的各时段缺水量
    water_rate2(i) = length(find(Qshortage2(i,:)==0))/11; % 供水目标中农业非关键期供水保证率
    d_water_rate2(i) = (water_rate2(i)-0)/(1-0); % 供水目标中农业非关键期供水保证率的有序度
    T_Q_shortage2(i) = sum(Qshortage2(i,:)); % 供水目标中农业非关键期的总缺水量
    d_T_Q_shortage2(i) = (41.56-T_Q_shortage2(i))/(41.56-0); % 农业非关键时期总缺水量的有序度
    
    % 某一年供水子系统有序度计算
    h_water(i) = 0.1*d_water_rate1(i)+0.25*d_T_Q_shortage_agr(i)+0.25*d_T_Q_shortage1(i)+0.20*d_water_rate2(i)+0.20*d_T_Q_shortage2(i);
    % ========== 发电目标的关键利益与非关键利益序参量计算 ==========
    % 防凌期发电保证率计算（9-13月）
    ele_rate1(i) = length(find((Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+...
                                Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+...
                                Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+...
                                Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+...
                                Ntii_qingtongxia(i,9:13))>431))/5;
    d_ele_rate1(i) = (ele_rate1(i)-0)/(1-0); % 发电目标中防凌期发电保证率的有序度
    
    % 防凌期梯级水库平均出力计算
    Ntiji_1(i) = mean(Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+...
                       Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+...
                       Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+...
                       Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+...
                       Ntii_qingtongxia(i,9:13));
    d_Ntiji_1(i) = (Ntiji_1(i)-0)/(1164-0); % 发电目标中防凌期梯级水库平均出力的有序度
    
    % 非防凌期发电保证率计算
    ele_rate2(i) = length(find((Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+...
                                Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+...
                                Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+...
                                Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+...
                                Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]))>431))/15;
    d_ele_rate2(i) = (ele_rate2(i)-0)/(1-0); % 发电目标中非防凌期发电保证率的有序度
    
    % 非防凌期梯级水库平均出力计算
    Ntiji_2(i) = mean(Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+...
                       Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+...
                       Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+...
                       Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+...
                       Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]));
    d_Ntiji_2(i) = (Ntiji_2(i)-0)/(1164-0); % 发电目标中非防凌期梯级水库平均出力的有序度
    
    % 某一年发电子系统有序度计算
    h_ele(i) = 0.2*d_ele_rate1(i)+0.2*d_Ntiji_1(i)+0.3*d_ele_rate2(i)+0.3*d_Ntiji_2(i);
    % ========== 输沙目标的关键利益与非关键利益序参量计算 ==========
    if f(i)==1 % 如果当年调沙
        % 判断调沙情况并计算调沙参数
        if Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) % 时段3、4均调沙
            Q_sed(i) = mean(Qliuout(i,[3 4])+LIU_LAN(i,[3 4])); % 调沙时期的平均流量
            t_sed(i) = t(3)+t(4); % 调沙历时，两个旬
        elseif Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)<Q_sediment-LIU_LAN(i,4) % 只有时段3调沙
            Q_sed(i) = Qliuout(i,3)+LIU_LAN(i,3);
            t_sed(i) = t(3); % 调沙历时，一个旬
        elseif Qliuout(i,3)<Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) % 只有时段4调沙
            Q_sed(i) = Qliuout(i,4)+LIU_LAN(i,4);
            t_sed(i) = t(4); % 调沙历时，一个旬
        end
       
        % 计算输沙有序度
        d_Q_sed(i) = (Q_sed(i)-1800)/(2200-1800); % 调沙流量有序度 
        d_t_sed(i) = (t_sed(i)-10)/(30-10); % 调沙历时的有序度
        h_sed(i) = 0.6*d_Q_sed(i)+0.4*d_t_sed(i); % 某一年输沙子系统有序度
    end
    
    % ========== 生态目标的关键利益与非关键利益序参量计算 ==========
    % 生态缺水流量计算
    qshortage_eco(i,:) = (Q_eco(i,:)-Qliuout(i,:)-LIU_LAN(i,:));
    Qshortage_eco(i,:) = max(qshortage_eco(i,:),0); % 生态目标中每个时段的生态缺水流量
    eco_rate(i) = numel(Qshortage_eco(i,:),Qshortage_eco(i,:)==0)/20; % 生态目标中生态供水保证率
    d_eco_rate(i) = (eco_rate(i)-0.75)/(1-0.75); % 生态目标中生态保证率的有序度
    
    % 生态脉冲计算
    if P(i)<=0.75 % 非枯水年
        L_eco(i) = length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>900)); % 统计5、6两个月中产生脉冲的时段数
    else % 枯水年
        L_eco(i) = length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>400)); % 统计5、6两个月中产生脉冲的时段数,枯水年生态脉冲400
    end
    
    % 生态脉冲有序度计算
    if L_eco(i)>0
        d_L_eco1(i) = 1; % 一次生态脉冲的有序度
        d_L_eco(i) = (L_eco(i)-1-0)/(5-0); % 生态目标中多次生态脉冲的有序度
    else 
        d_L_eco1(i) = 0;
        d_L_eco(i) = 0;
    end
    
    % 某一年生态子系统有序度计算
    h_eco(i) = 0.4*d_eco_rate(i)+0.3*d_L_eco1(i)+0.3*d_L_eco(i);
    % ========== 传统多目标模型的目标函数值求解 ==========
    % 全年各时段兰州缺水量计算
    qshortage(i,:) = (LAN(i,:)-Qliuout(i,:)-LIU_LAN(i,:)).*xishu(1:20);
    Qshortage(i,:) = max(qshortage(i,:),0); % 全年各时段兰州缺水量
    T_Q_shortage(i) = sum(Qshortage(i,:)); % 全年总兰州缺水量(亿m3)
    E_tiji(i) = sum(Etii_longliu(i,:)); % 全年总发电量（亿kwh）
    W_sed(i) = Q_sed(i)*t_sed(i)*24*3600/100000000; % 全年总输沙水量(亿m3)
end

% ========== 多年调节有序度求解 ==========
H_water = sum(h_water)/Y; % 供水子系统的多年调节有序度
H_ele = sum(h_ele)/Y; % 发电子系统的多年调节有序度
H_sed=0.8*sum(h_sed)/(k+1e-8)+0.2*((k/Y-0.1)/(0.3-0.1)); % 输沙子系统的多年调节有序度,调沙年份有序度的平均值与长系列调沙频率有序度的加权求和
H_eco = sum(h_eco)/Y; % 生态子系统的多年调节有序度

% ========== 梯级水库调度系统的总协同度求解 ==========
% H_tiji=0.3*H_water+0.3*H_ele+0.3* H_sed+0.1*H_eco; % 加权平均方法
H_tiji = geomean(max(0, [H_water,H_ele, H_sed, H_eco])); % 几何平均方法
f2 = (-1)*H_tiji; % 由寻找最大值转换为寻找最小值

% ========== 目标函数值求解 ==========
W_shortage = sum(T_Q_shortage)/Y;
f1 = W_shortage;

if M == 2
    % 目标1: 兰州断面总缺水量最小 (亿m3)
    f_obj(1) = f1;
    % 目标2: 梯级水电站群年均发电量最大（亿kWh）
    f_obj(2) = -mean(E_tiji);  % 龙-青铜峡之间的全部梯级
elseif M == 3
    % 目标1: 兰州断面总缺水量最小 (亿m3)
    f_obj(1) = f1;
    % 目标2: 梯级水电站群年均发电量最大（亿kWh）
    f_obj(2) = -mean(E_tiji);  % 龙-青铜峡之间的全部梯级
    % 目标3: 梯级调度系统总协同度最大
    f_obj(3) = f2;
end
X_F = [X_F, f_obj];


% 保存计算结果（nargout > 1 时才构造，不影响原有调用方）
if nargout > 1
    results = struct();

    % 龙羊峡水库调度结果
    results.Long.V = Vlong; % 库容
    results.Long.Qout = Qlongout;  % 下泄流量

    % 刘家峡水库调度结果
    results.Liu.V = Vliu; % 库容
    results.Liu.Qout = Qliuout;  % 下泄流量

    % 水电站出力
    results.N.Ntii_long = Ntii_long;
    results.N.Ntii_liu = Ntii_liu;
    results.N.Ntii_laxiwa = Ntii_laxiwa;
    results.N.Ntii_nina = Ntii_nina;
    results.N.Ntii_lijiaxia = Ntii_lijiaxia;
    results.N.Ntii_zhiganglaka = Ntii_zhiganglaka;
    results.N.Ntii_kangyang = Ntii_kangyang;
    results.N.Ntii_gongboxia = Ntii_gongboxia;
    results.N.Ntii_suzhi = Ntii_suzhi;
    results.N.Ntii_yanguoxia = Ntii_yanguoxia;
    results.N.Ntii_bapanxia = Ntii_bapanxia;
    results.N.Ntii_xiaoxia = Ntii_xiaoxia;
    results.N.Ntii_daxia = Ntii_daxia;
    results.N.Ntii_qingtongxia = Ntii_qingtongxia;
    results.N.Etii_longliu = Etii_longliu; % 梯级总发电量

    % 兰州断面缺水量
    results.liuzhou.Qshortage = Qshortage;
    results.liuzhou.T_Q_shortage = T_Q_shortage;

    % 生态数据
    results.ecology.Qshortage_eco = Qshortage_eco;
    results.ecology.eco_rate = eco_rate;

    % 协同度数据
    results.coordination.h_water = h_water;
    results.coordination.h_ele = h_ele;
    results.coordination.h_sed = h_sed;
    results.coordination.h_eco = h_eco;
end



end