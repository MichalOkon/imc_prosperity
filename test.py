from datamodel import Listing, OrderDepth, Trade, TradingState
from trader_40k import Trader

timestamp1 = 6251

listings = {
    "PEARLS": Listing(
        symbol="PEARLS",
        product="PEARLS",
        denomination="SEASHELLS"
    ),
    "BANANAS": Listing(
        symbol="BANANAS",
        product="BANANAS",
        denomination="SEASHELLS"
    ),
    "BERRIES": Listing(
        symbol="BERRIES",
        product="BERRIES",
        denomination="SEASHELLS"
    ),
}

order_depths = {
    "BERRIES": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    )
}

own_trades = {
    "PEARLS": [],
    "BANANAS": [],
    "BERRIES": []
}

market_trades = {
    "PEARLS": [
        Trade(
            symbol="PEARLS",
            price=11,
            quantity=4,
            buyer="",
            seller="",
            timestamp=900
        ),
        Trade(
            symbol="PEARLS",
            price=14,
            quantity=-3,
            buyer="",
            seller="",
            timestamp=900
        )
    ],
    "BANANAS": [Trade(
        symbol="BANANAS",
        price=140,
        quantity=6,
        buyer="",
        seller="",
        timestamp=900
    )]
}

position = {
    "PEARLS": 3,
    "BANANAS": -5,
    "BERRIES": 10
}

observations1 = {"DOLPHIN_SIGHTINGS": 6060}


state1 = TradingState(
    timestamp=timestamp1,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    observations=observations1,
    position=position
)



timestamp2 = 6252

listings = {
    "PEARLS": Listing(
        symbol="PEARLS",
        product="PEARLS",
        denomination="SEASHELLS"
    ),
    "BANANAS": Listing(
        symbol="BANANAS",
        product="BANANAS",
        denomination="SEASHELLS"
    ),
    "BERRIES": Listing(
        symbol="BERRIES",
        product="BERRIES",
        denomination="SEASHELLS"
    ),
    "DIVING_GEAR": Listing(
        symbol="DIVING_GEAR",
        product="DIVING_GEAR",
        denomination="SEASHELLS"
    ),
}

order_depths = {
    "BERRIES": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    ),
    "DIVING_GEAR": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    )
}

own_trades = {
    "PEARLS": [],
    "BANANAS": [],
    "BERRIES": [],
    "DIVING_GEAR": []

}

market_trades = {
    "PEARLS": [
        Trade(
            symbol="PEARLS",
            price=11,
            quantity=4,
            buyer="",
            seller="",
            timestamp=900
        ),
        Trade(
            symbol="PEARLS",
            price=14,
            quantity=-3,
            buyer="",
            seller="",
            timestamp=900
        )
    ],
    "BANANAS": [Trade(
        symbol="BANANAS",
        price=140,
        quantity=6,
        buyer="",
        seller="",
        timestamp=900
    )]
}

position = {
    "PEARLS": 3,
    "BANANAS": -5,
    "BERRIES": 10,
    "DIVING_GEAR": 10
}

observations2 = {"DOLPHIN_SIGHTINGS": 6080}

state2 = TradingState(
    timestamp=timestamp2,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    observations=observations2,
    position=position
)

timestamp3 = 6954

listings = {
    "PEARLS": Listing(
        symbol="PEARLS",
        product="PEARLS",
        denomination="SEASHELLS"
    ),
    "BANANAS": Listing(
        symbol="BANANAS",
        product="BANANAS",
        denomination="SEASHELLS"
    ),
    "BERRIES": Listing(
        symbol="BERRIES",
        product="BERRIES",
        denomination="SEASHELLS"
    ),
    "DIVING_GEAR": Listing(
        symbol="DIVING_GEAR",
        product="DIVING_GEAR",
        denomination="SEASHELLS"
    ),
}

order_depths = {
    "BERRIES": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    ),
    "DIVING_GEAR": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    )
}

own_trades = {
    "PEARLS": [],
    "BANANAS": [],
    "BERRIES": [],
    "DIVING_GEAR": []

}

