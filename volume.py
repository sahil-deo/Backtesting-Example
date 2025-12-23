import pandas as pd
import numpy as np
import datetime 
import matplotlib.pyplot as plt

from pathlib import Path
from metrics import Metrics


# capital for the test

use_default = input("Use Default Values (Y/n): ")


# default values

initial_cash = 100000

# duration of the test
start_date = "01-01-2024"
end_date = "12-31-2024"

if use_default == "n":
    initial_cash = int(input("Initial Cash: "))
    start_date = input("Start Date(DD-MM-YYYY): ")
    end_date = input("End Date(DD-MM-YYYY): ")




test_mode = input("1. Single File\n2. Multiple Files\n>")

list_of_data = []

if test_mode == "1":
    filepath = input("File Path: ")
    list_of_data.append(filepath)
elif test_mode == "2":
    folderpath = input("Folder Path: ")
    list_of_data = sorted(str(p) for p in Path(folderpath).glob("*.csv"))
else:
    print("Invalid Option\n")
    exit(0)

data_files = [pd.read_csv(file) for file in list_of_data]


aggregate_metrics = pd.DataFrame(columns=[
    "Symbol",
    "Max Drawdown",
    "Hit Rate",
    "Holding Shares",
    "Max Holding",
    "Out of Cash",
    "Buy Orders",
    "Sell Orders",
    "Initial Cash",
    "Current Cash",
    "Holding Cash",
    "Total Equity",
    "Profit",
    "Profit Percentage"
])

fileindex = 0

