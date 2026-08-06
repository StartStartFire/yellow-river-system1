# evaluation_system/__init__.py
# -*- coding: utf-8 -*-

"""
多算法综合评价系统包

一个集成了多种评价算法的综合系统，包括：
- NMF（非负矩阵分解布谷鸟搜索算法）
- PP（投影寻踪布谷鸟搜索算法）
- AHP_FUZZY（AHP模糊综合评价算法）

新增功能：
- 智能排名整合：使用序号总和理论进行最终排名整合
- 两两算法组合比较：分析不同算法组合的排名结果

使用示例：

# 1. 完整评估流程（包含排名整合）：
#    >>> from evaluation_system import run_complete_evaluation
#    >>> results = run_complete_evaluation('evaluation.xlsx')
#    >>> if results['integrated_results']['integration_successful']:
#    ...     print(f"最终排名: {results['integrated_results']['final_ranking']}")
#    ... else:
#    ...     print("评价失败")

# 2. 运行单个算法：
#    >>> from evaluation_system import run_single_algorithm
#    >>> pp_results = run_single_algorithm('PP', 'evaluation.xlsx')
#    >>> print(f"PP算法排名: {pp_results['results']['ranks']}")

# 3. 运行所有算法（不整合）：
#    >>> from evaluation_system import run_all_algorithms
#    >>> results = run_all_algorithms('evaluation.xlsx')
#    >>> for algo, result in results.items():
#    ...     print(f"{algo}算法运行状态: {result['success']}")

# 4. 获取系统信息：
#    >>> from evaluation_system import get_system_info, get_available_algorithms
#    >>> system_info = get_system_info()
#    >>> algorithms = get_available_algorithms()

# 5. 自定义配置运行：
#    >>> from evaluation_system import run_complete_evaluation
#    >>> custom_config = {
#    ...     'common': {'output_dir': 'my_results', 'log_level': 'DEBUG'},
#    ...     'optimization': {'N_pop': 50, 'N_IterTotal': 200}
#    ... }
#    >>> results = run_complete_evaluation('evaluation.xlsx', custom_config)

# 6. 获取算法描述：
#    >>> from evaluation_system import get_algorithm_description
#    >>> description = get_algorithm_description('PP')

# 7. 单独进行排名整合：
#    >>> from evaluation_system import calculate_rank_sum
#    >>> rankings = {'NMF': [0, 2, 1], 'PP': [1, 0, 2], 'AHP_FUZZY': [0, 1, 2]}
#    >>> final_ranking = calculate_rank_sum(rankings)
#    >>> print(f"最终排名: {final_ranking}")

支持的数据源格式：
- Excel文件 (.xlsx, .xls)
- CSV文件
- pandas DataFrame
- numpy数组

输出结果包含：
- 各算法独立排名
- 整合后的最终排名（使用序号总和理论）
- 详细的矩阵输出文件
- 评估总结报告
"""

__version__ = "1.2.0"
__author__ = "Evaluation System Team"

# 导出主要类和函数
from .main_controller import MainController
from .unified_config import UnifiedConfig
from .unified_output import UnifiedOutput

# 导出算法类
from .fuzzy_algorithm import FuzzyAlgorithm
from .nmf_algorithm import NMFAlgorithm
from .pp_algorithm import PPAlgorithm

# 导出排名整合模块
from .rank_sum_theory import RankSumTheory

# 导出数据处理函数
from .standardization_main import standardization_main


# 包级别的便捷函数
def run_complete_evaluation(data_source=None, config_dict=None):
    """
    运行完整评估流程的便捷函数（包含排名整合）

    Args:
        data_source: 数据源，可以是文件路径、DataFrame或numpy数组
        config_dict: 可选的配置字典

    Returns:
        Dict: 完整评估结果

    示例：
        # >>> results = run_complete_evaluation('evaluation.xlsx')
        # >>> if results['integrated_results']['integration_successful']:
        # >>>     final_ranking = results['integrated_results']['final_ranking']
        # >>>     print(f"最终整合排名: {final_ranking}")
        # >>> else:
        # >>>     print("评价失败")
    """
    controller = MainController(config_dict)
    return controller.complete_evaluation_run(data_source)


