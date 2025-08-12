# XuanXue - 玄学数据分析包

XuanXue是一个专门用于干支计算和股票玄学分析的Python包。

## 功能特性

- 🗓️ **干支计算**: 支持任意日期时间的干支计算
- 📈 **股票分析**: 查询股票上市日期的干支信息
- 🗄️ **智能缓存**: 自动缓存计算结果，提高查询效率
- ⚙️ **配置管理**: 简单的配置文件管理系统
- 🔧 **易于使用**: 类似pandas的简洁API

## 安装

cd ../XuanXue包开发
pip install -e .


## 快速开始

```python
import XuanXue as xx
或者 import XuanXue.xuanxue as xx

#配置数据库路径
xx.set_stock_meta_path("/path/to/your/stock_meta.db")
xx.set_stock_kbar_path("/path/to/your/stock_kbar.db")
"""
用户配置的路径在XuanXue/xuanxue/config/config.txt中
"""

#检查数据库路径下是否存在数据库文件
print(xx.check_stock_meta_path())
print(xx.check_stock_kbar_path())

#获取数据库路径
stock_meta_path = xx.get_stock_meta_path()
stock_kbar_path = xx.get_stock_kbar_path()

#函数nBoardDateGanZhi
"""
这个函数需要配置数据库stock_meta.db,返回的类型是
"""
result=xx.nBoardDateGanZhi('000001.SZ')
print(result)


#函数DateTimeGanZhi
ganzhi = xx.DateTimeGanZhi('2023/10/10 15:30:45')
print(f"干支: {ganzhi}")

#函数KbarSeriesGanZhi
“”“
使用这个函数需要配置stock_kbar.db
”“”
这个函数有三个用法
1. 输入一个k线数据的键，返回这个键的在数据库中所有k线数据（如果数据库中已经有数据库数据，则直接返回
，否则计算并存储）

test=x.KbarSeriesGanZhi("2019-01-01", "2024-01-31",x.KbarSeriesKey("600000","SH","1day"),useDB=True)
或者
test=x.KbarSeriesGanZhi("2019-01-01", "2024-01-31",["600000","SH","1day"],useDB=True)
或者
test=x.KbarSeriesGanZhi("2019-01-01", "2024-01-31",{"symbol":"600000","exchange":"SH","period":"1day"},useDB=True)



test是一个KbarSeriesGanZhi类型的对象，该类型提供
test.info()函数返回k线数据的键和干支列表


2. 不输入k线数据的键，返回所有在数据库中的k线数据与干支

test=x.KbarSeriesGanZhi("2019-01-01", "2024-01-31",None,useDB=True)

其中test是一个KbarSeriesGanZhiList类型的对象，该类型提供
test.info()函数返回所有在数据库中的k线数据的键和干支列表


3. 输入一个k线数据的字典，返回KbarSeriesGanZhi类型的对象

dic_example={"symbol":"600000","exchange":"SH","period":"1day","kbar":[[
    "2019-01-06 00:00:00",

    100,
    101,
    99,
    100,
    1000000,
    100000000,
],[
    "2019-01-03 00:00:00",
    100,
    101,
    99,
    100,
    1000000,
    100000000,
]]
}
test=x.KbarSeriesGanZhi("2019-01-01 00:00:00", "2019-01-10 00:00:00",dic_example,useDB=False)
print(test.info())



## API文档

### 主要函数

- `nBoardDateGanZhi(symbol)`: 查询股票上市日期干支
- `DateTimeGanZhi(datetime_str)`: 计算日期时间干支
- `set_stock_meta_path(path)`: 设置数据库路径
- `get_stock_meta_path()`: 获取当前数据库路径
- `check_stock_meta_path()`: 检查数据库状态

### 配置管理

```python
# 设置数据库路径
xx.set_stock_meta_path("/path/to/stock_meta.db")

# 获取当前路径
path = xx.get_stock_meta_path()

# 检查数据库是否可用
is_valid, message = xx.check_stock_meta_path()
```

## 依赖

- Python >= 3.8
- sxtwl >= 1.0.0

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持干支计算
- 支持股票数据查询
- 智能缓存系统