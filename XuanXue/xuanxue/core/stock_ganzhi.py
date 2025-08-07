"""
股票干支计算模块
"""
import sqlite3
import os
from datetime import datetime
from .ganzhi_calculator import GanZhiCalculator
from ..config import get_stock_meta_path, check_stock_meta_path

class StockGanZhiCalculator:
    def __init__(self, db_path=None):
        """
        初始化股票干支计算器
        :param db_path: 数据库路径，如果为None则使用配置文件中的路径
        """
        if db_path is None:
            # 使用配置文件中的路径
            self.db_path = get_stock_meta_path()
        else:
            self.db_path = db_path
        
        # 检查数据库路径是否可用
        self._check_database()
    
    def _check_database(self):
        """检查数据库是否可用"""
        is_valid, message = check_stock_meta_path()
        if not is_valid:
            raise Exception(f"数据库路径不可用: {message}")
        
        print(f"✓ 数据库路径检查通过: {self.db_path}")
    
    def get_stock_info(self, symbol):
        """
        获取股票基本信息和干支信息
        :param symbol: 股票代码，如 '000001.SZ'
        :return: 股票信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT symbol, name, exchange, list_date, 年干, 年支, 月干, 月支, 日干, 日支
                FROM stock_meta WHERE symbol = ?
            """, (symbol,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'symbol': result[0],
                    'name': result[1],
                    'exchange': result[2],
                    'list_date': result[3],
                    'year_gan': result[4],
                    'year_zhi': result[5],
                    'month_gan': result[6],
                    'month_zhi': result[7],
                    'day_gan': result[8],
                    'day_zhi': result[9]
                }
            else:
                raise ValueError(f"未找到股票代码 {symbol} 的信息")
                
        except sqlite3.Error as e:
            raise Exception(f"数据库查询错误: {e}")
    
    def _has_ganzhi_data(self, stock_info):
        """
        检查股票是否已有干支数据
        :param stock_info: 股票信息字典
        :return: bool
        """
        return all([
            stock_info['year_gan'], stock_info['year_zhi'],
            stock_info['month_gan'], stock_info['month_zhi'],
            stock_info['day_gan'], stock_info['day_zhi']
        ])
    
    def _calculate_and_save_ganzhi(self, symbol, list_date):
        """
        计算并保存干支到数据库
        :param symbol: 股票代码
        :param list_date: 上市日期
        :return: 干支结果
        """
        # 转换日期格式：20210101 -> 2021/01/01
        if len(list_date) == 8:
            formatted_date = f"{list_date[:4]}/{list_date[4:6]}/{list_date[6:8]}"
        else:
            # 如果已经是其他格式，直接使用
            formatted_date = list_date
        
        # 计算干支
        ganzhi_result = GanZhiCalculator(formatted_date)
        
        # 解析干支
        year_ganzhi = ganzhi_result[0]
        month_ganzhi = ganzhi_result[1] 
        day_ganzhi = ganzhi_result[2]
        
        # 分离天干地支
        year_gan, year_zhi = year_ganzhi[0], year_ganzhi[1]
        month_gan, month_zhi = month_ganzhi[0], month_ganzhi[1]
        day_gan, day_zhi = day_ganzhi[0], day_ganzhi[1]
        
        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE stock_meta 
                SET 年干=?, 年支=?, 月干=?, 月支=?, 日干=?, 日支=?
                WHERE symbol=?
            """, (year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, symbol))
            
            conn.commit()
            conn.close()
            
            print(f"✓ 已计算并保存 {symbol} 的干支信息")
            
            return {
                'year_gan': year_gan,
                'year_zhi': year_zhi,
                'month_gan': month_gan,
                'month_zhi': month_zhi,
                'day_gan': day_gan,
                'day_zhi': day_zhi,
                'year_ganzhi': year_ganzhi,
                'month_ganzhi': month_ganzhi,
                'day_ganzhi': day_ganzhi
            }
            
        except sqlite3.Error as e:
            raise Exception(f"保存干支信息到数据库失败: {e}")
    
    def nBoardDateGanZhi(self, symbol):
        """
        查询股票上市日期的干支
        如果数据库中已有干支记录，直接返回；如果没有，先计算并保存，然后返回
        :param symbol: 股票代码，如 '000001.SZ'
        :return: 上市日期的干支信息
        """
        try:
            # 获取股票基本信息
            stock_info = self.get_stock_info(symbol)
            
            # 检查是否已有干支数据
            if self._has_ganzhi_data(stock_info):
                # 直接从数据库返回
                print(f"✓ 从数据库获取 {symbol} 的干支信息")
                ganzhi_data = {
                    'year_gan': stock_info['year_gan'],
                    'year_zhi': stock_info['year_zhi'],
                    'month_gan': stock_info['month_gan'],
                    'month_zhi': stock_info['month_zhi'],
                    'day_gan': stock_info['day_gan'],
                    'day_zhi': stock_info['day_zhi'],
                    'year_ganzhi': stock_info['year_gan'] + stock_info['year_zhi'],
                    'month_ganzhi': stock_info['month_gan'] + stock_info['month_zhi'],
                    'day_ganzhi': stock_info['day_gan'] + stock_info['day_zhi']
                }
            else:
                # 计算并保存干支
                print(f"⚡ 计算 {symbol} 的干支信息...")
                ganzhi_data = self._calculate_and_save_ganzhi(symbol, stock_info['list_date'])
            
            # 转换日期格式用于显示
            list_date = stock_info['list_date']
            if len(list_date) == 8:
                formatted_date = f"{list_date[:4]}/{list_date[4:6]}/{list_date[6:8]}"
            else:
                formatted_date = list_date
            
            return {
                'symbol': symbol,
                'name': stock_info['name'],
                'exchange': stock_info['exchange'],
                'list_date': formatted_date,
                'ganzhi': [ganzhi_data['year_ganzhi'], ganzhi_data['month_ganzhi'], ganzhi_data['day_ganzhi']],
                'year_ganzhi': ganzhi_data['year_ganzhi'],
                'month_ganzhi': ganzhi_data['month_ganzhi'],
                'day_ganzhi': ganzhi_data['day_ganzhi'],
                'year_gan': ganzhi_data['year_gan'],
                'year_zhi': ganzhi_data['year_zhi'],
                'month_gan': ganzhi_data['month_gan'],
                'month_zhi': ganzhi_data['month_zhi'],
                'day_gan': ganzhi_data['day_gan'],
                'day_zhi': ganzhi_data['day_zhi']
            }
            
        except Exception as e:
            raise Exception(f"查询股票 {symbol} 上市日期干支失败: {e}")
    
    def batch_update_ganzhi(self, limit=None):
        """
        批量更新所有股票的干支信息
        :param limit: 限制更新数量，None表示更新所有
        :return: 更新统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取需要更新的股票（年干为空的）
            if limit:
                cursor.execute("SELECT symbol FROM stock_meta WHERE 年干 IS NULL LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT symbol FROM stock_meta WHERE 年干 IS NULL")
            
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            success_count = 0
            error_count = 0
            errors = []
            
            print(f"开始批量更新 {len(symbols)} 只股票的干支信息...")
            
            for symbol in symbols:
                try:
                    self.nBoardDateGanZhi(symbol)  # 使用新的方法，会自动保存
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"{symbol}: {e}")
                    print(f"✗ 更新 {symbol} 失败: {e}")
            
            return {
                'total': len(symbols),
                'success': success_count,
                'error': error_count,
                'errors': errors
            }
            
        except Exception as e:
            raise Exception(f"批量更新失败: {e}")

