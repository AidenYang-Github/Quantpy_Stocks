# ========================================================
# 止盈止损规则
# 横向区间止盈规则：卖出价=最高价*90%+买入价*10%
# 上升趋势只因规则：卖出价=最高价*60%+买入价*40%
# ========================================================
import math


def rules():
    max_price = float(input('最高价='))
    buy_price = float(input('买入价='))

    horizon_sell_price = round(0.9 * max_price + 0.1 * buy_price, 2)  # horizontal plate 横盘
    upward_sell_price = round(0.6 * max_price + 0.4 * buy_price, 2)  # upward trend 上升趋势

    print(f'横向区间卖出价格：{horizon_sell_price}\n'
          f'上升趋势卖出价格：{upward_sell_price}')


# ========================================================

# ========================================================
# 交易股票的整个过程费用记录

# === COST ===
Mini_Commission = 5.0  # 最低佣金

# === RATE ===
Commission_Rate = 0.00025  # 佣金率（旧：0.00087339999）
Stamp_Duty_Rate = 0.5 / 1000  # 印花税率SSD
Transfer_Rate = 0.01 / 1000  # 过户费率


class TradeCalculate:
    def __init__(self):
        """
        tp_of_stocks:total_prices_of_stocks: 目前已经购入股票的总金额
        tcat_of_stocks:total_cost_after_tax_of_stocks: 目前已经购入股票的税后总金额
        taf:total_account_funds: 账户总资金
        """
        self.mc = Mini_Commission
        self.cr = Commission_Rate
        self.sdr = Stamp_Duty_Rate
        self.tr = Transfer_Rate

        self.num_of_stocks = 0.0  # 目前已经购入的股票总数
        self.tp_of_stocks = 0.0  # total_prices_of_stocks: 目前已经购入股票的总金额
        self.tcat_of_stocks = 0.0
        self.taf = float(input('账户中初始资金：[默认为0.0]') or '0.0')  #

    def buy_func(self):
        """买入功能
        买入股票后的价格
        :return:
                cost_unit_price: 每股成本价
                total_cost: 买入股票的总成本价
        """
        purchase_price = float(input('买入价格：'))  # 成交价格
        num_of_purchased = float(input('买入股数：'))  # 成交数量
        purchase_transaction_amount = round(purchase_price * num_of_purchased, 2)  # 成交金额（买入成交额）

        # 佣金和过户费计算
        buy_commission = max(purchase_transaction_amount * self.cr, self.mc)  # 根据买入股票成交额设置的佣金
        transfer_fee = self.tr * purchase_transaction_amount  # 买入股票的过户费

        # 成本价和税后总价计算
        cost_unit_price = purchase_price + round(buy_commission / num_of_purchased, 3)  # 每股成本价
        total_cost = purchase_transaction_amount + buy_commission + transfer_fee  # 发生金额（总成本价）

        #
        self.num_of_stocks += num_of_purchased  # 将成交的股票数加入总购入的股票数中
        self.tp_of_stocks += purchase_transaction_amount  # 将成交的股票金额加入总购入的股票金额中
        self.tcat_of_stocks += total_cost  # 将股票成交后的税后金额加入总购入股票的税后总金额
        self.taf -= total_cost  # 账户总资金余额
        print(f'单股成本价:{cost_unit_price}\n'
              f'总持有股数：{int(self.num_of_stocks)}\n'
              f'总税后成本价：{total_cost}\n'
              f'账户总资金余额：{round(self.taf, 4)}\n')

        # 调用{保本价格指导}
        TradeCalculate.break_even_price_guidance(self)

        return cost_unit_price, total_cost

    def sell_func(self):
        """卖出功能
        卖出股票后的剩余股票数和总金额
        :return:
        """
        # 实际卖出股票后的价格
        sale_price = float(input('卖出价格：'))  # 卖出成交价格
        num_of_sold = float(input('卖出股数：'))  # 卖出股数

        if self.num_of_stocks >= num_of_sold:
            """
            rsta:real_sale_transaction_amount
            rsc:real_sale_commission
            rtpat:real_total_price_after_tax
            rbe:real_break-even
            """
            rsta = round(sale_price * num_of_sold, 2)  # 实际卖出成交额
            rsc = max(round(rsta * self.cr, 4), self.mc)  # 实际卖出所需缴纳的佣金
            rtpat = rsta * (1 - self.sdr - self.tr) - rsc  # 实际卖出股票后的税后总金额
            rbe = round(rtpat - self.tcat_of_stocks * num_of_sold / self.num_of_stocks, 4)  # 实际盈亏
            print(f'当以每股￥{sale_price}的价格卖出时，可得￥{round(rtpat, 4)}税后总额\n'
                  f'实际盈亏为￥{rbe}\n')

            self.num_of_stocks -= num_of_sold  # 将卖出的股数从总股数中减去
            self.tp_of_stocks -= rsta  # 将卖出股票的金额从总金额中减去
            self.tcat_of_stocks -= rtpat  # 将卖出股票的税后金额从总税后金额中减去
            self.taf += rtpat
            if int(self.num_of_stocks) > 0 and round(self.tcat_of_stocks, 4) > 0.0:
                print(f'股市中剩余{int(self.num_of_stocks)}股，剩余总资金为{round(self.tcat_of_stocks, 4)}\n'
                      f'账户总资金余额：{round(self.taf, 4)}\n')
            elif int(self.num_of_stocks) == 0 and round(self.tcat_of_stocks, 4) <= 0.0:
                print(f'股市中该股票已清仓\n\n'
                      f'[账户总资金余额：{round(self.taf, 4)}]')
                pass

            if self.num_of_stocks > 0.0:
                TradeCalculate.break_even_price_guidance(self)

            return rtpat, self.num_of_stocks
        else:
            print(f'卖出股数超过所拥有总股数！')

    def break_even_price_guidance(self):
        """保本价格指导
        保本卖出股票的价格（盈亏平衡价格指导）
        tcat:total_cost_after_tax_of_stocks
        :return:
                sell_price: 确保卖出后不亏本的每股报价
                total_price_at:  卖出股票后所得的税后总金额（total_price_after_tax）
        """
        # TODO[FINISH] sale_commission需要修改卖出的佣金，后续再考虑，关键节点在于卖出的成交额是否超过（5/commission_rate）
        # 通过总成交金额来判断所需上缴的佣金金额，以成交金额￥20000为界，＜则执行if，＞则执行else
        if self.tp_of_stocks <= self.mc / self.cr:
            # sale_commission = max(self.tp_of_stocks * self.cr, self.mc)  # 卖出所有股票所需要上交的佣金
            sale_commission = self.mc
            sell_price = (self.tcat_of_stocks + sale_commission) / (
                    self.num_of_stocks * (1 - self.sdr - self.tr))  # 卖出价格
            total_price_at = sell_price * self.num_of_stocks * (1 - self.sdr - self.tr) - sale_commission  # 卖出税后总价
        else:
            sell_price = self.tcat_of_stocks / (self.num_of_stocks * (1 - self.sdr - self.tr - self.cr))
            total_price_at = sell_price * self.num_of_stocks * (1 - self.sdr - self.tr - self.cr)  # 卖出税后总价

        print(f'------------------------------------\n'
              f'保本卖出价格：{sell_price}\n'
              f'卖出所有股票后所得的税后总金额：{round(total_price_at, 4)}\n'
              f'综上，卖出价格至少≥{round(math.ceil(sell_price * 100) / 100, 2)}才能保证不亏本！')
        return sell_price, total_price_at


def main():
    # buy_sale_point_calculate()
    trade = TradeCalculate()
    while True:
        if trade.num_of_stocks == 0.0:
            trade.buy_func()
        else:
            print('\n=====================================')
            if input('买入[1]or卖出[0]：') == '1':
                trade.buy_func()
            else:
                trade.sell_func()
                if trade.num_of_stocks == 0.0:
                    print('\n=====================================\n'
                          '该股票已清仓，整个交易流程结束')
                    break
    pass


if __name__ == '__main__':
    main()
