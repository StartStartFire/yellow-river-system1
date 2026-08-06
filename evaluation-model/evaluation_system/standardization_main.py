# data/standardization_main.py
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from .standardization_algorithm import data_parameters_read
from .standardization_algorithm import data_indicators_calculate
from .standardization_algorithm import data_results_save


def standardization_main(data_frame: pd.DataFrame) -> tuple:
    """
        主体控制函数 - 标准化处理主程序

    Args:
        data_frame: 包含输入数据的DataFrame

    Returns:
        tuple: (标准化后的指标矩阵, 原始参数矩阵)
               标准化矩阵：每行对应一个样本，每列对应一个指标
               原始矩阵：每行对应一个样本，每列对应一个原始参数
    """
    # 1. 参数输入 - 保存原始矩阵
    params, inverse_indices = data_parameters_read(data_frame)
    if params is None:
        raise ValueError("参数读取失败")

    # 保存原始参数矩阵（转置前）
    original_matrix = params.T.copy()  # 转置为(样本数, 参数数)

    # 2. 指标化计算
    normalized_indicators = data_indicators_calculate(params, inverse_indices)

    # 转置矩阵，使每行对应一个样本，每列对应一个指标
    result_matrix = normalized_indicators.T

    return result_matrix, original_matrix


# 如果直接运行此脚本，则执行使用示例
if __name__ == "__main__":
    try:
        # 使用示例：从Excel文件读取数据
        data_frame = pd.read_excel('evaluation.xlsx', sheet_name='sheet1')

        # 调用主控制函数
        result_matrix, original_matrix = standardization_main(data_frame)

        # 保存结果到文件
        data_results_save(result_matrix, '../../p1.txt')

        # 同时保存原始矩阵
        np.savetxt('original_matrix.txt', original_matrix, delimiter='\t', fmt='%.6f')

        print("标准化处理完成")

    except Exception as e:
        print(f"程序执行错误: {e}")