# 便捷函数
def nBoardDateGanZhi(symbol, db_path=None):
    """
    便捷函数：查询股票上市日期的干支
    如果数据库中已有干支记录，直接返回；如果没有，先计算并保存，然后返回
    :param symbol: 股票代码，如 '000001.SZ'
    :param db_path: 数据库路径，可选（如果不提供则使用配置文件中的路径）
    :return: 干支信息
    """
    try:
        calculator = StockGanZhiCalculator(db_path)
        return calculator.nBoardDateGanZhi(symbol)
    except Exception as e:
        print(f"查询股票 {symbol} 干支失败: {e}")
        raise

def DateTimeGanZhi(datetime_str):
    """
    便捷函数：计算指定日期时间的干支
    :param datetime_str: 日期时间字符串
    :return: 干支列表
    """
    try:
        return GanZhiCalculator(datetime_str)
    except Exception as e:
        print(f"计算日期 {datetime_str} 干支失败: {e}")
        raise

def check_database_status():
    """
    检查数据库状态的便捷函数
    :return: (是否可用, 状态信息)
    """
    return check_stock_meta_path()

def get_current_database_path():
    """
    获取当前配置的数据库路径
    :return: 数据库路径
    """
    return get_stock_meta_path()

# 测试代码
if __name__ == "__main__":
    print("=== 股票干支计算测试（智能缓存版本）===")
    
    # 检查数据库状态
    print("\n1. 检查数据库状态:")
    is_valid, message = check_database_status()
    print(f"   状态: {'✓ 可用' if is_valid else '✗ 不可用'}")
    print(f"   详情: {message}")
    print(f"   路径: {get_current_database_path()}")
    
    if not is_valid:
        print("\n数据库不可用，测试终止。")
        print("请使用以下方法配置正确的数据库路径:")
        print("  from XuanXue.xuanxue.config import set_stock_meta_path")
        print("  set_stock_meta_path('/path/to/your/stock_meta.db')")
        exit(1)
    
    print("\n2. 初始化计算器:")
    try:
        calculator = StockGanZhiCalculator()
        print("   ✓ 计算器初始化成功")
    except Exception as e:
        print(f"   ✗ 计算器初始化失败: {e}")
        exit(1)
    
    # 测试单个股票（第一次调用 - 可能需要计算）
    print("\n3. 测试单个股票查询（第一次）:")
    try:
        result = calculator.nBoardDateGanZhi('000001.SZ')
        print(f"   股票代码: {result['symbol']}")
        print(f"   股票名称: {result['name']}")
        print(f"   交易所: {result['exchange']}")
        print(f"   上市日期: {result['list_date']}")
        print(f"   年干支: {result['year_ganzhi']} ({result['year_gan']}{result['year_zhi']})")
        print(f"   月干支: {result['month_ganzhi']} ({result['month_gan']}{result['month_zhi']})")
        print(f"   日干支: {result['day_ganzhi']} ({result['day_gan']}{result['day_zhi']})")
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
    
    # 测试同一股票（第二次调用 - 应该从数据库直接读取）
    print("\n4. 测试同一股票查询（第二次，应该从缓存读取）:")
    try:
        result2 = calculator.nBoardDateGanZhi('000001.SZ')
        print(f"   结果一致性检查: {'✓ 一致' if result['ganzhi'] == result2['ganzhi'] else '✗ 不一致'}")
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
    
    # 测试便捷函数
    print("\n5. 测试便捷函数:")
    try:
        result3 = nBoardDateGanZhi('000002.SZ')
        print(f"   000002.SZ: {result3['name']} - {result3['ganzhi']}")
    except Exception as e:
        print(f"   ✗ 便捷函数测试失败: {e}")
    
    # 测试日期时间干支计算
    print("\n6. 测试日期时间干支计算:")
    try:
        date_result = DateTimeGanZhi('2023/10/10 15:30:45')
        print(f"   2023/10/10 15:30:45 的干支: {date_result}")
    except Exception as e:
        print(f"   ✗ 日期时间干支计算失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n功能说明:")
    print("  ✓ 首次查询股票时会计算干支并保存到数据库")
    print("  ✓ 再次查询同一股票时直接从数据库读取，提高效率")
    print("  ✓ 自动使用配置文件中的数据库路径")
    print("  ✓ 启动时自动检查数据库可用性")