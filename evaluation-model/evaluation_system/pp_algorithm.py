# algorithms/pp_algorithm.py
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from scipy.special import gamma
from typing import Dict, Any, Tuple, List
from .algorithm_base import BaseAlgorithm


class ProjectionPursuitCalculator:
    """投影寻踪计算器"""

    def __init__(self, A: np.ndarray):
        self.A = A
        self.n_schemes, self.n_indicators = A.shape
        self.Index = A

    def pp_fitness_calculate(self, b: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """计算投影寻踪适应度函数"""
        # 1. 平方和约束
        c = np.sqrt(np.sum(b ** 2))
        a = b / c  # 最佳投影方向a*（归一化）

        # 2. 计算投影值
        z = np.dot(self.Index, a)  # 最佳投影值z*

        # 3. 检查零分量
        if np.any(a == 0):
            return 999.0, a, np.zeros(self.n_schemes)

        # 4. 计算投影值均值
        Ez = np.mean(z)

        # 5. 计算标准差
        S = np.std(z, ddof=1)

        # 6. 计算局部密度
        z_diff = np.abs(z[:, None] - z[None, :])
        threshold = 0.1 * S
        mask = threshold - z_diff >= 0
        d = (threshold - z_diff) * mask
        Dz = np.sum(d)

        # 7. 计算投影寻踪指标
        Q = 1.0 / (1.0 + S * Dz)

        return Q, a, z


class CuckooCoreOperations:
    """布谷鸟搜索核心操作 - 投影寻踪版本"""

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
                      calculator: ProjectionPursuitCalculator) -> Tuple[
        float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """获取当前最优解"""
        for j in range(nest.shape[0]):
            fnew, _, _ = calculator.pp_fitness_calculate(newnest[j, :])
            if fnew <= fitness[j]:
                fitness[j] = fnew
                nest[j, :] = newnest[j, :]

        sorted_indices = np.argsort(fitness)
        sorted_fitness = fitness[sorted_indices]

        fmin = sorted_fitness[0]
        best = nest[sorted_indices[0], :]
        ranks = sorted_indices.copy()

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


class PPAlgorithm(BaseAlgorithm):
    """投影寻踪布谷鸟搜索算法 - 修正版本：基于投影值z*进行排名"""

    def __init__(self, config=None):
        super().__init__('PP', config)

    def generate_ranks_from_z(self, z: np.ndarray) -> np.ndarray:
        """根据投影值z生成排名（0-indexed，越小表示排名越靠前）"""
        # 按z值降序排序，z值越大排名越靠前
        sorted_indices = np.argsort(z)[::-1]  # 从大到小排序

        # 创建排名数组（0-indexed）
        ranks = np.zeros(len(z), dtype=int)
        for rank_position, original_index in enumerate(sorted_indices):
            ranks[original_index] = rank_position

        return ranks

    def print_ranking_results(self, z: np.ndarray, ranks: np.ndarray):
        """打印排名结果"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PP算法结果 - 方案排名及投影值")
        self.logger.info("=" * 60)

        # 按排名顺序显示
        sorted_indices = np.argsort(ranks)

        self.logger.info("\n方案排名（按投影值z*从大到小排序）:")
        self.logger.info("-" * 50)
        self.logger.info(f"{'排名':<6} {'方案索引':<10} {'投影值z*':<12}")
        self.logger.info("-" * 50)
        for rank_position, scheme_idx in enumerate(sorted_indices):
            self.logger.info(f"{rank_position + 1:<6} {scheme_idx:<10} {z[scheme_idx]:<12.6f}")

        self.logger.info("\n投影值z*（按原始索引顺序）:")
        self.logger.info("-" * 30)
        for i, z_val in enumerate(z):
            self.logger.info(f"方案 {i}: {z_val:.6f}")

        best_scheme_index = np.argmin(ranks)  # 排名最小的为最优方案
        best_scheme_score = z[best_scheme_index]
        self.logger.info(f"\n最优方案: 方案{best_scheme_index} (投影值z*: {best_scheme_score:.6f})")

    def algorithm_core_calculation(self, data_source) -> Dict[str, Any]:
        """
        运行投影寻踪算法 - 基于投影值z*进行排名

        Args:
            data_source: 数据源

        Returns:
            Dict: 算法结果，包含：
                - a: 最佳投影方向a*
                - z: 最佳投影值z*
                - ranks: 排名数组（0-indexed，越小表示排名越靠前）
                - best_scheme_index: z*最大的方案索引（最优方案）
                - best_scheme_score: 最大的z*值
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
            pp_calculator = ProjectionPursuitCalculator(self.data_matrix)
            core_ops = CuckooCoreOperations()

            # 初始化种群
            nest = core_ops.population_initialize(config_params)
            fitness = np.full(config_params['N_pop'], np.inf)

            # 获取初始最优解
            fmin, bestnest, nest, fitness, initial_ranks = core_ops.best_nest_get(
                nest, nest, fitness, pp_calculator
            )

            # 开始迭代
            cost_history = []
            iter_count = 1
            t = 1
            final_ranks = initial_ranks.copy()

            self.logger.info("开始投影寻踪布谷鸟搜索优化")

            while (iter_count <= config_params['N_IterTotal']) and (fmin > config_params['accuracy']):
                # 参数自适应
                alpha = 0.02 + 0.08 * np.sin(np.pi / 2 * (iter_count - 1) / (config_params['N_IterTotal'] - 1))

                # 种群变异
                tempnest = bestnest + alpha * np.random.randn(*bestnest.shape)

                # 评估变异
                temp_fitness, _, _ = pp_calculator.pp_fitness_calculate(tempnest)
                best_fitness, _, _ = pp_calculator.pp_fitness_calculate(bestnest)

                if temp_fitness <= best_fitness:
                    bestnest = tempnest
                    t += 1

                # 生成新解
                new_nest = core_ops.levy_flight_generate(nest, bestnest, config_params['Lb'], config_params['Ub'])

                # 评估新解
                fmin, bestnest, nest, fitness, current_ranks = core_ops.best_nest_get(
                    nest, new_nest, fitness, pp_calculator
                )
                final_ranks = current_ranks

                # 自适应发现概率
                pa = 0.1 + 0.15 * np.sin(np.pi / 2 * (iter_count - 1) / (config_params['N_IterTotal'] - 1))

                # 偏好随机游动
                new_nest = core_ops.empty_nests_generate(nest, config_params['Lb'], config_params['Ub'], pa)

                # 评估最优解
                fnew, best, nest, fitness, current_ranks = core_ops.best_nest_get(
                    nest, new_nest, fitness, pp_calculator
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

            # === 关键修正：明确计算投影方向a*和投影值z* ===
            _, a, z = pp_calculator.pp_fitness_calculate(bestnest)

            # === 新增：基于投影值z*生成排名 ===
            ranks = self.generate_ranks_from_z(z)
            best_scheme_index = np.argmin(ranks)  # 排名最小的为最优方案
            best_scheme_score = z[best_scheme_index]

            # 打印排名结果
            self.print_ranking_results(z, ranks)

            self.logger.info(f"优化完成，总耗时: {execution_time:.2f}秒")

            # 返回完整的计算结果 - 修正版本
            return {
                'best_solution': bestnest,  # 原始最优解向量
                'a': a,  # 最佳投影方向a*
                'z': z,  # 最佳投影值z*
                'ranks': ranks,  # 基于投影值z*的排名（0-indexed，越小表示排名越靠前）
                'best_scheme_index': best_scheme_index,  # z*最大的方案索引
                'best_scheme_score': best_scheme_score,  # 最大的z*值
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
                'optimization_criteria': '投影值z*最大的方案为最优方案'  # 明确寻优条件
            }

        except Exception as e:
            self.logger.error(f"投影寻踪算法运行失败: {e}")
            raise