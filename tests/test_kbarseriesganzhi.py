"""
测试KbarSeriesGanZhi功能
"""
import pytest
import datetime
import sqlite3
import tempfile
import os
from unittest.mock import patch

import XuanXue as xx
from XuanXue.xuanxue.utils.kbar_type import (
    Kbar, 
    KbarSeriesKey, 
    KbarSeries, 
    KbarSeriesGanZhi as KbarSeriesGanZhiType,
    KbarSeriesGanZhiList
)
from XuanXue.xuanxue.core.kbarseriesganzhi import _convert_dict_to_kbar_series

class TestKbarSeriesGanZhi:
    """KbarSeriesGanZhi功能测试类"""
    
    @pytest.fixture
    def sample_kbar_dict(self):
        """示例kbar字典数据"""
        return {
            "symbol": "TEST001",
            "exchange": "SZ",
            "period": "1h",
            "kbar": [
                ["2023-08-25 09:30:00", 20.0, 20.5, 19.8, 20.2, 500000, 10100000],
                ["2023-08-25 10:30:00", 20.2, 20.8, 20.0, 20.6, 600000, 12360000],
                ["2023-08-25 11:30:00", 20.6, 21.0, 20.4, 20.8, 700000, 14560000]
            ]
        }
    
    @pytest.fixture
    def sample_kbar_series(self):
        """示例KbarSeries对象"""
        key = KbarSeriesKey(symbol='TEST002', exchange='SH', period='1d')
        kbar_list = [
            Kbar(
                ts=datetime.datetime(2023, 8, 25, 9, 30),
                open=30.0, high=30.5, low=29.8, close=30.2,
                volume=400000, amount=12080000
            ),
            Kbar(
                ts=datetime.datetime(2023, 8, 25, 10, 30),
                open=30.2, high=30.8, low=30.0, close=30.6,
                volume=500000, amount=15300000
            )
        ]
        return KbarSeries(key, kbar_list)
    
    def test_convert_dict_to_kbar_series(self, sample_kbar_dict):
        """测试字典转KbarSeries功能"""
        # 测试正常转换
        kbar_series = _convert_dict_to_kbar_series(sample_kbar_dict)
        
        assert isinstance(kbar_series, KbarSeries)
        assert kbar_series.get_key().get_symbol() == "TEST001"
        assert kbar_series.get_key().get_exchange() == "SZ"
        assert kbar_series.get_key().get_period() == "1h"
        assert len(kbar_series.get_kbar_list()) == 3
        
        # 验证第一个kbar数据
        first_kbar = kbar_series.get_kbar_list()[0]
        assert isinstance(first_kbar.ts, datetime.datetime)
        assert first_kbar.open == 20.0
        assert first_kbar.high == 20.5
        assert first_kbar.low == 19.8
        assert first_kbar.close == 20.2
    
    def test_convert_dict_invalid_input(self):
        """测试字典转换的错误处理"""
        # 测试缺少kbar键
        invalid_dict1 = {"symbol": "TEST", "exchange": "SZ", "period": "1h"}
        with pytest.raises(ValueError, match="输入必须是包含kbar数据的字典"):
            _convert_dict_to_kbar_series(invalid_dict1)
        
        # 测试缺少必要键
        invalid_dict2 = {"symbol": "TEST", "kbar": []}
        with pytest.raises(ValueError, match="字典必须包含"):
            _convert_dict_to_kbar_series(invalid_dict2)
        
        # 测试kbar数据格式错误
        invalid_dict3 = {
            "symbol": "TEST", "exchange": "SZ", "period": "1h",
            "kbar": [["2023-08-25 09:30:00", 20.0]]  # 缺少数据
        }
        with pytest.raises(ValueError, match="每个kbar数据必须包含7个元素"):
            _convert_dict_to_kbar_series(invalid_dict3)
    
    @patch('XuanXue.xuanxue.core.kbarseriesganzhi.check_stock_kbar_path')
    @patch('XuanXue.xuanxue.core.kbarseriesganzhi.get_stock_kbar_path')
    def test_kbarseriesganzhi_usedb_false_dict(self, mock_get_path, mock_check_path, sample_kbar_dict):
        """测试useDB=False时使用字典输入"""
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            tmp_db_path = tmp_file.name
        
        try:
            # 设置mock
            mock_get_path.return_value = tmp_db_path
            mock_check_path.return_value = True
            
            # 创建测试数据库表
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kbar_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    period TEXT NOT NULL,
                    ts TIMESTAMP NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    amount REAL NOT NULL,
                    year_gan TEXT,
                    year_zhi TEXT,
                    month_gan TEXT,
                    month_zhi TEXT,
                    day_gan TEXT,
                    day_zhi TEXT,
                    hour_gan TEXT,
                    hour_zhi TEXT
                )
            ''')
            conn.commit()
            conn.close()
            
            # 测试KbarSeriesGanZhi函数
            result = xx.KbarSeriesGanZhi(
                start_datetime='2023-08-25 09:00:00',
                end_datetime='2023-08-25 12:00:00',
                kbar_series=sample_kbar_dict,
                useDB=False
            )
            
            # 验证结果
            assert isinstance(result, KbarSeriesGanZhiType)
            assert result.get_key().get_symbol() == "TEST001"
            assert len(result.get_ganzhi_list()) > 0
            
            # 验证干支格式
            for ganzhi in result.get_ganzhi_list():
                assert isinstance(ganzhi, str)
                assert "-" in ganzhi  # 干支格式应该包含分隔符
        
        finally:
            # 清理临时文件
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @patch('XuanXue.xuanxue.core.kbarseriesganzhi.check_stock_kbar_path')
    @patch('XuanXue.xuanxue.core.kbarseriesganzhi.get_stock_kbar_path')
    def test_kbarseriesganzhi_usedb_false_kbarseries(self, mock_get_path, mock_check_path, sample_kbar_series):
        """测试useDB=False时使用KbarSeries对象输入"""
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            tmp_db_path = tmp_file.name
        
        try:
            # 设置mock
            mock_get_path.return_value = tmp_db_path
            mock_check_path.return_value = True
            
            # 创建测试数据库表
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kbar_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    period TEXT NOT NULL,
                    ts TIMESTAMP NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    amount REAL NOT NULL,
                    year_gan TEXT,
                    year_zhi TEXT,
                    month_gan TEXT,
                    month_zhi TEXT,
                    day_gan TEXT,
                    day_zhi TEXT,
                    hour_gan TEXT,
                    hour_zhi TEXT
                )
            ''')
            conn.commit()
            conn.close()
            
            # 测试KbarSeriesGanZhi函数
            result = xx.KbarSeriesGanZhi(
                start_datetime='2023-08-25 09:00:00',
                end_datetime='2023-08-25 11:00:00',
                kbar_series=sample_kbar_series,
                useDB=False
            )
            
            # 验证结果
            assert isinstance(result, KbarSeriesGanZhiType)
            assert result.get_key().get_symbol() == "TEST002"
            assert len(result.get_ganzhi_list()) > 0
        
        finally:
            # 清理临时文件
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    def test_kbarseriesganzhi_usedb_true_list_format(self):
        """测试useDB=True时使用列表格式输入"""
        with patch('XuanXue.xuanxue.core.kbarseriesganzhi.check_stock_kbar_path') as mock_check:
            mock_check.return_value = False
            
            # 测试数据库不存在的情况
            with pytest.raises(FileNotFoundError, match="kbar数据库文件不存在"):
                xx.KbarSeriesGanZhi(
                    start_datetime='2023-08-25 09:00:00',
                    end_datetime='2023-08-25 12:00:00',
                    kbar_series=["TEST001", "SZ", "1h"],
                    useDB=True
                )
    
    def test_kbarseriesganzhi_usedb_true_dict_format(self):
        """测试useDB=True时使用字典格式输入（不含kbar数据）"""
        with patch('XuanXue.xuanxue.core.kbarseriesganzhi.check_stock_kbar_path') as mock_check:
            mock_check.return_value = False
            
            # 测试数据库不存在的情况
            with pytest.raises(FileNotFoundError, match="kbar数据库文件不存在"):
                xx.KbarSeriesGanZhi(
                    start_datetime='2023-08-25 09:00:00',
                    end_datetime='2023-08-25 12:00:00',
                    kbar_series={"symbol": "TEST001", "exchange": "SZ", "period": "1h"},
                    useDB=True
                )
    
    def test_kbarseriesganzhi_none_input(self):
        """测试kbar_series=None的情况"""
        with patch('XuanXue.xuanxue.core.kbarseriesganzhi.check_stock_kbar_path') as mock_check:
            mock_check.return_value = False
            
            # 测试数据库不存在的情况
            with pytest.raises(FileNotFoundError, match="kbar数据库文件不存在"):
                xx.KbarSeriesGanZhi(
                    start_datetime='2023-08-25 09:00:00',
                    end_datetime='2023-08-25 12:00:00',
                    kbar_series=None,
                    useDB=True
                )
    
    def test_invalid_time_format(self, sample_kbar_dict):
        """测试无效时间格式处理"""
        # 修改字典中的时间格式为无效格式
        invalid_dict = sample_kbar_dict.copy()
        invalid_dict["kbar"] = [
            ["invalid_time", 20.0, 20.5, 19.8, 20.2, 500000, 10100000]
        ]
        
        # 测试应该抛出异常
        with pytest.raises(Exception):
            _convert_dict_to_kbar_series(invalid_dict)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空kbar数据
        empty_dict = {
            "symbol": "TEST",
            "exchange": "SZ", 
            "period": "1h",
            "kbar": []
        }
        
        kbar_series = _convert_dict_to_kbar_series(empty_dict)
        assert len(kbar_series.get_kbar_list()) == 0
        
        # 测试单个kbar数据
        single_dict = {
            "symbol": "TEST",
            "exchange": "SZ",
            "period": "1h", 
            "kbar": [
                ["2023-08-25 09:30:00", 20.0, 20.5, 19.8, 20.2, 500000, 10100000]
            ]
        }
        
        kbar_series = _convert_dict_to_kbar_series(single_dict)
        assert len(kbar_series.get_kbar_list()) == 1