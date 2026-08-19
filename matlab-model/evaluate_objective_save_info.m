function [X_F, results] = evaluate_objective_save_info(x, V, M, Q_sediment)
global LONG_ZQ LONG_ZV LIU_ZQ LIU_ZV LAN_unagr
global Q_eco P LONG_IN LONG_LIU LIU_LAN LAN Y VarMax
%���������ˮλ
LONG_Z_INI = zeros(Y, 1);
LIU_Z_INI = zeros(Y, 1);
LONG_Z_INI(1) = 2580;  %��ʼ��������Ͽ���ˮλ2580
LIU_Z_INI(1) = 1720;  %��ʼ��������Ͽ���ˮλ1720
m=0;
k=0;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%�������ݼ�ˮ�����ϵ��ȳ���%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Qmin=[610,420,420,420,420];   %��������(11\12\1\2\3)
xishu=[0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0262656,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552,0.0087552];
t=[10,10,11,10,10,11,30,31,30,31,31,27,31,30,10,10,11,10,10,10];%��ʱ�ζ�Ӧ������
Zlongxia = zeros(Y,20);%�Ա���Ԥ���ڴ�
Hlong=zeros(Y,20);
Zliuxia=zeros(Y,20);
Hliu=zeros(Y,20);
Etii_Long=zeros(Y,20);
Etii_liu=zeros(Y,20);
qshortage=zeros(Y,20);
Qshortage=zeros(Y,20);
L_water=zeros(Y,20);
f=zeros(Y,1);%���ڱ�ǳ�ϵ�е��ڹ����н��е�ɳ����ݣ�����������˵�ɳ��f(i)=1,����f(i)=0
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
water_rate3=zeros(Y,1);
d_water_rate3=zeros(Y,1);
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
M_water=zeros(Y,1);
T_Q_shortage=zeros(Y,1);
W_sed=zeros(Y,1);
E_tiji=zeros(Y,1);

