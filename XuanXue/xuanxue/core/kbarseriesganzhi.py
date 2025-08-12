"""
K线图的干支序列,实现函数：

KbarSeriesGanZhi（start-datetime , end-datetime, K线序列, useDB=True）
对于特定的k线序列，计算其干支序列，返回{k线序列的键：[k线序列的干支序列]}，函数中的“K线序列”为k线序列的键
需要选中在start-datetime和end-datetime之间的k线序列

KbarSeriesGanZhi( start-datetime, end-datetime, NULL, useDB=True) 
对于数据库中的k线序列，计算其干支序列，返回{k线序列的键：[k线序列的干支序列],k线序列的键：[k线序列的干支序列],...}
函数中的“K线序列”为k线序列的键
需要选中在start-datetime和end-datetime之间的k线序列


KbarSeriesGanZhi( start-datetime, end-datetime, K线序列, useDB=False)
对于特定的k线序列，计算其干支序列，返回{k线序列的键：[k线序列的干支序列]}，函数中的“K线序列”{为k线序列的键,k线序列的值的列表}
需要选中在start-datetime和end-datetime之间的k线序列


k线序列的键为：{symbol:股票代码,exchange:交易所,period:周期}
"""

import datetime
import sqlite3
from ..utils import (
    Kbar,
    KbarSeriesKey,
    KbarSeries,
    KbarSeriesGanZhi as KbarSeriesGanZhiType, #导入别名，防止和函数重名
    KbarSeriesGanZhiList,
)
from ..config import get_stock_kbar_path,check_stock_kbar_path
from .ganzhi_calculator import parse_datetime_string,GanZhiCalculator


def isindatetime(ts, start_datetime, end_datetime):
    """
    判断datetime是否在start_datetime和end_datetime之间
    
    Args:
        ts: 时间戳，可以是字符串（ISO格式）或 datetime.datetime 对象
        start_datetime: 开始时间字符串，支持多种格式（如：'2023/08/25 10:00:00'）
        end_datetime: 结束时间字符串，支持多种格式（如：'2023/08/25 12:00:00'）
    
    Returns:
        bool: 如果ts在时间范围内返回True，否则返回False
    """
    try:
        # 处理ts参数 - 支持字符串和datetime对象
        if isinstance(ts, datetime.datetime):
            ts_dt = ts
        elif isinstance(ts, str):
            # 解析ts时间戳（ISO格式）
            if '.' in ts:
                # 有微秒的情况：2023-08-25T11:15:30.123456
                ts_dt = datetime.datetime.fromisoformat(ts)
            else:
                # 没有微秒的情况：2023-08-25T11:15:30
                ts_dt = datetime.datetime.fromisoformat(ts)
        else:
            print(f"不支持的时间类型: {type(ts)}")
            return False
        
        # 解析开始时间
        start_year, start_month, start_day, start_hour, start_minute, start_second = parse_datetime_string(start_datetime)
        start_dt = datetime.datetime(
            start_year, start_month, start_day,
            start_hour if start_hour >= 0 else 0,
            start_minute if start_minute >= 0 else 0,
            start_second if start_second >= 0 else 0
        )
        
        # 解析结束时间
        end_year, end_month, end_day, end_hour, end_minute, end_second = parse_datetime_string(end_datetime)
        end_dt = datetime.datetime(
            end_year, end_month, end_day,
            end_hour if end_hour >= 0 else 23,  # 如果没有指定时间，结束时间默认为当天23:59:59
            end_minute if end_minute >= 0 else 59,
            end_second if end_second >= 0 else 59
        )
        
        # 判断ts是否在时间范围内（包含边界）
        return start_dt <= ts_dt <= end_dt
        
    except Exception as e:
        # 如果解析失败，打印错误信息并返回False
        print(f"时间解析错误: ts='{ts}', start='{start_datetime}', end='{end_datetime}', error={e}")
        return False


