"""
干支计算模块

GanZhi_str
GanZhiCalculator_Date(year,month,day)
GanZhiCalculator_Core(year,month,day,hour=-1,minute=-1,second=-1)
calculate_hour_ganzhi(hour,day_gan_index)
calculate_ms_ganzhi(ms)
create_ganzhi_object(gan_index,zhi_index)
parse_datetiem_string(datetime_str)
GanZhiCalculator(datetime_str)

最终导出函数：DateTimeGanZhi

"""
import datetime
import sxtwl
from ..config.config import gan,zhi,gan_start_map

def GanZhi_Str(gz):
    """将 sxtwl.GZ 对象转为字符串"""
    return gan[gz.tg] + zhi[gz.dz]

def GanZhiCalculator_Date(year,month,day):
    """
    计算干支
    :param year: 年
    :param month: 月
    :param day: 日
    :return: 日期干支索引
    """

    day=sxtwl.fromSolar(year,month,day)
    year_gz = day.getYearGZ()
    month_gz = day.getMonthGZ()
    day_gz = day.getDayGZ()
    GanZhiOrder_Date = [year_gz, month_gz, day_gz]
    return GanZhiOrder_Date
   
def GanZhiCalculator_Core(year,month,day,hour=-1,minute=-1,second=-1):
    """
    计算干支
    :param year: 年
    :param month: 月
    :param day: 日
    :param hour: 时
    :param minute: 分
    :param second: 秒
    :return: 干支
    """
    
    GanZhiOrder_Date=GanZhiCalculator_Date(year,month,day)
    GanZhiOrder_Time=[]
    if hour>=0:
       day_gz=GanZhiOrder_Date[2]
       hour_gz=sxtwl.getShiGz(day_gz.tg,hour)
       GanZhiOrder_Time.append(hour_gz)
    else:
        GanZhiOrder_Time.append(-1)
    
    """
    if minute>=0:
        minute_gan_idx,minute_zhi_idx=calculate_ms_ganzhi(minute)
        minute_gz=create_ganzhi_object(minute_gan_idx,minute_zhi_idx)
        GanZhiOrder_Time.append(minute_gz)
    else:
        GanZhiOrder_Time.append(-1)

    if second>=0:
        second_gan_idx,second_zhi_idx=calculate_ms_ganzhi(second)
        second_gz=create_ganzhi_object(second_gan_idx,second_zhi_idx)
        GanZhiOrder_Time.append(second_gz)
    else:
        GanZhiOrder_Time.append(-1)
    """
    GanZhiOrder=GanZhiOrder_Date+GanZhiOrder_Time
    return GanZhiOrder

def calculate_ms_ganzhi(ms):

    """
    计算分秒干支
    :param ms: 分秒
    :return: 分秒干支索引
    """
    gan_index=ms%10
    zhi_index=ms%12
    return gan_index,zhi_index

def create_ganzhi_object(gan_index,zhi_index):
    """
    创建干支对象
    :param gan_index: 干支索引
    :param zhi_index: 地支索引
    :return: 干支对象
    """
    return sxtwl.GZ(gan_index,zhi_index)

def parse_datetime_string(datetime_str):
    """
    解析日期时间字符串
    :param datetime_str: 日期时间字符串，如 "2025/07/29 18:08:30"
    :return: (year, month, day, hour, minute, second)
    """
    # 支持多种格式，按精度排序
    formats = [
        ("%Y/%m/%d %H:%M:%S", True, True, True),    # 完整时间
        ("%Y-%m-%d %H:%M:%S", True, True, True),
        ("%Y%m%d %H:%M:%S", True, True, True),
        ("%Y/%m/%d %H:%M", True, True, False),      # 到分钟
        ("%Y-%m-%d %H:%M", True, False, False),        
        ("%Y%m%d %H:%M", True, False, False),
        ("%Y/%m/%d %H", True, False, False),       # 到小时
        ("%Y-%m-%d %H", True, False, False),
        ("%Y%m%d %H", True, False, False),
        ("%Y/%m/%d", False, False, False),          # 只有日期 
        ("%Y-%m-%d", False, False, False),
        ("%Y%m%d", False, False, False),
    ]
    
    for fmt, has_hour, has_minute, has_second in formats:
        try:
            dt = datetime.datetime.strptime(datetime_str, fmt)
            hour = dt.hour if has_hour else -1
            minute = dt.minute if has_minute else -1
            second = dt.second if has_second else -1
            return dt.year, dt.month, dt.day, hour, minute, second
        except ValueError:
            continue
    
    raise ValueError(f"无法解析日期时间格式: {datetime_str}")


def GanZhiCalculator(datetiem_str):
    """
    计算干支
    :param datetiem_str: 日期时间字符串，如 "2025/07/29 18:08:30"
    :return: 干支
    """
    year,month,day,hour,minute,second=parse_datetime_string(datetiem_str)
    GanZhiOrder=GanZhiCalculator_Core(year,month,day,hour,minute,second)
    GanZhi=[]
    for gz in GanZhiOrder:
        if gz==-1:
            GanZhi.append("无值")
        else:
            GanZhi.append(GanZhi_Str(gz))
    return GanZhi

def DateTimeGanZhi(datetime_str):
    return GanZhiCalculator(datetime_str)


# 测试代码
if __name__ == "__main__":
    print("=== 干支计算测试 ===")
    
    # 测试1：只计算日期
    print("\n1. 日期干支测试:")
    date_result = GanZhiCalculator("2023/10/10")
    print(f"2023年10月10日: {date_result}")
    
    # 测试2：计算完整时间
    print("\n2. 完整时间干支测试:")
    full_result = GanZhiCalculator("2025/07/29 18:08:30")
    print(f"2025年7月29日18时8分30秒: {full_result}")
    
  
    # 测试4：不同时间的对比
    print("\n4. 不同时间对比:")
    times = [
        "2025/07/29 00:00:00",
        "2025/07/29 12:00:00", 
        "2025/07/29 23:59:59"
    ]
    
    for time_str in times:
        result = GanZhiCalculator(time_str)
        print(f"{time_str}: {result}")

    # 测试5： 测试不同的日期
    print("\n5. 不同日期对比:")
    dates = [
        "2025/07/29",
        "2025/07/30",
        "2025/07/31"
    ]
    
    for date_str in dates:
        result = GanZhiCalculator(date_str)
        print(f"{date_str}: {result}")
    