market_trades = {
    "PEARLS": [
        Trade(
            symbol="PEARLS",
            price=11,
            quantity=4,
            buyer="",
            seller="",
            timestamp=900
        ),
        Trade(
            symbol="PEARLS",
            price=14,
            quantity=-3,
            buyer="",
            seller="",
            timestamp=900
        )
    ],
    "BANANAS": [Trade(
        symbol="BANANAS",
        price=140,
        quantity=6,
        buyer="",
        seller="",
        timestamp=900
    )]
}

position = {
    "PEARLS": 3,
    "BANANAS": -5,
    "BERRIES": 10,
    "DIVING_GEAR": 10
}

observations3 = {"DOLPHIN_SIGHTINGS": 6080}

state3 = TradingState(
    timestamp=timestamp3,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    observations=observations3,
    position=position
)



timestamp4 = 6974

listings = {
    "PEARLS": Listing(
        symbol="PEARLS",
        product="PEARLS",
        denomination="SEASHELLS"
    ),
    "BANANAS": Listing(
        symbol="BANANAS",
        product="BANANAS",
        denomination="SEASHELLS"
    ),
    "BERRIES": Listing(
        symbol="BERRIES",
        product="BERRIES",
        denomination="SEASHELLS"
    ),
    "DIVING_GEAR": Listing(
        symbol="DIVING_GEAR",
        product="DIVING_GEAR",
        denomination="SEASHELLS"
    ),
}

order_depths = {
    "BERRIES": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    ),
    "DIVING_GEAR": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    )
}

own_trades = {
    "PEARLS": [],
    "BANANAS": [],
    "BERRIES": [],
    "DIVING_GEAR": []

}

market_trades = {
    "PEARLS": [
        Trade(
            symbol="PEARLS",
            price=11,
            quantity=4,
            buyer="",
            seller="",
            timestamp=900
        ),
        Trade(
            symbol="PEARLS",
            price=14,
            quantity=-3,
            buyer="",
            seller="",
            timestamp=900
        )
    ],
    "BANANAS": [Trade(
        symbol="BANANAS",
        price=140,
        quantity=6,
        buyer="",
        seller="",
        timestamp=900
    )]
}

position = {
    "PEARLS": 3,
    "BANANAS": -5,
    "BERRIES": 10,
    "DIVING_GEAR": 10
}

observations4 = {"DOLPHIN_SIGHTINGS": 6080}

state4 = TradingState(
    timestamp=timestamp4,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    observations=observations4,
    position=position
)


timestamp5 = 6201

listings = {
    "PEARLS": Listing(
        symbol="PEARLS",
        product="PEARLS",
        denomination="SEASHELLS"
    ),
    "BANANAS": Listing(
        symbol="BANANAS",
        product="BANANAS",
        denomination="SEASHELLS"
    ),
    "BERRIES": Listing(
        symbol="BERRIES",
        product="BERRIES",
        denomination="SEASHELLS"
    ),
    "DIVING_GEAR": Listing(
        symbol="DIVING_GEAR",
        product="DIVING_GEAR",
        denomination="SEASHELLS"
    ),
}

order_depths = {
    "BERRIES": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    ),
    "DIVING_GEAR": OrderDepth(
        buy_orders={10: 7, 9: 5},
        sell_orders={11: -4, 12: -8}
    )
}

own_trades = {
    "PEARLS": [],
    "BANANAS": [],
    "BERRIES": [],
    "DIVING_GEAR": []

}

market_trades = {
    "PEARLS": [
        Trade(
            symbol="PEARLS",
            price=11,
            quantity=4,
            buyer="",
            seller="",
            timestamp=900
        ),
        Trade(
            symbol="PEARLS",
            price=14,
            quantity=-3,
            buyer="",
            seller="",
            timestamp=900
        )
    ],
    "BANANAS": [Trade(
        symbol="BANANAS",
        price=140,
        quantity=6,
        buyer="",
        seller="",
        timestamp=900
    )]
}

position = {
    "PEARLS": 3,
    "BANANAS": -5,
    "BERRIES": 10,
    "DIVING_GEAR": 10
}

observations5 = {"DOLPHIN_SIGHTINGS": 6080}

state5 = TradingState(
    timestamp=timestamp5,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    observations=observations5,
    position=position
)
trader = Trader()
trader.run(state1)
trader.run(state2)
trader.run(state3)
trader.run(state4)
trader.run(state5)