X_F = x(1: V);
for i=1:Y %Y�������������¿�ʼ���㲿��
    for j = 1:20%һ���е�ʱ��������Ҫ����Ϊʱ�Σ�����5��6��7��8�ĸ��¾���Ϊ����������Ѯ
        
        if j == 1   %��һ��ʱ��7���ϣ����ڵ�һ��ʱ�εĳ�ˮλ�������ˮλ��Ϊ����ֵ��������ʱ�β�ͬ���ʽ���һ��ʱ�ε�����д����
            Vlong(i,j)= chz1(LONG_ZV,LONG_Z_INI(i)); %��ֵ����ע�⣺ chz1��������֪ˮλ��ֵ���ݣ�chz2������֪���ݲ�ֵˮλ����֪��й������ֵ����ˮλ
            Vliu(i,j)= chz1(LIU_ZV,LIU_Z_INI(i));
        end
        Vlong(i,j+1) = chz1(LONG_ZV,x(j+(i-1)*20));    %ʱ��ĩ���ݣ��ڷ�
        Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;  %��й��������������������ϵ����0.0262656Ϊ�£�0.0087552ΪѮ m3/s
        Qqs_long(i,j)=0;
        if j>8 && j<14
            Qlongout(i,j) =550;%����������Ͽ���ձ�֤�������� ������ʱΪ��500~600��
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            if Vlong(i,j+1) < 42.63%С��������
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
            elseif Vlong(i,j+1) > 242.9% ����������
                Vlong(i,j+1) = 242.9;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
            end
            x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
        end
        if  Qlongout(i,j)<350 %������Ͽ����С�ڷ�ˮ������Ӧ��������̬����350���Ծ��߱���x(j+(i-1)*20)��������
            Qlongout(i,j)=550;%������ʱ�ǣ�800~1000����������ʱ�ǣ�600~800��
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            if Vlong(i,j+1) < 42.63%С��������
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
            elseif Vlong(i,j+1) > 242.9% ����������
                Vlong(i,j+1) = 242.9;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
            end
            x(j+(i-1)*20) = chz2(LONG_ZV,Vlong(i,j+1));
        elseif Qlongout(i,j)>1050
            Qlongout(i,j)=550;
            Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
            if Vlong(i,j+1) < 42.63%С��������
                Vlong(i,j+1) = 42.63;
                Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
            elseif Vlong(i,j+1) > 242.9% ����������
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
        Ntii_long(i,j) = 8.6 * (Hlong(i,j)- 0) * Qlongout(i,j)/10000; %��λ��ǧ��
        if Ntii_long(i,j) > 128
            Ntii_long(i,j) = 128;
            Qqs_long(i,j)=Qlongout(i,j)-Ntii_long(i,j) *10000/8.6/(Hlong(i,j)- 0);%��ˮ����
        elseif Ntii_long(i,j) <58.7 && Vlong(i,j)>100
            for  n=1:100
                Qlongout(i,j)=Qlongout(i,j)+10*n; %以10为一个步长逐渐增大龙羊峡出库流量，直至满足保证出力要求
                Vlong(i,j+1)=(LONG_IN(i,j)-Qlongout(i,j))*xishu(j)+Vlong(i,j);
                if Vlong(i,j+1) < 42.63%С��������
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                elseif Vlong(i,j+1) > 242.9% ����������
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
                Ntii_long(i,j) = 8.6 * (Hlong(i,j)-0) * Qlongout(i,j)/10000; %��λ��ǧ��
                if P(i)<0.75
                    if Ntii_long(i,j)>=58.7
                        break%����ѭ��
                    end
                else
                    if Ntii_long(i,j)>=58.7*0.8%��ˮƵ��Ϊ90%���ϵ��ؿ�ˮ�갴8�۷���
                        break%����ѭ��
                    end
                end
            end
        end
        Vliu(i,j+1) = chz1(LIU_ZV,x(j+20*Y+(i-1)*20));  %�³����ݣ��ڷ���xΪ���߱���ˮλ��һ�ν����������������ˮ�⹲Y���2*20*Y��ˮλֵ����20*Y����ǰ������Ͽ��ˮλ����
        Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);  %��й������m3/s
        if Qliuout(i,j)<LAN(i,j)-LIU_LAN(i,j)
            Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%�����ݶ�����ˮ��й
        end
        Qqs_liu(i,j)=0;
        if  j==8 %10��Ԥ�ڷ������
            Qliuout(i,j) =700;%������һ��ʱ����1990��2015������ˮ����ƫ�ݣ�10�²����ڹ���������  unifrnd(700,750,1)
        end
        if Qliuout(i,j) <350 %������Ͽ����С��350���Ծ��߱���x(j+20*Y+(i-1)*20)��������
            Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%�����ݶ�����ˮ��й
        elseif Qliuout(i,j) > 1200 %��������������
            Qliuout(i,j) =LAN(i,j)-LIU_LAN(i,j);%�����ݶ�����ˮ��й
        end
        Vliu(i,j+1)=(Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
        if Vliu(i,j+1) < 6.223%С��������
            Vliu(i,j+1) = 6.223;
            Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
        elseif Vliu(i,j+1) > 39.93% ����������
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
        Ntii_liu(i,j)= 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%ˮͷ��ʧΪ3m
        if Ntii_liu(i,j) > 122.5
            Ntii_liu(i,j) = 122.5;
            Qqs_liu(i,j)=Qliuout(i,j)-Ntii_liu(i,j)*10000/8.6/(Hliu(i,j)- 0);
        elseif Ntii_liu(i,j) <40
            for n=1:100
                Qliuout(i,j)= Qliuout(i,j)+10*n; %以10为步长逐渐增大出库流量，直至满足保证出力要求
                Vliu(i,j+1)=(Qlongout(i,j)+LONG_LIU(i,j)-Qliuout(i,j))*xishu(j)+Vliu(i,j);
                if Vliu(i,j+1) < 6.223%С��������
                    Vliu(i,j+1) = 6.223;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                elseif Vliu(i,j+1) > 39.93% ����������
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
                Ntii_liu(i,j)= 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%ˮͷ��ʧΪ3m
                if P(i)<0.75
                    if Ntii_liu(i,j)>=40
                        break%����ѭ��
                    end
                else
                    if Ntii_liu(i,j)>=40*0.8%��ˮƵ��Ϊ75%���ϵĿ�ˮ�갴8�۷���
                        break%����ѭ��
                    end
                end
            end
        end
        if j==3|| j==4  %��ɳ�·�
           
            if P(i)<=0.80 && Vlong(i,j)>85 && Vliu(i,j)>18 %�ж��Ƿ�Ϊƫ�ἰ����ˮ�꣬���ж�������ˮ���Ƿ����㹻���ݳ�ɳ  
                Qlongout(i,j) =1350 ;%7����Ѯ����Ͽˮλ�ϵͣ�������Ͽ����С��ɳ������й��ʣ���ɳˮ��������Ͽ����
                Vlong(i,j+1)=Vlong(i,j)-( Qlongout(i,j)-LONG_IN(i,j))*xishu(j);
                if Vlong(i,j+1) < 42.63%С��������
                    Vlong(i,j+1) = 42.63;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j);
                elseif Vlong(i,j+1) > 242.9% ����������
                    Vlong(i,j+1) = 242.9;
                    Qlongout(i,j) = LONG_IN(i,j)+(Vlong(i,j)-Vlong(i,j+1))/xishu(j) ;
                end
                x(j+(i-1)*20)=chz2(LONG_ZV,Vlong(i,j+1));
                Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));
                Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                Ntii_long(i,j) = 128;%��ɳ�ڼ������װ������
                Qqs_long(i,j)=Qlongout(i,j) - 1050;
                Qliuout(i,j) =Q_sediment - LIU_LAN(i,j) ;%Ҫʹ��ɳ������1800-2200֮�䣬
                Vliu(i,j+1)=Vliu(i,j)-( Qliuout(i,j)-Qlongout(i,j)-LONG_LIU(i,j))*xishu(j);%ע�⣺����Ͽˮ����ܵ���������
                if Vliu(i,j+1) < 6.223%С��������
                    Vliu(i,j+1) = 6.223;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                elseif Vliu(i,j+1) > 39.93% ����������
                    Vliu(i,j+1) = 39.93;
                    Qliuout(i,j) = Qlongout(i,j)+LONG_LIU(i,j)+(Vliu(i,j)-Vliu(i,j+1))/xishu(j);
                end
                x(j+20*Y+(i-1)*20)=chz2(LIU_ZV,Vliu(i,j+1));
                Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                Ntii_liu(i,j)=122.5;
                Qqs_liu(i,j)=Qliuout(i,j) -1200;
                f(i)=1;%�ǵ�i���Ƿ��ˮ��ɳ
                k=k+1;%�ǳ�ϵ�е�ɳ��������
            end
        end
        %%%%%%%%%%%%%%���������������ж�%%%%%%%%%%%%
        if j>8 && j<14
            if Qliuout(i,j) >Qmin(j-8) %��������Լ���ж�
                temp1= chz1(LIU_ZV,x(j+20*Y+(i-1)*20));%����Ͽ��ʱ��ĩ����
                temp2= chz1(LIU_ZV,VarMax(j+20*Y+(i-1)*20));%����Ͽ��ʱ�ο�������
                %temp2= 39.93;%����Ͽ��ʱ�ο�������
                temp3=(Qliuout(i,j) -Qmin(j-8))*xishu(j)-(temp2-temp1);%�ж��������Ͽ������������������������ǲ���ˮ������������й�����Ƿ�ᳬ������Ͽ��ʱ��ˮλ����
                if temp3>0%����Ͽ���������޷������ˮ��������˼·��1������Ͽ�治�µ�ˮ������Ͽ���棨��С����Ͽ���⣩��2������һʱ��������Ͽ��ţ����ڿ��ݣ��ڱ�������û�����֣�
                    temp11=chz1(LONG_ZV,x(j+(i-1)*20));%����Ͽ��ʱ�γ�����
                    temp22=chz1(LONG_ZV,VarMax(j-1+(i-1)*20));%����Ͽ��ʱ�ο�������
                    temp33=temp22-temp11;%����Ͽ����Ŀ���
                    if temp33>temp3  %�����㹻���ݿ��Խ��ɶ���ˮ����ͨ����С����Ͽ����������ʵ�֣�
                        Vlong(i,j+1)=Vlong(i,j+1)+temp3;
                        x(j+(i-1)*20)=chz2(LONG_ZV,Vlong(i,j+1));
                        Qlongout(i,j)=Qlongout(i,j)-temp3/xishu(j);
                        Qliuout(i,j) =Qmin(j-8);
                        x(j+20*Y+(i-1)*20)=VarMax(j+20*Y+(i-1)*20);%�������Ͽˮλ�ﵽ����ˮλ
                        Vliu(i,j+1) =chz1(LIU_ZV,x(j+20*Y+(i-1)*20));
                    else%��ʱ����Ͽ��������������Ͽ�Բ�������ȫ���ɶ����ˮ��
                        Vlong(i,j+1)=Vlong(i,j+1)+temp33;%������Ͽ�Ŀ��ݵ������޿��ݣ���������Ͽ����
                        x(j+(i-1)*20)=VarMax(j+(i-1)*20);
                        Qlongout(i,j)=Qlongout(i,j)-temp33/xishu(j);
                        Qliuout(i,j) =Qmin(j-8)+(temp3-temp33)/xishu(j);%����ˮ�ⶼ��������ֻ�ܳ�����������
                        x(j+20*Y+(i-1)*20)=VarMax(j+20*Y+(i-1)*20);
                        Vliu(i,j+1) =chz1(LIU_ZV,x(j+20*Y+(i-1)*20));
                    end
                else
                    Vliu(i,j+1)=Vliu(i,j+1)+(Qliuout(i,j)-Qmin(j-8))*xishu(j);
                    Qliuout(i,j) =Qmin(j-8);
                    x(j+20*Y+(i-1)*20)=chz2(LIU_ZV,Vliu(i,j+1));
                end
                Zlongxia(i,j) = chz2(LONG_ZQ,Qlongout(i,j));%����Ͽ�����������ж�
                Hlong(i,j) =0.5*(x(j+(i-1)*20)+x(j-1+(i-1)*20)) -Zlongxia(i,j);
                Ntii_long(i,j)= 8.6 * (Hlong(i,j)-0) * Qlongout(i,j)/10000;%ˮͷ��ʧ2.5m
                Zliuxia(i,j) = chz2(LIU_ZQ,Qliuout(i,j));%����Ͽ�����������ж�
                Hliu(i,j) = 1/2*(x(j+20*Y+(i-1)*20)+x(j-1+20*Y+(i-1)*20)) - Zliuxia(i,j);
                Ntii_liu(i,j) = 8.6 *(Hliu(i,j)-0)* Qliuout(i,j)/10000;%ˮͷ��ʧΪ3m
            end
        end
        Ntii_laxiwa(i,j)=8.3*205*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%������ˮ��վ�ĳ���
        if Ntii_laxiwa(i,j)>280
            Ntii_laxiwa(i,j)= 280;
        end
        Ntii_nina(i,j)=8*15*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%����ˮ��վ�ĳ���
        if Ntii_nina(i,j)>16
            Ntii_nina(i,j)=16;
        end
        Ntii_lijiaxia(i,j)=8.3*122*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%���Ͽˮ��վ�ĳ���
        if Ntii_lijiaxia(i,j) >160
            Ntii_lijiaxia(i,j) =160;
        end
        Ntii_jishixia(i,j)=8.3*66*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%��ʯϿˮ��վ�ĳ���
        if Ntii_jishixia(i,j) >102
            Ntii_jishixia(i,j) =102;
        end
        Ntii_zhiganglaka(i,j)=8.2*12.5*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%ֱ������ˮ��վ�ĳ���
        if Ntii_zhiganglaka(i,j) >19
            Ntii_zhiganglaka(i,j) =19;
        end
        Ntii_kangyang(i,j)=8.2*18.7*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%����ˮ��վ�ĳ���
        if Ntii_kangyang(i,j) >30
            Ntii_kangyang(i,j) =30;
        end
        Ntii_gongboxia(i,j)=8.3*99.3*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%����Ͽˮ��վ�ĳ���
        if Ntii_gongboxia(i,j) >150
            Ntii_gongboxia(i,j) =150;
        end
        Ntii_suzhi(i,j)=8.3*16*(Qlongout(i,j)+LONG_LIU(i,j))/10000;%��ֻˮ��վ�ĳ���
        if Ntii_suzhi(i,j) >22
            Ntii_suzhi(i,j) =22;
        end
        Ntii_yanguoxia(i,j)=7.9*38*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%�ι�Ͽˮ��վ�ĳ���
        if Ntii_yanguoxia(i,j) >40
            Ntii_yanguoxia(i,j) =40;
        end
        Ntii_bapanxia(i,j)=8.3*18*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%����Ͽˮ��վ�ĳ���
        if Ntii_bapanxia(i,j) >18
            Ntii_bapanxia(i,j) =18;
        end
        Ntii_xiaoxia(i,j)=8.3*13.8*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%СϿˮ��վ�ĳ���
        if Ntii_xiaoxia(i,j) >23
            Ntii_xiaoxia(i,j) =23;
        end
        Ntii_daxia(i,j)=8.3*24*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%��Ͽˮ��վ�ĳ���
        if Ntii_daxia(i,j) >30
            Ntii_daxia(i,j) =30;
        end
        Ntii_qingtongxia(i,j)=8.3*16*(Qliuout(i,j)+LIU_LAN(i,j))/10000;%��ͭϿˮ��վ�ĳ���
        if Ntii_qingtongxia(i,j) >30
            Ntii_qingtongxia(i,j) =30;
        end
        Etii_longliu(i,j)=(Ntii_long(i,j)+ Ntii_liu(i,j)+Ntii_laxiwa(i,j)+Ntii_nina(i,j)+Ntii_lijiaxia(i,j)+ Ntii_zhiganglaka(i,j)+ Ntii_kangyang(i,j)+Ntii_gongboxia(i,j)+Ntii_suzhi(i,j)+Ntii_yanguoxia(i,j)+Ntii_bapanxia(i,j)+Ntii_xiaoxia(i,j)+Ntii_daxia(i,j)+Ntii_qingtongxia(i,j)) * t(j) * 24 * 10^(-4);    %��λΪ��ǧ��ʱ;
        Qliuin(i,j) =Qlongout(i,j)+LONG_LIU(i,j);
        
        % ���¸���һ������ˮλ��ֵ����������ĩˮλ��
        if j==20
            LONG_Z_INI(i+1) = x(j+(i-1)*20);
            LIU_Z_INI(i+1) = x(j+20*Y+(i-1)*20);
        end
    end
    
    %���¿�ʼЭͬ�ȼ���
    %%%%%��ˮĿ��Ĺؼ�������ǹؼ��������������%%%%%
    qshortage1(i,:) = (LAN_unagr(i,1:20)-Qliuout(i,1:20)-LIU_LAN(i,1:20)).*xishu(1:20);%ȫ���ʱ�ι�ҵ������ӵ�����̬��ȱˮ��
    Qshortage1(i,:) = max(qshortage1(i,:),0);%ÿ��ʱ�ε����ݹ�ҵ������ӵ�����̬ȱˮ������m3��������������������ˮ����ȱˮ��ȱˮ���Ϊ0
    water_rate1(i)=length(find( Qshortage1(i,:)==0))/20; %��ˮĿ���й�ҵ��������ˮ��֤��
    d_water_rate1(i)=(water_rate1(i)-0)/(1-0);%��ˮĿ���й�ҵ��������ˮ��֤�ʵ������
    qshortage_agr(i,:) = (LAN(i,[1 2 5 15 16 18])-Qliuout(i,[1 2 5 15 16 18])-LIU_LAN(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18]);%ũҵ�ؼ�ʱ��ȱˮ����5�ϡ�5�С�6�ϡ�7�ϡ�7�С�8�У�
    Qshortage_agr(i,:) = max(qshortage_agr(i,:),0);%ũҵ�ؼ�ʱ�ڸ�ʱ��ȱˮ��
    T_Q_shortage_agr(i)=sum(Qshortage_agr(i,:)); %ũҵ�ؼ�ʱ����ȱˮ��
    d_T_Q_shortage_agr(i)=(26.63-T_Q_shortage_agr(i))/(26.63-0); %ũҵ�ؼ�ʱ����ȱˮ���������, ���ֵΪũҵ�ؼ�������ˮ����40%����25.4�ڷ�(2020ˮƽ��)����26.63�ڷ�(2030ˮƽ��)
    T_Q_shortage1(i)=max(Qshortage_agr(i,:)./((LAN(i,[1 2 5 15 16 18])-LAN_unagr(i,[1 2 5 15 16 18])).*xishu([1 2 5 15 16 18])));%ũҵ�ؼ�ʱ�����ȱˮ���
    d_T_Q_shortage1(i)=(1-T_Q_shortage1(i))/(1-0); %��ˮĿ����ũҵ�ؼ�ʱ�����ȱˮ��ȵ�����ȣ�����0.5
    qshortage2(i,:)=(LAN(i,[3 4 6:9 13 14 17 19 20])-Qliuout(i,[3 4 6:9 13 14 17 19 20])-LIU_LAN(i,[3 4 6:9 13 14 17 19 20])).*xishu([3 4 6:9 13 14 17 19 20]);%��ˮĿ����ũҵ�ǹؼ��ڵĸ�ʱ��ȱˮ��
    Qshortage2(i,:)=max(qshortage2(i,:),0);%��ˮĿ����ũҵ�ǹؼ��ڵĸ�ʱ��ȱˮ��
    water_rate2(i)=length(find( Qshortage2(i,:)==0))/11;%��ˮĿ����ũҵ�ǹؼ��ڹ�ˮ��֤��
    d_water_rate2(i)=(water_rate2(i)-0)/(1-0);%��ˮĿ����ũҵ�ǹؼ��ڹ�ˮ��֤�ʵ�����ȣ���ֵ����Ϊ1������Ϊ0.75
    T_Q_shortage2(i)=sum(Qshortage2(i,:)); %��ˮĿ����ũҵ�ǹؼ��ڵ���ȱˮ��
    d_T_Q_shortage2(i)=(41.56-T_Q_shortage2(i))/(41.56-0); %ũҵ�ǹؼ�ʱ����ȱˮ��������ȣ����ֵΪ�ǹؼ���ũҵ��ˮ��40%����32.696�ڷ�(2020ˮƽ��)����41.56(2030ˮƽ��50%)
    h_water(i)=0.1*d_water_rate1(i)+0.25*d_T_Q_shortage_agr(i)+0.25*d_T_Q_shortage1(i)+0.20*d_water_rate2(i)+0.20*d_T_Q_shortage2(i);%ĳһ�깩ˮ��ϵͳ�����
    %%%%%����Ŀ��Ĺؼ�������ǹؼ��������������%%%%%
    ele_rate1(i)= length(find((Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+Ntii_qingtongxia(i,9:13))>431))/5; %����Ŀ���з����ڷ��籣֤��
    d_ele_rate1(i)=(ele_rate1(i)-0)/(1-0);%����Ŀ���з����ڷ��籣֤�ʵ������
    Ntiji_1(i)=mean(Ntii_long(i,9:13) +Ntii_liu(i,9:13)+Ntii_laxiwa(i,9:13)+Ntii_nina(i,9:13)+Ntii_lijiaxia(i,9:13)+ Ntii_zhiganglaka(i,9:13)+ Ntii_kangyang(i,9:13)+Ntii_gongboxia(i,9:13)+Ntii_suzhi(i,9:13)+Ntii_yanguoxia(i,9:13)+Ntii_bapanxia(i,9:13)+Ntii_xiaoxia(i,9:13)+Ntii_daxia(i,9:13)+Ntii_qingtongxia(i,9:13));%����Ŀ���з������ݼ�ˮ��ƽ������
    d_Ntiji_1(i)=(Ntiji_1(i)-0)/(1164-0);%����Ŀ���з������ݼ�ˮ��ƽ�������������,15��ˮ�����װ��Ϊ1164��ǧ�ߣ���֤����֮��Ϊ431��ǧ��
    ele_rate2(i)= length(find((Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+ Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]))>431))/15; %����Ŀ���зǷ����ڵķ��籣֤��
    d_ele_rate2(i)=(ele_rate2(i)-0)/(1-0);%����Ŀ���зǷ����ڷ��籣֤�ʵ������
    Ntiji_2(i)=mean(Ntii_long(i,[1:8 14:20]) +Ntii_liu(i,[1:8 14:20])+Ntii_laxiwa(i,[1:8 14:20])+Ntii_nina(i,[1:8 14:20])+Ntii_lijiaxia(i,[1:8 14:20])+ Ntii_zhiganglaka(i,[1:8 14:20])+ Ntii_kangyang(i,[1:8 14:20])+Ntii_gongboxia(i,[1:8 14:20])+Ntii_suzhi(i,[1:8 14:20])+Ntii_yanguoxia(i,[1:8 14:20])+Ntii_bapanxia(i,[1:8 14:20])+Ntii_xiaoxia(i,[1:8 14:20])+Ntii_daxia(i,[1:8 14:20])+Ntii_qingtongxia(i,[1:8 14:20]));%����Ŀ���зǷ������ݼ�ˮ��ƽ������
    d_Ntiji_2(i)=(Ntiji_2(i)-0)/(1164-0);%����Ŀ���зǷ������ݼ�ˮ��ƽ�������������
    h_ele(i)=0.2*d_ele_rate1(i)+0.2*d_Ntiji_1(i)+0.3* d_ele_rate2(i)+0.3* d_Ntiji_2(i);%ĳһ�귢����ϵͳ�����
    %%%%%��ɳĿ��Ĺؼ�������ǹؼ��������������%%%%%
    if f(i)==1
        if Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) %���жϵ����Ƿ�ʱ��3��4����ɳ
            Q_sed(i)=mean(Qliuout(i,[3 4])+LIU_LAN(i,[3 4]));%��ɳʱ�ڵ�ƽ������
            t_sed(i)=t(3)+t(4);%��ɳ��ʱ������Ѯ
        elseif Qliuout(i,3)>=Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)<Q_sediment-LIU_LAN(i,4) %ֻ��ʱ��3��ɳ
            Q_sed(i)=Qliuout(i,3)+LIU_LAN(i,3);
            t_sed(i)=t(3);%��ɳ��ʱ��һ��Ѯ
        elseif Qliuout(i,3)<Q_sediment-LIU_LAN(i,3) && Qliuout(i,4)>=Q_sediment-LIU_LAN(i,4) %ֻ��ʱ��4��ɳ
            Q_sed(i)=Qliuout(i,4)+LIU_LAN(i,4);
            t_sed(i)=t(4);%��ɳ��ʱ��һ��Ѯ
        end
        
        d_Q_sed(i)=(Q_sed(i)-1800)/(2200-1800);%��ɳ��������� 
        d_t_sed(i)=(t_sed(i)-10)/(30-10);%��ɳ��ʱ�������
        h_sed(i)=0.6*d_Q_sed(i)+0.4*d_t_sed(i);%ĳһ����ɳ��ϵͳ�����
    end
    %%%%%��̬Ŀ��Ĺؼ�������ǹؼ��������������%%%%%
    qshortage_eco(i,:) = (Q_eco(i,:)-Qliuout(i,:)-LIU_LAN(i,:));
    Qshortage_eco(i,:) = max(qshortage_eco(i,:),0);%��̬Ŀ����ÿ��ʱ�ε���̬ȱˮ����
    eco_rate(i)=numel(Qshortage_eco(i,:),Qshortage_eco(i,:)==0)/20; %��̬Ŀ������̬��ˮ��֤��
    d_eco_rate(i)=(eco_rate(i)-0.75)/(1-0.75);%��̬Ŀ������̬��֤�ʵ������
    if P(i)<=0.75
        L_eco(i)=length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>900));%ͳ��5��6�������в��������ʱ����
    else
        L_eco(i)=length(find((Qliuout(i,15:20)+LIU_LAN(i,15:20))>400));%ͳ��5��6�������в��������ʱ����,��ˮ����̬����400
    end
    if L_eco(i)>0
        d_L_eco1(i)=1;%һ����̬����������
        d_L_eco(i)=(L_eco(i)-1-0)/(5-0);%��̬Ŀ���ж����̬����������
    else d_L_eco1(i)=0;
        d_L_eco(i)=0;
    end
    h_eco(i)=0.4* d_eco_rate(i)+0.3*d_L_eco1(i)+0.3* d_L_eco(i);%ĳһ����̬��ϵͳ�����
    %%%%%%%%%%%%%��ͳ��Ŀ��ģ�͵�Ŀ�꺯��ֵ���%%%%%%%%%%%%%%%%%%
    qshortage(i,:) = (LAN(i,:)-Qliuout(i,:)-LIU_LAN(i,:)).*xishu(1:20);%ȫ���ʱ������ȱˮ��
    Qshortage(i,:) = max(qshortage(i,:),0);%ȫ���ʱ������ȱˮ��
    T_Q_shortage(i)=sum(Qshortage(i,:));%ȫ��������ȱˮ��(��m3)
    E_tiji(i)=sum(Etii_longliu(i,:));%ȫ���ܷ���������kwh��
    W_sed(i)=Q_sed(i)*t_sed(i)*24*3600/100000000;%ȫ������ɳˮ��(��m3)
