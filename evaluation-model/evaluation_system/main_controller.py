# main_controller.py
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import time
import os
from typing import Dict, Any, List, Optional
from .unified_config import UnifiedConfig
from .unified_output import UnifiedOutput
from .nmf_algorithm import NMFAlgorithm
from .pp_algorithm import PPAlgorithm
from .fuzzy_algorithm import FuzzyAlgorithm
from .standardization_main import standardization_main
from .rank_sum_theory import RankSumTheory


class MainController:
    """统一主控制器 - 内置配置，不依赖外部文件"""

    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        初始化主控制器

        Args:
            config_dict: 可选的配置字典，用于覆盖默认配置
        """
        # 初始化配置
        self.config = UnifiedConfig(config_dict)

        # 先设置logger
        self.logger = self.config.logger

        # 初始化输出管理器
        self.output = UnifiedOutput(self.config)

        # 初始化算法
        self.algorithms = self.algorithms_initialize()

        # 验证配置
        if not self.config.config_validate():
            self.logger.warning("配置验证未通过，可能影响系统运行")

        self.logger.info("综合评价系统初始化完成")

    def algorithms_initialize(self) -> Dict[str, Any]:
        """
        初始化所有算法

        Returns:
            Dict: 算法实例字典
        """
        algorithms = {}

        # 动态导入算法
        try:
            from .nmf_algorithm import NMFAlgorithm
            algorithms['NMF'] = NMFAlgorithm(self.config)
            self.logger.info("NMF算法初始化成功")
        except ImportError as e:
            self.logger.error(f"初始化NMF算法失败: {e}")

        try:
            from .pp_algorithm import PPAlgorithm
            algorithms['PP'] = PPAlgorithm(self.config)
            self.logger.info("PP算法初始化成功")
        except ImportError as e:
            self.logger.error(f"初始化PP算法失败: {e}")

        try:
            from .fuzzy_algorithm import FuzzyAlgorithm
            algorithms['AHP_FUZZY'] = FuzzyAlgorithm(self.config)
            self.logger.info("AHP_FUZZY算法初始化成功")
        except ImportError as e:
            self.logger.error(f"初始化AHP-Fuzzy算法失败: {e}")

        if not algorithms:
            self.logger.error("没有可用的算法，请检查算法模块")
        else:
            self.logger.info(f"成功初始化 {len(algorithms)} 个算法: {list(algorithms.keys())}")

        return algorithms

    def single_algorithm_run(self, algorithm_name: str, data_source=None) -> Dict[str, Any]:
        """
        运行单个算法

        Args:
            algorithm_name: 算法名称
            data_source: 数据源，默认为配置中的data_source

        Returns:
            Dict: 包含算法结果和输出目录的字典
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"算法不存在: {algorithm_name}，可用算法: {list(self.algorithms.keys())}")

        algorithm = self.algorithms[algorithm_name]

        try:
            # 获取数据 - 现在返回两个矩阵
            if data_source is None:
                data_source = self.config.config_get('common', 'data_source')

            standardized_matrix, original_matrix = self.data_matrix_get(data_source)

            # 设置数据矩阵（使用标准化矩阵进行计算）
            algorithm.algorithm_data_matrix_set(standardized_matrix, original_matrix)

            # 运行算法
            self.logger.info(f"开始运行算法: {algorithm_name}")
            start_time = time.time()
            results = algorithm.algorithm_core_calculation(standardized_matrix)
            execution_time = time.time() - start_time

            # 在结果中添加原始矩阵
            results['original_data_matrix'] = original_matrix
            results['standardized_data_matrix'] = standardized_matrix

            # 保存结果
            output_dir = algorithm.algorithm_result_save(results)

            self.logger.info(f"算法 {algorithm_name} 运行完成，耗时: {execution_time:.2f}秒")

            return {
                'algorithm': algorithm_name,
                'results': results,
                'output_dir': output_dir,
                'execution_time': execution_time,
                'success': True
            }

        except Exception as e:
            self.logger.error(f"算法 {algorithm_name} 运行失败: {e}")
            return {
                'algorithm': algorithm_name,
                'error': str(e),
                'success': False
            }

    def all_algorithms_run(self, data_source=None) -> Dict[str, Dict[str, Any]]:
        """
        运行所有算法

        Args:
            data_source: 数据源，默认为配置中的data_source

        Returns:
            Dict: 所有算法的结果字典
        """
        if data_source is None:
            data_source = self.config.config_get('common', 'data_source')

        # 获取数据矩阵 - 现在返回两个矩阵
        standardized_matrix, original_matrix = self.data_matrix_get(data_source)

        all_results = {}
        for name, algorithm in self.algorithms.items():
            try:
                # 设置数据矩阵（使用标准化矩阵进行计算）
                algorithm.algorithm_data_matrix_set(standardized_matrix, original_matrix)

                self.logger.info(f"开始运行算法: {name}")
                start_time = time.time()
                results = algorithm.algorithm_core_calculation(standardized_matrix)
                execution_time = time.time() - start_time

                # 在结果中添加原始矩阵
                results['original_data_matrix'] = original_matrix
                results['standardized_data_matrix'] = standardized_matrix

                output_dir = algorithm.algorithm_result_save(results)
                all_results[name] = {
                    'results': results,
                    'output_dir': output_dir,
                    'execution_time': execution_time,
                    'success': True
                }
                self.logger.info(f"算法 {name} 运行完成，耗时: {execution_time:.2f}秒")
            except Exception as e:
                self.logger.error(f"算法 {name} 运行失败: {e}")
                all_results[name] = {
                    'error': str(e),
                    'success': False
                }

        return all_results

    def rankings_integrate(self, all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        整合所有算法的排名 - 直接使用序号总和理论

        Args:
            all_results: 所有算法的结果

        Returns:
            Dict: 整合结果
        """
        valid_rankings = {}
        original_data_matrix = None
        standardized_data_matrix = None

        # 获取数据矩阵（从第一个成功运行的算法结果中）
        for algo_name, result_info in all_results.items():
            if result_info.get('success', False):
                if 'original_data_matrix' in result_info['results']:
                    original_data_matrix = result_info['results']['original_data_matrix']
                if 'standardized_data_matrix' in result_info['results']:
                    standardized_data_matrix = result_info['results']['standardized_data_matrix']
                break

        if original_data_matrix is None:
            raise ValueError("无法获取原始数据矩阵，请检查算法运行结果")

        # 提取有效的排名数据
        for algo_name, result_info in all_results.items():
            if result_info.get('success', False) and 'ranks' in result_info['results']:
                valid_rankings[algo_name] = result_info['results']['ranks']

        if not valid_rankings:
            raise ValueError("没有有效的排名数据可供整合")

        # 直接使用序号总和理论进行排名整合
        rank_sum_theory = RankSumTheory(self.config)

        # 计算最终排名
        final_ranking = rank_sum_theory.final_ranking_calculate(valid_rankings)

        # 生成序号总和分析报告
        rank_sum_report = rank_sum_theory.rank_sum_report_generate(valid_rankings, final_ranking)

        # 计算两两算法组合的序号总和排序
        pairwise_rank_sum_results = rank_sum_theory.pairwise_rank_sum_calculate(valid_rankings)

        integrated_results = {
            'final_ranking': final_ranking,
            'ranking_method': 'rank_sum_theory',
            'rank_sum_report': rank_sum_report,
            'pairwise_rank_sum_results': pairwise_rank_sum_results,
            'all_rankings': valid_rankings,
            'original_data_matrix': original_data_matrix,
            'standardized_data_matrix': standardized_data_matrix,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'integration_successful': True
        }

        # 保存整合结果
        output_dir = self.output.output_integrated_results_save(integrated_results)
        integrated_results['output_dir'] = output_dir

        return integrated_results

    def data_matrix_get(self, data_source) -> tuple:
        """
        获取数据矩阵

        Args:
            data_source: 数据源

        Returns:
            tuple: (标准化矩阵, 原始矩阵)
        """
        if isinstance(data_source, np.ndarray):
            # 如果直接传入矩阵，则同时返回标准化和原始矩阵（相同）
            standardized_matrix = data_source
            original_matrix = data_source.copy()
            return standardized_matrix, original_matrix
        elif isinstance(data_source, pd.DataFrame):
            from .standardization_main import standardization_main
            standardized_matrix, original_matrix = standardization_main(data_source)
            return standardized_matrix, original_matrix
        elif isinstance(data_source, str):
            # 从文件加载
            if data_source.endswith(('.xlsx', '.xls')):
                sheet_name = self.config.config_get('common', 'sheet_name')
                df = pd.read_excel(data_source, sheet_name=sheet_name)
                from .standardization_main import standardization_main
                standardized_matrix, original_matrix = standardization_main(df)
                return standardized_matrix, original_matrix
            else:
                # 其他文件格式
                data_matrix = np.loadtxt(data_source)
                return data_matrix, data_matrix.copy()
        else:
            raise ValueError(f"不支持的数据源类型: {type(data_source)}")

    def complete_evaluation_run(self, data_source=None) -> Dict[str, Any]:
        """
        运行完整评估流程

        Args:
            data_source: 数据源，默认为配置中的data_source

        Returns:
            Dict: 完整评估结果
        """
        start_time = time.time()

        try:
            # 1. 运行所有算法
            self.logger.info("开始运行所有算法")
            all_results = self.all_algorithms_run(data_source)

            # 2. 整合排名（使用序号总和理论）
            self.logger.info("开始整合排名")
            integrated_results = self.rankings_integrate(all_results)

            # 3. 生成总结报告
            self.summary_report_generate(all_results, integrated_results)

            execution_time = time.time() - start_time

            self.logger.info(f"完整评估完成，总耗时: {execution_time:.2f}秒")

            return {
                'algorithm_results': all_results,
                'integrated_results': integrated_results,
                'execution_time': execution_time,
                'success': integrated_results['integration_successful']
            }

        except Exception as e:
            self.logger.error(f"完整评估失败: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def summary_report_generate(self, all_results: Dict[str, Any], integrated_results: Dict[str, Any]):
        """
        生成总结报告

        Args:
            all_results: 所有算法结果
            integrated_results: 整合结果
        """
        # 使用输出模块生成总结报告
        self.output.output_summary_report_generate(all_results, integrated_results)

    def available_algorithms_get(self) -> List[str]:
        """
        获取可用算法列表

        Returns:
            list: 算法名称列表
        """
        return list(self.algorithms.keys())

    def algorithm_info_get(self, algorithm_name: str) -> Dict[str, Any]:
        """
        获取算法信息

        Args:
            algorithm_name: 算法名称

        Returns:
            Dict: 算法信息
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"算法不存在: {algorithm_name}")

        algorithm = self.algorithms[algorithm_name]
        return {
            'name': algorithm.name,
            'description': UnifiedConfig.ALGORITHMS.get(algorithm_name, '未知算法'),
            'config': algorithm.config.config_get('optimization')
        }

    def system_info_get(self) -> Dict[str, Any]:
        """
        获取系统信息

        Returns:
            Dict: 系统信息
        """
        return {
            'available_algorithms': self.available_algorithms_get(),
            'config_summary': self.config.config_summary_get(),
            'output_directory': self.config.config_get('common', 'output_dir')
        }