def kbarseriesganzhi_none(db_path, start_datetime, end_datetime):
    """
    当kbar_series为None且useDB=True时，从数据库中获取所有K线数据并计算干支序列
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 修复：先查询所有数据，然后处理缺失的干支
        query = """
        SELECT id, symbol, exchange, period, ts, open, high, low, close, volume, amount,
               year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi
        FROM kbar_data 
        ORDER BY symbol, exchange, period, ts
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("数据库中没有找到K线数据")
            return KbarSeriesGanZhiList([])
        
        # 处理缺失干支的记录
        rows_to_update = []
        for row in rows:
            if isindatetime(row[4], start_datetime, end_datetime):
                ganzhi_fields = row[11:19]  # year_gan 到 hour_zhi
                if any(field is None or field == '' for field in ganzhi_fields):
                    rows_to_update.append(row)
        
        # 计算并更新缺失的干支
        if rows_to_update:
            print(f"正在计算 {len(rows_to_update)} 条记录的干支数据...")
            update_query = """
            UPDATE kbar_data 
            SET year_gan=?, year_zhi=?, month_gan=?, month_zhi=?, 
                day_gan=?, day_zhi=?, hour_gan=?, hour_zhi=?
            WHERE id=?
            """
            
            for row in rows_to_update:
                try:
                    # 时间格式转换
                    ts_value = row[4]
                    if isinstance(ts_value, str) and 'T' in ts_value:
                        dt_obj = datetime.datetime.fromisoformat(ts_value.replace('T', ' '))
                        ts_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')
                    else:
                        ts_str = str(ts_value)
                    
                    ganzhi_result = GanZhiCalculator(ts_str)
                    
                    if len(ganzhi_result) >= 4:
                        year_ganzhi = ganzhi_result[0]
                        month_ganzhi = ganzhi_result[1] 
                        day_ganzhi = ganzhi_result[2]
                        hour_ganzhi = ganzhi_result[3] if len(ganzhi_result) > 3 else "无值"
                        
                        # 解析干支字符串
                        year_gan = year_ganzhi[0] if len(year_ganzhi) >= 2 else ""
                        year_zhi = year_ganzhi[1] if len(year_ganzhi) >= 2 else ""
                        month_gan = month_ganzhi[0] if len(month_ganzhi) >= 2 else ""
                        month_zhi = month_ganzhi[1] if len(month_ganzhi) >= 2 else ""
                        day_gan = day_ganzhi[0] if len(day_ganzhi) >= 2 else ""
                        day_zhi = day_ganzhi[1] if len(day_ganzhi) >= 2 else ""
                        hour_gan = hour_ganzhi[0] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                        hour_zhi = hour_ganzhi[1] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                        
                        cursor.execute(update_query, (
                            year_gan, year_zhi, month_gan, month_zhi,
                            day_gan, day_zhi, hour_gan, hour_zhi,
                            row[0]  # id
                        ))
                except Exception as e:
                    print(f"计算干支时出错 (ID: {row[0]}): {e}")
                    continue
            
            conn.commit()
            print(f"已更新 {len(rows_to_update)} 条记录的干支数据")
        
        # 重新查询更新后的数据
        cursor.execute(query)
        updated_rows = cursor.fetchall()
        
        # 按key分组处理数据
        data_dict = {}
        for row in updated_rows:
            if isindatetime(row[4], start_datetime, end_datetime):
                symbol, exchange, period = row[1], row[2], row[3]
                key = KbarSeriesKey(symbol, exchange, period)
                
                # 构建干支字符串
                year_gan, year_zhi = row[11], row[12]
                month_gan, month_zhi = row[13], row[14]
                day_gan, day_zhi = row[15], row[16]
                hour_gan, hour_zhi = row[17], row[18]
                
                if year_gan and year_zhi:  # 确保有干支数据
                    ganzhi_str = f"{year_gan}{year_zhi}-{month_gan}{month_zhi}-{day_gan}{day_zhi}-{hour_gan}{hour_zhi}"
                    
                    if key not in data_dict:
                        data_dict[key] = []
                    data_dict[key].append(ganzhi_str)
        
        # 构建返回结果
        result_list = []
        for key, ganzhi_list in data_dict.items():
            if ganzhi_list:  # 只添加有数据的序列
                result_list.append(KbarSeriesGanZhiType(key, ganzhi_list))
        
        print(f"返回 {len(result_list)} 个K线序列的干支数据")
        return KbarSeriesGanZhiList(result_list)
        
    except sqlite3.OperationalError as e:
        if "unable to open database file" in str(e):
            raise FileNotFoundError(f"无法打开数据库文件: {db_path}") from e
        else:
            print(f"数据库操作错误: {e}")
            return KbarSeriesGanZhiList([])
    except Exception as e:
        print(f"kbarseriesganzhi_none 执行出错: {e}")
        return KbarSeriesGanZhiList([])
    finally:
        if 'conn' in locals():
            conn.close()


