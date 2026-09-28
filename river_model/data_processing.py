import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler 

###############平滑处理###############
def smoothing(data,percentage):
    '''
    平滑时间序列，对波动距离的区域进行处理，使相邻的数据点之间距离小于阈值
    
    param data: 待平滑的数据
    param percentage: 阈值
    return: 平滑后的数据
    '''
    # 复制原始数据以避免修改原数据
    cleaned_data = data.copy()
    # 遍历数据, 从第二个元素到倒数第二个元素
    for i in range(1,len(cleaned_data)-1):
        current = cleaned_data[i]
        prev = cleaned_data[i - 1]
        next = cleaned_data[i + 1]
        if cleaned_data[i] != 0 and prev != 0 and next != 0:    
            # 计算与前后数据的百分比差距
            diff_prev = abs((current - prev) / prev) * 100 
            diff_next = abs((current - next) / next) * 100 
            if diff_prev > percentage and diff_next > percentage:
                cleaned_data[i] = (prev + next) / 2
        else:
            continue
            
    return cleaned_data
###############异常值处理###############
def outlier_detection(timeseries, factor=1.5):
    '''
    计算IQR和识别异常值。
    
    - timeseries: 输入时间序列数据
    - factor: 用于计算IQR界限的乘数因子，默认为1.5
    - return: 包含异常值索引的numpy数组
    '''
    Q1 = np.percentile(timeseries, 25)
    Q3 = np.percentile(timeseries, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor*IQR
    upper_bound = Q3 + factor*IQR
     
    return np.where((timeseries < lower_bound) | (timeseries > upper_bound))[0]

import numpy as np
import matplotlib.pyplot as plt

def outlier_detection_pro(timeseries, factor=1.5):
    '''
    计算IQR并识别异常值，同时在原始时间序列图上标注异常点。
    
    - timeseries: 输入时间序列数据
    - factor: 用于计算IQR界限的乘数因子，默认为1.5
    - return: 包含异常值索引的numpy数组
    '''
    # 原始索引
    original_indices = np.arange(len(timeseries))

    # 计算IQR
    Q1 = np.percentile(timeseries, 25)
    Q3 = np.percentile(timeseries, 75)
    IQR = Q3 - Q1
    lower_bound = 50
    upper_bound = Q3 + factor * IQR

    # 找到异常值的索引
    outliers_index = np.where((timeseries < lower_bound) | (timeseries > upper_bound))[0]

    # 绘制时间序列
    plt.figure(figsize=(14, 7))
    plt.plot(original_indices, timeseries, label='Time Series', color='blue')

    # 标注异常值
    plt.scatter(outliers_index, timeseries[outliers_index], color='red', label='Outliers')

    # 设置边界线
    x_range = np.arange(len(timeseries))
    plt.plot(x_range, [lower_bound]*len(x_range), 'g--', linewidth=2, label='Lower Bound')
    plt.plot(x_range, [upper_bound]*len(x_range), 'g--', linewidth=2, label='Upper Bound')

    plt.legend()
    plt.title('Time Series with Outliers')
    plt.show()

    return outliers_index

def outlierHanding(timeseries, outliers, window_size=5):
    '''
    使用平滑窗口替换异常值
    
    - timeseries: 输入时间序列数据
    - outliers: 包含异常值索引的numpy数组
    - window_size: 平滑窗口的大小，默认为5
    - return: 异常值被替换后的numpy数组
    '''
    smoothed_data = np.copy(timeseries)
    for idx in outliers:
        # 确保窗口不超过数据边界
        start_idx = max(0, idx - (window_size // 2))
        end_idx = min(len(timeseries), idx + (window_size // 2) + 1)
        
        # 使用窗口内的中位数替换异常值  
        smoothed_data[idx] = np.median(timeseries[start_idx:end_idx])
    return smoothed_data

###############标准化处理###############
def normalization(timeseries):
    '''
    标准化处理（Standardization）是通过对原始数据进行数学变换，使其均值为0，标准差为1的过程。
    这种变换可以消除不同特征之间的量纲差异，使数据更易于处理和分析。
    对于时间序列数据而言，标准化可以帮助我们更好地理解数据的波动性和趋势
      
    - timeseries (pd.Series): 包含时间序列数据的Pandas Series对象。    
    - return: 标准化后的时间序列数据。
    '''
    # 确保输入是Pandas Series  
    if not isinstance(timeseries, pd.Series): 
        timeseries = pd.Series(timeseries)  
    # 将Pandas Series转换为二维NumPy数组，因为StandardScaler需要二维输入  
    values = timeseries.values.reshape(-1, 1)
    # 初始化StandardScaler  
    scaler = StandardScaler()
    # 拟合和转换数据  
    scaled_values = scaler.fit_transform(values)
    # 将结果转换回Pandas Series，并保留原始索引  
    scaled_timeseries = pd.Series(scaled_values.flatten(), index=timeseries.index)  
      
    return scaled_timeseries  
  
##############
import openpyxl

def write_to_excel(file_path, sheet_name, row, col, value):
    # 尝试打开Excel文件
    try:
        workbook = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        # 如果文件不存在，创建一个新的工作簿
        workbook = openpyxl.Workbook()
        # 移除默认创建的空表
        workbook.remove(workbook.active)
    
    # 如果表不存在，创建一个新的表
    if sheet_name not in workbook.sheetnames:
        sheet = workbook.create_sheet(title=sheet_name)
    else:
        sheet = workbook[sheet_name]
    
    # 将值写入指定位置
    sheet.cell(row=row, column=col, value=value)
    
    # 保存工作簿
    workbook.save(file_path)
