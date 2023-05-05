from itertools import product
from random import shuffle
from typing import Dict

import multiprocessing as mp
from simulator import Simulator
from trader_40k import Trader

PRODUCT_NAMES = ['DIP', "UKULELE", "BAGUETTE", "PICNIC_BASKET"]

threads = []

derivative_resolutions = (range(10, 50, 5))
diff_threshs = range(10, 50, 5)
my_lock = mp.Lock()

best_diff_thresh = {'DIP': 0, "UKULELE": 0, "BAGUETTE": 0, "PICNIC_BASKET": 0}
best_derivative_resolution = {'DIP': 0, "UKULELE": 0, "BAGUETTE": 0, "PICNIC_BASKET": 0}
best_profit_loss = {'DIP': -9999999, "UKULELE": -9999999, "BAGUETTE": -9999999, "PICNIC_BASKET": -9999999}


def main():
    manager = mp.Manager()
    global best_profit_loss, best_diff_thresh, best_derivative_resolution

    with mp.Pool() as pool:
        args = [(diff_thresh, derivative_resolution)
                for derivative_resolution, diff_thresh in product(derivative_resolutions, diff_threshs)]
        pool.starmap(run_simulation, args)

    with open('second.txt', 'w') as f:
        for product_name in PRODUCT_NAMES:
            # Write the string to the file
            f.write("{}  {}  {}  {}\n".format(product_name, best_profit_loss[product_name],
                                              best_derivative_resolution[product_name],
                                              best_diff_thresh[product_name]))


def init_simulators(trader):
    sim_day_three = Simulator("data/island-data-bottle-round-4/prices_round_4_day_3.csv",
                              "data/island-data-bottle-round-4/trades_round_4_day_3_nn.csv", trader)
    sim_day_two = Simulator("data/island-data-bottle-round-4/prices_round_4_day_2.csv",
                            "data/island-data-bottle-round-4/trades_round_4_day_2_nn.csv", trader)
    sim_day_one = Simulator("data/island-data-bottle-round-4/prices_round_4_day_1.csv",
                            "data/island-data-bottle-round-4/trades_round_4_day_1_nn.csv", trader)
    simulators = [sim_day_one, sim_day_two, sim_day_three]
    return simulators


def simulate_three_days(simulators) -> Dict[str, float]:
    total_profit_loss = {'DIP': 0, "UKULELE": 0, "BAGUETTE": 0, "PICNIC_BASKET": 0}
    average_profit_loss = {'DIP': 0, "UKULELE": 0, "BAGUETTE": 0, "PICNIC_BASKET": 0}
    for simulator in simulators:
        simulator.simulate()
        profit_loss_on_simulator = {'DIP': 0, "UKULELE": 0, "BAGUETTE": 0, "PICNIC_BASKET": 0}
        for product_name in PRODUCT_NAMES:
            profit_loss_on_simulator[product_name] = simulator.total_pnl[product_name][-1]
            simulator_shows_loss_of_shells = profit_loss_on_simulator[product_name] < 0
            if simulator_shows_loss_of_shells:
                profit_loss_on_simulator[product_name] = -9999999999 * 3
            total_profit_loss[product_name] += simulator.total_pnl[product_name][-1]
    for product_name in PRODUCT_NAMES:
        average_profit_loss[product_name] = total_profit_loss[product_name] / 3
    return average_profit_loss


def set_new_best_values(average_profit_loss, diff_thresh, derivative_resolution):
    global best_profit_loss, best_diff_thresh, best_derivative_resolution
    for product_name in PRODUCT_NAMES:
        if best_profit_loss[product_name] < average_profit_loss[product_name]:
            best_profit_loss[product_name] = average_profit_loss[product_name]
            best_diff_thresh[product_name] = diff_thresh
            best_derivative_resolution[product_name] = derivative_resolution


def run_simulation(diff_thresh, derivative_resolution):
    global my_lock, best_derivative_resolution, best_diff_thresh, best_profit_loss
    trader = Trader()
    simulators = init_simulators(trader)
    for product_name in PRODUCT_NAMES:
        trader.diff_thresh[product_name] = diff_thresh
        trader.derivative_resolution[product_name] = derivative_resolution

    average_profit_loss = simulate_three_days(simulators)

    my_lock.acquire()
    for product_name in PRODUCT_NAMES:
        if best_profit_loss[product_name] < average_profit_loss[product_name]:
            best_profit_loss[product_name] = average_profit_loss[product_name]
            best_diff_thresh[product_name] = diff_thresh
            best_derivative_resolution[product_name] = derivative_resolution
            print("{}  {}  {}  {}\n".format(product_name, best_profit_loss[product_name],
                                            best_derivative_resolution[product_name],
                                            best_diff_thresh[product_name]))
    my_lock.release()


if __name__ == "__main__":
    main()
