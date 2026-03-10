from PySide6.QtCore import QObject, QThread, Signal#, pyqtSignal
from queue import Queue
from queue import Empty as QueueEmpty
import socket
from threading import main_thread
from QueueEvent import *


class QueueWatcher(QThread):
    newNetMessage = Signal(str, str, str)
    newCSVfile = Signal(str, str)
    serverEND = Signal()
    deviceConnected = Signal(bool)
    deviceDisconnected = Signal(bool)
    logQueueEvent = Signal(str)
    updateDeviceStatus = Signal(str,str,str)
    
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
                if queueEvent.type == DEVICE_UPDATE:
                    self.update_device_status(device, queueEvent.property, queueEvent.value)
                    
                if queueEvent.type == NET_RESPONSE:
                    msg = queueEvent.msg
                    sType += 'NR'
                    self.newNetMessage.emit(msg, 'SPC', queueEvent.device)
                    
                elif queueEvent.type == NET_MSG:
                    msg = queueEvent.msg
                    sType += 'NM'
                    self.newNetMessage.emit(msg, queueEvent.device, 'SPC')
                elif queueEvent.type == NET_DAT:
                    filename = queueEvent.filename
                    data = queueEvent.data
                    filesize = f'{len(data)} Bytes' if len(data) < 1024 else \
                       f'{len(data)/1024.0} KiBytes' if len(data)/1024.0 < 1024 else \
                       f'{len(data)/1048576.0} MiBytes'
                       
                    self.newNetMessage.emit(f'file recieved: {filename} ({filesize})', queueEvent.device, 'SPC')
                    self.newCSVfile.emit(filename, data)
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
        