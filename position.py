class Position:
    def __init__(self, EntryPrice = 0, Quantity = 0, EntryTimeStamp = '', ExitTimeStamp = '', Status = 'open', ExitPrice = 0):
        
        self.EntryPrice = EntryPrice
        self.ExitPrice = ExitPrice
        
        self.EntryTimeStamp = EntryTimeStamp
        self.ExitTimeStamp = ExitTimeStamp
        
        self.Quantity = Quantity
        self.Status = Status
        self.High = EntryPrice