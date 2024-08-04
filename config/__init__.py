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
