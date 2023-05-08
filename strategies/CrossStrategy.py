from typing import Tuple

import numpy as np

from strategies.Strategy import Strategy
from datamodel import OrderDepth, TradingState


class CrossStrategy(Strategy):
    def __init__(self, name: str, min_req_price_difference: int, max_position: int):
        super().__init__(name, max_position)
        self.strategy_start_day = 2

        self.old_asks = []
        self.old_bids = []
        self.min_req_price_difference = min_req_price_difference

    def trade(self, trading_state: TradingState, orders: list):
        order_depth: OrderDepth = trading_state.order_depths[self.name]
        self.cache_prices(order_depth)
        if len(self.old_asks) < self.strategy_start_day or len(self.old_bids) < self.strategy_start_day:
            return

        avg_bid, avg_ask = self.calculate_prices(self.strategy_start_day)

        if len(order_depth.sell_orders) != 0:
            best_asks = sorted(order_depth.sell_orders.keys())

            i = 0
            while i < self.trade_count and len(best_asks) > i and best_asks[
                i] - self.min_req_price_difference < avg_bid:
                if self.prod_position == self.max_pos:
                    break
                self.buy_product(best_asks, i, order_depth, orders)
                i += 1

        if len(order_depth.buy_orders) != 0:
            best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

            i = 0
            while i < self.trade_count and len(best_bids) > i and best_bids[
                i] + self.min_req_price_difference > avg_ask:
                if self.prod_position == -self.max_pos:
                    break
                self.sell_product(best_bids, i, order_depth, orders)

                i += 1
        #
        # # Add some new orders on our own with very profitable prices hoping some stupid bots fill them
        # if avg_bid == avg_bid and avg_ask == avg_ask:
        #     mid_price = (avg_bid + avg_ask) / 2
        #     orders.append(Order(self.name, mid_price - self.spread,
        #                         max(0, min(self.max_own_order, self.max_pos - self.prod_position,
        #                                    self.max_pos - orig_position,
        #                                    self.max_pos - orig_position - new_buy_orders))))
        #     orders.append(Order(self.name, mid_price + self.spread,
        #                         -max(0, min(self.max_own_order, self.max_pos + self.prod_position,
        #                                     self.max_pos + orig_position,
        #                                     self.max_pos + orig_position - new_sell_orders))))

    def calculate_prices(self, days: int) -> Tuple[int, int]:
        # Calculate the average bid and ask price for the last days

        relevant_bids = []
        for bids in self.old_bids[-days:]:
            relevant_bids.extend([(value, bids[value]) for value in bids])
        relevant_asks = []
        for asks in self.old_asks[-days:]:
            relevant_asks.extend([(value, asks[value]) for value in asks])

        avg_bid = np.average([x[0] for x in relevant_bids], weights=[x[1] for x in relevant_bids])
        avg_ask = np.average([x[0] for x in relevant_asks], weights=[x[1] for x in relevant_asks])

        return avg_bid, avg_ask

    def cache_prices(self, order_depth: OrderDepth):
        sell_orders = order_depth.sell_orders
        buy_orders = order_depth.buy_orders

        self.old_asks.append(sell_orders)
        self.old_bids.append(buy_orders)
