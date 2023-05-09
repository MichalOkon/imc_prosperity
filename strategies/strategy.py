from datamodel import OrderDepth, Order, TradingState


class Strategy:
    def __init__(self, name: str, max_position: int):
        self.name: str = name
        self.cached_prices: list = []
        self.cached_means: list = []
        self.max_pos: int = max_position
        self.trade_count: int = 1

        self.prod_position: int = 0
        self.new_buy_orders: int = 0
        self.new_sell_orders: int = 0
        self.order_depth: OrderDepth = OrderDepth()

    def reset_from_state(self, state: TradingState):
        self.prod_position = state.position[self.name] if self.name in state.position.keys() else 0
        self.order_depth: OrderDepth = state.order_depths[self.name]

        self.new_buy_orders = 0
        self.new_sell_orders = 0

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

    def continuous_buy(self, order_depth: OrderDepth, orders: list):
        if len(order_depth.sell_orders) != 0:
            best_asks = sorted(order_depth.sell_orders.keys())

            i = 0
            while i < self.trade_count and len(best_asks) > i:
                if self.prod_position == self.max_pos:
                    break

                self.buy_product(best_asks, i, order_depth, orders)
                i += 1

    def continuous_sell(self, order_depth: OrderDepth, orders: list):
        if len(order_depth.buy_orders) != 0:
            best_bids = sorted(order_depth.buy_orders.keys(), reverse=True)

            i = 0
            while i < self.trade_count and len(best_bids) > i:
                if self.prod_position == -self.max_pos:
                    break

                self.sell_product(best_bids, i, order_depth, orders)
                i += 1
