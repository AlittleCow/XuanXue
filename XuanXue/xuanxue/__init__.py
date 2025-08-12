"""
XuanXue - 玄学数据分析包

nBoardDateGanZhi('000001.SZ') 这样是查询该股票上市日期的干支
DateTimeGanZhi('2025/07/29 18:08:00') 这样是计算单个日期的干支

KBarSeriesGanZhi( start-datetime , end-datetime, K线序列, useDB=false)
 这样是实时计算 K线序列在 Start-DateTime - End-DateTime的干支

KbarSeriesGanZhi( start-datetime, end-datetime, NULL, useDB=true) 
这样是在 K线数据库里面查询 Start-DateTime - End-DateTime的K线序列 ,然后计算干支,如果已经计算过了, 就返回DB的干支结果
"""

__version__ = "0.1.0"
__author__ = "XuWu"

from .core.ganzhi_calculator import DateTimeGanZhi
from .core.stock_ganzhi import OnBoardDateGanZhi
from .core.kbarseriesganzhi import KbarSeriesGanZhi
from .utils import KbarSeriesKey,KbarSeries,Kbar

from XuanXue.xuanxue.config import (
    get_stock_meta_path,
    set_stock_meta_path, 
    check_stock_meta_path,
    get_stock_kbar_path,
    set_stock_kbar_path,
    check_stock_kbar_path,
)

__all__ = [
    "OnBoardDateGanZhi", 
    "DateTimeGanZhi",
    "get_stock_meta_path",
    "set_stock_meta_path", 
    "check_stock_meta_path",
    "get_stock_kbar_path",
    "set_stock_kbar_path",
    "check_stock_kbar_path",
    "KbarSeriesGanZhi",
    "KbarSeriesKey",
    "KbarSeries",
    "Kbar"
]
