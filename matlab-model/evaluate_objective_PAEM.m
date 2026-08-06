function [X_F, results] = evaluate_objective_PAEM(x, V, M, K_mut, accuracy, Q_sediment)


global LONG_ZQ LONG_ZV LIU_ZQ LIU_ZV LAN_unagr
global Q_eco P LONG_IN LONG_LIU LIU_LAN LAN Y VarMin VarMax

% 约束参数（由 Web 服务通过全局变量注入）
global LONG_Z_INI_VAL LIU_Z_INI_VAL QMIN_VAL

%% 龙、刘起调水位
LONG_Z_INI = zeros(Y, 1);
LIU_Z_INI = zeros(Y, 1);
if ~isempty(LONG_Z_INI_VAL)
    LONG_Z_INI(1) = LONG_Z_INI_VAL;
else
    LONG_Z_INI(1) = 2580;  %默认龙羊峡起调水位2580
end
if ~isempty(LIU_Z_INI_VAL)
    LIU_Z_INI(1) = LIU_Z_INI_VAL;
else
    LIU_Z_INI(1) = 1720;   %默认刘家峡起调水位1720
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%以下是梯级水库联合调度程序%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if ~isempty(QMIN_VAL) && length(QMIN_VAL) == 5
    Qmin = QMIN_VAL;
else
    Qmin = [610,420,420,420,420];   %防凌流量(11\12\1\2\3)
end
xishu=[0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552];
t=[10,10,11,10,10,11,30,31,30,31,31,27,31,30,10,10,11,10,10,10];%各时段对应的天数
Zlongxia = zeros(Y,20);%对变量预设内存
Hlong=zeros(Y,20);
Zliuxia=zeros(Y,20);
Hliu=zeros(Y,20);

qshortage=zeros(Y,20);
Qshortage=zeros(Y,20);

f=zeros(Y,1);%用于标记长系列调节过程中进行调沙的年份，若当年进行了调沙则f(i)=1,否则f(i)=0
T_Q_shortage1=zeros(Y,1);
water_rate1=zeros(Y,1);
d_T_Q_shortage1=zeros(Y,1);
d_water_rate1=zeros(Y,1);
water_rate2=zeros(Y,1);
d_water_rate2=zeros(Y,1);
T_Q_shortage2=zeros(Y,1);
d_T_Q_shortage2=zeros(Y,1);
T_Q_shortage_agr=zeros(Y,1);
d_T_Q_shortage_agr=zeros(Y,1);

h_water=zeros(Y,1);
ele_rate1=zeros(Y,1);
d_ele_rate1=zeros(Y,1);
Ntiji_1=zeros(Y,1);
d_Ntiji_1=zeros(Y,1);
ele_rate2=zeros(Y,1);
d_ele_rate2=zeros(Y,1);
Ntiji_2=zeros(Y,1);
d_Ntiji_2=zeros(Y,1);
h_ele=zeros(Y,1);
Q_sed=zeros(Y,1);
d_Q_sed=zeros(Y,1);
t_sed=zeros(Y,1);
d_t_sed=zeros(Y,1);
h_sed=zeros(Y,1);
eco_rate=zeros(Y,1);
d_eco_rate=zeros(Y,1);
L_eco=zeros(Y,1);
d_L_eco=zeros(Y,1);
d_L_eco1=zeros(Y,1);
h_eco=zeros(Y,1);

T_Q_shortage=zeros(Y,1);
W_sed=zeros(Y,1);
E_tiji=zeros(Y,1);

%%
X_F = zeros(1 + K_mut, V + M);
X_F(1, 1: V) = x(1: V);
i_mut = randi([1, Y], 1, K_mut);  % 随机选一年
j_mut = randi([1, 20], 1, K_mut);  % 随机选一个旬/月

