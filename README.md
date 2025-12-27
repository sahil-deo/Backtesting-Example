
## Strategy

### Buy Condition:

- Compare average of yesterday’s last 120 min’s volume with last 10 min’s volume. 
- If 10 min volume is greater than MULTIPLIER * 120 min volume, a spike is observed. 
- If the slope of the trend is positive, i.e. value of the instrument is increase, then buy stock using CAPITALPERBUY * CurrentCapital. 
- eg. CurrentCapital = 10,000rs, CAPITALPERBUY = 10%, then buy using 1000rs.
- Buy order is executed at Today’s first candle’s OpenPrice.

### Sell Condition:
- Implemented a trailing stoploss at STOPLOSS%. 
- This works by iterating through every candle Today and comparing the CandleLow against the calculated StopLossPrice. 
- Sell order is executed exactly at StopLoss Price.

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

#### Test values

- MULTIPLIER = 3.0 # 300%
- STOPLOSS = 0.05 # 5%
- CAPITALPERBUY = 0.1 # 10%
- INITIALCAPITAL = 100000
- STARTDATE = '01-01-2024'
- ENDDATE = '12-31-2024'

- The Config values can be modified from config.py

The duration can be set from start of the data (02-02-2015) to end of the data (02-02-2025)

#### Data
The test data is list of .csv files defined in config.py

#### Test execution

```
$ python volume.py
```

## Results
Results of the test are stored in `./result/result.csv` file.

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



