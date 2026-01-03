TOPNSTOCKS = 100
MULTIPLIER = 1.5 # 200%
STOPLOSS = 0.02 # 2%
TAKEPROFIT = 0.06 #6%
TRENDTHRESHOLD = 0.0003 # 3% Slope of the trend should be greater than threshol0d
INITIALCAPITAL = 100000

TRAILING = True
TP = True

STARTDATE = '2024-01-01'
ENDDATE   = '2024-12-31'

BASELINEX = -135
BASELINEY = -20

ENDX = -20
ENDY = -10

ENTRY = -9

PATHTODATA = './data'

def getStocks():
    import os 
    return [os.path.join(PATHTODATA, f) 
            for f in os.listdir(PATHTODATA) 
            if f.endswith(".csv") and os.path.isfile(os.path.join(PATHTODATA, f))]

LISTOFSTOCKS = [
    # ----- Large Cap -----
    'data/data/largecap/RELIANCE.csv',
    'data/data/largecap/HDFCBANK.csv',
    'data/data/largecap/BHARTIARTL.csv',
    'data/data/largecap/TCS.csv',
    'data/data/largecap/ICICIBANK.csv',
    'data/data/largecap/SBIN.csv',
    'data/data/largecap/INFY.csv',
    'data/data/largecap/HINDUNILVR.csv',
    'data/data/largecap/ITC.csv',
    'data/data/largecap/KOTAKBANK.csv',
    'data/data/largecap/LT.csv',
    'data/data/largecap/AXISBANK.csv',
    'data/data/largecap/BAJFINANCE.csv',
    'data/data/largecap/MARUTI.csv',
    'data/data/largecap/NTPC.csv',
    'data/data/largecap/TATASTEEL.csv',
    'data/data/largecap/ULTRACEMCO.csv',
    'data/data/largecap/SUNPHARMA.csv',
    'data/data/largecap/WIPRO.csv',
    'data/data/largecap/HCLTECH.csv',

    # ----- Mid Cap -----
    'data/data/midcap/ABFRL.csv',
    'data/data/midcap/VOLTAS.csv',
    'data/data/midcap/CHOLAFIN.csv',
    'data/data/midcap/CROMPTON.csv',
    'data/data/midcap/DEEPAKNTR.csv',
    'data/data/midcap/GLENMARK.csv',
    'data/data/midcap/JUBLFOOD.csv',
    'data/data/midcap/MUTHOOTFIN.csv',
    'data/data/midcap/PAGEIND.csv',
    'data/data/midcap/PERSISTENT.csv',
    'data/data/midcap/POLYCAB.csv',
    'data/data/midcap/SRF.csv',
    'data/data/midcap/TATAELXSI.csv',
    'data/data/midcap/UBL.csv',
    'data/data/midcap/ZYDUSLIFE.csv',

    # ----- Small Cap -----
    'data/data/smallcap/AEGISLOG.csv',
    'data/data/smallcap/BALAMINES.csv',
    'data/data/smallcap/CERA.csv',
    'data/data/smallcap/DALBHARAT.csv',
    'data/data/smallcap/FINEORG.csv',
    'data/data/smallcap/GRANULES.csv',
    'data/data/smallcap/AJANTPHARM.csv', 
    'data/data/smallcap/INDIGO.csv',
    'data/data/smallcap/KEI.csv',
    'data/data/smallcap/LEMONTREE.csv',
    'data/data/smallcap/MAZDOCK.csv',
    'data/data/smallcap/RITES.csv',
    'data/data/smallcap/KPITTECH.csv',    
    'data/data/smallcap/TEJASNET.csv',
    'data/data/smallcap/HINDCOPPER.csv', 
]

