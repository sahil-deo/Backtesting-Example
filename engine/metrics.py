class Metrics:

    
    def __init__(self, NoOfSharesHolding = 0, NoOfSharesShort = 0, PeakHolding = 0, PeakShort = 0, CurrentShareValue = 0,
                INITIALCAPITAL = 0, CurrentCapital = 0, RanOutOfCapital = 0,
                CAPITALPERORDER = 100, MULTIPLIER = 1, 
                Short = 0, Long = 0, LastShort = 0, LastLong = 0, LastClose = 0, ShareHigh = None, ShareLow = None,
                Equity = None, ShareValue = None, OrderProfit = None, Orders = None, Positions = None):

        # ========================
        # POSITION / HOLDINGS
        # ========================
        self.NoOfSharesHolding  = NoOfSharesHolding   # amount of shares held right now
        self.NoOfSharesShort    = NoOfSharesShort     # amount of shares short right now
        self.PeakHolding        = PeakHolding         # maximum amount of shares held at a time
        self.PeakShort          = PeakShort           # maximum amount of shares short at a time
        self.CurrentShareValue  = CurrentShareValue   # current value of share

        # ========================  
        # CAPITAL & CASH FLOW   
        # ========================  
        self.INITIALCAPITAL     = INITIALCAPITAL    
        self.CurrentCapital     = CurrentCapital    
        self.RanOutOfCapital    = RanOutOfCapital             # no of times when current cash is insufficient to execute an order

        # ========================  
        # TRADE SIZING / RISK   
        # ========================  
        self.CAPITALPERORDER    = CAPITALPERORDER             # capital fraction per buy
        self.MULTIPLIER         = MULTIPLIER                  # volume multiplier

        # ========================  
        # ORDER COUNTS & PRICES 
        # ========================  
        self.Short          = Short                           # total short orders executed
        self.Long           = Long                            # total long orders executed
        self.LastLong       = LastLong                        # last long order price
        self.LastShort      = LastShort                       # last short order price
        self.LastClose      = LastClose                       # last close order price  
        self.ShareHigh      = ShareHigh                       # highest Share Price since last long
        self.ShareLow       = ShareLow                        # lowest Share Price since last short 
        self.LastLongDate   = ''
        self.LastShortDate  = ''
        self.LastCloseDate  = ''

        # ========================  
        # PERFORMANCE TRACKING  
        # ========================  
        self.Equity             = Equity if Equity is not None else []            # list of equity over time
        self.ShareValue         = ShareValue if ShareValue is not None else []     # list of share value over time
        self.OrderProfit        = OrderProfit if OrderProfit is not None else []   # list of executed order's profit and loss over time
        self.Orders             = Orders if Orders is not None else []
        self.Positions      = Positions if Positions is not None else []


