"""
股票数据库路径配置管理器
只管理 stock_meta_path 配置
"""
import os
import sqlite3
from typing import Optional, Tuple

class StockPathManager:
    """股票数据库路径管理器"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_file = os.path.join(current_dir, "config.txt")
        else:
            self.config_file = config_file
        
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """确保配置文件存在"""
        if not os.path.exists(self.config_file):
            # 创建默认配置
            self._save_path("stock_meta.db")
    
    def _load_path(self) -> str:
        """从配置文件加载路径"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('stock_meta_path='):
                        return line.split('=', 1)[1].strip()
        except Exception:
            pass
        
        # 如果读取失败，返回默认值
        return "stock_meta.db"
    
    def _save_path(self, path: str):
        """保存路径到配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# XuanXue 股票数据库路径配置\n")
                f.write("# 请确保路径指向有效的SQLite数据库文件\n\n")
                f.write(f"stock_meta_path={path}\n")
            
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_path(self) -> str:
        """获取当前配置的股票数据库路径（绝对路径）"""
        relative_path = self._load_path()
        
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(relative_path):
            return relative_path
        
        # 否则转换为绝对路径（相对于config文件所在目录）
        config_dir = os.path.dirname(self.config_file)
        absolute_path = os.path.abspath(os.path.join(config_dir, relative_path))
        return absolute_path
    
    def set_path(self, path: str) -> bool:
        """设置股票数据库路径"""
        # 转换为绝对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return self._save_path(path)
    
    def check_path(self) -> Tuple[bool, str]:
        """
        检查当前路径是否能正常工作
        
        Returns:
            Tuple[bool, str]: (是否可用, 提示信息)
        """
        path = self.get_path()
        
        # 检查文件是否存在
        if not os.path.exists(path):
            return False, f"数据库文件不存在: {path}"
        
        # 检查是否为文件
        if not os.path.isfile(path):
            return False, f"路径不是文件: {path}"
        
        # 检查是否为SQLite数据库
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            
            # 检查是否有stock_meta表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='stock_meta'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return False, f"数据库中缺少 'stock_meta' 表: {path}"
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(stock_meta)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = ['symbol', 'name', 'exchange', 'list_date']
            missing_columns = [col for col in required_columns if col not in columns]
            
            conn.close()
            
            if missing_columns:
                return False, f"stock_meta表缺少必要字段: {missing_columns}"
            
            return True, f"数据库路径正常: {path}"
            
        except sqlite3.Error as e:
            return False, f"数据库连接失败: {e}"
        except Exception as e:
            return False, f"检查数据库时出错: {e}"

# 全局实例
_path_manager = None

def get_path_manager() -> StockPathManager:
    """获取路径管理器实例"""
    global _path_manager
    if _path_manager is None:
        _path_manager = StockPathManager()
    return _path_manager

def get_stock_meta_path() -> str:
    """获取股票数据库路径（绝对路径）"""
    return get_path_manager().get_path()

def set_stock_meta_path(path: str) -> bool:
    """设置股票数据库路径"""
    return get_path_manager().set_path(path)

def check_stock_meta_path() -> Tuple[bool, str]:
    """
    检查股票数据库路径是否可用
    
    Returns:
        Tuple[bool, str]: (是否可用, 提示信息)
    """
    return get_path_manager().check_path()

# 测试代码
if __name__ == "__main__":
    print("=== 股票数据库路径管理器测试 ===")
    
    # 测试1：查看当前路径
    current_path = get_stock_meta_path()
    print(f"当前路径: {current_path}")
    
    # 测试2：检查路径是否可用
    is_valid, message = check_stock_meta_path()
    print(f"路径检查: {'✓' if is_valid else '✗'} {message}")
    
    # 测试3：设置新路径
    print("\n设置新路径测试:")
    test_path = "D:/test/stock.db"
    if set_stock_meta_path(test_path):
        print(f"设置成功: {get_stock_meta_path()}")
        is_valid, message = check_stock_meta_path()
        print(f"新路径检查: {'✓' if is_valid else '✗'} {message}")
    
    # 恢复原路径
    set_stock_meta_path(current_path)
    print(f"\n恢复原路径: {get_stock_meta_path()}")