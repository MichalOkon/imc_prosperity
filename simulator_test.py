from simulator import Simulator
from trader_40k import Trader

trader = Trader()
sim = Simulator("prices_round_4_day_1.csv", "trades_round_4_day_1_nn.csv", trader)
sim.simulate()
sim.plot_midprices()