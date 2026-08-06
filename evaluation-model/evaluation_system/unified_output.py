# unified_output.py
# -*- coding: utf-8 -*-
import numpy as np
import json
import time
import os
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional
from .unified_config import UnifiedConfig

plt.rcParams['font.family'] = ['Times New Roman', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12


class UnifiedOutput:
    """统一输出管理器 - 处理所有算法的输出"""

    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.output_dir = config.config_get('common', 'output_dir', 'results')
        self.timestamp = time.strftime('%Y%m%d_%H%M%S')
        self.output_directory_ensure()

    def output_directory_ensure(self):
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)

    def output_algorithm_result_save(self, algorithm_name: str, results: Dict[str, Any]) -> Optional[str]:
        """
        保存算法结果 - 通过配置控制输出内容
        """
        try:
            # 检查是否允许保存数据文件
            if not self.config.config_get('output', 'save_data_files', True):
                self.config.logger.info(f"数据文件保存被禁用，跳过{algorithm_name}结果保存")
                return None

            algo_dir = os.path.join(self.output_dir, algorithm_name, self.timestamp)
            os.makedirs(algo_dir, exist_ok=True)

            # 保存原始参数矩阵
            if (self.config.config_get('output', 'save_scheme_matrix', True) and
                    'original_data_matrix' in results):
                original_filename = f"{algorithm_name}_original_matrix.txt"
                original_filepath = os.path.join(algo_dir, original_filename)
                np.savetxt(original_filepath, results['original_data_matrix'],
                           delimiter='\t', fmt='%.6f')
                self.config.logger.info(f"原始参数矩阵已保存: {original_filename}")

            # 保存标准化指标矩阵
            if (self.config.config_get('output', 'save_scheme_matrix', True) and
                    'standardized_data_matrix' in results):
                standardized_filename = f"{algorithm_name}_standardized_matrix.txt"
                standardized_filepath = os.path.join(algo_dir, standardized_filename)
                np.savetxt(standardized_filepath, results['standardized_data_matrix'],
                           delimiter='\t', fmt='%.6f')
                self.config.logger.info(f"标准化指标矩阵已保存: {standardized_filename}")

            # 保存核心数据文件（根据配置）- 现在使用原始矩阵
            if self.config.config_get('output', 'save_scheme_matrix', True):
                self.output_core_data_save(results, algo_dir, algorithm_name)

            # 保存决策参数（根据配置）
            if self.config.config_get('output', 'save_decision_params', True):
                self.output_decision_params_save(results, algo_dir, algorithm_name)

            # 保存排名结果（根据配置）
            if self.config.config_get('output', 'save_rankings', True) and 'ranks' in results:
                self.output_ranking_results_save(results, algo_dir, algorithm_name)

            # 对于模糊评价法，保存一级评价排名结果（简化版）
            if (algorithm_name == 'AHP_FUZZY' and
                    self.config.config_get('output', 'save_fuzzy_first_level', True) and
                    'first_level_ranking_results' in results):
                self.output_fuzzy_first_level_save(results, algo_dir, algorithm_name)

            # 生成可视化（根据配置）
            if self.config.config_get('output', 'save_plots', True):
                self.output_visualizations_generate(results, algo_dir, algorithm_name)

            self.config.logger.info(f"{algorithm_name} 结果已保存至: {algo_dir}")
            return algo_dir

        except Exception as e:
            self.config.logger.error(f"保存{algorithm_name}结果失败: {e}")
            return None

    def output_fuzzy_first_level_save(self, results: Dict[str, Any], output_dir: str, algorithm_name: str):
        """
        保存模糊综合评价的一级评价排名结果 - 简化版，只保存排名对应的原始指标矩阵
        """
        try:
            first_level_results = results['first_level_ranking_results']
            original_matrix = results['original_data_matrix']

            # 创建一级评价结果目录
            first_level_dir = os.path.join(output_dir, 'first_level_evaluation')
            os.makedirs(first_level_dir, exist_ok=True)

            # 保存每个子系统的一级评价排名及对应的原始指标矩阵
            for subsystem, result in first_level_results.items():
                subsystem_name = result['name']
                indices = result['indices']

                # 保存子系统排名及对应的原始指标
                filename = f"{subsystem}_ranking_with_original_matrix.txt"
                filepath = os.path.join(first_level_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"子系统: {subsystem_name}\n")
                    f.write(f"指标索引: {indices}\n")
                    f.write(
                        f"最优方案: 方案{result['best_scheme_index'] + 1}, 得分: {result['best_scheme_score']:.6f}\n")
                    f.write("=" * 80 + "\n")

                    # 表头：排名 | 方案号 | 得分 | 原始指标数据
                    header = "排名\t方案号\t得分\t"
                    if isinstance(indices, slice):
                        # 切片索引
                        n_indicators = len(range(indices.start, indices.stop))
                        header += "\t".join([f"指标{i + 1}" for i in range(n_indicators)])
                    else:
                        # 列表索引
                        header += "\t".join([f"指标{i + 1}" for i in range(len(indices))])
                    f.write(header + "\n")

                    # 按排名排序输出
                    sorted_indices = result['sorted_indices']
                    for rank_position, scheme_idx in enumerate(sorted_indices):
                        line = f"{rank_position + 1}\t{scheme_idx + 1}\t{result['scores'][scheme_idx]:.6f}\t"

                        # 提取该方案对应的原始指标数据
                        if isinstance(indices, slice):
                            # 切片索引
                            indicator_data = original_matrix[scheme_idx, indices]
                        else:
                            # 列表索引
                            indicator_data = original_matrix[scheme_idx, indices]

                        # 添加指标数据
                        line += "\t".join([f"{x:.6f}" for x in indicator_data])
                        f.write(line + "\n")

                self.config.logger.info(f"子系统 {subsystem_name} 排名及原始指标已保存: {filename}")

        except Exception as e:
            self.config.logger.error(f"保存模糊综合评价一级评价结果失败: {e}")

    def output_core_data_save(self, results: Dict[str, Any], output_dir: str, algorithm_name: str):
        """
        保存核心数据：排序、方案号、原始参数矩阵
        """
        try:
            # 优先使用原始数据矩阵，如果不存在则使用标准化矩阵
            if 'original_data_matrix' in results:
                data_matrix = results['original_data_matrix']
                matrix_type = "原始参数"
            elif 'data_matrix' in results:
                data_matrix = results['data_matrix']
                matrix_type = "标准化指标"
            else:
                return

            if 'ranks' not in results:
                return

            ranks = results['ranks']
            n_schemes, n_indicators = data_matrix.shape

            # 按排名排序（从最优到最差）
            sorted_indices = np.argsort(ranks)

            # 创建核心数据矩阵：排序 | 方案号 | 原始参数矩阵
            core_data = np.column_stack([
                np.arange(1, n_schemes + 1),  # 排序（1,2,3,...）
                sorted_indices + 1,  # 方案号（原始索引+1）
                data_matrix[sorted_indices]  # 原始参数矩阵（按排名排序）
            ])

            # 保存核心数据
            filename = f"{algorithm_name}_core_data.txt"
            filepath = os.path.join(output_dir, filename)

            # 写入列标题
            headers = ['排序', '方案号'] + [f'参数{i + 1}' for i in range(n_indicators)]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 数据矩阵类型: {matrix_type}矩阵\n")
                f.write('\t'.join(headers) + '\n')
                for row in core_data:
                    line_parts = [f"{int(row[0])}", f"{int(row[1])}"] + [f"{x:.6f}" for x in row[2:]]
                    f.write('\t'.join(line_parts) + '\n')

            self.config.logger.info(f"核心数据已保存 ({matrix_type}): {filename}")

        except Exception as e:
            self.config.logger.error(f"保存核心数据失败: {e}")

    def output_decision_params_save(self, results: Dict[str, Any], output_dir: str, algorithm_name: str):
        """
        保存决策参数
        """
        try:
            decision_params = {}

            # 收集决策参数
            if 'best_solution' in results:
                decision_params['best_solution'] = results['best_solution'].tolist()

            if 'W' in results and 'H' in results:  # NMF算法
                decision_params['base_vector_W'] = results['W'].tolist()
                decision_params['weight_vector_H'] = results['H'].tolist()
                decision_params['best_scheme_index'] = int(results['best_scheme_index'])
                decision_params['best_scheme_score'] = float(results['best_scheme_score'])

            if 'a' in results and 'z' in results:  # PP算法
                decision_params['projection_direction_a'] = results['a'].tolist()
                decision_params['projection_values_z'] = results['z'].tolist()
                decision_params['best_scheme_index'] = int(results['best_scheme_index'])
                decision_params['best_scheme_score'] = float(results['best_scheme_score'])

            if 'ahp_weights' in results:  # Fuzzy算法
                decision_params['ahp_weights'] = results['ahp_weights'].tolist()
                decision_params['final_scores'] = results['final_scores'].tolist()
                decision_params['best_scheme_index'] = int(results['best_scheme_index'])
                decision_params['best_scheme_score'] = float(results['best_scheme_score'])

            # 通用参数
            if 'best_fitness' in results:
                decision_params['best_fitness'] = float(results['best_fitness'])
            if 'execution_time' in results:
                decision_params['execution_time'] = float(results['execution_time'])

            # 保存决策参数
            if decision_params:
                filename = f"{algorithm_name}_decision_params.json"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(decision_params, f, indent=2, ensure_ascii=False)

                self.config.logger.info(f"决策参数已保存: {filename}")

        except Exception as e:
            self.config.logger.error(f"保存决策参数失败: {e}")

    def output_ranking_results_save(self, results: Dict[str, Any], output_dir: str, algorithm_name: str):
        """
        保存排名结果
        """
        try:
            if 'ranks' not in results:
                return

            ranks = results['ranks']
            n_schemes = len(ranks)

            # 创建排名结果
            ranking_data = []
            for scheme_idx in range(n_schemes):
                ranking_data.append({
                    'scheme_index': int(scheme_idx + 1),
                    'rank': int(ranks[scheme_idx] + 1),
                    'rank_order': int(np.sum(ranks < ranks[scheme_idx]) + 1)  # 排名顺序
                })

            # 按排名顺序排序
            ranking_data.sort(key=lambda x: x['rank'])

            # 保存排名结果
            filename = f"{algorithm_name}_ranking_results.txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("方案号\t排名\t排名顺序\n")
                for item in ranking_data:
                    f.write(f"{item['scheme_index']}\t{item['rank']}\t{item['rank_order']}\n")

            self.config.logger.info(f"排名结果已保存: {filename}")

        except Exception as e:
            self.config.logger.error(f"保存排名结果失败: {e}")

    def output_visualizations_generate(self, results: Dict[str, Any], output_dir: str, algorithm_name: str):
        """
        生成可视化图表 - 根据配置控制
        """
        try:
            plot_format = self.config.config_get('output', 'plot_format', 'png')
            plot_dpi = self.config.config_get('output', 'plot_dpi', 300)

            # 收敛曲线
            if (self.config.config_get('output', 'save_convergence_plot', True) and
                    'cost_history' in results and len(results['cost_history']) > 0):
                plot_path = os.path.join(output_dir, f'convergence_plot.{plot_format}')
                self.output_convergence_plot_save(results['cost_history'], plot_path, plot_dpi)

        except Exception as e:
            self.config.logger.error(f"生成可视化失败: {e}")

    def output_integrated_results_save(self, integrated_results: Dict[str, Any]) -> Optional[str]:
        """
        保存整合结果 - 根据配置控制输出
        """
        try:
            # 检查是否允许保存数据文件
            if not self.config.config_get('output', 'save_data_files', True):
                self.config.logger.info("数据文件保存被禁用，跳过整合结果保存")
                return None

            integrated_dir = os.path.join(self.output_dir, 'integrated', self.timestamp)
            os.makedirs(integrated_dir, exist_ok=True)

            # 保存整合的核心数据
            if (self.config.config_get('output', 'save_scheme_matrix', True) and
                    'original_data_matrix' in integrated_results and 'final_ranking' in integrated_results):
                self.output_integrated_core_data_save(integrated_results, integrated_dir)

            # 保存整合的排名结果
            if (self.config.config_get('output', 'save_rankings', True) and
                    'final_ranking' in integrated_results):
                self.output_integrated_ranking_save(integrated_results, integrated_dir)

            # 保存序号总和报告
            if 'rank_sum_report' in integrated_results:
                self.output_rank_sum_report_save(integrated_results, integrated_dir)

            # 保存两两算法组合的序号总和排序结果（根据配置）
            if (self.config.config_get('output', 'save_pairwise_rankings', True) and
                    'pairwise_rank_sum_results' in integrated_results):
                self.output_pairwise_rank_sum_save(integrated_results, integrated_dir)

            self.config.logger.info(f"整合结果已保存至: {integrated_dir}")
            return integrated_dir

        except Exception as e:
            self.config.logger.error(f"保存整合结果失败: {e}")
            return None

    def output_pairwise_rank_sum_save(self, integrated_results: Dict[str, Any], output_dir: str):
        """
        保存两两算法组合的序号总和排序结果
        """
        try:
            pairwise_results = integrated_results['pairwise_rank_sum_results']

            for combo_name, combo_result in pairwise_results.items():
                # 创建子目录
                pairwise_dir = os.path.join(output_dir, 'pairwise_rankings')
                os.makedirs(pairwise_dir, exist_ok=True)

                # 保存最终排名
                filename = f"{combo_name}_final_ranking.txt"
                filepath = os.path.join(pairwise_dir, filename)

                final_ranking = combo_result['final_ranking']
                n_schemes = len(final_ranking)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"两两算法组合: {combo_name}\n")
                    f.write(f"使用算法: {', '.join(combo_result['algorithms_used'])}\n")
                    f.write("方案号\t最终排名\n")
                    for scheme_idx in range(n_schemes):
                        f.write(f"{scheme_idx + 1}\t{final_ranking[scheme_idx] + 1}\n")

                # 保存详细报告
                report_filename = f"{combo_name}_rank_sum_report.json"
                report_filepath = os.path.join(pairwise_dir, report_filename)

                with open(report_filepath, 'w', encoding='utf-8') as f:
                    json.dump(combo_result['rank_sum_report'], f, indent=2, ensure_ascii=False)

                self.config.logger.info(f"两两组合 {combo_name} 排名结果已保存")

            # 生成两两组合比较总结
            self.output_pairwise_summary_generate(pairwise_results, output_dir)

        except Exception as e:
            self.config.logger.error(f"保存两两算法组合排名结果失败: {e}")

    def output_pairwise_summary_generate(self, pairwise_results: Dict[str, Any], output_dir: str):
        """
        生成两两算法组合比较总结
        """
        try:
            summary = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'pairwise_comparisons': {}
            }

            for combo_name, combo_result in pairwise_results.items():
                final_ranking = combo_result['final_ranking']
                best_scheme = np.argmin(final_ranking) + 1  # 1-indexed

                summary['pairwise_comparisons'][combo_name] = {
                    'algorithms_used': combo_result['algorithms_used'],
                    'best_scheme': int(best_scheme),
                    'final_ranking': final_ranking.tolist()
                }

            # 保存总结文件
            summary_file = os.path.join(output_dir, 'pairwise_comparison_summary.json')
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.config.logger.info("两两算法组合比较总结已生成")

        except Exception as e:
            self.config.logger.error(f"生成两两算法组合比较总结失败: {e}")

    def output_rank_sum_report_save(self, integrated_results: Dict[str, Any], output_dir: str):
        """
        保存序号总和理论分析报告
        """
        try:
            rank_sum_report = integrated_results['rank_sum_report']

            filename = "rank_sum_report.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(rank_sum_report, f, indent=2, ensure_ascii=False)

            self.config.logger.info(f"序号总和报告已保存: {filename}")

        except Exception as e:
            self.config.logger.error(f"保存序号总和报告失败: {e}")

    def output_integrated_core_data_save(self, integrated_results: Dict[str, Any], output_dir: str):
        """
        保存整合核心数据 - 使用原始参数矩阵
        """
        try:
            # 优先使用原始数据矩阵
            if 'original_data_matrix' in integrated_results:
                data_matrix = integrated_results['original_data_matrix']
                matrix_type = "原始参数"
            elif 'data_matrix' in integrated_results:
                data_matrix = integrated_results['data_matrix']
                matrix_type = "标准化指标"
            else:
                return

            final_ranking = integrated_results['final_ranking']
            n_schemes, n_indicators = data_matrix.shape

            # 按整合排名排序
            sorted_indices = np.argsort(final_ranking)

            # 创建整合核心数据矩阵
            integrated_data = np.column_stack([
                np.arange(1, n_schemes + 1),  # 排序
                sorted_indices + 1,  # 方案号
                final_ranking[sorted_indices] + 1,  # 整合排名
                data_matrix[sorted_indices]  # 原始参数矩阵
            ])

            # 保存整合核心数据
            filename = "integrated_core_data.txt"
            filepath = os.path.join(output_dir, filename)

            headers = ['排序', '方案号', '整合排名'] + [f'参数{i + 1}' for i in range(n_indicators)]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 数据矩阵类型: {matrix_type}矩阵\n")
                f.write('\t'.join(headers) + '\n')
                for row in integrated_data:
                    line_parts = [f"{int(row[0])}", f"{int(row[1])}", f"{int(row[2])}"] + [f"{x:.6f}" for x in row[3:]]
                    f.write('\t'.join(line_parts) + '\n')

            self.config.logger.info(f"整合核心数据已保存 ({matrix_type}): {filename}")

        except Exception as e:
            self.config.logger.error(f"保存整合核心数据失败: {e}")

    def output_integrated_ranking_save(self, integrated_results: Dict[str, Any], output_dir: str):
        """
        保存整合排名结果
        """
        try:
            if 'final_ranking' not in integrated_results:
                return

            final_ranking = integrated_results['final_ranking']
            n_schemes = len(final_ranking)

            # 创建整合排名结果
            integrated_ranking = []
            for scheme_idx in range(n_schemes):
                integrated_ranking.append({
                    'scheme_index': int(scheme_idx + 1),
                    'final_rank': int(final_ranking[scheme_idx] + 1),
                    'rank_order': int(np.sum(final_ranking < final_ranking[scheme_idx]) + 1)
                })

            # 按最终排名排序
            integrated_ranking.sort(key=lambda x: x['final_rank'])

            # 保存整合排名
            filename = "integrated_ranking_results.txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("方案号\t最终排名\t排名顺序\n")
                for item in integrated_ranking:
                    f.write(f"{item['scheme_index']}\t{item['final_rank']}\t{item['rank_order']}\n")

            self.config.logger.info(f"整合排名结果已保存: {filename}")

        except Exception as e:
            self.config.logger.error(f"保存整合排名结果失败: {e}")

    def output_convergence_plot_save(self, cost_history: List[float], filepath: str, dpi: int = 300):
        """
        保存收敛曲线
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(cost_history, 'b-', linewidth=2)
            plt.xlabel('迭代次数')
            plt.ylabel('适应度')
            plt.title('优化收敛曲线')
            plt.grid(True, alpha=0.3)
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
            plt.close()
            self.config.logger.info(f"收敛曲线已保存: {filepath}")
        except Exception as e:
            self.config.logger.error(f"保存收敛曲线失败 {filepath}: {e}")

    def output_summary_report_generate(self, all_results: Dict[str, Any], integrated_results: Dict[str, Any]):
        """
        生成总结报告
        """
        try:
            if not self.config.config_get('output', 'save_data_files', True):
                return

            import json
            summary = {
                'evaluation_summary': {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'algorithms_executed': list(all_results.keys()),
                    'successful_algorithms': [
                        name for name, result in all_results.items()
                        if result.get('success', False)
                    ],
                    'integration_successful': integrated_results.get('integration_successful', False),
                },
                'output_configuration': {
                    'save_plots': self.config.config_get('output', 'save_plots', True),
                    'save_data_files': self.config.config_get('output', 'save_data_files', True),
                    'save_scheme_matrix': self.config.config_get('output', 'save_scheme_matrix', True),
                    'save_decision_params': self.config.config_get('output', 'save_decision_params', True),
                    'save_pairwise_rankings': self.config.config_get('output', 'save_pairwise_rankings', True),
                    'save_fuzzy_first_level': self.config.config_get('output', 'save_fuzzy_first_level', True)
                }
            }

            if integrated_results.get('integration_successful', False):
                summary['final_ranking'] = integrated_results['final_ranking'].tolist()

            summary_file = os.path.join(self.output_dir, 'evaluation_summary.json')
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.config.logger.info(f"评估总结已保存: {summary_file}")

        except Exception as e:
            self.config.logger.error(f"生成总结报告失败: {e}")