def kbarseriesganzhi_DB(db_path, start_datetime, end_datetime, kbar_series_key):
    """
    当kbar_series为KbarSeriesKey或字典时，从数据库中查询指定键的k线数据并计算干支
    如果数据库中没有干支记录，则计算并插入数据库中
    
    参数:
        kbar_series_key: 可以是KbarSeriesKey对象或字典格式 {"symbol":..., "exchange":..., "period":...}
    """
    try:
        # 处理输入参数：支持列表格式、字典格式和KbarSeriesKey对象
        if isinstance(kbar_series_key, list):
            # 如果是列表，创建KbarSeriesKey对象
            if len(kbar_series_key) != 3:
                raise ValueError("列表必须包含3个元素: [symbol, exchange, period]")
            
            key_obj = KbarSeriesKey(
                symbol=kbar_series_key[0],
                exchange=kbar_series_key[1],
                period=kbar_series_key[2]
            )
            symbol = kbar_series_key[0]
            exchange = kbar_series_key[1]
            period = kbar_series_key[2]
        elif isinstance(kbar_series_key, dict):
            # 如果是字典，创建KbarSeriesKey对象
            if not all(key in kbar_series_key for key in ['symbol', 'exchange', 'period']):
                raise ValueError("字典必须包含 'symbol', 'exchange', 'period' 三个键")
            
            key_obj = KbarSeriesKey(
                symbol=kbar_series_key['symbol'],
                exchange=kbar_series_key['exchange'],
                period=kbar_series_key['period']
            )
            symbol = kbar_series_key['symbol']
            exchange = kbar_series_key['exchange']
            period = kbar_series_key['period']
        elif hasattr(kbar_series_key, 'symbol') and hasattr(kbar_series_key, 'exchange') and hasattr(kbar_series_key, 'period'):
            # 如果是KbarSeriesKey对象
            key_obj = kbar_series_key
            symbol = kbar_series_key.symbol
            exchange = kbar_series_key.exchange
            period = kbar_series_key.period
        else:
            raise TypeError("kbar_series_key 必须是列表、字典或KbarSeriesKey对象")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询指定键的K线数据
        query = """
        SELECT id, symbol, exchange, period, ts, open, high, low, close, volume, amount,
               year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi
        FROM kbar_data 
        WHERE symbol = ? AND exchange = ? AND period = ?
        ORDER BY ts
        """
        
        cursor.execute(query, (symbol, exchange, period))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"未找到匹配的K线数据: {symbol}-{exchange}-{period}")
            return KbarSeriesGanZhiType(key_obj, [])
        
        # 过滤时间范围内的数据
        filtered_rows = []
        rows_to_update = []  # 需要更新干支的行
        
        for row in rows:
            if isindatetime(row[4], start_datetime, end_datetime):  # row[4] 是 ts
                filtered_rows.append(row)
                
                # 检查是否需要计算干支（任一干支字段为空）
                ganzhi_fields = row[11:19]  # year_gan 到 hour_zhi
                if any(field is None for field in ganzhi_fields):
                    rows_to_update.append(row)
        
        # 计算缺失的干支数据
        if rows_to_update:
            print(f"正在计算 {len(rows_to_update)} 条记录的干支数据...")
            
            update_query = """
            UPDATE kbar_data 
            SET year_gan=?, year_zhi=?, month_gan=?, month_zhi=?, 
                day_gan=?, day_zhi=?, hour_gan=?, hour_zhi=?
            WHERE id=?
            """
            
            for row in rows_to_update:
                try:
                    # 修复：确保时间格式正确转换
                    ts_value = row[4]  # ts字段
                    if isinstance(ts_value, str) and 'T' in ts_value:
                        # ISO格式转换为GanZhiCalculator期望的格式
                        dt_obj = datetime.datetime.fromisoformat(ts_value.replace('T', ' '))
                        ts_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')
                    else:
                        ts_str = str(ts_value)
                    
                    # 使用 GanZhiCalculator 函数计算干支
                    ganzhi_result = GanZhiCalculator(ts_str)
                    
                    if len(ganzhi_result) >= 4:
                        year_ganzhi = ganzhi_result[0]
                        month_ganzhi = ganzhi_result[1] 
                        day_ganzhi = ganzhi_result[2]
                        hour_ganzhi = ganzhi_result[3] if len(ganzhi_result) > 3 else "无值"
                        
                        # 解析干支字符串
                        year_gan = year_ganzhi[0] if len(year_ganzhi) >= 2 else ""
                        year_zhi = year_ganzhi[1] if len(year_ganzhi) >= 2 else ""
                        month_gan = month_ganzhi[0] if len(month_ganzhi) >= 2 else ""
                        month_zhi = month_ganzhi[1] if len(month_ganzhi) >= 2 else ""
                        day_gan = day_ganzhi[0] if len(day_ganzhi) >= 2 else ""
                        day_zhi = day_ganzhi[1] if len(day_ganzhi) >= 2 else ""
                        hour_gan = hour_ganzhi[0] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                        hour_zhi = hour_ganzhi[1] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                        
                        # 更新数据库
                        cursor.execute(update_query, (
                            year_gan, year_zhi, month_gan, month_zhi,
                            day_gan, day_zhi, hour_gan, hour_zhi,
                            row[0]  # id
                        ))
                    else:
                        print(f"干支计算结果不完整 (ID: {row[0]}): {ganzhi_result}")
                        
                except Exception as e:
                    print(f"计算干支时出错 (ID: {row[0]}): {e}")
                    continue
            
            conn.commit()
            print(f"已更新 {len(rows_to_update)} 条记录的干支数据")
        
        # 重新查询更新后的数据
        cursor.execute(query, (symbol, exchange, period))
        updated_rows = cursor.fetchall()
        
        # 构建结果
        ganzhi_list = []
        for row in updated_rows:
            if isindatetime(row[4], start_datetime, end_datetime):
                # 构建干支字符串
                ganzhi_str = f"{row[11] or ''}{row[12] or ''}-{row[13] or ''}{row[14] or ''}-{row[15] or ''}{row[16] or ''}-{row[17] or ''}{row[18] or ''}"
                ganzhi_list.append(ganzhi_str)
        
        return KbarSeriesGanZhiType(key_obj, ganzhi_list)
        
    except Exception as e:
        print(f"kbarseriesganzhi_DB 执行出错: {e}")
        # 确保返回时使用正确的key_obj
        if 'key_obj' in locals():
            return KbarSeriesGanZhiType(key_obj, [])
        else:
            # 如果key_obj创建失败，创建一个默认的
            default_key = KbarSeriesKey("", "", "")
            return KbarSeriesGanZhiType(default_key, [])
    finally:
        if 'conn' in locals():
            conn.close()


