from strategies.Strategy import Strategy
from datamodel import TradingState, OrderDepth


class FixedStrategy(Strategy):
    def __init__(self, name: str, max_pos: int):
        super().__init__(name, max_pos)
        self.pearls_price = 10000
        self.pearls_diff = 4

    def trade(self, trading_state: TradingState, orders: list):
        order_depth: OrderDepth = trading_state.order_depths[self.name]
        # Check if there are any SELL orders
        if len(order_depth.sell_orders) > 0:
            #
            # self.cache_prices(order_depth)
            # Sort all the available sell orders by their price
            best_asks = sorted(order_depth.sell_orders.keys())

            # Check if the lowest ask (sell order) is lower than the above defined fair value
            i = 0
            while i < self.trade_count and best_asks[i] < self.pearls_price:
                # Fill ith ask order if it's below the acceptable
                if self.prod_position == self.max_pos:
                    break
                self.buy_product(best_asks, i, order_depth, orders)
                i += 1
        if len(order_depth.buy_orders) != 0:
            best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

            i = 0
            while i < self.trade_count and best_bids[i] > self.pearls_price:
                if self.prod_position == -self.max_pos:
                    break
                self.sell_product(best_bids, i, order_depth, orders)
                i += 1
        # self.add_own_orders(orders)

    # def add_own_orders(self, orders):
    #     # Add some new orders on our own with very profitable prices hoping some silly bots fill them
    #     orders.append(
    #         Order(self.name, self.pearls_price - self.pearls_diff, max(0, min(20, self.max_pos - self.prod_position,
    #                                                                           self.max_pos - orig_position,
    #                                                                           self.max_pos - orig_position - new_buy_orders))))
    #     orders.append(
    #         Order(self.name, self.pearls_price + self.pearls_diff, -max(0, min(20, self.max_pos + self.prod_position,
    #                                                                            self.max_pos + orig_position,
    #                                                                            self.max_pos + orig_position - new_sell_orders))))

    def cache_prices(self, order_depth: OrderDepth):
        sell_orders = order_depth.sell_orders
        buy_orders = order_depth.buy_orders

        self.old_asks.append(sell_orders)
        self.old_bids.append(buy_orders)