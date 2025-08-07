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

# 配置数据库路径
xx.set_stock_meta_path("/path/to/your/stock_meta.db")

# 查询股票上市日期干支
result = xx.nBoardDateGanZhi('000001.SZ')
print(f"{result['name']} 上市日期干支: {result['ganzhi']}")

# 计算任意日期干支
ganzhi = xx.DateTimeGanZhi('2023/10/10 15:30:45')
print(f"干支: {ganzhi}")

# 检查数据库状态
is_valid, message = xx.check_stock_meta_path()
print(f"数据库状态: {message}")
```

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