end

H_water=sum(h_water)/Y;%��ˮ��ϵͳ�Ķ�����������
H_ele=sum( h_ele)/Y;%�󷢵���ϵͳ�Ķ�����������
H_sed=0.8*sum(h_sed)/k+0.2*((k/Y-0.1)/(0.3-0.1));%����ɳ��ϵͳ�Ķ�����������,��ɳ�������ȵ�ƽ��ֵ�볤ϵ�е�ɳƵ������ȵļ�Ȩ���
H_eco=sum(h_eco)/Y;%����̬��ϵͳ�Ķ�����������
%     H_tiji=0.3*H_water+0.3*H_ele+0.3* H_sed+0.1*H_eco;
H_tiji=geomean(max(0, [H_water,H_ele, H_sed, H_eco]));%���ݼ�ˮ�����ϵͳ����Эͬ�ȣ�����ƽ����
f2=(-1)*H_tiji;%��Ѱ�����ֵת��ΪѰ����Сֵ
W_shortage=sum(T_Q_shortage)/Y;
f1=W_shortage;

%% *************************************������ָ�����******************************************
%1.����Ͽ������Ͽ���ˮλ���
Zrr2_long = max(diff(x(1:V/2)), [], 'all');  % �������ˮλ�仯����
Zrr2_liu = max(diff(x(V/2+1:V)), [], 'all');  % �������ˮλ�仯����


