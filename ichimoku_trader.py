# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.
import json
from itertools import chain  # TODO: check if we can use this
from typing import Dict, List, Any, Tuple

import numpy as np

from datamodel import OrderDepth, TradingState, Order, Trade, Symbol, ProsperityEncoder

MAX_POS = 20

CONVERSION_LINE_LENGTH = 9
BASE_LINE_LENGTH = 26
SPAN_B_LINE_LENGTH = 52

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


class IchimokuTrader:

    def __init__(self):
        # dictionary mapping product names to list consisting of last own_trades and market_trades of the product
        self.cached_prices = {}

        # How many last days to consider when calculating the average prices
        self.last_days = 100

        # How many of the best bids/asks we should consider
        self.trade_count = 2

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
                if len(self.cached_prices[product]["ASK"]) >= 52:
                    conversion_line = self.calculate_conversion_or_base_line(product, "ASK", CONVERSION_LINE_LENGTH)
                    base_line = self.calculate_conversion_or_base_line(product, "ASK", BASE_LINE_LENGTH)
                    span_A = (conversion_line + base_line) / 2
                    span_B = self.calculate_conversion_or_base_line(product, "ASK", SPAN_B_LINE_LENGTH)

                    cloud = max(span_A, span_B)

                    if len(order_depth.sell_orders) > 0:

                        # Sort all the available sell orders by their price,
                        # and select only the sell order with the lowest price
                        best_asks = sorted(order_depth.sell_orders.keys())

                        # Check if the lowest ask (sell order) is lower than the above defined fair value
                        i = 0

                        while i < self.trade_count and best_asks[i] > cloud and conversion_line > base_line:
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




            # # # skip product if not enough data
            # # if len(self.cached_prices[product]["ASK"]) < self.last_days:
            # #     logger.print(f"Skipping {len(self.cached_prices[product]['ASK'])}")
            # #     continue
            #
            #
            #
            # # Define a fair value
            # # acceptable_price = self.calculate_price(product)
            #
            # # logger.print(f"acceptable price for {product}: {acceptable_price}")
            # # Check if there are any SELL orders
            # if len(order_depth.sell_orders) > 0:
            #
            #     # Sort all the available sell orders by their price,
            #     # and select only the sell order with the lowest price
            #     best_asks = sorted(order_depth.sell_orders.keys())
            #
            #     # Check if the lowest ask (sell order) is lower than the above defined fair value
            #     i = 0
            #     while i < self.trade_count and best_asks[i] < acceptable_price:
            #         if prod_position == MAX_POS:
            #             break
            #         best_ask_volume = order_depth.sell_orders[best_asks[i]]
            #         if prod_position - best_ask_volume <= MAX_POS:
            #             # In case the lowest ask is lower than our fair value,
            #             # This presents an opportunity for us to buy cheaply
            #             # The code below therefore sends a BUY order at the price level of the ask,
            #             # with the same quantity
            #             # We expect this order to trade with the sell order
            #             logger.print("BUY", str(-best_ask_volume) + "x", product, best_asks[i])
            #             orders.append(Order(product, best_asks[i], -best_ask_volume))
            #             prod_position += -best_ask_volume
            #         else:
            #             # Buy as much as we can without exceeding the MAX_POS
            #             logger.print(f"exceeding max pos for {product} in selling")
            #             vol = MAX_POS - prod_position
            #             logger.print(f"buying {vol} of {product}")
            #             orders.append(Order(product, best_asks[i], vol))
            #             logger.print(f"exceeding max pos for {product} in buying")
            #             prod_position += vol
            #         i += 1
            #
            # # The below code block is similar to the one above,
            # # the difference is that it finds the highest bid (buy order)
            # # If the price of the order is higher than the fair value
            # # This is an opportunity to sell at a premium
            # if len(order_depth.buy_orders) != 0:
            #     best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)
            #
            #     i = 0
            #     while i < self.trade_count and best_bids[i] > acceptable_price:
            #         if prod_position == -MAX_POS:
            #             break
            #         best_bid_volume = order_depth.buy_orders[best_bids[i]]
            #         if prod_position - best_bid_volume >= -MAX_POS:
            #             logger.print("SELL", str(best_bid_volume) + "x", product, best_bids[i])
            #             orders.append(Order(product, best_bids[i], -best_bid_volume))
            #             prod_position += -best_bid_volume
            #
            #         else:
            #             # Sell as much as we can without exceeding the MAX_POS
            #             logger.print(f"exceeding max pos for {product} in selling")
            #             vol = prod_position + MAX_POS
            #             logger.print(f"selling {vol} of {product}")
            #             orders.append(Order(product, best_bids[i], -vol))
            #             prod_position += -vol
            #         i += 1

            # Add all the above orders to the result dict
            result[product] = orders

            # Return the dict of orders
            # Depending on the logic above
        logger.flush(state, result)
        return result

    def cache_prices(self, state: TradingState) -> None:
        # Caches prices of bought and sold products

        market_trades = state.market_trades
        own_trades = state.own_trades
        listings = state.listings
        for product in listings.keys():

            if product not in self.cached_prices.keys():
                self.cached_prices[product] = {"ASK": [], "BID": []}

            asks = list(state.order_depths[product].sell_orders.items())
            bids = list(state.order_depths[product].buy_orders.items())
            self.cached_prices[product]["ASK"].append(asks)
            self.cached_prices[product]["BID"].append(bids)

            # prod_trades: List[Trade] = own_trades.get(product, []) + market_trades.get(product, [])

            # prices = [(trade.quantity, trade.price) for trade in prod_trades]
            # self.cached_prices[product].append(prices)

    def calculate_price(self, product):
        # Calculate average price of a product
        relevant_prices = list(chain(*(self.cached_prices[product][-self.last_days:])))
        prices = np.array([x[1] for x in relevant_prices])
        quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        return np.average(prices, weights=quantities)

    # price_list: List[List[Tuple[int, int]]]
    def calculate_conversion_or_base_line(self, product: str, offer_type: str, length: int) -> float:
        # Midpoint of the best across the last 9 prices
        relevant_best_offers = self.cached_prices[product][offer_type][-1:-length-1:-1]
        relevant_best_offer_prices = [x[0][0] for x in relevant_best_offers]
        high = max(relevant_best_offer_prices)
        low = min(relevant_best_offer_prices)
        return (high + low) / 2

    def calculate_leading_span_A(self):
        pass

    def calculate_leading_span_B(self):
        pass

    def calculate_cloud(self):
        pass