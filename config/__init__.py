import os

print('\n')
print(f'{"-" * 100}')

# 数据库参数初始化配置
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'stock_databases_02'  # 个股日线行情数据数据库
CUU = 'charset=utf8&use_unicode=1'

# 量化因子数据库
QUANTIZER_DATABASE = 'quantizer_db'

# 复权因子数据库
ADJFACTOR_DATABASE = 'adjfactor_db'

# 数据表名称配置
STOCK_TSCODE = '000001.SZ'
STOCK_BASIC_NAME = 'all_stock_basic'
DELISTED_STOCK_TBNAME = 'all_delisted_stock'

# Tushare接口状态说明（具体查看../Module/tushare_api.py文件）
# <stock_basic_>建议每天第一次参数设置为'L'，成功将数据存储到本地后，当天如需多次运行程序建议后续将参数设置为None
STOCK_BASIC_ = 'L'  # TuShare中的stock_basic接口：'L'为调用上市股票列表接口，'D'为调用退市股票列表接口；None为不调用接口；

# 是否使用前复权数据
USE_QFQ = True


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