%2.����Ͽ������Ͽ����ʿ����ʼ���
m_long_Vrate=sum(Vlong <= 42.73, 'all')/(20*Y);%����Ͽ�����,���ָ�������0.01������Ϊ53.43
m_liu_Vrate=sum(Vliu <= 6.323, 'all')/(20*Y);%����Ͽ�����
n_long_Vrate=sum(Vlong >= 242.8, 'all')/(20*Y); %����Ͽ������
n_liu_Vrate=sum(Vliu <= 39.83, 'all')/(20*Y); %����Ͽ������

%3.��ɳƽ��������,�����ɳ��������ݳ��������
Q_sed_m=0; %��ɳ��������1800�Ĵ���
for i=1:Y
    if Q_sed(i)>=1800
        Q_sed_m=Q_sed_m+1;
    else
        Q_sed_m=Q_sed_m;
    end
end
Q_sed_bizhi=Q_sed_m/Y;%�����ɳ��������̶�

% W_sed(i)=Q_sed(i)*t_sed(i)*24*3600/100000000;%ȫ������ɳˮ��(��m3)
W_sed4_year = zeros(1, Y);  % 预初始化，防止来沙条件不满足时变量不存在
anytrigger_year = false(1, Y);  % 预初始化
for i = 1:Y
    Qsed4 = Qliuout(i,3:4) + LIU_LAN(i,3:4);
    % ��ÿ��ʱ���ж��Ƿ������ɳ����
    for j = 1:2  % ����Qsed4������ʱ�Σ�����ѭ������
        if Qsed4(j) >= Q_sediment  % �����jʱ�ε�������������
            % �����ʱ�εĳ�ɳˮ��
            W_sed4_year(i) = Qsed4(j) * t_sed(i) * 24 * 3600 / 100000000;
            anytrigger_year(i) = true;  % ��Ǹ��괥����ɳ
            break;  % һ���ҵ�����������ʱ�Σ�����ѭ���������ټ��㲻�����ʱ��
        end
    end
