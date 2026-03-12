"""
  @file LoadWorker.py
  @brief 
  @author Jade Cawley
  @version  V0.3.2
  @data 2026-03-12

Loads various parts of program and updates the splash screen

Main program flow (TODO)
"""
# python library imports
from queue import Queue
from queue import Empty as QueueEmpty
import socket
from threading import main_thread
import time

# external python library imports
from PySide6.QtCore import QObject, QThread, Signal

# program library imports
from server.QueueEvent import *

class LoadWorker(QThread):
    nextLoadStep = Signal(int)

    def __init__(self, queue, server, serverThread, dashThread):
        super().__init__()
        self.qMain = queue
        self.server = server
        self.serverThread = serverThread
        self.dashThread = dashThread
        
    def run(self):
        print("LW: Load Worker started")
        self.nextLoadStep.emit(0)
        
        #
        #
        # START TCP SERVER
        #
        #
        
        # get ip and port of server address
        ip, port = self.server.server_address
    
        # start server thread and wait 0.5 seconds
        print(f'LW: establishing server @ {ip}:{port}')
        self.serverThread.start()
        time.sleep(1)
        
        # if the server thread isn't created sucessfully, end the program
        if not self.serverThread.is_alive():
            print("LW: server thread crashed")
            return
        
        print(f"LW: Server loop running in thread: {self.serverThread.name}")
        self.nextLoadStep.emit(25)
        
        #
        #
        # START DASH HTTP SERVER
        #
        #
        
        # testing loading the next step...
        print(f'LW: establishing dash http server')
        self.dashThread.start()
        time.sleep(1)
        
        # if the server thread isn't created sucessfully, end the program
        if not self.dashThread.is_alive():
            print("LW: dash http server thread crashed")
            
        print(f"LW: {self.dashThread.name} started successfully")
        self.nextLoadStep.emit(25)
        
        #
        #
        # LOAD STEP 3
        #
        #
        
        # testing loading the next step...
        time.sleep(2)
        self.nextLoadStep.emit(25)
        print(f"LW: load 2")
        
        #
        #
        # LOAD STEP 4
        #
        #
        
        # testing loading the next step...
        time.sleep(2)
        self.nextLoadStep.emit(25)
        print(f"LW: load 3")
        
        time.sleep(2)
        