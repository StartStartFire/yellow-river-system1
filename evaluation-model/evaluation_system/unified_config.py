# unified_config.py
# -*- coding: utf-8 -*-
import numpy as np
import logging
import os
from typing import Dict, Any, Union


class UnifiedConfig:
    """统一配置管理器 - 内置所有配置，不依赖外部文件"""

    # 算法类型定义
    ALGORITHMS = {
        'NMF': '非负矩阵分解布谷鸟搜索',
        'PP': '投影寻踪布谷鸟搜索',
        'AHP_FUZZY': 'AHP模糊综合评价',
        'ALL': '所有算法'
    }

    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        初始化统一配置管理器

        Args:
            config_dict: 可选的配置字典，用于覆盖默认配置
        """
        self.configs = self.config_default_load()

        # 如果提供了配置字典，则更新默认配置
        if config_dict:
            self._deep_update(self.configs, config_dict)

        self.config_logging_setup()

    def config_default_load(self) -> Dict[str, Any]:
        """配置默认加载"""
        return {
            'common': {
                'data_source': 'evaluation.xlsx',
                'sheet_name': 'sheet1',
                'output_dir': 'results',
                'log_level': 'INFO',
                'silent_mode': True
            },
            'optimization': {
                'nd': 22,
                'N_pop': 100,
                'N_IterTotal': 500,
                'Lb': [0.0] * 22,
                'Ub': [1.0] * 22,
                'accuracy': -np.inf
            },
            'fuzzy': {
                'ahp_comparisons': {
                    (0, 1): 5 / 2, (0, 2): 5 / 3, (0, 3): 5 / 5, (0, 4): 5 / 4,
                    (1, 2): 2 / 3, (1, 3): 2 / 5, (1, 4): 2 / 4,
                    (2, 3): 3 / 5, (2, 4): 3 / 4,
                    (3, 4): 5 / 4
                },
                'subsystem_config': {
                    'water': {
                        'name': '水子系统',
                        'indices': slice(0, 6),  # 使用切片而不是列表
                        'weights': [0.3, 0.3, 0.1, 0.1, 0.1, 0.1]
                    },
                    'sand': {
                        'name': '沙子系统',
                        'indices': slice(6, 8),  # 使用切片而不是列表
                        'weights': [0.75, 0.25]
                    },
                    'energy': {
                        'name': '能子系统',
                        'indices': slice(8, 13),  # 使用切片而不是列表
                        'weights': [0.235, 0.235, 0.176, 0.176, 0.176]
                    },
                    'disaster': {
                        'name': '灾子系统',
                        'indices': slice(13, 16),  # 使用切片而不是列表
                        'weights': [0.333, 0.333, 0.333]
                    },
                    'ecology': {
                        'name': '生子系统',
                        'indices': slice(16, 22),  # 使用切片而不是列表
                        'weights': [0.25, 0.25, 0.167, 0.167, 0.083, 0.083]
                    }
                }
            },
            # 在output配置部分添加：
            'output': {
                # 可视化配置
                'save_plots': True,  # 总开关：是否保存任何图像
                'save_convergence_plot': True,  # 收敛曲线

                # 数据输出配置
                'save_data_files': True,  # 总开关：是否保存任何数据文件
                'save_scheme_matrix': True,  # 方案-指标矩阵
                'save_decision_params': False,  # 决策参数
                'save_rankings': False,  # 排名结果
                'save_matrix_outputs': False,  # 矩阵形式输出
                'save_pairwise_rankings': False,  # 新增：是否保存两两算法比较结果

                # 输出格式配置
                'plot_format': 'png',
                'plot_dpi': 300,
                'data_format': 'txt',  # txt, csv, json
                'ranks_format': 'txt',
                'report_format': 'json'
            }
        }

    def config_logging_setup(self):
        """配置日志设置"""
        log_level = getattr(logging, self.config_get('common', 'log_level', 'INFO'))
        silent_mode = self.config_get('common', 'silent_mode', False)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('algorithm_system.log', encoding='utf-8'),
                logging.StreamHandler() if not silent_mode else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger('UnifiedConfig')
        self.logger.info("统一配置管理器初始化完成")

    def config_get(self, category: str, key: str = None, default=None) -> Any:
        """
        获取配置值

        Args:
            category: 配置类别
            key: 配置键名，为None时返回整个类别
            default: 默认值

        Returns:
            配置值
        """
        if category not in self.configs:
            return default if key is None else default

        if key is None:
            return self.configs[category]

        return self.configs[category].get(key, default)

    def config_set(self, category: str, key: str, value: Any):
        """
        设置配置值

        Args:
            category: 配置类别
            key: 配置键名
            value: 配置值
        """
        if category not in self.configs:
            self.configs[category] = {}
        self.configs[category][key] = value
        self.logger.debug(f"设置配置: {category}.{key} = {value}")

    def config_update(self, config_dict: Dict[str, Any]):
        """
        批量更新配置

        Args:
            config_dict: 配置字典
        """
        self._deep_update(self.configs, config_dict)
        self.logger.info("配置已更新")

    def config_optimization_dimension_update(self, actual_nd: int):
        """
        配置优化维度更新

        Args:
            actual_nd: 实际维度
        """
        current_nd = self.config_get('optimization', 'nd')
        if current_nd != actual_nd:
            self.logger.info(f"更新优化维度: {current_nd} -> {actual_nd}")
            self.config_set('optimization', 'nd', actual_nd)
            self.config_set('optimization', 'Lb', [0.0] * actual_nd)
            self.config_set('optimization', 'Ub', [1.0] * actual_nd)

    def config_validate(self) -> bool:
        """
        配置验证

        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查必要配置
            required_common = ['data_source', 'output_dir']
            for key in required_common:
                if not self.config_get('common', key):
                    self.logger.error(f"缺少必要配置: common.{key}")
                    return False

            # 检查优化配置
            required_optimization = ['nd', 'N_pop', 'N_IterTotal', 'Lb', 'Ub']
            for key in required_optimization:
                if self.config_get('optimization', key) is None:
                    self.logger.error(f"缺少必要配置: optimization.{key}")
                    return False

            self.logger.info("配置验证通过")
            return True

        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False

    def _deep_update(self, original: Dict, update: Dict):
        """
        深度更新字典

        Args:
            original: 原始字典
            update: 更新字典
        """
        for key, value in update.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value

    def config_summary_get(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            Dict: 配置摘要
        """
        return {
            'algorithms': list(self.ALGORITHMS.keys()),
            'optimization_params': {
                'nd': self.config_get('optimization', 'nd'),
                'N_pop': self.config_get('optimization', 'N_pop'),
                'N_IterTotal': self.config_get('optimization', 'N_IterTotal')
            },
            'output_settings': self.config_get('output')
        }