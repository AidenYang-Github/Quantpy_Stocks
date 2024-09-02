"""
Created on 2022年10月27日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks

数据处理 & 图像展示模块

字段	        类型	说明
0.ts_code	    str	    股票代码
1.trade_date	str	    交易日期
2.open	        float	开盘价
3.high	        float	最高价
4.low	        float	最低价
5.close	        float	收盘价
6.pre_close	    float	昨收价
7.change	    float	涨跌额
8.pct_chg	    float	涨跌幅
9.vol	        float	成交量
10.amount	    float	成交额

change = close - pre_close
pct_chg = change/pre_close

"""
# -*- coding: UTF-8 -*-
import sys
import time
from datetime import datetime
import argparse

# import numpy as np
import pandas as pd
import mplfinance as mpf
# import matplotlib.pyplot as plt

from config import stock_table_name
from Module import MySQL_Database

local_datetime = time.strftime('%Y%m%d')

# 数据库初始化设置
DB = MySQL_Database.MySQLDatabaseOperations()  # 初始化数据库


# DB.create_mysql_database()   # 新建数据库


class MySQLDataProcessing:
    """
    从数据表中获取数据，并绘图以及分析
    """

    def __init__(self):
        pass


# =============== 外部传参 ===============
def init_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=0, help='--num=int, display stock number')  # 默认值0代表开放到所有数据
    parser.add_argument('--stock_code', type=str, default='', help='--stock_code=str')  # 增加参数，开放ts_code
    parser.add_argument('--function', type=int, default=0,
                        help='--function=0：获取股票的具体数据；=1：绘制股价走势日k线图；=2：获取股票涨跌记录')  # 功能选项
    return parser.parse_args()


args = init_arg()


# =============== 进度条展示 ===============
def view_bar(num, total):
    rate = num / total
    rate_num = round(rate * 100, 2)
    fz = int(num / total * 100)
    r = '\r[%s%s]%0.2f%%' % ("=" * fz, " " * (100 - fz), rate_num,)
    sys.stdout.write(r)
    sys.stdout.flush()


# =============== 数据处理 ===============
def tscode_to_tbname(ts_code=''):
    """
    将ts_code转换成股票的数据表名，'000001.SZ'→'sz000001'
    :param ts_code:
    :return:
    """
    try:
        tscode = ts_code.split('.')
        table_name = tscode[1].lower() + tscode[0]
        return table_name
    except Exception as e:
        print(e)


def fluctuation_statistics(ts_code=''):
    tbname = tscode_to_tbname(ts_code)
    df = DB.read_data(tbname)

    # 收盘价
    df1 = df.values[-1][5]  # 最新一天的收盘价
    df2 = df.values[-2][5]  # 倒数第二天的收盘价
    df3 = df.values[-3][5]  # 倒数第三天的收盘价
    df4 = df.values[-5][5]  # 倒数第五天的收盘价
    df5 = df.values[-10][5]  # 倒数半个月（10天）的收盘价
    df6 = round(sum([a[5] for a in df.values[-25:-15]]) / len(df.values[-25:-15]), 2)  # 倒数一个月（20天）的平均收盘价
    df7 = round(sum([a[5] for a in df.values[-45:-35]]) / len(df.values[-45:-35]), 2)  # 倒数两个月（40天）的平均收盘价
    df8 = round(sum([a[5] for a in df.values[-65:-55]]) / len(df.values[-65:-55]), 2)  # 倒数三个月（60天）的平均收盘价
    df9 = round(sum([a[5] for a in df.values[-125:-115]]) / len(df.values[-125:-115]), 2)  # 倒数六个月（120天）的平均收盘价
    df10 = round(sum([a[5] for a in df.values[-185:-175]]) / len(df.values[-185:-175]), 2)  # 倒数九个月（180天）的平均收盘价
    df11 = round(sum([a[5] for a in df.values[-245:-235]]) / len(df.values[-245:-235]), 2)  # 倒数十二个月（240天）的平均收盘价

    # 涨跌幅
    f1 = round((df1 - df2) / df2 * 100, 4)
    f2 = round((df1 - df3) / df3 * 100, 4)
    f3 = round((df1 - df4) / df4 * 100, 4)
    f4 = round((df1 - df5) / df5 * 100, 4)
    f5 = round((df1 - df6) / df6 * 100, 4)
    f6 = round((df1 - df7) / df7 * 100, 4)
    f7 = round((df1 - df8) / df8 * 100, 4)
    f8 = round((df1 - df9) / df9 * 100, 4)
    f9 = round((df1 - df10) / df10 * 100, 4)
    f10 = round((df1 - df11) / df11 * 100, 4)

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


