# IMC Prosperity Trading Algorithm

This repository contains code developed by the team Zahcheesha for the IMC trading competition. Our algorithm secured a position in the top 1% of all competing teams. In addition, we have developed a versatile simulator to test trading strategies without the need for official game access.

## Prerequisites

To install the necessary packages, use pip with the following command:

```
pip install -r requirements.txt
```

The code has been tested with Python 3.11.0.

## Running the Simulation

To execute the simulation, enter the following command in your console:

```
python runner.py <name_of_the_trader> <csv_filename_with_round_data> <csv_filename_with_trades_data>
```

Replace `<name_of_the_trader>`, `<csv_filename_with_round_data>`, and `<csv_filename_with_trades_data>` with the appropriate values.

## Code Organization

The code is organized as follows:

- `trader.py`: Implements the trader logic
- `datamodel.py`: Defines basic data models used in trading
- `products`: This directory holds the implementation of specific products
- `strategies`: This directory contains implementations of strategies employed across multiple products
- `helpers`: This directory houses helper functions utilized during the parameter tuning process
- `simulator`: This directory comprises the code for the game simulator that allows for strategy testing without official game access