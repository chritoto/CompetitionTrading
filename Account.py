import datetime

class Account:
    
    """
    Data structures that holds the state (cash and owned stocks) of an account
    """
    
    
    def __init__(self, ID, startCash, liststocks):
        
        self.ID = ID
        self.nom = ''
        self.cash = startCash
        self.totalvalue = startCash
        self.actions = {}
        self.waitlist = []
        self.TotalValueHist = [[],[]]
        for stock in liststocks:
            self.actions[stock] = 0
        
    def getCash(self):
        return self.cash
    
    def getStocks(self):
        return self.actions
    
    def addCash(self, amount):
        self.cash += amount
        
    def addStock(self, stock, amount):
        self.actions[stock] += amount
        
    def getWaitList(self):
        return self.waitlist
    
    def addWaitList(self, action, buy, price, quantity, date):
        if len(self.waitlist) > 20:
            return 3
        self.waitlist.append([action, buy, price, quantity, date])
        return 0
    
    def removeWaitList(self, element):
        self.waitlist.remove(element)
    
    def updateTotalValue(self, stocksPrice, currentTime):
        stockValue = 0
        for i in self.actions.keys():
            stockValue += stocksPrice[i] * self.actions[i]
        self.totalvalue = self.cash + stockValue
        self.TotalValueHist[0].append(currentTime)
        self.TotalValueHist[1].append(self.totalvalue)
        return self.totalvalue
    
    def getTotalValue(self):
        return self.totalvalue
        
    