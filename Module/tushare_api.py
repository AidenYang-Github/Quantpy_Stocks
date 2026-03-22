"""
Created on 2023年03月02日

@author: Aiden_yang
@website：https://gitee.com/aiden_yang/Stocks

# Tushare接口说明
# pro.stock_basic()：接口每小时只能调用一次，每天会有调用次数限制
# pro.daily()：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
# pro.trade_cal()：需2000积分
# pro.bak_basic：每天最多访问该接口20次，每分钟最多访问该接口2次，单次最大5000条
# pro.bak_daily：
# pro.stock_mx：
# pro.suspend_d：
"""
import tushare as ts

from TOKEN_ID import TOKEN

# 初始化pro接口
pro = ts.pro_api(TOKEN)


class TuShareAPI:
    def __init__(self):
        pass


# 股票列表
def stock_basic(exchange='', list_status=''):
    """
    名称	    类型  必选	描述
    ts_code	    str	    N	TS股票代码
    name	    str	    N	名称
    market	    str	    N	市场类别 （主板/创业板/科创板/CDR/北交所）
    list_status	str	    N	上市状态 L上市 D退市 P暂停上市，默认是L
    exchange	str	    N	交易所 SSE上交所 SZSE深交所 BSE北交所
    is_hs	    str	    N	是否沪深港通标的，N否 H沪股通 S深股通
    limit：单次返回数据长度
    offset：请求数据的开始位移量

    :param exchange:交易所 SSE上交所 SZSE深交所 HKEX港交所，例如：'SSE'
    :param list_status:上市状态 L上市 D退市 P暂停上市，例如：'L'
    :return:
    """
    df = pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": exchange,
        "market": "",
        "is_hs": "",
        "list_status": list_status,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "cnspell",
        "market",
        "list_date",
        "act_name",
        "act_ent_type",
        "fullname",
        "enname",
        "exchange",
        "curr_type",
        "list_status",
        "delist_date",
        "is_hs"
    ])
    return df


# 交易日历
def trade_cal(cal_date='', start_date='', end_date='', is_open='', limit='', offset=''):
    df = pro.trade_cal(**{
        "exchange": "",
        "cal_date": cal_date,
        "start_date": start_date,
        "end_date": end_date,
        "is_open": is_open,
        "limit": limit,
        "offset": offset
    }, fields=[
        "exchange",
        "cal_date",
        "is_open",
        "pretrade_date"
    ])
    return df


# ################ 从接口获取数据 # ################
# 以下函数调用了pro.daily()接口
def get_daily_data(ts_code):
    """
    根据股票的ts_code，获取股票的每日数据
    pro.daily：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
    :param ts_code:具体股票的ts_code，str
    :return:
    """
    df = pro.daily(ts_code=ts_code)
    return df


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


# 备用列表
def bak_basic(trade_date='', ts_code='', limit='', offset=''):
    """
    每天最多访问该接口20次，每分钟最多访问该接口2次，单次最大5000条
    """
    df = pro.bak_basic(**{
        "trade_date": trade_date,
        "ts_code": ts_code,
        "limit": limit,
        "offset": offset
    }, fields=[
        "trade_date",
        "ts_code",
        "name",
        "industry",
        "area",
        "pe",
        "float_share",
        "total_share",
        "total_assets",
        "liquid_assets",
        "fixed_assets",
        "reserved",
        "reserved_pershare",
        "eps",
        "bvps",
        "pb",
        "list_date",
        "undp",
        "per_undp",
        "rev_yoy",
        "profit_yoy",
        "gpr",
        "npr",
        "holder_num"
    ])
    return df


# 备用行情
def bak_daily(ts_code='', trade_date='', start_date='', end_date='', offset='', limit=''):
    df = pro.bak_daily(**{
        "ts_code": ts_code,
        "trade_date": trade_date,
        "start_date": start_date,
        "end_date": end_date,
        "offset": offset,
        "limit": limit
    }, fields=[
        "ts_code",
        "trade_date",
        "name",
        "pct_change",
        "close",
        "change",
        "open",
        "high",
        "low",
        "pre_close",
        "vol_ratio",
        "turn_over",
        "swing",
        "vol",
        "amount",
        "selling",
        "buying",
        "total_share",
        "float_share",
        "pe",
        "industry",
        "area",
        "float_mv",
        "total_mv",
        "avg_price",
        "strength",
        "activity",
        "avg_turnover",
        "attack",
        "interval_3",
        "interval_6"
    ])
    return df