def _convert_dict_to_kbar_series(kbar_dict):
    """
    将包含kbar数据的字典转换为KbarSeries对象
    """
    if not isinstance(kbar_dict, dict) or 'kbar' not in kbar_dict:
        raise ValueError("输入必须是包含kbar数据的字典")
    
    if not all(key in kbar_dict for key in ['symbol', 'exchange', 'period', 'kbar']):
        raise ValueError("字典必须包含 'symbol', 'exchange', 'period', 'kbar' 四个键")
    
    # 创建KbarSeriesKey
    key_obj = KbarSeriesKey(
        symbol=kbar_dict['symbol'],
        exchange=kbar_dict['exchange'],
        period=kbar_dict['period']
    )
    
    # 转换kbar数据为Kbar对象列表
    kbar_list = []
    for kbar_data in kbar_dict['kbar']:
        if len(kbar_data) != 7:
            raise ValueError("每个kbar数据必须包含7个元素: [ts, open, high, low, close, volume, amount]")
        
        # 解析时间戳
        ts_str = kbar_data[0]
        if isinstance(ts_str, str):
            # parse_datetime_string 返回元组，需要转换为 datetime 对象
            year, month, day, hour, minute, second = parse_datetime_string(ts_str)
            ts = datetime.datetime(
                year, month, day,
                hour if hour >= 0 else 0,
                minute if minute >= 0 else 0,
                second if second >= 0 else 0
            )
        elif isinstance(ts_str, datetime.datetime):
            ts = ts_str
        else:
            raise ValueError(f"不支持的时间戳类型: {type(ts_str)}")
        
        # 创建Kbar对象
        kbar_obj = Kbar(
            ts=ts,
            open=float(kbar_data[1]),
            high=float(kbar_data[2]),
            low=float(kbar_data[3]),
            close=float(kbar_data[4]),
            volume=float(kbar_data[5]),
            amount=float(kbar_data[6])
        )
        kbar_list.append(kbar_obj)
    
    # 创建并返回KbarSeries对象
    return KbarSeries(key_obj, kbar_list)


