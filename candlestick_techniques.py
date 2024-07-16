# 日本蜡烛图技术，蜡烛图形态代码化
from datetime import datetime
from mysql_data_processing import read_data, tscode_to_tbname


def windows(df):
    """
    窗口：windows，向上跳空：upward gap，向下跳空：downward gap
    跳空并列阴阳线形态：Tasuki gaps，向上跳空并列阴阳线形态：Upward gapping tasuki，向下跳空并列阴阳线形态：Downward gapping tasuki
    向上跳空并列阳线：Upgap side-by-side white lines，向下跳空并列阳线形态：Downgap side-by-side white lines
    :param df:
    :return:
    """
    windows_date = [[], []]
    count_up = 0
    count_down = 0
    up_tasuki = []
    down_tasuki = []
    upgap = []
    downgap = []
    st = datetime.now()
    for i in range(0, len(df.values) - 2):
        if df.high[i] < df.low[i + 1]:  # 向上跳空
            count_up += 1
            pc = (df.low[i + 1] - df.high[i]) / df.low[i + 1] * 100  # 计算跳空幅度
            windows_date[0].append(df.trade_date[i + 1])
            print(f'该股票在{df.trade_date[i + 1]}向上跳空，跳空幅度为{round(pc, 2)}%')
            if df.high[i] < df.low[i + 2] and df.close[i + 1] > df.open[i + 2] > df.open[i + 1] > df.close[i + 2]:
                up_tasuki.append(df.trade_date[i + 1])
                print(f'{df.trade_date[i + 1]}为向上跳空并列阴阳线形态')
            elif df.high[i] < df.low[i + 2] and df.open[i + 1] == df.open[i + 2] \
                    and df.open[i + 1] < df.close[i + 1] and df.open[i + 2] < df.close[i + 2]:
                upgap.append(df.trade_date[i + 1])
                print(f'{df.trade_date[i + 1]}为向上跳空并列阳线形态')
        elif df.low[i] > df.high[i + 1]:  # 向下跳空
            count_down += 1
            pc = (df.low[i] - df.high[i + 1]) / df.high[i + 1] * 100  # 计算跳空幅度
            windows_date[1].append(df.trade_date[i + 1])
            print(f'该股票在{df.trade_date[i + 1]}向下跳空，跳空幅度为{round(pc, 2)}%')
            if df.low[i] > df.high[i + 2] and df.close[i + 1] < df.open[i + 2] < df.open[i + 1] < df.close[i + 2]:
                down_tasuki.append(df.trade_date[i + 1])
                print(f'{df.trade_date[i + 1]}为向下跳空并列阴阳线形态')
            elif df.low[i] > df.high[i + 2] and df.open[i + 1] == df.open[i + 2] \
                    and df.open[i + 1] < df.close[i + 1] and df.open[i + 2] < df.close[i + 2]:
                downgap.append(df.trade_date[i + 1])
                print(f'{df.trade_date[i + 1]}为向下跳空并列阳线形态')

    print('共耗时：%s，截至目前为止，该股票向上跳空%d次，向下跳空%d' % (datetime.now() - st, count_up, count_down))
    print(f'\n向上跳空并列阴阳线形态有：{up_tasuki}，\n向下跳空并列阴阳线形态有：{down_tasuki}')
    print(f'\n向上跳空并列阳线形态有：{upgap}，\n向下跳空并列阳线形态有：{downgap}')
    pass