end
AVW_sed4=mean(W_sed4_year);%�����ɳˮ��ˮ�����



%4.���귢�籣֤�ʣ���20*Y��ʱ���㣬�������㣬ʱ�γ����ﵽ��֤������
%����Ͽ���귢�籣֤��58.7
ele_long_time = numel(Ntii_long(Ntii_long>0.90*58.7));
dn_elerate_long = ele_long_time/(20*Y);
%����Ͽ���귢�籣֤��40
ele_liu_time = numel(Ntii_liu(Ntii_liu>40));
dn_elerate_liu = ele_liu_time/(20*Y);

%5.����ƽ����ˮ��
Qqs_long_rata = sum(Qqs_long,'all')/sum(Qlongout,'all');%����Ͽ����ƽ����ˮ��
Qqs_liu_rata  = sum(Qqs_liu,'all')/sum(Qliuout,'all');%����Ͽ����ƽ����ˮ��

%6.��С������
C = [Ntiji_1; Ntiji_2];  %�ϲ�����ʱ��ƽ������
min_Ntiji= min(C, [], 'all');  %�ҳ��ϲ����ȫ����Сֵ,�ݼ�ˮ��Ⱥƽ����С����


%����������Ͽ�����й����R16
MAXQ_LONG= max(max(Qlongout(:, 1:8)));


