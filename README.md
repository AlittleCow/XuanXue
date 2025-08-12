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



## 项目文件结构

XuanXue包开发/
├── .coverage                    # 代码覆盖率报告文件
├── .gitignore                   # Git忽略文件配置
├── .pytest_cache/               # pytest缓存目录
├── README.md                    # 项目说明文档
├── XuanXue/                     # 主包目录
│   ├── __init__.py             # 包初始化文件
│   ├── examples/               # 使用示例目录
│   └── xuanxue/                # 核心模块目录
│       ├── __init__.py         # 模块初始化，导出主要API
│       ├── config/             # 配置模块
│       │   ├── __init__.py     # 配置模块初始化
│       │   ├── config.py       # 干支配置常量（天干地支映射表）
│       │   ├── config.txt      # 配置文件
│       │   └── config_manager.py # 配置管理器（数据库路径等）
│       ├── core/               # 核心功能模块
│       │   ├── ganzhi_calculator.py # 干支计算器（日期时间转干支）
│       │   ├── kbarseriesganzhi.py  # K线序列干支计算（主要功能）
│       │   └── stock_ganzhi.py      # 股票干支计算（上市日期干支）
│       └── utils/              # 工具模块
│           ├── __init__.py     # 工具模块初始化
│           └── kbar_type.py    # K线数据类型定义
├── getdata.py                   # 数据获取脚本（从tushare获取股票基本信息）
├── htmlcov/                     # HTML格式的代码覆盖率报告目录
├── pytest.ini                  # pytest测试配置文件
├── requirements-dev.txt         # 开发环境依赖包列表
├── requirements.txt             # 生产环境依赖包列表
├── run_tests.py                 # 测试运行脚本
├── setup.py                     # 包安装配置脚本
├── stock_meta.db               # 股票基本信息数据库，用于示范数据库格式
├── stock_kbar.db               # 股票k线数据数据库，用于示范数据库格式
└── tests/                       # 测试目录
    ├── __init__.py             # 测试模块初始化
    ├── conftest.py             # pytest配置和fixture
    ├── test_config.py          # 配置模块测试
    ├── test_ganzhi_calculator.py # 干支计算器测试
    ├── test_integration.py     # 集成测试
    ├── test_performance.py     # 性能测试
    └── test_stock_ganzhi.py    # 股票干支功能测试

##测试
请运行run_tests.py文件或者test_demo.py


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