def run_all_algorithms(data_source=None, config_dict=None):
    """
    运行所有算法的便捷函数（不进行整合）

    Args:
        data_source: 数据源，可以是文件路径、DataFrame或numpy数组
        config_dict: 可选的配置字典

    Returns:
        Dict: 所有算法的结果

    示例：
        # >>> results = run_all_algorithms('evaluation.xlsx')
        # >>> for algo, result in results.items():
        # >>>     if result['success']:
        # >>>         print(f"{algo}算法最优方案: 方案{result['results']['best_scheme_index'] + 1}")
    """
    controller = MainController(config_dict)
    return controller.all_algorithms_run(data_source)


def run_single_algorithm(algorithm_name, data_source=None, config_dict=None):
    """
    运行单个算法的便捷函数

    Args:
        algorithm_name: 算法名称 ('NMF', 'PP', 'AHP_FUZZY')
        data_source: 数据源
        config_dict: 可选的配置字典

    Returns:
        Dict: 单个算法结果

    示例：
        # >>> pp_results = run_single_algorithm('PP', 'evaluation.xlsx')
        # >>> pp_ranks = pp_results['results']['ranks']
        # >>> print(f"PP算法排名: {pp_ranks}")
    """
    controller = MainController(config_dict)
    return controller.single_algorithm_run(algorithm_name, data_source)


def get_available_algorithms(config_dict=None):
    """
    获取可用算法列表的便捷函数

    Args:
        config_dict: 可选的配置字典

    Returns:
        List[str]: 可用算法名称列表

    示例：
        # >>> algorithms = get_available_algorithms()
        # >>> print(f"可用算法: {algorithms}")
        # ['NMF', 'PP', 'AHP_FUZZY']
    """
    controller = MainController(config_dict)
    return controller.available_algorithms_get()


def get_system_info(config_dict=None):
    """
    获取系统信息的便捷函数

    Args:
        config_dict: 可选的配置字典

    Returns:
        Dict: 系统信息

    示例：
        # >>> system_info = get_system_info()
        # >>> print(f"输出目录: {system_info['output_directory']}")
        # >>> print(f"配置摘要: {system_info['config_summary']}")
    """
    controller = MainController(config_dict)
    return controller.system_info_get()


def create_default_config():
    """
    创建默认配置的便捷函数

    Returns:
        UnifiedConfig: 默认配置实例

    示例：
        # >>> config = create_default_config()
        # >>> pop_size = config.config_get('optimization', 'N_pop')
        # >>> print(f"默认种群大小: {pop_size}")
    """
    return UnifiedConfig()


def quick_evaluate(data_file, algorithms=None):
    """
    快速评估函数 - 简化接口

    Args:
        data_file: 数据文件路径
        algorithms: 要运行的算法列表，None表示运行完整评估

    Returns:
        Dict: 评估结果

    示例：
        # >>> results = quick_evaluate('evaluation.xlsx', algorithms=['NMF', 'AHP_FUZZY'])
        # >>> for algo, result in results.items():
        # ...     print(f"{algo}算法运行状态: {result['success']}")
    """
    controller = MainController()

    if algorithms is None:
        # 运行完整评估（包含排名整合）
        return controller.complete_evaluation_run(data_file)
    else:
        # 运行指定算法（不进行整合）
        results = {}
        for algo in algorithms:
            if algo in controller.available_algorithms_get():
                results[algo] = controller.single_algorithm_run(algo, data_file)
        return results


def get_algorithm_description(algorithm_name):
    """
    获取算法描述的便捷函数

    Args:
        algorithm_name: 算法名称

    Returns:
        str: 算法描述

    示例：
        # >>> description = get_algorithm_description('PP')
        # >>> print(description)
        '投影寻踪布谷鸟搜索算法 - 基于投影指标的优化方法'
    """
    algorithms_info = {
        'NMF': '非负矩阵分解布谷鸟搜索算法 - 基于矩阵分解的优化方法',
        'PP': '投影寻踪布谷鸟搜索算法 - 基于投影指标的优化方法',
        'AHP_FUZZY': 'AHP模糊综合评价算法 - 结合层次分析和模糊数学的综合评价方法'
    }
    return algorithms_info.get(algorithm_name, '未知算法')