%����������Ͽ�����й����R17
MAXQ_LIU= max(max(Qliuout(:, 1:8)));


%����Ͽˮ�ⰲȫ��������ƫ���9��13
f_ice(i,:) = (Qliuout(i,9:13)-Qmin)./ Qmin;
Q_ice1 = mean(f_ice(:), 'all');

%7.������ˮ��֤��
% ��ҵ��ˮָ��
dn_water_rate1= numel(Qshortage1( Qshortage1==0)) / (20*Y); %���깤ҵ������ˮ��֤��
max_Qshortage1=max(Qshortage1(:))/411;%��ҵ�������ȱˮ��

% ũҵ��ˮָ��
agr_Qshortage= zeros(Y, 20); % ��ʼ��Ŀ�����Ϊȫ�����
columns1 = [1, 2, 5, 15, 16, 18];% ũҵ�ؼ�����ռʱ��
agr_Qshortage(:, columns1) = Qshortage_agr;% ũҵ�ؼ��ڸ�ʱ��ȱˮ��
columns2 = [3, 4, 6, 7, 8, 9, 13, 14, 17, 19, 20];% ũҵ�ǹؼ�����ռʱ��
agr_Qshortage(:, columns2) = Qshortage2;% ũҵ�ǹؼ��ڸ�ʱ��ȱˮ��

