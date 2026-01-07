import pandas as pd
import numpy as np

from pathlib import Path
from engine.metrics import Metrics
from engine.order import Order
from engine.position import Position
import configs.volume2_cfg as cfg



def generateMean(df):

    results = []

    todayDFs = df.groupby('date')

    for date, todayDF in todayDFs:
        if len(todayDF) < 135:
            continue
        
        vol = todayDF['volume'].to_numpy()
        baselineVolumeMean  = vol[cfg.BASELINEX:cfg.BASELINEY].mean()
        endVolumeMean       = vol[cfg.ENDX:cfg.ENDY].mean()
        
        closes = todayDF['close'].iloc[cfg.ENDX:cfg.ENDY].to_numpy()
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]
        slope = slope / closes.mean() # Slope Normalization
        

        results.append({
            "date":date,
            "baselinemean":baselineVolumeMean,
            "endmean":endVolumeMean,
            "trend":slope
        })


    dailyDf = pd.DataFrame(results)
    dailyDf.sort_values('date', inplace = True)
    dailyDf.reset_index(drop = True, inplace = True)

    dailyDf['ma15endmean'] = dailyDf['endmean'].rolling(window=15).mean()
    dailyDf['baselinepct'] = (dailyDf['endmean']/dailyDf['baselinemean']) * 100
    dailyDf['endpct']      = (dailyDf['endmean']/dailyDf['ma15endmean']) * 100
    

    dailyDf.dropna(inplace=True)
    dailyDf.reset_index(drop=True, inplace=True)
    
    return dailyDf


# stockMetrics[stockname]-> metrics for the stock
openPositions = []
closedPositions = []
stockMetrics = {}

