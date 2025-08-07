"""
集成测试
"""
import pytest
import XuanXue as xx

class TestIntegration:
    """集成测试类"""
    
    def test_full_workflow(self, setup_xuanxue, sample_stocks):
        """测试完整工作流程"""
        xx = setup_xuanxue
        
        # 1. 检查配置
        is_valid, message = xx.check_stock_meta_path()
        assert is_valid, f"数据库配置无效: {message}"
        
        # 2. 测试日期干支计算
        date_result = xx.DateTimeGanZhi("2023/10/10 15:30:45")
        assert len(date_result) == 6
        assert all(ganzhi != "无值" for ganzhi in date_result)
        
        # 3. 测试股票干支查询
        for symbol in sample_stocks[:3]:  # 测试前3只股票
            try:
                stock_result = xx.OnBoardDateGanZhi(symbol)
                assert stock_result['symbol'] == symbol
                assert len(stock_result['ganzhi']) == 3
                assert all(len(gz) == 2 for gz in stock_result['ganzhi'])
            except Exception as e:
                pytest.fail(f"查询股票 {symbol} 失败: {e}")
    
    def test_package_imports(self):
        """测试包导入"""
        # 测试主要导入
        import XuanXue as xx
        
        # 检查主要函数存在
        assert hasattr(xx, 'OnBoardDateGanZhi')
        assert hasattr(xx, 'DateTimeGanZhi')
        assert hasattr(xx, 'get_stock_meta_path')
        assert hasattr(xx, 'set_stock_meta_path')
        assert hasattr(xx, 'check_stock_meta_path')
        
        # 检查版本信息
        assert hasattr(xx, '__version__')
        assert hasattr(xx, '__author__')
    
    def test_alternative_imports(self):
        """测试其他导入方式"""
        # 测试具体函数导入
        from XuanXue import OnBoardDateGanZhi, DateTimeGanZhi
        
        assert callable(OnBoardDateGanZhi)
        assert callable(DateTimeGanZhi)
    
    def test_error_handling(self, setup_xuanxue):
        """测试错误处理"""
        xx = setup_xuanxue
        
        # 测试无效日期
        with pytest.raises(Exception):
            xx.DateTimeGanZhi("invalid_date")
        
        # 测试无效股票代码
        with pytest.raises(Exception):
            xx.OnBoardDateGanZhi("INVALID.CODE")
        
        # 测试无效数据库路径
        xx.set_stock_meta_path("/nonexistent/path.db")
        is_valid, message = xx.check_stock_meta_path()
        assert not is_valid