def doji(df):
    """
    十字线Doji，北方十字线Northern doji，南方十字线Southern doji，
    蜻蜓十字线Dragonfly doji，墓碑十字线Gravestone doji，长腿十字线Long-legged doji
    :param df:
    :return:
    """
    st = datetime.now()
    doji_ = []
    northern_doji = []
    southern_doji = []
    dragonfly_doji = []
    gravestone_doji = []
    long_legged_doji = []
    for i in range(2, len(df.values)):
        if df.open[i] == df.close[i] and df.high[i] > df.open[i] > df.low[i]:  # 十字线
            if df.open[i - 2] < df.open[i - 1] < df.open[i]:
                northern_doji.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为北方十字线')
            elif df.open[i - 2] > df.open[i - 1] > df.open[i]:
                southern_doji.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为南方十字线')
            else:
                doji_.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为十字线')

            upper_shadow = abs(df.high[i] - df.open[i])
            lower_shadow = abs(df.low[i] - df.open[i])
            if 0.8 < upper_shadow / lower_shadow < 1.2 and df.high[i] > 1.02 * df.open[i] \
                    and df.low[i] > 0.98 * df.open[i]:
                long_legged_doji.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为长腿十字线')
        elif df.high[i] == df.open[i] == df.close[i] > df.low[i]:
            dragonfly_doji.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为蜻蜓十字线')
        elif df.high[i] > df.open[i] == df.close[i] == df.low[i]:
            gravestone_doji.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为墓碑十字线')
        # TODO 北方/南方/蜻蜓/墓碑/长腿十字线的近似形式待整理，并准确分类

    print(f'\n共耗时：{datetime.now() - st}'
          f'\n十字线：{doji_}，\n长腿十字线：{long_legged_doji}'
          f'\n北方十字线：{northern_doji}，\n南方十字线：{southern_doji}'
          f'\n蜻蜓十字线：{dragonfly_doji}，\n墓碑十字线：{gravestone_doji}')
    pass


def umbrella_lines(df):
    """
    伞形线：锤子线hammer&上吊线hanging_man
    :param df:
    :return:
    """
    st = datetime.now()
    hammer_white = []
    hammer_black = []
    hanging_white = []
    hanging_black = []

    for i in range(2, len(df.values)):
        if df.high[i] == df.close[i] and df.low[i] < df.open[i]:
            if df.open[i] - df.low[i] > 2 * (df.close[i] - df.open[i]):
                if df.low[i] < df.low[i - 1] < df.low[i - 2]:
                    hammer_white.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为白色实体的锤子')
                elif df.high[i] > df.high[i - 1] > df.high[i - 2]:
                    hanging_white.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为白色实体的上吊线')
                else:
                    print(f'{df.trade_date[i]}该白色实体伞形线趋势不明显')
            # else:
            #     print(f'{df.trade_date[i]}的下影线不够长，达不到锤子线&上吊线标准')
        elif df.high[i] == df.open[i] and df.low[i] < df.close[i]:
            if df.close[i] - df.low[i] > 2 * (df.open[i] - df.close[i]):
                if df.low[i] < df.low[i - 1] < df.low[i - 2]:
                    hammer_black.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为黑色实体的锤子线')
                elif df.high[i] > df.high[i - 1] > df.high[i - 2]:
                    hanging_black.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为黑色实体的上吊线')
                else:
                    print(f'{df.trade_date[i]}该黑色实体伞形线趋势不明显')
            # else:
            #     print(f'{df.trade_date[i]}的下影线不够长，达不到锤子线&上吊线标准')

    print(f'共耗时：{datetime.now() - st}，'
          f'\n白色锤子线为{hammer_white}，\n白色上吊线为{hanging_white}，'
          f'\n黑色锤子线为{hammer_black}，\n黑色上吊线为{hanging_black}')
    pass


def belt_hold_line(df):
    """
    捉腰带线
    :param df:
    :return:
    """
    st = datetime.now()
    white_belt_line = []
    white_belt_line_ = []
    black_belt_line = []
    black_belt_line_ = []
    for i in range(len(df.values)):
        if df.low[i] + 0.1 * (df.close[i] - df.open[i]) >= df.open[i] and \
                df.close[i] + 0.2 * (df.close[i] - df.open[i]) >= df.high[i] and df.open[i] < df.close[i]:
            if df.low[i] == df.open[i]:
                white_belt_line.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为看涨捉腰带线')
            else:
                white_belt_line_.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为看涨捉腰带线的变体')
        elif df.high[i] <= df.open[i] + 0.1 * (df.open[i] - df.close[i]) and \
                df.close[i] <= df.low[i] + 0.2 * (df.open[i] - df.close[i]) and df.open[i] > df.close[i]:
            if df.high[i] == df.open[i]:
                black_belt_line.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为看跌捉腰带线')
            else:
                black_belt_line_.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为看跌捉腰带线的变体')

    print(f'共耗时：{datetime.now() - st}，'
          f'\n看涨捉腰带线有：{white_belt_line}，\n看涨捉腰带线的变体有：{white_belt_line_}，'
          f'\n看跌捉腰带线有：{black_belt_line}，\n看跌捉腰带线的变体有：{black_belt_line_}，')
    pass


