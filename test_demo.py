#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XuanXue包功能演示测试
用于展示四个主要功能的使用方法和结果
"""

import XuanXue as xx
import sys
import os

def print_separator(title):
    """打印分隔线和标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_datetime_ganzhi():
    """测试日期时间干支计算功能"""
    print_separator("1. DateTimeGanZhi - 日期时间干支计算")
    
    test_dates = [
        "2023-10-10 15:30:45",
        "2024-01-01 00:00:00", 
        "2024-12-31 23:59:59",
        "1949-10-01 15:00:00"
    ]
    
    for date_str in test_dates:
        try:
            result = xx.DateTimeGanZhi(date_str)
            print(f"📅 {date_str} => {result}")
        except Exception as e:
            print(f"❌ {date_str} => 错误: {e}")

def test_onboard_date_ganzhi():
    """测试股票上市日期干支查询功能"""
    print_separator("2. OnBoardDateGanZhi - 股票上市日期干支查询")
    
    # 配置股票元数据数据库路径
    stock_meta_path = "d:\\股票基本信息数据库\\XuanXue包开发\\stock_meta.db"
    if os.path.exists(stock_meta_path):
        xx.set_stock_meta_path(stock_meta_path)
        print(f"✅ 数据库路径已配置: {stock_meta_path}")
    else:
        print(f"⚠️  数据库文件不存在: {stock_meta_path}")
    
    test_stocks = [
        "000001.SZ",  # 平安银行
        "600000.SH",  # 浦发银行
        "000002.SZ",  # 万科A
        "INVALID.CODE"  # 无效代码
    ]
    
    for stock_code in test_stocks:
        try:
            result = xx.OnBoardDateGanZhi(stock_code)
            print(f"📈 {stock_code} => {result}")
        except Exception as e:
            print(f"❌ {stock_code} => 错误: {e}")

def test_kbar_series_ganzhi_usedb_false():
    """测试K线序列干支计算功能 (useDB=False)"""
    print_separator("3. KbarSeriesGanZhi - K线序列干支计算 (实时计算模式)")
    
    # 示例K线数据
    kbar_dict = {
        "symbol": "TEST001",
        "exchange": "SZ",
        "period": "1day",
        "kbar": [
            ["2023-10-10 09:30:00", 20.0, 20.5, 19.8, 20.2, 1000000, 20100000],
            ["2023-10-11 09:30:00", 20.2, 20.8, 20.0, 20.6, 1200000, 24720000],
            ["2023-10-12 09:30:00", 20.6, 21.0, 20.4, 20.8, 1100000, 22880000]
        ]
    }
    
    try:
        result = xx.KbarSeriesGanZhi(
            start_datetime="2023-10-10 00:00:00",
            end_datetime="2023-10-13 00:00:00",
            kbar_series=kbar_dict,
            useDB=False
        )
        print(f"📊 实时计算结果:")
        print(f"   股票代码: {result.get_key().get_symbol()}")
        print(f"   交易所: {result.get_key().get_exchange()}")
        print(f"   周期: {result.get_key().get_period()}")
        print(f"   干支数据条数: {len(result.get_ganzhi_list())}")
        
        # 显示前3条干支数据
        ganzhi_list = result.get_ganzhi_list()
        for i, ganzhi in enumerate(ganzhi_list[:3]):
            print(f"   第{i+1}条: {ganzhi}")
            
    except Exception as e:
        print(f"❌ K线序列干支计算失败: {e}")

def test_kbar_series_ganzhi_usedb_true():
    """测试K线序列干支查询功能 (useDB=True)"""
    print_separator("4. KbarSeriesGanZhi - K线序列干支查询 (数据库模式)")
    
    # 配置K线数据库路径
    kbar_db_path = "d:\\股票基本信息数据库\\XuanXue包开发\\stock_kbar.db"
    if os.path.exists(kbar_db_path):
        xx.set_stock_kbar_path(kbar_db_path)
        print(f"✅ K线数据库路径已配置: {kbar_db_path}")
        
        try:
            # 测试从数据库查询
            result = xx.KbarSeriesGanZhi(
                start_datetime="2015-01-01 00:00:00",
                end_datetime="2023-01-31 23:59:59",
                kbar_series=None,  # 查询所有K线序列
                useDB=True
            )
            
            print(f"📊 数据库查询结果:")
            kbar_list = result.get_kbar_series_ganzhi_list()
            print(f"   查询到 {len(kbar_list)} 个K线序列")
            
            # 显示前3个序列的信息
            for i, kbar_series in enumerate(kbar_list[:3]):
                key = kbar_series.get_key()
                print(f"   序列{i+1}: {key.get_symbol()}.{key.get_exchange()} ({key.get_period()}) - {len(kbar_series.get_ganzhi_list())}条数据")
                
        except Exception as e:
            print(f"❌ 数据库查询失败: {e}")
    else:
        print(f"⚠️  K线数据库文件不存在: {kbar_db_path}")
        print("   可以使用 getdata.py 生成测试数据")

def main():
    """主函数"""
    print("🚀 XuanXue包功能演示测试开始")
    print(f"📦 XuanXue版本: {getattr(xx, '__version__', '未知')}")
    
    # 执行所有测试
    test_datetime_ganzhi()
    test_onboard_date_ganzhi()
    test_kbar_series_ganzhi_usedb_false()
    test_kbar_series_ganzhi_usedb_true()
    
    print_separator("测试完成")
    print("✅ 所有功能演示完成！")
    print("📸 现在可以截图保存测试结果")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)