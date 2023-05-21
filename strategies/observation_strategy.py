from datamodel import TradingState, OrderDepth
from strategies.strategy import Strategy


class ObservationStrategy(Strategy):
    def __init__(self, name: str, max_position: int):
        super().__init__(name, max_position)
        self.old_dolphins = -1
        self.dolphins_spotted = False
        self.dolphins_gone = False

        self.dolphin_action_time = 900
        self.gear_timestamp_diff = 70000

        self.dolphins_spotted_timestamp = -1
        self.dolphins_gone_timestamp = -1

    def handle_observations(self, trading_state: TradingState):
        for observation in trading_state.observations.keys():
            if observation == "DOLPHIN_SIGHTINGS":
                if self.old_dolphins == -1:
                    self.old_dolphins = trading_state.observations["DOLPHIN_SIGHTINGS"]
                    continue
                if trading_state.observations["DOLPHIN_SIGHTINGS"] - self.old_dolphins > 10:
                    # print("DOLPHINS SPOTTED")
                    self.dolphins_spotted = True
                    self.dolphins_spotted_timestamp = trading_state.timestamp
                if trading_state.observations["DOLPHIN_SIGHTINGS"] - self.old_dolphins < -10:
                    # print("DOLPHINS GONE")
                    self.dolphins_gone = True
                    self.dolphins_gone_timestamp = trading_state.timestamp
                self.old_dolphins = trading_state.observations["DOLPHIN_SIGHTINGS"]

    def trade(self, trading_state: TradingState, orders: list):

        self.handle_observations(trading_state)

        order_depth: OrderDepth = trading_state.order_depths[self.name]

        if self.dolphins_spotted and trading_state.timestamp - self.dolphins_spotted_timestamp < self.dolphin_action_time:
            # start buying gear if dolphins have been spotted
            print(self.dolphins_spotted_timestamp)
            # print("BUYING GEAR")
            print(trading_state.timestamp)
            self.continuous_buy(order_depth, orders)

        if self.dolphins_gone and trading_state.timestamp - self.dolphins_gone_timestamp < self.dolphin_action_time:
            # start selling gear if dolphins are going away
            # print("SELLING GEAR")
            self.continuous_sell(order_depth, orders)
        if self.dolphins_spotted and trading_state.timestamp - self.dolphins_spotted_timestamp > self.gear_timestamp_diff:
            # Start selling after dolphins have been spotted for long enough
            self.continuous_sell(order_depth, orders)

            if trading_state.timestamp - self.dolphins_spotted_timestamp - self.gear_timestamp_diff > self.dolphin_action_time:
                self.dolphins_spotted = False

        if self.dolphins_gone and trading_state.timestamp - self.dolphins_gone_timestamp > self.gear_timestamp_diff:
            # Start buying after dolphins have been gone for long enough
            self.continuous_buy(order_depth, orders)
            if trading_state.timestamp - self.dolphins_gone_timestamp - self.gear_timestamp_diff > self.dolphin_action_time:
                self.dolphins_gone = False
