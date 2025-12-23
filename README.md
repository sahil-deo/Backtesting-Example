
### Strategy

- Trade Condition:
- compare mean volume of yesterday's last 120 mins and 10 mins
- if last 10 min mean volume > last 120 mins mean volume * multiplier           # this indicates spike in volume 
-
- Buy Condition:
- if slope is positive, trend is upwards
- buy x amounts of shares using certain percentage of capital                   # capital_per_buy is the percentage of capital used for each buy order
-
- Sell Condition:
- if slope is negative, trend is downwards
- sell number of shares holding * sell_multiplier                               # sell_multiplier is the percentage of shares sold for each sell order

