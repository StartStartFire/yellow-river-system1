import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import json
from datetime import datetime
from tkinter import filedialog, Tk
from data_processing import *
from interpolationReservoir import *
from input_Opreation_01 import floodProcess_zq, floodProcess_hq, floodProcess_mh, floodProcess_xt, floodProcess_tnh,\
    Parameters_LYX, Parameters_LXW, Parameters_LJ, Parameters_GBX, Parameters_JSX, Parameters_LJX, Parameters_HSX

# ---------- 服务化回调钩子（唯一侵入点，仿 MATLAB http_callback_push.m） ----------
# 仅在设置环境变量时启用；交互式运行不受影响。
import urllib.request as _urlreq
RIVER_CB_URL = os.environ.get("RIVER_CB_URL", "")
RIVER_JOB_ID = os.environ.get("RIVER_JOB_ID", "")


def _cb_push(data_type, data):
    """向 Web 服务 /cb 端点推送进度/过程数据。失败静默降级，不影响模型。"""
    if not RIVER_CB_URL:
        return
    try:
        payload = {"type": data_type, "data": data}
        req = _urlreq.Request(RIVER_CB_URL, data=json.dumps(payload).encode("utf-8"),
                              headers={"Content-Type": "application/json"}, method="POST")
        _urlreq.urlopen(req, timeout=1)
    except Exception:
        pass

'''
# 输入：
# 1.唐乃亥场次洪水过程/唐乃亥流量逐时段输入
# 2.区间来水过程(各支流汇入)
# 3.区间引水过程(农业引水、生活工业引水======排沙停灌)
# 4.塑造断面流量过程几天(流量阈值、流量持续日期)
# 5.各水库初始状态(初始水位)

# 输出：
# 1.符合控制断面的下泄流量过程
# 2.各水库的发电过程
# 3.各水库水位变化过程
# 4.各水库弃水过程
==============================
场景设置
1.龙-拉-李-公-积-刘
2.龙-拉-李-公-积-刘-黑
==============================
1.根据唐乃亥历史场次洪水的输入，进行科学研究
2.逐时段模拟，进行实际应用
'''
## 输入
StartTime = '2021-09-01'
StartTime = datetime.strptime(StartTime, '%Y-%m-%d')
number =  20                                             # 排沙流量持续日期，d
SDF_lz = 1800                                            # 兰州断面排沙流量阈值(Sediment discharge flow threshold)                                         # 下河沿面排沙流量阈值
Q_lz = np.full(number,SDF_lz)

## 数据预处理
# 模拟入库
Q_in_LYX = np.zeros(number)
Q_in_LXW = np.zeros(number)
Q_in_LJ = np.zeros(number)
Q_in_GBX = np.zeros(number)
Q_in_JSX = np.zeros(number)
Q_in_LJX = np.zeros(number)
Q_in_HSX = np.zeros(number)
# 模拟出库
Q_out_LYX = np.zeros(number)
Q_out_LXW = np.zeros(number)
Q_out_LJ = np.zeros(number)
Q_out_GBX = np.zeros(number)
Q_out_JSX = np.zeros(number)
Q_out_LJX = np.zeros(number)
Q_out_HSX = np.zeros(number)
Q_out_LJXPeak = np.zeros(number)  # 刘家峡凑峰时多下泄的流量

# 输入洪水频率（100年、50年、10年、2年）若为输入洪水频率则使用默认值2年
flood_frequency = os.environ.get("RIVER_FLOOD_FREQ", "") or (input("请输入洪水频率（100年/50年/10年/5年/2年）：") or "2年")

# 初始水位Z_ini（若有水库初始位置，则用户手动输入，若无，则采用默认值）
idex = os.environ.get("RIVER_Z_INI", "") or (input("是否有各水库初始位置(Yes/No)：") or "默认值")
if idex.strip().lower() == 'yes':
    # 用户输入各水库初始位置
    Z_ini_LYX = float(input("龙羊峡初始坝前水位(m)："))
    Z_ini_LXW = float(input("拉西瓦初始坝前水位(m)："))
    Z_ini_LJ = float(input("李家峡初始坝前水位(m)："))
    Z_ini_GBX = float(input("公伯峡初始坝前水位(m)："))
    Z_ini_JSX = float(input("积石峡初始坝前水位(m)："))
    Z_ini_LJX = float(input("刘家峡初始坝前水位(m)："))
    Z_ini_HSX = float(input("黑山峡初始坝前水位(m)："))
else:
    # 使用默认值
    Z_ini_LYX = 2594    # 2024年项目年会黄河公司给出汛前龙羊峡水位
    Z_ini_LXW = 2452     # 防洪限制水位
    Z_ini_LJ = 2180   # 正常蓄水位
    Z_ini_GBX = 2005  # 正常蓄水位
    Z_ini_JSX = 1854    # 防洪限制水位
    Z_ini_LJX = 1735     # 正常蓄水位
    Z_ini_HSX = 4.5         # 未建

'''水电站出力计算方法：
=============================================
1.根据水库合计下泄流量，确定下游水位
2.上下游水位确定发电水头
3.发电流量和发电水头，查表确定单台机组出力n
4.N = number_PowerStation*n
=============================================
'''
# 各水电站装机容量(installed capacity [kw])
number_PowerStation = {
	'LYX': 4,   # 每台装机容量32万kw    128
	'LXW': 6,   # 每台装机容量70万kw    420
	'LJ': 4,    # 每台装机容量40万kw    160
	'GBX': 5,   # 每台装机容量30万kw    150
	'JSX': 3,   # 每台装机容量34万kw    102
	'LJX': 5,   # 装机容量分别为22.5万kw（3）、25万kw、30万kw，只有30万kw机组的出力曲线   122.5
	'HSX': 1,   # 未建，规划总装机260万kw
}
# 最大过机流量(Maximum Throughflow [m3/s])
Q_MaxTroMachine = {
    'LYX': 1192,    # 298*4
    'LXW': 2280,    #380*6
    'LJ': 1508,     # 377*4
    'GBX': 1694,    # 338.7*5
    'JSX': 1729,    # 576.2*3    
    'LJX': 1350, # 258（22.5MW）/348（30.0 MW）
    'HSX': 1,
}