def runBacktest(i, j, stocks):
    STARTDATE       = pd.to_datetime(cfg.STARTDATE).date()
    ENDDATE         = pd.to_datetime(cfg.ENDDATE).date()
    STOPLOSS        = cfg.STOPLOSS[i]
    MULTIPLIER      = cfg.MULTIPLIER[j]
    
    openPositions = []
    closedPositions = []
    stockMetrics = {}

    allStocksMean = {}
    allStocksByDate = {}

    for stock in stocks:

        df = pd.read_csv(stock)
        stockName = stock.split('/')[-1].replace('.csv', '')
        print(stockName)

        stockMetrics[stockName] = Metrics(
            MULTIPLIER=MULTIPLIER
        )  

        df["timestamp"] = pd.to_datetime(df["date"])
        df["date"]      = df["timestamp"].dt.date
        df = df[
            (df['date'] >= STARTDATE) &
            (df['date'] < ENDDATE)
        ]
        df["time"]      = df["timestamp"].dt.time
        df.sort_values('timestamp', inplace=True) 

        # allStocksByDate[stockName]=dict(tuple(df.groupby('date')))

        grouped = {}
        for d, g in df.groupby('date', sort=False):
            grouped[d] = {
                "open"  :g['open'].to_numpy(),
                "close" :g['close'].to_numpy(),
                "high"  :g['high'].to_numpy(),
                "low"   :g['low'].to_numpy(),
                "timestamp":g['timestamp'].to_numpy(),
            }
        allStocksByDate[stockName] = grouped
        allStocksMean[stockName]=generateMean(df)

    dfs = []
    for stock, df in allStocksMean.items():
        temp = df.copy()             
        temp['stock'] = stock
        dfs.append(temp)

    masterDf = pd.concat(dfs, ignore_index=True)

    filteredDf = masterDf[
        # (masterDf["endpct"] > MULTIPLIER*100) & 
        (masterDf["baselinepct"] > MULTIPLIER*100) & 
        (masterDf['trend'] > cfg.TRENDTHRESHOLD)
    ]

    topStocksMeanByDate = dict(tuple((
        filteredDf
        .sort_values("date", ascending=True)
        .groupby("date")
    )))

    # topStocksMeanByDate.to_csv('result/topstocks.csv')

    all_dates = set()
    for stock_dates in allStocksByDate.values():
        all_dates.update(stock_dates.keys())
    dates = sorted(all_dates)

    # Test Start

    for di in range(len(dates)):
        topStocksToday = topStocksMeanByDate.get(dates[di])
        
        # Continue in case no stock today satisfies the criteria
        if topStocksToday is not None:
        # print(f'{topStocksToday['date'].iloc[0]}:{topStocksToday['stock'].iloc[0]}')

        # filter the top n stocks
            topStocksToday = topStocksToday.sort_values('baselinepct', ascending=False,)
            if len(topStocksToday) > cfg.TOPNSTOCKS:
                topStocksToday = topStocksToday[:cfg.TOPNSTOCKS]

            # Entry Logic
            for si in range(len(topStocksToday)):

                # ---- Get OHLC for current stock for today
                stockName = topStocksToday['stock'].iloc[si]
                todayDf = allStocksByDate[stockName][dates[di]]
                price = todayDf['open'][cfg.ENTRY]
                timestamp = todayDf['timestamp'][cfg.ENTRY]

                # quantity = int(cfg.INITIALCAPITAL / price)
                quantity = 1 # for pure return % per trade
                cost = price * quantity
                if quantity > 0:
                    openPositions.append(Position(
                        Name=stockName,
                        EntryTimeStamp=timestamp,
                        EntryPrice=price,
                        Quantity=quantity,
                        Type='long'
                    ))

                    stockMetrics[stockName].Orders.append(Order(
                        TimeStamp=timestamp,
                        Quantity=quantity,
                        Type='long',
                        PnL=0,
                        TotalCost=cost,
                        Price = price,
                        BaseLineVolumeMean = topStocksToday['baselinemean'].iloc[si],
                        EndVolumeMean = topStocksToday['endmean'].iloc[si],
                        MA15Mean = topStocksToday['ma15endmean'].iloc[si]
                    ))
                else:
                    stockMetrics[stockName].RanOutOfCash+=1
                print(stockName, price, timestamp)

        # Exit Logic

        for pi in range(len(openPositions)):
            
            if openPositions[pi].Status == 'closed':
                continue

            stockName = openPositions[pi].Name
            todayDf = allStocksByDate[stockName][dates[di]]
            
            timestamps = todayDf['timestamp']            
            if dates[di] == pd.Timestamp(openPositions[pi].EntryTimeStamp).date():
                # dont sell same day
                continue

            highs = todayDf['high']
            lows = todayDf['low']
            opens = todayDf['open']

            sold = False
            for i in range(len(todayDf)):
                
                # if timestamps[i] <= openPositions[pi].EntryTimeStamp:
                #     continue

                candleHigh = highs[i]
                candleLow = lows[i]
                candleOpen = opens[i]
                
                if cfg.TRAILING:
                    openPositions[pi].High = max(candleHigh, openPositions[pi].High)
                
                stopPrice = openPositions[pi].High * (1-STOPLOSS)
                stoplossTriggered = False

                sellPrice = 0

                if candleOpen < stopPrice:
                    stoplossTriggered = True
                    sellPrice = candleOpen

                elif candleLow <= stopPrice:
                    stoplossTriggered = True
                    sellPrice=stopPrice

                if stoplossTriggered:
                    noOfSharesToSell = openPositions[pi].Quantity
                    
                    openPositions[pi].Status = 'closed'
                    openPositions[pi].ExitPrice = sellPrice

                    timeStamp = timestamps[i]
                    openPositions[pi].ExitTimeStamp = timeStamp

                    entryPrice = openPositions[pi].EntryPrice
                    cost = sellPrice*noOfSharesToSell
                    profit = cost - (entryPrice*noOfSharesToSell)  

                    stockMetrics[stockName].Orders.append(Order(
                        TimeStamp = timestamps[i],
                        Quantity = noOfSharesToSell,
                        Type='close',
                        PnL=profit,
                        Price=sellPrice,
                        TotalCost=cost
                    ))
                    sold=True
                    break
            
            if sold:
                continue

            # sell eod if not sold entire day
            noOfSharesToSell = openPositions[pi].Quantity
            # sellPrice = todayDf['open'][-1]
            sellPrice = opens[-1]
            openPositions[pi].Status = 'closed'
            openPositions[pi].ExitPrice = sellPrice
            
            timeStamp = timestamps[-1]
            openPositions[pi].ExitTimeStamp = timeStamp

            entryPrice = openPositions[pi].EntryPrice
            cost = sellPrice*noOfSharesToSell
            profit = cost - (entryPrice*noOfSharesToSell)  

            stockMetrics[stockName].Orders.append(Order(
                TimeStamp = timeStamp,
                Quantity = noOfSharesToSell,
                Type='close',
                PnL=profit,
                Price=sellPrice,
                TotalCost=cost
            ))

    rows = []
    for p in openPositions:
        rows.append({
            "stock": p.Name,
            "type": p.Type,
            "entryTime": p.EntryTimeStamp,
            "exitTime": p.ExitTimeStamp,
            "entryPrice": round(p.EntryPrice, 2),
            "exitPrice": round(p.ExitPrice, 2),  
            "quantity": round(p.Quantity, 2),
            "entryCost": round(p.Quantity * p.EntryPrice, 2),
            "exitCost": round(p.Quantity * p.ExitPrice, 2),
            "status": p.Status,
            "pnl": round((p.ExitPrice - p.EntryPrice) * p.Quantity if p.Status == "closed" else 0, 2),
            "profitpct": round(((p.ExitPrice - p.EntryPrice) / p.EntryPrice) * 100 if p.Status == "closed" else 0, 4)
        })

    positionsDf = pd.DataFrame(rows)
    positionsByStock = dict(tuple(positionsDf.groupby('stock')))

    positionsDf.sort_values("exitTime", inplace=True)
    positionsDf.reset_index(drop=True, inplace=True)

    meanDF = pd.DataFrame(columns=['stock', 'profitPct', 'totalTrades', 'winRate', 'avgWinpct', 'avgLosspct', 'expentancypct', 'profitFactor'])
    for stock in positionsByStock.keys():


        
        df = positionsByStock[stock]

        totalTrades = len(df) 
        wins = df[df['profitpct'] > 0]
        losses = df[df['profitpct'] < 0]
        winRate = len(wins)/totalTrades if totalTrades > 0 else 0
        lossRate = 1-winRate
        avgWinPct = wins['profitpct'].mean() if len(wins) > 0 else 0 
        avgLossPct = losses['profitpct'].mean() if len(losses) > 0 else 0
        expentancyPct = (winRate * avgWinPct) - (lossRate * abs(avgLossPct))
        profitFactor = (wins['profitpct'].sum() / abs(losses['profitpct'].sum())) if len(losses) > 0 else float('inf')

        row = {
            "stock":stock,
            "profitPct": round((df['pnl'].sum()/df['entryPrice'].sum())*100, 2),
            "totalTrades": totalTrades,
            "winRate": round(winRate, 2),
            "avgWinpct": round(avgWinPct, 2),
            "avgLosspct": round(avgLossPct, 2),
            "expentancypct": round(expentancyPct, 2),
            "profitFactor": round(profitFactor, 2)
        }
        meanDF.loc[len(meanDF)] = row
        if cfg.GETTOP:
            positionsByStock[stock].to_csv(f'./results/Top_Stocks_Performance/Multiplier_{int(MULTIPLIER*100)}/Stoploss_{int(STOPLOSS*100)}/{stock}_positions.csv')
        else:
            positionsByStock[stock].to_csv(f'./results/Individual_Performance/Multiplier_{int(MULTIPLIER*100)}/Stoploss_{int(STOPLOSS*100)}/{stock}_positions.csv')
    
    # meanDF.to_csv(f"./results/Multi_{int(MULTIPLIER*100)}_SL_{int(STOPLOSS*100)}.csv")
    return meanDF

