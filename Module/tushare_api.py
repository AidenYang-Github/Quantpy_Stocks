"""
# Tushare接口说明
# pro.stock_basic()：接口每小时只能调用一次
# pro.daily()：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
# pro.trade_cal()：需2000积分
"""
import tushare as ts

from TOKEN_ID import TOKEN

# 初始化pro接口
pro = ts.pro_api(TOKEN)


class TuShareAPI:
    def __init__(self):
        pass


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


if __name__ == '__main__':
    dataframe = pro_bar(ts_code='000001.SZ')
    print(dataframe)
