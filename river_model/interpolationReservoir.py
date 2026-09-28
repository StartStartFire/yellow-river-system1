import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.spatial import cKDTree

def interpolation_2D(sample, point, idex=1):
    '''
    根据2 columns的DataFrame构建插值函数：
    sample是n*2的矩阵
    当idex=1时（默认），以x为横坐标，y为纵坐标，
    当idex=2时，以y为横坐标，x为纵坐标
    '''
    assert isinstance(sample, pd.DataFrame), "sample must be a pandas DataFrame"
    if idex == 1:
        x = sample.iloc[:, 0]
        y = sample.iloc[:, 1]
        f = interp1d(x, y, bounds_error=False, fill_value="extrapolate")
        return f(point)
    elif idex == 2:
        x = sample.iloc[:, 1]
        y = sample.iloc[:, 0]
        f = interp1d(x, y, bounds_error=False, fill_value="extrapolate")
        return f(point)
    else:
        raise ValueError("idex must be 1 or 2")
    
def get_power_output(file_path, sheet_name, head_col, q_col, power_col, H_cal, Q_cal):
    """
    根据计算得出的水头和过机流量查询其对应的出力值。
    查询逻辑：先查找水头最接近 H_cal 的行，再在这些行内查找过机流量最接近 Q_cal 的行，最后返回对应的出力。
    
    参数:
    file_path -- Excel文件的路径
    sheet_name -- 表名
    head_col -- 水头列的名称
    q_col -- 过机流量列的名称
    power_col -- 出力列的名称
    H_cal -- 计算得出的水头值
    Q_cal -- 计算得出的过机流量值
    
    返回:
    对应的出力值，如果没有匹配项，则返回None。
    """
    # 读取Excel文件
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # 确保H_cal和Q_cal是标量
    if isinstance(H_cal, np.ndarray):
        H_cal = H_cal[0]
    if isinstance(Q_cal, np.ndarray):
        Q_cal = Q_cal[0]
    
    # 计算水头列与目标水头的绝对差值
    df['head_diff'] = abs(df[head_col] - H_cal)
    
    # 找到水头差值最小的行
    min_head_diff = df['head_diff'].min()
    closest_head_rows = df[df['head_diff'] == min_head_diff]
    
    # 如果水头差值最小的行不止一行，计算过机流量列与目标过机流量的绝对差值，找到过机流量最接近的行
    if len(closest_head_rows) == 1:
        closest_row = closest_head_rows
    else:
        closest_head_rows['q_diff'] = abs(closest_head_rows[q_col] - Q_cal)
        min_q_diff = closest_head_rows['q_diff'].min()
        closest_row = closest_head_rows[closest_head_rows['q_diff'] == min_q_diff]
    
    # 如果仍然有多个行，选择第一个
    if len(closest_row) > 1:
        closest_row = closest_row.iloc[[0]]
    
    # 返回对应的出力值
    if not closest_row.empty:
        return closest_row[power_col].values[0]
    else:
        return None