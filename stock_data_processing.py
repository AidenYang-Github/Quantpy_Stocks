# 从.xls文件中采集股票数据
import os
import xlrd
import matplotlib.pyplot as plt
import tushare as ts

from TOKEN_ID import TOKEN

STOCK_PATH = r'D:\A Skateboy S\Stock_related\stockData\allstock'
STOCK_NAME = '300750.SZ'

FILE_PATH = r'D:\A_Skateboy_Dataset'
FILE_FORMAT = '.xlsx'

ts.set_token(TOKEN)
pro = ts.pro_api()


class STOCK:
    def collections(self, sp, si):
        """
        stock collection
        :param sp: stock path
        :param si: stock id
        :return: stock content
        """
        stock_dir = os.path.join(sp, si)
        workbook = xlrd.open_workbook(stock_dir)
        worksheet = workbook.sheet_by_index(0)
        return worksheet

    def tushare_api(self):
        data = pro.stock_basic(exchange='', list_status='L', fields='ts_code, symbol, name, area, industry, list_date')
        return data


def ts_get_stocks_list():
    """
    获取股票列表
    :return:
    """
    pro = ts.pro_api()
    df = pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "market",
        "list_date",
        "fullname",
        "exchange"
    ])
    return df


def ts_get_stocks_daily(ts_code):
    """
    获取股票日线行情
    :param ts_code:
    :return:
    """
    pro = ts.pro_api()
    df = pro.daily(ts_code=ts_code)

    # 将股票日线行情保存成excel
    excel_file_generating(df, ts_code)
    return df


def excel_file_generating(data_frame, stock_name):
    """
    生成excel表格
    :param data_frame: 股票的一系列数据
    :param stock_name: 股票的ts代码
    :return:
    """
    file_dir = os.path.join(FILE_PATH, stock_name + FILE_FORMAT)
    data_frame.to_excel(file_dir)
    return


def get_whole_stocks_excel():
    """
    获取所有股票信息
    :return:
    """
    list_df = ts_get_stocks_list()
    ts_code_arr = list_df.ts_code.values

    for ts_code in ts_code_arr:
        ts_get_stocks_daily(ts_code)
    return list_df, ts_code_arr


if __name__ == '__main__':
    stock = STOCK()

    # FUNCTION collections
    """
    sheet = stock.collections(STOCK_PATH, stock_name + '.xls')
    rows = sheet.row_values(0)
    cols = sheet.col_values(2)
    plt.figure()
    plt.grid()
    plt.plot(cols[::-1][:-1])
    plt.show()
    """

    # FUNCTION tushare_api
    """
    DF = stock.tushare_api()
    """

    # main
    # rs = ts_get_stocks_daily(STOCK_NAME)
    # ts_get_stocks_list()
    # get_whole_stocks_excel()
    pass
