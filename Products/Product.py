import numpy as np

from datamodel import OrderDepth, Order


class Product:
    def __init__(self, name: str, prod_position: int, new_buy_orders: int, new_sell_orders: int):
        self.name = name
        self.cached_prices: list = []
        self.cached_means: list = []
        self.max_pos: int = 0

        self.prod_position: int = prod_position
        self.new_buy_orders: int = new_buy_orders
        self.new_sell_orders: int = new_sell_orders

    def sell_product(self, best_bids, i, order_depth, orders):
        # Sell product at best bid
        best_bid_volume = order_depth.buy_orders[best_bids[i]]
        if self.prod_position - best_bid_volume >= -self.max_pos:
            orders.append(Order(self.name, best_bids[i], -best_bid_volume))
            self.prod_position += -best_bid_volume
            self.new_sell_orders += best_bid_volume

        else:
            # Sell as much as we can without exceeding the self.max_pos[product]
            vol = self.prod_position + self.max_pos
            orders.append(Order(self.name, best_bids[i], -vol))
            self.prod_position += -vol
            self.new_sell_orders += vol

    def buy_product(self, best_asks, i, order_depth, orders):
        # Buy product at best ask
        best_ask_volume = order_depth.sell_orders[best_asks[i]]
        if self.prod_position - best_ask_volume <= self.max_pos:
            orders.append(Order(self.name, best_asks[i], -best_ask_volume))
            self.prod_position += -best_ask_volume
            self.new_buy_orders += -best_ask_volume
        else:
            # Buy as much as we can without exceeding the self.max_pos[product]
            vol = self.max_pos - self.prod_position
            orders.append(Order(self.name, best_asks[i], vol))
            self.prod_position += vol
            self.new_buy_orders += vol


class DiffStrategy(Product):
    def __init__(self, derivative_resolution: int, diff_thresh: int, trade_count: int, name: str, prod_position: int,
                 new_buy_orders: int, new_sell_orders: int):
        super().__init__(name, prod_position, new_buy_orders, new_sell_orders)
        self.derivative_resolution: int = derivative_resolution
        self.diff_thresh: int = diff_thresh
        self.trade_count: int = trade_count

    def trade(self, order_depth: OrderDepth, orders: list):
        self.calculate_means()

        diff = self.get_price_difference()

        if diff < -self.diff_thresh and len(order_depth.sell_orders) != 0:
            best_asks = sorted(order_depth.sell_orders.keys())

            i = 0
            while i < self.trade_count and len(best_asks) > i:
                if self.prod_position == self.max_pos:
                    break
                self.buy_product(best_asks, i, order_depth, orders)
                i += 1

        if diff > self.diff_thresh and len(order_depth.buy_orders) != 0:
            best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

            i = 0
            while i < self.trade_count and len(best_bids) > i:
                if self.prod_position == -self.max_pos:
                    break
                self.sell_product(best_bids, i, order_depth, orders)

                i += 1

    def get_price_difference(self):
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

