"""
测试配置管理功能
"""
import pytest
import os
import tempfile
import XuanXue as xx

class TestConfigManager:
    """配置管理测试类"""
    
    def test_set_and_get_path(self, setup_xuanxue):
        """测试设置和获取数据库路径"""
        xx = setup_xuanxue
        
        # 获取当前路径
        current_path = xx.get_stock_meta_path()
        assert current_path is not None
        assert os.path.isabs(current_path)  # 应该是绝对路径
    
    def test_check_valid_path(self, setup_xuanxue):
        """测试检查有效的数据库路径"""
        xx = setup_xuanxue
        
        is_valid, message = xx.check_stock_meta_path()
        assert is_valid == True
        assert "正常" in message or "可用" in message
    
    def test_check_invalid_path(self):
        """测试检查无效的数据库路径"""
        import XuanXue as xx
        
        # 设置不存在的路径
        invalid_path = "/nonexistent/path/stock.db"
        xx.set_stock_meta_path(invalid_path)
        
        is_valid, message = xx.check_stock_meta_path()
        assert is_valid == False
        assert "不存在" in message or "失败" in message
    
    def test_relative_path_conversion(self, setup_xuanxue):
        """测试相对路径转换为绝对路径"""
        xx = setup_xuanxue
        
        # 设置相对路径
        xx.set_stock_meta_path("test.db")
        path = xx.get_stock_meta_path()
        
        # 应该转换为绝对路径
        assert os.path.isabs(path)
        assert path.endswith("test.db")