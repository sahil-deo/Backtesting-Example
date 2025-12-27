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
    "Max Holding",
    "Out of Capital",
    "Buy Orders",
    "Sell Orders",
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
    
    df = df.dropna()
    df = df.drop_duplicates(subset="date")
    df["timestamp"] = pd.to_datetime(df["date"])
    df["date"] = df["timestamp"].dt.date
    df = df.sort_values("timestamp")


    # ----- initialization of Metrics of the test -----

    metrics = Metrics(
        INITIALCAPITAL=INITIALCAPITAL, 
        CurrentCapital=INITIALCAPITAL,      # current capital = initial cast at the start of the test
        CAPITALPERBUY=config.CAPITALPERBUY,            # percentage of capital to use per buy order
        MULTIPLIER= config.MULTIPLIER,               # percentage of spike in volume required to activate trade condition
        SELLMULTIPLIER=0.5             # percentage of shares to sell per sell order
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

    for i in range(1, len(Dates)): # loop over dates 

        YesterdayDF = Grouped[Dates[i-1]]    
        TodayDF = Grouped[Dates[i]]    
        
        YesterdayBaselineVolume = YesterdayDF["volume"].iloc[-130:-10]
        YesterdayEndVolume = YesterdayDF["volume"].iloc[-10:]

        YesterdayBaselineMean = YesterdayBaselineVolume.mean()     # mean of volume of trades from yesterday's last 120 mins 
        YesterdayEndMean = YesterdayEndVolume.mean()           # mean of volume of trades from yesterday's last 10 mins

        TodayOpenPrice = TodayDF["open"].iloc[0]                             # today's open price <= using open price as the bid price
        # print(f"Symbol: {Symbol}, Date: {Dates[i]}, Price: {TodayOpenPrice}, DF shape: {TodayDF.shape}")
        if len(YesterdayDF) < 120:                                           # Skips Short Days
            continue

        # ----- Volume Spike Condition -----

        # volume of trades in last 10 mins is greater than the volume of trades in last 120 mins * multiplier
        if(YesterdayEndMean > YesterdayBaselineMean*metrics.MULTIPLIER):    

            Arr = YesterdayDF["close"].iloc[-10:].to_numpy()
            X = np.arange(len(Arr))

            # slope to determine the direction of the trend
            Slope = np.polyfit(X, Arr, 1)[0]

            # ----- Buy Condition -----

            if Slope > 0:        
                
                InvestableCapital = metrics.CurrentCapital * (metrics.CAPITALPERBUY)
                NoOfSharesToBuy = int(InvestableCapital/TodayOpenPrice)

                if NoOfSharesToBuy >= 1:
                
                    metrics.Buy+=1
                
                    Cost = TodayOpenPrice * NoOfSharesToBuy
                
                    metrics.TotalCost += Cost
                    metrics.CurrentCapital -= Cost
                    metrics.LastBuy = TodayOpenPrice
                    metrics.NoOfSharesHolding += NoOfSharesToBuy
                    metrics.PeakHolding = max(metrics.PeakHolding, metrics.NoOfSharesHolding)

                    if metrics.ShareHigh is None:
                        metrics.ShareHigh = TodayOpenPrice
                    else:
                        # Update ShareHigh to reflect current market price on new entry
                        metrics.ShareHigh = max(metrics.ShareHigh, TodayOpenPrice)


                    TimeStamp = TodayDF.iloc[0]["timestamp"]
                    metrics.Positions.append(Position(EntryPrice=TodayOpenPrice, Quantity=NoOfSharesToBuy, EntryTimeStamp=TimeStamp))
                    metrics.Orders.append(Order(
                            TimeStamp=TimeStamp, 
                            Quantity=NoOfSharesToBuy, 
                            Type='buy', 
                            PnL=0, 
                            SharePrice=TodayOpenPrice, 
                            TotalCost = Cost,
                            BaseLineVolume=YesterdayBaselineVolume.sum(),
                            EndVolume=YesterdayEndVolume.sum(),
                            BaseLineVolumeMean=YesterdayBaselineMean,
                            EndVolumeMean=YesterdayEndMean
                        ))
                    metrics.LastBuyDate = Dates[i]
                else:
                    metrics.RanOutOfCapital += 1

            # ----- Sell Condition -----

            # elif Slope < 0 and metrics.NoOfSharesHolding > 0:
                
            #     metrics.Sell+=1
            #     metrics.LastSell = TodayOpenPrice
                


            #     SharesToSell = int(metrics.NoOfSharesHolding * metrics.SELLMULTIPLIER)
                
            #     # for cases like 
            #     # NoOfSharesHolding (1) * SellMultiplier (0.2)  
            #     # 0.2 gets converted to int = 0 <- cannot sell zero shares
            #     SharesSold = max(1, SharesToSell)    

            #     # not completely necessary but adds a guard rail
            #     SharesSold = min(SharesSold, metrics.NoOfSharesHolding)
                
            #     # avg price is required for calculation of Profit 
            #     AvgPrice = metrics.TotalCost/metrics.NoOfSharesHolding
            #     SellValue = TodayOpenPrice * SharesSold

            #     Profit = SellValue - (AvgPrice * SharesSold)
                
            #     metrics.CurrentCapital += SellValue
            #     metrics.OrderProfit.append(Profit) # order Profit is noted for hitrate calculation later
            #     metrics.NoOfSharesHolding -= SharesSold
            #     metrics.TotalCost -= AvgPrice * SharesSold               
            #     metrics.Orders.append(Order(TimeStamp=TodayDF.iloc[0]["timestamp"], Quantity=SharesSold, Type='sell', PnL=Profit, SharePrice=TodayOpenPrice, TotalCost = SellValue))

        # ----- Trailing Stop Loss at config.STOPLOSS percent -----

        

        if metrics.NoOfSharesHolding > 0:

            # if metrics.ShareHigh == None:
            #     metrics.ShareHigh = metrics.LastBuy


            for _, Row in TodayDF.iterrows():
                
                CandleHigh = Row["high"]
                CandleLow = Row["low"]


                # ----- Computing new stoploss price -----
                
                for position in metrics.Positions:
                    
                    position.High = max(CandleHigh, position.High)

                    if position.Status == 'closed':
                        continue

                    StopPrice = position.High * (1-STOPLOSS)

                    if CandleLow <= StopPrice:
                        metrics.Sell+=1
                        metrics.LastSell = StopPrice
                        SharesToSell = position.Quantity
                        SharesSold = SharesToSell


                        # ----- Updating Position -----

                        position.Status='closed'
                        position.ExitPrice = StopPrice
                        
                        TimeStamp = TodayDF.iloc[0]["timestamp"]
                        position.ExitTimeStamp = TimeStamp
                        

                        # ----- Updating Metrics ------

                        EntryPrice = position.EntryPrice

                        SellValue = StopPrice * SharesSold

                        Profit = SellValue - (EntryPrice * SharesSold)

                        metrics.CurrentCapital += SellValue
                        metrics.OrderProfit.append(Profit)
                        
                        metrics.NoOfSharesHolding -= SharesSold
                        metrics.TotalCost -= EntryPrice * SharesSold

                        metrics.Orders.append(Order(
                            TimeStamp=Row["timestamp"],
                            Quantity=SharesSold,
                            Type="sell",
                            PnL=Profit,
                            SharePrice=StopPrice,
                            TotalCost=SellValue
                        ))
                        

                        metrics.LastSellDate = Dates[i]

                        # break  # Exit day after loss sell

                    # metrics.ShareHigh = max(CandleHigh, metrics.ShareHigh)


        # ----- Update Equity daily based on today's share price -----
        ToDayClosePrice = TodayDF["close"].iloc[-1]
        metrics.Equity.append((metrics.NoOfSharesHolding * ToDayClosePrice) + metrics.CurrentCapital)
        metrics.ShareValue.append(ToDayClosePrice)
        metrics.CurrentShareValue = ToDayClosePrice


    # ----- post test metrics calculation -----

    HoldingCapital = metrics.NoOfSharesHolding * metrics.CurrentShareValue
    Profit = (metrics.CurrentCapital+HoldingCapital) - metrics.INITIALCAPITAL
    ProfitPercentage = (Profit / metrics.INITIALCAPITAL) * 100
    MaxDrawdown = 0
    Peak = metrics.Equity[0] if metrics.Equity else metrics.INITIALCAPITAL


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
    # print("Buy Orders:",        metrics.Buy)
    # print("Sell Orders:",       metrics.Sell)
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
        "Max Holding":       metrics.PeakHolding,
        "Out of Capital":    metrics.RanOutOfCapital,
        "Buy Orders":        metrics.Buy,
        "Sell Orders":       metrics.Sell,
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

    positions = pd.DataFrame(columns=['EntryTimeStamp', 'EntryPrice', 'Quantity','TotalCost', 'Status', 'ExitTimeStamp', 'ExitPrice','Profit/Loss', 'Profit/LossPercentage'])
    for i in metrics.Positions:
        
        PositionProfit=0
        PositionProfitPercentage=0
        
        if i.Status == 'closed':
            PositionProfit = (i.ExitPrice - i.EntryPrice)*i.Quantity
            PositionProfitPercentage = ((i.ExitPrice - i.EntryPrice)/i.EntryPrice)*100
        
        row = {
            "EntryTimeStamp": i.EntryTimeStamp,
            "EntryPrice": round(i.EntryPrice, 2),
            "Quantity": i.Quantity,
            "TotalCost": round(i.Quantity * i.EntryPrice),
            "Status": i.Status,
            "ExitTimeStamp": i.ExitTimeStamp,
            "ExitPrice": i.ExitPrice,
            "Profit/Loss": PositionProfit,
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
    "Max Holding":       round(AggregateMetrics["Max Holding"].mean(), 2),
    "Out of Capital":       round(AggregateMetrics["Out of Capital"].mean(), 2),
    "Buy Orders":        round(AggregateMetrics["Buy Orders"].mean(), 2),
    "Sell Orders":       round(AggregateMetrics["Sell Orders"].mean(), 2),
    "Initial Capital":      round(AggregateMetrics["Initial Capital"].mean(), 2),
    "Current Capital":      round(AggregateMetrics["Current Capital"].mean(), 2),
    "Holding Capital":      round(AggregateMetrics["Holding Capital"].mean(), 2),
    "Total Equity":      round(AggregateMetrics["Total Equity"].mean(), 2),
    "Profit":            round(AggregateMetrics["Profit"].mean(), 2),
    "Profit Percentage": round(AggregateMetrics["Profit Percentage"].mean(), 2)
}

AggregateMetrics.loc[len(AggregateMetrics)] = row



# ----- save results at result/result.csv -----
AggregateMetrics.to_csv("result/result.csv")