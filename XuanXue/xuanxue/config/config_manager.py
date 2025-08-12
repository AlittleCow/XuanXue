"""
股票数据库路径配置管理器
管理 stock_meta_path 和 stock_kbar_path 配置
"""
import os
import sqlite3
from typing import Optional, Tuple, Dict

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
            self._save_paths({
                "stock_meta_path": "stock_meta.db",
                "stock_kbar_path": "kbar_db/stock_kbar.db"
            })
    
    def _load_paths(self) -> Dict[str, str]:
        """从配置文件加载所有路径"""
        paths = {}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('stock_meta_path='):
                        paths['stock_meta_path'] = line.split('=', 1)[1].strip()
                    elif line.startswith('stock_kbar_path='):
                        paths['stock_kbar_path'] = line.split('=', 1)[1].strip()
        except Exception:
            pass
        
        # 设置默认值
        if 'stock_meta_path' not in paths:
            paths['stock_meta_path'] = "stock_meta.db"
        if 'stock_kbar_path' not in paths:
            paths['stock_kbar_path'] = "kbar_db/stock_kbar.db"
        
        return paths
    
    def _load_path(self, path_key: str) -> str:
        """从配置文件加载指定路径"""
        paths = self._load_paths()
        return paths.get(path_key, "")
    
    def _save_paths(self, paths: Dict[str, str]):
        """保存所有路径到配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# XuanXue 股票数据库路径配置\n")
                f.write("# 请确保路径指向有效的SQLite数据库文件\n\n")
                f.write(f"stock_meta_path={paths.get('stock_meta_path', 'stock_meta.db')}\n")
                f.write(f"stock_kbar_path={paths.get('stock_kbar_path', 'kbar_db/stock_kbar.db')}\n")
            
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def _save_path(self, path_key: str, path: str):
        """保存单个路径到配置文件"""
        current_paths = self._load_paths()
        current_paths[path_key] = path
        return self._save_paths(current_paths)
    
    def get_path(self, path_key: str = "stock_meta_path") -> str:
        """获取当前配置的数据库路径（绝对路径）"""
        relative_path = self._load_path(path_key)
        
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(relative_path):
            return relative_path
        
        # 否则转换为绝对路径（相对于config文件所在目录）
        config_dir = os.path.dirname(self.config_file)
        absolute_path = os.path.abspath(os.path.join(config_dir, relative_path))
        return absolute_path
    
    def set_path(self, path_key: str, path: str) -> bool:
        """设置数据库路径"""
        # 转换为绝对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return self._save_path(path_key, path)
    
    def check_path(self, path_key: str = "stock_meta_path") -> Tuple[bool, str]:
        """
        检查当前路径是否能正常工作
        
        Args:
            path_key: 路径键名，"stock_meta_path" 或 "stock_kbar_path"
            
        Returns:
            Tuple[bool, str]: (是否可用, 提示信息)
        """
        path = self.get_path(path_key)
        
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
            
            if path_key == "stock_meta_path":
                # 检查stock_meta表
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
                
                if missing_columns:
                    conn.close()
                    return False, f"stock_meta表缺少必要字段: {missing_columns}"
                    
            elif path_key == "stock_kbar_path":
                # 检查K线数据表（可能有多个表，检查是否为有效的SQLite数据库即可）
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if not tables:
                    conn.close()
                    return False, f"K线数据库中没有任何表: {path}"
                
                # 可以进一步检查是否有K线相关的表结构
                # 这里简化处理，只要有表就认为是有效的
            
            conn.close()
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

# === Stock Meta 数据库相关函数 ===
def get_stock_meta_path() -> str:
    """获取股票元数据数据库路径（绝对路径）"""
    return get_path_manager().get_path("stock_meta_path")

def set_stock_meta_path(path: str) -> bool:
    """设置股票元数据数据库路径"""
    return get_path_manager().set_path("stock_meta_path", path)

def check_stock_meta_path() -> Tuple[bool, str]:
    """
    检查股票元数据数据库路径是否可用
    
    Returns:
        Tuple[bool, str]: (是否可用, 提示信息)
    """
    return get_path_manager().check_path("stock_meta_path")

# === Stock KBar 数据库相关函数 ===
def get_stock_kbar_path() -> str:
    """获取股票K线数据库路径（绝对路径）"""
    return get_path_manager().get_path("stock_kbar_path")

def set_stock_kbar_path(path: str) -> bool:
    """设置股票K线数据库路径"""
    return get_path_manager().set_path("stock_kbar_path", path)

def check_stock_kbar_path() -> Tuple[bool, str]:
    """
    检查股票K线数据库路径是否可用
    
    Returns:
        Tuple[bool, str]: (是否可用, 提示信息)
    """
    return get_path_manager().check_path("stock_kbar_path")

# === 通用函数 ===
def get_all_paths() -> Dict[str, str]:
    """获取所有配置的数据库路径"""
    manager = get_path_manager()
    return {
        "stock_meta_path": manager.get_path("stock_meta_path"),
        "stock_kbar_path": manager.get_path("stock_kbar_path")
    }

def check_all_paths() -> Dict[str, Tuple[bool, str]]:
    """检查所有数据库路径是否可用"""
    manager = get_path_manager()
    return {
        "stock_meta": manager.check_path("stock_meta_path"),
        "stock_kbar": manager.check_path("stock_kbar_path")
    }

# 测试代码
if __name__ == "__main__":
    print("=== 股票数据库路径管理器测试 ===")
    
    # 测试1：查看当前所有路径
    all_paths = get_all_paths()
    print("当前配置的路径:")
    for key, path in all_paths.items():
        print(f"  {key}: {path}")
    
    # 测试2：检查所有路径是否可用
    print("\n路径检查结果:")
    all_checks = check_all_paths()
    for db_name, (is_valid, message) in all_checks.items():
        print(f"  {db_name}: {'✓' if is_valid else '✗'} {message}")
    
    # 测试3：单独测试stock_meta
    print("\n=== Stock Meta 数据库测试 ===")
    meta_path = get_stock_meta_path()
    print(f"Meta数据库路径: {meta_path}")
    is_valid, message = check_stock_meta_path()
    print(f"Meta数据库检查: {'✓' if is_valid else '✗'} {message}")
    
    # 测试4：单独测试stock_kbar
    print("\n=== Stock KBar 数据库测试 ===")
    kbar_path = get_stock_kbar_path()
    print(f"KBar数据库路径: {kbar_path}")
    is_valid, message = check_stock_kbar_path()
    print(f"KBar数据库检查: {'✓' if is_valid else '✗'} {message}")
    
    # 测试5：设置新路径
    print("\n=== 路径设置测试 ===")
    original_kbar_path = get_stock_kbar_path()
    test_kbar_path = "D:/test/kbar.db"
    
    if set_stock_kbar_path(test_kbar_path):
        print(f"KBar路径设置成功: {get_stock_kbar_path()}")
        is_valid, message = check_stock_kbar_path()
        print(f"新KBar路径检查: {'✓' if is_valid else '✗'} {message}")
        
        # 恢复原路径
        set_stock_kbar_path(original_kbar_path)
        print(f"恢复原KBar路径: {get_stock_kbar_path()}")
    else:
        print("KBar路径设置失败")