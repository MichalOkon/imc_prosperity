from typing import List

import numpy as np

from datamodel import TradingState, Trade, OrderDepth
from strategies.strategy import Strategy


class DiffStrategy(Strategy):
    def __init__(self, name: str, max_position: int, derivative_resolution: int, diff_thresh: int):
        super().__init__(name, max_position)
        self.derivative_resolution: int = derivative_resolution
        self.diff_thresh: int = diff_thresh

    def trade(self, trading_state: TradingState, orders: list):
        order_depth: OrderDepth = trading_state.order_depths[self.name]
        self.cache_purchased_prices(trading_state)
        self.calculate_means()

        diff = self.get_price_difference()

        if diff < -self.diff_thresh and len(order_depth.sell_orders) != 0:
            self.continuous_buy(order_depth, orders)

        if diff > self.diff_thresh and len(order_depth.buy_orders) != 0:
            self.continuous_sell(order_depth, orders)

    def get_price_difference(self) -> float:
        # Calculate the difference between the current mean and the mean from
        # self.derivative_resolution days ago
        if len(self.cached_means) < self.derivative_resolution + 1:
            old_mean = self.cached_means[0]
        else:
            old_mean = self.cached_means[-self.derivative_resolution]
        diff = self.cached_means[-1] - old_mean
        return diff

    def calculate_means(self):
        #
        if len(self.cached_prices) == 0:
            self.cached_means.append(0)

        else:
            relevant_prices = []
            for day_prices in self.cached_prices[max(-len(self.cached_prices), -1):]:
                for price in day_prices:
                    relevant_prices.append(price)
            prices = np.array([x[1] for x in relevant_prices])
            quantities = np.abs(np.array([x[0] for x in relevant_prices]))

            self.cached_means.append(np.average(prices, weights=quantities))

    def cache_purchased_prices(self, state: TradingState) -> None:
        # Caches prices of bought and sold products

        market_trades = state.market_trades
        own_trades = state.own_trades

        prod_trades: List[Trade] = own_trades.get(self.name, []) + market_trades.get(self.name, [])

        if len(prod_trades) > 0:
            prices = [(trade.quantity, trade.price) for trade in prod_trades]
            self.cached_prices.append(prices)
