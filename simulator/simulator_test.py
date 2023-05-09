import importlib
import sys

from .simulator import Simulator


def main():
    trader_file = importlib.import_module(sys.argv[1])
    trader = trader_file.Trader()
    sim = Simulator(sys.argv[2], sys.argv[3], trader)

    # Use this to function to start the simulation
    sim.simulate()
    sim.plot_midprices()


if __name__ == "__main__":
    main()
