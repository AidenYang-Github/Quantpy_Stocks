"""
Created on 2024年08月01日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks

数据库操作模块
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from config import USERNAME, PASSWORD, HOST, PORT, DATABASE, CUU


class MySQLDatabaseOperations:
    """
    数据库操作
    """

    def __init__(self, database=DATABASE):
        # 创建数据库连接
        self.engine_ts = create_engine('mysql://%s:%s@%s:%s/%s?%s' % (USERNAME, PASSWORD, HOST, PORT, database, CUU))
        pass

    # =============== 新建数据库 ===============
    def create_mysql_database(self, database=DATABASE):
        """
        检查数据库是否存在，不存在则新建数据库
        :return: 若不存在，则返回新建数据库的链接；否则无返回值，为默认数据库
        """
        self.engine_ts = create_engine('mysql://%s:%s@%s:%s/%s?%s' % (USERNAME, PASSWORD, HOST, PORT, database, CUU))
        if not database_exists(self.engine_ts.url):
            print(f'{database}数据库不存在，新建数据库链接：{self.engine_ts.url}')
            create_database(self.engine_ts.url)
        else:
            print(f'{database}数据库已存在，后续操作将在该数据库下进行')
        return self.engine_ts

    # =============== 从数据库读取数据 ===============
    def show_tables(self, database=DATABASE):
        """
        读取数据库中所有的数据表
        :return:list:[str,str,……]
        """
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}'".format(db_name=database)
        dataframe = pd.read_sql_query(sql, self.engine_ts)

        table_name_list = dataframe.TABLE_NAME.to_list()
        return table_name_list

    def read_data(self, table_name):
        """
        根据表名，读取表中的数据
        :param table_name: 表名
        :return: 表中数据
        """
        sql = "SELECT * FROM {tb_name}".format(tb_name=table_name)
        dataframe = pd.read_sql_query(sql, self.engine_ts)
        return dataframe

    def read_table_last_date(self, table_name):
        """
        获取股票日线行情表中最新的日期
        :param table_name:
        :return:
        """
        sql = "SELECT max(trade_date) FROM {tb_name}".format(tb_name=table_name)
        dataframe = pd.read_sql_query(sql, self.engine_ts)
        return dataframe.values[0][0]

    def read_bak_basic_data(self, tb_name, ts_code):
        """
        根据表名，读取表中的数据
        :param tb_name: 表名
        :param ts_code: 股票代码
        :return: 表中数据
        """
        sql = "SELECT trade_date,ts_code,pe,pb FROM {tb_name} WHERE ts_code='{ts_code}'".format(tb_name=tb_name,
                                                                                                ts_code=ts_code)
        dataframe = pd.read_sql_query(sql, self.engine_ts)
        return dataframe

    def read_tscode_name(self, stn, ts_code):
        """
        根据股票的代码获取股票的中文名称
        :param stn:所要查询的表名称
        :param ts_code:所要查询的股票代码（例如：000001.SZ）
        :return:股票的中文名称（例如：平安银行）
        """
        sql = "SELECT ts_code,name FROM {stock_table_name} WHERE ts_code='{ts_code}'".format(stock_table_name=stn,
                                                                                             ts_code=ts_code)
        dataframe = pd.read_sql_query(sql, self.engine_ts)
        return dataframe.name[0]

    # =============== 向数据库存储数据 ===============
    def write_data(self, dataframe, table_name, **kwargs):
        """
        将给定的df数据存入数据表中
        :param dataframe:所需存入的df数据，dataframe
        :param table_name:存入表中的名称，str
        :return:
        """
        if_exists = 'append'
        chunksize = 5000
        for key, value in kwargs.items():
            if key == 'if_exists':
                if_exists = value
            elif key == 'chunksize':
                chunksize = value

        dataframe.to_sql(table_name, self.engine_ts, index=False, if_exists=if_exists, chunksize=chunksize)
        return
