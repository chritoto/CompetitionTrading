

class API:
    
    """Initialize the API and creates a new market user"""
    def __init__(self, Market):
        self.market = Market
        self.ID = self.market.createAccount()
        
    """Defini le nom de lequipe"""
    def setEquipe(self, nom):
        self.market.setEquipe(self.ID, nom)
        
    """Returns the current date and time of the market"""
    def getTime(self):
        return self.market.getTime()
        
    """Returns the list of the stocks on the market"""
    def getListStocks(self):
        return self.market.getListStocks()
        
    """Returns the price of the specified Stock if valid, 0 otherwise"""
    def getPrice(self,action):
        return self.market.getPrice(action)
        
    """Returns a dictionary of the past dates and time
        and the corresponding values"""
    def getPastPrice(self,action, debut, fin):
        return self.market.getPastPrice(action, debut, fin)
        
    def getArticles(self,action, debut):
        pass
    
    """Returns a dictionary of the current stocks owned by the user"""
    def getUserStocks(self):
        return self.market.getStocks(self.ID)
    
    """Returns the current cash of the user"""
    def getUserCash(self):
        return self.market.getCash(self.ID)
        
    """Attemps to buy the specified quantity of the stock
        Returns 0 if successfull, 1 if the stock is wrongly inputed
        and 2 if the quantity asked cost more than the cash in the account"""
    def marketBuy(self, action, quantity):
        return self.market.marketBuy(self.ID, action, quantity)
    
    """Attemps to sell the specified quantity of the stock
        Returns 0 if successfull, 1 if the stock is wrongly inputed
        and 2 if asked to sell more than currently owned"""
    def marketSell(self, action, quantity):
        return self.market.marketSell(self.ID, action, quantity)
    
    """Adds the stock, the price limit and the quantity to the list of limitBuys
        Returns 0 if successfull, 1 if the stock is wrongly inputed,
         2 if asked to more than cash available and 3 if the limit of 
         20 current limit buys or sells is reached"""
    def limitBuy(self, action, limit, quantity):
        return self.market.limitBuy(self.ID, action, limit, quantity)
    
    """Adds the stock, the price limit and the quantity to the list of limitSells
        Returns 0 if successfull, 1 if the stock is wrongly inputed,
         2 if asked to sell more than currently owned and 3 if the limit of 
         20 current limit buys or sells is reached"""
    def limitSell(self, action, limit, quantity):
        return self.market.limitSell(self.ID, action, limit, quantity)