def inverted_hammer_shooting_star(df):
    """
    倒锤子线inverted_hammer <==> 流星线shooting_star
    :return:
    """
    st = datetime.now()
    white_inverted_hammer = []
    black_inverted_hammer = []
    white_shooting_star = []
    black_shooting_star = []
    for i in range(2, len(df.values)):
        if df.open[i] < df.close[i]:  # 白色实体
            if df.low[i - 2] > df.low[i - 1] > df.low[i] == df.open[i] and \
                    df.high[i] - df.close[i] >= 2 * (df.close[i] - df.open[i]):
                white_inverted_hammer.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为白色实体倒锤子线')
            elif df.high[i - 2] < df.high[i - 1] < df.high[i] and df.low[i] == df.open[i] and \
                    df.high[i] - df.close[i] >= 2 * (df.close[i] - df.open[i]):
                white_shooting_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为白色实体流星线')
        elif df.open[i] > df.close[i]:  # 黑色实体
            if df.low[i - 2] > df.low[i - 1] > df.low[i] == df.close[i] and \
                    df.high[i] - df.open[i] >= 2 * (df.open[i] - df.close[i]):
                black_inverted_hammer.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为黑色实体倒锤子线')
            elif df.high[i - 2] < df.high[i - 1] < df.high[i] and df.low[i] == df.close[i] and \
                    df.high[i] - df.open[i] >= 2 * (df.open[i] - df.close[i]):
                black_shooting_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为黑色实体流星线')
    print(f'共耗时：{datetime.now() - st}，'
          f'\n白色倒锤子线有{white_inverted_hammer}，\n白色流星线有{white_shooting_star}，'
          f'\n黑色倒锤子线有{black_inverted_hammer}，\n黑色流星线有{black_shooting_star}')
    pass


def tri_star(df):
    """
    三星形态：tri-star
    :param df:
    :return:
    """
    st = datetime.now()
    tri_star_top = []
    tri_star_bottom = []

    for i in range(1, len(df.values) - 1):
        if df.open[i - 1] == df.close[i - 1] < df.open[i] == df.close[i] > df.open[i + 1] == df.close[i + 1]:
            tri_star_top.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为三星顶部形态')
        elif df.open[i - 1] == df.close[i - 1] > df.open[i] == df.close[i] < df.open[i + 1] == df.close[i + 1]:
            tri_star_bottom.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为三星底部形态')

    print(f'\n共耗时：{datetime.now() - st}，\n三星顶部形态有：{tri_star_top}，\n三星底部形态有：{tri_star_bottom}')
    pass


def three_crows(df):
    """
    三只乌鸦
    :param df:
    :return:
    """
    st = datetime.now()
    zero_limit = -0.03
    three_crows_ = []  # 三只乌鸦
    three_crows_1 = []  # 三只乌鸦的变体（更加疲软）
    for i in range(2, len(df.values)):
        if df.open[i - 2] > df.open[i - 1] > df.open[i] and df.close[i - 2] > df.close[i - 1] > df.close[i] \
                and df.change[i - 2] < zero_limit and df.change[i - 1] < zero_limit and df.change[i] < zero_limit:
            if df.open[i - 2] > df.close[i - 2] > df.open[i - 1] > df.close[i - 1] > df.open[i] > df.close[i]:
                three_crows_1.append(df.trade_date[i])
                print(f'{df.trade_date[i]}完成了更加疲软的三只乌鸦形态')
            else:
                three_crows_.append(df.trade_date[i])
                print(f'{df.trade_date[i]}完成了三只乌鸦形态')

    print(f'\n共耗时：{datetime.now() - st}，\n三只乌鸦形态有：{three_crows_}，\n三只乌鸦的变体有：{three_crows_1}')
    pass