'''水电站(Hydropower Stations)'''
# 电站出力(Power output [MW])
N_LYX = np.zeros((number,1))
N_LXW = np.zeros((number,1))
N_LJ = np.zeros((number,1))
N_GBX = np.zeros((number,1))
N_JSX = np.zeros((number,1))
N_LJX = np.zeros((number,1))
N_HSX = np.zeros((number,1))
# 电站引水流量
Q_ele_LYX = np.zeros((number,1))
Q_ele_LXW = np.zeros((number,1))
Q_ele_LJ = np.zeros((number,1))
Q_ele_GBX = np.zeros((number,1))
Q_ele_JSX = np.zeros((number,1))
Q_ele_LJX = np.zeros((number,1))
Q_ele_HSX = np.zeros((number,1))
# 水库上游水位
Zup_LYX = np.zeros((number,1))
Zup_LXW = np.zeros((number,1))
Zup_LJ = np.zeros((number,1))
Zup_GBX = np.zeros((number,1))
Zup_JSX = np.zeros((number,1))
Zup_LJX = np.zeros((number,1))
Zup_HSX = np.zeros((number,1))
# 水库下游水位
Zdown_LYX = np.zeros((number,1))
Zdown_LXW = np.zeros((number,1))
Zdown_LJ = np.zeros((number,1))
Zdown_GBX = np.zeros((number,1))
Zdown_JSX = np.zeros((number,1))
Zdown_LJX = np.zeros((number,1))
Zdown_HSX = np.zeros((number,1))
# 发电水头
H_ele_LYX = np.zeros((number,1))
H_ele_LXW = np.zeros((number,1))
H_ele_LJ = np.zeros((number,1))
H_ele_GBX = np.zeros((number,1))
H_ele_JSX = np.zeros((number,1))
H_ele_LJX = np.zeros((number,1))
H_ele_HSX = np.zeros((number,1))
# 弃水
Q_ele_abandoned_LYX = np.zeros((number,1))
Q_ele_abandoned_LXW = np.zeros((number,1))
Q_ele_abandoned_LJ = np.zeros((number,1))
Q_ele_abandoned_GBX = np.zeros((number,1))
Q_ele_abandoned_JSX = np.zeros((number,1))
Q_ele_abandoned_LJX = np.zeros((number,1))
Q_ele_abandoned_HSX = np.zeros((number,1))
# 水库水量变化
W_LYX = np.zeros((number,1))
W_LXW = np.zeros((number,1))
W_LJ = np.zeros((number,1))
W_GBX = np.zeros((number,1))
W_JSX = np.zeros((number,1))
W_LJX = np.zeros((number,1))
W_HSX = np.zeros((number,1))
# 各水库发电的关键参数
#保证出力
Row_warrantedOutput_LYX = Parameters_LYX['装机容量'][Parameters_LYX['装机容量']['机组参数'] == '保证出力'].index[0]
Row_warrantedOutput_LXW = Parameters_LXW['装机容量'][Parameters_LXW['装机容量']['机组参数'] == '保证出力'].index[0]
Row_warrantedOutput_LJ = Parameters_LJ['装机容量'][Parameters_LJ['装机容量']['机组参数'] == '保证出力'].index[0]
Row_warrantedOutput_GBX = Parameters_GBX['装机容量'][Parameters_GBX['装机容量']['机组参数'] == '保证出力'].index[0]
Row_warrantedOutput_JSX = Parameters_JSX['装机容量'][Parameters_JSX['装机容量']['机组参数'] == '保证出力'].index[0]
Row_warrantedOutput_LJX = Parameters_LJX['装机容量'][Parameters_LJX['装机容量']['机组参数'] == '保证出力'].index[0]
Q_warrantedOutput_LYX = Parameters_LYX['装机容量'].loc[Row_warrantedOutput_LYX,'参数']
Q_warrantedOutput_LXW = Parameters_LXW['装机容量'].loc[Row_warrantedOutput_LXW,'参数']
Q_warrantedOutput_LJ = Parameters_LJ['装机容量'].loc[Row_warrantedOutput_LJ,'参数']
Q_warrantedOutput_GBX = Parameters_GBX['装机容量'].loc[Row_warrantedOutput_GBX,'参数']
Q_warrantedOutput_JSX = Parameters_JSX['装机容量'].loc[Row_warrantedOutput_JSX,'参数']
Q_warrantedOutput_LJX = Parameters_LJX['装机容量'].loc[Row_warrantedOutput_LJX,'参数']
#死水位
Row_Zdead_LYX = Parameters_LYX['水库水位'][Parameters_LYX['水库水位']['水库特征水位'] == '死水位'].index[0]
Row_Zdead_LXW = Parameters_LXW['水库水位'][Parameters_LXW['水库水位']['水库特征水位'] == '死水位'].index[0]
Row_Zdead_LJ = Parameters_LJ['水库水位'][Parameters_LJ['水库水位']['水库特征水位'] == '死水位'].index[0]
Row_Zdead_GBX = Parameters_GBX['水库水位'][Parameters_GBX['水库水位']['水库特征水位'] == '死水位'].index[0]
Row_Zdead_JSX = Parameters_JSX['水库水位'][Parameters_JSX['水库水位']['水库特征水位'] == '死水位'].index[0]
Row_Zdead_LJX = Parameters_LJX['水库水位'][Parameters_LJX['水库水位']['水库特征水位'] == '死水位'].index[0]
Zdead_LYX = Parameters_LYX['水库水位'].loc[Row_Zdead_LYX,'高程']
Zdead_LXW = Parameters_LXW['水库水位'].loc[Row_Zdead_LXW,'高程']
Zdead_LJ = Parameters_LJ['水库水位'].loc[Row_Zdead_LJ,'高程']
Zdead_GBX = Parameters_GBX['水库水位'].loc[Row_Zdead_GBX,'高程']
Zdead_JSX = Parameters_JSX['水库水位'].loc[Row_Zdead_JSX,'高程']
Zdead_LJX = Parameters_LJX['水库水位'].loc[Row_Zdead_LJX,'高程']
#正常蓄水位
Row_Zfloodcontrol_LYX = Parameters_LYX['水库水位'][Parameters_LYX['水库水位']['水库特征水位'] == '防洪限制水位'].index[0]
Row_Zfloodcontrol_LXW = Parameters_LXW['水库水位'][Parameters_LXW['水库水位']['水库特征水位'] == '防洪限制水位'].index[0]
Row_Zfloodcontrol_LJ = Parameters_LJ['水库水位'][Parameters_LJ['水库水位']['水库特征水位'] == '防洪限制水位'].index[0]
Row_Zfloodcontrol_GBX = Parameters_GBX['水库水位'][Parameters_GBX['水库水位']['水库特征水位'] == '正常蓄水位'].index[0]
Row_Zfloodcontrol_JSX = Parameters_JSX['水库水位'][Parameters_JSX['水库水位']['水库特征水位'] == '防洪限制水位'].index[0]
Row_Zfloodcontrol_LJX = Parameters_LJX['水库水位'][Parameters_LJX['水库水位']['水库特征水位'] == '防洪限制水位'].index[0]
Zfloodcontrol_LYX = Parameters_LYX['水库水位'].loc[Row_Zfloodcontrol_LYX,'高程']
Zfloodcontrol_LXW = Parameters_LXW['水库水位'].loc[Row_Zfloodcontrol_LXW,'高程']
Zfloodcontrol_LJ = Parameters_LJ['水库水位'].loc[Row_Zfloodcontrol_LJ,'高程']
Zfloodcontrol_GBX = Parameters_GBX['水库水位'].loc[Row_Zfloodcontrol_GBX,'高程']
Zfloodcontrol_JSX = Parameters_JSX['水库水位'].loc[Row_Zfloodcontrol_JSX,'高程']
Zfloodcontrol_LJX = Parameters_LJX['水库水位'].loc[Row_Zfloodcontrol_LJX,'高程']
# 设计洪水位
Row_Zdesignflood_LYX = Parameters_LYX['水库水位'][Parameters_LYX['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Row_Zdesignflood_LXW = Parameters_LXW['水库水位'][Parameters_LXW['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Row_Zdesignflood_LJ = Parameters_LJ['水库水位'][Parameters_LJ['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Row_Zdesignflood_GBX = Parameters_GBX['水库水位'][Parameters_GBX['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Row_Zdesignflood_JSX = Parameters_JSX['水库水位'][Parameters_JSX['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Row_Zdesignflood_LJX = Parameters_LJX['水库水位'][Parameters_LJX['水库水位']['水库特征水位'] == '设计洪水位'].index[0]
Zdesignflood_LYX = Parameters_LYX['水库水位'].loc[Row_Zdesignflood_LYX,'高程']
Zdesignflood_LXW = Parameters_LXW['水库水位'].loc[Row_Zdesignflood_LXW,'高程']
Zdesignflood_LJ = Parameters_LJ['水库水位'].loc[Row_Zdesignflood_LJ,'高程']
Zdesignflood_GBX = Parameters_GBX['水库水位'].loc[Row_Zdesignflood_GBX,'高程']
Zdesignflood_JSX = Parameters_JSX['水库水位'].loc[Row_Zdesignflood_JSX,'高程']
Zdesignflood_LJX = Parameters_LJX['水库水位'].loc[Row_Zdesignflood_LJX,'高程']
# 水库群库容变化量
Qd = np.zeros((number,1))
# 各区间滞时
tdelay_tnh_LYX = np.zeros((number,1))
tdelay_LYX_LXW = np.zeros((number,1))
tdelay_LXW_LJ = np.zeros((number,1))
tdelay_LJ_GBX = np.zeros((number,1))
tdelay_GBX_JSX = np.zeros((number,1))
tdelay_JSX_LJX = np.zeros((number,1))
tdelay_zq_LJX = np.zeros((number,1))
tdelay_hq_LJX = np.zeros((number,1))
tdelay_LJX_lz = np.zeros((number,1))
tdelay_xt_lz = np.zeros((number,1))
tdelay_mh_lz = np.zeros((number,1))
tdelay_lz_HSX = np.zeros((number,1))
tdelay_jy_HSX = np.zeros((number,1))
tdelay_HSX_xhy = np.zeros((number,1))
# 各区间损失
Qloss_tnh_LYX = np.full((number, 1), 0.01)
Qloss_LYX_LXW = np.full((number, 1), 0.02)
Qloss_LXW_LJ = np.full((number, 1), 0.03)
Qloss_LJ_GBX = np.full((number, 1), 0.03)
Qloss_GBX_JSX = np.full((number, 1), 0.02)
Qloss_JSX_LJX = np.full((number, 1), 0.02)
Qloss_zq_LJX = np.full((number, 1), 0.01)
Qloss_hq_LJX = np.full((number, 1), 0.01)
Qloss_LJX_lz = np.full((number, 1), 0.03)
Qloss_xt_lz = np.full((number, 1), 0.02)
Qloss_mh_lz = np.full((number, 1), 0.02)
Qloss_lz_HSX = np.full((number, 1), 0.01)
Qloss_jy_HSX = np.full((number, 1), 0.01)
Qloss_HSX_xhy = np.full((number, 1), 0.01)


def run_real_time_scheduling(use_real_time_scheduling1=True):
    global Q_out_LYX, Q_out_LXW, Q_out_LJ, Q_out_GBX, Q_out_JSX, Q_out_LJX
    global Zup_LYX, Zup_LXW, Zup_LJ, Zup_GBX, Zup_JSX, Zup_LJX
    global N_LYX, N_LXW, N_LJ, N_GBX, N_JSX, N_LJX
    global Q_ele_abandoned_LYX, Q_ele_abandoned_LXW, Q_ele_abandoned_LJ, Q_ele_abandoned_GBX, Q_ele_abandoned_JSX, Q_ele_abandoned_LJX, Q_in
    # 总弃水量

    # 初始化变量
    Q_in = np.zeros((number, 1))
    N_LJX = np.zeros(number)
    N_JSX = np.zeros(number)
    N_GBX = np.zeros(number)
    N_LJ = np.zeros(number)
    N_LXW = np.zeros(number)
    N_LYX = np.zeros(number)

    # 当需要的下泄流量大于最大过机流量时，按最大过机流量下泄，此时下游需要补充的流量
    Q_LYXdownstream = np.zeros(number) 
    Q_LXWdownstream = np.zeros(number)
    Q_LJdownstream = np.zeros(number)
    Q_GBXdownstream = np.zeros(number)
    Q_JSXdownstream = np.zeros(number)

    Q_ele_abandoned_LYX = np.zeros(number)
    Q_ele_abandoned_LXW = np.zeros(number)
    Q_ele_abandoned_LJ = np.zeros(number)
    Q_ele_abandoned_GBX = np.zeros(number)
    Q_ele_abandoned_JSX = np.zeros(number)
    Q_ele_abandoned_LJX = np.zeros(number)
    
    for i in range(number):                         # 遍历整个时段
        
        # 各水文站数据
        hydStation_zq = floodProcess_zq.loc[i, flood_frequency]
        hydStation_hq = floodProcess_hq.loc[i, flood_frequency]
        hydStation_mh = floodProcess_mh.loc[i, flood_frequency]
        hydStation_xt = floodProcess_xt.loc[i, flood_frequency]
        '''
        ============================================
        逐时段精细化凑泄（正推） 模拟计算
        ============================================
        考虑区间(10)：
        1.唐乃亥-龙羊峡
        2.龙羊峡-拉西瓦
        3.拉西瓦-李家峡
        4.李家峡-公伯峡
        5.公伯峡-积石峡
        6.积石峡-刘家峡
        7.刘家峡-兰州
        8.兰州-黑山峡
        9.黑山峡-下河沿
        
        保证：所有水库蓄水在汛线水位以下（防洪安全）、刘家峡/黑三峡上游水库以最大发电流量和最大水头（发电效益）
            
            根据实际调水调沙，调水调沙期不考虑农业灌溉，而生活工业引水忽略不计
        '''
        ###### 滞时计算
        # tdelay_tnh_LYX[i] = timedelay_corralation(floodProcess_tnh, hydStation_lyx, tdelays_tnh[i])
   
        ###### 水量损失计算
    

        ###### 水库群调节计算
    
        # 单个水库容量变化由全体水库群的综合发电效益确定
        # 确定的方法为试算法
            #先假定水库需水量变化为0，计算整个水库群的发电效益
            #根据发电效益，调整单个水库需水量变化
            #最终确定整个水库群的调度过程，输出调度过程
    
        # 从下向上第一次计算
        '''    兰州-刘家峡    '''
        if use_real_time_scheduling1:
        # 水库下泄 = 断面流量 - 支流来水（考虑滞时）/流量损失    
            Q_out_LJX[i] = (Q_lz[i] - hydStation_mh * (1 - Qloss_mh_lz[i].item()) \
                                        - hydStation_xt * (1 - Qloss_xt_lz[i].item())) / (1 - Qloss_LJX_lz[i].item())
        else:
            Q_out_LJX[i] = liujiaxiastream_data[i]                            
        Q_in_LJX[i] = Q_out_LJX[i] - hydStation_zq * (1 - Qloss_zq_LJX[i].item() ) - hydStation_hq * (1 - Qloss_hq_LJX[i].item()) # 径流调解下的入库流量
               
        if i == 0:
            Zup_LJX[i] = Z_ini_LJX
        else:
            Zup_LJX[i] = Zup_LJX[i-1]             
        '''    积石峡-刘家峡    '''
        Q_out_JSX[i] = (Q_in_LJX[i] - hydStation_zq * (1 - Qloss_zq_LJX[i].item()) \
                                            - hydStation_hq * (1 - Qloss_hq_LJX[i].item())) \
                                / (1 - Qloss_JSX_LJX[i].item())
        Q_in_JSX[i] = Q_out_JSX[i]
        if i == 0:
            Zup_JSX[i] = Z_ini_JSX
        else:
            Zup_JSX[i] = Zup_JSX[i-1]
                
        '''    公伯峡-积石峡    '''
        Q_out_GBX[i] = Q_in_JSX[i] / (1 - Qloss_GBX_JSX[i].item())
        Q_in_GBX[i] = Q_out_GBX[i]
        if i == 0:
            Zup_GBX[i] = Z_ini_GBX
        else:
            Zup_GBX[i] = Zup_GBX[i-1]
                
        '''    李家峡-公伯峡    '''
        Q_out_LJ[i] = Q_in_GBX[i] / (1 - Qloss_LJ_GBX[i].item())
        Q_in_LJ[i] = Q_out_LJ[i]
        if i == 0:
            Zup_LJ[i] = Z_ini_LJ
        else:
            Zup_LJ[i] = Zup_LJ[i-1]
                
        '''    拉西瓦-李家峡    '''
        Q_out_LXW[i] = Q_in_LJ[i] / (1 - Qloss_LXW_LJ[i].item())
        Q_in_LXW[i] = Q_out_LXW[i]
        if i == 0:
            Zup_LXW[i] = Z_ini_LXW
        else:
            Zup_LXW[i] = Zup_LXW[i-1]
                
        '''    龙羊峡-拉西瓦    '''
        Q_out_LYX[i] = Q_in_LXW[i] / (1 - Qloss_LYX_LXW[i].item())
        Q_in_LYX[i] = Q_out_LYX[i]
        if i == 0:
            Zup_LYX[i] = Z_ini_LYX
        else:
            Zup_LYX[i] = Zup_LYX[i-1]
    
        # 判断唐乃亥来水能否满足干流水库群需水，确定所需调节的时段库容量
        # Qd[i] = hydStation_tnh.loc[Row_tnh+i - tdelay_tnh_LYX[i],'流量'].to_numpy() - Q_in_LYX[i]
        Q_in[i] = floodProcess_tnh.loc[[i], flood_frequency].to_numpy() - Q_in_LYX[i]

        ### 从下向上第二次计算，从上向下计算(当来水不能满足下泄水量时，下游水库依次补水；当来水大于下泄水量时上游水库依次蓄水)
        if Q_in[i] >= 0:
            '''___龙羊峡___'''
            # 优先蓄水，直到达到设计洪水位
            if Zup_LYX[i] < Zdesignflood_LYX:
                # 计算可蓄水量
                available_storage_LYX = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zdesignflood_LYX, 1) - interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1)
                # 更新出库流量
                if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:
                    Q_LYXdownstream[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']   # 此时需要的下泄流量超过了最大过机流量，按最大过机流量下泄，下游需要提供的流量
                    Q_out_LYX[i] = Q_MaxTroMachine['LYX']
                else:
                    pass
                # 判断可蓄水量与来水量的大小
                W_in = (Q_in[i] +  Q_in_LYX[i] - Q_out_LYX[i]) * 8.64 / 10000
                if available_storage_LYX >=  W_in:
                    # 更新库容和水位
                    actual_storage_LYX = W_in
                    W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) + actual_storage_LYX
                    Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
                    # 更新入库流量
                    Q_in_LYX[i] += Q_in[i]
                else:
                    actual_storage_LYX = available_storage_LYX
                    # 更新库容和水位
                    W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) + actual_storage_LYX
                    Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
                    # 更新入库、出库流量
                    Q_in_LYX[i] += Q_in[i]
                    Q_out_LYX[i] += (W_in - actual_storage_LYX) * 10000 / 8.64
                # 剩余水量传递给下一个水库
                remaining_water = W_in - actual_storage_LYX
                    # 确保剩余水量不为负
                if remaining_water < 0:
                    remaining_water = 0          
            else:
                # 已达到设计洪水位，来水全部下泄
                Q_in_LYX[i] += Q_in[i]
                Q_out_LYX[i] = Q_in_LYX[i]
                Q_LYXdownstream[i] = 0
                remaining_water = Q_out_LYX[i] * 8.64 / 10000        
            # 利用下泄流量查找尾水位            
            Zdown_LYX[i] = interpolation_2D(Parameters_LYX['下泄流量下游水位曲线'], Q_out_LYX[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:
                Q_ele_LYX[i] = Q_MaxTroMachine['LYX']
                Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']
            else:
                Q_ele_LYX[i] = Q_out_LYX[i]
                Q_ele_abandoned_LYX[i] = 0
            # 计算出力
            H_ele_LYX[i] = Zup_LYX[i] - Zdown_LYX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/龙羊峡.xlsx'  # 假设NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LYX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LYX[i], Q_ele_LYX[i] / number_PowerStation['LYX']) * number_PowerStation['LYX']
                                        
            '''___拉西瓦___'''
            Q_in_LXW[i] = Q_out_LYX[i]  * (1 - Qloss_LYX_LXW[i].item())  # 龙羊峡出库等于拉西瓦入库
            remaining_water = remaining_water * (1 - Qloss_LYX_LXW[i].item())
            if remaining_water > 0 and Zup_LXW[i] < Zdesignflood_LXW:
                # 拉西瓦水库蓄水
                available_storage_LXW = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zdesignflood_LXW, 1) - interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1)
                # 更新出库流量
                if Q_out_LXW[i] >= Q_MaxTroMachine['LXW']:
                    Q_LXWdownstream[i] = Q_out_LXW[i] - Q_MaxTroMachine['LXW']   # 此时需要的下泄流量超过了最大过机流量，按最大过机流量下泄，下游需要提供的流量
                    Q_out_LXW[i] = Q_MaxTroMachine['LXW']
                if available_storage_LXW >=  remaining_water:  
                    # 更新库容和水位
                    actual_storage_LXW = remaining_water               
                    W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1) + actual_storage_LXW
                    Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
                else:
                    actual_storage_LXW = available_storage_LXW
                    W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1) + actual_storage_LXW
                    Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
                    Q_out_LXW[i] += (remaining_water - actual_storage_LXW) * 10000 / 8.64  
                remaining_water = remaining_water - actual_storage_LXW
                if remaining_water < 0:
                    remaining_water = 0
            else:
                Q_out_LXW[i] = Q_in_LXW[i]
                Q_LXWdownstream[i] = 0
                remaining_water = remaining_water
            # 利用下泄流量查找尾水位
            Zdown_LXW[i] = interpolation_2D(Parameters_LXW['下泄流量下游水位曲线'], Q_out_LXW[i] / number_PowerStation['LXW'], 2)
            # 计算发电流量和弃水流量
            if Q_out_LXW[i] >= Q_MaxTroMachine['LXW']:
                Q_ele_LXW[i] = Q_MaxTroMachine['LXW']
                Q_ele_abandoned_LXW[i] = Q_out_LXW[i] - Q_MaxTroMachine['LXW']
            else:
                Q_ele_LXW[i] = Q_out_LXW[i]
                Q_ele_abandoned_LXW[i] = 0
            # 计算出力
            H_ele_LXW[i] = Zup_LXW[i] - Zdown_LXW[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/拉西瓦.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LXW[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LXW[i], Q_ele_LXW[i] / number_PowerStation['LXW']) * number_PowerStation['LXW']
            
            '''___李家峡___'''
            Q_in_LJ[i] = Q_out_LXW[i] * (1 - Qloss_LXW_LJ[i].item()) # 拉西瓦出库等于李家峡入库
            remaining_water = remaining_water * (1 - Qloss_LXW_LJ[i].item())
            if remaining_water > 0 and Zup_LJ[i] < Zdesignflood_LJ:
                # 李家峡水库蓄水
                available_storage_LJ = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zdesignflood_LJ, 1) - interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zup_LJ[i], 1)
                if Q_out_LJ[i] >= Q_MaxTroMachine['LJ']:
                    Q_LJdownstream[i] = Q_out_LJ[i] - Q_MaxTroMachine['LJ']   # 此时需要的下泄流量超过了最大过机流量，按最大过机流量下泄，下游需要提供的流量
                    Q_out_LJ[i] = Q_MaxTroMachine['LJ']
                if available_storage_LJ >=  remaining_water:  
                    # 更新库容和水位
                    actual_storage_LJ = remaining_water              
                else:
                    actual_storage_LJ = available_storage_LJ
                    Q_out_LJ[i] += (remaining_water - actual_storage_LJ) * 10000 / 8.64  
                remaining_water = remaining_water - actual_storage_LJ
                if remaining_water < 0:
                    remaining_water = 0
            else:
                Q_out_LJ[i] = Q_in_LJ[i]
                Q_LJdownstream[i] = 0
                remaining_water = remaining_water
            # 利用下泄流量查找尾水位
            Zdown_LJ[i] = interpolation_2D(Parameters_LJ['下泄流量下游水位曲线'], Q_out_LJ[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_LJ[i] >= Q_MaxTroMachine['LJ']:
                Q_ele_LJ[i] = Q_MaxTroMachine['LJ']
                Q_ele_abandoned_LJ[i] = Q_out_LJ[i] - Q_MaxTroMachine['LJ']
            else:
                Q_ele_LJ[i] = Q_out_LJ[i]
                Q_ele_abandoned_LJ[i] = 0
            # 计算出力
            H_ele_LJ[i] = Zup_LJ[i] - Zdown_LJ[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/李家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LJ[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJ[i], Q_ele_LJ[i] / number_PowerStation['LJ']) * number_PowerStation['LJ']
                        
            '''___公伯峡___'''
            Q_in_GBX[i] = Q_out_LJ[i] * (1 - Qloss_LJ_GBX[i].item()) # 李家峡出库等于公伯峡入库
            remaining_water = remaining_water * (1 - Qloss_LJ_GBX[i].item())
            if remaining_water > 0 and Zup_GBX[i] < Zdesignflood_GBX:
                # 公伯峡水库蓄水
                available_storage_GBX = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zdesignflood_GBX, 1) - interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zup_GBX[i], 1)
                if Q_out_GBX[i] >= Q_MaxTroMachine['GBX']:
                    Q_GBXdownstream[i] = Q_out_GBX[i] - Q_MaxTroMachine['GBX']   # 此时需要的下泄流量超过了最大过机流量，按最大过机流量下泄，下游需要提供的流量
                    Q_out_GBX[i] = Q_MaxTroMachine['GBX']
                if available_storage_GBX >=  remaining_water:
                    # 更新库容和水位
                    actual_storage_GBX = remaining_water
                else:
                    actual_storage_GBX = available_storage_GBX
                    Q_out_GBX[i] += (remaining_water - actual_storage_GBX) * 10000 / 8.64
                remaining_water = remaining_water - actual_storage_LJ
                if remaining_water < 0:
                    remaining_water = 0
            else:
                Q_out_GBX[i] = Q_in_GBX[i]
                Q_GBXdownstream[i] = 0
                remaining_water = remaining_water
            # 利用下泄流量查找尾水位
            Zdown_GBX[i] = interpolation_2D(Parameters_GBX['下泄流量下游水位曲线'], Q_out_GBX[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_GBX[i] >= Q_MaxTroMachine['GBX']:
                Q_ele_GBX[i] = Q_MaxTroMachine['GBX']
                Q_ele_abandoned_GBX[i] = Q_out_GBX[i] - Q_MaxTroMachine['GBX']
            else:
                Q_ele_GBX[i] = Q_out_GBX[i]
                Q_ele_abandoned_GBX[i] = 0
            # 计算出力
            H_ele_GBX[i] = Zup_GBX[i] - Zdown_GBX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/公伯峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_GBX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_GBX[i], Q_ele_GBX[i] / number_PowerStation['GBX']) * number_PowerStation['GBX']
            
            '''___积石峡___'''
            Q_in_JSX[i] = Q_out_GBX[i] * (1 - Qloss_GBX_JSX[i].item()) # 公伯峡出库等于积石峡入库
            remaining_water = remaining_water * (1 - Qloss_GBX_JSX[i].item())
            if remaining_water > 0 and Zup_JSX[i] < Zdesignflood_JSX:
                # 积石峡水库蓄水
                available_storage_JSX = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zdesignflood_JSX, 1) - interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1)
                if Q_out_JSX[i] >= Q_MaxTroMachine['JSX']:
                    Q_JSXdownstream[i] = Q_out_JSX[i] - Q_MaxTroMachine['JSX']   # 此时需要的下泄流量超过了最大过机流量，按最大过机流量下泄，下游需要提供的流量
                    Q_out_JSX[i] = Q_MaxTroMachine['JSX']
                if available_storage_JSX >= remaining_water:
                    # 更新库容和水位
                    actual_storage_JSX = remaining_water
                    W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1) + actual_storage_JSX
                    Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
                else:
                    actual_storage_JSX = available_storage_JSX
                    W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1) + actual_storage_JSX
                    Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
                    Q_out_JSX += (remaining_water - actual_storage_JSX) * 10000 / 8.64     
                remaining_water = remaining_water - actual_storage_JSX
                if remaining_water < 0:
                    remaining_water = 0 
            else:
                Q_out_JSX[i] = Q_in_JSX[i]
                Q_JSXdownstream[i] = 0
                remaining_water = remaining_water
            # 利用下泄流量查找尾水位
            Zdown_JSX[i] = interpolation_2D(Parameters_JSX['下泄流量下游水位曲线'], Q_out_JSX[i] / number_PowerStation['JSX'], 2)
            # 计算发电流量和弃水流量
            if Q_out_JSX[i] >= Q_MaxTroMachine['JSX']:
                Q_ele_JSX[i] = Q_MaxTroMachine['JSX']
                Q_ele_abandoned_JSX[i] = Q_out_JSX[i] - Q_MaxTroMachine['JSX']
            else:
                Q_ele_JSX[i] = Q_out_JSX[i]
                Q_ele_abandoned_JSX[i] = 0
            # 计算出力
            H_ele_JSX[i] = Zup_JSX[i] - Zdown_JSX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/积石峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_JSX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_JSX[i], Q_ele_JSX[i] / number_PowerStation['JSX']) * number_PowerStation['JSX']
            if N_JSX[i] >= 150:
                N_JSX[i] = 150
            else:
                pass
            
            '''___刘家峡___'''
            Q_in_LJX[i] = Q_out_JSX[i] * (1 - Qloss_JSX_LJX[i].item()) \
                            + hydStation_zq * (1 - Qloss_zq_LJX[i].item())\
                                + hydStation_hq * (1 - Qloss_hq_LJX[i].item())# 积石峡出库等于刘家峡入库
            remaining_water = remaining_water * (1 - Qloss_JSX_LJX[i].item())
            if remaining_water > 0 and Zup_LJX[i] < Zdesignflood_LJX:
                # 刘家峡水库蓄水
                available_storage_LJX = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zdesignflood_LJX, 1) - interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1)
                if available_storage_LJX >= remaining_water:
                    actual_storage_LJX = remaining_water
                    W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) + actual_storage_LJX
                    Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
                else:
                    actual_storage_LJX = available_storage_LJX
                    W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) + actual_storage_LJX
                    Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
                    Q_out_LJX[i] += (remaining_water - actual_storage_LJX) * 10000 / 8.64
                remaining_water = remaining_water - actual_storage_LJX
                if remaining_water < 0:
                    remaining_water = 0
                else:
                    pass
            else:
                # 刘家峡水库下泄流量（梯级水库群上游水库按最大过机流量下泄，此时需要刘家峡水库补充下泄）
                Q_out_LJX[i] = Q_in_LJX[i] + Q_LYXdownstream[i] * (1 - Qloss_LYX_LXW[i].item()) * (1 - Qloss_LXW_LJ[i].item()) * (1 - Qloss_LJ_GBX[i].item()) * (1 - Qloss_GBX_JSX[i].item()) * (1 - Qloss_JSX_LJX[i].item()) \
                    + Q_LXWdownstream[i] * (1 - Qloss_LXW_LJ[i].item()) * (1 - Qloss_LJ_GBX[i].item()) * (1 - Qloss_GBX_JSX[i].item()) * (1 - Qloss_JSX_LJX[i].item()) \
                        + Q_LJdownstream[i] * (1 - Qloss_LJ_GBX[i].item()) * (1 - Qloss_GBX_JSX[i].item()) * (1 - Qloss_JSX_LJX[i].item()) \
                            + Q_GBXdownstream[i] * (1 - Qloss_GBX_JSX[i].item()) * (1 - Qloss_JSX_LJX[i].item()) \
                                + Q_JSXdownstream[i] * (1 - Qloss_JSX_LJX[i].item())
            
            # 当i等于number-3、number-2、number-1和number时，分别设置Q_out_LJX[i]的值
            if i == number -3:
                Q_out_LJX[i] =1350
            elif i == number-2:
                Q_out_LJX[i] =1000
            elif i == number-1:
                Q_out_LJX[i] =800

            # 统一计算库容和水位
            W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) + (Q_in_LJX[i] - Q_out_LJX[i])  * 8.64 / 10000
            Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
            
            # 利用下泄流量查找尾水位
            Zdown_LJX[i] = interpolation_2D(Parameters_LJX['下泄流量下游水位曲线'], Q_out_LJX[i] / number_PowerStation['LJX'], 2)     
            # 计算发电流量和弃水流量
            if Q_out_LJX[i] >= Q_MaxTroMachine['LJX']:
                Q_ele_LJX[i] = Q_MaxTroMachine['LJX']
                Q_ele_abandoned_LJX[i] = Q_out_LJX[i] - Q_MaxTroMachine['LJX']
            else:
                Q_ele_LJX[i] = Q_out_LJX[i]
                Q_ele_abandoned_LJX[i] = 0
            # 计算出力
            H_ele_LJX[i] = Zup_LJX[i] - Zdown_LJX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/刘家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LJX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJX[i], Q_ele_LJX[i] / number_PowerStation['LJX']) * number_PowerStation['LJX']            
            Q_out_LJXPeak[i] =  Q_out_LJX[i] - Q_in_LJX[i]
            if Q_out_LJXPeak[i] >= 0:
                Q_out_LJXPeak[i] = Q_out_LJXPeak[i]
            else:
                Q_out_LJXPeak[i] = 0
        
        
        # Q_in[i]<0,结合唐乃亥来水和水库群总弃水，从下向上第二次计算，即来水不够且龙羊峡在汛限水位以上，刘家峡优先放水
        elif Q_in[i] <0 and Zup_LYX[i] > Zfloodcontrol_LYX:
            '''___刘家峡___'''
            supply_water = -Q_in[i] * 8.64 / 10000 # 将水库需要提供的水量转换位正数
            if Zup_LJX[i] > Zdead_LJX:
                available_supply_LJX = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) - interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zdead_LJX, 1)
                
                if available_supply_LJX >= supply_water:
                    actual_supply_LJX = supply_water # 亿m3

                    Q_in_LJX[i] = Q_out_LJX[i] + Q_in[i]
                    supply_water = supply_water - actual_supply_LJX
                else:
                    actual_supply_LJX = supply_water - available_supply_LJX
                    W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zdead_LJX, 1)
                    Zup_LJX[i] = Zdead_LJX
                    Q_out_LJX[i] = Q_in_LJX[i] + actual_supply_LJX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LJX
            else:
                Zup_LJX[i] = Zdead_LJX
                Q_in_LJX[i] = Q_in_LJX[i] + supply_water * 10000 / 8.64
                    
            if Q_out_LJX[i] >= Q_MaxTroMachine['LJX']:
                Q_ele_LJX[i] = Q_MaxTroMachine['LJX']
                Q_ele_abandoned_LJX[i] = Q_out_LJX[i] - Q_MaxTroMachine['LJX']
            else:
                Q_ele_LJX[i] = Q_out_LJX[i]
                Q_ele_abandoned_LJX[i] = 0
            
            '''___积石峡___'''   
            Q_out_JSX[i] = (Q_in_LJX[i] - hydStation_zq * (1 - Qloss_zq_LJX[i].item()) \
                                                - hydStation_hq * (1 - Qloss_hq_LJX[i].item())) \
                                    / (1 - Qloss_JSX_LJX[i].item())
            Q_in_JSX[i] = Q_out_JSX[i]
            if Zup_JSX[i] > Zdead_JSX:
                available_supply_JSX = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1) - interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zdead_JSX, 1)
                
                if available_supply_JSX >= supply_water:
                    actual_supply_JSX = supply_water # 亿m3

                    Q_out_JSX[i] += actual_supply_JSX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_JSX
                else:
                    actual_supply_JSX = supply_water - available_supply_JSX # 亿m3
                    W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zdead_JSX, 1)
                    Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
                    Q_out_JSX[i] += actual_supply_JSX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_JSX       
            else:
                Zup_JSX[i] = Zdead_JSX
                Q_in_JSX[i] = Q_in_JSX[i] + supply_water * 10000 / 8.64
                    
            if Q_out_JSX[i] >= Q_MaxTroMachine['JSX']:
                Q_ele_JSX[i] = Q_MaxTroMachine['JSX']
                Q_ele_abandoned_JSX[i] = Q_out_JSX[i] - Q_MaxTroMachine['JSX']
            else:
                Q_ele_JSX[i] = Q_out_JSX[i]
                Q_ele_abandoned_JSX[i] = 0
                
            '''___公伯峡___'''      
            Q_out_GBX[i] = Q_in_JSX[i] / (1 - Qloss_GBX_JSX[i].item())
            Q_in_GBX[i] = Q_out_GBX[i]
            if Zup_GBX[i] > Zdead_GBX:
                available_supply_GBX = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zup_GBX[i], 1) - interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zdead_GBX, 1)
                
                if available_supply_GBX >= supply_water:
                    actual_supply_GBX = supply_water

                    Q_out_GBX[i] += actual_supply_GBX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_JSX
                        
                else:
                    actual_supply_GBX = supply_water - available_supply_GBX
                    W_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zdead_GBX, 1)
                    Zup_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], W_GBX[i], 2)
                    Q_out_JSX[i] += actual_supply_JSX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_JSX
            else:
                Zup_GBX[i] = Zdead_GBX
                W_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zup_GBX[i], 1)
            
            if Q_out_GBX[i] >= Q_MaxTroMachine['GBX']:
                Q_ele_GBX[i] = Q_MaxTroMachine['GBX']
                Q_ele_abandoned_GBX[i] = Q_out_GBX[i] - Q_MaxTroMachine['GBX']
            else:
                Q_ele_GBX[i] = Q_out_GBX[i]
                Q_ele_abandoned_GBX[i] = 0
                    
            '''___李家峡___'''
            Q_out_LJ[i] = Q_in_GBX[i] / (1 - Qloss_LJ_GBX[i].item())
            Q_in_LJ[i] = Q_out_LJ[i]
            if Zup_LJ[i] > Zdead_LJ:
                available_supply_LJ = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zup_LJ[i], 1) - interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zdead_LJ, 1)
                
                if available_supply_LJ >= supply_water:
                    actual_supply_LJ = supply_water

                    Q_out_LJ[i] += actual_supply_LJ * 10000 / 8.64
                    supply_water = supply_water - actual_supply_JSX
                else:
                    actual_supply_LJ = supply_water - available_supply_LJ
                    W_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zdead_LJ, 1)
                    Zup_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], W_LJ[i], 2)
                    Q_out_LJ[i] += actual_supply_LJ * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LJ
            else:
                Zup_LJ[i] = Zdead_LJ
                W_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zup_LJ[i], 1)
            
            if Q_out_LJ[i] >= Q_MaxTroMachine['LJ']:
                Q_ele_LJ[i] = Q_MaxTroMachine['LJ']
                Q_ele_abandoned_LJ[i] = Q_out_LJ[i] - Q_MaxTroMachine['LJ']
            else:
                Q_ele_LJ[i] = Q_out_LJ[i]
                Q_ele_abandoned_LJ[i] = 0
                
            '''___拉西瓦___'''
            Q_out_LXW[i] = Q_in_LJ[i] / (1 - Qloss_LXW_LJ[i].item())
            Q_in_LXW[i] = Q_out_LXW[i]
            if Zup_LXW[i] > Zdead_LXW:
                available_supply_LXW = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1) - interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zdead_LXW, 1)
                
                if available_supply_LXW >= supply_water:
                    actual_supply_LXW = supply_water

                    Q_out_LXW[i] += actual_supply_LXW * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LXW
                else:
                    actual_supply_LXW = supply_water - available_supply_LXW
                    W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zdead_LXW, 1) - actual_supply_LXW
                    Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
                    Q_out_LXW[i] += actual_supply_LXW * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LXW
            else:
                Zup_LXW[i] = Zdead_LXW
                W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1)
                
            if Q_out_LXW[i] >= Q_MaxTroMachine['LXW']:
                Q_ele_LXW[i] = Q_MaxTroMachine['LXW']
                Q_ele_abandoned_LXW[i] = Q_out_LXW[i] - Q_MaxTroMachine['LXW']
            else:
                Q_ele_LXW[i] = Q_out_LXW[i]
                Q_ele_abandoned_LXW[i] = 0
                    
            '''___龙羊峡___'''
            Q_out_LYX[i] = Q_in_LXW[i] / (1 - Qloss_LYX_LXW[i].item())
            Q_in_LYX[i] = Q_in[i] + Q_in_LYX[i]  
            if Zup_LYX[i] > Zdead_LYX:
                available_supply_LYX = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) - interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zdead_LYX, 1)
                
                if available_supply_LYX >= supply_water:
                    actual_supply_LYX = supply_water
                    if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:  
                        Q_ele_LYX[i] = Q_MaxTroMachine['LYX']  
                        Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']
                        Q_out_LYX[i] = Q_MaxTroMachine['LYX']
                    else:
                        pass
                    W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) - actual_supply_LYX + (Q_in_LYX[i] - Q_out_LYX[i]) * 8.64 /10000
                    Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
                    Q_out_LYX[i] += actual_supply_LYX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LXW
                else:
                    actual_supply_LYX = supply_water - available_supply_LYX
                    W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) - actual_supply_LYX
                    Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
                    Q_out_LYX[i] += actual_supply_LYX * 10000 / 8.64
                    supply_water = supply_water - actual_supply_LXW
                    print('水库群库容不足，难以进行调水调沙任务')
            else:
                Zup_LYX[i] = Zdead_LYX
                W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1)
                print('水库群库容不足，难以进行调水调沙任务')
                    
            if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:  
                Q_ele_LYX[i] = Q_MaxTroMachine['LYX']  
                Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']
            else:
                Q_ele_LYX[i] = Q_out_LYX[i]
                Q_ele_abandoned_LYX[i] = 0
                    

            # 当龙羊峡水库水位高于汛限水位时，按最大过机流量进行下泄
            '''___龙羊峡___'''
            Q_out_LYX[i] = Q_MaxTroMachine['LYX']
            W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) + (Q_in_LYX[i] - Q_out_LYX[i]) * 8.64 / 10000
            Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
            Q_ele_LYX[i] = Q_out_LYX[i]
            Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_ele_LYX[i]
            # 利用下泄流量查找尾水位            
            Zdown_LYX[i] = interpolation_2D(Parameters_LYX['下泄流量下游水位曲线'], Q_out_LYX[i], 2)    
            # 计算出力
            H_ele_LYX[i] = Zup_LYX[i] - Zdown_LYX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/龙羊峡.xlsx'  # 假设NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LYX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LYX[i], Q_ele_LYX[i] / number_PowerStation['LYX']) * number_PowerStation['LYX'] 
            
            '''___拉西瓦___'''
            Q_in_LXW[i] = Q_out_LYX[i]  * (1 - Qloss_LYX_LXW[i].item())  # 龙羊峡出库等于拉西瓦入库
            Q_out_LXW[i]  = Q_in_LXW[i]
            W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1) + (Q_in_LXW[i] - Q_out_LXW[i]) * 8.64 / 10000
            Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
            Q_ele_LXW[i] = Q_out_LXW[i]
            Q_ele_abandoned_LXW[i] = Q_out_LXW[i] - Q_ele_LXW[i] 
            # 利用下泄流量查找尾水位
            Zdown_LXW[i] = interpolation_2D(Parameters_LXW['下泄流量下游水位曲线'], Q_out_LXW[i] / number_PowerStation['LXW'], 2)
            # 计算出力
            H_ele_LXW[i] = Zup_LXW[i] - Zdown_LXW[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/拉西瓦.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LXW[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LXW[i], Q_ele_LXW[i] / number_PowerStation['LXW']) * number_PowerStation['LXW']
            
            '''___李家峡___'''
            Q_in_LJ[i] = Q_out_LXW[i] * (1 - Qloss_LXW_LJ[i].item()) # 拉西瓦出库等于李家峡入库
            Q_out_LJ[i] = Q_in_LJ[i]
            W_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zup_LJ[i], 1) + (Q_in_LJ[i] - Q_out_LJ[i]) * 8.64 / 10000
            Zup_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], W_LJ[i], 2)
            Q_ele_LJ[i] = Q_out_LJ[i]
            Q_ele_abandoned_LJ[i] = Q_out_LJ[i] - Q_ele_LJ[i]
            # 利用下泄流量查找尾水位
            Zdown_LJ[i] = interpolation_2D(Parameters_LJ['下泄流量下游水位曲线'], Q_out_LJ[i], 2)
            # 计算出力
            H_ele_LJ[i] = Zup_LJ[i] - Zdown_LJ[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/李家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LJ[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJ[i], Q_ele_LJ[i] / number_PowerStation['LJ']) * number_PowerStation['LJ']
            
            '''___公伯峡___'''
            Q_in_GBX[i] = Q_out_LJ[i] * (1 - Qloss_LJ_GBX[i].item()) # 李家峡出库等于公伯峡入库
            Q_out_GBX[i] = Q_in_GBX[i]
            W_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zup_GBX[i], 1) + (Q_in_GBX[i] - Q_out_GBX[i]) * 8.64 / 10000
            Zup_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], W_GBX[i], 2)
            Q_ele_GBX[i] = Q_out_GBX[i]
            Q_ele_abandoned_GBX[i] = Q_out_GBX[i] - Q_ele_GBX[i]
            # 利用下泄流量查找尾水位
            Zdown_GBX[i] = interpolation_2D(Parameters_GBX['下泄流量下游水位曲线'], Q_out_GBX[i], 2)
            # 计算出力
            H_ele_GBX[i] = Zup_GBX[i] - Zdown_GBX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/公伯峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_GBX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_GBX[i], Q_ele_GBX[i] / number_PowerStation['GBX']) * number_PowerStation['GBX']
            
            '''___积石峡___'''
            Q_in_JSX[i] = Q_out_GBX[i] * (1 - Qloss_GBX_JSX[i].item()) # 公伯峡出库等于积石峡入库
            Q_out_JSX[i] = Q_in_JSX[i]
            W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1) + (Q_in_JSX[i] - Q_out_JSX[i]) * 8.64 / 10000
            Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
            Q_ele_JSX[i] = Q_out_JSX[i]
            Q_ele_abandoned_JSX[i] = Q_out_JSX[i] - Q_ele_JSX[i]
            # 利用下泄流量查找尾水位
            Zdown_JSX[i] = interpolation_2D(Parameters_JSX['下泄流量下游水位曲线'], Q_out_JSX[i] / number_PowerStation['JSX'], 2)
            # 计算出力
            H_ele_JSX[i] = Zup_JSX[i] - Zdown_JSX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/积石峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_JSX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_JSX[i], Q_ele_JSX[i] / number_PowerStation['JSX']) * number_PowerStation['JSX']
            
            '''___刘家峡___'''
            Q_in_LJX[i] = Q_out_JSX[i] * (1 - Qloss_JSX_LJX[i].item()) \
                            + hydStation_zq * (1 - Qloss_zq_LJX[i].item()) \
                                + hydStation_hq * (1 - Qloss_hq_LJX[i].item()) # 积石峡出库等于刘家峡入库
            # 当i等于number-3、number-2、number-1和number时，分别设置Q_out_LJX[i]的值
            if i == number -3:
                Q_out_LJX[i] =1350
            elif i == number-2:
                Q_out_LJX[i] =1000
            elif i == number-1:
                Q_out_LJX[i] =800           
            W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) + (Q_in_LJX[i] - Q_out_LJX[i]) * 8.64 / 10000
            Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_LJX[i] >= Q_MaxTroMachine['LJX']:
                Q_ele_LJX[i] = Q_MaxTroMachine['LJX']
                Q_ele_abandoned_LJX[i] = Q_out_LJX[i] - Q_MaxTroMachine['LJX']                    
            else:
                Q_ele_LJX[i] = Q_out_LJX[i]
                Q_ele_abandoned_LJX[i] = 0
            # 利用下泄流量查找尾水位
            Zdown_LJX[i] = interpolation_2D(Parameters_LJX['下泄流量下游水位曲线'], Q_out_LJX[i] / number_PowerStation['LJX'], 2)
            # 计算水头
            H_ele_LJX[i] = Zup_LJX[i] - Zdown_LJX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/刘家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'                                                                                                                                               
            N_LJX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJX[i], Q_ele_LJX[i] / number_PowerStation['LJX']) * number_PowerStation['LJX']                       

        
        # 不仅来水不够，而且龙羊峡也未达到汛限水位以上，所以不进行水沙调控 
        else:
            '''龙羊峡'''
            Q_in_LYX[i] = Q_in_LYX[i] + Q_in[i]
            Q_out_LYX[i]  = Q_in_LYX[i]
            # 更新出库流量
            if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:
                Q_out_LYX[i] = Q_MaxTroMachine['LYX']
            W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Zup_LYX[i], 1) + (Q_in_LYX[i] - Q_out_LYX[i]) * 8.64 / 10000
            Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)     
            # 利用下泄流量查找尾水位            
            Zdown_LYX[i] = interpolation_2D(Parameters_LYX['下泄流量下游水位曲线'], Q_out_LYX[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:
                Q_ele_LYX[i] = Q_MaxTroMachine['LYX']
                Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']
            else:
                Q_ele_LYX[i] = Q_out_LYX[i]
                Q_ele_abandoned_LYX[i] = 0
            # 计算出力
            H_ele_LYX[i] = Zup_LYX[i] - Zdown_LYX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/龙羊峡.xlsx'  # 假设NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LYX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LYX[i], Q_ele_LYX[i] / number_PowerStation['LYX']) * number_PowerStation['LYX']
        
            '''拉西瓦'''
            Q_in_LXW[i] = Q_out_LYX[i]  * (1 - Qloss_LYX_LXW[i].item())  # 龙羊峡出库等于拉西瓦入库
            Q_out_LXW[i] = Q_in_LXW[i]
            W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Zup_LXW[i], 1) + (Q_in_LXW[i] - Q_out_LXW[i]) * 8.64 / 10000
            Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
            # 利用下泄流量查找尾水位
            Zdown_LXW[i] = interpolation_2D(Parameters_LXW['下泄流量下游水位曲线'], Q_out_LXW[i] / number_PowerStation['LXW'], 2)
            # 计算发电流量和弃水流量
            if Q_out_LXW[i] >= Q_MaxTroMachine['LXW']:
                Q_ele_LXW[i] = Q_MaxTroMachine['LXW']
                Q_ele_abandoned_LXW[i] = Q_out_LXW[i] - Q_MaxTroMachine['LXW']
            else:
                Q_ele_LXW[i] = Q_out_LXW[i]
                Q_ele_abandoned_LXW[i] = 0
            # 计算出力
            H_ele_LXW[i] = Zup_LXW[i] - Zdown_LXW[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/拉西瓦.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LXW[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LXW[i], Q_ele_LXW[i] / number_PowerStation['LXW']) * number_PowerStation['LXW']
            
            '''___李家峡___'''
            Q_in_LJ[i] = Q_out_LXW[i] * (1 - Qloss_LXW_LJ[i].item()) # 拉西瓦出库等于李家峡入库
            Q_out_LJ[i] = Q_in_LJ[i]             
            W_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Zup_LJ[i], 1) + (Q_in_LJ[i] - Q_out_LJ[i]) * 8.64 / 10000
            Zup_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], W_LJ[i], 2)
            # 利用下泄流量查找尾水位
            Zdown_LJ[i] = interpolation_2D(Parameters_LJ['下泄流量下游水位曲线'], Q_out_LJ[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_LJ[i] >= Q_MaxTroMachine['LJ']:
                Q_ele_LJ[i] = Q_MaxTroMachine['LJ']
                Q_ele_abandoned_LJ[i] = Q_out_LJ[i] - Q_MaxTroMachine['LJ']
            else:
                Q_ele_LJ[i] = Q_out_LJ[i]
                Q_ele_abandoned_LJ[i] = 0
            # 计算出力
            H_ele_LJ[i] = Zup_LJ[i] - Zdown_LJ[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/李家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LJ[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJ[i], Q_ele_LJ[i] / number_PowerStation['LJ']) * number_PowerStation['LJ']
                        
            '''___公伯峡___'''
            Q_in_GBX[i] = Q_out_LJ[i] * (1 - Qloss_LJ_GBX[i].item()) # 李家峡出库等于公伯峡入库
            Q_out_GBX[i] = Q_in_GBX[i]
            W_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Zup_GBX[i], 1) + (Q_in_GBX[i] -  Q_out_GBX[i]) * 8.64 / 10000
            Zup_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], W_GBX[i], 2)
            # 利用下泄流量查找尾水位
            Zdown_GBX[i] = interpolation_2D(Parameters_GBX['下泄流量下游水位曲线'], Q_out_GBX[i], 2)
            # 计算发电流量和弃水流量
            if Q_out_GBX[i] >= Q_MaxTroMachine['GBX']:
                Q_ele_GBX[i] = Q_MaxTroMachine['GBX']
                Q_ele_abandoned_GBX[i] = Q_out_GBX[i] - Q_MaxTroMachine['GBX']
            else:
                Q_ele_GBX[i] = Q_out_GBX[i]
                Q_ele_abandoned_GBX[i] = 0
            # 计算出力
            H_ele_GBX[i] = Zup_GBX[i] - Zdown_GBX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/公伯峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_GBX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_GBX[i], Q_ele_GBX[i] / number_PowerStation['GBX']) * number_PowerStation['GBX']
            
            '''___积石峡___'''
            Q_in_JSX[i] = Q_out_GBX[i] * (1 - Qloss_GBX_JSX[i].item()) # 公伯峡出库等于积石峡入库
            Q_out_JSX[i] = Q_in_JSX[i]
            W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Zup_JSX[i], 1) + (Q_in_JSX[i] -  Q_out_JSX[i]) * 8.64 / 10000
            Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
            # 利用下泄流量查找尾水位
            Zdown_JSX[i] = interpolation_2D(Parameters_JSX['下泄流量下游水位曲线'], Q_out_JSX[i] / number_PowerStation['JSX'], 2)
            # 计算发电流量和弃水流量
            if Q_out_JSX[i] >= Q_MaxTroMachine['JSX']:
                Q_ele_JSX[i] = Q_MaxTroMachine['JSX']
                Q_ele_abandoned_JSX[i] = Q_out_JSX[i] - Q_MaxTroMachine['JSX']
            else:
                Q_ele_JSX[i] = Q_out_JSX[i]
                Q_ele_abandoned_JSX[i] = 0
            # 计算出力
            H_ele_JSX[i] = Zup_JSX[i] - Zdown_JSX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/积石峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_JSX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_JSX[i], Q_ele_JSX[i] / number_PowerStation['JSX']) * number_PowerStation['JSX']
            
            '''___刘家峡___'''
            Q_in_LJX[i] = Q_out_JSX[i] * (1 - Qloss_JSX_LJX[i].item()) \
                            + hydStation_zq * (1 - Qloss_zq_LJX[i].item())\
                                + hydStation_hq * (1 - Qloss_hq_LJX[i].item())# 积石峡出库等于刘家峡入库
            Q_out_LJX[i] = Q_in_LJX[i]
            # 当i等于number-3、number-2、number-1和number时，分别设置Q_out_LJX[i]的值
            if i == number -3:
                Q_out_LJX[i] =1350
            elif i == number-2:
                Q_out_LJX[i] =1000
            elif i == number-1:
                Q_out_LJX[i] =800
            W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Zup_LJX[i], 1) + (Q_in_LJX[i] -  Q_out_LJX[i]) * 8.64 / 10000
            Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
            # 利用下泄流量查找尾水位
            Zdown_LJX[i] = interpolation_2D(Parameters_LJX['下泄流量下游水位曲线'], Q_out_LJX[i] / number_PowerStation['LJX'], 2)
            # 计算发电流量和弃水流量
            if Q_out_LJX[i] >= Q_MaxTroMachine['LJX']:
                Q_ele_LJX[i] = Q_MaxTroMachine['LJX']
                Q_ele_abandoned_LJX[i] = Q_out_LJX[i] - Q_MaxTroMachine['LJX']
            else:
                Q_ele_LJX[i] = Q_out_LJX[i]
                Q_ele_abandoned_LJX[i] = 0

            # 计算出力
            H_ele_LJX[i] = Zup_LJX[i] - Zdown_LJX[i]
            # 从NHQ曲线文件中查找对应的出力值
            file_path = './水库特征数据集/刘家峡.xlsx'  # NHQ曲线文件路径
            sheet_name = '水电站水头H-出力N-流量Q关系表'
            head_col = '水头'
            q_col = '过机流量'
            power_col = '出力'
            N_LJX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJX[i], Q_ele_LJX[i] / number_PowerStation['LJX']) * number_PowerStation['LJX']
                     
   
        # 根据NHQ曲线查出对应的出力，可能会高于额定出力，所以进行调整
        if N_LYX[i] >= 128:
            N_LYX[i] = 128
        else:
            pass       
        if N_LXW[i] >= 420:
            N_LXW[i] = 420
        else:
            pass
        if N_LJ[i] >= 160:
            N_LJ[i] = 160
        else:
            pass            
        if N_GBX[i] >= 150:
            N_GBX[i] = 150
        else:
            pass            
        if N_JSX[i] >= 150:
            N_JSX[i] = 150
        else:
            pass            
        if N_LJX[i] >= 122.5:
            N_LJX[i] = 122.5
        else:
            pass             
            # 刘家峡凑峰流量
        if Q_out_LJX[i] > Q_in_LJX[i]:
            Q_out_LJXPeak[i] =  Q_out_LJX[i] - Q_in_LJX[i]
        else:
            Q_out_LJXPeak[i] = 0

    # 检查并调整数组维度
    Q_out_LYX = Q_out_LYX.flatten()  # 转换为一维数组
    Q_out_LXW = Q_out_LXW.flatten()
    Q_out_LJ = Q_out_LJ.flatten()
    Q_out_GBX = Q_out_GBX.flatten()
    Q_out_JSX = Q_out_JSX.flatten()
    Q_out_LJX = Q_out_LJX.flatten()

