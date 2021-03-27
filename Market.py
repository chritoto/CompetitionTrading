import datetime
from Account import Account
import uuid 
import csv
from multiprocessing import Process, Queue
import plotly.graph_objects as go
import os

import threading
import time

class Market:
    
    """

    """
    
    startCash = 10000
    
    fACPC = "Donnees/Asclepius.csv"
    fAME = "Donnees/Amaterasu.csv"
    fOZV = "Donnees/Odziozo.csv"
    fSHT = "Donnees/shu.csv"
    fLAL = "Donnees/lavaleum2.csv"
    
    dACPC = {}
    dAME = {}
    dOZV = {}
    dSHT = {}
    dLAL = {}
    
    prices = {
        'ACPC' : 0,
        'AME' : 0,
        'OZV' : 0,
        'SHT' : 0,
        'LAL' : 0,
        'ETF' : 0
        }
    
    pricesDiv = {
        'ACPC' : 0,
        'AME' : 0,
        'OZV' : 0,
        'SHT' : 0
        }
    
    listStocks = ["ACPC","AME","OZV","SHT","LAL","ETF"]
    
    done = False
    
    
    
    def __init__(self, qDisp, vitesse):
        self.currentDateTime = datetime.datetime(2020, 3, 27, 9, 30, 0)
        self.accounts = {}
        self.qDisp = qDisp
        self.sleepTime = 1/vitesse
        
        #Import Data
        with open(self.fACPC, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%d/%m/%Y,%H:%M:%S')
                self.dACPC[date] = float(row[1])
                
        with open(self.fAME, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%d/%m/%Y,%H:%M:%S')
                self.dAME[date] = float(row[1])
        
        with open(self.fOZV, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%d/%m/%Y,%H:%M:%S')
                self.dOZV[date] = float(row[1])
                
        with open(self.fSHT, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%d/%m/%Y,%H:%M:%S')
                self.dSHT[date] = float(row[1])
                
        with open(self.fLAL, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%d/%m/%Y,%H:%M:%S')
                self.dLAL[date] = float(row[1])
                
        self.updatePrices()
        
        for key in self.pricesDiv.keys():
            self.pricesDiv[key] = self.prices[key]
        
        self.updateETF()
        self.updateqDisp()
        
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
    def start(self):
        self.timer = threading.Thread(target=self.countTime)
        self.timer.start()
    
    def stop(self):
        self.timer.run = False
        
    def countTime(self):
        while getattr(self.timer, "run", True):
            self.oldTime = time.time()
            time.sleep(self.sleepTime)
            i = int((time.time()-self.oldTime)/self.sleepTime)
            for j in range(i):
                self.currentDateTime += datetime.timedelta(0,0,0,0,5)
                if(self.currentDateTime.time() > datetime.time(16,0,0)):
                    self.currentDateTime += datetime.timedelta(hours=17,minutes=30)
                    if(self.currentDateTime.weekday()==5):
                        self.currentDateTime += datetime.timedelta(days=2)
            self.updatePrices()
            self.updateETF()
            self.manageWaitLists()
            self.updateTotalValues()
            self.updateqDisp()
                    
    def updatePrices(self):
        if self.currentDateTime not in self.dACPC:
            self.done = True
            self.stop()
            return
        self.prices['ACPC'] = self.dACPC[self.currentDateTime]
        self.prices['AME'] = self.dAME[self.currentDateTime]
        self.prices['OZV'] = self.dOZV[self.currentDateTime]
        self.prices['SHT'] = self.dSHT[self.currentDateTime]
        self.prices['LAL'] = self.dLAL[self.currentDateTime]
        
        
    def updateETF(self):
        val = 0
        for key in self.pricesDiv.keys():
            val += self.prices[key]/self.pricesDiv[key]
        self.prices['ETF'] = val
        
    def updateqDisp(self):
        equipes = {}
        for account in self.accounts.keys():
            equipes[self.accounts[account].nom] = [self.accounts[account].nom,
                                                   self.accounts[account].totalvalue,
                                                   self.accounts[account].cash,
                                                   self.accounts[account].actions['ACPC'],
                                                   self.accounts[account].actions['AME'],
                                                   self.accounts[account].actions['OZV'],
                                                   self.accounts[account].actions['SHT'],
                                                   self.accounts[account].actions['LAL'],
                                                   self.accounts[account].actions['ETF']]
        try:
            self.qDisp.get_nowait()
        except:
            pass
        self.qDisp.put([self.prices,self.currentDateTime, equipes])
        
    def manageWaitLists(self):
        for key in self.accounts.keys():
            waitlist = self.accounts[key].getWaitList()
            for i in waitlist:
                if i[1]: #limit Buy
                    if self.prices[i[0]] < i[2]:
                        self.marketBuy(key, i[0], i[3])
                        self.accounts[key].removeWaitList(i)
                    elif self.currentDateTime > i[4]:
                        self.accounts[key].removeWaitList(i)
                else: #limit Sell
                    if self.prices[i[0]] > i[2]:
                        self.marketSell(key, i[0], i[3])
                        self.accounts[key].removeWaitList(i)
                    elif self.currentDateTime > i[4]:
                        self.accounts[key].removeWaitList(i)
                    
        
    def updateTotalValues(self):
        for key in self.accounts.keys():
            self.accounts[key].updateTotalValue(self.prices, self.currentDateTime)
        
        
    def createAccount(self):
        ID = uuid.uuid4()
        account = Account(ID, self.startCash, self.listStocks)
        self.accounts[ID] = account
        return ID
    
    def setEquipe(self, ID, nom):
        if not ID in self.accounts:
            return None
        self.accounts[ID].nom = nom
        f = open("logs/"+nom+".txt", "w")
        f.close()
        self.accounts[ID].file = open("logs/"+nom+".txt", "a")
        
    def displayData(self):
        for key in self.accounts.keys():
            fig = go.Figure(go.Scatter(
                x = self.accounts[key].TotalValueHist[0],
                y = self.accounts[key].TotalValueHist[1],
                connectgaps=True
            ))
            fig.update_layout(xaxis={'type': 'date',
                                      'rangebreaks':[dict(bounds=["sat", "mon"]),
                                     {'pattern': 'hour', 'bounds': [16, 9.5]}]})
            fig.show()
    
    def getTime(self):
        return self.currentDateTime
    
    def getCash(self, ID):
        if not ID in self.accounts:
            return None
        return self.accounts[ID].getCash()
    
    def getStocks(self, ID):
        if not ID in self.accounts:
            return None
        return self.accounts[ID].getStocks()
    
    def getListStocks(self):
        return self.listStocks
    
    def getPrice(self,action):
        if action not in self.listStocks:
            return 0
        return self.prices[action]
    
    def getPrices(self):
        return self.prices
    
    def getPastPrice(self,action, debut, fin):
        if action not in self.listStocks:
            return 0
        if fin > self.currentDateTime:
            fin = self.currentDateTime
        dic = getattr(self, 'd'+action)
        tempdic = {}
        for key in dic.keys():
            if key >= debut and key <= fin:
                tempdic[key] = dic.get(key)
        return tempdic
    
    def marketBuy(self, ID, action, quantity):
        if action not in self.listStocks:
            return 1
        if not ID in self.accounts:
            return None
        cost = self.prices[action] * quantity
        if cost > self.accounts[ID].getCash():
            return 2
        self.accounts[ID].addCash(-cost)
        self.accounts[ID].addStock(action, quantity)
        self.accounts[ID].file.write('BUY: '+action+ " x"+str(quantity)+" at "+self.currentDateTime.strftime("%d/%m/%Y,%H:%M:%S")+"\n")
        self.accounts[ID].file.flush()
        return 0
    
    def marketSell(self, ID, action, quantity):
        if action not in self.listStocks:
            return 1
        if not ID in self.accounts:
            return None
        cost = self.prices[action] * quantity
        if quantity > self.accounts[ID].getStocks()[action]:
            return 2
        self.accounts[ID].addCash(cost)
        self.accounts[ID].addStock(action, -quantity)
        self.accounts[ID].file.write('SELL: '+action+ " x"+str(quantity)+" at "+self.currentDateTime.strftime("%d/%m/%Y,%H:%M:%S")+"\n")
        self.accounts[ID].file.flush()
        return 0
    
    def limitBuy(self, ID, action, limit, quantity):
        if action not in self.listStocks:
            return 1
        if not ID in self.accounts:
            return None
        cost = limit * quantity
        if cost > self.accounts[ID].getCash():
            return 2
        return self.accounts[ID].addWaitList(action, True, limit, quantity, self.currentDateTime + datetime.timedelta(days=7))
    
    def limitSell(self, ID, action, limit, quantity):
        if action not in self.listStocks:
            return 1
        if not ID in self.accounts:
            return None
        if quantity > self.accounts[ID].getStocks()[action]:
            return 2
        return self.accounts[ID].addWaitList(action, False, limit, quantity, self.currentDateTime + datetime.timedelta(days=7))
    
        
        
    