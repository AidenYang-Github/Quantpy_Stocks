import os

print('\n')
print(f'{"-" * 100}')

# 数据库参数初始化配置
username = 'root'
password = '123456'
host = '127.0.0.1'
port = '3306'
database = 'stock_databases_02'
cuu = 'charset=utf8&use_unicode=1'

# 数据表名称配置
stock_table_name = 'all_stock_basic'
delisted_stock_tbname = 'all_delisted_stock'

# Tushare接口状态说明（具体查看../Module/tushare_api.py文件）
# <stock_basic_>建议每天第一次参数设置为'L'，成功将数据存储到本地后，当天如需多次运行程序建议后续将参数设置为None
stock_basic_ = 'L'  # TuShare中的stock_basic接口：'L'为调用上市股票列表接口，'D'为调用退市股票列表接口；None为不调用接口；


# 字体颜色管理
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BLUEBOLD = '\033[94m\033[1m'
    END = '\033[0m'


print(f'配置文件已加载，文件路径：{os.path.abspath(__file__)}')
