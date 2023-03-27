from simulator import Simulator
from trader_40k import Trader

trader = Trader()
sim = Simulator("island-data-bottle-round-4/prices_round_4_day_3.csv", "island-data-bottle-round-4/trades_round_4_day_3_nn.csv", trader)
sim.simulate()
sim.plot_midprices()