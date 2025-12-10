from PySide6.QtCore import QObject, QThread, pyqtSignal
from queue import Queue
from queue import Empty as QueueEmpty
import socket

class QueueWatcher(QObject):
    newNetMessage = pyqtSignal(str)
    appConnected = pyqtSignal(socket)
    botConnected = pyqtSignal(socket)
    
    def setQueue(self, queue):
        self.queue = queue
        
    def watch(self):
        try:
            msg = self.queue.get(timeout=25)
            print(f"main: [{msg}]")
        except QueueEmpty as e:
            if not server_thread.is_alive():
                print('main: server thread crashed')
                running = False
        
        if msg == 
        