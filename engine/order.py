class Order:
    def __init__(self, 
                 TimeStamp='', 
                 Name ='', 
                 Type = 'long', 
                 Price = 0, 
                 Quantity = 0, 
                 TotalCost=0, 
                 BaseLineVolume = 0, 
                 EndVolume = 0, 
                 BaseLineVolumeMean = 0, 
                 EndVolumeMean = 0,
                 MA15Mean = 0,
                 PnL = 0
        ):
        
        self.TimeStamp = TimeStamp
        self.Name = Name
        self.Type = Type # long / short / close 
        self.Quantity = Quantity
        self.Price = Price
        self.TotalCost = TotalCost
        self.BaseLineVolume = BaseLineVolume 
        self.EndVolume = EndVolume
        self.BaseLineVolumeMean = BaseLineVolumeMean 
        self.EndVolumeMean = EndVolumeMean
        self.MA15Mean = MA15Mean
        self.PnL = PnL
