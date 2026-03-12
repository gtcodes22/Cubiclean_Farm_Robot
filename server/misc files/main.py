import socket
import socketserver
import threading
import time
from threaded_TCP_server import ThreadedTCPRequestHandler, ThreadedTCPServer, client
from threaded_TCP_server import qMain, qThread, message_handler

from enum import Enum
import pygame
from pygame.locals import *
from bitarray import bitarray
from queue import Queue
from queue import Empty as QueueEmpty
#import spidev

class State(Enum):
    HALT = 0
    CONNECTION_WAIT = 1
    CONNECTED = 2
    

def main():
    isRunning = True
    clock = pygame.time.Clock()
    state = State.CONNECTION_WAIT
    
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 1991

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    #        threading.Thread.__init__(self, args=(), kwargs=None)
    #server_thread = threading.Thread(target=server.serve_forever, args=(), kwargs=None)
    
    server_thread = threading.Thread(target=server.start, args=(qMain,qThread,), kwargs=None)
    
   # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)
    
    if not server_thread.is_alive():
        print("Main: Server thread crashed")
        exit()
        
    print("Main: Server loop running in thread:", server_thread.name)
    #else:
    #    print("Server failed to initialise")
    #    exit()
    
    client_thread = threading.Thread( target=client, args=(ip, port),
                                            daemon=True)
        
    #client_thread.start()
    
    # initialise SPI connection
    #spi = spidev.SpiDev()
    channel, device = 0,0
    #spi.open(channel,device)
    
    # set reading to be single channel
    SINGDIFF = '1'
    
    # select channel zero
    INPUT_CHANNEL_CONFIG = '000'
    
    # message to send to SPI to get reading from a single ADC channel
    # (8 bits, start bit to first bit is 7 bits
    spi_msg = bitarray('01{}{}00'.format(SINGDIFF,INPUT_CHANNEL_CONFIG))
    
    # loop
    while isRunning:
        msg = ""
        resp = ""
        ADC = ""
        
        if state == State.CONNECTION_WAIT:
            # wait for connection
            
            print("Waiting for connection... (5s)")
            try:
                msg = qMain.get(timeout=20)
                if msg == "CONN_INIT":
                    state = State.CONNECTED
                print(msg)                 
            except QueueEmpty:
                # expected behaviour, just loop around until the user connects
                #pass
                
                # quit program for testing
                print("error")
                exit()
            
        elif state == State.CONNECTED:
            # get data from ADC over SPI
            #spi.writebytes(spi_msg)
            #data = spi.readbytes(4)
            #data_ba = bitarray(data)
            
            # just output raw data
            ADC = "FFA2"#data
            
            try:
                msg = qMain.get(timeout=20)
                #with print_lock:
            except QueueEmpty:
                print("Main: server didn't respond to put")
                state = State.CONNECTION_WAIT
            
            print("Main: [{}]".format(msg))
            
            if msg == "EXIT":
                print("Main: Got EXIT signal")
                #state = State.CONNECTION_WAIT
                # close main program (for testing)
                print("Main: exiting program")
                server.shutdown()
                exit()
            else:
                # handle message from client
                #resp = message_handler(msg, "15 N")
                resp = message_handler(msg, "ADC: {}".format(ADC))
                
                # put response onto qThread if program is still running
                qThread.put(resp)
        
        
        
        # run things at 50 fps
        clock.tick(50)
    
    server.shutdown()    

if __name__ == "__main__":
    main()