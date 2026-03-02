from PySide6.QtCore import QObject, QThread, Signal#, pyqtSignal
from queue import Queue
from queue import Empty as QueueEmpty
import socket
from threading import main_thread
from QueueEvent import *
import time

class LoadWorker(QThread):
    nextLoadStep = Signal(int)
    '''
    newNetMessage = Signal(str, str, str)
    serverEND = Signal()
    deviceConnected = Signal(bool)
    deviceDisconnected = Signal(bool)
    logQueueEvent = Signal(str)
    '''
    def __init__(self, queue, server, serverThread):
        super().__init__()
        self.qMain = queue
        self.server = server
        self.serverThread = serverThread
        
    def run(self):
        print("LW: Load Worker started")
        
        self.nextLoadStep.emit(0)
        
        # get ip and port of server address
        ip, port = self.server.server_address
    
        # start server thread and wait 0.5 seconds
        print(f'main: establishing server @ {ip}:{port}')
        self.serverThread.start()
        time.sleep(1)
        
        # if the server thread isn't created sucessfully, end the program
        if not self.serverThread.is_alive():
            print("main: server thread crashed")
            return
        
        print(f"LW: Server loop running in thread: {self.serverThread.name}")
        self.nextLoadStep.emit(25)
        
        # testing loading the next step...
        time.sleep(3)
        self.nextLoadStep.emit(25)
        print(f"LW: load 1")
        
        # testing loading the next step...
        time.sleep(3)
        self.nextLoadStep.emit(25)
        print(f"LW: load 2")
        
        # testing loading the next step...
        time.sleep(3)
        self.nextLoadStep.emit(25)
        print(f"LW: load 3")
        
        time.sleep(2)
        