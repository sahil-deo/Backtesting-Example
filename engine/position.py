class Position:
    def __init__(self, 
                 Name = '', 
                 Type = 'long',
                 Status = 'open', 
                 EntryTimeStamp = '', 
                 EntryPrice = 0, 
                 Quantity = 0, 
                 ExitTimeStamp = '', 
                 ExitPrice = 0, 
        ):
        
        self.Name = Name

        self.EntryPrice = EntryPrice
        self.ExitPrice = ExitPrice
        
        self.EntryTimeStamp = EntryTimeStamp
        self.ExitTimeStamp = ExitTimeStamp
        
        self.Quantity = Quantity
        self.Status = Status
        self.High = EntryPrice
        self.Low = EntryPrice
        self.Type = Type