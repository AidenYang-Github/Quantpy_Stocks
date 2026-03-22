"""
Created on 2024年09月02日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks
"""
from datetime import datetime

import backtrader as bt
import pandas as pd

from Module import MySQL_Database, mysql_data_processing as mdp
from Strategy import CASH
from config import STOCK_BASIC_NAME, STOCK_TSCODE, USE_QFQ


class MyStrategy(bt.Strategy):
    """"""
    params = (('period', 10),)  # 设置周期为10天

    def __init__(self, ):
        """Constructor for MyStrategy"""
        # 引用到输入数据的close价格
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None  # To keep track of pending orders
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.MovingAverageSimple()
        # self.sma = bt.indicators.MovingAverageSimple(period=self.params.period)   # 默认均线周期是30天，可自行设置

    def log(self, txt, dt=None):
        """
        # 提供记录功能 Logging function for this strategy
        :param txt:
        :param dt:
        :return:
        """
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        """
        order.Status:[0~8]
        ['Created', 'Submitted', 'Accepted', 'Partial', 'Completed', 'Canceled', 'Expired', 'Margin', 'Rejected']
        :param order:
        :return:
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))
                pass

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):  # 交易执行后，在这里处理
        if not trade.isclosed:
            return

        # 记录下盈利数据(GROSS:毛利，NET:净利)
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        """
        # 策略核心：均线买卖策略——收盘价大于均线则买入，收盘价低于均线则卖出
        :return:
        """
        # 目前的策略就是简单显示下收盘价,Simple log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # 检查是否在市场 Check if we are in the market
        if not self.position:
            if self.dataclose[0] > self.sma[0]:  # 大于均线买入
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()  # Keep track of the created order to avoid a 2nd order
        else:
            if self.dataclose[0] < self.sma[0]:  # 小于均线卖出
                self.log('SELL CREATED, %.2f' % self.dataclose[0])
                self.order = self.sell()  # Keep track of the created order to avoid a 2nd order


def get_database_data(stn):
    """
    # 加载数据库中的个股数据
    :param stn:stock table name -> 从数据库中的'all_stock_basic'数据表获取数据
    :return:
    """
    # 从数据库中获取所需回测的股票数据名称
    database = MySQL_Database.MySQLDatabaseOperations()
    all_stock_basic = database.read_data(stn)  # 获取数据表“all_stock_basic”中所有上市股票的代码
    stock_name = mdp.tscode_to_tbname(all_stock_basic.ts_code[0])  # 取数据库中第一只股票的代码名字

    # 加载该个股OHLC及成交量等数据，并使用交易日期作为DataFrame的index
    df = database.read_data(stock_name)
    df.index = pd.to_datetime(df['trade_date'])

    # 重组df的列名称，让其符合backtrader要求的格式
    df.drop(['ts_code', 'trade_date', 'pre_close', 'change', 'pct_chg', 'amount'], axis=1, inplace=True)
    df.rename(columns={'vol': 'volume'}, inplace=True)
    return df


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 设置一个回测策略
    cerebro.addstrategy(MyStrategy)

    # 获取数据库中的个股数据
    if USE_QFQ:
        stock_df = mdp.adj_data_processing(STOCK_TSCODE)
    else:
        stock_df = get_database_data(STOCK_BASIC_NAME)

    # 将数据适配到bt框架的数据类型
    start_date = datetime(2024, 1, 1)  # 回测开始时间
    end_date = datetime.now()  # 回测结束时间
    data = bt.feeds.PandasData(dataname=stock_df, fromdate=start_date, todate=end_date)

    # 将数据传入回测系统
    cerebro.adddata(data)

    # 设定初始金额
    cerebro.broker.setcash(cash=CASH)

    # 设置佣金：千分之一
    cerebro.broker.setcommission(commission=0.001)

    # 设置每次交易买入的股数
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(style='candle')
