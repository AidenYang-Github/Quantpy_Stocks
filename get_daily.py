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

    et = datetime.now()
    print('\n')
    if len(update_stocks_list) != 0:
        print(f'本次更新股票：{update_stocks_list}')
    if len(new_stocks_list) != 0:
        print('本次新增股票:\n', new_stocks_list)
    print('%d stocks are imported into the database.' % count)
    print('It takes {} to get stocks!'.format(et - st))