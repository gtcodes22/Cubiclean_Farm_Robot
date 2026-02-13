import threading
import time 
from queue import Queue

print_lock = threading.Lock()

class MyThread(threading.Thread):
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.daemon = True
        self.receive_messages = args[0]
        self.isRunning = True
        
        self.mainQueue = None
        if type(args[1]) == type(Queue()):
            self.mainQueue = args[1]

    def run(self):
        print(threading.currentThread().getName(), self.receive_messages)
        while self.isRunning:
            val = self.queue.get()
            self.do_thing_with_message(val)

    def do_thing_with_message(self, message):
        if self.receive_messages:
            with print_lock:
                print(threading.currentThread().getName(), "Received {}".format(message))
                if message == None or message == "exit thread":
                    self.isRunning = False
                    
                elif message == "connected to unity?":
                    self.send("ye ye yeus?")
                    
    def send(self, msg):
        self.mainQueue.put(msg)
                    

if __name__ == '__main__':
    threads = []
    for t in range(10):
        q = Queue()
        threads.append(MyThread(q, args=(t % 2 == 0,)))
        threads[t].start()
        time.sleep(0.1)

    for t in threads:
        t.queue.put("Print this!")

    for t in threads:
        t.join()