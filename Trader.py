
import threading
import time
import numpy

class Trader:
    
    """
    
    
    Implantez ici votre algorithme de trading. Le marche est accessible avec la
    variable Market. Les differentes fonctions disponibles sont disponibles dans
    le fichier API et expliquees dans le document de la competition
    """
    
    #Nom de l'equipe:
    equipe = 'TEST'

    def __init__(self, API):
        
        self.API = API
        self.API.setEquipe(self.equipe)
        
    """Function called at start of run"""
    def run(self):
        
        """You can add initialization code here"""
        
        
        self.t = threading.currentThread()
        while getattr(self.t, "run", True):
            self.trade()
            
            
            
    """Your trading algorithm goes here!
        The function is called continuously"""
    def trade(self):
        time.sleep(0.05)
        self.API.marketBuy('LAL',1)
       # print(self.API.getUserStocks())
        #print(self.API.getPastPrice("ACPC", datetime.datetime(2019,1,1),datetime.datetime(2020, 4, 2)))
        #print(self.API.getPrice("ACPC"))
    