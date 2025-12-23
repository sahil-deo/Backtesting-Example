import pandas as pd 
import numpy as np 

df = pd.read_csv("data/data.csv")

#reverse sorting the data
df = df.iloc[::-1].reset_index()

#fixing string 

# 1. "ABC " -> "ABC"
# 2. "A ABC" -> "A_ABC"

df.columns = df.columns.str.strip().str.replace(" ", "_")

# Starting Test

no_of_shares = 0

initial_cash = int(input("Initial Cash: "))
current_cash = initial_cash
ran_out_of_cash = 0

#orders executed
buy=0
sell=0
peak_holding = 0


close_idx = df.columns.get_loc("Close")
open_idx = df.columns.get_loc("Open")
for i in range(2, len(df)):
    if df.iloc[i-2, close_idx] > df.iloc[i-1, close_idx] and df.iloc[i-1, close_idx] > df.iloc[i, close_idx]:
        if buy > 0:
            sell+=1
            no_of_shares-=1
            current_cash+=df.iloc[i, close_idx]

    elif df.iloc[i-2, close_idx] < df.iloc[i-1, close_idx] and df.iloc[i-1, close_idx] < df.iloc[i, close_idx]:
        if current_cash > df.iloc[i, close_idx]:
            buy+=1
            if(no_of_shares > peak_holding):
                peak_holding = buy
            no_of_shares+=1
            current_cash-=df.iloc[i, close_idx]
        else:
            ran_out_of_cash += 1
    pass

holding_cash = no_of_shares * df.iloc[len(df)-1, close_idx]
print("Holding:", no_of_shares)
print("Max Holding", peak_holding)
print("Holding Cash:", int(holding_cash))
print("No. of out of cash: ", ran_out_of_cash)
print("Total Buy Orders: ", buy)
print("Total Sell Orders: ", sell)
print("Initial Cash: ", int(initial_cash))
print("Current Cash: ", int(current_cash))
if(initial_cash > current_cash+holding_cash):
    print("Profit: ", int((current_cash + holding_cash) - initial_cash))
else:
    print("Profit: ", int(initial_cash - (current_cash + holding_cash)))