for k_m = 0: K_mut
    m=0;
    k=0;
    if k_m > 0
        state_0 = {Vlong, Vliu};
        decision_0  = X_F(k_m, 1: V);

        x = decision_0;
        i_start = i_mut(k_m);
        j_start = j_mut(k_m);
        im = (i_start - 1) * 20 + j_start;
        x(im) = mutation_one_variable(x(im), 20, VarMin(im), VarMax(im));
        
        decision_mut = x(1: V);
        X_F(k_m + 1, 1: V) = decision_mut;
    else
        i_start = 1;
        j_start = 1;
    end
    
    for i = i_start: Y  %Y是总年数，以下开始计算部分
        flag_s = false;
        flag_d = false;
        for j = 1: 20  %一年中的时段数，主要以月为时段，其中5、6、7、8四个月均分为上中下三个旬
            
            if j == 1   %第一个时段7月上，由于第一个时段的初水位（即起调水位）为给定值，与其他时段不同，故将第一个时段单独编写程序
                Vlong(i,j)= chz1(LONG_ZV, LONG_Z_INI(i)); %插值函数注解： chz1仅用于已知水位插值库容；chz2用于已知库容插值水位或已知下泄流量插值下游水位
                Vliu(i,j)= chz1(LIU_ZV, LIU_Z_INI(i));
            end
            Vlong(i,j+1) = chz1(LONG_ZV,x(j+(i-1)*20));    %时段末库容，亿方
            Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;  %下泄流量，库容与流量换算系数：0.0262656为月；0.0087552为旬 m3/s
            Qqs_long(i,j)=0;
            if j>8 && j<14
                Qlongout(i,j) =550;%防凌期龙羊峡按照保证出力发电 无西线时为（500~600）
                Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                if Vlong(i,j+1) < 42.63%小于死库容
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                elseif Vlong(i,j+1) > 242.9% 大于满库容
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                end
                x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
            end
            if  Qlongout(i,j)<350 %因龙羊峡出库小于丰水年所对应的适宜生态流量350而对决策变量x(j+(i-1)*20)进行修正
                Qlongout(i,j)=550;%有西线时是（800~1000），无西线时是（600~800）
                Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                if Vlong(i,j+1) < 42.63%小于死库容
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                elseif Vlong(i,j+1) > 242.9% 大于满库容
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                end
                x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
            elseif Qlongout(i,j)>1050
                Qlongout(i,j)=550;
                Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                if Vlong(i,j+1) < 42.63%小于死库容
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                elseif Vlong(i,j+1) > 242.9% 大于满库容
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                end
                x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
            end
            Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
            if j==1
                Hlong(i,j) =0.5*(x(j+(i-1)*20)+LONG_Z_INI(i)) -Zlongxia(i,j);
            else
                Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
            end
            Ntii_long(i,j) = 8.6 * (Hlong(i,j)- 0) * Qlongout(i,j)/10000; %单位万千瓦
            if Ntii_long(i,j) > 128
                Ntii_long(i,j) = 128;
                Qqs_long(i,j)=Qlongout(i,j)-Ntii_long(i,j) *10000/8.6/(Hlong(i,j)- 0);%弃水流量
            elseif Ntii_long(i,j) <58.7 && Vlong(i,j)>100
                for  n=1:100
                    Qlongout(i,j)=Qlongout(i,j)+10*n; %以10为一个步长逐渐增大龙羊峡出库流量，直至满足保证出力要求
                    Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                    if Vlong(i,j+1) < 42.63%小于死库容
                        Vlong(i,j+1) = 42.63;
                        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                    elseif Vlong(i,j+1) > 242.9% 大于满库容
                        Vlong(i,j+1) = 242.9;
                        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                    end
                    x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
                    Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
                    if j==1
                        Hlong(i,j) =0.5*(x(j+(i-1)*20)+LONG_Z_INI(i)) -Zlongxia(i,j);
                    else
                        Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                    end
                    Ntii_long(i,j) = 8.6 * (Hlong(i,j)-0) * Qlongout(i,j)/10000; %单位万千瓦
                    if P(i)<0.75
                        if Ntii_long(i,j)>=58.7
                            break%跳出循环
                        end
                    else
                        if Ntii_long(i,j)>=58.7*0.8%来水频率为90%以上的特枯水年按8折发电
                            break%跳出循环
                        end
                    end
                end
            end
            Vliu(i,j+1) = chz1(LIU_ZV,x(j+20*Y+(i-1)*20));  %月初库容，亿方，x为决策变量水位，一次解的生成是生成两个水库共Y年的2*20*Y个水位值。“20*Y”是前面龙羊峡的水位过程
            Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);  %下泄流量，m3/s
            if Qliuout(i,j)<LAN(i,j)-LIU_LAN(i,j)
                Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%按兰州断面需水下泄
            end
            Qqs_liu(i,j)=0;
            if  j==8 %10月预腾防凌库容
                Qliuout(i,j) =700;%无西线一期时由于1990至2015序列来水过于偏枯，10月不宜腾过多防凌库容  unifrnd(700,750,1)
            end
            if Qliuout(i,j) <350 %因刘家峡出库小于350而对决策变量x(j+20*Y+(i-1)*20)进行修正
                Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%按兰州断面需水下泄
            elseif Qliuout(i,j) > 1200 %最大过机流量限制
                Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%按兰州断面需水下泄
            end
            Vliu(i,j+1)=(Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
            if Vliu(i,j+1) < 6.223%小于死库容
                Vliu(i,j+1) = 6.223;
                Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
            elseif Vliu(i,j+1) > 39.93% 大于满库容
                Vliu(i,j+1) = 39.93;
                Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
            end
            x(j+20*Y+(i-1)*20)=chz2(LIU_ZV, Vliu(i,j+1));
            Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
            if j==1
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+LIU_Z_INI(i)) - Zliuxia(i,j);
            else
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
            end
            Ntii_liu(i,j)= 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%水头损失为3m
            if Ntii_liu(i,j) > 122.5
                Ntii_liu(i,j) = 122.5;
                Qqs_liu(i,j)=Qliuout(i,j)-Ntii_liu(i,j)*10000/8.6/(Hliu(i,j)- 0);
            elseif Ntii_liu(i,j) <40
                for n=1:100
                    Qliuout(i,j)= Qliuout(i,j)+10*n; %以10为步长逐渐增大出库流量，直至满足保证出力要求
                    Vliu(i,j+1)=(Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
                    if Vliu(i,j+1) < 6.223%小于死库容
                        Vliu(i,j+1) = 6.223;
                        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                    elseif Vliu(i,j+1) > 39.93% 大于满库容
                        Vliu(i,j+1) = 39.93;
                        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                    end
                    x(j+20*Y+(i-1)*20)=chz2(LIU_ZV, Vliu(i,j+1));
                    Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
                    if j==1
                        Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+LIU_Z_INI(i)) - Zliuxia(i,j);
                    else
                        Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                    end
                    Ntii_liu(i,j)= 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%水头损失为3m
                    if P(i)<0.75
                        if Ntii_liu(i,j)>=40
                            break%跳出循环
                        end
                    else
                        if Ntii_liu(i,j)>=40*0.8%来水频率为75%以上的枯水年按8折发电
                            break%跳出循环
                        end
                    end
                end
            end
            if j==3|| j==4  %调沙月份
            
                if P(i)<=0.80 && Vlong(i,j)>85 && Vliu(i,j)>18 %判断是否为偏丰及以上水年，并判断龙、刘水库是否有足够库容冲沙
                    Qlongout(i,j) =1350 ;%7月下旬刘家峡水位较低，故龙羊峡按最小调沙流量下泄，剩余调沙水量由刘家峡补充
                    Vlong(i,j+1)=Vlong(i,j)-( Qlongout(i,j)-LONG_IN(i,j))*xishu(j);
                    if Vlong(i,j+1) < 42.63%小于死库容
                        Vlong(i,j+1) = 42.63;
                        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                    elseif Vlong(i,j+1) > 242.9% 大于满库容
                        Vlong(i,j+1) = 242.9;
                        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                    end
                    x(j+(i-1)*20)=chz2(LONG_ZV,Vlong(i,j+1));
                    Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
                    Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                    Ntii_long(i,j) = 128;%调沙期间出力按装机满发
                    Qqs_long(i,j)=Qlongout(i,j) - 1050;
                    Qliuout(i,j) =Q_sediment - LIU_LAN(i,j) ;%要使调沙流量在1800-2200之间，
                    Vliu(i,j+1)=Vliu(i,j)-( Qliuout(i,j)-Qlongout(i,j)-LONG_LIU(i,j))*xishu(j);%注意：刘家峡水库可能跌破死库容
                    if Vliu(i,j+1) < 6.223%小于死库容
                        Vliu(i,j+1) = 6.223;
                        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                    elseif Vliu(i,j+1) > 39.93% 大于满库容
                        Vliu(i,j+1) = 39.93;
                        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                    end
                    x(j+20*Y+(i-1)*20)=chz2(LIU_ZV,Vliu(i,j+1));
                    Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
                    Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                    Ntii_liu(i,j)=122.5;
                    Qqs_liu(i,j)=Qliuout(i,j) -1200;
                    f(i)=1;%记第i年是否调水调沙
                    k=k+1;%记长系列调沙的总年数
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
            Ntii_laxiwa(i,j)=8.3*205*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%拉西瓦水电站的出力
            if Ntii_laxiwa(i,j)>280
                Ntii_laxiwa(i,j)= 280;
            end
            Ntii_nina(i,j)=8*15*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%尼那水电站的出力
            if Ntii_nina(i,j)>16
                Ntii_nina(i,j)=16;
            end
            Ntii_lijiaxia(i,j)=8.3*122*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%李家峡水电站的出力
            if Ntii_lijiaxia(i,j) >160
                Ntii_lijiaxia(i,j) =160;
            end
            Ntii_jishixia(i,j)=8.3*66*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%积石峡水电站的出力
            if Ntii_jishixia(i,j) >102
                Ntii_jishixia(i,j) =102;
            end
            Ntii_zhiganglaka(i,j)=8.2*12.5*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%直岗拉卡水电站的出力
            if Ntii_zhiganglaka(i,j) >19
                Ntii_zhiganglaka(i,j) =19;
            end
            Ntii_kangyang(i,j)=8.2*18.7*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%康扬水电站的出力
            if Ntii_kangyang(i,j) >30
                Ntii_kangyang(i,j) =30;
            end
            Ntii_gongboxia(i,j)=8.3*99.3*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%公伯峡水电站的出力
            if Ntii_gongboxia(i,j) >150
                Ntii_gongboxia(i,j) =150;
            end
            Ntii_suzhi(i,j)=8.3*16*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%苏只水电站的出力
            if Ntii_suzhi(i,j) >22
                Ntii_suzhi(i,j) =22;
            end
            Ntii_yanguoxia(i,j)=7.9*38*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%盐锅峡水电站的出力
            if Ntii_yanguoxia(i,j) >40
                Ntii_yanguoxia(i,j) =40;
            end
            Ntii_bapanxia(i,j)=8.3*18*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%八盘峡水电站的出力
            if Ntii_bapanxia(i,j) >18
                Ntii_bapanxia(i,j) =18;
            end
            Ntii_xiaoxia(i,j)=8.3*13.8*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%小峡水电站的出力
            if Ntii_xiaoxia(i,j) >23
                Ntii_xiaoxia(i,j) =23;
            end
            Ntii_daxia(i,j)=8.3*24*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%大峡水电站的出力
            if Ntii_daxia(i,j) >30
                Ntii_daxia(i,j) =30;
            end
            Ntii_qingtongxia(i,j)=8.3*16*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%青铜峡水电站的出力
            if Ntii_qingtongxia(i,j) >30
                Ntii_qingtongxia(i,j) =30;
            end
            Etii_longliu(i,j)=(Ntii_long(i,j)+ Ntii_liu(i,j)+Ntii_laxiwa(i,j)+Ntii_nina(i,j)+Ntii_lijiaxia(i,j)+ Ntii_zhiganglaka(i,j)+ Ntii_kangyang(i,j)+Ntii_gongboxia(i,j)+Ntii_suzhi(i,j)+Ntii_yanguoxia(i,j)+Ntii_bapanxia(i,j)+Ntii_xiaoxia(i,j)+Ntii_daxia(i,j)+Ntii_qingtongxia(i,j)) * t(j) * 24 * 10^(-4);    %单位为亿千瓦时;
            Qliuin(i,j) =Qlongout(i,j)+LONG_LIU(i,j);
            
            % 重新给下一年的起调水位赋值（即上年年末水位）
            if j==20
                LONG_Z_INI(i + 1) = x(j+(i-1)*20);
                LIU_Z_INI(i + 1) = x(j+20*Y+(i-1)*20);
            end
        end
        
      
        %以下开始协同度计算
        %%%%%供水目标的关键利益与非关键利益序参量计算%%%%%
        qshortage1(i,:) = (LAN_unagr(i,1:20)-Qliuout(i,1:20)-LIU_LAN(i,1:20)).*xishu(1:20);%全年各时段工业、生活、河道外生态的缺水量
        Qshortage1(i,:) = max(qshortage1(i,:),0);%每个时段的兰州工业、生活、河道外生态缺水量，亿m3，若刘出库流量大于需水，则不缺水，缺水深度为0
        water_rate1(i)=length(find( Qshortage1(i,:)==0))/20; %供水目标中工业、生活用水保证率
        d_water_rate1(i)=(water_rate1(i)-0)/(1-0);%供水目标中工业、生活用水保证率的有序度
        qshortage_agr(i,:) = (LAN(i,[1 2 5 15 16 18])-Qliuout(i,[1 2 5 15 16 18])-LIU_LAN(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18]);%农业关键时期缺水量（5上、5中、6上、7上、7中、8中）
        Qshortage_agr(i,:) = max(qshortage_agr(i,:),0);%农业关键时期各时段缺水量
        T_Q_shortage_agr(i)=sum(Qshortage_agr(i,:)); %农业关键时期总缺水量
        d_T_Q_shortage_agr(i)=(26.63-T_Q_shortage_agr(i))/(26.63-0); %农业关键时期总缺水量的有序度, 最大值为农业关键期总需水量的40%，即25.4亿方(2020水平年)，或26.63亿方(2030水平年)
        T_Q_shortage1(i)=max(Qshortage_agr(i,:)./((LAN(i,[1 2 5 15 16 18])-LAN_unagr(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18])));%农业关键时期最大缺水深度
        d_T_Q_shortage1(i)=(1-T_Q_shortage1(i))/(1-0); %供水目标中农业关键时期相对缺水深度的有序度，上限0.5
        qshortage2(i,:)=(LAN(i,[3 4 6:9 13 14 17 19 20])-Qliuout(i,[3 4 6:9 13 14 17 19 20])-LIU_LAN(i,[3 4 6:9 13 14 17 19 20])).*xishu([3 4 6:9 13 14 17 19 20]);%供水目标中农业非关键期的各时段缺水量
        Qshortage2(i,:)=max(qshortage2(i,:),0);%供水目标中农业非关键期的各时段缺水量
        water_rate2(i)=length(find( Qshortage2(i,:)==0))/11;%供水目标中农业非关键期供水保证率
        d_water_rate2(i)=(water_rate2(i)-0)/(1-0);%供水目标中农业非关键期供水保证率的有序度，阈值上限为1，下限为0.75
        T_Q_shortage2(i)=sum(Qshortage2(i,:)); %供水目标中农业非关键期的总缺水量
        d_T_Q_shortage2(i)=(41.56-T_Q_shortage2(i))/(41.56-0); %农业非关键时期总缺水量的有序度，最大值为非关键期农业需水的40%，即32.696亿方(2020水平年)，或41.56(2030水平年50%)
        h_water(i)=0.1*d_water_rate1(i)+0.25*d_T_Q_shortage_agr(i)+0.25*d_T_Q_shortage1(i)+0.20*d_water_rate2(i)+0.20*d_T_Q_shortage2(i);%某一年供水子系统有序度
        %%%%%发电目标的关键利益与非关键利益序参量计算%%%%%
        ele_rate1(i)= length(find((Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+Ntii_qingtongxia(i,9:13))>431))/5; %发电目标中防凌期发电保证率
        d_ele_rate1(i)=(ele_rate1(i)-0)/(1-0);%发电目标中防凌期发电保证率的有序度
        Ntiji_1(i)=mean(Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+Ntii_qingtongxia(i,9:13));%发电目标中防凌期梯级水库平均出力
        d_Ntiji_1(i)=(Ntiji_1(i)-0)/(1164-0);%发电目标中防凌期梯级水库平均出力的有序度,15级水库的总装机为1164万千瓦，保证出力之和为431万千瓦
        ele_rate2(i)= length(find((Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+ Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]))>431))/15; %发电目标中非防凌期的发电保证率
        d_ele_rate2(i)=(ele_rate2(i)-0)/(1-0);%发电目标中非防凌期发电保证率的有序度
        Ntiji_2(i)=mean(Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+ Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]));%发电目标中非防凌期梯级水库平均出力
        d_Ntiji_2(i)=(Ntiji_2(i)-0)/(1164-0);%发电目标中非防凌期梯级水库平均出力的有序度
        h_ele(i)=0.2*d_ele_rate1(i)+0.2*d_Ntiji_1(i)+0.3* d_ele_rate2(i)+0.3* d_Ntiji_2(i);%某一年发电子系统有序度
        %%%%%输沙目标的关键利益与非关键利益序参量计算%%%%%
        if f(i)==1
            if Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) %先判断当年是否时段3、4均调沙
                Q_sed(i)=mean(Qliuout(i,[3 4])+LIU_LAN(i,[3 4]));%调沙时期的平均流量
                t_sed(i)=t(3)+t(4);%调沙历时，两个旬
            elseif Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)<Q_sediment-LIU_LAN(i,4) %只有时段3调沙
                Q_sed(i)=Qliuout(i,3)+LIU_LAN(i,3);
                t_sed(i)=t(3);%调沙历时，一个旬
            elseif Qliuout(i,3)<Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) %只有时段4调沙
                Q_sed(i)=Qliuout(i,4)+LIU_LAN(i,4);
                t_sed(i)=t(4);%调沙历时，一个旬
            end

            d_Q_sed(i)=(Q_sed(i)-1800)/(2200-1800);%调沙流量有序度
            d_t_sed(i)=(t_sed(i)-10)/(30-10);%调沙历时的有序度
            h_sed(i)=0.6*d_Q_sed(i)+0.4*d_t_sed(i);%某一年输沙子系统有序度
        end
        %%%%%生态目标的关键利益与非关键利益序参量计算%%%%%
        qshortage_eco(i,:) = (Q_eco(i,:)-Qliuout(i,:)-LIU_LAN(i,:));
        Qshortage_eco(i,:) = max(qshortage_eco(i,:),0);%生态目标中每个时段的生态缺水流量
        eco_rate(i)=numel(Qshortage_eco(i,:),Qshortage_eco(i,:)==0)/20; %生态目标中生态供水保证率
        d_eco_rate(i)=(eco_rate(i)-0.75)/(1-0.75);%生态目标中生态保证率的有序度
        if P(i)<=0.75
            L_eco(i)=length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>900));%统计5、6两个月中产生脉冲的时段数
        else
            L_eco(i)=length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>400));%统计5、6两个月中产生脉冲的时段数,枯水年生态脉冲400
        end
        if L_eco(i)>0
            d_L_eco1(i)=1;%一次生态脉冲的有序度
            d_L_eco(i)=(L_eco(i)-1-0)/(5-0);%生态目标中多次生态脉冲的有序度
        else d_L_eco1(i)=0;
            d_L_eco(i)=0;
        end
        h_eco(i)=0.4* d_eco_rate(i)+0.3*d_L_eco1(i)+0.3* d_L_eco(i);%某一年生态子系统有序度
        %%%%%%%%%%%%%传统多目标模型的目标函数值求解%%%%%%%%%%%%%%%%%%
        qshortage(i,:) = (LAN(i,:)-Qliuout(i,:)-LIU_LAN(i,:)).*xishu(1:20);%全年各时段兰州缺水量
        Qshortage(i,:) = max(qshortage(i,:),0);%全年各时段兰州缺水量
        T_Q_shortage(i)=sum(Qshortage(i,:));%全年总兰州缺水量(亿m3)
        E_tiji(i)=sum(Etii_longliu(i,:));%全年总发电量（亿kwh）
        W_sed(i)=Q_sed(i)*t_sed(i)*24*3600/100000000;%全年总输沙水量(亿m3)
        
        % 近似计算精度是否满足要求
        if k_m > 0
            flag_s = abs(state_0{1}(i, j) - Vlong(i, j)) + abs(state_0{2}(i, j) - Vliu(i, j)) <= accuracy(1);
            flag_d = abs(decision_0(j+(i-1)*20) - decision_mut(j+(i-1)*20)) + abs(decision_0(j+20*Y+(i-1)*20) - decision_mut(j+20*Y+(i-1)*20)) <= accuracy(2);
        end
        if flag_s && flag_d
            break
        end
    end
    
    H_water=sum(h_water)/Y;%求供水子系统的多年调节有序度
    H_ele=sum( h_ele)/Y;%求发电子系统的多年调节有序度
    H_sed=0.8*sum(h_sed)/(k+1e-8)+0.2*((k/Y-0.1)/(0.3-0.1));%求输沙子系统的多年调节有序度,调沙年份有序度的平均值与长系列调沙频率有序度的加权求和
    H_eco=sum(h_eco)/Y;%求生态子系统的多年调节有序度
    %     H_tiji=0.3*H_water+0.3*H_ele+0.3* H_sed+0.1*H_eco;
    H_tiji=geomean(max(0, [H_water,H_ele, H_sed, H_eco]));%求梯级水库调度系统的总协同度（几何平均）
    f2=(-1)*H_tiji;%由寻找最大值转换为寻找最小值
    W_shortage=sum(T_Q_shortage)/Y;
    f1=W_shortage;
    
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
    
    %% 汇总原个体和变异个体
    X_F(k_m + 1, V + 1: V + M) = f_obj;
