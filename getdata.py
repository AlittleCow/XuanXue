import tushare as ts 
import sqlite3
import pandas as pd

# 初始化tushare
tushare = ts.pro_api()

# 获取各交易所股票数据
df_szse = tushare.stock_company(exchange='SZSE', fields='ts_code,com_name,setup_date')
df_sse = tushare.stock_company(exchange='SSE', fields='ts_code,com_name,setup_date')
df_bse = tushare.stock_company(exchange='BSE', fields='ts_code,com_name,setup_date')

def save_to_database():
    """将获取的数据保存到stock_meta.db数据库"""
    # 为每个数据框添加交易所标识
    df_szse['exchange'] = 'SZSE'
    df_sse['exchange'] = 'SSE'
    df_bse['exchange'] = 'BSE'
    
    # 合并所有数据
    df_all = pd.concat([df_szse, df_sse, df_bse], ignore_index=True)
    
    # 重命名列以匹配数据库字段
    df_all = df_all.rename(columns={
        'ts_code': 'symbol',
        'com_name': 'name',
        'setup_date': 'list_date'
    })
    
    # 添加天干地支列（暂时为空）
    df_all['年干'] = None
    df_all['年支'] = None
    df_all['月干'] = None
    df_all['月支'] = None
    df_all['日干'] = None
    df_all['日支'] = None
    
    # 连接数据库并保存数据
    conn = sqlite3.connect('stock_meta.db')
    
    # 创建表（如果不存在）
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_meta (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            exchange TEXT NOT NULL,
            list_date TEXT,
            年干 TEXT,
            年支 TEXT,
            月干 TEXT,
            月支 TEXT,
            日干 TEXT,
            日支 TEXT
        )
    ''')
    
    # 保存数据
    df_all.to_sql('stock_meta', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    
    print(f"成功保存 {len(df_all)} 条股票数据到 stock_meta.db")
    return df_all

# 如果直接运行此文件，则执行保存操作
if __name__ == "__main__":
    save_to_database()
