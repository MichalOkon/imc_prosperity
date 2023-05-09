from strategies.cross_strategy import CrossStrategy
from strategies.diff_strategy import DiffStrategy
from strategies.fixed_strategy import FixedStrategy
from strategies.time_based_strategy import TimeBasedStrategy


class Pearls(FixedStrategy):
    def __init__(self):
        super().__init__("PEARLS", max_pos=20)


class Bananas(CrossStrategy):
    def __init__(self):
        super().__init__("BANANAS", min_req_price_difference=3, max_position=20)


class PinaColadas(DiffStrategy):
    def __init__(self):
        super().__init__("PINA_COLADAS", max_position=150, derivative_resolution=150, diff_thresh=30)


class Baguette(DiffStrategy):
    def __init__(self):
        super().__init__("BAGUETTE", max_position=150, derivative_resolution=20, diff_thresh=200)


class Dip(DiffStrategy):
    def __init__(self):
        super().__init__("DIP", max_position=300, derivative_resolution=100, diff_thresh=40)


class Coconut(DiffStrategy):
    def __init__(self):
        super().__init__("COCONUTS", max_position=600, derivative_resolution=1500, diff_thresh=30)


class Ukulele(DiffStrategy):
    def __init__(self):
        super().__init__("UKULELE", max_position=70, derivative_resolution=20, diff_thresh=150)


class Basket(DiffStrategy):
    def __init__(self):
        super().__init__("PICNIC_BASKET", max_position=70, derivative_resolution=50, diff_thresh=100)


class Berries(TimeBasedStrategy):
    def __init__(self):
        super().__init__("BERRIES", min_req_price_difference=2, max_position=250)


class DivingGear(DiffStrategy):
    def __init__(self):
        super().__init__("DIVING_GEAR", max_position=50, derivative_resolution=15, diff_thresh=25)
