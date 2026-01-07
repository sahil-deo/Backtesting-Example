import pandas as pd
import configs.volume2_cfg as cfg

BASE_PATH = 'results/Individual_Performance'
OUT_PATH  = 'results/SortedByProfit'

if __name__ == '__main__':

    for multiplier in cfg.MULTIPLIER:
        commonDf = None  # reset per multiplier

        for stoploss in cfg.STOPLOSS:
            filename = f'{BASE_PATH}/Multi_{int(multiplier*100)}_SL_{int(stoploss*100)}.csv'
            name = f'Multi_{int(multiplier*100)}_SL_{int(stoploss*100)}'

            df = pd.read_csv(filename)

            # filter on stricter profit condition
            df = df[df['profitPct'] > 0.3]

            # keep minimal required columns
            df = df[['stock', 'profitPct']]
            df = df.rename(columns={'profitPct': name})

            # inner merge ensures stock survives all stoplosses
            if commonDf is None:
                commonDf = df
            else:
                commonDf = commonDf.merge(df, on='stock', how='inner')

        # skip empty results safely
        if commonDf is None or commonDf.empty:
            continue

        # compute average profit across stoplosses
        profitCols = [c for c in commonDf.columns if c.startswith('Multi_')]
        commonDf['avgProfitPct'] = round(commonDf[profitCols].mean(axis=1), 2)

        commonDf = commonDf.sort_values('avgProfitPct', ascending=False)

        # dynamic output per multiplier
        outFile = f'{OUT_PATH}/TopStocks_Multi_{int(multiplier*100)}.csv'
        commonDf.to_csv(outFile, index=False)
