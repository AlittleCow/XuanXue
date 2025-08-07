"""
pytest配置文件和共享fixtures
"""
import pytest
import os
import tempfile
import sqlite3
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_db_path():
    """创建测试用的数据库"""
    # 创建临时数据库文件
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "test_stock_meta.db")
    
    # 创建测试数据库结构
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # 创建stock_meta表
    cursor.execute("""
        CREATE TABLE stock_meta (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            exchange TEXT,
            list_date TEXT,
            年干 TEXT,
            年支 TEXT,
            月干 TEXT,
            月支 TEXT,
            日干 TEXT,
            日支 TEXT
        )
    """)
    
    # 插入测试数据
    test_data = [
        ('000001.SZ', '平安银行', 'SZ', '19910403', None, None, None, None, None, None),
        ('000002.SZ', '万科A', 'SZ', '19910129', None, None, None, None, None, None),
        ('000858.SZ', '五粮液', 'SZ', '19980427', None, None, None, None, None, None),
        ('600000.SH', '浦发银行', 'SH', '19991110', None, None, None, None, None, None),
        ('600036.SH', '招商银行', 'SH', '20020409', None, None, None, None, None, None),
        # 已有干支数据的测试股票
        ('301117.SZ', '佳缘科技', 'SZ', '20211203', '辛', '丑', '己', '亥', '癸', '亥'),
    ]
    
    cursor.executemany("""
        INSERT INTO stock_meta (symbol, name, exchange, list_date, 年干, 年支, 月干, 月支, 日干, 日支)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, test_data)
    
    conn.commit()
    conn.close()
    
    yield test_db
    
    # 清理临时文件
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def setup_xuanxue(test_db_path):
    """设置XuanXue包使用测试数据库"""
    import XuanXue as xx
    
    # 保存原始配置
    original_path = None
    try:
        original_path = xx.get_stock_meta_path()
    except:
        pass
    
    # 设置测试数据库路径
    xx.set_stock_meta_path(test_db_path)
    
    yield xx
    
    # 恢复原始配置
    if original_path:
        xx.set_stock_meta_path(original_path)

@pytest.fixture
def sample_dates():
    """提供测试用的日期数据"""
    return [
        "2023/10/10",
        "2023/10/10 15:30:45",
        "2023-10-10",
        "2023-10-10 15:30:45",
        "20231010",
        "2023/1/1",
        "2023/12/31 23:59:59"
    ]

@pytest.fixture
def sample_stocks():
    """提供测试用的股票代码"""
    return [
        "000001.SZ",
        "000002.SZ", 
        "000858.SZ",
        "600000.SH",
        "600036.SH",
        "301117.SZ"  # 已有干支数据
    ]