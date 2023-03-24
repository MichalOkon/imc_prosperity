# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.
from typing import Dict, List, Any, Tuple
import json

import numpy as np

from datamodel import OrderDepth, TradingState, Order, Trade, Symbol, ProsperityEncoder

PEARLS_PRICE = 10000


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: Dict[Symbol, List[Order]]) -> None:
        logs = self.logs
        if logs.endswith("\n"):
            logs = logs[:-1]

        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.state = None
        self.orders = {}
        self.logs = ""


logger = Logger()


class Trader:

    def __init__(self):
        # dictionary mapping product names to list consisting of last own_trades and market_trades of the product
        self.cached_prices = {}
        self.cached_means = {}

        # How many last days to consider when calculating the average prices
        self.last_days = 100
        self.banana_days = 2
        self.mean_days = {"PINA_COLADAS": 1, "COCONUTS": 1, "DIVING_GEAR": 1,"BERRIES": 1}
        self.derivative_resolution = {"PINA_COLADAS": 10, "COCONUTS": 10, "DIVING_GEAR": 10,"BERRIES": 10}  # best 10
        self.diff_thresh = {"PINA_COLADAS": 20, "COCONUTS": 5, "DIVING_GEAR": 10,"BERRIES": 10}  # best 20 pina, 5 coco
        # How many of the best bids/asks we should consider
        self.trade_count = 1

        self.old_asks = {"BANANAS": [], "PEARLS": [], "PINA_COLADAS": [], "COCONUTS": []}
        self.old_bids = {"BANANAS": [], "PEARLS": [], "PINA_COLADAS": [], "COCONUTS": []}
        self.spread = {"BANANAS": 2, "PINA_COLADAS": 1, "COCONUTS": 2}
        self.fill_diff = {"BANANAS": 3, "PINA_COLADAS": 0, "COCONUTS": 3}
        self.mean_diffs = {"BANANAS": [], "PEARLS": [], "PINA_COLADAS": [], "COCONUTS": [], "DIVING_GEAR": [], "BERRIES": []}

        self.max_pos = {"BANANAS": 20, "PEARLS": 20, "PINA_COLADAS": 300, "COCONUTS": 600, "DIVING_GEAR": 50, "BERRIES": 250}
        self.max_own_order = {"BANANAS": 20, "PEARLS": 20, "PINA_COLADAS": 10, "COCONUTS": 300, "DIVING_GEAR": 25, "BERRIES": 125}

        self.pina_means = []
        self.coco_stds = []

        self.std_window = 500
        self.mean_window = 50

        self.above = False
        self.below = False

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            orig_position = state.position[product] if product in state.position.keys() else 0
            prod_position = orig_position
            # Retrieve the Order Depth containing all the market BUY and SELL orders
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            new_buy_orders = 0
            new_sell_orders = 0

            if product == "PEARLS":
                self.cache_pearl_prices(state)
                # Define a fair value
                acceptable_price = PEARLS_PRICE
                # Check if there are any SELL orders

                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price
                    best_asks = sorted(order_depth.sell_orders.keys())

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    i = 0
                    while i < self.trade_count and best_asks[i] < acceptable_price:
                        # Fill ith ask order if it's below the acceptable
                        if prod_position == self.max_pos[product] or new_buy_orders == 20:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= self.max_pos[product]:
                            # Buy
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                            new_buy_orders += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the self.max_pos[product]
                            vol = self.max_pos[product] - prod_position
                            orders.append(Order(product, best_asks[i], vol))
                            prod_position += vol
                            new_buy_orders += vol
                        i += 1
                if len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                    i = 0
                    while i < self.trade_count and best_bids[i] > acceptable_price:
                        if prod_position == -self.max_pos[product] or new_sell_orders == 20:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -self.max_pos[product]:
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume
                            new_sell_orders += best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the self.max_pos[product]
                            vol = prod_position + self.max_pos[product]
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                            new_sell_orders += vol
                        i += 1

                # Add some new orders on our own with very profitable prices hoping some stupid bots fill them
                orders.append(Order(product, acceptable_price - 4, max(0, min(20, self.max_pos[product] - prod_position,
                                                                              self.max_pos[product] - orig_position,
                                                                              self.max_pos[
                                                                                  product] - orig_position - new_buy_orders))))
                orders.append(
                    Order(product, acceptable_price + 4, -max(0, min(20, self.max_pos[product] + prod_position,
                                                                     self.max_pos[product] + orig_position,
                                                                     self.max_pos[
                                                                         product] + orig_position - new_sell_orders))))
                # print("new sell orders: ", new_sell_orders)
                # print("new buy orders: ", new_buy_orders)
                # print("prod position: ", prod_position)
                # sell_capacity = min(ORDER_LIMIT - new_sell_orders - new_buy_orders, self.max_pos[product] + prod_position)
                # print("sell capacity: ", sell_capacity)
                # if sell_capacity > 0:
                #     orders.append(Order(product, acceptable_price + 5, -sell_capacity))
                #
                # buy_capacity =  min(ORDER_LIMIT - new_buy_orders - new_sell_orders, self.max_pos[product] - prod_position)
                # print("buy capacity: ", buy_capacity)
                # if buy_capacity > 0:
                #     orders.append(Order(product, acceptable_price - 5, buy_capacity))

            elif product == "BANANAS":
                self.cache_prices(state)
                if len(self.old_asks[product]) < self.banana_days or len(self.old_bids[product]) < self.banana_days:
                    continue
                avg_bid, avg_ask = self.calculate_prices(product, self.banana_days)

                if len(order_depth.sell_orders) != 0:
                    best_asks = sorted(order_depth.sell_orders.keys())

                    i = 0
                    while i < self.trade_count and len(best_asks) > i and best_asks[i] - self.fill_diff[
                        product] < avg_bid:
                        if prod_position == self.max_pos[product]:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= self.max_pos[product]:
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                            new_buy_orders += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the self.max_pos[product]
                            vol = self.max_pos[product] - prod_position
                            orders.append(Order(product, best_asks[i], vol))
                            prod_position += vol
                            new_buy_orders += vol
                        i += 1

                if len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                    i = 0
                    while i < self.trade_count and len(best_bids) > i and best_bids[i] + self.fill_diff[
                        product] > avg_ask:
                        if prod_position == -self.max_pos[product]:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -self.max_pos[product]:
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume
                            new_sell_orders += best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the self.max_pos[product]
                            vol = prod_position + self.max_pos[product]
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                            new_sell_orders += vol

                        i += 1
                #
                # Add some new orders on our own with very profitable prices hoping some stupid bots fill them
                mid_price = (avg_bid + avg_ask) / 2
                orders.append(Order(product, mid_price - self.spread[product],
                                    max(0, min(self.max_own_order[product], self.max_pos[product] - prod_position,
                                               self.max_pos[product] - orig_position,
                                               self.max_pos[product] - orig_position - new_buy_orders))))
                orders.append(Order(product, mid_price + self.spread[product],
                                    -max(0, min(self.max_own_order[product], self.max_pos[product] + prod_position,
                                                self.max_pos[product] + orig_position,
                                                self.max_pos[product] + orig_position - new_sell_orders))))

            if  product == "PINA_COLADAS" or product == "COCONUTS" or product == "DIVING_GEAR" or product == "BERRIES":
                self.cache_pearl_prices(state)
                self.calculate_means(product)

                # if product == "COCONUTS":
                #     if len(self.cached_means[product]) < self.derivative_resolution[product] + 2:
                #         old_mean = self.cached_means[product][0]
                #     else:
                #         old_mean = np.mean(self.cached_means[product][-self.derivative_resolution[product]:-1])
                #     diff = self.cached_means[product][-1] - old_mean
                # else:
                #     if len(self.cached_means[product]) < self.derivative_resolution[product] + 1:
                #         old_mean = self.cached_means[product][0]
                #     else:
                #         old_mean = self.cached_means[product][-self.derivative_resolution[product]]
                #     diff = self.cached_means[product][-1] - old_mean

                if len(self.cached_means[product]) < self.derivative_resolution[product] + 1:
                    old_mean = self.cached_means[product][0]
                else:
                    old_mean = self.cached_means[product][-self.derivative_resolution[product]]
                diff = self.cached_means[product][-1] - old_mean

                self.mean_diffs[product].append(diff)
                if diff < -self.diff_thresh[product] and len(order_depth.sell_orders) != 0:
                    best_asks = sorted(order_depth.sell_orders.keys())

                    i = 0
                    while i < self.trade_count and len(best_asks) > i:
                        if prod_position == self.max_pos[product]:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= self.max_pos[product]:
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                            new_buy_orders += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the self.max_pos[product]
                            vol = self.max_pos[product] - prod_position
                            orders.append(Order(product, best_asks[i], vol))
                            prod_position += vol
                            new_buy_orders += vol
                        i += 1

                if diff > self.diff_thresh[product] and len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                    i = 0
                    while i < self.trade_count and len(best_bids) > i:
                        if prod_position == -self.max_pos[product]:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -self.max_pos[product]:
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume
                            new_sell_orders += best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the self.max_pos[product]
                            vol = prod_position + self.max_pos[product]
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                            new_sell_orders += vol

                        i += 1

            if product == "COCONUTS":

                if len(self.old_asks[product]) < self.std_window or len(self.old_bids[product]) < self.std_window:
                    self.coco_stds.append(0)
                else:
                    std_bid, std_ask = self.calculate_stds(product, self.std_window)
                    mid_std = (std_bid + std_ask) / 2
                    self.coco_stds.append(mid_std)

            if product == "PINA_COLADAS":

                self.cache_prices(state)
                if len(self.old_asks[product]) < self.banana_days or len(self.old_bids[product]) < self.banana_days:
                    self.pina_means.append(0)
                    continue

                avg_bid, avg_ask = self.calculate_prices(product, self.mean_window)
                mid_avg = (avg_bid + avg_ask) / 2
                self.pina_means.append(mid_avg)

                lower_bound = self.pina_means[-1] - 2 * self.coco_stds[-1]
                upper_bound = self.pina_means[-1] + 2 * self.coco_stds[-1]

                best_ask = None
                best_bid = None

                if len(order_depth.sell_orders) != 0:
                    best_asks = sorted(order_depth.sell_orders.keys())
                    best_ask = best_asks[-1]

                    i = 0
                    while i < self.trade_count and len(best_asks) > i and \
                            not self.below and not self.above and best_asks[i] < lower_bound:
                        self.below = True
                        if prod_position == self.max_pos[product]:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= self.max_pos[product]:
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                            new_buy_orders += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the self.max_pos[product]
                            vol = self.max_pos[product] - prod_position
                            orders.append(Order(product, best_asks[i], vol))
                            prod_position += vol
                            new_buy_orders += vol
                        i += 1

                if len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
                    best_bid = best_bids[-1]

                    i = 0
                    while i < self.trade_count and len(best_bids) > i and \
                            not self.below and not self.above and best_bids[i] > upper_bound:
                        self.above = True
                        if prod_position == -self.max_pos[product]:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -self.max_pos[product]:
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume
                            new_sell_orders += best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the self.max_pos[product]
                            vol = prod_position + self.max_pos[product]
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                            new_sell_orders += vol

                        i += 1

                if best_bid is not None and best_ask is not None:
                    price = (best_bid + best_ask) / 2
                    if self.below and price > lower_bound:
                        assert not self.above
                        self.below = False
                    elif self.above and price < upper_bound:
                        assert not self.below
                        self.above = False
                # #
                # # Add some new orders on our own with very profitable prices hoping some stupid bots fill them
                # mid_price = (avg_bid + avg_ask) / 2
                # orders.append(Order(product, mid_price - self.spread[product], max(0, min(self.max_own_order[product], self.max_pos[product] - prod_position,
                #                                                                         self.max_pos[product] - orig_position,
                #                                                                         self.max_pos[product] - orig_position - new_buy_orders))))
                # orders.append(Order(product, mid_price + self.spread[product], -max(0, min(self.max_own_order[product], self.max_pos[product] + prod_position,
                #                                                                          self.max_pos[product] + orig_position,
                #                                                                          self.max_pos[product] + orig_position - new_sell_orders))))

            # Add all the above orders to the result dict
            result[product] = orders

            # Return the dict of orders
            # Depending on the logic above
        logger.flush(state, result)
        return result

    def cache_prices(self, state: TradingState) -> None:
        for product in state.order_depths.keys():
            if product not in self.old_bids.keys():
                self.old_bids[product] = []
            if product not in self.old_asks.keys():
                self.old_asks[product] = []
            sell_orders = state.order_depths[product].sell_orders
            buy_orders = state.order_depths[product].buy_orders

            self.old_asks[product].append(sell_orders)
            self.old_bids[product].append(buy_orders)

    def calculate_prices(self, product, days: int) -> Tuple[int, int]:
        relevant_bids = []
        for bids in self.old_bids[product][-days:]:
            relevant_bids.extend([(value, bids[value]) for value in bids])
        relevant_asks = []
        for asks in self.old_asks[product][-days:]:
            relevant_asks.extend([(value, asks[value]) for value in asks])

        avg_bid = np.average([x[0] for x in relevant_bids], weights=[x[1] for x in relevant_bids])
        avg_ask = np.average([x[0] for x in relevant_asks], weights=[x[1] for x in relevant_asks])

        return avg_bid, avg_ask

    def calculate_stds(self, product, days: int) -> Tuple[int, int]:
        relevant_bids = []
        for bids in self.old_bids[product][-days:]:
            relevant_bids.extend([(value, bids[value]) for value in bids])
        relevant_asks = []
        for asks in self.old_asks[product][-days:]:
            relevant_asks.extend([(value, asks[value]) for value in asks])

        std_bid = np.std([x[0] for x in relevant_bids])
        std_ask = np.std([x[0] for x in relevant_asks])

        return std_bid, std_ask

    def cache_pearl_prices(self, state: TradingState) -> None:
        # Caches prices of bought and sold products

        market_trades = state.market_trades
        own_trades = state.own_trades
        listings = state.listings
        for product in listings.keys():

            if product not in self.cached_prices.keys():
                self.cached_prices[product] = []

            prod_trades: List[Trade] = own_trades.get(product, []) + market_trades.get(product, [])

            if len(prod_trades) > 0:
                prices = [(trade.quantity, trade.price) for trade in prod_trades]
                self.cached_prices[product].append(prices)

    def calculate_means(self, product):
        if product not in self.cached_means:
            self.cached_means[product] = []

        if len(self.cached_prices[product]) == 0:
            self.cached_means[product].append(0)

        else:
            relevant_prices = []
            for day_prices in self.cached_prices[product][max(-len(self.cached_prices), -self.mean_days[product]):]:
                for price in day_prices:
                    relevant_prices.append(price)
            prices = np.array([x[1] for x in relevant_prices])
            quantities = np.abs(np.array([x[0] for x in relevant_prices]))

            self.cached_means[product].append(np.average(prices, weights=quantities))

    def calculate_price(self, product):
        # Calculate average price of a product
        relevant_prices = []
        for day_prices in self.cached_prices[product][-self.last_days:]:
            for price in day_prices:
                relevant_prices.append(price)
        prices = np.array([x[1] for x in relevant_prices])
        quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        return np.average(prices, weights=quantities)