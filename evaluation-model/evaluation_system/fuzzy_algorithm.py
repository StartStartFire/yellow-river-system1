# algorithms/fuzzy_algorithm.py
# -*- coding: utf-8 -*-
import numpy as np
from typing import Dict, Any, Tuple
from .algorithm_base import BaseAlgorithm


class AHPCalculator:
    """层次分析法(AHP)权重计算器"""

    def __init__(self, n: int):
        self.n = n
        self.A = np.ones((n, n))
        self.consistency_RI = [0, 0.0001, 0.52, 0.89, 1.12, 1.26, 1.36, 1.41, 1.46, 1.49, 1.52, 1.54, 1.56, 1.58, 1.59]

    def ahp_comparison_matrix_set(self, comparisons: dict):
        """设置判断矩阵的比较关系 - 支持元组和字符串两种格式"""
        # 清空矩阵
        self.A = np.ones((self.n, self.n))

        # 设置上三角部分的比较值
        for key, value in comparisons.items():
            if isinstance(key, tuple):
                i, j = key
            elif isinstance(key, str):
                i, j = map(int, key.split('-'))
            else:
                continue

            if i < j and i < self.n and j < self.n:
                self.A[i, j] = value

        # 根据对称性填充下三角部分
        for i in range(self.n):
            for j in range(i + 1, self.n):
                self.A[j, i] = 1.0 / self.A[i, j]

    def ahp_weights_calculate(self) -> Tuple[np.ndarray, Dict[str, float]]:
        """计算权重并进行一致性检验"""
        # 计算几何平均法权重
        prod_A = np.prod(self.A, axis=1)
        prod_n_A = np.power(prod_A, 1.0 / self.n)
        weights = prod_n_A / np.sum(prod_n_A)

        # 一致性分析
        eigenvalues, eigenvectors = np.linalg.eig(self.A)
        max_eigenvalue = np.max(np.real(eigenvalues))

        CI = (max_eigenvalue - self.n) / (self.n - 1)
        CR = CI / self.consistency_RI[self.n] if self.n < len(self.consistency_RI) else 0

        consistency_info = {
            'CI': float(np.real(CI)),
            'CR': float(np.real(CR)),
            'max_eigenvalue': float(np.real(max_eigenvalue)),
            'is_consistent': CR < 0.10
        }

        return weights, consistency_info