# =============== 个股K线展示 ===============
def k_line_display(stock_name):
    """
    获取单支股票的数据，并绘制股价走势日k线图
    :param stock_name: str，股票ts_code，包含后缀，；例如“000001.SZ”
    :return:
    """
    # data = pd.read_csv(stock_name + '.csv')  # 传入数据
    # sn = stock_name.split('.')
    data = DB.read_data(tscode_to_tbname(ts_code=stock_name))
    stock_chinese_name = DB.read_tscode_name(stock_table_name, stock_name)
    # bak_basic_data = DB.read_bak_basic_data(tb_name='all_bak_basic_20230318', ts_code=stock_name)

    # 构建所需绘制图片的数据集
    # 将data中的trade_date/open/high/low/close/vol构建新的df
    data_k_line1 = pd.DataFrame(
        {
            'Date': data['trade_date'].astype(str),
            'Open': data['open'],
            'High': data['high'],
            'Low': data['low'],
            'Close': data['close'],
            'Pclose': data['pre_close'],
            'Change': data['change'],
            'Pchange': data['pct_chg'],
            'Volume': data['vol'],
            'Amount': data['amount']
        }
    )

    # 将bak_basic_data中的trade_date/pe/pb构建新的df
    # data_k_line2 = pd.DataFrame(
    #     {
    #         'Date': bak_basic_data['trade_date'].astype(str),
    #         'Pe': bak_basic_data['pe'],
    #         'Pb': bak_basic_data['pb']
    #     }
    # )

    # 合并以上两个dataframe中的数据
    # data_k_line0 = pd.merge(data_k_line1, data_k_line2, on='Date')    # 按照key合并，
    # data_k_line0 = pd.merge(data_k_line1, data_k_line2, how='left')  # 按照类型合并
    data_k_line0 = data_k_line1

    # 将字符串类型的日期转换成时间戳的索引
    data_k_line0['Date'] = pd.to_datetime(data_k_line0['Date'])
    data_k_line = data_k_line0.set_index('Date')  # 以日期为索引

    # 设置k线颜色
    my_color = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='inherit',
        wick='i',  # wick：上下影线颜色，i表示继承up和down的颜色
        volume='i',  # 成交量直方图颜色，也可用i继承up和down的颜色
        ohlc='i'
    )

    # 设置k线样式
    """mpf.available_styles()
    具体见：https://github.com/matplotlib/mplfinance/wiki/Mplfinance-Style-Sheets-Reference
    'binance'：甘露寺蜜璃色
    'binancedark'：报错
    'blueskies'：天蓝色系
    'brasil'：绿色背景黄藏蓝色柱
    'charles'：深绿红色柱
    'checkers'：红黑色柱
    'classic'：全黑色柱
    'default'：黑白色柱
    'ibd'：粉红蓝色柱
    'kenan'：红黑色柱
    'mike'：全黑背景蓝黑色柱
    'nightclouds'：全黑背景蓝白色柱
    'sas'：深红深蓝色柱
    'starsandstripes'：深红深蓝色柱
    'tradingview'：报错
    'yahoo'：亮红亮绿色柱
    """
    my_style = mpf.make_mpf_style(
        marketcolors=my_color,  # 设置图标显示配色 mpf.available_styles() 可以查看所有样式
        gridaxis='both',  # 设置网格位置
        gridstyle='-.',  # 设置网格线线型
        rc={'font.family': 'SimHei'}  # 设置中文兼容（如果STSong无效的话改成SimHei）
    )

    # 获取指定数量的k线数据，开放参数手动调节
    # args.num = 100
    data_k_line_index = data_k_line.index[-1 * args.num:]  # 取索引中最后args.num个数据
    part_of_data_k_line = data_k_line.loc[data_k_line_index, :]

    # 将pe数据提取出来
    # add_plot = mpf.make_addplot(part_of_data_k_line['Pe'])
    # add_plot = [mpf.make_addplot(part_of_data_k_line[['Pe']]),
    #             mpf.make_addplot(part_of_data_k_line[['Pb']])]

    # 读取显示区间的最后一个交易日的数据
    last_k_line_data = part_of_data_k_line.iloc[-1]
    # 使用mpf.figure()函数可以返回一个figure对象，从而进入External Axes Mode，从而实现对Axes对象和figure对象的自由控制
    fig = mpf.figure(style=my_style, figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))

    # 添加三个图表，四个数字分别代表图表左下角在figure中的坐标，以及图表的宽（0.88）、高（0.60）
    # 添加第二、三张图表时，使用sharex关键字指明与ax1在x轴上对齐，且共用x轴
    ax1 = fig.add_axes([0.06, 0.25, 0.88, 0.60])
    ax2 = fig.add_axes([0.06, 0.15, 0.88, 0.10], sharex=ax1)
    ax3 = fig.add_axes([0.06, 0.05, 0.88, 0.10], sharex=ax1)

    # 设置三张图表的Y轴坐标
    ax1.set_ylabel('price of stock (yuan)')
    ax2.set_ylabel('Trading volume (shares)')
    ax3.set_ylabel('MACD')

    # 标题格式，字体为中文字体，颜色为黑色，粗体，水平中心对齐（pingfang HK）
    title_font = {'fontname': 'SimHei',
                  'size': '16',
                  'color': 'black',
                  'weight': 'bold',
                  'va': 'bottom',
                  'ha': 'center'}
    # 红色数字格式（显示开盘收盘价）粗体红色24号字
    large_red_font = {'fontname': 'Arial',
                      'size': '24',
                      'color': 'red',
                      'weight': 'bold',
                      'va': 'bottom'}
    # 绿色数字格式（显示开盘收盘价）粗体绿色24号字
    large_green_font = {'fontname': 'Arial',
                        'size': '24',
                        'color': 'green',
                        'weight': 'bold',
                        'va': 'bottom'}
    # 小数字格式（显示其他价格信息）粗体红色12号字
    small_red_font = {'fontname': 'Arial',
                      'size': '12',
                      'color': 'red',
                      'weight': 'bold',
                      'va': 'bottom'}
    # 小数字格式（显示其他价格信息）粗体绿色12号字
    small_green_font = {'fontname': 'Arial',
                        'size': '12',
                        'color': 'green',
                        'weight': 'bold',
                        'va': 'bottom'}
    # 标签格式，可以显示中文，普通黑色12号字
    normal_label_font = {'fontname': 'SimHei',
                         'size': '12',
                         'color': 'black',
                         'va': 'bottom',
                         'ha': 'right'}
    # 普通文本格式，普通黑色12号字
    normal_font = {'fontname': 'Arial',
                   'size': '12',
                   'color': 'black',
                   'va': 'bottom',
                   'ha': 'left'}

    # 在figure对象上添加文本对象，用于显示各种价格和标题
    fig.text(0.50, 0.94, f'{stock_name}-{stock_chinese_name}', **title_font)
    fig.text(0.12, 0.90, '开/收: ', **normal_label_font)
    fig.text(0.14, 0.89, f'{last_k_line_data["Open"]} / {last_k_line_data["Close"]}', **large_red_font)
    fig.text(0.14, 0.86, f'{last_k_line_data["Change"]}', **small_red_font)
    fig.text(0.22, 0.86, f'[{last_k_line_data["Pchange"]}%]', **small_red_font)
    fig.text(0.12, 0.86, f'{last_k_line_data.name.date()}', **normal_label_font)
    fig.text(0.40, 0.90, '最高: ', **normal_label_font)
    fig.text(0.40, 0.90, f'{last_k_line_data["High"]}', **small_red_font)
    fig.text(0.40, 0.86, '最低: ', **normal_label_font)
    fig.text(0.40, 0.86, f'{last_k_line_data["Low"]}', **small_green_font)
    fig.text(0.55, 0.90, '成交量(万手): ', **normal_label_font)
    fig.text(0.55, 0.90, f'{round(last_k_line_data["Volume"] / 10000, 3)}', **normal_font)
    fig.text(0.55, 0.86, '成交额(亿元): ', **normal_label_font)
    fig.text(0.55, 0.86, f'{round(last_k_line_data["Amount"] / 100000, 3)}', **normal_font)
    # fig.text(0.70, 0.90, '涨停: ')
    # fig.text(0.70, 0.90, f'{last_k_line_data["upper_lim"]}')
    # fig.text(0.70, 0.86, '跌停: ')
    # fig.text(0.70, 0.86, f'{last_k_line_data["lower_lim"]}')
    # fig.text(0.85, 0.90, '均价: ')
    # fig.text(0.85, 0.90, f'{last_k_line_data["average"]}')
    fig.text(0.85, 0.86, '昨收: ', **normal_label_font)
    fig.text(0.85, 0.86, f'{last_k_line_data["Pclose"]}', **normal_font)

    # 显示K线
    # mpf.plot(
    #     part_of_data_k_line,
    #     type='candle',  # 设置显示样式，选项['ohlc','candle','line','renko','pnf']
    #     title='%s K-line chart of stock price trend' % stock_name,  # 设置图标题
    #     ylabel='price of stock (yuan)',  # 设置y轴标题
    #     style=my_style,  # 应用上面命令设置的样式
    #     # style='default',  # 应用上面命令设置的样式
    #     show_nontrading=False,  # 是否显示非交易日，默认为False：显示
    #     volume=True,  # 下方是否显示成交量，默认为False
    #     ylabel_lower='Trading volume (shares)',  # 成交量图的y轴标题
    #     datetime_format='%Y-%m-%d',  # x轴的时间显示格式
    #     xrotation=45,  # x轴的时间坐标旋转角度
    #     linecolor='#00ff00',  # 若type='line'设置线条的颜色
    #     tight_layout=False,  # 是否紧密显示
    #     mav=(5, 10, 30),  # Moving Average
    #     # addplot=add_plot,
    #     warn_too_much_data=7000  # 最大报警数值，默认599，超过599条数据后会显示警告
    # )

    # plt.rcParams['font.sans-serif'] = ['SimHei']
    mpf.plot(part_of_data_k_line,
             ax=ax1,
             volume=ax2,
             type='candle',
             style=my_style,
             mav=(5, 10, 30),  # Moving Average
             warn_too_much_data=7000  # 最大报警数值，默认599，超过599条数据后会显示警告
             )
    fig.show()
    pass


