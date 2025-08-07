"""
测试干支计算功能
"""
import pytest
import XuanXue as xx

class TestGanZhiCalculator:
    """干支计算测试类"""
    
    def test_datetime_ganzhi_basic(self, sample_dates):
        """测试基本日期时间干支计算"""
        # 定义天干地支常量用于验证
        gan = "甲乙丙丁戊己庚辛壬癸"
        zhi = "子丑寅卯辰巳午未申酉戌亥"
        
        for date_str in sample_dates:
            try:
                result = xx.DateTimeGanZhi(date_str)
                assert isinstance(result, list)
                assert len(result) >= 3  # 至少包含年月日
                
                # 检查干支格式
                for ganzhi in result[:3]:  # 年月日
                    if ganzhi != "无值":
                        assert len(ganzhi) == 2  # 干支应该是两个字符
                        assert ganzhi[0] in gan  # 第一个字符应该是天干
                        assert ganzhi[1] in zhi  # 第二个字符应该是地支
                        
            except Exception as e:
                pytest.fail(f"计算日期 {date_str} 干支失败: {e}")
    
    def test_specific_date_ganzhi(self):
        """测试特定日期的干支计算 - 验证一致性而非硬编码结果"""
        test_dates = ["2023/10/10", "2023/1/1", "2024/12/31"]
        
        for date_str in test_dates:
            # 多次计算同一日期，验证结果一致性
            result1 = xx.DateTimeGanZhi(date_str)
            result2 = xx.DateTimeGanZhi(date_str)
            assert result1 == result2, f"日期 {date_str} 多次计算结果不一致"
            
            # 验证结果格式
            assert len(result1) >= 3
            for ganzhi in result1[:3]:  # 年月日
                if ganzhi != "无值":
                    assert len(ganzhi) == 2
                    # 验证是有效的干支组合
                    gan = "甲乙丙丁戊己庚辛壬癸"
                    zhi = "子丑寅卯辰巳午未申酉戌亥"
                    assert ganzhi[0] in gan
                    assert ganzhi[1] in zhi
    
    def test_time_components(self):
        """测试时分秒干支计算"""
        # 包含时分秒的日期
        result = xx.DateTimeGanZhi("2023/10/10 15:30:45")
        assert len(result) == 6  # 年月日时分秒
        
        # 检查时分秒不为"无值"
        assert result[3] != "无值"  # 时
        assert result[4] != "无值"  # 分
        assert result[5] != "无值"  # 秒
    
    def test_missing_time_components(self):
        """测试缺少时分秒的情况"""
        result = xx.DateTimeGanZhi("2023/10/10")
        assert len(result) == 6
        
        # 时分秒应该为"无值"
        assert result[3] == "无值"  # 时
        assert result[4] == "无值"  # 分  
        assert result[5] == "无值"  # 秒
    
    def test_invalid_date_format(self):
        """测试无效日期格式"""
        invalid_dates = [
            "invalid_date",
            "2023/13/01",  # 无效月份
            "2023/02/30",  # 无效日期
            "",
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises(Exception):
                xx.DateTimeGanZhi(invalid_date)
        
        # 单独测试None
        with pytest.raises(Exception):
            xx.DateTimeGanZhi(None)