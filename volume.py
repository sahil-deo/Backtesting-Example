import pandas as pd
import numpy as np

from pathlib import Path
from metrics import Metrics, Order
from position import Position
import config 


INITIALCAPITAL = config.INITIALCAPITAL

# duration of the test
STARTDATE = config.STARTDATE
ENDDATE = config.ENDDATE

STOPLOSS = config.STOPLOSS

ListOfData = config.LISTOFINSTRUMENTS

if len(ListOfData) < 1:
    print("Empty List of Instruments")
    exit(-1)

DataFiles = [pd.read_csv(file) for file in ListOfData]


AggregateMetrics = pd.DataFrame(columns=[
    "Symbol",
    "Max Drawdown",
    "Hit Rate",
    "Holding Shares",
    "Short Shares",
    "Max Holding",
    "Max Short",
    "Out of Capital",
    "Short Orders",
    "Long Orders",
    "Initial Capital",
    "Current Capital",
    "Holding Capital",
    "Total Equity",
    "Profit",
    "Profit Percentage"
])

FileIndex = 0

for df in DataFiles:

    # ----- tracking name of the symbol -----

    Symbol = ListOfData[FileIndex].split("/")[-1].replace(".csv", "")
    FileIndex+=1
    print(FileIndex, Symbol)

    # ----- cleaning the data ----- 
    
    df.dropna(inplace=True)
    df.drop_duplicates(subset="date", inplace=True)
    df["timestamp"] = pd.to_datetime(df["date"])
    df["date"] = df["timestamp"].dt.date
    df = df.sort_values("timestamp")


    # ----- initialization of Metrics of the test -----

    metrics = Metrics(
        INITIALCAPITAL=INITIALCAPITAL, 
        CurrentCapital=INITIALCAPITAL,      # current capital = initial cast at the start of the test
        CAPITALPERORDER=config.CAPITALPERORDER,            # percentage of capital to use per buy order
        MULTIPLIER= config.MULTIPLIER,               # percentage of spike in volume required to activate trade condition
    )

    # ----- filtering dates for test -----

    df = df[
        (df["date"] >= pd.to_datetime(STARTDATE).date()) & 
        (df["date"] <= pd.to_datetime(ENDDATE).date())
    ]


    # ----- pre grouping days and indexing by date -----

    Grouped = dict(tuple(df.groupby("date")))
    Dates=sorted(Grouped.keys())

    Days = df["date"].drop_duplicates().reset_index()
    DateIndex = Days.columns.get_loc("date")


    # ----- test loop -----

    for i in range(len(Dates)): # loop over dates 

        TodayDF = Grouped[Dates[i]]    
        
        TodayBaselineVolume = TodayDF["volume"].iloc[-135:-15]
        TodayEndVolume = TodayDF["volume"].iloc[-15:-5]

        TodayBaselineMean = TodayBaselineVolume.mean()     # mean of volume of trades from yesterday's last 135 - 15 mins 
        TodayEndMean = TodayEndVolume.mean()           # mean of volume of trades from yesterday's last 15 - 10 mins

        TodayBuyPrice = TodayDF["close"].iloc[-4]                             # today's open price <= using dayend - 2 price as the bid price
        TodaySellPrice = TodayDF["close"].iloc[-4]                             # today's sell price <= using dayend - 5 price as the ask price

        # print(f"Symbol: {Symbol}, Date: {Dates[i]}, Price: {TodayOpenPrice}, DF shape: {TodayDF.shape}")
        
        if len(TodayDF) < 135:                                           # Skips Short Days
            continue

        # ----- Volume Spike Condition -----

        # volume of trades in last 10 mins is greater than the volume of trades in last 120 mins * multiplier
        if(TodayEndMean > TodayBaselineMean*metrics.MULTIPLIER):    

            Arr = TodayDF["close"].iloc[-15:-5].to_numpy()
            X = np.arange(len(Arr))

            # slope to determine the direction of the trend
            Slope = np.polyfit(X, Arr, 1)[0]

            # ----- Buy Condition -----

            if Slope > 0:        
                
                InvestableCapital = metrics.CurrentCapital * (metrics.CAPITALPERORDER)
                NoOfSharesToBuy = int(InvestableCapital/TodayBuyPrice)

                if NoOfSharesToBuy >= 1:
                
                    metrics.Long+=1
                
                    Cost = TodayBuyPrice * NoOfSharesToBuy
                
                    metrics.CurrentCapital -= Cost
                    metrics.LastLong = TodayBuyPrice
                    metrics.NoOfSharesHolding += NoOfSharesToBuy
                    metrics.PeakHolding = max(metrics.PeakHolding, metrics.NoOfSharesHolding)
                    metrics.LastLongDate = Dates[i]
                    EntryTimeStamp = TodayDF.iloc[-4]["timestamp"]

                    if metrics.ShareHigh is None:
                        metrics.ShareHigh = TodayBuyPrice
                    else:
                        # Update ShareHigh to reflect current market price on new entry
                        metrics.ShareHigh = max(metrics.ShareHigh, TodayBuyPrice)



                    metrics.Positions.append(Position(EntryPrice=TodayBuyPrice, Quantity=NoOfSharesToBuy, EntryTimeStamp=EntryTimeStamp, Type='long'))
                    metrics.Orders.append(Order(
                            TimeStamp=EntryTimeStamp, 
                            Quantity=NoOfSharesToBuy, 
                            Type='long', 
                            PnL=0, 
                            TotalCost = Cost,
                            SharePrice=TodayBuyPrice, 
                            BaseLineVolume=TodayBaselineVolume.sum(),
                            EndVolume=TodayEndVolume.sum(),
                            BaseLineVolumeMean=TodayBaselineMean,
                            EndVolumeMean=TodayEndMean
                        ))
                else:
                    metrics.RanOutOfCapital += 1

            # ----- Sell Condition -----

            elif Slope < 0:
                
                InvestableCapital = metrics.CurrentCapital * (metrics.CAPITALPERORDER)
                NoOfSharesToSell = int(InvestableCapital/TodaySellPrice)
                
                if NoOfSharesToSell > 0:

                    metrics.Short+=1

                    Cost = TodaySellPrice * NoOfSharesToSell                    
                    
                    metrics.CurrentCapital += Cost
                    metrics.LastShort = TodaySellPrice
                    metrics.NoOfSharesShort += NoOfSharesToSell
                    metrics.PeakShort = max(metrics.PeakShort, metrics.NoOfSharesShort)
                    metrics.LastShortDate = Dates[i]
                    EntryTimeStamp = TodayDF.iloc[-4]["timestamp"]

                    if metrics.ShareLow == None: 
                        metrics.ShareLow = TodaySellPrice
                    else:
                        metrics.ShareLow = min(metrics.ShareLow, TodaySellPrice)

                    metrics.Positions.append(Position(EntryPrice=TodaySellPrice, Quantity=NoOfSharesToSell, EntryTimeStamp=EntryTimeStamp, Type='short'))
                    metrics.Orders.append(Order(
                                TimeStamp=EntryTimeStamp, 
                                Quantity=NoOfSharesToSell, 
                                Type='short', 
                                PnL=0, 
                                TotalCost = Cost,
                                SharePrice=TodaySellPrice, 
                                BaseLineVolume=TodayBaselineVolume.sum(),
                                EndVolume=TodayEndVolume.sum(),
                                BaseLineVolumeMean=TodayBaselineMean,
                                EndVolumeMean=TodayEndMean
                            ))
                else:
                    metrics.RanOutOfCapital += 1


        


        # ----- Trailing Stop Loss at config.STOPLOSS percent -----


        for _, Row in TodayDF.iterrows():
            
            CandleHigh = Row["high"]
            CandleLow = Row["low"]


            
            for position in metrics.Positions:

                if position.Status == 'closed':
                    continue

                if position.Type == "long":

                    if position.EntryTimeStamp >= Row["timestamp"]: 
                        continue
                
                    # ----- Computing new stoploss price -----
                    
                    position.High = max(CandleHigh, position.High)

                    StopPrice = position.High * (1-STOPLOSS)

                    if CandleLow <= StopPrice:
                        metrics.LastClose = StopPrice
                        NoOfSharesToSell = position.Quantity


                        # ----- Updating Position -----

                        position.Status='closed'
                        position.ExitPrice = StopPrice

                        TimeStamp = Row['timestamp']
                        position.ExitTimeStamp = TimeStamp
                        
                        # ----- Updating Metrics ------

                        EntryPrice = position.EntryPrice
                        Cost = StopPrice * NoOfSharesToSell
                        Profit = Cost - (EntryPrice * NoOfSharesToSell)
                        
                        metrics.CurrentCapital += Cost
                        metrics.OrderProfit.append(Profit)
                        metrics.NoOfSharesHolding -= NoOfSharesToSell
                        metrics.LastCloseDate = Dates[i]

                        # ----- Creating Close Order -----

                        metrics.Orders.append(Order(
                            TimeStamp=Row["timestamp"],
                            Quantity=NoOfSharesToSell,
                            Type="close",
                            PnL=Profit,
                            SharePrice=StopPrice,
                            TotalCost=Cost
                        ))
                        


                        # break  # Exit day after loss sell

                    # metrics.ShareHigh = max(CandleHigh, metrics.ShareHigh)
                elif position.Type == 'short':
                    if position.EntryTimeStamp >= Row["timestamp"]: 
                        continue
                
                    position.Low = min(CandleLow, position.Low)

                    StopPrice = position.Low * (1+STOPLOSS)

                    if CandleHigh >= StopPrice:
                        metrics.LastClose = StopPrice
                        NoOfSharesToBuy = position.Quantity


                        # ----- Updating Position -----

                        position.Status='closed'
                        position.ExitPrice = StopPrice

                        TimeStamp = Row['timestamp']
                        position.ExitTimeStamp = TimeStamp
                        
                        # ----- Updating Metrics ------

                        EntryPrice = position.EntryPrice
                        Cost = StopPrice * NoOfSharesToBuy
                        Profit = (EntryPrice * NoOfSharesToBuy) - Cost

                        metrics.CurrentCapital -= Cost
                        metrics.OrderProfit.append(Profit)
                        metrics.NoOfSharesShort -= NoOfSharesToBuy
                        metrics.LastCloseDate = Dates[i]

                        # ----- Creating Close Order -----

                        metrics.Orders.append(Order(
                            TimeStamp=Row["timestamp"],
                            Quantity=NoOfSharesToBuy,
                            Type="close",
                            PnL=Profit,
                            SharePrice=StopPrice,
                            TotalCost=Cost
                        ))
            
        # Close Short positions at EOD
        TodayClosePrice = TodayDF["close"].iloc[-1]

        for position in metrics.Positions:
            if position.Type == 'short' and position.Status != 'closed':
                
                StopPrice = TodayClosePrice
                NoOfSharesToBuy = position.Quantity

                # ----- Updating Position -----

                position.Status='closed'
                position.ExitPrice = StopPrice
                TimeStamp = TodayDF.iloc[-1]["timestamp"]
                position.ExitTimeStamp = TimeStamp
                
                # ----- Updating Metrics ------

                
                EntryPrice = position.EntryPrice
                Cost = StopPrice * NoOfSharesToBuy
                Profit = (EntryPrice * NoOfSharesToBuy) - Cost

                metrics.CurrentCapital -= Cost
                metrics.OrderProfit.append(Profit)
                metrics.NoOfSharesShort -= NoOfSharesToBuy
                metrics.LastCloseDate = Dates[i]

                # ----- Creating Close Order -----

                metrics.Orders.append(Order(
                    TimeStamp=TimeStamp,
                    Quantity=NoOfSharesToBuy,
                    Type="close",
                    PnL=Profit,
                    SharePrice=StopPrice,
                    TotalCost=Cost
                ))


        # ----- Update Equity daily based on today's share price -----
        Equity = metrics.CurrentCapital

        for p in metrics.Positions:
            if p.Status == "open":
                if p.Type == "long":
                    Equity += (TodayClosePrice - p.EntryPrice) * p.Quantity
                else:
                    Equity -= (TodayClosePrice - p.EntryPrice) * p.Quantity

        metrics.Equity.append(Equity)
        metrics.CurrentShareValue = TodayClosePrice

    # ----- post test metrics calculation -----

    HoldingCapital = metrics.NoOfSharesHolding * metrics.CurrentShareValue

    Profit = (metrics.CurrentCapital+HoldingCapital) - metrics.INITIALCAPITAL
    ProfitPercentage = (Profit / metrics.INITIALCAPITAL) * 100
    MaxDrawdown = 0
    Peak = max(metrics.INITIALCAPITAL, metrics.Equity[0]) if metrics.Equity else metrics.INITIALCAPITAL



    for i in metrics.Equity:
        if i > Peak: Peak = i
        
        Drawdown = (Peak - i)/Peak
        MaxDrawdown = max(MaxDrawdown, Drawdown)

    HitRate = 0
    Hits = 0

    for i in metrics.OrderProfit: 
        if i > 0: Hits += 1

    HitRate = (Hits / len(metrics.OrderProfit)) * 100 if metrics.OrderProfit else 0      # avoid divide by 0 error


    # ----- displaying metrics (not used) -----
    # print("Symbol:",            Symbol)
    # print("Max Drawdown:",      round(MaxDrawdown * 100, 2))
    # print("Hit Rate:",          round(HitRate, 2))
    # print("Holding Shares:",    metrics.NoOfSharesHolding)
    # print("Max Holding:",       metrics.PeakHolding)
    # print("Out of Capital:",       metrics.RanOutOfCapital)
    # print("Buy Orders:",        metrics.Long)
    # print("Sell Orders:",       metrics.Short)
    # print("Initial Capital:",      round(metrics.InitialCapital, 2))
    # print("Current Capital:",      round(metrics.CurrentCapital, 2))
    # print("Holding Capital:",      round(HoldingCapital, 2))
    # print("Total Equity:",      round(metrics.CurrentCapital + HoldingCapital, 2))
    # print("Profit:",            round(Profit, 2))
    # print("Profit Percentage:", round((Profit / metrics.InitialCapital) * 100, 2))


    # ----- save metrics ----- 
    row = {
        "Symbol":            Symbol,
        "Max Drawdown":      round(MaxDrawdown * 100, 2),
        "Hit Rate":          round(HitRate, 2),
        "Holding Shares":    metrics.NoOfSharesHolding,
        "Short Shares":      metrics.NoOfSharesShort,
        "Max Holding":       metrics.PeakHolding,
        "Max Short":         metrics.PeakShort,
        "Out of Capital":    metrics.RanOutOfCapital,
        "Long Orders":       metrics.Long,
        "Short Orders":      metrics.Short,
        "Initial Capital":   round(metrics.INITIALCAPITAL, 2),
        "Current Capital":   round(metrics.CurrentCapital, 2),
        "Holding Capital":   round(HoldingCapital, 2),
        "Total Equity":      round(metrics.CurrentCapital + HoldingCapital, 2),
        "Profit":            round(Profit, 2),
        "Profit Percentage": round(ProfitPercentage, 2),
    }

    AggregateMetrics.loc[len(AggregateMetrics)] = row

    orders = pd.DataFrame(columns=['TimeStamp','Type', 'Price', 'Quantity', 'Profit/Loss', 'TotalCost', 'BaselineVolume', 'EndVolume', 'BaselineVolumeMean', 'EndVolumeMean'])
    for i in metrics.Orders:
        row = {
            "TimeStamp": i.TimeStamp,
            "Type":i.Type,
            "Price": round(i.SharePrice, 2),
            "Quantity": i.Quantity,
            "TotalCost": round(i.TotalCost, 2),
            "Profit/Loss": round(i.PnL, 2),
            "BaselineVolume": i.BaseLineVolume,
            "EndVolume": i.EndVolume,
            "BaselineVolumeMean": round(i.BaseLineVolumeMean,2),
            "EndVolumeMean": round(i.EndVolumeMean, 2)

        }
        orders.loc[len(orders)]=row

    positions = pd.DataFrame(columns=['EntryTimeStamp', 'Type', 'EntryPrice', 'Quantity','TotalCost', 'Status', 'ExitTimeStamp', 'ExitPrice','Profit/Loss', 'Profit/LossPercentage'])
    for i in metrics.Positions:
        
        PositionProfit=0
        PositionProfitPercentage=0
        
        if i.Status == 'closed':
            if i.Type == 'long':
                PositionProfit = (i.ExitPrice - i.EntryPrice) * i.Quantity
                PositionProfitPercentage = ((i.ExitPrice - i.EntryPrice) / i.EntryPrice) * 100
            else:  # short
                PositionProfit = (i.EntryPrice - i.ExitPrice) * i.Quantity
                PositionProfitPercentage = ((i.EntryPrice - i.ExitPrice) / i.EntryPrice) * 100

        row = {
            "EntryTimeStamp": i.EntryTimeStamp,
            "Type": i.Type,
            "EntryPrice": round(i.EntryPrice, 2),
            "Quantity": i.Quantity,
            "TotalCost": round(i.Quantity * i.EntryPrice),
            "Status": i.Status,
            "ExitTimeStamp": i.ExitTimeStamp,
            "ExitPrice": round(i.ExitPrice, 2),
            "Profit/Loss": round(PositionProfit, 2),
            "Profit/LossPercentage": round(PositionProfitPercentage,2)
        }
        positions.loc[len(positions)]=row

    positions.to_csv(f"result/{Symbol}_Positions.csv", index=False)
    orders.to_csv(f"result/{Symbol}_Orders.csv", index=False)


    print(f"Max Drawdown:{round(MaxDrawdown, 2)}  Hit Rate: {round(HitRate, 2)}  Profit: {round((Profit/metrics.INITIALCAPITAL)*100, 2)}")

