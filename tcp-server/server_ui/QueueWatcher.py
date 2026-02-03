from PySide6.QtCore import QObject, QThread, Signal#, pyqtSignal
from queue import Queue
from queue import Empty as QueueEmpty
import socket
from threading import main_thread
from QueueEvent import *


class QueueWatcher(QThread):
    newNetMessage = Signal(str)
    serverEND = Signal()
    #appConnected = pyqtSignal(socket)
    #botConnected = pyqtSignal(socket)
    
    def setQueue(self, queue):
        self.queue = queue
        
    def run(self):
        print("QW: QueueWatcher started")
        while True:
            try:
                queueEvent = self.queue.get(timeout=25)
                
                msg = ''
                sType = f'{queueEvent.type}'
                if queueEvent.type == NET_RESPONSE:
                    msg = queueEvent.msg
                    sType += 'NR'
                    
                elif queueEvent.type == NET_MSG:
                    msg = queueEvent.msg
                    sType += 'NM'
                
                elif queueEvent.type == SERVER_END:
                    self.serverEND.emit()
                    
                    return
                
                # add message to window only if there is a message
                if msg:
                    print(f"QW: [{queueEvent.device}] {msg}")
                    self.newNetMessage.emit(msg)
                
                
                
            except QueueEmpty as e:
                if not main_thread().is_alive():
                    print('main: server thread crashed')
                    running = False
            
        #if msg == 
        