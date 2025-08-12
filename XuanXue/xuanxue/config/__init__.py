"""
配置模块
"""

# 保留原有配置变量（向后兼容）
from .config import gan, zhi, gan_start_map

# 导入股票数据库路径管理功能
from .config_manager import (
    get_stock_meta_path,
    set_stock_meta_path, 
    check_stock_meta_path,
    StockPathManager,
    get_stock_kbar_path,
    set_stock_kbar_path,
    check_stock_kbar_path
)

__all__ = [
    # 原有配置
    'gan', 'zhi', 'gan_start_map',
    # 股票数据库路径管理
    'get_stock_meta_path', 
    'set_stock_meta_path',
    'check_stock_meta_path',
    'StockPathManager',
    'get_stock_kbar_path',
    'set_stock_kbar_path',
    'check_stock_kbar_path'

]