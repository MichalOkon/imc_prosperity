# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.
from itertools import chain
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

MAX_POS = 20


class Trader:

    def __init__(self):
        # dictionary mapping product names to list consisting of last own_trades and market_trades of the product
        self.cached_prices = {}

        # How many last days to consider when calculating the average prices
        self.last_days = {'BANANAS': 15, 'PEARLS':0}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # print(
        #     f"timestamp: {state.timestamp}, listings: {state.listings}, order_depths: {state.order_depths}, own_trades: {state.own_trades}, market_trades: {state.market_trades}, position: {state.position}, observations: {state.observations}")
        self.cache_prices(state)
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            prod_position = 0 if product not in state.position.keys() else state.position[product]
            # skip product if not enough data
            if len(self.cached_prices[product]) < self.last_days[product]:
                # print(f"Skipping {len(self.cached_prices[product])}")
                continue

            # Retrieve the Order Depth containing all the market BUY and SELL orders
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # Define a fair value
            # acceptable_price = self.calculate_price(product)
            acc_price_lo, acc_price_hi = self.calculate_price(product)

            print(f"acceptable price for {product}: {(acc_price_lo, acc_price_hi)}")
            # If statement checks if there are any SELL orders
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the above defined fair value
                if best_ask < acc_price_lo:
                    if prod_position - best_ask_volume <= MAX_POS:
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        # print("BUY", str(-best_ask_volume) + "x", product, best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    else:
                        # Buy as much as we can without exceeding the MAX_POS
                        # print(f"exceeding max pos for {product} in selling")
                        vol = MAX_POS - prod_position
                        # print(f"buying {vol} of {product}")
                        orders.append(Order(product, best_ask, vol))
                        # print(f"exceeding max pos for {product} in buying")

            # The below code block is similar to the one above,
            # the difference is that it finds the highest bid (buy order)
            # If the price of the order is higher than the fair value
            # This is an opportunity to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acc_price_hi:
                    if prod_position - best_bid_volume >= -MAX_POS:
                        # print("SELL", str(best_bid_volume) + "x", product, best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                    else:
                        # Sell as much as we can without exceeding the MAX_POS
                        # print(f"exceeding max pos for {product} in selling")
                        vol = prod_position + MAX_POS
                        # print(f"selling {vol} of {product}")
                        orders.append(Order(product, best_bid, -vol))
            # Add all the above orders to the result dict
            result[product] = orders

            # Return the dict of orders
            # Depending on the logic above
        return result

    def cache_prices(self, state: TradingState) -> None:
        # Caches prices of bought and sold products

        market_trades = state.market_trades
        own_trades = state.own_trades
        listings = state.listings
        for product in listings.keys():

            if product not in self.cached_prices.keys():
                self.cached_prices[product] = []

            prod_trades = own_trades.get(product, []) + market_trades.get(product, [])

            if len(prod_trades) > 0:
                prices = [(trade.quantity, trade.price) for trade in prod_trades]
                self.cached_prices[product].append(prices)

    def calculate_price(self, product):
        # Calculate average price of a product
        # relevant_prices = list(chain(*(self.cached_prices[product][-self.last_days:])))
        # values = np.array([x[1] for x in relevant_prices])
        # quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        if product == 'PEARLS':
            return 10000, 10000

        days = 5

        days_avg = self.last_days[product]
        # if product == 'BANANAS':
        #     days_avg = 5

        # if product == 'BANANAS':

        #     relevant_prices = list(chain(*(self.cached_prices[product][-days:])))
        #     values = np.array([x[1] for x in relevant_prices])
        #     quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        #     return np.average(values, weights=quantities)
        
        # else:
        #     relevant_prices = list(chain(*(self.cached_prices[product][-days:])))
        #     values = np.array([x[1] for x in relevant_prices])
        #     quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        #     return np.average(values, weights=quantities)

        relevant_prices = list(chain(*(self.cached_prices[product][-days_avg:])))
        values = np.array([x[1] for x in relevant_prices])
        quantities = np.abs(np.array([x[0] for x in relevant_prices]))

        avg =  np.average(values, weights=quantities)
    
        relevant_prices = self.cached_prices[product][-days:]

        days_prices = []

        for day in relevant_prices:
            days_prices.append(np.average([x[1] for x in day], weights=[x[0] for x in day]))

        x = np.arange(0, days)
        y = np.array(days_prices)
        z = np.polyfit(x, y, 1)

        p = np.poly1d(z)
        y_hat = p(x)

        delta = np.mean(np.abs(y - y_hat))
        
        a = 1.8

        delta *= a

        # delta = max(2, delta)

        # delta = 1

        return avg - delta, avg + delta