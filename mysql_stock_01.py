"""
Created on 2022年09月17日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks

股票数据接口
@website：https://tushare.pro/
本文件只需使用基础积分（120）即可
"""
import time
import argparse
from datetime import datetime, timedelta

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine

from TOKEN_ID import TOKEN
from tushare_api import trade_cal, stock_mx, suspend_d, bak_basic, bak_daily
from mysql_data_processing import view_bar, tscode_to_tbname

local_datetime = time.strftime('%Y%m%d')
delay60 = timedelta(seconds=60)

# 接口调用
# pro.stock_basic()：接口每小时只能调用一次
# pro.daily()：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
# pro.trade_cal()：需2000积分
stock_basic_ = None  # TuShare中的stock_basic接口：'L'为调用上市股票列表接口，'D'为调用退市股票列表接口；None为不调用接口

# 数据表名称
stock_table_name = 'all_stock_basic'
delisted_stock_tbname = 'all_delisted_stock'

# 初始化pro接口
pro = ts.pro_api(TOKEN)

# 初始化数据库
username = 'root'
password = '123456'
host = '127.0.0.1'
port = '3306'
database = 'stock_databases_01'
cuu = 'charset=utf8&use_unicode=1'
engine_ts = create_engine('mysql://%s:%s@%s:%s/%s?%s' % (username, password, host, port, database, cuu))


class MySQLDaily:
    def __init__(self):
        pass


class TuShareStock:
    def __init__(self):
        """
        获取stock_basic，并根据参数选择将数据是否储存到数据表中
        stock_basic_:True，调用stock_basic接口；False，不调用该接口【该接口每小时只能调用一次】

        输入参数：
        exchange:交易所 SSE上交所 SZSE深交所 BSE北交所
        list_status:上市状态 L上市 D退市 P暂停上市，默认是L

        输出参数：
        fields:
        名称	    类型	默认显示	描述
        ts_code	    str	Y	TS代码
        symbol	    str	Y	股票代码
        name	    str	Y	股票名称
        area	    str	Y	地域
        industry	str	Y	所属行业
        fullname	str	N	股票全称
        enname	    str	N	英文全称
        cnspell	    str	N	拼音缩写
        market	    str	Y	市场类型（主板/创业板/科创板/CDR）
        exchange	str	N	交易所代码
        curr_type	str	N	交易货币
        list_status	str	N	上市状态 L上市 D退市 P暂停上市
        list_date	str	Y	上市日期
        """
        self.stock_basic_API = stock_basic_
        self.database_name = database
        self.stock_basic_name = stock_table_name
        self.delisted_stock_name = delisted_stock_tbname

        # 【20240702】以下函数调用了pro.stock_basic()接口，每小时只能调用一次
        # TODO 以下调用两次的stock_basic可以合并成一个，利用list_status来调用不同的stock_basic以此实现不同的数据获取，
        #  但所造成的影响就是，这样会改变现有的数据表结构，如下：
        """
        # 根据不同的需求，选取不同的功能，例如API为'L'则进行“上市的股票列表”获取，API为'D'则进行“退市的股票列表”获取
        if self.stock_basic_API == 'L':
            self.stock_name = stock_table_name
        elif self.stock_basic_API == 'D':
            self.stock_name = delisted_stock_tbname
        """

        if self.stock_basic_API == 'L':
            # Exception: 抱歉，您每天最多访问该接口5次
            self.stocks_list = pro.stock_basic(exchange='', list_status='L',
                                               fields='ts_code, symbol, name, area, industry, '
                                                      'fullname, market, exchange, list_date')
        elif self.stock_basic_API == 'D':
            # [Exception: 抱歉，您每分钟最多访问该接口1次，权限的具体详情访问：https://tushare.pro/document/1?doc_id=108。]
            self.delisted_stock_list = pro.stock_basic(list_status='D',
                                                       fields='ts_code, symbol, name, fullname, market,  '
                                                              ' exchange, list_status, list_date, delist_date')
        else:
            print(f'不调用stock_basic接口，股票代码直接从数据库{self.database_name}的{self.stock_basic_name}表中获取')

    def write_stock_list(self):
        """
        将从tushare网站获取的stock_basic写入MySQL数据库的"all_stock_basic"表中
        :return:
        """
        # self.stocks_list.to_sql('all_stock_basic', engine_ts, index=False, if_exists='append', chunksize=5000)
        self.stocks_list.to_sql(self.stock_basic_name, engine_ts, index=False, if_exists='replace')

    def write_delisted_stock_list(self):
        """
        将从tushare网站获取的已经退市的stock_basic写入MySQL数据库的"delisted_stock"表中
        :return:
        """
        self.delisted_stock_list.to_sql(self.delisted_stock_name, engine_ts, index=False, if_exists='replace')

    def get_ts_code(self):
        """
        从stock_list中获取ts_code
        :return: ts_code
        """
        ts_code = self.stocks_list.ts_code
        return ts_code


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


# ################ 参数定义 # ################
def init_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', type=str, default='',
                        help='function=delisted_stock/suspend_d/stock_mx/bak_basic/bak_daily')
    return parser.parse_args()


