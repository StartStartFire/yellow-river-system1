# algorithms/nmf_algorithm.py
# -*- coding: utf-8 -*-
import numpy as np
from scipy.special import gamma
from typing import Dict, Any, Tuple
from .algorithm_base import BaseAlgorithm


class INMFCalculator:
    """改进的非负矩阵分解计算器"""

    def __init__(self, A: np.ndarray):
        self.A = A.T
        self.r, self.c = A.shape

    def nmf_fitness_calculate(self, x: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """计算适应度函数"""
        l = np.linalg.norm(x)
        W = x / l  # 基向量V*（归一化）
        H = np.dot(W, self.A)  # 权向量H*
        B = np.outer(W, H)
        y = np.sum((self.A - B) ** 2)
        return y, W, H


class CuckooCoreOperations:
    """布谷鸟搜索核心操作"""

    @staticmethod
    def population_initialize(config: Dict[str, Any]) -> np.ndarray:
        """初始化种群"""
        nd = config['nd']
        N_pop = config['N_pop']
        Lb = config['Lb']
        Ub = config['Ub']

        return Lb + (Ub - Lb) * np.random.rand(N_pop, nd)

    @staticmethod
    def best_nest_get(nest: np.ndarray, newnest: np.ndarray, fitness: np.ndarray,
                      calculator: INMFCalculator) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """获取当前最优解"""
        for j in range(nest.shape[0]):
            fnew, _, _ = calculator.nmf_fitness_calculate(newnest[j, :])
            if fnew <= fitness[j]:
                fitness[j] = fnew
                nest[j, :] = newnest[j, :]

        sorted_indices = np.argsort(fitness)
        sorted_fitness = fitness[sorted_indices]

        fmin = sorted_fitness[0]
        best = nest[sorted_indices[0], :]
        ranks = sorted_indices.astype(np.int32)

        return fmin, best, nest, fitness, ranks

    @staticmethod
    def empty_nests_generate(nest: np.ndarray, Lb: np.ndarray, Ub: np.ndarray, pa: float) -> np.ndarray:
        """通过偏好随机游动生成新解"""
        n = nest.shape[0]
        K = np.random.random(nest.shape) > pa
        idx1 = np.random.permutation(n)
        idx2 = np.random.permutation(n)
        stepsize = np.random.rand() * (nest[idx1, :] - nest[idx2, :])
        new_nest = nest + stepsize * K

        for j in range(new_nest.shape[0]):
            new_nest[j, :] = CuckooCoreOperations.bounds_apply(new_nest[j, :], Lb, Ub)

        return new_nest

    @staticmethod
    def levy_flight_generate(nest: np.ndarray, best: np.ndarray, Lb: np.ndarray, Ub: np.ndarray) -> np.ndarray:
        """通过Levy飞行生成新解"""
        n, nd = nest.shape
        beta = 3 / 2
        sigma_val = (gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                     (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)

        for j in range(n):
            s = nest[j, :]
            u = np.random.randn(nd) * sigma_val
            v = np.random.randn(nd)
            step = u / np.abs(v) ** (1 / beta)
            stepsize = 0.01 * step * (s - best)
            s = s + stepsize * np.random.randn(nd)
            nest[j, :] = CuckooCoreOperations.bounds_apply(s, Lb, Ub)

        return nest

    @staticmethod
    def bounds_apply(s: np.ndarray, Lb: np.ndarray, Ub: np.ndarray) -> np.ndarray:
        """应用简单边界约束"""
        ns_tmp = s.copy()
        ns_tmp[ns_tmp < Lb] = Lb[ns_tmp < Lb]
        ns_tmp[ns_tmp > Ub] = Ub[ns_tmp > Ub]
        return ns_tmp


class NMFAlgorithm(BaseAlgorithm):
    """NMF布谷鸟搜索算法 - 修正版本：基于权向量H值进行排名"""

    def __init__(self, config=None):
        super().__init__('NMF', config)

    def generate_ranks_from_H(self, H: np.ndarray) -> np.ndarray:
        """根据权向量H生成排名（0-indexed，越小表示排名越靠前）"""
        # 按H值降序排序，H值越大排名越靠前
        sorted_indices = np.argsort(H)[::-1]  # 从大到小排序

        # 创建排名数组（0-indexed）
        ranks = np.zeros(len(H), dtype=int)
        for rank_position, original_index in enumerate(sorted_indices):
            ranks[original_index] = rank_position

        return ranks

    def print_ranking_results(self, H: np.ndarray, ranks: np.ndarray):
        """打印排名结果"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("NMF算法结果 - 方案排名及权向量")
        self.logger.info("=" * 60)

        # 按排名顺序显示
        sorted_indices = np.argsort(ranks)

        self.logger.info("\n方案排名（按权向量H从大到小排序）:")
        self.logger.info("-" * 50)
        self.logger.info(f"{'排名':<6} {'方案索引':<10} {'权向量H值':<12}")
        self.logger.info("-" * 50)
        for rank_position, scheme_idx in enumerate(sorted_indices):
            self.logger.info(f"{rank_position + 1:<6} {scheme_idx:<10} {H[scheme_idx]:<12.6f}")

        self.logger.info("\n权向量H（按原始索引顺序）:")
        self.logger.info("-" * 30)
        for i, h_val in enumerate(H):
            self.logger.info(f"方案 {i}: {h_val:.6f}")

        best_scheme_index = np.argmin(ranks)  # 排名最小的为最优方案
        best_scheme_score = H[best_scheme_index]
        self.logger.info(f"\n最优方案: 方案{best_scheme_index} (权向量H值: {best_scheme_score:.6f})")

    def algorithm_core_calculation(self, data_source) -> Dict[str, Any]:
        """
        运行NMF算法 - 基于权向量H值进行排名

        Args:
            data_source: 数据源

        Returns:
            Dict: 算法结果，包含：
                - W: 基向量V*（归一化）
                - H: 权向量H*
                - ranks: 排名数组（0-indexed，越小表示排名越靠前）
                - best_scheme_index: H*最大的方案索引（最优方案）
                - best_scheme_score: 最大的H*值
        """
        import time
        import pandas as pd

        try:
            start_time = time.time()

            # 设置数据矩阵
            if isinstance(data_source, np.ndarray):
                self.algorithm_data_matrix_set(data_source)
            else:
                # 从文件加载数据
                from .standardization_main import standardization_main

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

            # 获取配置
            config_params = self.algorithm_optimization_config_get()

            # 初始化计算器和核心操作
            nmf_calculator = INMFCalculator(self.data_matrix)
            core_ops = CuckooCoreOperations()

            # 初始化种群和适应度
            nest = core_ops.population_initialize(config_params)
            fitness = np.full(config_params['N_pop'], np.inf)

            # 获取初始最优解和排名
            fmin, bestnest, nest, fitness, initial_ranks = core_ops.best_nest_get(
                nest, nest, fitness, nmf_calculator
            )

            # 开始迭代
            cost_history = []
            iter_count = 1
            t = 1
            final_ranks = initial_ranks.copy()

            self.logger.info("开始NMF布谷鸟搜索优化")

            while (iter_count <= config_params['N_IterTotal']) and (fmin > config_params['accuracy']):
                # 参数自适应
                alpha = 0.02 + 0.08 * np.sin(np.pi / 2 * (iter_count - 1) / (config_params['N_IterTotal'] - 1))

                # 种群变异
                tempnest = bestnest + alpha * np.random.randn(*bestnest.shape)

                # 评估变异
                temp_fitness, _, _ = nmf_calculator.nmf_fitness_calculate(tempnest)
                best_fitness, _, _ = nmf_calculator.nmf_fitness_calculate(bestnest)

                if temp_fitness <= best_fitness:
                    bestnest = tempnest
                    t += 1

                # 生成新解
                new_nest = core_ops.levy_flight_generate(nest, bestnest, config_params['Lb'], config_params['Ub'])

                # 评估新解并获取排名
                fmin, bestnest, nest, fitness, current_ranks = core_ops.best_nest_get(
                    nest, new_nest, fitness, nmf_calculator
                )
                final_ranks = current_ranks

                # 自适应发现概率
                pa = 0.1 + 0.15 * np.sin(np.pi / 2 * (iter_count - 1) / (config_params['N_IterTotal'] - 1))

                # 偏好随机游动生成新解
                new_nest = core_ops.empty_nests_generate(nest, config_params['Lb'], config_params['Ub'], pa)

                # 评估最优解并获取排名
                fnew, best, nest, fitness, current_ranks = core_ops.best_nest_get(
                    nest, new_nest, fitness, nmf_calculator
                )
                final_ranks = current_ranks

                if fnew < fmin:
                    fmin = fnew
                    bestnest = best

                cost_history.append(fmin)

                # 记录日志
                if iter_count % 50 == 0:
                    self.logger.info(f"迭代 {iter_count}, 最优适应度: {fmin:.6f}")

                iter_count += 1

            execution_time = time.time() - start_time

            # 计算最终的W和H
            _, W, H = nmf_calculator.nmf_fitness_calculate(bestnest)

            # 生成基于H值的排名
            ranks = self.generate_ranks_from_H(H)
            best_scheme_index = np.argmin(ranks)  # 排名最小的为最优方案
            best_scheme_score = H[best_scheme_index]

            # 打印排名结果
            self.print_ranking_results(H, ranks)

            self.logger.info(f"优化完成，总耗时: {execution_time:.2f}秒")

            # 返回完整的计算结果
            return {
                'best_solution': bestnest,  # 原始最优解向量
                'W': W,  # 基向量V*（归一化）
                'H': H,  # 权向量H*
                'ranks': ranks,  # 排名数组（0-indexed，越小表示排名越靠前）
                'best_scheme_index': best_scheme_index,  # 最优方案索引
                'best_scheme_score': best_scheme_score,  # 最优方案得分
                'best_fitness': fmin,
                'cost_history': cost_history,
                'execution_time': execution_time,
                'iterations': iter_count - 1,
                'effective_mutations': t,
                'population_ranks': final_ranks,  # 保留种群个体排名（内部使用）
                'data_matrix': self.data_matrix,
                'initial_ranks': initial_ranks,
                'population_size': config_params['N_pop'],
                'dimension': config_params['nd'],
                'optimization_criteria': 'H*值最大的方案为最优方案'  # 明确寻优条件
            }

        except Exception as e:
            self.logger.error(f"NMF算法运行失败: {e}")
            raise