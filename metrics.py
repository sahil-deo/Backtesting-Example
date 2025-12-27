class Metrics:

    
    def __init__(self, NoOfSharesHolding = 0, PeakHolding = 0, CurrentShareValue = 0,
                INITIALCAPITAL = 0, CurrentCapital = 0, TotalCost = 0, RanOutOfCapital = 0,
                CAPITALPERBUY = 100, MULTIPLIER = 1, SELLMULTIPLIER = 1, 
                Buy = 0, Sell = 0, LastBuy = 0, LastSell = 0, ShareHigh = None,
                Equity = None, ShareValue = None, OrderProfit = None, Orders = None, Positions = None):

        # ========================
        # POSITION / HOLDINGS
        # ========================
        self.NoOfSharesHolding  = NoOfSharesHolding    # amount of shares held right now
        self.PeakHolding        = PeakHolding                    # maximum amount of shares held at a time
        self.CurrentShareValue  = CurrentShareValue       # current value of share

        # ========================  
        # CAPITAL & CASH FLOW   
        # ========================  
        self.INITIALCAPITAL     = INITIALCAPITAL    
        self.CurrentCapital     = CurrentCapital    
        self.TotalCost          = TotalCost                  # total cost of holding shares
        self.RanOutOfCapital    = RanOutOfCapital             # no of times when current cash is insufficient to buy a share

        # ========================  
        # TRADE SIZING / RISK   
        # ========================  
        self.CAPITALPERBUY      = CAPITALPERBUY              # capital fraction per buy
        self.MULTIPLIER         = MULTIPLIER                    # volume multiplier
        self.SELLMULTIPLIER     = SELLMULTIPLIER              # fraction of shares to sell

        # ========================  
        # ORDER COUNTS & PRICES 
        # ========================  
        self.Buy            = Buy                                # total buy orders executed
        self.Sell           = Sell                               # total sell orders executed
        self.LastBuy        = LastBuy                           # last buy price
        self.LastSell       = LastSell                          # last sell price
        self.ShareHigh      = ShareHigh                       # Highest Share Price since last buy
        self.LastBuyDate    = ''
        self.LastSellDate   = ''

        # ========================  
        # PERFORMANCE TRACKING  
        # ========================  
        self.Equity             = Equity if Equity is not None else []            # list of equity over time
        self.ShareValue         = ShareValue if ShareValue is not None else []     # list of share value over time
        self.OrderProfit        = OrderProfit if OrderProfit is not None else []   # list of executed order's profit and loss over time
        self.Orders             = Orders if Orders is not None else []
        self.Positions      = Positions if Positions is not None else []

class Order:
    def __init__(self, TimeStamp='', Quantity = 0, Type = '', PnL = 0, SharePrice = 0, TotalCost=0, BaseLineVolume = 0, EndVolume = 0, BaseLineVolumeMean = 0, EndVolumeMean = 0):
        
        self.TimeStamp = TimeStamp
        self.Quantity = Quantity
        self.Type = Type # buy or sell
        self.PnL = PnL
        self.TotalCost = TotalCost
        self.SharePrice = SharePrice
        self.BaseLineVolume = BaseLineVolume 
        self.EndVolume = EndVolume
        self.BaseLineVolumeMean = BaseLineVolumeMean 
        self.EndVolumeMean = EndVolumeMean

