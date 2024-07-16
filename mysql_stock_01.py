"""
Created on 2022年09月17日

@author: Aiden_yang
@website：https://tushare.pro/
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
suspend_d_tbname = 'all_suspend_stock'
stock_mx_tbname = 'all_stock_mx'
# bak_basic_tbname = 'all_bak_basic'
bak_basic_tbname = 'all_bak_basic_20230318'
# bak_daily_tbname = 'all_bak_daily'
bak_daily_tbname = 'all_bak_daily_20230318'

# 初始化pro接口
# TOKEN = ''
pro = ts.pro_api(TOKEN)

# 初始化数据库
username = 'root'
password = '123456'
host = '127.0.0.1'
port = '3306'
database = 'stock_databases_01'
cuu = 'charset=utf8&use_unicode=1'
# engine_ts = create_engine('mysql://root:123456@127.0.0.1:3306/stock_databases?charset=utf8&use_unicode=1')
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


# 以下函数调用了pro.trade_cal()接口
def is_trade_date(cal_date=local_datetime):
    """
    是否为交易日
    :param cal_date: 系统日期
    :return: bool值，是交易日返回True，不是交易日返回False
    """
    dataframe = pro.trade_cal(**{
        "exchange": "",
        "cal_date": cal_date,
        "start_date": "",
        "end_date": "",
        "is_open": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "exchange",
        "cal_date",
        "is_open",
        "pretrade_date"])

    is_open = bool(dataframe.is_open.values[0])
    pre_trade_date = dataframe.pretrade_date.values[0]
    return is_open, pre_trade_date


def gap_date(start_date):
    """
    查询start_date交易日的下一个交易日
    该接口每分钟最多访问60次

    exchange：交易所 SSE上交所 SZSE深交所
    cal_date：日历日期
    start_date：开始日期 （格式：YYYYMMDD 下同）
    end_date：结束日期
    is_open：是否交易 0休市 1交易
    limit：单次返回数据长度
    offset：请求数据的开始位移量

    :param start_date:
    :return:
    """
    dataframe = pro.trade_cal(**{
        "exchange": "",
        "cal_date": "",
        "start_date": start_date,
        "end_date": "",
        "is_open": 1,
        "limit": 2,
        "offset": ""
    }, fields=[
        "exchange",
        "cal_date",
        "is_open",
        "pretrade_date"])

    # ntd = dataframe.values[1][1]  # next trade date
    ntd = dataframe.cal_date.values[1]  # next trade date
    """
    此处会出现报错：index 1 is out of bounds for axis 0 with size 0
    """
    return ntd


def next_trade_date(start_date):
    """
    查询start_date交易日的下一个交易日
    该接口每分钟最多访问60次

    exchange：交易所 SSE上交所 SZSE深交所
    cal_date：日历日期
    start_date：开始日期 （格式：YYYYMMDD 下同）
    end_date：结束日期
    is_open：是否交易 0休市 1交易
    limit：单次返回数据长度
    offset：请求数据的开始位移量

    :param start_date:
    :return:
    """
    dataframe = pro.trade_cal(**{
        "exchange": "",
        "cal_date": "",
        "start_date": start_date,
        "end_date": "",
        "is_open": 1,
        "limit": "",
        "offset": ""
    }, fields=[
        "exchange",
        "cal_date",
        "is_open",
        "pretrade_date"])

    # ntd = dataframe.values[1][1]  # next trade date
    ntd = dataframe.cal_date.values[::-1][1]  # next trade date
    """
    此处会出现报错：index 1 is out of bounds for axis 0 with size 0
    """
    return ntd


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


def write_all_stock(ts_code):
    """
    write whole stock daily data into the database
    :param ts_code: all stock ts_code set
    :return:
    """
    count = 0
    start_time = datetime.now()
    for tsc in ts_code:
        # 将ts_code调整成适合存储到数据库中的表的名称
        tsc_table_name = ''.join(tsc.split('.')[::-1]).lower()

        dataframe = get_daily_data(ts_code=tsc)
        write_data(dataframe[::-1], tsc_table_name)
        count += 1
    end_time = datetime.now()
    print('%d stocks are imported into the database.' % count)
    print('The program is finished!')
    print('Starting time is ', start_time)
    print('Ending time is   ', end_time)
    print('It takes ', (end_time - start_time))


# 暂未使用到以下函数
def write_stock_mx(table_name=stock_mx_tbname):
    """
    # 获取所需股票的动量因子
    :param table_name:
    :return:
    """
    """
    ts_code = ['002749.SZ', '002753.SZ', '002783.SZ', '002789.SZ', '002790.SZ', '002791.SZ', '002792.SZ', '002811.SZ',
               '002818.SZ', '002832.SZ', '002833.SZ', '002845.SZ', '002862.SZ', '002871.SZ', '002875.SZ', '002879.SZ',
               '002881.SZ', '002887.SZ', '002900.SZ', '002923.SZ', '002935.SZ', '002987.SZ', '003009.SZ', '003025.SZ',
               '003029.SZ', '300395.SZ', '300417.SZ', '300445.SZ', '300485.SZ', '300494.SZ', '300499.SZ', '300501.SZ',
               '300511.SZ', '300514.SZ', '300517.SZ', '300528.SZ', '300533.SZ', '300538.SZ', '300547.SZ', '300549.SZ',
               '300550.SZ', '300558.SZ', '300559.SZ', '300560.SZ', '300572.SZ', '300581.SZ', '300587.SZ', '300589.SZ',
               '300594.SZ', '300600.SZ', '300601.SZ', '300610.SZ', '300634.SZ', '300642.SZ', '300650.SZ', '300652.SZ',
               '300653.SZ', '300673.SZ', '300677.SZ', '300684.SZ', '300698.SZ', '300729.SZ', '300739.SZ', '300743.SZ',
               '300745.SZ', '300753.SZ', '300774.SZ', '300787.SZ', '300813.SZ', '300814.SZ', '300834.SZ', '300836.SZ',
               '300837.SZ', '300838.SZ', '300839.SZ', '300844.SZ', '300854.SZ', '300857.SZ', '300858.SZ', '300860.SZ',
               '300866.SZ', '300884.SZ', '300887.SZ', '300888.SZ', '300889.SZ', '300890.SZ', '300891.SZ', '300892.SZ',
               '300893.SZ', '300895.SZ', '300896.SZ', '300897.SZ', '300900.SZ', '300902.SZ', '300906.SZ', '300907.SZ',
               '300908.SZ', '300910.SZ', '300911.SZ', '300912.SZ', '300913.SZ', '300915.SZ', '300916.SZ', '300918.SZ',
               '300919.SZ', '300920.SZ', '300921.SZ', '300922.SZ', '300923.SZ', '300926.SZ', '300927.SZ', '300928.SZ',
               '300929.SZ', '300930.SZ', '300931.SZ', '300933.SZ', '300942.SZ', '300947.SZ', '300951.SZ', '300952.SZ',
               '300955.SZ', '300956.SZ', '300957.SZ', '300958.SZ', '300959.SZ', '300964.SZ', '300965.SZ', '300967.SZ',
               '300968.SZ', '300969.SZ', '300970.SZ', '300971.SZ', '300972.SZ', '300973.SZ', '300976.SZ', '300977.SZ',
               '300978.SZ', '300980.SZ', '300981.SZ', '300982.SZ', '300983.SZ', '300984.SZ', '300985.SZ', '300986.SZ',
               '300988.SZ', '300989.SZ', '300990.SZ', '300991.SZ', '300993.SZ', '300995.SZ', '300996.SZ', '300997.SZ',
               '300998.SZ', '300999.SZ', '301000.SZ', '301001.SZ', '301002.SZ', '301003.SZ', '301004.SZ', '301005.SZ',
               '301007.SZ', '301008.SZ', '301009.SZ', '301010.SZ', '301011.SZ', '301013.SZ', '301017.SZ', '301019.SZ',
               '301022.SZ', '301023.SZ', '301026.SZ', '301028.SZ', '301029.SZ', '301030.SZ', '301032.SZ', '301033.SZ',
               '301036.SZ', '301037.SZ', '301038.SZ', '301039.SZ', '301040.SZ', '301041.SZ', '301042.SZ', '301043.SZ',
               '301045.SZ', '301046.SZ', '301047.SZ', '301049.SZ', '301050.SZ', '301051.SZ', '301052.SZ', '301053.SZ',
               '301055.SZ', '301056.SZ', '301057.SZ', '301058.SZ', '301059.SZ', '301061.SZ', '301063.SZ', '301066.SZ',
               '301067.SZ', '301069.SZ', '301070.SZ', '301072.SZ', '301073.SZ', '301075.SZ', '301076.SZ', '301077.SZ',
               '301078.SZ', '301079.SZ', '301080.SZ', '301081.SZ', '301082.SZ', '301085.SZ', '301086.SZ', '301087.SZ',
               '301088.SZ', '301091.SZ', '301093.SZ', '301095.SZ', '301096.SZ', '301100.SZ', '301102.SZ', '301103.SZ',
               '301105.SZ', '301106.SZ', '301107.SZ', '301108.SZ', '301110.SZ', '301111.SZ', '301112.SZ', '301113.SZ',
               '301115.SZ', '301116.SZ', '301118.SZ', '301119.SZ', '301120.SZ', '301121.SZ', '301122.SZ', '301123.SZ',
               '301125.SZ', '301126.SZ', '301127.SZ', '301130.SZ', '301131.SZ', '301132.SZ', '301135.SZ', '301136.SZ',
               '301137.SZ', '301139.SZ', '301148.SZ', '301150.SZ', '301151.SZ', '301152.SZ', '301153.SZ', '301155.SZ',
               '301156.SZ', '301159.SZ', '301160.SZ', '301161.SZ', '301162.SZ', '301163.SZ', '301165.SZ', '301167.SZ',
               '301169.SZ', '301171.SZ', '301175.SZ', '301176.SZ', '301177.SZ', '301178.SZ', '301179.SZ', '301180.SZ',
               '301182.SZ', '301183.SZ', '301185.SZ', '301186.SZ', '301188.SZ', '301189.SZ', '301190.SZ', '301191.SZ',
               '301193.SZ', '301195.SZ', '301196.SZ', '301197.SZ', '301198.SZ', '301199.SZ', '301200.SZ', '301205.SZ',
               '301206.SZ', '301207.SZ', '301208.SZ', '301211.SZ', '301213.SZ', '301215.SZ', '301216.SZ', '301217.SZ',
               '301218.SZ', '301219.SZ', '301220.SZ', '301221.SZ', '301223.SZ', '301226.SZ', '301227.SZ', '301228.SZ',
               '301230.SZ', '301231.SZ', '301233.SZ', '301234.SZ', '301235.SZ', '301236.SZ', '301237.SZ', '301238.SZ',
               '301239.SZ', '301248.SZ', '301255.SZ', '301256.SZ', '301257.SZ', '301258.SZ', '301259.SZ', '301260.SZ',
               '301263.SZ', '301265.SZ', '301266.SZ', '301267.SZ', '301268.SZ', '301269.SZ', '301276.SZ', '301277.SZ',
               '301280.SZ', '301282.SZ', '301283.SZ', '301285.SZ', '301286.SZ', '301289.SZ', '301290.SZ', '301296.SZ',
               '301297.SZ', '301298.SZ', '301299.SZ', '301300.SZ', '301301.SZ', '301302.SZ', '301303.SZ', '301306.SZ',
               '301308.SZ', '301309.SZ', '301311.SZ', '301312.SZ', '301313.SZ', '301316.SZ', '301317.SZ', '301318.SZ',
               '301321.SZ', '301322.SZ', '301326.SZ', '301327.SZ', '301328.SZ', '301330.SZ', '301331.SZ', '301333.SZ',
               '301335.SZ', '301338.SZ', '301339.SZ', '301349.SZ', '301356.SZ', '301358.SZ', '301359.SZ', '301361.SZ',
               '301365.SZ', '301366.SZ', '301368.SZ', '301369.SZ', '301373.SZ', '301379.SZ', '301380.SZ', '301388.SZ',
               '301389.SZ', '301391.SZ', '301396.SZ', '301398.SZ', '301408.SZ', '600941.SH', '601330.SH', '601598.SH',
               '601658.SH', '601811.SH', '601858.SH', '601865.SH', '601878.SH', '603013.SH', '603020.SH', '603036.SH',
               '603037.SH', '603041.SH', '603042.SH', '603043.SH', '603055.SH', '603059.SH', '603068.SH', '603081.SH',
               '603087.SH', '603089.SH', '603093.SH', '603101.SH', '603115.SH', '603121.SH', '603127.SH', '603129.SH',
               '603138.SH', '603139.SH', '603167.SH', '603178.SH', '603180.SH', '603181.SH', '603185.SH', '603186.SH',
               '603187.SH', '603197.SH', '603199.SH', '603200.SH', '603208.SH', '603212.SH', '603218.SH', '603228.SH',
               '603229.SH', '603232.SH', '603258.SH', '603260.SH', '603266.SH', '603267.SH', '603277.SH', '603278.SH',
               '603279.SH', '603289.SH', '603298.SH', '603301.SH', '603303.SH', '603313.SH', '603319.SH', '603332.SH',
               '603337.SH', '603356.SH', '603359.SH', '603363.SH', '603379.SH', '603380.SH', '603385.SH', '603387.SH',
               '603392.SH', '603408.SH', '603444.SH', '603527.SH', '603529.SH', '603530.SH', '603535.SH', '603536.SH',
               '603568.SH', '603577.SH', '603585.SH', '603586.SH', '603590.SH', '603595.SH', '603596.SH', '603605.SH',
               '603619.SH', '603629.SH', '603630.SH', '603639.SH', '603650.SH', '603662.SH', '603663.SH', '603666.SH',
               '603668.SH', '603669.SH', '603676.SH', '603679.SH', '603683.SH', '603689.SH', '603697.SH', '603706.SH',
               '603707.SH', '603709.SH', '603713.SH', '603719.SH', '603727.SH', '603737.SH', '603739.SH', '603755.SH',
               '603767.SH', '603790.SH', '603801.SH', '603813.SH', '603815.SH', '603817.SH', '603826.SH', '603829.SH',
               '603856.SH', '603860.SH', '603866.SH', '603867.SH', '603868.SH', '603879.SH', '603882.SH', '603897.SH',
               '603899.SH', '603906.SH', '603908.SH', '603917.SH', '603929.SH', '603931.SH', '603933.SH', '603937.SH',
               '603938.SH', '603950.SH', '603963.SH', '603966.SH', '603967.SH', '603968.SH', '603970.SH', '603983.SH',
               '603992.SH', '605003.SH', '605058.SH', '605089.SH', '605099.SH', '605100.SH', '605108.SH', '605111.SH',
               '605136.SH', '605179.SH', '605180.SH', '605186.SH', '605259.SH', '605277.SH', '605298.SH', '689009.SH']
    """

    trade_date0 = trade_cal(start_date='20140102', end_date=datetime.now().date().strftime('%Y%m%d'), is_open='1')
    trade_date = trade_date0.cal_date.values[::-1]

    count = 0
    st = datetime.now()
    for td in trade_date:
        count += 1
        df = stock_mx(trade_date=td)
        df.to_sql(table_name, engine_ts, index=False, if_exists='append')
        print('%d：%s这天的动量因子数量为%d，目前耗时：%s' % (count, td, len(df.values), datetime.now() - st))
    print('Done!')


def write_suspend_d(table_name=suspend_d_tbname):
    """
    # 获取所有停牌的股票的记录
    :param table_name:
    :return:
    """
    count = 0
    count1 = 0

    start_date = ['19990101', '20000101', '20010101', '20010710', '20020101', '20020618', '20021218', '20030101',
                  '20030616', '20031111', '20040101', '20040531', '20041028', '20050101', '20050630', '20051018',
                  '20051212', '20060101', '20060223', '20060327', '20060421', '20060524', '20060623', '20060728',
                  '20060925', '20061213', '20070101', '20070308', '20070427', '20070625', '20070829', '20071030',
                  '20071225', '20080101', '20080303', '20080422', '20080613', '20080903', '20081222', '20090101',
                  '20090514', '20090908', '20100101', '20100519', '20100913', '20110101', '20110420', '20110708',
                  '20111028', '20120101', '20120410', '20120619', '20121109', '20130101', '20130507', '20130725',
                  '20130930', '20131206', '20140101', '20140304', '20140417', '20140526', '20140630', '20140730',
                  '20140901', '20141008', '20141106', '20141204', '20141231', '20150101', '20150130', '20150305',
                  '20150330', '20150420', '20150511', '20150528', '20150612', '20150630', '20150709', '20150715',
                  '20150727', '20150807', '20150821', '20150908', '20150922', '20151014', '20151029', '20151117',
                  '20151208', '20151231', '20160101', '20160129', '20160302', '20160328', '20160419', '20160512',
                  '20160603', '20160630', '20160726', '20160825', '20160927', '20161104', '20161207', '20170101',
                  '20170213', '20170315', '20170417', '20170515', '20170612', '20170706', '20170801', '20170828',
                  '20170926', '20171103', '20171206', '20180101', '20180201', '20180302', '20180328', '20180426',
                  '20180529', '20180628', '20180809', '20181025', '20190101', '20200101', '20200825', '20210101',
                  '20210713', '20220101', '20220606', '20220905', '20230101']
    end_date = ['19991231', '20001231', '20010709', '20011231', '20020617', '20021217', '20021231', '20030615',
                '20031110', '20031231', '20040530', '20041027', '20041231', '20050629', '20051017', '20051211',
                '20051231', '20060222', '20060326', '20060420', '20060523', '20060622', '20060727', '20060924',
                '20061212', '20061231', '20070307', '20070426', '20070624', '20070828', '20071029', '20071224',
                '20071231', '20080302', '20080421', '20080612', '20080902', '20081221', '20081231', '20090513',
                '20090907', '20091231', '20100518', '20100912', '20101231', '20110419', '20110707', '20111027',
                '20111231', '20120409', '20120618', '20121108', '20121231', '20130506', '20130724', '20130929',
                '20131205', '20131231', '20140303', '20140416', '20140525', '20140629', '20140729', '20140829',
                '20141007', '20141105', '20141203', '20141230', '20141231', '20150129', '20150304', '20150329',
                '20150419', '20150510', '20150527', '20150611', '20150629', '20150708', '20150714', '20150726',
                '20150806', '20150820', '20150907', '20150921', '20151013', '20151028', '20151116', '20151207',
                '20151230', '20151231', '20160128', '20160301', '20160327', '20160418', '20160511', '20160602',
                '20160629', '20160725', '20160824', '20160926', '20161103', '20161206', '20161231', '20170212',
                '20170314', '20170416', '20170514', '20170611', '20170705', '20170731', '20170827', '20170925',
                '20171102', '20171205', '20171231', '20180131', '20180301', '20180327', '20180425', '20180528',
                '20180627', '20180808', '20181024', '20181231', '20191231', '20200824', '20201231', '20210712',
                '20211231', '20220605', '20220904', '20221231', '20231231']
    st = datetime.now()
    t1 = datetime.now()
    for dt0, dt1 in zip(start_date, end_date):
        count1 += 1
        dataframe = suspend_d(suspend_type='S', start_date=dt0, end_date=dt1)
        dataframe.to_sql(table_name, engine_ts, index=False, if_exists='append')

        if len(dataframe.values) > 4999:
            count += 1
            print('超过5000条的日期：%s-%s' % (dt0, dt1))

        loop = 50  # 每loop次循环算作一轮，默认loop=50
        if count1 % loop == 0:
            t2 = datetime.now()
            if (t2 - t1) < delay60:
                delay_time = (delay60 - (t2 - t1)).seconds
                time.sleep(delay_time + 1)
                print('延时：', delay_time + 1)
            print('第%d轮前%d次循环累计耗时：%s' % (count1 // loop + 1, count1, datetime.now() - t1))
            t1 = datetime.now()
        else:
            print('第%d轮前%d次循环累计耗时：%s' % (count1 // loop + 1, count1, datetime.now() - t1))
    print('达限数量：%d，总耗时：%s' % (count, datetime.now() - st))

    """
    st = datetime.now()
    t1 = datetime.now()
    for i in range(0, len(ts_code), 10):
        count1 += 1
        tscode = ','.join(ts_code.values[i:i + 10])
        dataframe = suspend_d(ts_code=tscode, suspend_type='S')
        dataframe.to_sql(table_name, engine_ts, index=False, if_exists='append')

        if len(dataframe.values) >= 4999:
            count += 1
            print('超过5000条的股票代码：%s' % tscode)
        else:
            print('停牌总次数：%d，本轮目前耗时：%s —— 股票组合 [%s]' % (len(dataframe.values), datetime.now() - t1, tscode))

        if count1 % 40 == 0:
            t2 = datetime.now()
            print('调用%d次接口耗时：%s' % (count1, t2 - st))
            if (t2 - t1) < delay60:
                delay_time = (delay60 - (t2 - t1)).seconds
                time.sleep(delay_time)
                print('本轮耗时：%s，延时：%s' % (t2 - t1, delay_time))
            else:
                print('本轮耗时：%s' % (t2 - t1))
            t1 = datetime.now()
            print('\n')
    print('停牌股票的数量：%d，耗时：%s' % (count, datetime.now() - st))
    """
    print('DONE!')


def write_bak_basic():
    """
    # 获取所需股票的备用列表
    :return:
    """
    print('日期：', datetime.now())
    ts_code = ['002749.SZ', '002753.SZ', '002783.SZ', '002789.SZ', '002790.SZ', '002791.SZ', '002792.SZ', '002811.SZ',
               '002818.SZ', '002832.SZ', '002833.SZ', '002845.SZ', '002862.SZ', '002871.SZ', '002875.SZ', '002879.SZ',
               '002881.SZ', '002887.SZ', '002900.SZ', '002923.SZ', '002935.SZ', '002987.SZ', '003009.SZ', '003025.SZ',
               '003029.SZ', '300395.SZ', '300417.SZ', '300445.SZ', '300485.SZ', '300494.SZ', '300499.SZ', '300501.SZ',
               '300511.SZ', '300514.SZ', '300517.SZ', '300528.SZ', '300533.SZ', '300538.SZ', '300547.SZ', '300549.SZ',
               '300550.SZ', '300558.SZ', '300559.SZ', '300560.SZ', '300572.SZ', '300581.SZ', '300587.SZ', '300589.SZ',
               '300594.SZ', '300600.SZ', '300601.SZ', '300610.SZ', '300634.SZ', '300642.SZ', '300650.SZ', '300652.SZ',
               '300653.SZ', '300673.SZ', '300677.SZ', '300684.SZ', '300698.SZ', '300729.SZ', '300739.SZ', '300743.SZ',
               '300745.SZ', '300753.SZ', '300774.SZ', '300787.SZ', '300813.SZ', '300814.SZ', '300836.SZ', '300837.SZ',
               '300838.SZ', '300839.SZ', '300844.SZ', '300854.SZ', '300857.SZ', '300858.SZ', '300860.SZ', '300866.SZ',
               '300884.SZ', '300887.SZ', '300888.SZ', '300889.SZ', '300890.SZ', '300891.SZ', '300892.SZ', '300893.SZ',
               '300895.SZ', '300896.SZ', '300897.SZ', '300900.SZ', '300902.SZ', '300906.SZ', '300907.SZ', '300908.SZ',
               '300910.SZ', '300911.SZ', '300912.SZ', '300913.SZ', '300915.SZ', '300916.SZ', '300918.SZ', '300919.SZ',
               '300920.SZ', '300921.SZ', '300922.SZ', '300923.SZ', '300926.SZ', '300927.SZ', '300928.SZ', '300929.SZ',
               '300930.SZ', '300931.SZ', '300933.SZ', '300942.SZ', '300947.SZ', '300951.SZ', '300952.SZ', '300955.SZ',
               '300956.SZ', '300957.SZ', '300958.SZ', '300959.SZ', '300964.SZ', '300965.SZ', '300967.SZ', '300968.SZ',
               '300969.SZ', '300970.SZ', '300971.SZ', '300972.SZ', '300973.SZ', '300976.SZ', '300977.SZ', '300978.SZ',
               '300980.SZ', '300981.SZ', '300982.SZ', '300983.SZ', '300984.SZ', '300985.SZ', '300986.SZ', '300988.SZ',
               '300989.SZ', '300990.SZ', '300991.SZ', '300993.SZ', '300995.SZ', '300996.SZ', '300997.SZ', '300998.SZ',
               '300999.SZ', '301000.SZ', '301001.SZ', '301002.SZ', '301003.SZ', '301004.SZ', '301005.SZ', '301007.SZ',
               '301008.SZ', '301009.SZ', '301010.SZ', '301011.SZ', '301013.SZ', '301017.SZ', '301019.SZ', '301022.SZ',
               '301023.SZ', '301026.SZ', '301028.SZ', '301029.SZ', '301030.SZ', '301032.SZ', '301033.SZ', '301036.SZ',
               '301037.SZ', '301038.SZ', '301039.SZ', '301040.SZ', '301041.SZ', '301042.SZ', '301043.SZ', '301045.SZ',
               '301046.SZ', '301047.SZ', '301049.SZ', '301050.SZ', '301051.SZ', '301052.SZ', '301053.SZ', '301055.SZ',
               '301056.SZ', '301057.SZ', '301058.SZ', '301059.SZ', '301061.SZ', '301063.SZ', '301066.SZ', '301067.SZ',
               '301069.SZ', '301070.SZ', '301072.SZ', '301073.SZ', '301075.SZ', '301076.SZ', '301077.SZ', '301078.SZ',
               '301079.SZ', '301080.SZ', '301081.SZ', '301082.SZ', '301085.SZ', '301086.SZ', '301087.SZ', '301088.SZ',
               '301091.SZ', '301093.SZ', '301096.SZ', '301100.SZ', '301108.SZ', '301111.SZ', '301113.SZ', '301118.SZ',
               '301119.SZ', '301126.SZ', '301127.SZ', '301155.SZ', '301167.SZ', '301169.SZ', '301177.SZ', '301178.SZ',
               '301179.SZ', '301180.SZ', '301182.SZ', '301185.SZ', '301186.SZ', '301188.SZ', '301189.SZ', '301190.SZ',
               '301193.SZ', '301198.SZ', '301199.SZ', '301211.SZ', '301213.SZ', '301221.SZ', '601330.SH', '601598.SH',
               '601658.SH', '601811.SH', '601858.SH', '601865.SH', '601878.SH', '603013.SH', '603020.SH', '603036.SH',
               '603037.SH', '603041.SH', '603042.SH', '603043.SH', '603055.SH', '603059.SH', '603068.SH', '603081.SH',
               '603087.SH', '603089.SH', '603093.SH', '603101.SH', '603115.SH', '603121.SH', '603127.SH', '603129.SH',
               '603138.SH', '603139.SH', '603167.SH', '603178.SH', '603180.SH', '603181.SH', '603185.SH', '603186.SH',
               '603187.SH', '603197.SH', '603199.SH', '603200.SH', '603208.SH', '603212.SH', '603218.SH', '603228.SH',
               '603229.SH', '603232.SH', '603258.SH', '603260.SH', '603266.SH', '603267.SH', '603277.SH', '603278.SH',
               '603279.SH', '603289.SH', '603298.SH', '603301.SH', '603303.SH', '603313.SH', '603319.SH', '603332.SH',
               '603337.SH', '603356.SH', '603359.SH', '603363.SH', '603379.SH', '603380.SH', '603385.SH', '603387.SH',
               '603392.SH', '603408.SH', '603444.SH', '603527.SH', '603529.SH', '603530.SH', '603535.SH', '603536.SH',
               '603568.SH', '603577.SH', '603585.SH', '603586.SH', '603590.SH', '603595.SH', '603596.SH', '603605.SH',
               '603619.SH', '603629.SH', '603630.SH', '603639.SH', '603650.SH', '603662.SH', '603663.SH', '603666.SH',
               '603668.SH', '603669.SH', '603676.SH', '603679.SH', '603683.SH', '603689.SH', '603697.SH', '603706.SH',
               '603707.SH', '603709.SH', '603713.SH', '603719.SH', '603727.SH', '603737.SH', '603739.SH', '603755.SH',
               '603767.SH', '603790.SH', '603801.SH', '603813.SH', '603815.SH', '603817.SH', '603826.SH', '603829.SH',
               '603856.SH', '603860.SH', '603866.SH', '603867.SH', '603868.SH', '603879.SH', '603882.SH', '603897.SH',
               '603899.SH', '603906.SH', '603908.SH', '603917.SH', '603929.SH', '603931.SH', '603933.SH', '603937.SH',
               '603938.SH', '603950.SH', '603963.SH', '603966.SH', '603967.SH', '603968.SH', '603970.SH', '603983.SH',
               '603992.SH', '605003.SH', '605058.SH', '605089.SH', '605099.SH', '605100.SH', '605108.SH', '605111.SH',
               '605136.SH', '605179.SH', '605180.SH', '605186.SH', '605259.SH', '605277.SH', '605298.SH']

    ts_code = ['300972.SZ', '300964.SZ', '300550.SZ', '300494.SZ', '603929.SH', '300912.SZ', '003029.SZ', '300634.SZ',
               '300970.SZ', '300971.SZ', '002987.SZ', '603755.SH', '603042.SH', '300511.SZ', '301179.SZ', '300906.SZ',
               '300995.SZ', '300931.SZ', '300998.SZ', '603081.SH', '601598.SH', '601811.SH', '300837.SZ', '605277.SH',
               '301032.SZ', '603983.SH', '301178.SZ', '002832.SZ', '301001.SZ', '300967.SZ', '003025.SZ', '300996.SZ',
               '603186.SH', '601658.SH', '605179.SH', '300981.SZ', '300902.SZ', '603650.SH', '300918.SZ', '301058.SZ', ]

    ts_code = ['301056.SZ', '605058.SH', '300973.SZ', '603860.SH', '300743.SZ', '301088.SZ', '603444.SH', '603868.SH',
               '301039.SZ', '002818.SZ']

    count = 0
    # df_res = pd.DataFrame()
    st = datetime.now()

    for tscode in ts_code:
        count += 1

        # t1 = datetime.now()  # 调用接口的时间
        df = bak_basic(ts_code=tscode)
        # t2 = datetime.now()
        df.to_sql(bak_basic_tbname, engine_ts, index=False, if_exists='append')
        # df_res = df_res.append(df)
        # t3 = datetime.now()

        print('已存储%d支股票，该股票为%s，目前耗时%s' % (count, tscode, datetime.now() - st))
        time.sleep(30)

        # if count % 2 == 0:
        #     if delay60 > (datetime.now() - t1):  # 表示调用接口两次后所花费的时间<60s
        #         delay_time = (delay60 - (datetime.now() - t1)).seconds + 1
        #         print('延时%ds' % delay_time)
        #         time.sleep(delay_time)
        #         print('目前耗时%s' % (datetime.now() - t1))
        #         # t1 = datetime.now()
        #     else:
        #         pass

    # 将dataframe数据一次性存储到数据库中
    # df_res.to_sql(bak_basic_tbname, engine_ts, index=False, if_exists='append')
    print('DONE!')


def write_bak_daily():
    """
    # 获取所需股票的备用行情
    :return:
    """
    print('日期：', datetime.now())
    ts_done = ['002749.SZ', '002753.SZ', '002783.SZ', '002789.SZ', '002790.SZ', '002791.SZ', '002792.SZ', '002811.SZ',
               '002818.SZ', '002832.SZ', '002833.SZ', '002845.SZ', '002862.SZ', '002871.SZ', '002875.SZ', '002879.SZ',
               '002881.SZ', '002887.SZ', '002900.SZ', '002923.SZ', '002935.SZ', '002987.SZ', '003009.SZ', '003025.SZ',
               '003029.SZ', '300395.SZ', '300417.SZ', '300445.SZ', '300485.SZ', '300494.SZ', '300499.SZ', '300501.SZ',
               '300511.SZ', '300514.SZ', '300517.SZ', '300528.SZ', '300533.SZ', '300538.SZ', '300547.SZ', '300549.SZ',
               '300550.SZ', '300558.SZ', '300559.SZ', '300560.SZ', '300572.SZ', '300581.SZ', '300587.SZ', '300589.SZ',
               '300594.SZ', '300600.SZ', '300601.SZ', '300610.SZ', '300634.SZ', '300642.SZ', '300650.SZ', '300652.SZ',
               '300653.SZ', '300673.SZ', '300677.SZ', '300684.SZ', '300698.SZ', '300729.SZ', '300739.SZ', '300743.SZ',
               '300745.SZ', '300753.SZ', '300774.SZ', '300787.SZ', '300813.SZ', '300814.SZ', '300836.SZ', '300837.SZ',
               '300838.SZ', '300839.SZ', '300844.SZ', '300854.SZ', '300857.SZ', '300858.SZ', '300860.SZ', '300866.SZ',
               '300884.SZ', '300887.SZ', '300888.SZ', '300889.SZ', '300890.SZ', '300891.SZ', '300892.SZ', '300893.SZ',
               '300895.SZ', '300896.SZ', '300897.SZ', '300900.SZ', '300902.SZ', '300906.SZ', '300907.SZ', '300908.SZ',
               '300910.SZ', '300911.SZ', '300912.SZ', '300913.SZ', '300915.SZ', '300916.SZ', '300918.SZ', '300919.SZ',
               '300920.SZ', '300921.SZ', '300922.SZ', '300923.SZ', '300926.SZ', '300927.SZ', '300928.SZ', '300929.SZ',
               '300930.SZ', '300931.SZ', '300933.SZ', '300942.SZ', '300947.SZ', '300951.SZ', '300952.SZ', '300955.SZ',
               '300956.SZ', '300957.SZ', '300958.SZ', '300959.SZ', '300964.SZ', '300965.SZ', '300967.SZ', '300968.SZ',
               '300969.SZ', '300970.SZ', '300971.SZ', '300972.SZ', '300973.SZ', '300976.SZ', ]
    ts_code = ['300977.SZ', '300978.SZ',
               '300980.SZ', '300981.SZ', '300982.SZ', '300983.SZ', '300984.SZ', '300985.SZ', '300986.SZ', '300988.SZ',
               '300989.SZ', '300990.SZ', '300991.SZ', '300993.SZ', '300995.SZ', '300996.SZ', '300997.SZ', '300998.SZ',
               '300999.SZ', '301000.SZ', '301001.SZ', '301002.SZ', '301003.SZ', '301004.SZ', '301005.SZ', '301007.SZ',
               '301008.SZ', '301009.SZ', '301010.SZ', '301011.SZ', '301013.SZ', '301017.SZ', '301019.SZ', '301022.SZ',
               '301023.SZ', '301026.SZ', '301028.SZ', '301029.SZ', '301030.SZ', '301032.SZ', '301033.SZ', '301036.SZ',
               '301037.SZ', '301038.SZ', '301039.SZ', '301040.SZ', '301041.SZ', '301042.SZ', '301043.SZ', '301045.SZ',
               '301046.SZ', '301047.SZ', '301049.SZ', '301050.SZ', '301051.SZ', '301052.SZ', '301053.SZ', '301055.SZ',
               '301056.SZ', '301057.SZ', '301058.SZ', '301059.SZ', '301061.SZ', '301063.SZ', '301066.SZ', '301067.SZ',
               '301069.SZ', '301070.SZ', '301072.SZ', '301073.SZ', '301075.SZ', '301076.SZ', '301077.SZ', '301078.SZ',
               '301079.SZ', '301080.SZ', '301081.SZ', '301082.SZ', '301085.SZ', '301086.SZ', '301087.SZ', '301088.SZ',
               '301091.SZ', '301093.SZ', '301096.SZ', '301100.SZ', '301108.SZ', '301111.SZ', '301113.SZ', '301118.SZ',
               '301119.SZ', '301126.SZ', '301127.SZ', '301155.SZ', '301167.SZ', '301169.SZ', '301177.SZ', '301178.SZ',
               '301179.SZ', '301180.SZ', '301182.SZ', '301185.SZ', '301186.SZ', '301188.SZ', '301189.SZ', '301190.SZ',
               '301193.SZ', '301198.SZ', '301199.SZ', '301211.SZ', '301213.SZ', '301221.SZ', '601330.SH', '601598.SH',
               '601658.SH', '601811.SH', '601858.SH', '601865.SH', '601878.SH', '603013.SH', '603020.SH', '603036.SH',
               '603037.SH', '603041.SH', '603042.SH', '603043.SH', '603055.SH', '603059.SH', '603068.SH', '603081.SH',
               '603087.SH', '603089.SH', '603093.SH', '603101.SH', '603115.SH', '603121.SH', '603127.SH', '603129.SH',
               '603138.SH', '603139.SH', '603167.SH', '603178.SH', '603180.SH', '603181.SH', '603185.SH', '603186.SH',
               '603187.SH', '603197.SH', '603199.SH', '603200.SH', '603208.SH', '603212.SH', '603218.SH', '603228.SH',
               '603229.SH', '603232.SH', '603258.SH', '603260.SH', '603266.SH', '603267.SH', '603277.SH', '603278.SH',
               '603279.SH', '603289.SH', '603298.SH', '603301.SH', '603303.SH', '603313.SH', '603319.SH', '603332.SH',
               '603337.SH', '603356.SH', '603359.SH', '603363.SH', '603379.SH', '603380.SH', '603385.SH', '603387.SH',
               '603392.SH', '603408.SH', '603444.SH', '603527.SH', '603529.SH', '603530.SH', '603535.SH', '603536.SH',
               '603568.SH', '603577.SH', '603585.SH', '603586.SH', '603590.SH', '603595.SH', '603596.SH', '603605.SH',
               '603619.SH', '603629.SH', '603630.SH', '603639.SH', '603650.SH', '603662.SH', '603663.SH', '603666.SH',
               '603668.SH', '603669.SH', '603676.SH', '603679.SH', '603683.SH', '603689.SH', '603697.SH', '603706.SH',
               '603707.SH', '603709.SH', '603713.SH', '603719.SH', '603727.SH', '603737.SH', '603739.SH', '603755.SH',
               '603767.SH', '603790.SH', '603801.SH', '603813.SH', '603815.SH', '603817.SH', '603826.SH', '603829.SH',
               '603856.SH', '603860.SH', '603866.SH', '603867.SH', '603868.SH', '603879.SH', '603882.SH', '603897.SH',
               '603899.SH', '603906.SH', '603908.SH', '603917.SH', '603929.SH', '603931.SH', '603933.SH', '603937.SH',
               '603938.SH', '603950.SH', '603963.SH', '603966.SH', '603967.SH', '603968.SH', '603970.SH', '603983.SH',
               '603992.SH', '605003.SH', '605058.SH', '605089.SH', '605099.SH', '605100.SH', '605108.SH', '605111.SH',
               '605136.SH', '605179.SH', '605180.SH', '605186.SH', '605259.SH', '605277.SH', '605298.SH']
    ts_code = ['300972.SZ', '300964.SZ', '300550.SZ', '300494.SZ', '603929.SH', '300912.SZ', '003029.SZ', '300634.SZ',
               '300970.SZ', '300971.SZ', '002987.SZ', '603755.SH', '603042.SH', '300511.SZ', '301179.SZ', '300906.SZ',
               '300995.SZ', '300931.SZ', '300998.SZ', '603081.SH', '601598.SH', '601811.SH', '300837.SZ', '605277.SH',
               '301032.SZ', '603983.SH', '301178.SZ', '002832.SZ', '301001.SZ', '300967.SZ', '003025.SZ', '300996.SZ',
               '603186.SH', '601658.SH', '605179.SH', '300981.SZ', '300902.SZ', '603650.SH', '300918.SZ', '301058.SZ',
               '301056.SZ', '605058.SH', '300973.SZ', '603860.SH', '300743.SZ', '301088.SZ', '603444.SH', '603868.SH',
               '301039.SZ', '002818.SZ']
    count = 0
    # df_res = pd.DataFrame()
    st = datetime.now()

    for tscode in ts_code:
        count += 1

        # t1 = datetime.now()  # 调用接口的时间
        df = bak_daily(ts_code=tscode)
        # t2 = datetime.now()
        df.to_sql(bak_daily_tbname, engine_ts, index=False, if_exists='append')
        # df_res = df_res.append(df)
        # t3 = datetime.now()

        print('已存储%d支股票，该股票为%s，目前耗时%s' % (count, tscode, datetime.now() - st))
        time.sleep(12)

        # if count % 2 == 0:
        #     if delay60 > (datetime.now() - t1):  # 表示调用接口两次后所花费的时间<60s
        #         delay_time = (delay60 - (datetime.now() - t1)).seconds + 1
        #         print('延时%ds' % delay_time)
        #         time.sleep(delay_time)
        #         print('目前耗时%s' % (datetime.now() - t1))
        #         # t1 = datetime.now()
        #     else:
        #         pass

    # 将dataframe数据一次性存储到数据库中
    # df_res.to_sql(bak_daily_tbname, engine_ts, index=False, if_exists='append')
    print('DONE!')


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
# 已使用到该函数
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
def get_all_stocks(ts_code, tables):
    """
    循环tushare网站上的最新stock_basic中的ts_code，将缺少的数据逐个补全到数据表中
    :param ts_code:
    :param tables:
    :return:
    """
    count = 0
    tbc_list = []  # to be confirmed
    new_stocks_list = []  # 新增股票
    a_time = datetime.now()
    fixed_time = timedelta(seconds=60)

    api_call_num = 1
    st = datetime.now()
    count_st = datetime.now()
    for tsc in ts_code:
        tsc_table_name = ''.join(tsc.split('.')[::-1]).lower()
        if tsc_table_name in tables:
            # 目前数据库中已有的股票
            last_date = read_table_last_date(tsc_table_name)
            if last_date is not None:
                if local_datetime > last_date:
                    api_call_num += 1
                    ntd = gap_date(last_date)  # ntd:next_trade_date
                    df = get_trade_date_data(tsc, start_date=ntd)
                    reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                    write_data(reverse_df, tsc_table_name)
                else:
                    print('数据表中最新日期=当天日期')
            else:
                # last_date is None，表示该支股票在数据库中有数据表，
                # 但表内却没有数据，需要将从接口获取的所有数据导入表中
                api_call_num += 1
                tbc_list.append(tsc)
                df = get_trade_date_data(tsc)
                reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
                write_data(reverse_df, tsc_table_name)
                print('{}这支股票待确认，last_date={}'.format(tsc_table_name, last_date))
        else:
            # 相较于目前数据库中新增的股票
            api_call_num += 1
            new_stocks_list.append(tsc)
            df = get_trade_date_data(tsc)
            reverse_df = df[::-1]
            write_data(reverse_df, tsc_table_name)
            print('===> 新增股票：', tsc)

        # # TODO 需要调整：统计一分钟内调用接口的次数
        # # 每轮跑stock_count支股票
        # stock_count = 50
        # if api_call_num % stock_count == 0:
        #     present_time = datetime.now()
        #     break_time = present_time - count_st
        #     duration_time = present_time - st
        #     if break_time.seconds < 60:
        #         delay_time = (fixed_time - break_time).seconds + 2
        #         time.sleep(delay_time)
        #         print('总耗时：{}，本轮耗时：{}，需要等待{}s'.format(duration_time, break_time, delay_time))
        #         count_st = datetime.now()
        #     else:
        #         print('总耗时：{}，本轮耗时：{}，无需等待'.format(duration_time, break_time))
        #         count_st = datetime.now()

        # 通过控制次数来确保接口调用每分钟少于60次
        count += 1
        if count % 50 == 0:
            print('api_call_num:', api_call_num)
            intermediate_time = datetime.now()
            print('目前已获取%d支股票，用时%s' % (count, intermediate_time - st))
            b_time = datetime.now()
            ba_time = b_time - a_time
            if ba_time.seconds < 60:
                delay_time = fixed_time - ba_time
                print('需要等待', delay_time)
                time.sleep(delay_time.seconds + 1)
            else:
                print('无需等待')
            a_time = datetime.now()

    et = datetime.now()
    print('\n\n')
    if len(tbc_list) != 0:
        print('待确认股票:\n', tbc_list)
    print('本次新增股票:\n', new_stocks_list)
    print('%d stocks are imported into the database.' % count)
    print('It takes {} to get stocks!'.format(et - st))


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

    """
    # 获取数据库中各个股票数据表中最新的日期，并形成字典备用
    print(f'\n以下进行{Color.BLUEBOLD}[数据库中各股票最新日期]{Color.END}的获取，进度如下：')
    num_1 = 0
    last_date_dict = {}
    for tb_name in tables:
        if tb_name[:2] == 'bj' or tb_name[:2] == 'sh' or tb_name[:2] == 'sz':
            last_date = read_table_last_date(tb_name)
            # 更新字典，将日期作为键，股票代码作为值
            if last_date not in last_date_dict:
                last_date_dict.update({last_date: [tb_name]})
            else:
                last_date_dict[last_date].append(tb_name)
        num_1 += 1
        view_bar(num_1, len(tables))
    print('\n获取数据表中股票的最新时间共耗时：%s\n' % (datetime.now() - st))

    # 更新字典形式，以最新日期的下一个交易日作为键，股票代码作为值存入新的字典中备用
    st1 = datetime.now()
    next_date_dict = {}
    for last_date in last_date_dict.keys():
        # next_date = next_trade_date(last_date)
        if last_date is not None:
            if last_date < local_datetime:
                print(f'下列股票最近更新日期为{last_date}，可能未及时更新或已停牌或新增：{last_date_dict[last_date]}')
        else:
            print(f'{last_date_dict[last_date]}无最近更新日期，可能为最近新增股票')
        for dict_ts_code in last_date_dict[last_date]:
            next_date_dict.update({dict_ts_code: last_date})
    print('\n更新字典共耗时：%s\n' % (datetime.now() - st1))

    # 根据stock_basic中的股票代码，获取TS网站中各个股票的日线行情数据
    print(f'\n以下进行{Color.BLUEBOLD}[TS网站中各个股票的日线行情数据]{Color.END}的获取，进度如下：')
    st2 = datetime.now()
    for tsc in ts_code:
        count += 1
        tsc_table_name = ''.join(tsc.split('.')[::-1]).lower()
        if tsc_table_name in next_date_dict:
            # 目前数据表中有该支股票，但是时间不是最新的，下列为更新数据表操作
            # TODO 存在股票代码已经存储到all_stock_basic的数据表中，但是该股票尚未开盘（即股票已上市，但未开盘）
            #  所以数据表中依然没有数据的情况，还需要判断该股票日线行情是否录入到数据表中（加一个数据长度的判断再进行存储）
            update_stocks_list.append(tsc)  # 更新股票列表集合
            df = get_trade_date_data(tsc, start_date=next_date_dict[tsc_table_name])
            reverse_df = df[::-1]  # 将数据写入数据表之前，要先倒转顺序
            # print(reverse_df[1:2])
            # write_data(reverse_df[1:], tsc_table_name)
        else:
            # 相较于目前数据库中新增的股票
            new_stocks_list.append(tsc)  # 新增股票列表集合
            df = get_trade_date_data(tsc)
            reverse_df = df[::-1]
            # write_data(reverse_df, tsc_table_name)
            print('===> 新增股票：', tsc)

        # 每获取1000支股票，输出查看一下时间
        # count += 1
        # if count % 1000 == 0:
        #     print('目前已获取%d支股票，用时%s' % (count, datetime.now() - st2))

        view_bar(count, len(ts_code))  # 实时刷新进度条
    """
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
    # 判断是否为交易日
    # is_trade = is_trade_date()[0]
    # pre_trade = is_trade_date()[1]

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
        # get_all_stocks(tscode, tables)
        get_daily_stocks(tscode, tables)

        end_time = datetime.now()

        print('=====================%s=======================' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('Starting time is ', start_time)
        print('Ending time is   ', end_time)
        print('It takes {}, the program is finished!'.format(end_time - start_time))
    else:
        print('非交易日')

    # 单个股票采集
    # tscode = '000001.SZ'
    # df = get_daily_data(ts_code=tscode)

    # WRITE DATA INTO DATABASES(>=4900)
    # write_all_stock(tscode)

    # READ DATA FROM MYSQL
    # read_df = read_data('stock_basic')


if __name__ == '__main__':
    main()

    # duplicate_list = duplicate_checking()
    pass
