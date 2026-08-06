%% 加载数据
clc
load_data('data.xlsx','全无')

%% 加载2013到2014年数据
% clc
% Copy_of_load_data("./data.xlsx","全无")

%% 运行nsga_2主函数
nsga_2_para(15, 20, 2, 1800.0, 0.9)

%% 运行paem主函数
% 数据和运行分离
% out = PAEM_para(15, 20, 50, 2, 1800.0, 0.9)