end
% 选择非支配个体
index_nondominated = find_nondominated_solution(X_F, V, M);
X_F = X_F(index_nondominated, :);

% 保存计算结果（nargout > 1 时才构造，不影响原有调用方）
if nargout > 1
    results = struct();

    % 龙羊峡水库调度结果
    results.Long.V = round(Vlong, 3); % 库容
    results.Long.Qout = round(Qlongout, 3);  % 下泄流量

    % 刘家峡水库调度结果
    results.Liu.V = round(Vliu, 3); % 库容
    results.Liu.Qout = round(Qliuout, 3);  % 下泄流量

    % 水电站出力（单位为亿千瓦时）
    results.N.Ntii_long = round(Ntii_long, 3);
    results.N.Ntii_liu = round(Ntii_liu, 3);
    results.N.Ntii_laxiwa = round(Ntii_laxiwa, 3);
    results.N.Ntii_nina = round(Ntii_nina, 3);
    results.N.Ntii_lijiaxia = round(Ntii_lijiaxia, 3);
    results.N.Ntii_zhiganglaka = round(Ntii_zhiganglaka, 3);
    results.N.Ntii_kangyang = round(Ntii_kangyang, 3);
    results.N.Ntii_gongboxia = round(Ntii_gongboxia, 3);
    results.N.Ntii_suzhi = round(Ntii_suzhi, 3);
    results.N.Ntii_yanguoxia = round(Ntii_yanguoxia, 3);
    results.N.Ntii_bapanxia = round(Ntii_bapanxia, 3);
    results.N.Ntii_xiaoxia = round(Ntii_xiaoxia, 3);
    results.N.Ntii_daxia = round(Ntii_daxia, 3);
    results.N.Ntii_qingtongxia = round(Ntii_qingtongxia, 3);
    results.N.Etii_longliu = round(Etii_longliu, 3); % 梯级总发电量

    % 兰州断面缺水量
    results.liuzhou.Qshortage = round(Qshortage, 3);
    results.liuzhou.T_Q_shortage = round(T_Q_shortage, 3);

    % 生态数据
    results.ecology.Qshortage_eco = round(Qshortage_eco, 3);
    results.ecology.eco_rate = round(eco_rate, 3);

    % 协同度数据
    results.coordination.h_water = round(h_water, 3);
    results.coordination.h_ele = round(h_ele, 3);
    results.coordination.h_sed = round(h_sed, 3);
    results.coordination.h_eco = round(h_eco, 3);
end


end