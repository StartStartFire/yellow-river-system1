# algorithms/rank_sum_theory.py
# -*- coding: utf-8 -*-
import numpy as np
from typing import Dict, List, Any, Optional


class RankSumTheory:
    """
    序号总和理论 - 用于最终方案排序
    """

    def __init__(self, config=None):
        self.config = config
        self.logger = config.logger if config else self._setup_default_logger()

    def _setup_default_logger(self):
        """设置默认日志记录器"""
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('RankSumTheory')

    def final_ranking_calculate(self, rankings_dict: Dict[str, np.ndarray]) -> np.ndarray:
        """
        使用序号总和理论计算最终排名

        Args:
            rankings_dict: 各算法的排名字典 {算法名: 排名数组}

        Returns:
            np.ndarray: 最终排名（0-indexed）
        """
        try:
            algorithm_names = list(rankings_dict.keys())
            n_schemes = len(rankings_dict[algorithm_names[0]])

            # 计算每个方案的序号总和
            rank_sums = np.zeros(n_schemes)
            for algo in algorithm_names:
                # 转换为1-indexed排名进行求和
                rank_sums += (rankings_dict[algo] + 1)

            # 按序号总和升序排序（总和越小，排名越靠前）
            sorted_indices = np.argsort(rank_sums)

            # 分配最终排名（0-indexed）
            final_ranking = np.zeros(n_schemes, dtype=int)
            for new_rank, original_index in enumerate(sorted_indices):
                final_ranking[original_index] = new_rank

            self.logger.info(f"序号总和理论计算完成，最优方案: 方案{sorted_indices[0] + 1}")
            self.logger.info(f"各方案序号总和: {rank_sums}")

            return final_ranking

        except Exception as e:
            self.logger.error(f"序号总和理论计算失败: {e}")
            raise

    def pairwise_rank_sum_calculate(self, rankings_dict: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        计算两两算法组合的序号总和排序

        Args:
            rankings_dict: 各算法的排名字典

        Returns:
            Dict: 两两算法组合的序号总和排序结果
        """
        pairwise_results = {}
        algorithm_names = list(rankings_dict.keys())

        # 生成所有两两组合
        combinations = [
            ('NMF', 'PP'),
            ('NMF', 'AHP_FUZZY'),
            ('PP', 'AHP_FUZZY'),
            ('ALL', 'ALL')  # 所有算法组合
        ]

        for algo1, algo2 in combinations:
            if algo1 == 'ALL' and algo2 == 'ALL':
                # 所有算法组合
                combo_name = 'ALL'
                combo_rankings = rankings_dict
            else:
                # 检查算法是否存在
                if algo1 not in algorithm_names or algo2 not in algorithm_names:
                    continue
                combo_name = f"{algo1}-{algo2}"
                combo_rankings = {algo1: rankings_dict[algo1], algo2: rankings_dict[algo2]}

            # 计算序号总和排序
            try:
                final_ranking = self.final_ranking_calculate(combo_rankings)
                rank_sum_report = self.rank_sum_report_generate(combo_rankings, final_ranking)

                pairwise_results[combo_name] = {
                    'final_ranking': final_ranking,
                    'rank_sum_report': rank_sum_report,
                    'algorithms_used': list(combo_rankings.keys())
                }

                self.logger.info(f"两两组合 {combo_name} 序号总和排序计算完成")

            except Exception as e:
                self.logger.warning(f"两两组合 {combo_name} 序号总和排序计算失败: {e}")

        return pairwise_results

    def rank_sum_report_generate(self, rankings_dict: Dict[str, np.ndarray],
                                 final_ranking: np.ndarray) -> Dict[str, Any]:
        """
        生成序号总和理论分析报告

        Args:
            rankings_dict: 各算法的排名字典
            final_ranking: 最终排名结果

        Returns:
            Dict: 序号总和分析报告
        """
        algorithm_names = list(rankings_dict.keys())
        n_schemes = len(final_ranking)

        # 计算每个方案的序号总和
        rank_sums = np.zeros(n_schemes)
        for algo in algorithm_names:
            rank_sums += (rankings_dict[algo] + 1)

        # 构建详细的排名数据
        scheme_details = []
        for i in range(n_schemes):
            scheme_ranks = {}
            for algo in algorithm_names:
                scheme_ranks[algo] = int(rankings_dict[algo][i] + 1)  # 1-indexed

            scheme_details.append({
                'scheme_index': i + 1,
                'final_rank': int(final_ranking[i] + 1),
                'rank_sum': int(rank_sums[i]),
                'algorithm_ranks': scheme_ranks
            })

        # 按最终排名排序方案详情
        sorted_scheme_details = sorted(scheme_details, key=lambda x: x['final_rank'])

        report = {
            'ranking_method': 'rank_sum_theory',
            'total_algorithms': len(algorithm_names),
            'total_schemes': n_schemes,
            'scheme_details': sorted_scheme_details,
            'rank_sums': rank_sums.tolist(),
            'best_scheme': sorted_scheme_details[0]['scheme_index'],
            'worst_scheme': sorted_scheme_details[-1]['scheme_index']
        }

        return report