def kbarseriesganzhi_noDB(db_path, start_datetime, end_datetime, kbar_series):
    """
    当kbar_series为KbarSeries或字典且useDB=False时，实时计算干支序列
    并将数据库中不存在的记录连带干支信息插入数据库中
    
    参数:
        kbar_series: 可以是KbarSeries对象或包含kbar数据的字典
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        result_list = []  # 改为列表存储 KbarSeriesGanZhi 对象
        
        # 检查输入类型并进行转换
        if isinstance(kbar_series, dict) and 'kbar' in kbar_series:
            # 如果是包含kbar数据的字典，转换为KbarSeries对象
            kbar_series = _convert_dict_to_kbar_series(kbar_series)
        
        # 处理 KbarSeries 对象
        if hasattr(kbar_series, 'get_key') and hasattr(kbar_series, 'get_kbar_list'):
            # 单个 KbarSeries 对象
            key = kbar_series.get_key()
            kbar_list = kbar_series.get_kbar_list()
            
            ganzhi_list = []
            new_records = []  # 需要插入数据库的新记录
            
            for kbar in kbar_list:
                # 检查时间范围
                if not isindatetime(kbar.ts, start_datetime, end_datetime):
                    continue
                
                # 检查数据库中是否已存在该记录
                check_query = """
                SELECT id FROM kbar_data 
                WHERE symbol=? AND exchange=? AND period=? AND ts=?
                """
                cursor.execute(check_query, (key.symbol, key.exchange, key.period, kbar.ts))
                existing = cursor.fetchone()
                
                # 计算干支
                try:
                    # 将datetime对象转换为字符串格式供GanZhiCalculator使用
                    if isinstance(kbar.ts, datetime.datetime):
                        ts_str = kbar.ts.strftime('%Y/%m/%d %H:%M:%S')
                    else:
                        # 如果是字符串，需要转换格式
                        if 'T' in str(kbar.ts):
                            # ISO格式转换
                            dt_obj = datetime.datetime.fromisoformat(str(kbar.ts).replace('T', ' '))
                            ts_str = dt_obj.strftime('%Y/%m/%d %H:%M:%S')
                        else:
                            ts_str = str(kbar.ts)
                    
                    # 使用 GanZhiCalculator 函数计算干支
                    ganzhi_result = GanZhiCalculator(ts_str)
                    
                    if len(ganzhi_result) >= 4:
                        year_ganzhi = ganzhi_result[0]
                        month_ganzhi = ganzhi_result[1] 
                        day_ganzhi = ganzhi_result[2]
                        hour_ganzhi = ganzhi_result[3] if len(ganzhi_result) > 3 else "无值"
                        
                        # 构建干支字符串
                        ganzhi_str = f"{year_ganzhi}-{month_ganzhi}-{day_ganzhi}-{hour_ganzhi}"
                        ganzhi_list.append(ganzhi_str)
                        
                        # 如果数据库中不存在，准备插入
                        if not existing:
                            # 解析干支字符串以便存储到数据库
                            year_gan = year_ganzhi[0] if len(year_ganzhi) >= 2 else ""
                            year_zhi = year_ganzhi[1] if len(year_ganzhi) >= 2 else ""
                            month_gan = month_ganzhi[0] if len(month_ganzhi) >= 2 else ""
                            month_zhi = month_ganzhi[1] if len(month_ganzhi) >= 2 else ""
                            day_gan = day_ganzhi[0] if len(day_ganzhi) >= 2 else ""
                            day_zhi = day_ganzhi[1] if len(day_ganzhi) >= 2 else ""
                            hour_gan = hour_ganzhi[0] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                            hour_zhi = hour_ganzhi[1] if len(hour_ganzhi) >= 2 and hour_ganzhi != "无值" else ""
                            
                            # 准备插入数据库的记录
                            new_records.append((
                                key.symbol, key.exchange, key.period, kbar.ts,
                                kbar.open, kbar.high, kbar.low, kbar.close,
                                kbar.volume, kbar.amount,
                                year_gan, year_zhi, month_gan, month_zhi,
                                day_gan, day_zhi, hour_gan, hour_zhi
                            ))
                    
                    else:
                        print(f"警告：无法计算时间 {ts_str} 的干支")
                        ganzhi_list.append("计算失败")
                        
                except Exception as e:
                    print(f"计算干支时出错: {e}")
                    ganzhi_list.append("计算出错")
            
            # 批量插入新记录
            if new_records:
                insert_query = """
                INSERT INTO kbar_data (
                    symbol, exchange, period, ts, open, high, low, close, volume, amount,
                    year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.executemany(insert_query, new_records)
                print(f"已插入 {len(new_records)} 条新的K线记录到数据库")
            
            # 创建 KbarSeriesGanZhi 对象
            kbar_series_ganzhi = KbarSeriesGanZhiType(key, ganzhi_list)
            result_list.append(kbar_series_ganzhi)
            
            conn.commit()
            conn.close()
            
            # 返回单个 KbarSeriesGanZhi 对象
            return kbar_series_ganzhi
        
        else:
            raise TypeError("kbar_series 必须是 KbarSeries 对象或包含kbar数据的字典")
            
    except Exception as e:
        print(f"处理过程中出错: {e}")
        if 'conn' in locals():
            conn.close()
        raise


def KbarSeriesGanZhi(start_datetime, end_datetime, kbar_series, useDB: bool = True):
    
    db_path = get_stock_kbar_path()

    if not check_stock_kbar_path():
        raise FileNotFoundError("kbar数据库文件不存在,请先配置kbar数据库文件路径")
        return None

    if kbar_series is None:
        """
        当kbar_series为None时，从数据库中查询所有在时间范围内的k线序列
        并且最终返回一个KbarSeriesGanZhiList
        """
        kbar_series_ganzhi_list = kbarseriesganzhi_none(db_path, start_datetime, end_datetime)
        return kbar_series_ganzhi_list

    else:
        """
        当kbar_series不为None时，计算kbar_series中所有k线序列的干支序列
        并且最终返回一个KbarSeriesGanZhiList
        """

        if useDB:
            """
            当useDB为True时，从数据库中查询所有在时间范围内的k线序列：如果数据库中没有记录，则计算并插入数据库中
            如果有记录则直接使用，不计算
            并且最终返回一个KbarSeriesGanZhi
            此时kbar_series为一个KbarSeriesKey、列表或字典（不包含kbar数据）
            """
            kbar_series_ganzhi = kbarseriesganzhi_DB(db_path, start_datetime, end_datetime, kbar_series)
            return kbar_series_ganzhi

        else:
            """
            当useDB为False时，实时计算kbar_series中所有k线序列的干支序列
            并且最终返回一个KbarSeriesGanZhiList
            此时kbar_series可以是：
            1. KbarSeries对象
            2. 包含kbar数据的字典格式：{"symbol":..., "exchange":..., "period":..., "kbar":[[...], [...]]}
            """
            # 直接传递给kbarseriesganzhi_noDB，让它内部处理字典转换
            kbar_series_ganzhi = kbarseriesganzhi_noDB(db_path, start_datetime, end_datetime, kbar_series)
            return kbar_series_ganzhi