def three_white(df):
    """
    白三兵：three_white_0；前方受阻形态：three_white_1；停顿形态：three_white_2
    :param df:
    :return:
    """
    st = datetime.now()
    three_white_0 = []
    three_white_1 = []
    three_white_2 = []
    three_ = []
    for i in range(2, len(df.values)):
        change_i_2 = df.close[i - 2] - df.open[i - 2]
        change_i_1 = df.close[i - 1] - df.open[i - 1]
        change_i = df.close[i] - df.open[i]
        if df.close[i - 2] < df.close[i - 1] < df.close[i] and change_i_2 > 0 and change_i_1 > 0 and change_i > 0:
            if change_i_2 > change_i_1 > change_i:
                three_white_1.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为前方受阻形态')
            elif change_i_2 > change_i_1 > 2 * change_i:
                three_white_2.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为停顿形态')
            elif change_i_2 <= change_i_1 <= change_i:
                three_white_0.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为白三兵形态')
            else:
                three_.append(df.trade_date[i])
                print(f'{df.trade_date[i]}待定')
    print(f'\n共耗时：{datetime.now() - st}，\n白三兵形态：{three_white_0}'
          f'\n前方受阻形态：{three_white_1}，\n停顿形态：{three_white_2}，\n待定：{three_}')
    pass


def engulfing_pattern(df):
    """
    engulfing_pattern吞没形态；
    bullish_engulfing_pattern看涨吞没形态；
    bearish_engulfing_pattern看跌吞没形态
    :param df:
    :return:
    """
    st = datetime.now()
    bullish_engulfing_pattern = []
    bearish_engulfing_pattern = []
    for i in range(2, len(df.values) - 1):
        change_i = df.close[i] - df.open[i]
        change_i_a1 = df.close[i + 1] - df.open[i + 1]
        mp_i = (df.open[i] + df.close[i]) / 2
        middle_price_i_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        middle_price_i_b2 = (df.open[i - 2] + df.close[i - 2]) / 2

        if change_i < 0 < change_i_a1 and df.close[i + 1] > df.open[i] and df.open[i + 1] < df.close[i] \
                and middle_price_i_b2 > middle_price_i_b1 > mp_i:
            bullish_engulfing_pattern.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看涨吞没形态，形态完成时的收盘价为{df.close[i + 1]}')
        elif change_i > 0 > change_i_a1 and df.close[i + 1] < df.open[i] and df.open[i + 1] > df.close[i] \
                and middle_price_i_b2 < middle_price_i_b1 < mp_i:
            bearish_engulfing_pattern.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看跌吞没形态，形态完成时的收盘价为{df.close[i + 1]}')
    print(f'\n共耗时：{datetime.now() - st}'
          f'\n看涨吞没形态有：{bullish_engulfing_pattern}，\n看跌吞没形态有：{bearish_engulfing_pattern}')

    pass


