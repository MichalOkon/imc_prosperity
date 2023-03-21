import itertools
from typing import List

prices = {
    "Pizza": {"Pizza": 1, "Wasabi": 0.5, "Snowball": 1.45, "Shells": 0.75},
    "Wasabi": {"Pizza": 1.95, "Wasabi": 1, "Snowball": 3.1, "Shells": 1.49},
    "Snowball": {"Pizza": 0.67, "Wasabi": 0.31, "Snowball": 1, "Shells": 0.48},
    "Shells": {"Pizza": 1.34, "Wasabi": 0.64, "Snowball": 1.98, "Shells": 1},
}

goods = ["Pizza", "Wasabi", "Snowball", "Shells"]


def calc_money(trades: List[str], amount: float) -> float:
    for i in range(0, len(trades) - 1):
        good_from = trades[i]
        good_to = trades[i + 1]
        amount *= prices[good_from][good_to]
    return amount


if __name__ == '__main__':
    start_amount = 2_000
    result = []
    all_combinations = list(itertools.product(goods, repeat=4)) + list(itertools.product(goods, repeat=3)) + list(itertools.product(goods, repeat=2)) + list(itertools.product(goods, repeat=1))
    print(len(all_combinations))

    for combination in all_combinations:
        trade = ["Shells"] + list(combination) + ["Shells"]
        print(trade)
        result.append((calc_money(trade, start_amount) - start_amount, trade))

    result.sort(key=lambda x: (-x[0], len(x[1])))
    print(result)