# 动能因子
def stock_mx(ts_code='', trade_date='', start_date='', end_date=''):
    df = pro.stock_mx(**{
        "ts_code": ts_code,
        "trade_date": trade_date,
        "start_date": start_date,
        "end_date": end_date,
        "limit": "",
        "offset": ""
    }, fields=[
        "trade_date",
        "ts_code",
        "mx_grade",
        "com_stock",
        "evd_v",
        "zt_sum_z",
        "wma250_z"
    ])
    return df


# 每日停复牌信息
def suspend_d(ts_code='', suspend_type='', trade_date='', start_date='', end_date=''):
    df = pro.suspend_d(**{
        "ts_code": ts_code,
        "suspend_type": suspend_type,
        "trade_date": trade_date,
        "start_date": start_date,
        "end_date": end_date,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "suspend_timing",
        "suspend_type"
    ])
    return df


# 通用行情接口
def pro_bar(ts_code='', sd='', ed='', asset='E', adj='qfq', freq='D', ma=[5, 10]):
    """
    Parameters:
    ------------
    :param ts_code: 证券代码，支持股票,ETF/LOF,期货/期权,港股,数字货币
    :param sd: 开始日期  YYYYMMDD
    :param ed: 结束日期 YYYYMMDD
    :param asset: 证券类型 E:股票和交易所基金，I:沪深指数,C:数字货币,FT:期货 FD:基金/O期权/H港股/CB可转债
    :param adj: 复权类型,None不复权,qfq:前复权,hfq:后复权
    :param freq: 支持1/5/15/30/60分钟,周/月/季/年
    :param ma: 均线,支持自定义均线频度，如：ma5/ma10/ma20/ma60/maN
    :return:
    """
    df = ts.pro_bar(ts_code=ts_code,
                    asset=asset,
                    start_date=sd,
                    end_date=ed,
                    adj=adj,
                    freq=freq,
                    ma=ma)
    return df


# 股票技术因子（量化因子）
def stk_factor(ts_code, start_date='', end_date='', trade_date=''):
    """
    接口：stk_factor
    描述：获取股票每日技术面因子（量化因子）数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史
    限量：单次最大10000条，可以循环或者分页提取（若积分只有120基础积分的情况下，每分钟只能调用两次，每天最多调用6次）
    积分：5000积分每分钟可以请求100次，8000积分以上每分钟500次，具体请参阅积分获取办法

    ts_code：股票代码
    start_date：开始日期
    end_date：结束日期
    trade_date：交易日期
    limit：单次返回数据长度
    offset：请求数据的开始位移量
    :return:
    """
    df = pro.stk_factor(**{
        "ts_code": ts_code,
        "start_date": start_date,
        "end_date": end_date,
        "trade_date": trade_date,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "close",
        "open",
        "high",
        "low",
        "pre_close",
        "change",
        "pct_change",
        "vol",
        "amount",
        "adj_factor",
        "open_hfq",
        "open_qfq",
        "close_hfq",
        "close_qfq",
        "high_hfq",
        "high_qfq",
        "low_hfq",
        "low_qfq",
        "pre_close_hfq",
        "pre_close_qfq",
        "macd_dif",
        "macd_dea",
        "macd",
        "kdj_k",
        "kdj_d",
        "kdj_j",
        "rsi_6",
        "rsi_12",
        "rsi_24",
        "boll_upper",
        "boll_mid",
        "boll_lower",
        "cci"
    ])
    return df


# 复权因子
def adj_factor(ts_code, trade_date='', start_date='', end_date=''):
    """
    接口：adj_factor，可以通过数据工具调试和查看数据。
    更新时间：早上9点30分
    描述：获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子。
    积分要求：2000积分起，5000以上可高频调取（经测试，120基础积分可单次调取6000条数据，且每分钟最多访问该接口200次）

    7、Tushare股票行情的前复权机制是什么？
    在Tushare数据接口里，不管是旧版的一些接口还是Pro版的行情接口，都是以用户设定的end_date开始往前复权，
    跟所有行情软件或者财经网站上看到的前复权可能存在差异，因为行情软件都是以最近一个交易日开始往前复权的。
    比如今天是2018年10月26日，您想查2018年1月5日～2018年9月28日的前复权数据，Tushare是先查找9月28日的复权因子，
    从28日开始复权，而行情软件是从10月26日这天开始复权的。同时，Tushare的复权采用“分红再投”模式计算。

    :param ts_code:股票代码
    :param trade_date:交易日期（YYYYMMDD，下同）
    :param start_date:开始日期
    :param end_date:结束日期
    :return:
    """
    df = pro.adj_factor(**{
        "ts_code": ts_code,
        "trade_date": trade_date,
        "start_date": start_date,
        "end_date": end_date,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "adj_factor"
    ])
    return df


if __name__ == '__main__':
    dataframe = pro_bar(ts_code='000001.SZ')
    print(dataframe)
