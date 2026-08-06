# data/standardization_algorithm.py
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def data_parameters_read(data_frame: pd.DataFrame):
    """
    参数输入模块 - 从DataFrame读取数据

    Args:
        data_frame: 包含数据的DataFrame

    Returns:
        tuple: (参数矩阵, 需要取倒数的参数索引列表)
    """
    try:
        # 直接从传入的DataFrame中提取数据
        params = data_frame.iloc[0:100, 0:22].values.T  # 转置以便每行对应一个参数

        # 指定需要取倒数的参数索引（0-based）
        inverse_indices = [0, 1, 2, 3, 4, 5, 10, 11, 15, 17, 19, 21]

        return params, inverse_indices

    except Exception as e:
        print(f"读取数据错误: {e}")
        return None, []


def data_min_max_normalize(data: np.ndarray, inverse: bool = False) -> np.ndarray:
    """
    最小-最大归一化函数

    Args:
        data: 输入数据
        inverse: 是否取倒数

    Returns:
        np.ndarray: 归一化后的数据
    """
    if inverse:
        # 避免除0错误
        data = np.where(data != 0, 1.0 / data, 1.0)

    data_min = np.min(data)
    data_max = np.max(data)

    if data_min == data_max:
        return np.full_like(data, 0.5, dtype=float)
    else:
        normalized = (data - data_min) / (data_max - data_min)
        # 处理NaN值（除0等情况）
        normalized = np.nan_to_num(normalized, nan=1.0)
        return normalized


def data_indicators_calculate(params: np.ndarray, inverse_indices: list) -> np.ndarray:
    """
    指标化计算模块 - 对参数进行归一化处理

    Args:
        params: 参数矩阵
        inverse_indices: 需要取倒数的参数索引列表

    Returns:
        np.ndarray: 归一化后的指标矩阵
    """
    num_params, num_samples = params.shape
    normalized_indicators = np.zeros((num_params, num_samples))

    # 对每个参数进行归一化处理
    for i in range(num_params):
        inverse_flag = i in inverse_indices
        normalized_indicators[i] = data_min_max_normalize(params[i], inverse=inverse_flag)

    return normalized_indicators


def data_results_save(result_matrix: np.ndarray, output_file: str = 'p1.txt'):
    """
    结果输出模块 - 将结果矩阵保存到文件

    Args:
        result_matrix: 结果矩阵
        output_file: 输出文件名
    """
    # 保存到文件
    np.savetxt(output_file, result_matrix, delimiter='\t', fmt='%.6f')