run_real_time_scheduling(use_real_time_scheduling1=True)

# 获取民和站和享堂站的流量数据
mh_flow = []
xt_flow = []
for i in range(number):    
    hydStation_mh = floodProcess_mh.loc[i, flood_frequency]
    hydStation_xt = floodProcess_xt.loc[i, flood_frequency]
    mh_flow.append(hydStation_mh)  # 添加民和水文站来水
    xt_flow.append(hydStation_xt)  # 添加享堂水文站来水


# 读取数据文件
file_name = f'场次洪水过程/龙拉李公积刘{flood_frequency}一遇削峰、凑峰调度过程.xlsx'
df = pd.read_excel(file_name, sheet_name='Sheet1')

# ---------- 所有河段数据读取 ----------
# 兰州段相关数据
liujiaxiastream_data = df.iloc[:, 28].values  # 刘家峡出库

# ---------- 通用函数 ----------
def calculate_nonlinear_coefficients(k, x, flow, max_flow, a, b, c):
    # 添加数值稳定性处理
    if max_flow == 0:
        max_flow = 1e-6
    if flow > max_flow:
        flow = max_flow
    if flow < 0:
        flow = 0
    
    time_varying_index = a + b * np.exp(-c * flow / max_flow)
    denominator = (1 + 0.5 * x * k) ** 2
    nonlinear_factor = np.power(flow, time_varying_index)
    
    # 避免除零错误
    if denominator == 0:
        denominator = 1e-6
    
    c0 = 0.5 * (1 - x / k) * nonlinear_factor / denominator
    c1 = (0.5 * (1 - x / k) * nonlinear_factor - k) / denominator
    c2 = 1 - c0 - c1
    
    # 限制系数范围
    c0 = np.clip(c0, 0, 1)
    c1 = np.clip(c1, 0, 1)
    c2 = np.clip(c2, 0, 1)
    
    return c0, c1, c2

