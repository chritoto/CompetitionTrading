
import threading
from multiprocessing import Process, Queue
import time

from Trader import Trader
from API import API
from Market import Market
from Visualization import Visual

def initVisual(qDisp, qStart):
    app = Visual(qDisp, qStart)
    app.app.run_server()

def main():
    
    qDisp = Queue()
    qStart = Queue()
    market = Market(qDisp)
    
    Tapp = Process(target=initVisual, args=(qDisp, qStart,))
    Tapp.start()
    
    print("ok")
    
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
        if(not qStart.empty()):
            start = qStart.get()
        else:
            start = market.done
    
    
    t1.run = False
    
    market.stop()
    
    t1.join()
    
    

if __name__ == "__main__":
    main()