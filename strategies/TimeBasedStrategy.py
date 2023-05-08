from datamodel import TradingState
from strategies.CrossStrategy import CrossStrategy


class TimeBasedStrategy(CrossStrategy):
    def __init__(self, name, min_req_price_difference, max_position):
        super().__init__(name, min_req_price_difference, max_position)
        self.berries_ripe_timestamp = 350000
        self.berries_peak_timestamp = 500000
        self.berries_sour_timestamp = 650000

    def trade(self, trading_state: TradingState, orders: list):
        order_depth = trading_state.order_depths[self.name]
        if 0 < trading_state.timestamp - self.berries_ripe_timestamp < 5000:
            print("BERRIES ALMOST RIPE")
            # start buying berries if they start being ripe
            if len(order_depth.sell_orders) != 0:
                best_asks = sorted(order_depth.sell_orders.keys())

                i = 0
                while i < self.trade_count and len(best_asks) > i:
                    if self.prod_position == -self.max_pos:
                        break
                    self.buy_product(best_asks, i, order_depth, orders)
                    i += 1
        elif 0 < trading_state.timestamp - self.berries_peak_timestamp < 5000:
            print("BERRIES READY TO SELL")
            if len(order_depth.buy_orders) != 0:
                best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                i = 0
                while i < self.trade_count and len(best_bids) > i:
                    if self.prod_position == -self.max_pos:
                        break
                    self.sell_product(best_bids, i, order_depth, orders)
                    i += 1
        else:
            super().trade(trading_state, orders)
