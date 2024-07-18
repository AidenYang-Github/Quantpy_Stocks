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
