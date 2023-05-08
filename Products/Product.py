from Products.Strategy import Strategy, FixedStrategy, CrossStrategy, DiffStrategy


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