def dark_cloud_cover(df):
    """
    乌云盖顶
    :param df:
    :return:
    """
    dark_cloud = []
    dark_cloud_variant = []
    for i in range(1, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        middle_price_i_b1 = (df.open[i - 1] + df.close[i - 1]) / 2

        if df.open[i] < df.close[i + 1] < df.close[i] < df.open[i + 1] and middle_price_i_b1 < mp_i:
            if mp_i >= df.close[i + 1]:
                dark_cloud.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为乌云盖顶形态')
            else:
                dark_cloud_variant.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为乌云盖顶形态的变体')
    print(f'\n乌云盖顶形态有：{dark_cloud}，\n乌云盖顶变体形态有：{dark_cloud_variant}')
    pass


def piercing_pattern(df):
    """
    刺透形态：Piercing pattern
    待入线形态：On-neck line
    切入线形态：In-neck line
    插入线形态：Thrusting line
    :param df:
    :return:
    """
    piercing = []
    on_neck_line = []
    in_neck_line = []
    thrusting_line = []

    for i in range(2, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        middle_price_i_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        if df.open[i] > df.close[i + 1] > df.close[i] > df.open[i + 1] and middle_price_i_b1 > mp_i:
            if mp_i < df.close[i + 1]:
                piercing.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为刺透形态')
            elif mp_i >= df.close[i + 1]:
                thrusting_line.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为插入线形态')
        elif df.open[i] > df.close[i] > df.close[i + 1] > df.open[i + 1]:
            on_neck_line.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为待入线形态')
        elif df.open[i] > df.close[i] == df.close[i + 1] > df.open[i + 1]:
            in_neck_line.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为切入线形态')
    print(f'\n刺透形态有：{piercing}，\n待入线形态有：{on_neck_line}'
          f'\n切入线形态有：{in_neck_line}，\n插入线形态有：{thrusting_line}')
    pass


def harami(df):
    """
    孕线形态：Harami
    十字孕线形态：Harami cross
    :param df:
    :return:
    """
    rise_harami = []
    descend_harami = []
    rise_harami_cross = []
    descend_harami_cross = []

    for i in range(2, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        mp_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        mp_b2 = (df.open[i - 2] + df.close[i - 2]) / 2
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_a1 = abs(df.open[i + 1] - df.close[i + 1])

        if df.close[i] > df.open[i + 1] > df.open[i] and df.close[i] > df.close[i + 1] > df.open[i] \
                and mp_b2 < mp_b1 < mp_i and real_body_i > 3 * real_body_a1:
            if df.open[i + 1] == df.close[i + 1]:
                rise_harami_cross.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为上升十字孕线形态')
            else:
                rise_harami.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为上升孕线形态')
        elif df.open[i] > df.open[i + 1] > df.close[i] and df.open[i] > df.close[i + 1] > df.close[i] \
                and mp_b2 > mp_b1 > mp_i and real_body_i > 3 * real_body_a1:
            if df.open[i + 1] == df.close[i + 1]:
                descend_harami_cross.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为下降十字孕线形态')
            else:
                descend_harami.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为下降孕线形态')

    print(f'\n上升孕线形态：{rise_harami}，\n下降孕线形态：{descend_harami}'
          f'\n上升十字孕线形态：{rise_harami_cross}，\n下降十字孕线形态：{descend_harami_cross}')
    pass


def tweezers_top_and_bottom(df):
    """
    平头顶部形态：Tweezers_top
    平头底部形态：Tweezers_bottom
    :param df:
    :return:
    """
    tweezers_top = []
    tweezers_bottom = []
    for i in range(2, len(df.values) - 1):
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_a1 = abs(df.open[i + 1] - df.close[i + 1])
        mp_i = (df.open[i] + df.close[i]) / 2
        mp_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        mp_b2 = (df.open[i - 2] + df.close[i - 2]) / 2
        if df.high[i] == df.high[i + 1] and real_body_i > real_body_a1 \
                and mp_b2 < mp_b1 < mp_i:
            tweezers_top.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为平头顶部形态')
        elif df.low[i] == df.low[i + 1] and real_body_i > real_body_a1 \
                and mp_b2 > mp_b1 > mp_i:
            tweezers_bottom.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为平头底部形态')
    print(f'\n平头顶部形态有：{tweezers_top}，\n平头底部形态有：{tweezers_bottom}')
    pass


def counterattack_lines(df):
    """
    反击线：Counterattack lines
    看涨反击线：bullish counterattack lines
    看跌反击线：bearish counterattack lines
    :param df:
    :return:
    """
    bullish_counterattack = []
    bearish_counterattack = []
    for i in range(2, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        mp_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        mp_b2 = (df.open[i - 2] + df.close[i - 2]) / 2
        if df.open[i] > df.close[i] == df.close[i + 1] > df.open[i + 1] \
                and mp_b2 > mp_b1 > mp_i:
            bullish_counterattack.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看涨反击线形态')
        elif df.open[i] < df.close[i] == df.close[i + 1] < df.open[i + 1] \
                and mp_b2 < mp_b1 < mp_i:
            bearish_counterattack.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看跌反击线形态')
    print(f'\n看涨反击线形态有：{bullish_counterattack}，\n看跌反击线形态有：{bearish_counterattack}')
    pass


def separating_lines(df):
    """
    分手线：Separating lines
    看涨分手线形态：bullish separating lines
    看跌分手线形态：bearish separating lines
    mp：middle_price
    :param df:
    :return:
    """
    bullish_sl = []
    bearish_sl = []
    for i in range(1, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        mp_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        mp_a1 = (df.open[i + 1] + df.close[i + 1]) / 2
        # middle_price_a2 = (df.open[i + 2] + df.close[i + 2]) / 2
        if df.close[i] < df.open[i] == df.open[i + 1] < df.close[i + 1] and mp_b1 < mp_i < mp_a1:
            bullish_sl.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看涨的分手线形态')
        elif df.close[i] > df.open[i] == df.open[i + 1] > df.close[i + 1] and mp_b1 > mp_i > mp_a1:
            bearish_sl.append(df.trade_date[i])
            print(f'{df.trade_date[i]}为看跌的分手线形态')
    print(f'\n看涨分手线形态有：{bullish_sl}，\n看跌分手线形态有：{bearish_sl}')
    pass


def star(df):
    """
    星线：Star
    十字星线：Doji_star
    :param df:
    :return:
    """
    upward_star = []
    downward_star = []
    upward_doji_star = []
    downward_doji_star = []
    for i in range(2, len(df.values) - 1):
        mp_i = (df.open[i] + df.close[i]) / 2
        mp_b1 = (df.open[i - 1] + df.close[i - 1]) / 2
        mp_b2 = (df.open[i - 2] + df.close[i - 2]) / 2
        mp_a1 = (df.open[i + 1] + df.close[i + 1]) / 2
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_a1 = abs(df.open[i + 1] - df.close[i + 1])
        if mp_b2 < mp_b1 < mp_i < mp_a1 and real_body_i > 2 * real_body_a1:
            if df.open[i] < df.close[i] < df.open[i + 1] < df.close[i + 1]:
                upward_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为上升趋势中的星线')
            elif df.open[i] < df.close[i] < df.open[i + 1] == df.close[i + 1]:
                upward_doji_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为上升趋势中的十字星线')
        elif mp_b2 > mp_b1 > mp_i > mp_a1 and real_body_i > 2 * real_body_a1:
            if df.open[i] > df.close[i] > df.close[i + 1] > df.open[i + 1]:
                downward_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为下降趋势中的星线')
            elif df.open[i] > df.close[i] > df.close[i + 1] > df.open[i + 1]:
                downward_doji_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为下降趋势中的十字星线')
    print(f'\n上升趋势中的星线有：{upward_star}，\n下降趋势中的星线有：{downward_star}')
    print(f'\n上升趋势中的十字星线有：{upward_doji_star}，\n下降趋势中的十字星线有：{downward_doji_star}')
    pass


def upside_gap_two_crows(df):
    """
    向上跳空两只乌鸦：Upside gap two crows
    :param df:
    :return:
    """
    upside_two_crows = []
    for i in range(len(df.values) - 2):
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_a1 = abs(df.open[i + 1] - df.close[i + 1])
        real_body_a2 = abs(df.open[i + 2] - df.close[i + 2])
        if real_body_i > real_body_a2 > real_body_a1 and \
                df.open[i + 2] > df.open[i + 1] > df.close[i + 1] > df.close[i + 2] > df.close[i] > df.open[i]:
            print(f'{df.trade_date[i]}为向上跳空两只乌鸦')
            upside_two_crows.append(df.trade_date[i])
    print(f'向上跳空两只乌鸦有：{upside_two_crows}')
    pass


def morning_evening_star(df):
    """
    启明星形态：Morning star
    黄昏星形态：Evening star
    十字启明星形态：Morning doji star
    十字黄昏星形态：Evening doji star
    弃婴形态：Abandoned baby
    :param df:
    :return:
    """
    morning_star = []
    morning_doji_star = []
    evening_star = []
    evening_doji_star = []
    up_abandoned_baby = []
    down_abandoned_baby = []
    for i in range(len(df.values) - 2):
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_a1 = abs(df.open[i + 1] - df.close[i + 1])
        real_body_a2 = abs(df.open[i + 2] - df.close[i + 2])
        middle_price_i = (df.open[i] + df.close[i]) / 2
        if df.open[i] > df.close[i + 2] > df.close[i] and df.close[i + 2] > df.open[i + 2] and \
                real_body_i > real_body_a2 > real_body_a1 and df.close[i] > df.open[i + 1] and \
                df.close[i] > df.close[i + 1] and df.close[i + 2] > middle_price_i:
            if df.open[i + 1] == df.close[i + 1]:
                if df.low[i] > df.high[i + 1] and df.low[i + 2] > df.high[i + 1]:
                    down_abandoned_baby.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为弃婴底部形态')
                else:
                    morning_doji_star.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为十字启明星形态')
            else:
                morning_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为启明星形态')
        elif df.open[i] < df.close[i + 2] < df.close[i] and df.close[i + 2] < df.open[i + 2] and \
                real_body_i > real_body_a2 > real_body_a1 and df.close[i] < df.open[i + 1] and \
                df.close[i] < df.close[i + 1] and df.close[i + 2] < middle_price_i:
            if df.open[i + 1] == df.close[i + 1]:
                if df.high[i] > df.low[i + 1] and df.high[i + 2] > df.low[i + 1]:
                    up_abandoned_baby.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为弃婴顶部形态')
                else:
                    evening_doji_star.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为十字黄昏星形态')
            else:
                evening_star.append(df.trade_date[i])
                print(f'{df.trade_date[i]}为黄昏星形态')
    print(f'\n启明星形态有：{morning_star}'
          f'\n十字启明星形态有：{morning_doji_star}'
          f'\n弃婴底部形态有：{down_abandoned_baby}'
          f'\n黄昏星形态有：{evening_star}'
          f'\n十字黄昏星形态有：{evening_doji_star}'
          f'\n弃婴顶部形态有：{up_abandoned_baby}')
    pass


def three_methods(df):
    """
    三法形态：Three methods
    上升三法形态：bullish three methods
    下降三法形态：bearish three methods
    :param df:
    :return:
    """
    bullish_three_methods = []
    bearish_three_methods = []
    for i in range(len(df.values) - 4):
        middle_price_i_a1 = (df.open[i + 1] + df.close[i + 1]) / 2
        middle_price_i_a2 = (df.open[i + 2] + df.close[i + 2]) / 2
        middle_price_i_a3 = (df.open[i + 3] + df.close[i + 3]) / 2
        real_body_i = abs(df.open[i] - df.close[i])
        real_body_i_a1 = abs(df.open[i + 1] - df.close[i + 1])
        real_body_i_a2 = abs(df.open[i + 2] - df.close[i + 2])
        real_body_i_a3 = abs(df.open[i + 3] - df.close[i + 3])
        # real_body_i_a4 = abs(df.open[i + 4] - df.close[i + 4])
        if real_body_i > real_body_i_a1 and real_body_i > real_body_i_a2 and real_body_i > real_body_i_a3:
            if df.close[i + 4] > df.close[i] > df.open[i] and df.close[i + 4] > df.open[i + 4] > df.close[i + 3]:
                if middle_price_i_a1 > middle_price_i_a2 > middle_price_i_a3 and \
                        df.open[i + 1] < df.high[i] and df.close[i + 3] > df.low[i]:
                    bullish_three_methods.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为上升三法形态')
            elif df.close[i + 4] < df.close[i] < df.open[i] and df.close[i + 4] < df.open[i + 4] < df.close[i + 3]:
                if middle_price_i_a1 < middle_price_i_a2 < middle_price_i_a3 and \
                        df.open[i + 1] > df.low[i] and df.close[i + 3] < df.high[i]:
                    bearish_three_methods.append(df.trade_date[i])
                    print(f'{df.trade_date[i]}为下降三法形态')
    print(f'\n上升三法形态有：{bullish_three_methods}')
    print(f'\n下降三法形态有：{bearish_three_methods}')
    pass


if __name__ == '__main__':
    # ts_code = '300964.SZ'
    ts_code = '601882.SH'
    dataframe = read_data(tscode_to_tbname(ts_code=ts_code))
    # windows(dataframe)
    # doji(dataframe)
    # umbrella_lines(dataframe)
    # belt_hold_line(dataframe)
    # inverted_hammer_shooting_star(dataframe)
    # tri_star(dataframe)
    # three_crows(dataframe)
    # three_white(dataframe)
    engulfing_pattern(dataframe)    # 吞没形态
    # dark_cloud_cover(dataframe)
    # piercing_pattern(dataframe)
    # harami(dataframe)
    # tweezers_top_and_bottom(dataframe)
    # counterattack_lines(dataframe)
    # separating_lines(dataframe)
    # star(dataframe)
    # upside_gap_two_crows(dataframe)
    # morning_evening_star(dataframe)
    # three_methods(dataframe)
