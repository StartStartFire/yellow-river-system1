import pandas as pd

## 读取数据文件
# 读取水库特征数据文件
Parameters_LYX = pd.read_excel('./水库特征数据集/龙羊峡.xlsx', sheet_name=None)
Parameters_LXW = pd.read_excel('./水库特征数据集/拉西瓦.xlsx', sheet_name=None)
Parameters_LJ = pd.read_excel('./水库特征数据集/李家峡.xlsx', sheet_name=None)
Parameters_GBX = pd.read_excel('./水库特征数据集/公伯峡.xlsx', sheet_name=None)
Parameters_JSX = pd.read_excel('./水库特征数据集/积石峡.xlsx', sheet_name=None)
Parameters_LJX = pd.read_excel('./水库特征数据集/刘家峡.xlsx', sheet_name=None)
Parameters_HSX = pd.read_excel('./水库特征数据集/黑山峡.xlsx', sheet_name=None)

'''# 读取实际运行过程数据集
reserviorRun_LJX = pd.read_excel('./水库实际运行过程数据集/龙羊峡2019-2023年水库日运行资料.xlsx', engine='openpyxl')
reserviorRun_LXW = pd.read_excel('./水库实际运行过程数据集/拉西瓦2019-2023年水库日运行资料.xlsx', engine='openpyxl')
reserviorRun_LJ = pd.read_excel('./水库实际运行过程数据集/李家峡2019-2023年水库日运行资料.xlsx', engine='openpyxl')
reserviorRun_GBX = pd.read_excel('./水库实际运行过程数据集/公伯峡2019-2023年水库日运行资料.xlsx', engine='openpyxl')
reserviorRun_JSX = pd.read_excel('./水库实际运行过程数据集/积石峡2019-2023年水库日运行资料.xlsx', engine='openpyxl')'''

# 读取水文站逐日平均流量
# 干流
hydStation_tnh = pd.read_excel('./水文站逐日平均流量/唐乃亥.xlsx', engine='openpyxl')
hydStation_xh = pd.read_excel('./水文站逐日平均流量/循化.xlsx', engine='openpyxl')
hydStation_lz = pd.read_excel('./水文站逐日平均流量/兰州.xlsx', engine='openpyxl')
hydStation_xhy = pd.read_excel('./水文站逐日平均流量/下河沿.xlsx', engine='openpyxl')

# 支流
hydStation_zq = pd.read_excel('./水文站逐日平均流量/大夏河-折桥.xlsx', engine='openpyxl')
hydStation_hq = pd.read_excel('./水文站逐日平均流量/洮河-红旗.xlsx', engine='openpyxl')
hydStation_xt = pd.read_excel('./水文站逐日平均流量/大通河-享堂.xlsx', engine='openpyxl')
hydStation_mh = pd.read_excel('./水文站逐日平均流量/湟水-民和.xlsx', engine='openpyxl')
hydStation_jy = pd.read_excel('./水文站逐日平均流量/祖厉河-靖远.xlsx', engine='openpyxl')
hydStation_qys = pd.read_excel('./水文站逐日平均流量/清水河-泉眼山.xlsx', engine='openpyxl')

# 区间引水(不考虑)
'''
# 生活用水
# 工业水
# 农业水
# 生态水
'''

# 场次洪水过程
floodProcess_tnh = pd.read_excel('./场次洪水过程/典型年洪水过程1.xlsx', engine='openpyxl')
floodProcess_hq = pd.read_excel('./场次洪水过程/红旗.xlsx', engine='openpyxl')
floodProcess_zq = pd.read_excel('./场次洪水过程/折桥.xlsx', engine='openpyxl')
floodProcess_xt = pd.read_excel('./场次洪水过程/享堂.xlsx', engine='openpyxl')
floodProcess_mh = pd.read_excel('./场次洪水过程/民和.xlsx', engine='openpyxl')
# floodProcess_tnh_15 = pd.read_excel('./场次洪水过程/15日典型年洪水过程.xlsx')
# floodProcess_tnh_25 = pd.read_excel('./场次洪水过程/25日典型年洪水过程.xlsx')

'''
数据预处理
'''
# 时间格式转化
#支流水文站
hydStation_zq['时间'] = pd.to_datetime(hydStation_zq['时间'])
hydStation_hq['时间'] = pd.to_datetime(hydStation_hq['时间'])
hydStation_xt['时间'] = pd.to_datetime(hydStation_xt['时间'])
hydStation_mh['时间'] = pd.to_datetime(hydStation_mh['时间'])
hydStation_jy['时间'] = pd.to_datetime(hydStation_jy['时间'])
hydStation_qys['时间'] = pd.to_datetime(hydStation_qys['时间'])