class FuzzyComprehensiveEvaluator:
    """模糊综合评价器"""

    def __init__(self, data_matrix: np.ndarray, subsystem_config: Dict[str, Dict[str, Any]], config):
        self.data = data_matrix
        self.n_schemes, self.n_indicators = data_matrix.shape
        self.subsystem_config = subsystem_config
        self.config = config
        self.fuzzy_config_validate()

    def fuzzy_config_validate(self):
        """验证子系统配置的有效性"""
        total_indicators = 0

        for subsystem, config in self.subsystem_config.items():
            indices = config['indices']
            weights = np.array(config['weights'])

            # 验证权重和
            weight_sum = np.sum(weights)
            if not np.isclose(weight_sum, 1.0, atol=1e-5):
                if np.isclose(weight_sum, 1.0, atol=0.01):
                    self.config.logger.warning(f"子系统 {subsystem} 权重和不为1 ({weight_sum:.6f})，正在进行自动归一化")
                    config['weights'] = weights / weight_sum
                else:
                    raise ValueError(f"子系统 {subsystem} 权重和不为1: {weight_sum:.6f}")

            # 验证索引范围
            if isinstance(indices, list):
                max_index = max(indices) if indices else -1
                expected_weights = len(indices)
            elif isinstance(indices, slice):
                max_index = indices.stop - 1 if indices.stop else -1
                expected_weights = indices.stop - indices.start
            else:
                raise ValueError(f"不支持的索引类型: {type(indices)}")

            if max_index >= self.n_indicators:
                raise ValueError(f"子系统 {subsystem} 索引超出数据范围: {max_index} >= {self.n_indicators}")

            # 验证权重维度
            if len(weights) != expected_weights:
                raise ValueError(f"子系统 {subsystem} 权重维度不匹配: 期望{expected_weights}, 实际{len(weights)}")

            total_indicators += expected_weights

        if total_indicators != self.n_indicators:
            self.config.logger.warning(f"配置的指标总数({total_indicators})与数据指标数({self.n_indicators})不匹配")
        else:
            self.config.logger.info(f"配置的指标总数({total_indicators})与数据指标数({self.n_indicators})匹配")

    def fuzzy_first_level_evaluation(self) -> Dict[str, Dict[str, Any]]:
        """一级模糊综合评价"""
        results = {}

        for subsystem, config in self.subsystem_config.items():
            indices = config['indices']
            weights = np.array(config['weights'])
            name = config.get('name', subsystem)

            # 提取子系统数据
            subsystem_data = self.data[:, indices]

            # 计算评价结果: R * A
            evaluation_result = np.dot(subsystem_data, weights)
            results[subsystem] = {
                'scores': evaluation_result,
                'name': name,
                'weights': weights,
                'indices': indices
            }

        return results

    def fuzzy_first_level_ranking_calculate(self, first_level_results: Dict[str, Dict[str, Any]]) -> Dict[
        str, Dict[str, Any]]:
        """
        计算一级模糊综合评价的排名

        Args:
            first_level_results: 一级评价结果

        Returns:
            Dict: 包含每个子系统排名信息的结果
        """
        ranking_results = {}

        for subsystem, result in first_level_results.items():
            scores = result['scores']

            # 计算排名 - 按分数降序排序
            sorted_indices = np.argsort(scores)[::-1]
            ranking = np.zeros(len(scores), dtype=int)

            # 为每个排序位置分配排名（1为最好）
            for rank_position, original_index in enumerate(sorted_indices):
                ranking[original_index] = rank_position

            # 找到最优方案
            best_scheme_index = sorted_indices[0]
            best_scheme_score = scores[best_scheme_index]

            ranking_results[subsystem] = {
                'name': result['name'],
                'scores': scores,
                'ranking': ranking,
                'sorted_indices': sorted_indices,
                'best_scheme_index': best_scheme_index,
                'best_scheme_score': best_scheme_score,
                'weights': result['weights'],
                'indices': result['indices']
            }

            self.config.logger.info(
                f"子系统 {subsystem} 排名完成，最优方案: 方案{best_scheme_index + 1}, 得分: {best_scheme_score:.6f}")

        return ranking_results

    def fuzzy_second_level_evaluation(self, first_level_results: Dict[str, Dict[str, Any]],
                                      second_level_weights: np.ndarray) -> np.ndarray:
        """二级模糊综合评判"""
        # 构建二级评价矩阵 R
        score_arrays = []

        for subsystem, result in first_level_results.items():
            score_arrays.append(result['scores'])

        R_matrix = np.column_stack(score_arrays)

        # 验证权重维度
        if len(second_level_weights) != R_matrix.shape[1]:
            raise ValueError(f"二级权重维度不匹配: 期望{R_matrix.shape[1]}, 实际{len(second_level_weights)}")

        # 二级综合评判: R * A_ahp
        final_scores = np.dot(R_matrix, second_level_weights)

        return final_scores

    def fuzzy_ranking_calculate(self, final_scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """计算方案排名 - 确保与正确程序一致"""
        # 获取方案数量
        n_schemes = len(final_scores)

        # 按分数降序排序，获取排序后的索引
        sorted_indices = np.argsort(final_scores)[::-1]

        # 创建排名数组
        ranking = np.zeros(n_schemes, dtype=int)

        # 为每个排序位置分配排名（1为最好）
        for rank_position, original_index in enumerate(sorted_indices):
            ranking[original_index] = rank_position

        return ranking, sorted_indices


class FuzzyAlgorithm(BaseAlgorithm):
    """AHP模糊综合评价算法"""

    def __init__(self, config=None):
        super().__init__('AHP_FUZZY', config)

    def algorithm_core_calculation(self, data_source) -> Dict[str, Any]:
        """
        运行AHP模糊综合评价

        Args:
            data_source: 数据源

        Returns:
            Dict: 算法结果
        """
        import time

        try:
            start_time = time.time()

            # 设置数据矩阵
            if isinstance(data_source, np.ndarray):
                self.algorithm_data_matrix_set(data_source)
            else:
                # 从文件加载数据
                from .standardization_main import standardization_main
                import pandas as pd

                if isinstance(data_source, str):
                    if data_source.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(data_source, sheet_name=self.config.config_get('common', 'sheet_name'))
                        data_matrix = standardization_main(df)
                    else:
                        data_matrix = np.loadtxt(data_source)
                elif isinstance(data_source, pd.DataFrame):
                    data_matrix = standardization_main(data_source)
                else:
                    raise ValueError(f"不支持的数据源类型: {type(data_source)}")

                self.algorithm_data_matrix_set(data_matrix)

            # 获取配置 - 直接使用配置文件中的比较矩阵
            fuzzy_config = self.config.config_get('fuzzy')
            ahp_comparisons = fuzzy_config['ahp_comparisons']  # 使用配置文件中的比较矩阵
            subsystem_config = fuzzy_config['subsystem_config']

            # AHP权重计算
            ahp_calc = AHPCalculator(n=5)
            ahp_calc.ahp_comparison_matrix_set(ahp_comparisons)
            ahp_weights, consistency_info = ahp_calc.ahp_weights_calculate()

            # 使用AHP计算的权重作为二级评价权重
            second_level_weights = ahp_weights

            # 模糊综合评价
            fuzzy_eval = FuzzyComprehensiveEvaluator(self.data_matrix, subsystem_config, self.config)

            # 一级评价
            first_level_results = fuzzy_eval.fuzzy_first_level_evaluation()

            # 一级评价排名
            first_level_ranking_results = fuzzy_eval.fuzzy_first_level_ranking_calculate(first_level_results)

            # 二级评价
            final_scores = fuzzy_eval.fuzzy_second_level_evaluation(first_level_results, second_level_weights)

            # 计算最终排名
            ranking, sorted_indices = fuzzy_eval.fuzzy_ranking_calculate(final_scores)

            execution_time = time.time() - start_time

            # 记录结果
            self.logger.info("AHP模糊综合评价完成")
            self.logger.info(f"一致性比率 CR: {consistency_info['CR']:.4f}")
            self.logger.info(f"最优方案: 方案{sorted_indices[0] + 1}, 得分: {final_scores[sorted_indices[0]]:.6f}")
            self.logger.info(f"执行时间: {execution_time:.2f}秒")

            # 构建结果字典
            user_config_data = {
                'data_source': data_source if isinstance(data_source, str) else 'direct_matrix_input',
                'subsystem_config': subsystem_config,
                'ahp_comparisons': ahp_comparisons
            }

            return {
                'best_scheme_index': sorted_indices[0],
                'best_scheme_score': final_scores[sorted_indices[0]],
                'ranks': ranking,
                'final_scores': final_scores,
                'ahp_weights': ahp_weights,
                'consistency_info': consistency_info,
                'first_level_results': {
                    subsystem_name: {
                        'name': result['name'],
                        'scores': result['scores'],
                        'weights': result['weights'],
                        'indices': result['indices']
                    } for subsystem_name, result in first_level_results.items()
                },
                'first_level_ranking_results': first_level_ranking_results,  # 新增一级评价排名结果
                'user_config': user_config_data,
                'execution_time': execution_time,
                'data_matrix': self.data_matrix
            }

        except Exception as e:
            self.logger.error(f"AHP模糊综合评价运行失败: {e}")
            raise