# ----- calculating mean of all metrics -----
row = {
    "Symbol":            "Mean",
    "Max Drawdown":      round(AggregateMetrics["Max Drawdown"].mean(), 2),
    "Hit Rate":          round(AggregateMetrics["Hit Rate"].mean(), 2),
    "Holding Shares":    round(AggregateMetrics["Holding Shares"].mean(), 2),
    "Short Shares":      round(AggregateMetrics["Short Shares"].mean(), 2),
    "Max Holding":       round(AggregateMetrics["Max Holding"].mean(), 2),
    "Max Short":         round(AggregateMetrics["Max Short"].mean(), 2),
    "Out of Capital":    round(AggregateMetrics["Out of Capital"].mean(), 2),
    "Long Orders":       round(AggregateMetrics["Long Orders"].mean(), 2),
    "Short Orders":      round(AggregateMetrics["Short Orders"].mean(), 2),
    "Initial Capital":   round(AggregateMetrics["Initial Capital"].mean(), 2),
    "Current Capital":   round(AggregateMetrics["Current Capital"].mean(), 2),
    "Holding Capital":   round(AggregateMetrics["Holding Capital"].mean(), 2),
    "Total Equity":      round(AggregateMetrics["Total Equity"].mean(), 2),
    "Profit":            round(AggregateMetrics["Profit"].mean(), 2),
    "Profit Percentage": round(AggregateMetrics["Profit Percentage"].mean(), 2)
}

AggregateMetrics.loc[len(AggregateMetrics)] = row



# ----- save results at result/result.csv -----
AggregateMetrics.to_csv("result/result.csv")


from multiprocessing import Pool
import os

def Process(ListOfData):
    pass



if __name__ == '__main__':
    with Pool(processes=os.cpu_count()) as pool:
        ArgsList = [(df, ListOfData[i].split("/")[-1].replace(".csv", ""), i) for i, df in enumerate(DataFiles)]

        results = pool.map(Process, ArgsList)

    AggregateMetrics = pd.DataFrame(results)
