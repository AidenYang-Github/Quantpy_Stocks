# 	1）近一年涨跌幅>0；
# 	2）近一年涨跌次数超过一半；

import pandas as pd
from mysql_data_processing import show_tables, read_data, write_data
from datetime import datetime


def stock_selection():
    """
    # 筛选主板、中小板和创业板的股票
    :return: MBM：主板, SME：中小板, GEM：创业板
    """
    tb_list = show_tables()

    MBM = []
    SME = []
    GEM = []
    for tb_ in tb_list:
        tb_5 = tb_[:5]
        if tb_5 == 'sz000' or tb_5 == 'sz001' or tb_5 == 'sh600' or tb_5 == 'sh601' or tb_5 == 'sh603' or tb_5 == 'sh605':
            MBM.append(tb_)
        elif tb_5 == 'sz002' or tb_5 == 'sz003':
            SME.append(tb_)
        elif tb_5 == 'sz300' or tb_5 == 'sz301':
            GEM.append(tb_)
    print(f'\n符合<主板/中小板/创业板>条件的股票共：{len(MBM) + len(SME) + len(GEM)}支，'
          f'其中主板：{len(MBM)}支，中小板：{len(SME)}支，创业板：{len(GEM)}支')
    return {'MBM': MBM, 'SME': SME, 'GEM': GEM}


def main():
    loc_date = datetime.now().strftime('%Y%m%d')  # 当前日期
    different_market = stock_selection()

    # 根据近一年涨跌幅数据筛选
    amount = 250  # 需要获取的数量
    all_market_res = []
    for key in different_market.keys():
        st = datetime.now()
        suitable_count = 0  # 符合要求的股票数量
        dtype_error = 0
        suitable_tscode = []  # 符合要求的股票代码合集
        unsuitable_tscode = []  # 不符合要求的股票代码合集
        res_info_list = []  # 符合要求的股票数据合集
        for tscode in different_market[key]:
            zero = 0
            positive = 0
            negative = 0
            df = read_data(tscode)
            if len(df) >= amount:
                change_250 = df.change.values[-amount:]  # 取近一年的涨跌额
                one_year_ago_close = df.close.values[-amount]  # amount天之前的收盘价
                current_close = df.close.values[-1]  # 当前的收盘价
                wfq_close_change = round(current_close - one_year_ago_close, 2)
                if change_250.dtype != 'float64':  # 有的字段类型不一致，将object类型的字段转换成float64
                    change_250 = df.change[-amount:].apply(pd.to_numeric)

                if change_250.dtype == 'float64':
                    chg_250_sum = round(sum(change_250), 3)
                    for chg in change_250:
                        if chg > 0.0:
                            positive += 1
                        elif chg == 0.0:
                            zero += 1
                        else:
                            negative += 1

                    if positive >= negative and chg_250_sum > 0.0:
                        suitable_count += 1
                        suitable_tscode.append(tscode)
                        change_amount = round(sum(change_250), 2)
                        price_limit = round(chg_250_sum / df.close.values[-amount] * 100, 2)
                        positive_proportion = round(positive / (positive + negative + zero) * 100, 2)  # 正向占比
                        negative_proportion = round(negative / (positive + negative + zero) * 100, 2)  # 负向占比

                        res_info_list.append([tscode, one_year_ago_close, current_close, wfq_close_change,
                                              change_amount, price_limit, positive, negative, zero,
                                              positive_proportion, negative_proportion, key])
                        # print(f'{tscode}在第{amount}个交易日之前的收盘价为：{one_year_ago_close}，当前收盘价为：{current_close}，'
                        #       f'近一年的涨跌额为{change_amount}，相较一年前涨跌幅：{price_limit}%，'
                        #       f'上涨{positive}天，下跌{negative}天，持平{zero}天，上涨天数占比：{positive_proportion}%')
                else:
                    dtype_error += 1
                    unsuitable_tscode.append(tscode)
                    print(f'{tscode}的dtype为{change_250.dtype}')

        print(f'共计{suitable_count}支{key}符合条件，{dtype_error}支dtype错误，共耗时：{datetime.now() - st}')
        # res_df = pd.DataFrame(res_info_list, columns=['ts_code', 'one_year_ago_close', 'current_close',
        #                                               'wfq_close_change', 'change_amount', 'price_limit', 'positive',
        #                                               'negative', 'zero', 'ps_pro%', 'ng_pro%', 'mkt_type'])
        """
        'ts_code', 股票代码
        'one_year_ago_close', 一年前的收盘价 
        'current_close', 目前的收盘价
        'wfq_close_change', 未复权的涨跌额
        'change_amount', 涨跌额
        'price_limit', 一年内的价格涨幅
        'positive', 上涨的天数
        'negative', 下跌的天数
        'zero', 停牌或未涨跌天数
        'ps_pro%', 上涨天数占比
        'ng_pro%', 下跌天数占比
        'mkt_type' 股票市场类型
        """
        res_df = pd.DataFrame(res_info_list,
                              columns=['ts_code', 'oya_cls', 'now_cls', 'wfq_cls_chg', 'change_',
                                       'price_lmt', 'pst', 'ngt', 'zero', 'ps_pro%', 'ng_pro%', 'mkt_tp'])
        all_market_res.extend(res_info_list)

        write_data(res_df, f'all_{key.lower()}_{loc_date}')

    all_market_res_df = pd.DataFrame(all_market_res,
                                     columns=['ts_code', 'oya_cls', 'now_cls', 'wfq_cls_chg', 'change_',
                                              'price_lmt', 'pst', 'ngt', 'zero', 'ps_pro%', 'ng_pro%', 'mkt_type'])
    write_data(all_market_res_df, f'all_market_{loc_date}')
    pass


if __name__ == '__main__':
    main()
