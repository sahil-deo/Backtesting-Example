
## Strategy

### Trade Condition:
- Compare mean volume of yesterday's last 120 mins and 10 mins
- If last 10 min mean volume > last 120 mins mean volume * **multiplier** `# this indicates spike in volume `

### Buy Condition:
- If slope is positive, trend is upwards
- Buy x amounts of shares using certain percentage of capital `# capital_per_buy is the percentage of capital used for each buy order`

### Sell Condition:
- If slope is negative, trend is downwards
- Sell number of shares holding * **sell_multiplier** `# sell_multiplier is the percentage of shares sold for each sell order`

## Run the test

1. Create a virtual environment:

`$ python -m venv .venv`

2. Use the virtual environment as the python interpretor

`$ source .venv/bin/activate`

3. Install required packages

`$ pip install -r requirements.txt`

4. Run the test

`$ python volume.py`

## Test

The Test is done over a duration of time with an initial capital.

#### Default values

- Capital: 1,00,000
- Duration: 01-01-2024 to 31-12-2024

The duration can be set from start of the data (02-02-2015) to end of the data (02-02-2025)

#### Data
The test data can be either a single csv file or an entire folder consisting of only csv files.

#### Test execution

```
$ python volume.py
```

```
Use Default Values (Y/n): Y
```

```
1. Single File 
2. Multiple Files
> 2
```

```
Enter folder path: ./data
```

## Results
Results of the test are stored in `./results/result.csv` file.

Following Metrics are calculated in the result:

1. Max Drawdown 
2. Hit Rate
3. Holding Shares `# No. of shares still holding after the test`
4. Max Holding `# Maximum no. of shares held at a point in test`
5. Out of Cash `# No. of times not enough cash for a buy order`
6. Buy Orders `# Total no. of buy orders`
7. Sell Orders `# Total no. of sell orders`
8. Initial Cash 
9. Current Cash
10. Holding Cash `# Value of currently holding shares`
11. Total Equity `# Current Cash + Holding Cash`
12. Profit 
13. Profit Percentage



