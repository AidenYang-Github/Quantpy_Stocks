# call mysql_stock.py
# import mysql_stock.main
from mysql_stock_01 import main

if __name__ == '__main__':
    """
    # mysql_stock.py中由于受到接口权限限制，改用mysql_stock_01.py的接口进行日线行情调用
    """
    main()