for df in data_files:

    # ----- tracking name of the symbol -----

    symbol = list_of_data[fileindex].split("/")[-1].replace(".csv", "")
    fileindex+=1
    print(fileindex, symbol)

    # ----- cleaning the data ----- 
    
    df = df.dropna()
    df = df.drop_duplicates(subset="date")
    df["timestamp"] = pd.to_datetime(df["date"])
    df["date"] = df["timestamp"].dt.date
    df = df.sort_values("timestamp")


    # ----- initialization of Metrics of the test -----

    metrics = Metrics(
        initial_cash=initial_cash, 
        current_cash=initial_cash,      # current cash = initial cast at the start of the test
        capital_per_buy=0.1,            # percentage of capital to use per buy order
        multiplier = 1.5,               # percentage of spike in volume required to activate trade condition
        sell_multiplier=0.5             # percentage of shares to sell per sell order
    )

    # ----- filtering dates for test -----

    df = df[
        (df["date"] >= pd.to_datetime(start_date).date()) & 
        (df["date"] <= pd.to_datetime(end_date).date())
    ]


    # ----- pre grouping days and indexing by date -----

    grouped = dict(tuple(df.groupby("date")))
    dates=sorted(grouped.keys())

    days = df["date"].drop_duplicates().reset_index()
    date_index = days.columns.get_loc("date")


    # ----- test loop -----

    for i in range(1, len(dates)): # loop over dates 

        yesterday_df = grouped[dates[i-1]]    
        today_df = grouped[dates[i]]    

        yesterday_baseline_mean = yesterday_df["volume"].iloc[-120:].mean()     # mean of volume of trades from yesterday's last 120 mins 
        yesterday_end_mean = yesterday_df["volume"].iloc[-10:].mean()           # mean of volume of trades from yesterday's last 10 mins

        today_open_price = today_df["open"].iloc[0]                             # today's open price <= using open price as the bid price


        # ----- Volume Spike Condition -----

        # volume of trades in last 10 mins is greater than the volume of trades in last 120 mins * multiplier
        if(yesterday_end_mean > yesterday_baseline_mean*metrics.multiplier):    

            arr = yesterday_df["close"].iloc[-10:].to_numpy()
            x = np.arange(len(arr))

            # slope to determine the direction of the trend
            slope = np.polyfit(x, arr, 1)[0]

            # ----- Buy Condition -----

            if slope > 0:
                
                investable_capital = metrics.current_cash * (metrics.capital_per_buy)
                no_of_shares_to_buy = int(investable_capital/today_open_price)

                if no_of_shares_to_buy >= 1:
                
                    metrics.buy+=1
                
                    cost = today_open_price * no_of_shares_to_buy
                
                    metrics.total_cost += cost
                    metrics.current_cash -= cost
                    metrics.last_buy = today_open_price
                    metrics.no_of_shares_holding += no_of_shares_to_buy
                    metrics.peak_holding = max(metrics.peak_holding, metrics.no_of_shares_holding)
                                
                else:
                    metrics.ran_out_of_cash += 1

            # ----- Sell Condition -----

            elif slope < 0 and metrics.no_of_shares_holding > 0:
                
                metrics.sell+=1
                metrics.last_sell = today_open_price
                


                shares_sold = int(metrics.no_of_shares_holding * metrics.sell_multiplier)
                
                # for cases like 
                # no_of_shares_holding (1) * sell_multiplier (0.2)  
                # 0.2 gets converted to int = 0 <- cannot sell zero shares
                shares_to_sell = max(1, shares_sold)    

                # not completely necessary but adds a guard rail
                shares_to_sell = min(shares_to_sell, metrics.no_of_shares_holding)
                
                # avg price is required for calculation of profit 
                avg_price = metrics.total_cost/metrics.no_of_shares_holding
                sell_value = today_open_price * shares_to_sell

                profit = sell_value - (avg_price * shares_to_sell)
                
                metrics.current_cash += sell_value
                metrics.order_profit.append(profit) # order profit is noted for hitrate calculation later
                metrics.no_of_shares_holding -= shares_to_sell
                metrics.total_cost -= avg_price * shares_to_sell               



        # ----- Update Equity daily based on today's share price -----

        metrics.equity.append((metrics.no_of_shares_holding * today_open_price) + metrics.current_cash)
        metrics.share_value.append(today_open_price)
        metrics.current_share_value = today_open_price


    # ----- post test metrics calculation -----

    holding_cash = metrics.no_of_shares_holding * metrics.current_share_value
    profit = (metrics.current_cash+holding_cash) - metrics.initial_cash

    max_drawdown = 0
    peak = metrics.equity[0] if metrics.equity else metrics.initial_cash


    for i in metrics.equity:
        if i > peak: peak = i
        
        drawdown = (peak - i)/peak
        max_drawdown = max(max_drawdown, drawdown)

    hit_rate = 0
    hits = 0

    for i in metrics.order_profit: 
        if i > 0: hits += 1

    hit_rate = (hits / len(metrics.order_profit)) * 100 if metrics.order_profit else 0      # avoid divide by 0 error


    # ----- displaying metrics (not used) -----
    # print("Symbol:",            symbol)
    # print("Max Drawdown:",      round(max_drawdown * 100, 2))
    # print("Hit Rate:",          round(hit_rate, 2))
    # print("Holding Shares:",    metrics.no_of_shares_holding)
    # print("Max Holding:",       metrics.peak_holding)
    # print("Out of Cash:",       metrics.ran_out_of_cash)
    # print("Buy Orders:",        metrics.buy)
    # print("Sell Orders:",       metrics.sell)
    # print("Initial Cash:",      round(metrics.initial_cash, 2))
    # print("Current Cash:",      round(metrics.current_cash, 2))
    # print("Holding Cash:",      round(holding_cash, 2))
    # print("Total Equity:",      round(metrics.current_cash + holding_cash, 2))
    # print("Profit:",            round(profit, 2))
    # print("Profit Percentage:", round((profit / metrics.initial_cash) * 100, 2))


    # ----- save metrics ----- 
    row = {
        "Symbol":            symbol,
        "Max Drawdown":      round(max_drawdown * 100, 2),
        "Hit Rate":          round(hit_rate, 2),
        "Holding Shares":    metrics.no_of_shares_holding,
        "Max Holding":       metrics.peak_holding,
        "Out of Cash":       metrics.ran_out_of_cash,
        "Buy Orders":        metrics.buy,
        "Sell Orders":       metrics.sell,
        "Initial Cash":      round(metrics.initial_cash, 2),
        "Current Cash":      round(metrics.current_cash, 2),
        "Holding Cash":      round(holding_cash, 2),
        "Total Equity":      round(metrics.current_cash + holding_cash, 2),
        "Profit":            round(profit, 2),
        "Profit Percentage": round((profit / metrics.initial_cash) * 100, 2),
    }

    aggregate_metrics.loc[len(aggregate_metrics)] = row

# ----- calculating mean of all metrics -----
row = {
    "Symbol":            "Mean",
    "Max Drawdown":      round(aggregate_metrics["Max Drawdown"].mean(), 2),
    "Hit Rate":          round(aggregate_metrics["Hit Rate"].mean(), 2),
    "Holding Shares":    round(aggregate_metrics["Holding Shares"].mean(), 2),
    "Max Holding":       round(aggregate_metrics["Max Holding"].mean(), 2),
    "Out of Cash":       round(aggregate_metrics["Out of Cash"].mean(), 2),
    "Buy Orders":        round(aggregate_metrics["Buy Orders"].mean(), 2),
    "Sell Orders":       round(aggregate_metrics["Sell Orders"].mean(), 2),
    "Initial Cash":      round(aggregate_metrics["Initial Cash"].mean(), 2),
    "Current Cash":      round(aggregate_metrics["Current Cash"].mean(), 2),
    "Holding Cash":      round(aggregate_metrics["Holding Cash"].mean(), 2),
    "Total Equity":      round(aggregate_metrics["Total Equity"].mean(), 2),
    "Profit":            round(aggregate_metrics["Profit"].mean(), 2),
    "Profit Percentage": round(aggregate_metrics["Profit Percentage"].mean(), 2)
}

aggregate_metrics.loc[len(aggregate_metrics)] = row


# ----- save results at result/result.csv -----
aggregate_metrics.to_csv("result/result.csv")