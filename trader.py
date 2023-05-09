from typing import Dict, List, Tuple

import numpy as np

from products.product import Pearls, Bananas, PinaColadas, Baguette, Ukulele, Basket, Coconut, Dip, Berries, DivingGear

PEARLS_PRICE = 10000

from datamodel import Order, Trade, TradingState


class Trader:

    def __init__(self):
        self.products = {
            "PEARLS": Pearls(),
            "BANANAS": Bananas(),
            "PINA_COLADAS": PinaColadas(),
            "BAGUETTE": Baguette(),
            "UKULELE": Ukulele(),
            "PICNIC_BASKET": Basket(),
            "COCONUTS": Coconut(),
            "DIP": Dip(),
            "BERRIES": Berries(),
            "DIVING_GEAR": DivingGear()
        }

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        # Initialize the method output dict as an empty dict
        result = {}

        for product in state.order_depths.keys():
            if product in self.products.keys():
                orders: list[Order] = []

                self.products[product].reset_from_state(state)
                self.products[product].trade(trading_state=state, orders=orders)
                result[product] = orders

        return result
