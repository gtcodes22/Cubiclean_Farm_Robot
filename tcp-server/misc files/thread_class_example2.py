from thread_class_example import MyThread
import threading
import time 
from queue import Queue
from queue import Empty as QueueEmpty

print_lock = threading.Lock()
reply_lock = threading.Lock()

# not working, await outside async function
#def wait_for_message(q):
#    await q.not_empty()

if __name__ == '__main__':
    q = Queue()
    mainQ = Queue()
    
    serverThread = MyThread(q, args=(True,mainQ,))
    serverThread.start()
    #serverThread.join() # use join when closing down child threads
    time.sleep(0.1)

    # have you connected?
    serverThread.queue.put("connected to unity?")
    #reply_lock.lock()
    time.sleep(0.1)
    
    #wait_for_message(mainQ)
    msg = ""
    try:
        msg = mainQ.get(timeout=1)
        with print_lock:
            print(msg)
            
    except QueueEmpty:
        print("Error, no response! no no nooo")
        
    serverThread.queue.put(None)
    serverThread.isRunning = False
        

    
    