from PySide6.QtCore import QObject, QThread, Signal#, pyqtSignal
from queue import Queue
from queue import Empty as QueueEmpty
import socket
from threading import main_thread
from QueueEvent import *


class QueueWatcher(QThread):
    newNetMessage = Signal(str, str, str)
    serverEND = Signal()
    deviceConnected = Signal(bool)
    deviceDisconnected = Signal(bool)
    logQueueEvent = Signal(str)
    
    def setQueue(self, queue):
        self.queue = queue
        
    def run(self):
        print("QW: QueueWatcher started")
        while True:
            try:
                queueEvent = self.queue.get(timeout=25)
                
                msg = ''
                device = queueEvent.device
                sType = f'{queueEvent.type}'
                
                if queueEvent.type == DEVICE_CONNECTED:
                    self.deviceConnected.emit(device == 'RPI')
                if queueEvent.type == DEVICE_DISCONNECTED:
                    self.deviceDisconnected.emit(device == 'RPI')
                    
                if queueEvent.type == NET_RESPONSE:
                    msg = queueEvent.msg
                    sType += 'NR'
                    self.newNetMessage.emit(msg, 'SPC', queueEvent.device)
                    
                elif queueEvent.type == NET_MSG:
                    msg = queueEvent.msg
                    sType += 'NM'
                    self.newNetMessage.emit(msg, queueEvent.device, 'SPC')
                
                elif queueEvent.type == SERVER_END:
                    self.serverEND.emit()
                    
                    return
                
                # add message to window only if there is a message
                
                
                # add queue event to debug log
                self.logQueueEvent.emit(queueEvent.description)
                
            except QueueEmpty as e:
                if not main_thread().is_alive():
                    print('main: server thread crashed')
                    running = False
            
        #if msg == 
        