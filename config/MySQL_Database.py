import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from config import username, password, host, port, database, cuu


class MySQLDatabaseOperations:
    """
    数据库操作
    """

    def __init__(self):
        # 创建数据库连接
        self.engine_ts = create_engine('mysql://%s:%s@%s:%s/%s?%s' % (username, password, host, port, database, cuu))
        pass

    # =============== 新建数据库 ===============
    def create_mysql_database(self, database=database):
        """
        检查数据库是否存在，不存在则新建数据库
        :return: 若不存在，则返回新建数据库的链接；否则无返回值，为默认数据库
        """
        self.engine_ts = create_engine('mysql://%s:%s@%s:%s/%s?%s' % (username, password, host, port, database, cuu))
        if not database_exists(self.engine_ts.url):
            print(f'{database}数据库不存在，新建数据库链接：{self.engine_ts.url}')
            create_database(self.engine_ts.url)
        else:
            print(f'{database}数据库已存在，后续操作将在该数据库下进行')
        return self.engine_ts

    # =============== 从数据库读取数据 ===============
    def show_tables(self):
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

    def read_detail_data(self, df):
        """
            读取dataframe中具体的数据
            :param df:dataframe格式的数据
            :return:
            """
        trade_date = df.trade_date.values
        open = df.open.values
        high = df.high.values
        low = df.low.values
        close = df.close.values
        pre_close = df.pre_close.values
        change = df.change.values
        pct_chg = df.pct_chg.values
        vol = df.vol.values
        amount = df.amount.values

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

    # ################ 向数据库存储数据 # ################
    def write_data(self, dataframe, stocks_data):
        """
        将给定的df数据存入数据表中
        :param dataframe:所需存入的df数据，dataframe
        :param stocks_data:存入表中的名称，str
        :return:
        """
        dataframe.to_sql(stocks_data, self.engine_ts, index=False, if_exists='append', chunksize=5000)
        return

