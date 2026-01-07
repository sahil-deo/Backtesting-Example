from strategies.volume.volume2 import runBacktest
import configs.volume2_cfg as cfg
import pandas as pd
import multiprocessing as mp

def run_batch(args):
    i, j, batch_id, stocks = args

    print(f'Batch: {batch_id}')
    print(f'SL: {cfg.STOPLOSS[i]} MP: {cfg.MULTIPLIER[j]}')

    #  avoid shared state by passing stocks explicitly
    return runBacktest(i, j, stocks)


if __name__ == '__main__':
    
    listOfStocks = cfg.getStocks()

    print(f'Total CPUs: {mp.cpu_count()}')
    for i in range(len(cfg.STOPLOSS)):
        for j in range(len(cfg.MULTIPLIER)):

            batchSize = 10
            if cfg.GETTOP:
                batchSize = len(listOfStocks)
            
            n = len(listOfStocks)
            noOfBatches = n // batchSize

            tasks = []  #  collect batch tasks
            for k in range(noOfBatches):
                start = k * batchSize
                end = start + batchSize
                stocks_slice = listOfStocks[start:end]

                #  package arguments for multiprocessing
                tasks.append((i, j, k, stocks_slice))

            #  parallel execution starts here
            with mp.Pool(processes=mp.cpu_count()-1) as pool:
                results = pool.map(run_batch, tasks)

            #  concat results after multiprocessing
            meanDF = pd.concat(results, ignore_index=True)
            meanDF = meanDF.sort_values('profitPct', ascending=False)
            meanDF = meanDF.reset_index(drop=True)

            if cfg.GETTOP:
                meanDF.to_csv(
                    f"./results/Top_Stocks_Performance/Multi_{int(cfg.MULTIPLIER[j]*100)}_SL_{int(cfg.STOPLOSS[i]*100)}.csv",
                    index=False
                )
            else:
                meanDF.to_csv(
                    f"./results/Individual_Performance/Multi_{int(cfg.MULTIPLIER[j]*100)}_SL_{int(cfg.STOPLOSS[i]*100)}.csv",
                    index=False
                )
