"""
测试股票干支查询功能
"""
import pytest
import sqlite3
import XuanXue as xx

class TestStockGanZhi:
    """股票干支测试类"""
    
    def test_onboard_date_ganzhi_existing_data(self, setup_xuanxue):
        """测试查询已有干支数据的股票"""
        xx = setup_xuanxue
        
        # 查询已有干支数据的股票
        result = xx.OnBoardDateGanZhi('301117.SZ')
        
        assert result['symbol'] == '301117.SZ'
        assert result['name'] == '佳缘科技'
        assert result['exchange'] == 'SZ'
        assert result['list_date'] == '2021/12/03'
        
        # 检查干支数据
        assert result['year_ganzhi'] == '辛丑'
        assert result['month_ganzhi'] == '己亥'
        assert result['day_ganzhi'] == '癸亥'
        
        assert result['ganzhi'] == ['辛丑', '己亥', '癸亥']
    
    def test_onboard_date_ganzhi_calculate_new(self, setup_xuanxue):
        """测试计算新股票的干支数据"""
        xx = setup_xuanxue
        
        # 查询没有干支数据的股票
        result = xx.OnBoardDateGanZhi('000001.SZ')
        
        assert result['symbol'] == '000001.SZ'
        assert result['name'] == '平安银行'
        assert result['exchange'] == 'SZ'
        assert result['list_date'] == '1991/04/03'
        
        # 检查干支数据已计算
        assert result['year_ganzhi'] is not None
        assert result['month_ganzhi'] is not None
        assert result['day_ganzhi'] is not None
        assert len(result['ganzhi']) == 3
        
        # 验证数据已保存到数据库
        db_path = xx.get_stock_meta_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 年干, 年支, 月干, 月支, 日干, 日支 FROM stock_meta WHERE symbol = ?", ('000001.SZ',))
        db_result = cursor.fetchone()
        conn.close()
        
        assert db_result is not None
        assert all(x is not None for x in db_result)  # 所有干支字段都应该有值
    
    def test_onboard_date_ganzhi_multiple_calls(self, setup_xuanxue):
        """测试多次调用同一股票的一致性"""
        xx = setup_xuanxue
        
        # 第一次调用
        result1 = xx.OnBoardDateGanZhi('000002.SZ')
        
        # 第二次调用
        result2 = xx.OnBoardDateGanZhi('000002.SZ')
        
        # 结果应该一致
        assert result1['ganzhi'] == result2['ganzhi']
        assert result1['year_ganzhi'] == result2['year_ganzhi']
        assert result1['month_ganzhi'] == result2['month_ganzhi']
        assert result1['day_ganzhi'] == result2['day_ganzhi']
    
    def test_onboard_date_ganzhi_invalid_symbol(self, setup_xuanxue):
        """测试无效股票代码"""
        xx = setup_xuanxue
        
        with pytest.raises(Exception) as exc_info:
            xx.OnBoardDateGanZhi('INVALID.XX')
        
        assert "未找到" in str(exc_info.value) or "不存在" in str(exc_info.value)
    
    def test_stock_ganzhi_calculator_class(self, setup_xuanxue, test_db_path):
        """测试StockGanZhiCalculator类"""
        from XuanXue.xuanxue.core.stock_ganzhi import StockGanZhiCalculator
        calculator = StockGanZhiCalculator(test_db_path)
        
        # 测试获取股票信息
        stock_info = calculator.get_stock_info('000001.SZ')
        assert stock_info['symbol'] == '000001.SZ'
        assert stock_info['name'] == '平安银行'
        
        # 测试干支计算
        result = calculator.OnBoardDateGanZhi('000858.SZ')
        assert result['symbol'] == '000858.SZ'
        assert result['name'] == '五粮液'
        assert len(result['ganzhi']) == 3
    
    def test_batch_update_ganzhi(self, setup_xuanxue):
        """测试批量更新干支"""
        xx = setup_xuanxue
        
        from XuanXue.xuanxue.core.stock_ganzhi import StockGanZhiCalculator
        calculator = StockGanZhiCalculator()
        
        # 批量更新（限制数量）
        result = calculator.batch_update_ganzhi(limit=2)
        
        assert 'total' in result
        assert 'success' in result
        assert 'error' in result
        assert result['total'] <= 2
        assert result['success'] + result['error'] == result['total']