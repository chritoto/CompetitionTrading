
import threading
from multiprocessing import Process, Queue
import time

from Trader import Trader
from API import API
from Market import Market
from Visualization import Visual
import matplotlib.pyplot as plt

#À modifier pour changer la vitesse de simulation
vitesse = 400

def initVisual(qDisp, qStart, qData):
    app = Visual(qDisp, qStart, qData)
    app.app.run_server()

def main():
    
    qDisp = Queue()
    qStart = Queue()
    qData = Queue()
    market = Market(qDisp, vitesse)
    
    Tapp = Process(target=initVisual, args=(qDisp, qStart, qData,))
    Tapp.start()
    
    
    start = False
    while(not start):
        while(qStart.empty()):
            time.sleep(0.1)
        start = qStart.get()
    
    api1 = API(market)
    trader1 = Trader(api1)
    t1 = threading.Thread(target=trader1.run)
    
    t1.start()
    
    market.start()
    

    while(start):
        while(qStart.empty() and not market.done):
            time.sleep(0.1)
            try:
                data = qData.get_nowait();
                if(data == True):
                    market.displayData()
            except:
                pass
        if(not qStart.empty()):
            start = qStart.get()
        else:
            start = market.done
    
    
    t1.run = False
    
    
    if market.done:
        while(start):
            while(qStart.empty()):
                time.sleep(0.1)
            try:
                data = qData.get_nowait();
                if(data == True):
                    market.displayData()
            except:
                pass
            start = qStart.get()
            
    market.stop()
    
    t1.join()
    
    

if __name__ == "__main__":
    main()