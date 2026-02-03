import socket
import threading
import socketserver
import time 
from queue import Queue
from queue import Empty as QueueEmpty

from test_client import client
from packet import PacketMessage, construct_packet
from ThreadedTCPRequestHandler import ThreadedTCPRequestHandler, ThreadedTCPServer

# create two queues, one for the server thread and one for the main thread
# ideally, these would not be global variables
qMain = Queue()
qThread = Queue()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0
   
    # init threaded server
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    
    with server:
        # get server IP address and port number
        ip, port = server.server_address
        
        # create a thread which uses server.start as the starting function,
        # providing qMain and qThread as arguments
        server_thread = threading.Thread(target=server.start,
            args=(qMain,qThread,), kwargs=None)
        
        # A 'daemon' thread terminates when the main thread terminates
        server_thread.daemon = True
        
        # start server thread and wait 0.5 seconds
        server_thread.start()
        time.sleep(0.5)
        
        # if the server thread isn't created sucessfully, end the program
        if not server_thread.is_alive():
            print("main: server thread crashed")
            exit()
        else:
            print("main: Server loop running in thread:", server_thread.name)
        
        # create two client threads, representing the app and the bot
        client_thread = threading.Thread(target=client, args=(ip, port, 'APP'),
                                            daemon=True)
        client_thread2 = threading.Thread(target=client, args=(ip, port, 'RPI'),
                                            daemon=True)
                     
        # start tcp client test threads
        client_thread.start()
        client_thread2.start()
        
        running = True
        while running:
            msg = ""
            resp = ""
            
            # try getting a message from the queue
            try:
                msg = qMain.get(timeout=15)
                #with print_lock:
            except QueueEmpty:
                print("main: no response from server")
                running = False
            
            print(f"main: [{msg}]")
            
            if msg == "EXIT":
                print("Main: Got EXIT signal")
                running = False
            
        print("Main: exiting program")
        server.shutdown()
        exit()