# ---------- 各河段独立计算函数 ----------
def muskingum_nonlinear_lanzhou(params, liujiaxiastream_data, mh_flow, xt_flow):
    """兰州段专用函数"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(liujiaxiastream_data)
    simulated_stream = np.zeros_like(liujiaxiastream_data)
    max_flow = np.max(liujiaxiastream_data)
    simulated_stream1[0] = liujiaxiastream_data[0]   # 初始值设置为刘家峡出库的第一个值

    for i in range(1, len(liujiaxiastream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, liujiaxiastream_data[i], max_flow, a, b, c)
        simulated_stream1[i] = c0 * liujiaxiastream_data[i] + c1 * liujiaxiastream_data[i-1] + c2 * previous_flow
    
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = (simulated_stream1[i] + mh_flow[i] + xt_flow[i]) * (1 + 0.05) # 叠加民和和享堂流量
    
    return simulated_stream

def muskingum_nonlinear_xiaheyan(params, lanzhoustream_data):
    """下河沿段专用函数"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(lanzhoustream_data)
    simulated_stream = np.zeros_like(lanzhoustream_data)
    bankfull_flow = 4000
    simulated_stream1[0] = lanzhoustream_data[0]  # 初始值设置为兰州流量的第一个值

    for i in range(1, len(lanzhoustream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, lanzhoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = (c0 * lanzhoustream_data[i] + c1 * lanzhoustream_data[i-1] + c2 * previous_flow)
    
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.04)# 叠加靖远流量
    
    return simulated_stream

def muskingum_nonlinear_qingtongxia(params, xiaheyanstream_data):
    """青铜峡段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(xiaheyanstream_data)
    simulated_stream = np.zeros_like(xiaheyanstream_data)
    bankfull_flow = 3000
    simulated_stream1[0] = xiaheyanstream_data[0]  # 初始值设置为下河沿流量的第一个值

    for i in range(1, len(xiaheyanstream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, xiaheyanstream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * xiaheyanstream_data[i] + \
                                         c1 * xiaheyanstream_data[i-1] + \
                                         c2 * previous_flow
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.2) # 叠加泉眼山流量
    
    return simulated_stream

def muskingum_nonlinear_shizuishan(params, qingtongxia_data):
    """石嘴山段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(qingtongxia_data)
    simulated_stream = np.zeros_like(qingtongxia_data)
    bankfull_flow = 2300
    simulated_stream1[0] = qingtongxia_data[0]  # 初始值设置为青铜峡流量的第一个值

    for i in range(1, len(qingtongxia_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, qingtongxia_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * qingtongxia_data[i] + \
                                         c1 * qingtongxia_data[i-1] + \
                                         c2 * previous_flow
    
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 + 0.08)

    return simulated_stream

def muskingum_nonlinear_bayangaole(params, shizuishanstream_data):
    """巴彦高勒段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(shizuishanstream_data)
    simulated_stream = np.zeros_like(shizuishanstream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = shizuishanstream_data[0] 

    for i in range(1, len(shizuishanstream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, shizuishanstream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * shizuishanstream_data[i] + \
                                         c1 * shizuishanstream_data[i-1] + \
                                         c2 * previous_flow
    
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.15)

    return simulated_stream

def muskingum_nonlinear_sanhuhekou(params, bayangaolestream_data):
    """三湖河口段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(bayangaolestream_data)    
    simulated_stream = np.zeros_like(bayangaolestream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = bayangaolestream_data[0] 

    for i in range(1, len(bayangaolestream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, bayangaolestream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * bayangaolestream_data[i] + \
                                         c1 * bayangaolestream_data[i-1] + \
                                         c2 * previous_flow
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 + 0.03)
        
    return simulated_stream

def muskingum_nonlinear_baotou(params, sanhuhekoustream_data):
    """包头段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(sanhuhekoustream_data)    
    simulated_stream = np.zeros_like(sanhuhekoustream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = sanhuhekoustream_data[0] 

    for i in range(1, len(sanhuhekoustream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, sanhuhekoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * sanhuhekoustream_data[i] + \
                                         c1 * sanhuhekoustream_data[i-1] + \
                                         c2 * previous_flow
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.02)
        
    return simulated_stream

def muskingum_nonlinear_toudaoguai(params, sanhuhekoustream_data):
    """头道拐段专用函数""" 
    k, x, a, b, c = params  # 接受幂次参数
    simulated_stream1 = np.zeros_like(sanhuhekoustream_data)
    simulated_stream = np.zeros_like(sanhuhekoustream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = sanhuhekoustream_data[0] 

    for i in range(1, len(sanhuhekoustream_data)):
        previous_flow = simulated_stream1[i-1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, sanhuhekoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * sanhuhekoustream_data[i] + \
                                         c1 * sanhuhekoustream_data[i-1] + \
                                         c2 * previous_flow
    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.02)
          
    return simulated_stream

# ---------- 参数定义 ----------
# 兰州段参数
params_lanzhou = [0.9974,	0.1593,	0.0586,	0.1295,	0.7299
]

# 下河沿段参数
params_xiaheyan = [1.0617,	0.3496,	0.0538,	0.1072,	0.147
]

# 青铜峡段参数
params_qingtongxia = [1.3369,	0.4798,	0.0228,	0.3047,	0.6955
]

# 石嘴山段参数
params_shizuishan = [1.2781,	0.2277,	0.1569,	0.0002,	0.5459
]

# 巴彦高勒段参数
params_bayangaole = [1.7758,	0.2075,	0.0802,	0.0789,	-0.0946
]

# 三湖河口段参数
params_sanhuhekou = [1.0937,	0.5155,	0.0244,	0.2699,	0.4313
]

# 包头段参数
params_baotou = [1.1383,	0.3418,	0.1114,	0.0515,	0.0623
]

# 头道拐段参数
params_toudaoguai = [0.8599,	0.4563,	0.0492,	0.1876,	0.3661
]


# 耦合两个模型
# 1. 将实时调度模型中刘家峡的出库流量作为洪水演进模型的输入流量
liujiaxiastream_data = Q_out_LJX.flatten()

# ---------- 改进后的反馈调整函数 ----------
def dynamic_adjust_step(deviation):
    """根据偏差值动态计算调整步长"""
    if deviation > 200:
        return 60
    elif deviation > 150:
        return 30
    else:
        return 10

def get_target_range(day_index, total_days):
    """动态目标范围函数"""
    if start_control_day < day_index < end_control_day:
        return (1850, 1900)  # 控制期目标范围
    else:
        return (800, 1800)  # 非控制期不限制

def adjust_liujiaxia_discharge(simulated_lanzhou, liujiaxiastream_data, total_days):
    adjusted = liujiaxiastream_data.copy()
    
    for i in range(len(simulated_lanzhou)):
        t_min, t_max = get_target_range(i, total_days)
        current_flow = simulated_lanzhou[i]
        
        if start_control_day <= i <= end_control_day:  # 只在控制时段调整
            if current_flow > t_max:
                excess = current_flow - t_max
                step = dynamic_adjust_step(excess)
                # 仅修改当前时段的刘家峡流量
                adjusted[i] = max(adjusted[i] - step, 0)
                
            elif current_flow < t_min:
                shortage = t_min - current_flow
                step = dynamic_adjust_step(shortage)
                # 仅修改当前时段的刘家峡流量
                adjusted[i] += step
    
    return adjusted

# 定义反馈修正控制时段内的凑峰调度
def run_real_time_scheduling_for_single_step(i):
    """
    仅更新指定时段的调度计算，用于反馈调整机制
    
    参数:
        i: 当前需要调整的时段索引
        use_real_time_scheduling1: 是否使用实时调度标志
    """
    global Q_out_LJX, Q_out_JSX, Q_out_GBX, Q_out_LJ, Q_out_LXW, Q_out_LYX
    global Zup_LJX, Zup_JSX, Zup_GBX, Zup_LJ, Zup_LXW, Zup_LYX
    global N_LJX, N_JSX, N_GBX, N_LJ, N_LXW, N_LYX
    global Q_ele_abandoned_LJX, Q_ele_abandoned_JSX, Q_ele_abandoned_GBX, Q_ele_abandoned_LJ, Q_ele_abandoned_LXW, Q_ele_abandoned_LYX
    global W_LJX, W_JSX, W_GBX, W_LJ, W_LXW, W_LYX
    
    # 获取当前时段需要的刘家峡流量（已调整后的值）
    Q_out_LJX[i] = liujiaxiastream_data[i]
    
    # 定义当前时段的支流来水
    hydStation_zq = floodProcess_zq.loc[i, flood_frequency]
    hydStation_hq = floodProcess_hq.loc[i, flood_frequency]
    
    # 1. 从刘家峡开始向上游更新各水库的状态
    # 刘家峡
    if i >= 1:
        W_LJX[i] = W_LJX[i-1]  # 前一时段的库容作为当前时段的初始库容
        Zup_LJX[i] = Zup_LJX[i-1]  # 前一时段的水位作为当前时段的初始水位
    else:
        W_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], Z_ini_LJX, 1)
        Zup_LJX[i] = Z_ini_LJX
    
    # 计算刘家峡的入库流量（需要考虑支流来水）
    Q_in_LJX[i] = Q_out_JSX[i] * (1 - Qloss_JSX_LJX[i].item()) \
                + hydStation_zq * (1 - Qloss_zq_LJX[i].item()) \
                + hydStation_hq * (1 - Qloss_hq_LJX[i].item())
    
    # 计算刘家峡的库容变化
    W_LJX[i] += (Q_in_LJX[i] - Q_out_LJX[i]) * 8.64 / 10000
    
    # 更新刘家峡的水位
    Zup_LJX[i] = interpolation_2D(Parameters_LJX['上游水位库容曲线'], W_LJX[i], 2)
    
    # 计算刘家峡的发电流量和弃水流量
    if Q_out_LJX[i] >= Q_MaxTroMachine['LJX']:
        Q_ele_LJX[i] = Q_MaxTroMachine['LJX']
        Q_ele_abandoned_LJX[i] = Q_out_LJX[i] - Q_MaxTroMachine['LJX']
    else:
        Q_ele_LJX[i] = Q_out_LJX[i]
        Q_ele_abandoned_LJX[i] = 0
    
    # 计算刘家峡的出力
    H_ele_LJX[i] = Zup_LJX[i] - interpolation_2D(Parameters_LJX['下泄流量下游水位曲线'], Q_out_LJX[i] / number_PowerStation['LJX'], 2)
    file_path = './水库特征数据集/刘家峡.xlsx'
    sheet_name = '水电站水头H-出力N-流量Q关系表'
    head_col = '水头'
    q_col = '过机流量'
    power_col = '出力'
    N_LJX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJX[i], Q_ele_LJX[i] / number_PowerStation['LJX']) * number_PowerStation['LJX']
    
    # 2. 更新积石峡的状态（受刘家峡调整影响）
    Q_out_JSX[i] = (Q_in_LJX[i] - hydStation_zq * (1 - Qloss_zq_LJX[i].item()) \
                       - hydStation_hq * (1 - Qloss_hq_LJX[i].item())) / (1 - Qloss_JSX_LJX[i].item())
    

    Zup_JSX[i] = Z_ini_JSX
    W_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], Z_ini_JSX, 1)
    Q_in_JSX[i] = Q_out_GBX[i] * (1 - Qloss_GBX_JSX[i].item())
    
    W_JSX[i] += (Q_in_JSX[i] - Q_out_JSX[i]) * 8.64 / 10000
    Zup_JSX[i] = interpolation_2D(Parameters_JSX['上游水位库容曲线'], W_JSX[i], 2)
    
    if Q_out_JSX[i] >= Q_MaxTroMachine['JSX']:
        Q_ele_JSX[i] = Q_MaxTroMachine['JSX']
        Q_ele_abandoned_JSX[i] = Q_out_JSX[i] - Q_MaxTroMachine['JSX']
    else:
        Q_ele_JSX[i] = Q_out_JSX[i]
        Q_ele_abandoned_JSX[i] = 0
    
    H_ele_JSX[i] = Zup_JSX[i] - interpolation_2D(Parameters_JSX['下泄流量下游水位曲线'], Q_out_JSX[i] / number_PowerStation['JSX'], 2)
    file_path = './水库特征数据集/积石峡.xlsx'
    N_JSX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_JSX[i], Q_ele_JSX[i] / number_PowerStation['JSX']) * number_PowerStation['JSX']
    
    # 3. 更新公伯峡的状态（受积石峡调整影响）
    Q_out_GBX[i] = Q_in_JSX[i] / (1 - Qloss_GBX_JSX[i].item())
    
    Zup_GBX[i] = Z_ini_GBX
    W_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], Z_ini_GBX, 1)
    
    Q_in_GBX[i] = Q_out_LJ[i] * (1 - Qloss_LJ_GBX[i].item())
    
    W_GBX[i] += (Q_in_GBX[i] - Q_out_GBX[i]) * 8.64 / 10000
    Zup_GBX[i] = interpolation_2D(Parameters_GBX['上游水位库容曲线'], W_GBX[i], 2)
    
    if Q_out_GBX[i] >= Q_MaxTroMachine['GBX']:
        Q_ele_GBX[i] = Q_MaxTroMachine['GBX']
        Q_ele_abandoned_GBX[i] = Q_out_GBX[i] - Q_MaxTroMachine['GBX']
    else:
        Q_ele_GBX[i] = Q_out_GBX[i]
        Q_ele_abandoned_GBX[i] = 0
    
    H_ele_GBX[i] = Zup_GBX[i] - interpolation_2D(Parameters_GBX['下泄流量下游水位曲线'], Q_out_GBX[i], 2)
    file_path = './水库特征数据集/公伯峡.xlsx'
    N_GBX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_GBX[i], Q_ele_GBX[i] / number_PowerStation['GBX']) * number_PowerStation['GBX']
    
    # 4. 更新李家峡的状态（受公伯峡调整影响）
    Q_out_LJ[i] = Q_in_GBX[i] / (1 - Qloss_LJ_GBX[i].item())
    
    Zup_LJ[i] = Z_ini_LJ
    W_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], Z_ini_LJ, 1)
    
    Q_in_LJ[i] = Q_out_LXW[i] * (1 - Qloss_LXW_LJ[i].item())
    
    W_LJ[i] += (Q_in_LJ[i] - Q_out_LJ[i]) * 8.64 / 10000
    Zup_LJ[i] = interpolation_2D(Parameters_LJ['上游水位库容曲线'], W_LJ[i], 2)
    
    if Q_out_LJ[i] >= Q_MaxTroMachine['LJ']:
        Q_ele_LJ[i] = Q_MaxTroMachine['LJ']
        Q_ele_abandoned_LJ[i] = Q_out_LJ[i] - Q_MaxTroMachine['LJ']
    else:
        Q_ele_LJ[i] = Q_out_LJ[i]
        Q_ele_abandoned_LJ[i] = 0
    
    H_ele_LJ[i] = Zup_LJ[i] - interpolation_2D(Parameters_LJ['下泄流量下游水位曲线'], Q_out_LJ[i], 2)
    file_path = './水库特征数据集/李家峡.xlsx'
    N_LJ[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LJ[i], Q_ele_LJ[i] / number_PowerStation['LJ']) * number_PowerStation['LJ']
    
    # 5. 更新拉西瓦的状态（受李家峡调整影响）
    Q_out_LXW[i] = Q_in_LJ[i] / (1 - Qloss_LXW_LJ[i].item())
    
    Zup_LXW[i] = Z_ini_LXW
    W_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], Z_ini_LXW, 1)
    
    Q_in_LXW[i] = Q_out_LYX[i] * (1 - Qloss_LYX_LXW[i].item())
    
    W_LXW[i] += (Q_in_LXW[i] - Q_out_LXW[i]) * 8.64 / 10000
    Zup_LXW[i] = interpolation_2D(Parameters_LXW['上游水位库容曲线'], W_LXW[i], 2)
    
    if Q_out_LXW[i] >= Q_MaxTroMachine['LXW']:
        Q_ele_LXW[i] = Q_MaxTroMachine['LXW']
        Q_ele_abandoned_LXW[i] = Q_out_LXW[i] - Q_MaxTroMachine['LXW']
    else:
        Q_ele_LXW[i] = Q_out_LXW[i]
        Q_ele_abandoned_LXW[i] = 0
    
    H_ele_LXW[i] = Zup_LXW[i] - interpolation_2D(Parameters_LXW['下泄流量下游水位曲线'], Q_out_LXW[i] / number_PowerStation['LXW'], 2)
    file_path = './水库特征数据集/拉西瓦.xlsx'
    N_LXW[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LXW[i], Q_ele_LXW[i] / number_PowerStation['LXW']) * number_PowerStation['LXW']
    
    # 6. 更新龙羊峡的状态（受拉西瓦调整影响）
    Q_out_LYX[i] = Q_in_LXW[i] / (1 - Qloss_LYX_LXW[i].item())
    
    if i >= 1:
        W_LYX[i] = W_LYX[i-1]
        Zup_LYX[i] = Zup_LYX[i-1]
    else:
        W_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], Z_ini_LYX, 1)
        Zup_LYX[i] = Z_ini_LYX
    
    Q_in_LYX[i] = floodProcess_tnh.loc[i, flood_frequency]  # 唐乃亥来水
    
    W_LYX[i] += (Q_in_LYX[i] - Q_out_LYX[i]) * 8.64 / 10000
    Zup_LYX[i] = interpolation_2D(Parameters_LYX['上游水位库容曲线'], W_LYX[i], 2)
    
    if Q_out_LYX[i] >= Q_MaxTroMachine['LYX']:
        Q_ele_LYX[i] = Q_MaxTroMachine['LYX']
        Q_ele_abandoned_LYX[i] = Q_out_LYX[i] - Q_MaxTroMachine['LYX']
    else:
        Q_ele_LYX[i] = Q_out_LYX[i]
        Q_ele_abandoned_LYX[i] = 0
    
    H_ele_LYX[i] = Zup_LYX[i] - interpolation_2D(Parameters_LYX['下泄流量下游水位曲线'], Q_out_LYX[i], 2)
    file_path = './水库特征数据集/龙羊峡.xlsx'
    N_LYX[i] = get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_ele_LYX[i], Q_ele_LYX[i] / number_PowerStation['LYX']) * number_PowerStation['LYX']
    
    # 根据NHQ曲线查出对应的出力，可能会高于额定出力，所以进行调整
    if N_LYX[i] >= 128:
        N_LYX[i] = 128
    else:
        pass       
    if N_LXW[i] >= 420:
        N_LXW[i] = 420
    else:
        pass
    if N_LJ[i] >= 160:
        N_LJ[i] = 160
    else:
        pass            
    if N_GBX[i] >= 150:
        N_GBX[i] = 150
    else:
        pass            
    if N_JSX[i] >= 150:
        N_JSX[i] = 150
    else:
        pass            
    if N_LJX[i] >= 122.5:
        N_LJX[i] = 122.5
    else:
        pass 
    
    # 7. 更新兰州断面模拟流量（受刘家峡调整影响）
    simulated_lanzhou[i] = muskingum_nonlinear_lanzhou(params_lanzhou, Q_out_LJX, mh_flow, xt_flow)[i]
    
    # 统一调整后的输出
    Q_out_LJX = liujiaxiastream_data.reshape(-1, 1)


# ---------- 改进后的反馈循环 ----------
max_iterations = 200
tolerance = 20  # 收敛容差缩小到20m³/s
total_days = number  # 假设 number 是模拟的总天数
start_control_day = 1  # 第6天（0-based索引）
end_control_day = total_days - 1  # 倒数第4天

# 绘制每次迭代后兰州断面的模拟流量
# 设置中文字体为宋体（核心配置）
plt.rcParams.update({
    'font.family': 'SimSun',  # 设置全局字体为宋体（解决中文显示方框问题）
    'font.size': 10,         # 全局默认字体大小为10pt
    'mathtext.fontset': 'stix',  # 数学公式字体集使用STIX（兼容Times New Roman风格）
    
    # 坐标轴标签样式
    'axes.labelsize': 14,    # 坐标轴标签字体大小
    'axes.titlesize': 14,    # 坐标轴标题字体大小

    # 坐标轴线宽样式
    'axes.linewidth': 3,     # 设置坐标轴线宽
    
    # 刻度标签样式
    'xtick.labelsize': 14,   # X轴刻度标签字体大小
    'ytick.labelsize': 14,   # Y轴刻度标签字体大小
    
    # 刻度标签长度
    'xtick.major.size': 8,   # 设置X轴刻度线长度
    'ytick.major.size': 8,   # 设置Y轴刻度线长度
    'xtick.major.width': 3,  # 设置X轴刻度线宽度
    'ytick.major.width': 3,  # 设置Y轴刻度线宽度
    
    # 图例样式
    'legend.fontsize': 10.5,   # 图例文本字体大小
    
    # 线条样式
    'lines.linewidth': 1.5,  # 默认线条宽度为1.5pt
    
    # 输出图像参数
    'figure.dpi': 300,       # 输出图像分辨率（每英寸点数）
    'figure.figsize': (2, 2)  # 默认图像尺寸（宽6.4英寸，高4.8英寸）
})
 
# 保存图片时的附加配置
mpl.rc('savefig', facecolor='white')  # 保存图片时强制设置背景为白色（避免透明背景）

def plot_lanzhou_flow_iterations(simulated_lanzhou_initial, simulated_lanzhou_history, iteration_count, output_dir='输出文件', legend_position=(0.05, 0.95)):
    """
    绘制兰州断面模拟流量的初始流量、每次迭代后的流量以及最终收敛的流量
    
    参数:
        simulated_lanzhou_initial: 初始模拟的兰州断面流量
        simulated_lanzhou_history: 每次迭代后的兰州断面流量历史记录
        iteration_count: 迭代次数
        output_dir: 输出目录，默认为“输出文件”
        legend_position: 图例的坐标位置，默认为(0.05, 0.95)
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 准备绘图数据
    days = np.arange(1, len(simulated_lanzhou_initial) + 1)
    control_start = 6  # 第6天（0-based索引为5）
    control_end = len(simulated_lanzhou_initial) - 4  # 倒数第4天（0-based索引为 len-5）
    
    # 创建图形和坐标轴对象
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制初始流量
    ax.plot(days, simulated_lanzhou_initial, label='初始模拟流量', color='gray', linestyle='--', alpha=0.7)
    
    # 绘制每次迭代后的流量，但不为每次迭代添加图例
    colors = plt.cm.viridis(np.linspace(0, 1, iteration_count))  # 根据迭代次数生成颜色映射
    iteration_label_added = False  # 标志，确保迭代过程标签只添加一次
    
    for idx in range(iteration_count):
        # 只为第一次迭代添加图例标签
        label = '迭代过程' if idx == 0 else ""
        ax.plot(days, simulated_lanzhou_history[idx], label=label, color=colors[idx])
    
    # 绘制最终收敛的流量
    final_flow = simulated_lanzhou_history[-1]
    ax.plot(days, final_flow, label='最终收敛流量', color='red', linewidth=2)
    
    # 添加控制期目标范围
    ax.axvspan(control_start, control_end, color='yellow', alpha=0.1, label='控制期')
    ax.axhline(y=1800, color='green', linestyle='-.', label='目标下限 (1800 m³/s)')
    ax.axhline(y=1900, color='purple', linestyle='-.', label='目标上限 (1900 m³/s)')
    
    # 设置坐标轴标签朝内
    ax.tick_params(axis='both', direction='in')
    
    # 添加图表元素
    ax.set_title(f'兰州断面{flood_frequency}一遇实时凑峰调度模拟流量迭代过程')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('流量 (m³/s)')
    
    # 将图例放置在指定的坐标位置
    ax.legend(bbox_to_anchor=legend_position, loc='center', frameon=False)
    
    # 添加注释和标记重要点
    max_initial = np.max(simulated_lanzhou_initial)
    max_final = np.max(final_flow)
    
    # 初始最大值注释
    initial_max_index = np.argmax(simulated_lanzhou_initial)
    ax.annotate(f'初始最大值: {max_initial:.0f} m³/s', 
                xy=(initial_max_index + 1, max_initial),
                xytext=(30, 2), textcoords='offset points',  # 向右和向上移动注释文本
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.5, headwidth=4))
    
    # 最终最大值注释
    final_max_index = np.argmax(final_flow)
    ax.annotate(f'最终最大值: {max_final:.0f} m³/s', 
                xy=(final_max_index + 1, max_final),
                xytext=(-90, -30), textcoords='offset points',  # 向左和向下移动注释文本
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.5, headwidth=4))
    
    # 调整布局并保存
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'兰州断面{flood_frequency}一遇实时凑峰调度模拟流量迭代过程.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图像以释放内存
    
    print(f"Flow iteration plot saved to {output_path}")

# 在反馈调整循环之后调用绘图函数
simulated_lanzhou_history = []

# 在反馈调整循环之后调用绘图函数
LJX_discharge_history = []

for iteration in range(max_iterations):
    # 运行洪水演进模型
    simulated_lanzhou = muskingum_nonlinear_lanzhou(params_lanzhou, liujiaxiastream_data, mh_flow, xt_flow)
    
    # 保存当前迭代的兰州断面流量到历史记录
    simulated_lanzhou_history.append(simulated_lanzhou.copy())
    
    # 保存当前迭代的刘家峡下泄流量到历史记录
    LJX_discharge_history.append(liujiaxiastream_data.copy())
    
    # 检查控制期流量
    max_deviation = 0
    for i in range(total_days):
        if start_control_day <= i <= end_control_day:
            t_min, t_max = get_target_range(i, total_days)
            flow = simulated_lanzhou[i]
            deviation = max(flow - t_max, t_min - flow, 0)
            max_deviation = max(max_deviation, deviation)

    # 服务化：每次反馈迭代向 /cb 推送进度与过程数据
    _cb_push("progress", {
        "job_id": RIVER_JOB_ID,
        "iteration": iteration + 1,
        "max_deviation": float(max_deviation),
        "progress_percent": round((iteration + 1) / max_iterations * 100, 2),
    })
    _cb_push("process_data", {
        "job_id": RIVER_JOB_ID,
        "iteration": iteration + 1,
        "liujiaxia_outflow": [float(v) for v in liujiaxiastream_data],
        "lanzhou_flow": [float(v) for v in simulated_lanzhou],
    })

    # 收敛检查
    if max_deviation <= tolerance:
        print(f"迭代 {iteration + 1}: 最大偏差 {max_deviation} ≤ {tolerance}，已收敛")
        break
     
    # 执行流量调整
    liujiaxiastream_data = adjust_liujiaxia_discharge(simulated_lanzhou, liujiaxiastream_data, total_days)

    # 仅重新计算受影响的时段
    for i in range(number):
        if start_control_day <= i <= end_control_day:
            run_real_time_scheduling_for_single_step(i)


# 保存刘家峡下泄流量和兰州断面模拟流量到Excel
# 合并刘家峡下泄流量和兰州断面模拟流量的历史记录
combined_data = {}
for iteration, (ljx_flow, lanzhou_flow) in enumerate(zip(LJX_discharge_history, simulated_lanzhou_history)):
    combined_data[f"刘家峡迭代{iteration + 1}"] = ljx_flow
    combined_data[f"兰州迭代{iteration + 1}"] = lanzhou_flow

combined_df = pd.DataFrame(combined_data)
combined_df.index = [f"时段{i + 1}" for i in range(len(combined_df.index))]
combined_file = f'输出文件/刘家峡下泄流量和兰州断面模拟流量{flood_frequency}一遇耦合反馈实时凑峰调度迭代过程.xlsx'
combined_df.to_excel(combined_file, index=True)
print(f"刘家峡下泄流量和兰州断面耦合反馈模拟流量迭代过程保存到 {combined_file}")

# 调用绘图函数时，可以指定图例的坐标位置
plot_lanzhou_flow_iterations(
    simulated_lanzhou_initial=simulated_lanzhou_history[0],
    simulated_lanzhou_history=simulated_lanzhou_history,
    iteration_count=len(simulated_lanzhou_history),
    legend_position=(0.10, 0.60)  # 图例位置设置为坐标 
)

# 显示图像（如果需要即时查看）
plt.show()


# 将实时调度模型中刘家峡的出库流量作为洪水演进模型的输入流量
liujiaxiastream_data = Q_out_LJX.flatten()

# 2. 调用洪水演进模型计算兰州断面的模拟流量
simulated_lanzhou = muskingum_nonlinear_lanzhou(params_lanzhou, liujiaxiastream_data, mh_flow, xt_flow)

# 下河沿段计算（输入：兰州模拟流量 + 靖远支流）
simulated_xiaheyan = muskingum_nonlinear_xiaheyan(params_xiaheyan, simulated_lanzhou)

# 青铜峡段计算（输入：下河沿模拟流量 + 泉眼山支流）
simulated_qingtongxia = muskingum_nonlinear_qingtongxia(params_qingtongxia, simulated_xiaheyan)

# 石嘴山段计算
simulated_shizuishan = muskingum_nonlinear_shizuishan(params_shizuishan, simulated_qingtongxia)

# 巴彦高勒段计算
simulated_bayangaole = muskingum_nonlinear_bayangaole(params_bayangaole, simulated_shizuishan)

# 三湖河口段计算
simulated_sanhuhekou = muskingum_nonlinear_sanhuhekou(params_sanhuhekou, simulated_bayangaole)

# 包头段计算
simulated_baotou = muskingum_nonlinear_baotou(params_baotou, simulated_sanhuhekou)

# 头道拐段计算
simulated_toudaoguai = muskingum_nonlinear_toudaoguai(params_toudaoguai, simulated_baotou)


# 创建一个空的DataFrame
output_df = pd.DataFrame()

# 确保所有数组的长度一致
length = number + 1  # 10

# 添加龙羊峡调度过程
output_df['龙羊峡水位变化'] = Zup_LYX.flatten()[:length]
output_df['龙羊峡出力过程'] = N_LYX.flatten()[:length]
output_df['龙羊峡入库流量'] = Q_in_LYX.flatten()[:length]
output_df['龙羊峡下泄流量'] = Q_out_LYX.flatten()[:length]
output_df['龙羊峡弃水量'] = Q_ele_abandoned_LYX.flatten()[:length]

# 添加拉西瓦调度过程
output_df['拉西瓦水位变化'] = Zup_LXW.flatten()[:length]
output_df['拉西瓦出力过程'] = N_LXW.flatten()[:length]
output_df['拉西瓦入库流量'] = Q_in_LXW.flatten()[:length]
output_df['拉西瓦下泄流量'] = Q_out_LXW.flatten()[:length]
output_df['拉西瓦弃水量'] = Q_ele_abandoned_LXW.flatten()[:length]

# 添加李家峡调度过程
output_df['李家峡水位变化'] = Zup_LJ.flatten()[:length]
output_df['李家峡出力过程'] = N_LJ.flatten()[:length]
output_df['李家峡入库流量'] = Q_in_LJ.flatten()[:length]
output_df['李家峡下泄流量'] = Q_out_LJ.flatten()[:length]
output_df['李家峡弃水量'] = Q_ele_abandoned_LJ.flatten()[:length]

# 添加公伯峡调度过程
output_df['公伯峡水位变化'] = Zup_GBX.flatten()[:length]
output_df['公伯峡出力过程'] = N_GBX.flatten()[:length]
output_df['公伯峡入库流量'] = Q_in_GBX.flatten()[:length]
output_df['公伯峡下泄流量'] = Q_out_GBX.flatten()[:length]
output_df['公伯峡弃水量'] = Q_ele_abandoned_GBX.flatten()[:length]

# 添加积石峡调度过程
output_df['积石峡水位变化'] = Zup_JSX.flatten()[:length]
output_df['积石峡出力过程'] = N_JSX.flatten()[:length]
output_df['积石峡入库流量'] = Q_in_JSX.flatten()[:length]
output_df['积石峡下泄流量'] = Q_out_JSX.flatten()[:length]
output_df['积石峡弃水量'] = Q_ele_abandoned_JSX.flatten()[:length]

# 添加刘家峡峡调度过程
output_df['刘家峡水位变化'] = Zup_LJX.flatten()[:length]
output_df['刘家峡出力过程'] = N_LJX.flatten()[:length]
output_df['刘家峡入库流量'] = Q_in_LJX.flatten()[:length]
output_df['刘家峡下泄流量'] = Q_out_LJX.flatten()[:length]
output_df['刘家峡弃水量'] = Q_ele_abandoned_LJX.flatten()[:length]

# 在 run_real_time_scheduling 函数的循环中动态获取每日流量
zq_flow = []
hq_flow = []
mh_flow = []
xt_flow = []

for i in range(number):
    # 获取当前时段的支流来水值
    hydStation_zq = floodProcess_zq.loc[i, flood_frequency]
    hydStation_hq = floodProcess_hq.loc[i, flood_frequency]
    hydStation_mh = floodProcess_mh.loc[i, flood_frequency]
    hydStation_xt = floodProcess_xt.loc[i, flood_frequency]
    
    # 添加各支流来水过程
    zq_flow.append(hydStation_zq)  # 添加折桥水文站来水
    hq_flow.append(hydStation_hq)  # 添加红旗水文站来水
    mh_flow.append(hydStation_mh)  # 添加民和水文站来水
    xt_flow.append(hydStation_xt)  # 添加享堂水文站来水

# 添加各支流来水过程
output_df['折桥水文站来水过程'] = zq_flow[:length]
output_df['红旗水文站来水过程'] = hq_flow[:length]
output_df['民和水文站来水过程'] = mh_flow[:length]
output_df['享堂水文站来水过程'] = xt_flow[:length]

# 添加兰州段数据
output_df['兰州模拟流量'] = simulated_lanzhou

# 添加下河沿段数据
output_df['下河沿模拟流量'] = simulated_xiaheyan

# 添加青铜峡段数据
output_df['青铜峡模拟流量'] = simulated_qingtongxia


# 添加石嘴山段数据
output_df['石嘴山模拟流量'] = simulated_shizuishan

# 添加巴彦高勒段数据
output_df['巴彦高勒模拟流量'] = simulated_bayangaole


# 添加三湖河口段数据
output_df['三湖河口模拟流量'] = simulated_sanhuhekou

# 添加包头段数据
output_df['包头模拟流量'] = simulated_baotou

# 添加头道拐段数据
output_df['头道拐模拟流量'] = simulated_toudaoguai
  
# 确保存储路径存在
import os
if not os.path.exists('输出文件'):
    os.makedirs('输出文件')

# 保存到Excel
output_file = f'输出文件/龙拉李公积刘{flood_frequency}一遇耦合反馈实时凑峰调度串联模拟.xlsx'
output_df.to_excel(output_file, index=False)

print(f"Simulated data saved to {output_file}")


def run_sediment_model(Q_in, Q_out):
    """
    水动力冲淤计算模型
    参数:
        Q_in: 包头流量序列 (m³/s)
        Q_out: 头道拐流量序列 (m³/s)
    """
    # ---------- 0. 固定断面参数+输沙率 ----------
    BASE_XLSX = os.path.join(os.path.dirname(__file__), '场次洪水过程', '断面参数.xlsx')
    if not os.path.exists(BASE_XLSX):
        raise FileNotFoundError('请将"断面参数.xlsx"放在"场次洪水过程"文件夹中！')

    tbl_seg = pd.read_excel(BASE_XLSX, sheet_name='断面参数', header=0)
    tbl_sed = pd.read_excel(BASE_XLSX, sheet_name='输沙率', header=0)

    # ---------- 1. 获取流量数据 ----------
    Q_in = np.array(Q_in);
    Q_out = np.array(Q_out)
    T = len(Q_in)
    time = np.arange(1, T + 1)

    # ---------- 2. 读输沙率 ----------
    Qs_in = tbl_sed['包头输沙率(t/s)'].values[:T]
    Qs_out = tbl_sed['头道拐输沙率(t/s)'].values[:T]
    if np.all(pd.isna(Qs_out)):
        Qs_out = Qs_in * 0.95

    # ---------- 3. 读断面参数 ----------
    Nx = len(tbl_seg)
    L_seg = tbl_seg['段长(km)'].values * 1000
    Bc_seg = tbl_seg['主槽宽(m)'].values
    Bt_seg = tbl_seg['滩地宽(m)'].values
    Jc_seg = tbl_seg['主槽比降(0/000)'].values / 1000
    Jt_seg = tbl_seg['滩地比降(0/000)'].values / 1000
    nc_seg = tbl_seg['主槽糙率'].values
    nt_seg = tbl_seg['滩地糙率'].values
    Zc0_seg = tbl_seg['初始主槽床高(m)'].values
    Zt0_seg = tbl_seg['初始滩地床高(m)'].values

    # ---------- 4. 计算参数 ----------
    g = 9.81;
    gamma_s = 1.4e3;
    omega_t = 2e-4;
    K = 1.75
    Delta_t = 86400  # 日尺度
    a_seg = 3.037;
    b_seg = 0.979

    # 变量初始化
    Q = np.zeros((Nx, T));
    Qs = np.zeros((Nx, T))
    Qc = np.zeros((Nx, T));
    Qt = np.zeros((Nx, T))
    Zc = np.zeros((Nx, T));
    Zt = np.zeros((Nx, T))
    DeltaZc = np.zeros((Nx, T));
    DeltaZt = np.zeros((Nx, T))
    total_seg = np.zeros((Nx, T))
    Zc[:, 0] = Zc0_seg;
    Zt[:, 0] = Zt0_seg
    Q[0, :] = Q_in;
    Qs[0, :] = Qs_in

    # 区间汇入
    Q_branch = np.zeros((Nx, T))
    Qs_branch = np.zeros((Nx, T))
    for tt in range(T):
        dq = (Q_out[tt] - Q_in[tt]) / Nx
        dqs = (Qs_out[tt] - Qs_in[tt]) / Nx
        Q_branch[:, tt] = dq
        Qs_branch[:, tt] = dqs

    # 牛顿迭代
    def solve_flow_balance(Q_val, Bc, Bt, Jc, Jt, nc, nt, Zc, Zt):
        Ht = max(Q_val / ((Bc + Bt) * 10), 0.01)
        tol = 1e-3;
        maxIt = 200
        for _ in range(maxIt):
            base_c = max(Zc - Zt + Ht, 1e-3);
            base_t = max(Ht, 1e-3)
            Qc = (Bc * np.sqrt(Jc) / nc) * base_c ** (5 / 3)
            Qt = (Bt * np.sqrt(Jt) / nt) * base_t ** (5 / 3)
            F = Qc + Qt - Q_val
            if abs(F) < tol: return Ht, True
            dQc = (5 / 3) * (Bc * np.sqrt(Jc) / nc) * base_c ** (2 / 3)
            dQt = (5 / 3) * (Bt * np.sqrt(Jt) / nt) * base_t ** (2 / 3)
            Ht = max(Ht - F / (dQc + dQt), 1e-3)
        return Ht, False

    # 主循环
    for tt in range(1, T):
        for i in range(1, Nx):
            Q[i, tt] = Q[i - 1, tt] + Q_branch[i, tt]
            Qs[i, tt] = Qs[i - 1, tt] + Qs_branch[i, tt]
        for i in range(Nx):
            Ht, _ = solve_flow_balance(
                Q[i, tt], Bc_seg[i], Bt_seg[i], Jc_seg[i], Jt_seg[i],
                nc_seg[i], nt_seg[i], Zc[i, tt - 1], Zt[i, tt - 1])

            Qc[i, tt] = (Bc_seg[i] * np.sqrt(Jc_seg[i]) / nc_seg[i]) * \
                        max(Zc[i, tt - 1] - Zt[i, tt - 1] + Ht, 1e-3) ** (5 / 3)
            Qt[i, tt] = (Bt_seg[i] * np.sqrt(Jt_seg[i]) / nt_seg[i]) * \
                        max(Ht, 1e-3) ** (5 / 3)

            Qs_cap = a_seg * Q[i, tt] ** b_seg
            dz_main = max(Zc[i, tt - 1] - Zt[i, tt - 1], 1e-3)
            DeltaZc[i, tt] = (Qs[i, tt - 1] - Qs_cap) * Delta_t / \
                             (Bc_seg[i] * dz_main * gamma_s)
            if Zc[i, tt - 1] <= Zt[i, tt - 1]: DeltaZc[i, tt] = 0.

            Vt = Qt[i, tt] / (Bt_seg[i] * max(Ht, 1e-3))
            sedOut = Vt * Bt_seg[i] * omega_t
            sedIn_t = (Qs[i, tt - 1] - Qs_cap) * (1 / (1 + K))
            DeltaZt[i, tt] = (sedIn_t - sedOut) / (Bt_seg[i] * max(Ht, 1e-3) * gamma_s)

            Zc[i, tt] = Zc[i, tt - 1] + DeltaZc[i, tt]
            Zt[i, tt] = Zt[i, tt - 1] + DeltaZt[i, tt]
            total_seg[i, tt] = total_seg[i, tt - 1] + \
                               DeltaZc[i, tt] * Bc_seg[i] + DeltaZt[i, tt] * Bt_seg[i]

    # 控制台汇总
    # 控制台汇总
    print('\n==== 各段冲淤（8 段）====')
    for i in range(Nx):
        print(f'段{i + 1:2d} 长{L_seg[i] / 1000:6.2f} km  总冲淤{total_seg[i, -1]:10.2f} m³')
    total_sum = sum(total_seg[:, -1])
    print(f'全河段合计 {total_sum:12.2f} m³')

    # 准备Excel汇总数据
    output_dir = '输出文件'
    os.makedirs(output_dir, exist_ok=True)

    excel_path = os.path.join(output_dir, f'耦合冲淤过程_{flood_frequency}一遇.xlsx')

    # 创建汇总表
    summary_data = {
        '段号': [f'段{i + 1}' for i in range(Nx)],
        '段长(km)': L_seg / 1000,
        '总冲淤量(m³)': [total_seg[i, -1] for i in range(Nx)]
    }

    # 添加合计行
    summary_data['段号'] = np.append(summary_data['段号'], '全河段合计')
    summary_data['段长(km)'] = np.append(summary_data['段长(km)'], np.nan)  # 合计行不显示长度
    summary_data['总冲淤量(m³)'] = np.append(summary_data['总冲淤量(m³)'], total_sum)

    df_summary = pd.DataFrame(summary_data)

    # 保存到Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='冲淤汇总', index=False)

    print(f"\n冲淤汇总数据已保存至: {excel_path}")

    return total_seg, L_seg

# ==================== 模型耦合执行 ====================

# 检查输出目录
if not os.path.exists('输出文件'):
    os.makedirs('输出文件')


# 执行冲淤计算（使用调度结果）
run_sediment_model(Q_in=simulated_baotou, Q_out=simulated_toudaoguai)

print("\n耦合模型计算完成！")