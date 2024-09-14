"""
Created on 2024年09月05日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks

数据存储模块
"""
import time
from datetime import datetime

from Module import MySQL_Database, tushare_api, mysql_data_processing as mdp
from config import QUANTIZER_DATABASE, ADJFACTOR_DATABASE, STOCK_BASIC_NAME

# 若程序报错则延时循环执行：sec
TIME = 5


# ################ 通过日期循环日线行情数据 # ################
def get_daily_stocks(db, ts_code, tables):
    """
    循环tushare网站上的最新stock_basic中的ts_code，将数据表中所有股票的最新日期提取出来，
    再通过日期获取数据，然后存储到对应的股票数据表中
    :param db: 所要操作的数据库：
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
        tbname = mdp.tscode_to_tbname(tscode)

        if tbname in tables:
            update_stocks_list.append(tscode)
            last_date = db.read_table_last_date(tbname)  # 获取该股票最新一天的日期

            # 更新字典，将日期作为键，股票代码作为值
            if last_date not in last_date_dict:
                last_date_dict.update({last_date: [tscode]})
            else:
                last_date_dict[last_date].append(tscode)

            # 根据数据表中是否有最新数据来进行获取并存储
            if last_date is not None:
                # 该股票在数据表中有最新日期的数据，直接根据日期获取网站上的日线行情
                df = tushare_api.get_trade_date_data(tscode, start_date=last_date)
                reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                if len(reverse_df) > 1:
                    db.write_data(reverse_df[1:], tbname)
                    pass
                # else:
                #     print('该股票目前为最新数据')
                #     pass
            else:
                # 该股票在数据表中无最新日期的数据，获取网站上该股票的所有日线行情
                df = tushare_api.get_daily_data(tscode)
                reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                db.write_data(reverse_df, tbname)
        else:
            # 该股票不在数据库中，直接获取网站上该股票的所有日线行情
            new_stocks_list.append(tscode)
            df = tushare_api.get_daily_data(tscode)
            reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
            db.write_data(reverse_df, tbname)

        mdp.view_bar(count, len(ts_code))  # 实时刷新进度条

    # 股票日期更新情况
    print('\n')
    for ld_key in last_date_dict.keys():
        if ld_key is None:
            print(f'目前{last_date_dict[ld_key]}这些股票尚未更新或刚上市尚未开盘')
        else:
            print(f'更新至{ld_key}日期的股票如下：{last_date_dict[ld_key]}')

    et = datetime.now()
    print('\n')
    # if len(update_stocks_list) != 0:
    #     print(f'本次更新股票：{update_stocks_list}')
    if len(new_stocks_list) != 0:
        print('本次新增股票:\n', new_stocks_list)
    print('%d stocks are imported into the database.' % count)
    print('It takes {} to get stocks!'.format(et - st))


def get_store_quantizer_data(db, table_df, table_lists):
    """
    获取股票每日技术面因子（量化因子）相关数据并存储进量化因子数据库中
    :param db: 所要操作的数据库：'quantizer_db'
    :param table_df:股票列表：stock_basic
    :param table_lists:数据库中所有数据表的列表
    :return:
    """
    count = 0
    for stock_code in table_df.ts_code:
        try:
            table_name = mdp.tscode_to_tbname(stock_code)
            if table_name not in table_lists:
                # 调用api，并将数据存储到数据库中
                quantizer_df = tushare_api.stk_factor(ts_code=stock_code)
                reverse_quantizer_df = quantizer_df[::-1]
                db.write_data(reverse_quantizer_df, table_name)
                count += 1
            else:
                # 读取数据表中最后一个日期，再将数据存储到数据库中
                df = db.read_data(table_name)
                last_date = df.trade_date.array[-1]  # 获取数据表中最后一个日期（即最新的日期）
                quantizer_df = tushare_api.stk_factor(ts_code=stock_code, start_date=last_date)
                if len(quantizer_df) > 1:
                    reverse_quantizer_df = quantizer_df[::-1]
                    db.write_data(reverse_quantizer_df[1:], table_name)
                count += 1
            mdp.view_bar(count, len(table_lists))
        except Exception as e:
            print(f'{e}\n延迟{TIME}s')
            time.sleep(TIME)
            continue
    print(f'共存储{count}次')


def get_store_adjfactor_data(db, table_df, table_lists):
    """
    获取复权因子相关数据并存储进复权因子数据库中
    :param db: 所要操作的数据库：'adjfactor_db'
    :param table_df:股票列表：stock_basic
    :param table_lists:数据库中所有数据表的列表
    :return:
    """
    count = 0
    for stock_code in table_df.ts_code:
        try:
            table_name = mdp.tscode_to_tbname(stock_code)
            if table_name not in table_lists:
                # 调用api，并将数据存储到数据库中
                quantizer_df = tushare_api.adj_factor(ts_code=stock_code)
                reverse_quantizer_df = quantizer_df[::-1]
                db.write_data(reverse_quantizer_df, table_name)
                count += 1
            else:
                # 读取数据表中最后一个日期，再将数据存储到数据库中
                df = db.read_data(table_name)
                last_date = df.trade_date.array[-1]  # 获取数据表中最后一个日期（即最新的日期）
                quantizer_df = tushare_api.adj_factor(ts_code=stock_code, start_date=last_date)
                if len(quantizer_df) > 1:
                    reverse_quantizer_df = quantizer_df[::-1]
                    db.write_data(reverse_quantizer_df[1:], table_name)
                count += 1
            mdp.view_bar(count, len(table_lists))
        except Exception as e:
            print(f'{e}\n延迟{TIME}s')
            time.sleep(TIME)
            continue
    print(f'共存储{count}次')


def main_get_store_data():
    # 0.选择需要操作的数据库名称
    database_name = ADJFACTOR_DATABASE

    # 1.先从存储日线行情的数据库中获取所有股票列表
    db = MySQL_Database.MySQLDatabaseOperations()
    table_df = db.read_data(STOCK_BASIC_NAME)

    # 2.再建立存储含有量化/复权因子数据的数据库
    db_ = MySQL_Database.MySQLDatabaseOperations(database=database_name)
    table_lists = db_.show_tables(database=database_name)

    if database_name == QUANTIZER_DATABASE:
        # 3.获取量化因子相关数据并存储进量化因子数据库中
        get_store_quantizer_data(db_, table_df, table_lists)
    elif database_name == ADJFACTOR_DATABASE:
        # 3.获取复权因子相关数据并存储进复权因子数据库中
        get_store_adjfactor_data(db_, table_df, table_lists)


if __name__ == '__main__':
    print('==========%s==========' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    main_get_store_data()
    print('==========%s==========' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('Done!!!')