dn_water_rate2= (numel(agr_Qshortage( agr_Qshortage==0))/(20*Y));%ũҵ��ˮ��֤��

agr_demand = [817,817,817,577,577,577,236,346,297,0,0,0,162,501,847,847,847,935,935,935];%һ���ڸ�ʱ�ε�ũҵ��ˮ��
agr_demand_all=repmat(agr_demand, Y, 1);%54�����������ڵ�ũҵ��ˮ��
agr_Qshortage_rate = agr_Qshortage./agr_demand_all;
max_Qshortage2=max(agr_Qshortage_rate(:));%ũҵ���ȱˮ��

% ��̬��ˮָ��
dn_eco_rate= numel(Qshortage_eco( Qshortage_eco==0)) / (20*Y); %������̬��ˮ��֤��
max_Qshortage3=max(Qshortage_eco(:))/350;%��̬���ȱˮ��

evaluating_index = [Zrr2_long Zrr2_liu m_long_Vrate m_liu_Vrate n_long_Vrate n_liu_Vrate Q_sed_bizhi AVW_sed4 dn_elerate_long dn_elerate_liu  Qqs_long_rata Qqs_liu_rata min_Ntiji MAXQ_LONG MAXQ_LIU Q_ice1 dn_water_rate1 max_Qshortage1 dn_water_rate2 max_Qshortage2 dn_eco_rate max_Qshortage3];