# ================ 查重程序 ==================
def duplicate_checking():
    """
    数据表查重
    :return:
    """
    print('\n开始查重')
    # 获取数据库中已有的表名
    tables = DB.show_tables()  # 数据库中所有的数据表
    engine_ts = DB.create_mysql_database()  # 新建数据库

    tb_list = []
    # param = ''
    for tb_name in tables:
        if tb_name[:2] == 'al' or tb_name[:2] == 'st':
            param = 'ts_code'
        elif tb_name[:2] == 'bj' or tb_name[:2] == 'sh' or tb_name[:2] == 'sz':
            param = 'trade_date'
        else:
            continue

        sql = 'SELECT {0} FROM {1} GROUP BY {0} HAVING count({0})>1'.format(param, tb_name)
        dataframe = pd.read_sql_query(sql, engine_ts)
        if dataframe.values.size != 0:
            tb_list.append(tb_name)

    if len(tb_list) != 0:
        print('重复列表如下：\n', tb_list)
        return tb_list
    else:
        print('数据表均无重复')


# =============== 主程序 ===============
def main():
    """
    获取数据库中所有数据表的名称，并读取各个股票的具体数据
    :return:
    """
    tables = DB.show_tables()

    for tb_name in tables:
        if tb_name[:2] == 'bj' or tb_name[:2] == 'sh' or tb_name[:2] == 'sz':
            # 读取到股票
            df = DB.read_data(tb_name)
            DB.read_detail_data(df)


def main_stock_fluctuation_statistics(ts_code=''):
    """
    获取股票涨跌记录
    :return:
    """
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

    fluctuation_list = []
    st = datetime.now()
    for tscode in ts_code:
        fluctuation_list.append(fluctuation_statistics(tscode))
    print('耗时：', datetime.now() - st)
    return fluctuation_list


if __name__ == '__main__':
    # func_num = args.function
    # ts_code = args.stock_code
    func_num = 1
    tscode = '000001.SZ'

    if func_num == 0:
        main()
    elif func_num == 1:
        print('Stock Code: ', tscode)
        k_line_display(tscode)  # 开放ts_code
    elif func_num == 2:
        main_stock_fluctuation_statistics()
