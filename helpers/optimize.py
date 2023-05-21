import threading
from itertools import product

from simulator.simulator import Simulator
from trader import Trader

PRODUCT_NAME = 'DIP'

threads = []

derivative_resolutions = range(10, 50, 5)
diff_thresholds = range(10, 60, 10)
my_lock = threading.Lock()

best_diff_thresh = 0
best_derivative_resolution = 0
best_profit_loss = -999999999999


def simulate_three_days(derivative_resolution: int, diff_thresh: int):
    trader = Trader()
    if hasattr(trader.products[PRODUCT_NAME], 'diff_thresh'):
        trader.products[PRODUCT_NAME].diff_thresh = diff_thresh
    if hasattr(trader.products[PRODUCT_NAME], 'derivative_resolution'):
        trader.products[PRODUCT_NAME].derivative_resoltuion = derivative_resolution

    sim = Simulator("datasets/island-data-bottle-round-4/prices_round_4_day_3.csv",
                    "datasets/island-data-bottle-round-4/trades_round_4_day_3_nn.csv", trader)
    sim.simulate()
    first: int = sim.total_pnl[PRODUCT_NAME][-1]

    sim = Simulator("datasets/island-data-bottle-round-4/prices_round_4_day_2.csv",
                    "datasets/island-data-bottle-round-4/trades_round_4_day_2_nn.csv", trader)
    sim.simulate()
    second: int = sim.total_pnl[PRODUCT_NAME][-1]

    sim = Simulator("datasets/island-data-bottle-round-4/prices_round_4_day_1.csv",
                    "datasets/island-data-bottle-round-4/trades_round_4_day_1_nn.csv", trader)
    sim.simulate()
    third: int = sim.total_pnl[PRODUCT_NAME][-1]

    average_profit: float = (first + second + third) / 3
    my_lock.acquire()
    global best_profit_loss, best_derivative_resolution, best_diff_thresh
    if best_profit_loss < average_profit:
        best_profit_loss = average_profit
        best_diff_thresh = diff_thresh
        best_derivative_resolution = derivative_resolution
    my_lock.release()


def main():
    for derivative_resolution, diff_thresh in product(derivative_resolutions, diff_thresholds):
        try:
            thread = threading.Thread(target=simulate_three_days, args=(derivative_resolution, diff_thresh),
                                      daemon=True)
            threads.append(thread)
            thread.start()
        except RuntimeError:
            break
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
    print(best_derivative_resolution, best_diff_thresh, best_profit_loss)
