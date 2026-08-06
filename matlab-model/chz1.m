function [y,flag]=chz1(A,x)
%二维线性插值函数，A为二维插值矩阵，x为待插值自变量，y为待插值因变量，flag指示是否为插值
%若flag=1，则插值成功，若flag=0，则插值超出给定范围
m=size(A);
r=m(1);%A的行数
flag=1;
if x<A(1,1)
    y=A(1,2);
    flag=0;
else if x>A(r,1)
        y=A(r,2);
        flag=0;
    else 
        for i=1:(r-1)
            if A(i,1)<=x&&x<=A(i+1,1)
               y=A(i,2)+(A(i+1,2)-A(i,2))/(A(i+1,1)-A(i,1))*(x-A(i,1));
            end
        end
    end
end