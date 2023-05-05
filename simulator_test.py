from simulator import Simulator
from trader_40k import Trader

trader = Trader()

sim = Simulator("data/island-data-bottle-round-4/prices_round_4_day_1.csv", "data/island-data-bottle-round-4/trades_round_4_day_1_nn.csv", trader)
sim.simulate()
sim.plot_midprices()
sim.plot_pnl()
sim = Simulator("data/island-data-bottle-round-4/prices_round_4_day_2.csv", "data/island-data-bottle-round-4/trades_round_4_day_2_nn.csv", trader)
sim.simulate()
sim.plot_midprices()
sim.plot_pnl()
sim = Simulator("data/island-data-bottle-round-4/prices_round_4_day_3.csv", "data/island-data-bottle-round-4/trades_round_4_day_3_nn.csv", trader)
sim.simulate()
sim.plot_midprices()
sim.plot_pnl()