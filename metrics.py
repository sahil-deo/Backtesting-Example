class Metrics:

    
    def __init__(self, no_of_shares_holding = 0, peak_holding = 0, current_share_value = 0,
                initial_cash = 0, current_cash = 0, total_cost = 0, ran_out_of_cash = 0,
                capital_per_buy = 100, multipier = 1, sell_multiplier = 1, 
                buy = 0, sell = 0, last_buy = 0, last_sell = 0, 
                equity = [], share_value = [], order_profit = []):

        # ========================
        # POSITION / HOLDINGS
        # ========================
        self.no_of_shares_holding = no_of_shares_holding    # amount of shares held right now
        self.peak_holding = peak_holding                    # maximum amount of shares held at a time
        self.current_share_value = current_share_value      # current value of share

        # ========================  
        # CAPITAL & CASH FLOW   
        # ========================  
        self.initial_cash     = initial_cash    
        self.current_cash     = current_cash    
        self.total_cost       = total_cost                  # total cost of holding shares
        self.ran_out_of_cash  = ran_out_of_cash             # no of times when current cash is insufficient to buy a share

        # ========================  
        # TRADE SIZING / RISK   
        # ========================  
        self.capital_per_buy = capital_per_buy              # capital fraction per buy
        self.multiplier      = multipier                    # volume multiplier
        self.sell_multiplier = sell_multiplier              # fraction of shares to sell

        # ========================  
        # ORDER COUNTS & PRICES 
        # ========================  
        self.buy       = buy                                # total buy orders executed
        self.sell      = sell                               # total sell orders executed
        self.last_buy  = last_buy                           # last buy price
        self.last_sell = last_sell                          # last sell price

        # ========================  
        # PERFORMANCE TRACKING  
        # ========================  
        self.equity       = equity                          # list of equity over time
        self.share_value  = share_value                     # list of share value over time
        self.order_profit = order_profit                    # list of executed order's profit and loss over time