def get_fuzzy_first_level_results(data_source=None, config_dict=None):
    """
    获取模糊综合评价的一级评价结果的便捷函数

    Args:
        data_source: 数据源
        config_dict: 可选的配置字典

    Returns:
        Dict: 一级评价结果

    示例：
        # >>> first_level_results = get_fuzzy_first_level_results('evaluation.xlsx')
        # >>> for subsystem, result in first_level_results.items():
        # ...     print(f"{result['name']}最优方案: 方案{result['best_scheme_index'] + 1}")
    """
    controller = MainController(config_dict)
    fuzzy_results = controller.single_algorithm_run('AHP_FUZZY', data_source)

    if fuzzy_results.get('success', False) and 'first_level_ranking_results' in fuzzy_results['results']:
        return fuzzy_results['results']['first_level_ranking_results']
    else:
        raise ValueError("无法获取模糊综合评价的一级评价结果")


def calculate_rank_sum(rankings_dict, config_dict=None):
    """
    使用序号总和理论计算最终排名的便捷函数

    Args:
        rankings_dict: 各算法的排名字典 {算法名: 排名数组}
        config_dict: 配置字典

    Returns:
        np.ndarray: 最终排名

    示例:
        # >>> rankings = {
        # ...     'NMF': np.array([0, 2, 1]),
        # ...     'PP': np.array([1, 0, 2]),
        # ...     'AHP_FUZZY': np.array([0, 1, 2])
        # ... }
        # >>> final_ranking = calculate_rank_sum(rankings)
        # >>> print(f"最终排名: {final_ranking}")
    """
    config = UnifiedConfig(config_dict)
    rank_sum_calculator = RankSumTheory(config)
    return rank_sum_calculator.final_ranking_calculate(rankings_dict)


def calculate_pairwise_rank_sum(rankings_dict, config_dict=None):
    """
    计算两两算法组合的序号总和排序的便捷函数

    Args:
        rankings_dict: 各算法的排名字典
        config_dict: 配置字典

    Returns:
        Dict: 两两算法组合的序号总和排序结果

    示例:
        # >>> rankings = {
        # ...     'NMF': np.array([0, 2, 1]),
        # ...     'PP': np.array([1, 0, 2]),
        # ...     'AHP_FUZZY': np.array([0, 1, 2])
        # ... }
        # >>> pairwise_results = calculate_pairwise_rank_sum(rankings)
        # >>> print(f"NMF-PP组合最优方案: {pairwise_results['NMF-PP']['rank_sum_report']['best_scheme']}")
    """
    config = UnifiedConfig(config_dict)
    rank_sum_calculator = RankSumTheory(config)
    return rank_sum_calculator.pairwise_rank_sum_calculate(rankings_dict)


# 导出所有公共接口
__all__ = [
    # 主要类
    'MainController',
    'UnifiedConfig',
    'UnifiedOutput',

    # 算法类
    'FuzzyAlgorithm',
    'NMFAlgorithm',
    'PPAlgorithm',

    # 排名整合模块
    'RankSumTheory',

    # 数据处理函数
    'standardization_main',

    # 便捷函数
    'run_complete_evaluation',
    'run_all_algorithms',
    'run_single_algorithm',
    'get_available_algorithms',
    'get_system_info',
    'create_default_config',
    'quick_evaluate',
    'get_algorithm_description',
    'get_fuzzy_first_level_results',

    # 排名整合相关函数
    'calculate_rank_sum',
    'calculate_pairwise_rank_sum',
]

# 包初始化完成提示
# import logging
#
# logger = logging.getLogger('evaluation_system')
# logger.info(f"综合评价系统 v{__version__} 初始化完成")