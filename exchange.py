import pandas as pd
from matplotlib import pyplot as plt

from datamodel import OrderDepth, TradingState, Trade, Listing
from trader import Trader

TUTORIAL_ITERATION_AMOUNT = 2000


def simulate(trader):
    historical_penal = list()
    prices = {"PEARLS": [], "BANANAS": []}

    prices_path = f"data/island-data-bottle-round-1/prices_round_1_day_0.csv"
    trades_path = f"data/island-data-bottle-round-1/trades_round_1_day_0_nn.csv"
    df_prices = pd.read_csv(prices_path, sep=';')
    df_trades = pd.read_csv(trades_path, sep=';')

    state: TradingState = TradingState(-1, {}, {}, {}, {}, {}, {})

    last_prices = {}
    cash = 0
    pnl = 0

    for _, row in df_prices.iterrows():
        time = row["timestamp"]
        if time >= 200000:
            break

        product = row["product"]
        if product not in state.position:
            state.position[product] = 0
            state.own_trades[product] = []
            state.market_trades[product] = []

        state.listings[product] = Listing(product, product, "SEASHELLS")

        # fill OrderDepth with top 3 best bid and ask prices
        state.order_depths[product] = OrderDepth()
        best_bid = None
        best_ask = None
        for i in range(1, 4):
            bid_price = row[f"bid_price_{i}"]
            ask_price = row[f"ask_price_{i}"]
            if bid_price > 0:
                state.order_depths[product].buy_orders[bid_price] = row[f"bid_volume_{i}"]
                if not best_bid:
                    best_bid = bid_price
            if ask_price > 0:
                state.order_depths[product].sell_orders[ask_price] = row[f"ask_volume_{i}"]
                if not best_ask:
                    best_ask = ask_price

        mid_point_price = (best_bid + best_ask) / 2
        prices[product].append(mid_point_price)

        # process our trades
        if time != state.timestamp and state.timestamp != -1:
            # state.timestamp = time
            output = trader.run(state)
            for product in output:
                for order in output[product]:  # process trader orders
                    levels = state.order_depths[order.symbol]
                    if order.quantity < 0:  # sell/ask - need corresponding buy
                        volume = abs(order.quantity)
                        while len(levels.buy_orders):
                            best_bid = max(levels.buy_orders.keys())
                            last_prices[product] = best_bid
                            if best_bid < order.price:
                                break  # if no overlap, skip
                            taken_volume = min(volume, levels.buy_orders[best_bid])
                            volume -= taken_volume
                            levels.buy_orders[best_bid] -= taken_volume
                            state.position[product] -= taken_volume
                            cash += best_bid * taken_volume
                            state.own_trades[product].append(Trade(product, best_bid, taken_volume, None, "self", state.timestamp))
                            if volume <= 0:
                                break
                            if levels.buy_orders[best_bid] <= 0:
                                del levels.buy_orders[best_bid]
                    else:  # buy / bid  - need corresponding sell
                        volume = order.quantity
                        while len(levels.sell_orders):
                            best_ask = min(levels.sell_orders.keys())
                            last_prices[product] = best_ask
                            if best_ask > order.price:
                                break  # if no overlap, skip
                            taken_volume = min(volume, levels.sell_orders[best_ask])
                            volume -= taken_volume
                            levels.sell_orders[best_ask] -= taken_volume
                            state.position[product] += taken_volume
                            cash -= best_ask * taken_volume
                            state.own_trades[product].append(Trade(product, best_ask, taken_volume, "self", None, state.timestamp))
                            if volume <= 0:
                                break
                            if levels.sell_orders[best_ask] <= 0:
                                del levels.sell_orders[best_ask]

        # process bots' trades that happened at this time
        trades = df_trades[df_trades['timestamp'] == time]
        for _, trade in trades.iterrows():
            symbol = trade['symbol']
            if symbol != product:
                continue
            t = Trade(symbol, trade['price'], trade['quantity'], trade['buyer'], trade['seller'], time)
            state.market_trades[product].append(t)

        for product in state.position:
            if abs(state.position[product]) > 20:
                raise RuntimeError(f"Position limit for {product} violated - {state.position[product]}")

        position_values = [state.position.get(x, 0) * prices[x][-1] if len(prices[x]) > 0 else 0 for x in prices.keys()]
        pnl = cash + sum(position_values)
        print(time, pnl, (cash, state.position))
        historical_penal.append(pnl)
        state.timestamp = time

    print(pnl, (cash, state.position))
    plt.plot(df_prices["timestamp"][:4000], historical_penal)
    plt.show()

    plt.plot(prices["PEARLS"])
    plt.show()

    plt.plot(prices["BANANAS"])
    plt.show()


if __name__ == '__main__':
    simulate(Trader())