#干流水文站
hydStation_tnh['时间'] = pd.to_datetime(hydStation_tnh['时间'])
hydStation_xh['时间'] = pd.to_datetime(hydStation_xh['时间'])
hydStation_lz['时间'] = pd.to_datetime(hydStation_lz['时间'])
hydStation_xhy['时间'] = pd.to_datetime(hydStation_xhy['时间'])
'''#水库
reserviorRun_LJX['日期'] = pd.to_datetime(reserviorRun_LJX['日期'])
reserviorRun_LXW['日期'] = pd.to_datetime(reserviorRun_LXW['日期'])
reserviorRun_LJ['日期'] = pd.to_datetime(reserviorRun_LJ['日期'])
reserviorRun_GBX['日期'] = pd.to_datetime(reserviorRun_GBX['日期'])
reserviorRun_JSX['日期'] = pd.to_datetime(reserviorRun_JSX['日期'])'''

# 处理水文站中的0值
hydStation_zq['流量'] = hydStation_zq['流量'].replace(0, pd.NA)
hydStation_zq['流量'] = hydStation_zq['流量'].interpolate(method='cubic')
hydStation_hq['流量'] = hydStation_hq['流量'].replace(0, pd.NA)
hydStation_hq['流量'] = hydStation_hq['流量'].interpolate(method='cubic')
hydStation_xt['流量'] = hydStation_xt['流量'].replace(0, pd.NA)
hydStation_xt['流量'] = hydStation_xt['流量'].interpolate(method='cubic')
hydStation_mh['流量'] = hydStation_mh['流量'].replace(0, pd.NA)
hydStation_mh['流量'] = hydStation_mh['流量'].interpolate(method='cubic')
hydStation_jy['流量'] = hydStation_jy['流量'].replace(0, pd.NA)
hydStation_jy['流量'] = hydStation_jy['流量'].interpolate(method='cubic')
hydStation_qys['流量'] = hydStation_qys['流量'].replace(0, pd.NA)
hydStation_qys['流量'] = hydStation_qys['流量'].interpolate(method='cubic')


hydStation_tnh['流量'] = hydStation_tnh['流量'].replace(0, pd.NA)
hydStation_tnh['流量'] = hydStation_tnh['流量'].interpolate(method='cubic')
hydStation_xh['流量'] = hydStation_xh['流量'].replace(0, pd.NA)
hydStation_xh['流量'] = hydStation_xh['流量'].interpolate(method='cubic')
hydStation_lz['流量'] = hydStation_lz['流量'].replace(0, pd.NA)
hydStation_lz['流量'] = hydStation_lz['流量'].interpolate(method='cubic')
hydStation_xhy['流量'] = hydStation_xhy['流量'].replace(0, pd.NA)
hydStation_xhy['流量'] = hydStation_xhy['流量'].interpolate(method='cubic')

# 合并相同日期的数据
hydStation_zq['日期'] = hydStation_zq['时间'].dt.date
hydStation_zq = hydStation_zq.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_hq['日期'] = hydStation_hq['时间'].dt.date
hydStation_hq = hydStation_hq.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_xt['日期'] = hydStation_xt['时间'].dt.date
hydStation_xh['日期'] = hydStation_xh['时间'].dt.date
hydStation_xt = hydStation_xt.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_mh['日期'] = hydStation_mh['时间'].dt.date
hydStation_mh = hydStation_mh.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_jy['日期'] = hydStation_jy['时间'].dt.date
hydStation_jy = hydStation_jy.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_qys['日期'] = hydStation_qys['时间'].dt.date
hydStation_qys = hydStation_qys.groupby('日期').agg({'流量':'mean'}).reset_index()

hydStation_tnh['日期'] = hydStation_tnh['时间'].dt.date
hydStation_tnh = hydStation_tnh.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_xh['日期'] = hydStation_xh['时间'].dt.date
hydStation_xh = hydStation_xh.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_lz['日期'] = hydStation_lz['时间'].dt.date
hydStation_lz = hydStation_lz.groupby('日期').agg({'流量':'mean'}).reset_index()
hydStation_xhy['日期'] = hydStation_xhy['时间'].dt.date
hydStation_xhy = hydStation_xhy.groupby('日期').agg({'流量':'mean'}).reset_index()

'''reserviorRun_LJX['日期'] = reserviorRun_LJX['日期'].dt.date
reserviorRun_LXW['日期'] = reserviorRun_LXW['日期'].dt.date
reserviorRun_LJ['日期'] = reserviorRun_LJ['日期'].dt.date
reserviorRun_GBX['日期'] = reserviorRun_GBX['日期'].dt.date
reserviorRun_JSX['日期'] = reserviorRun_JSX['日期'].dt.date'''