if M == 2
    % Ŀ��1: ���ݶ�����ȱˮ����С (��m3)
    f_obj(1) = f1;
    % Ŀ��2: �ݼ�ˮ��վȺ��������������kWh��
    f_obj(2) = -mean(E_tiji);  % ��-��ͭϿ֮���ȫ���ݼ�
elseif M == 3
    % Ŀ��1: ���ݶ�����ȱˮ����С (��m3)
    f_obj(1) = f1;
    % Ŀ��2: �ݼ�ˮ��վȺ��������������kWh��
    f_obj(2) = -mean(E_tiji);  % ��-��ͭϿ֮���ȫ���ݼ�
    % Ŀ��3: �ݼ�����ϵͳ��Эͬ�����
    f_obj(3) = f2;
end
X_F = [X_F, f_obj];

% ���������
results = struct();
results.individual = x;
results.objectives = abs(f_obj);
results.evaluating = evaluating_index;
% ����Ͽˮ����Ƚ��
results.Long.V = Vlong; % ����
results.Long.Qin = LONG_IN;  % ��ˮ����
results.Long.Qout = Qlongout;  % ��й����
results.Long.Qqs_ = Qqs_long;  % ��ˮ����
results.Long.Curve_ZV = LONG_ZV;  % ˮ��ˮλ-���ݹ�ϵ����
results.Long.Curve_ZQ = LONG_ZQ;  % ˮ��վβˮλ-����������ϵ����

% ����Ͽˮ����Ƚ��
results.Liu.V = Vliu; % ����
results.Liu.Qin = Qliuin;  % ��ˮ����
results.Liu.Qout = Qliuout;  % ��й����
results.Liu.Qqs = Qqs_liu;  % ��ˮ����
results.Liu.Curve_ZV = LIU_ZV;  % ˮ��ˮλ-���ݹ�ϵ����
results.Liu.Curve_ZQ = LIU_ZQ;  % ˮ��վβˮλ-����������ϵ����

% ���ݶ���
results.Lan.Water_demand = LAN;  % ���ݶ�����ˮ����
results.Lan.Q_ecology = Q_eco;  % ���ݶ�����̬����Ҫ��
results.Lan.Q_sediment = Q_sediment;  % ���ݶ����ɳ����Ҫ��

% ������ˮ
results.Qin_LONG_LIU = LONG_LIU;  % ��-��������ˮ����
results.Qin_LIU_LAN = LIU_LAN;  % ��-��������ˮ����

% ˮ��վ��������λΪ��ǧ��ʱ������վƴ����Ӧ�ĺ������������������ע�ͣ�
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

% ---- Decision-analysis extras: targets / water_usage / coordination ----
xishu_mat = repmat(xishu, Y, 1);
supply_lan = Qliuout + LIU_LAN;   % Lanzhou section water supply (Y x 20)

% Coordination degree (annual mean)
results.coordination.h_water = mean(h_water);
results.coordination.h_ele = mean(h_ele);
results.coordination.h_sed = mean(h_sed);
results.coordination.h_eco = mean(h_eco);

% Target satisfaction rates (0~100)
t_gen  = mean([dn_elerate_long, dn_elerate_liu]) * 100;
t_eco  = max(min(dn_eco_rate, 1), 0) * 100;
t_agr  = dn_water_rate2 * 100;
t_life = dn_water_rate1 * 100;
t_qqs  = max(0, 1 - mean([Qqs_long_rata, Qqs_liu_rata])) * 100;
t_sed  = Q_sed_bizhi * 100;
results.targets.power      = min(round(t_gen, 1), 100);
results.targets.ecology    = round(t_eco, 1);
results.targets.irrigation = min(round(t_agr, 1), 100);
results.targets.domestic   = min(round(t_life, 1), 100);
results.targets.spill      = round(t_qqs, 1);
results.targets.sediment   = min(round(t_sed, 1), 100);

% Water usage by category (1e8 m3)
W_qqs  = sum((Qqs_long + Qqs_liu) .* xishu_mat, 'all');
W_sedt = sum(W_sed);
W_ecow = sum(min(Q_eco, supply_lan) .* xishu_mat, 'all');
d_agr  = max(LAN - LAN_unagr, 0);
W_agr  = sum(min(d_agr, max(supply_lan - LAN_unagr, 0)) .* xishu_mat, 'all');
W_life = sum(min(LAN_unagr, supply_lan) .* xishu_mat, 'all');
W_gen  = sum((Qlongout - Qqs_long) .* xishu_mat, 'all') + sum((Qliuout - Qqs_liu) .* xishu_mat, 'all');
results.water_usage.power      = round(W_gen, 2);
results.water_usage.ecology    = round(W_ecow, 2);
results.water_usage.irrigation = round(W_agr, 2);
results.water_usage.domestic   = round(W_life, 2);
results.water_usage.spill      = round(W_qqs, 2);
results.water_usage.sediment   = round(W_sedt, 2);
end