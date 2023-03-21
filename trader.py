# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.
import json
from itertools import chain  # TODO: check if we can use this
from typing import Dict, List, Any

import numpy as np

from datamodel import OrderDepth, TradingState, Order, Trade, Symbol, ProsperityEncoder

MAX_POS = 20
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

        # How many last days to consider when calculating the average prices
        self.last_days = 100
        self.banana_days = 5
        # How many of the best bids/asks we should consider
        self.trade_count = 2

        self.banana_asks = []
        self.banana_bids = []

        self.fill_diff = 3

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        logger.print(
            f"timestamp: {state.timestamp}, listings: {state.listings}, order_depths: {state.order_depths}, own_trades: {state.own_trades}, market_trades: {state.market_trades}, position: {state.position}, observations: {state.observations}")
        self.cache_prices(state)
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            prod_position = state.position[product] if product in state.position.keys() else 0

            # Retrieve the Order Depth containing all the market BUY and SELL orders
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            if product == "BANANAS":

                self.cache_banana_prices(state)
                if len(self.banana_asks) < self.banana_days or len(self.banana_bids) < self.banana_days:
                    logger.print(f"Skipping {len(self.banana_asks)}")
                    continue
                avg_bid, avg_ask = self.calculate_banana_prices()

                if len(order_depth.sell_orders) != 0:
                    best_asks = sorted(order_depth.sell_orders.keys())

                    i = 0
                    while i < self.trade_count and best_asks[i] - self.fill_diff < avg_bid:
                        if prod_position == MAX_POS:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= MAX_POS:
                            # In case the lowest ask is lower than our fair value,
                            # This presents an opportunity for us to buy cheaply
                            # The code below therefore sends a BUY order at the price level of the ask,
                            # with the same quantity
                            # We expect this order to trade with the sell order
                            logger.print("BUY", str(-best_ask_volume) + "x", product, best_asks[i])
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the MAX_POS
                            logger.print(f"exceeding max pos for {product} in selling")
                            vol = MAX_POS - prod_position
                            logger.print(f"buying {vol} of {product}")
                            orders.append(Order(product, best_asks[i], vol))
                            logger.print(f"exceeding max pos for {product} in buying")
                            prod_position += vol
                        i += 1

                if len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                    i = 0
                    while i < self.trade_count and best_bids[i] + self.fill_diff > avg_ask:
                        if prod_position == -MAX_POS:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -MAX_POS:
                            logger.print("SELL", str(best_bid_volume) + "x", product, best_bids[i])
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the MAX_POS
                            logger.print(f"exceeding max pos for {product} in selling")
                            vol = prod_position + MAX_POS
                            logger.print(f"selling {vol} of {product}")
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                        i += 1

            else:
                # Define a fair value
                acceptable_price = PEARLS_PRICE
                logger.print(f"acceptable price for {product}: {acceptable_price}")
                # Check if there are any SELL orders
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_asks = sorted(order_depth.sell_orders.keys())

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    i = 0
                    while i < self.trade_count and best_asks[i] < acceptable_price:
                        if prod_position == MAX_POS:
                            break
                        best_ask_volume = order_depth.sell_orders[best_asks[i]]
                        if prod_position - best_ask_volume <= MAX_POS:
                            # In case the lowest ask is lower than our fair value,
                            # This presents an opportunity for us to buy cheaply
                            # The code below therefore sends a BUY order at the price level of the ask,
                            # with the same quantity
                            # We expect this order to trade with the sell order
                            logger.print("BUY", str(-best_ask_volume) + "x", product, best_asks[i])
                            orders.append(Order(product, best_asks[i], -best_ask_volume))
                            prod_position += -best_ask_volume
                        else:
                            # Buy as much as we can without exceeding the MAX_POS
                            logger.print(f"exceeding max pos for {product} in selling")
                            vol = MAX_POS - prod_position
                            logger.print(f"buying {vol} of {product}")
                            orders.append(Order(product, best_asks[i], vol))
                            logger.print(f"exceeding max pos for {product} in buying")
                            prod_position += vol
                        i += 1

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0:
                    best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

                    i = 0
                    while i < self.trade_count and best_bids[i] > acceptable_price:
                        if prod_position == -MAX_POS:
                            break
                        best_bid_volume = order_depth.buy_orders[best_bids[i]]
                        if prod_position - best_bid_volume >= -MAX_POS:
                            logger.print("SELL", str(best_bid_volume) + "x", product, best_bids[i])
                            orders.append(Order(product, best_bids[i], -best_bid_volume))
                            prod_position += -best_bid_volume

                        else:
                            # Sell as much as we can without exceeding the MAX_POS
                            logger.print(f"exceeding max pos for {product} in selling")
                            vol = prod_position + MAX_POS
                            logger.print(f"selling {vol} of {product}")
                            orders.append(Order(product, best_bids[i], -vol))
                            prod_position += -vol
                        i += 1

                # Add all the above orders to the result dict
            result[product] = orders

            # Return the dict of orders
            # Depending on the logic above
        logger.flush(state, result)
        return result

    def cache_banana_prices(self, state: TradingState) -> None:
        if "BANANAS" in state.order_depths.keys():
            sell_orders = state.order_depths["BANANAS"].sell_orders
            buy_orders = state.order_depths["BANANAS"].buy_orders

            self.banana_asks.append(sell_orders)
            self.banana_bids.append(buy_orders)

    def calculate_banana_prices(self) -> (int, int):
        relevant_bids = []
        for bids in self.banana_bids[-self.banana_days:]:
            relevant_bids.extend([(value, bids[value]) for value in bids])
        relevant_asks = []
        for asks in self.banana_asks[-self.banana_days:]:
            relevant_asks.extend([(value, asks[value]) for value in asks])

        avg_bid = np.average([x[0] for x in relevant_bids], weights=[x[1] for x in relevant_bids])
        avg_ask = np.average([x[0] for x in relevant_asks], weights=[x[1] for x in relevant_asks])

        return avg_bid, avg_ask

    def cache_prices(self, state: TradingState) -> None:
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

    def calculate_price(self, product):
        # Calculate average price of a product
        relevant_prices = list(chain(*(self.cached_prices[product][-self.last_days:])))
        prices = np.array([x[1] for x in relevant_prices])
        quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        return np.average(prices, weights=quantities)
