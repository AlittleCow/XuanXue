"""
XuanXue - 玄学数据分析包

使用方法:
    import xuanxue as xx
    
    # 配置数据库
    xx.set_stock_meta_path("/path/to/stock_meta.db")
    
    # 查询股票干支
    result = xx.nBoardDateGanZhi('000001.SZ')
    
    # 计算日期干支
    ganzhi = xx.DateTimeGanZhi('2023/10/10')
"""

__version__ = "1.0.0"
__author__ = "XuWu"

# 导入主要功能
from .xuanxue import (
    OnBoardDateGanZhi,
    DateTimeGanZhi,
    get_stock_meta_path,
    set_stock_meta_path,
    check_stock_meta_path,
    get_stock_kbar_path,
    set_stock_kbar_path,
    check_stock_kbar_path,
    KbarSeriesGanZhi,
    KbarSeriesKey,
    KbarSeries,
    Kbar

)


__all__ = [
    # 主要函数
    "OnBoardDateGanZhi",
    "DateTimeGanZhi", 
    "KbarSeriesGanZhi",

    
    # 配置管理
    "get_stock_meta_path",
    "set_stock_meta_path",
    "check_stock_meta_path",
    "get_stock_kbar_path",
    "set_stock_kbar_path",
    "check_stock_kbar_path",

    #类别
    "KbarSeriesKey",
    "KbarSeries",
    "Kbar",


    

    
    # 版本信息
    "__version__", "__author__"
]