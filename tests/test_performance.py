"""
性能测试
"""
import pytest
import time
import XuanXue as xx

class TestPerformance:
    """性能测试类"""
    
    def test_date_calculation_performance(self):
        """测试日期计算性能"""
        dates = [f"2023/{i:02d}/15" for i in range(1, 13)]  # 12个月的日期
        
        start_time = time.time()
        
        for date in dates:
            result = xx.DateTimeGanZhi(date)
            assert len(result) >= 3
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 12个日期计算应该在1秒内完成
        assert elapsed < 1.0, f"日期计算性能过慢: {elapsed:.2f}秒"
    
    def test_stock_query_caching(self, setup_xuanxue):
        """测试股票查询缓存性能"""
        xx = setup_xuanxue
        
        symbol = '000001.SZ'
        
        # 第一次查询（可能需要计算）
        start_time = time.time()
        result1 = xx.OnBoardDateGanZhi(symbol)
        first_query_time = time.time() - start_time
        
        # 第二次查询（应该从缓存读取）
        start_time = time.time()
        result2 = xx.OnBoardDateGanZhi(symbol)
        second_query_time = time.time() - start_time
        
        # 结果应该一致
        assert result1['ganzhi'] == result2['ganzhi']
        
        # 第二次查询应该更快（或至少不会慢很多）
        assert second_query_time <= first_query_time * 2, \
            f"缓存查询性能异常: 第一次{first_query_time:.3f}s, 第二次{second_query_time:.3f}s"
    
    @pytest.mark.slow
    def test_batch_processing(self, setup_xuanxue, sample_stocks):
        """测试批量处理性能（标记为慢速测试）"""
        xx = setup_xuanxue
        
        start_time = time.time()
        
        results = []
        for symbol in sample_stocks:
            try:
                result = xx.OnBoardDateGanZhi(symbol)
                results.append(result)
            except Exception:
                pass  # 忽略错误，专注性能测试
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 批量查询应该在合理时间内完成
        assert elapsed < 10.0, f"批量查询性能过慢: {elapsed:.2f}秒"
        assert len(results) > 0, "没有成功查询任何股票"