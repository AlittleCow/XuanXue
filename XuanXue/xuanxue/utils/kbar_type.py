import datetime
from typing import List, Optional

class Kbar:
    def __init__(self, ts: datetime.datetime, open: float, high: float, low: float, close: float, volume: float, amount: float):
        self.ts = ts
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.amount = amount
    
    def get_ts(self):
        return self.ts
    
    def get_open(self):
        return self.open
    
    def get_high(self):
        return self.high
    
    def get_low(self):
        return self.low
    
    def get_close(self):
        return self.close
    
    def get_volume(self):
        return self.volume
    
    def get_amount(self):
        return self.amount
    
    def __str__(self):
        return f"Kbar(ts={self.ts}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume}, amount={self.amount})"
    
    def __repr__(self):
        return self.__str__()

class KbarSeriesKey:
    def __init__(self, symbol: str, exchange: str, period: str):
        self.symbol = symbol
        self.exchange = exchange
        self.period = period
    
    def get_symbol(self):
        return self.symbol
    
    def get_exchange(self):
        return self.exchange
    
    def get_period(self):
        return self.period
    
    def __str__(self):
        return f"KbarSeriesKey(symbol={self.symbol}, exchange={self.exchange}, period={self.period})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, KbarSeriesKey):
            return False
        return (self.symbol == other.symbol and 
                self.exchange == other.exchange and 
                self.period == other.period)
    
    def __hash__(self):
        return hash((self.symbol, self.exchange, self.period))

class KbarSeries:
    def __init__(self, kbar_series_key: KbarSeriesKey, kbar_list: List[Kbar]):
        self.kbar_series_key = kbar_series_key
        self.kbar_list = kbar_list
    
    def get_key(self):
        return self.kbar_series_key
    
    def get_kbar_list(self):
        return self.kbar_list
    
    def get_length(self):
        return len(self.kbar_list)
    
    def add_kbar(self, kbar: Kbar):
        """添加K线数据"""
        self.kbar_list.append(kbar)
    
    def get_latest_kbar(self) -> Optional[Kbar]:
        """获取最新的K线数据"""
        if self.kbar_list:
            return max(self.kbar_list, key=lambda x: x.ts)
        return None
    
    def filter_by_time_range(self, start_time: datetime.datetime, end_time: datetime.datetime) -> 'KbarSeries':
        """按时间范围过滤"""
        filtered_kbars = [
            kbar for kbar in self.kbar_list 
            if start_time <= kbar.ts <= end_time
        ]
        return KbarSeries(self.kbar_series_key, filtered_kbars)

class KbarSeriesGanZhi:
    def __init__(self, kbar_series_key: KbarSeriesKey, ganzhi_list: List[str]):
        self.kbar_series_key = kbar_series_key
        self.ganzhi_list = ganzhi_list
    
    def get_key(self):
        return self.kbar_series_key
    
    def get_ganzhi_list(self):
        return self.ganzhi_list
    
    def get_length(self):
        return len(self.ganzhi_list)
    
    def add_ganzhi(self, ganzhi: str):
        """添加干支数据"""
        self.ganzhi_list.append(ganzhi)
    
    def info(self):
        return {
            "key":[
                self.kbar_series_key.get_symbol(),
                self.kbar_series_key.get_exchange(),
                self.kbar_series_key.get_period(),
            ],
            "ganzhi":self.ganzhi_list,
        }
    

class KbarSeriesGanZhiList:
    def __init__(self, kbar_series_ganzhi_list: List[KbarSeriesGanZhi] = None):
        self.kbar_series_ganzhi_list = kbar_series_ganzhi_list or []
    
    def get_kbar_series_ganzhi_list(self):
        return self.kbar_series_ganzhi_list
    
    def get_series_amount(self):
        return len(self.kbar_series_ganzhi_list)
    
    def add_kbar_series_ganzhi(self, kbar_series_ganzhi: KbarSeriesGanZhi):
        """添加K线干支序列"""
        self.kbar_series_ganzhi_list.append(kbar_series_ganzhi)
    
    def find_kbar_series(self, symbol: str, exchange: str, period: str) -> Optional[KbarSeriesGanZhi]:
        """查找指定的K线序列"""
        for kbar_series_ganzhi in self.kbar_series_ganzhi_list:
            key = kbar_series_ganzhi.get_key()
            if (key.get_symbol() == symbol and 
                key.get_exchange() == exchange and 
                key.get_period() == period):
                return kbar_series_ganzhi
        return None
    
    def get_all_symbols(self) -> List[str]:
        """获取所有股票代码"""
        return list(set(series.get_key().get_symbol() for series in self.kbar_series_ganzhi_list))
    
    def filter_by_symbol(self, symbol: str) -> 'KbarSeriesGanZhiList':
        """按股票代码过滤"""
        filtered_list = [
            series for series in self.kbar_series_ganzhi_list
            if series.get_key().get_symbol() == symbol
        ]
        return KbarSeriesGanZhiList(filtered_list)
    
    def info(self):
        info_list=[]
        for i in range(len(self.kbar_series_ganzhi_list)):
            info_list.append({
                "key":[
                    self.kbar_series_ganzhi_list[i].get_key().get_symbol(),
                    self.kbar_series_ganzhi_list[i].get_key().get_exchange(),
                    self.kbar_series_ganzhi_list[i].get_key().get_period(),
                ],
                "ganzhi":self.kbar_series_ganzhi_list[i].get_ganzhi_list(),
            })
        return info_list



    
    
   
        