args = init_arg()


# ################ 从接口获取数据 # ################
# 以下函数调用了pro.daily()接口
def get_daily_data(ts_code):
    """
    根据股票的ts_code，获取股票的每日数据
    pro.daily：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
    :param ts_code:具体股票的ts_code，str
    :return:
    """
    dataframe = pro.daily(ts_code=ts_code)
    return dataframe


def get_trade_date_data(ts_code, trade_date='', start_date=''):
    """
    A股日线行情
    根据股票的ts_code，获取该股票的交易日数据或起始交易日数据
    其中参数，trade_date优先级高于start_date，即若trade_date不为空的话，即便start_date有日期也无效
    :param ts_code: 具体股票的ts_code，str
    :param trade_date: 交易日期，只获取该交易日期的数据
    :param start_date: 开始日期，获取从该日期开始，直到程序运行当天（交易日）或到结束日期为止的所有数据
    :return:
    """
    dataframe = pro.daily(**{
        "ts_code": ts_code,
        "trade_date": trade_date,
        "start_date": start_date,
        "end_date": "",
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"])
    return dataframe


# ################ 向数据库存储数据 # ################
def write_data(dataframe, stocks_data):
    """
    将给定的df数据存入数据表中
    :param dataframe:所需存入的df数据，dataframe
    :param stocks_data:存入表中的名称，str
    :return:
    """
    # dataframe.to_sql(stocks_data, engine_ts, index=False, if_exists='append', chunksize=10000)
    dataframe.to_sql(stocks_data, engine_ts, index=False, if_exists='append', chunksize=5000)
    return


# ################ 从数据库读取数据 # ################
def read_data(table_name):
    """
    根据表名，读取表中的数据
    :param table_name: 表名
    :return: 表中数据
    """
    # sql = "SELECT * FROM {tb_name} LIMIT 20".format(tb_name=table_name)
    sql = "SELECT * FROM {tb_name}".format(tb_name=table_name)
    dataframe = pd.read_sql_query(sql, engine_ts)
    return dataframe


def read_table_last_date(table_name):
    """
    获取股票日线行情表中最新的日期
    :param table_name:
    :return:
    """
    sql = "SELECT max(trade_date) FROM {tb_name}".format(tb_name=table_name)
    dataframe = pd.read_sql_query(sql, engine_ts)
    return dataframe.values[0][0]


def show_tables():
    """
    获取数据库中已有的表名
    :return:
    """
    sql = "select table_name from information_schema.tables where table_schema='{db_name}'".format(db_name=database)
    dataframe = pd.read_sql_query(sql, engine_ts)

    table_name_list = dataframe.TABLE_NAME.to_list()
    return table_name_list


# ################ stock_basic数据表相操作 # ################
def stock_basic_save_into_db(ts_code, tables, ts_stock, sb_name):
    """

    :param ts_code:
    :param tables:
    :param ts_stock:
    :param sb_name:
    :return:
    """
    """
    获取tushare网站的股票数据，并和数据库中的进行对比，再实行存储
    :param ts_code:tushare网站上的stock_basic的数据
    :param tables:MySQL数据库（stock_databases_01库）中所有的数据表
    :return:
    """
    # TODO 整体逻辑需要再思考，如果不需要知道每次新增哪些股票，则可以整体全部replace
    # ts_stock = TuShareStock()
    # sb_name = ts_stock.stock_basic_name  # 数据表all_stock_basic
    if sb_name in tables:
        read_df = read_data(sb_name)  # 读取all_stock_basic表中的数据
        if len(ts_code) == len(read_df):
            if len(set(ts_code == read_df.ts_code)) != 1:
                # TODO 当数据表中的股票个数和接口获取的股票支数相同，会出现两种情况，
                #  一种是没有新增股票个数，另一种是新增了股票但也退市了股票且新增的股票个数和退市的股票个数相等，
                #  该判断中所涉及的是第二种情况，判断条件需重新设计
                print("The number of stocks hasn't changed but stock detail info has changed!")
            else:
                print('%s 无新增股票' % time.strftime('%Y-%m-%d'))
        else:
            # TODO 等有新增数据再进行调整
            ts_stock.write_stock_list()
            print('有新增股票数据，已存储到%s' % sb_name)
    else:
        # new_table = pd.DataFrame(data=None,
        #                          columns=['ts_code', 'symbol', 'name', 'area', 'industry', 'fullname', 'market',
        #                                   'exchange', 'list_date'])
        # write_data(new_table, sb_name)
        ts_stock.write_stock_list()
        print('数据表%s不在数据库中，已将[https://tushare.pro/]的数据存储到数据库中' % sb_name)


# ################ 各个股票的数据表相操作 # ################
# 暂未使用到该函数


# ################ 通过日期循环日线行情数据 # ################
def get_daily_stocks(ts_code, tables):
    """
        循环tushare网站上的最新stock_basic中的ts_code，将数据表中所有股票的最新日期提取出来，
        再通过日期获取数据，然后存储到对应的股票数据表中
        :param ts_code:数据库中all_stock_basic数据表中的ts_code
        :param tables:数据库中所有的数据表（包含股票日线行情表和其他“股票列表”等所有的数据表）
        :return:
    """
    count = 0
    new_stocks_list = []  # 新增股票列表
    update_stocks_list = []  # 更新股票列表

    st = datetime.now()

    # 循环ts_code中的股票，进行判断并添加日线行情到数据库中
    last_date_dict = {}
    for tscode in ts_code:
        count += 1
        tbname = tscode_to_tbname(tscode)

        if tbname in tables:
            update_stocks_list.append(tscode)
            last_date = read_table_last_date(tbname)  # 获取该股票最新一天的日期

            # 更新字典，将日期作为键，股票代码作为值
            if last_date not in last_date_dict:
                last_date_dict.update({last_date: [tscode]})
            else:
                last_date_dict[last_date].append(tscode)

            # 根据数据表中是否有最新数据来进行获取并存储
            if last_date is not None:
                # 该股票在数据表中有最新日期的数据，直接根据日期获取网站上的日线行情
                df = get_trade_date_data(tscode, start_date=last_date)
                reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                if len(reverse_df) > 1:
                    # write_data(reverse_df[1:], tbname)
                    pass
                else:
                    # print('该股票目前为最新数据')
                    pass
            else:
                # 该股票在数据表中无最新日期的数据，获取网站上该股票的所有日线行情
                df = get_daily_data(tscode)
                reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                # write_data(reverse_df, tbname)
        else:
            # 该股票不在数据库中，直接获取网站上该股票的所有日线行情
            new_stocks_list.append(tscode)
            df = get_daily_data(tscode)
            reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
            # write_data(reverse_df, tbname)

        view_bar(count, len(ts_code))  # 实时刷新进度条

    # 股票日期更新情况
    for ld_key in last_date_dict.keys():
        if ld_key is None:
            print(f'目前{last_date_dict[ld_key]}这些股票尚未更新或刚上市尚未开盘')
        else:
            print(f'更新至{ld_key}日期的股票如下：{last_date_dict[ld_key]}')

    et = datetime.now()
    print('\n')
    if len(update_stocks_list) != 0:
        print(f'本次更新股票：{update_stocks_list}')
    if len(new_stocks_list) != 0:
        print('本次新增股票:\n', new_stocks_list)
    print('%d stocks are imported into the database.' % count)
    print('It takes {} to get stocks!'.format(et - st))


# ================ 查重程序 ==================
def duplicate_checking():
    """
    数据表查重
    :return:
    """
    print('\n开始查重')
    # 获取数据库中已有的表名
    tables = show_tables()  # 数据库中所有的数据表

    tb_list = []
    # param = ''
    for tb_name in tables:
        if tb_name[:2] == 'al' or tb_name[:2] == 'st':
            param = 'ts_code'
        elif tb_name[:2] == 'bj' or tb_name[:2] == 'sh' or tb_name[:2] == 'sz':
            param = 'trade_date'
        else:
            continue

        sql = 'select {0} from {1} group by {0} having count({0})>1'.format(param, tb_name)
        dataframe = pd.read_sql_query(sql, engine_ts)
        if dataframe.values.size != 0:
            tb_list.append(tb_name)

    if len(tb_list) != 0:
        print('重复列表如下：\n', tb_list)
        return tb_list
    else:
        print('数据表均无重复')


# ================ 主程序 ==================
def main():
    print('\n')
    print(f'{"-" * 100}')
    print(f'{" " * 43 + "Program Start" + " " * 44}')
    print(f'{"-" * 100}')
    print('\n')

    # 获取数据库中已有的表名
    tables = show_tables()  # 数据库中所有的数据表

    is_trade = True  # 手动运行
    if is_trade:
        start_time = datetime.now()  # 获取整个程序运行的时间统计

        mysql_stock_list = TuShareStock()
        sb_table_name = mysql_stock_list.stock_basic_name

        if mysql_stock_list.stock_basic_API:
            # 获取TS网站的stock_basic数据并存储到表相关操作
            tscode = mysql_stock_list.get_ts_code()  # 确认调用了stock_basic接口，获取tushare上stock_basic的ts_code
            print(f'stock_basic中股票个数为：{len(tscode)}')

            stock_basic_save_into_db(tscode, tables, mysql_stock_list, sb_table_name)  # 将TS网站获取到的stock_basic存储到数据库中
            print(f'已将TS网站中的stock_basic数据更新到数据库中，共耗时：{datetime.now() - start_time}')
        else:
            sb_df = read_data(sb_table_name)  # 直接读取数据库中stock_basic中数据，且从表中获取tscode
            tscode = sb_df.ts_code
            print(f'数据库中股票个数为：{len(tscode)}')

        # 各个股票的数据表相关操作
        get_daily_stocks(tscode, tables)

        end_time = datetime.now()

        print('=====================%s=======================' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('Starting time is ', start_time)
        print('Ending time is   ', end_time)
        print('It takes {}, the program is finished!'.format(end_time - start_time))
    else:
        print('非交易日')


if __name__ == '__main__':
    main()
