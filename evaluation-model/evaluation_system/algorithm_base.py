# algorithm_base.py
# -*- coding: utf-8 -*-
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np
from .unified_config import UnifiedConfig
from .unified_output import UnifiedOutput


class BaseAlgorithm(ABC):
    """算法基类 - 所有算法的统一接口"""

    def __init__(self, name: str, config: UnifiedConfig = None):
        """
        初始化算法基类

        Args:
            name: 算法名称
            config: 统一配置管理器
        """
        self.name = name
        self.config = config or UnifiedConfig()
        self.output = UnifiedOutput(self.config)
        self.logger = logging.getLogger(f'Algorithm.{name}')
        self.data_matrix = None
        self.original_data_matrix = None  # 新增：原始数据矩阵

    @abstractmethod
    def algorithm_core_calculation(self, data_source) -> Dict[str, Any]:
        """
        算法核心计算模块

        Args:
            data_source: 数据源

        Returns:
            Dict: 算法结果
        """
        pass

    def algorithm_result_save(self, results: Dict[str, Any]) -> str:
        """
        算法结果保存模块

        Args:
            results: 算法结果

        Returns:
            str: 输出目录路径
        """
        return self.output.output_algorithm_result_save(self.name, results)

    def algorithm_optimization_config_get(self) -> Dict[str, Any]:
        """
        算法优化配置获取

        Returns:
            Dict: 优化配置
        """
        opt_config = self.config.config_get('optimization').copy()

        # 动态更新维度
        if self.data_matrix is not None:
            actual_nd = self.data_matrix.shape[1]
            self.config.config_optimization_dimension_update(actual_nd)
            opt_config = self.config.config_get('optimization').copy()

        # 转换为numpy数组
        opt_config['Lb'] = np.array(opt_config['Lb'])
        opt_config['Ub'] = np.array(opt_config['Ub'])

        return opt_config

    def algorithm_data_validate(self, data_matrix: np.ndarray) -> bool:
        """
        算法数据验证

        Args:
            data_matrix: 数据矩阵

        Returns:
            bool: 数据是否有效
        """
        if data_matrix is None:
            self.logger.error("数据矩阵为空")
            return False

        if not isinstance(data_matrix, np.ndarray):
            self.logger.error("数据矩阵必须是numpy数组")
            return False

        if data_matrix.ndim != 2:
            self.logger.error("数据矩阵必须是二维数组")
            return False

        if np.any(np.isnan(data_matrix)) or np.any(np.isinf(data_matrix)):
            self.logger.warning("数据矩阵包含NaN或无穷值")

        self.logger.info(f"数据验证通过，形状: {data_matrix.shape}")
        return True

    def algorithm_data_matrix_set(self, data_matrix: np.ndarray, original_matrix: np.ndarray = None):
        """
        设置数据矩阵

        Args:
            data_matrix: 标准化数据矩阵（用于计算）
            original_matrix: 原始数据矩阵（用于输出，可选）
        """
        if self.algorithm_data_validate(data_matrix):
            self.data_matrix = data_matrix
            if original_matrix is not None:
                self.original_data_matrix = original_matrix
            else:
                self.original_data_matrix = data_matrix.copy()  # 如果没有提供，则使用标准化矩阵的副本
            self.logger.info(f"数据矩阵设置完成: 标准化{data_matrix.shape}, 原始{self.original_data_matrix.shape}")
        else:
            raise ValueError("数据矩阵验证失败")