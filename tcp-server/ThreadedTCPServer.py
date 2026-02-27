import socket
import threading
import socketserver
import time 
from queue import Queue
from queue import Empty as QueueEmpty
from select import select

from packet import PacketMessage, construct_packet, is_valid_packet, is_valid_properties
from is_socket_closed import *
from QueueEvent import *

import struct

# class which inherits methods from ThreadingMixIn and TCPServer
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def start(self,qMain,qThread):
        self.qMain = qMain      # queue for sending messages to main thread
        self.qThread = qThread  # queue for recieving messages from main
                                # thread
        self.appSocket = None
        self.botSocket = None
        
        # run the server until it is shutdown
        try:
            self.serve_forever()
        except Exception as e:
            print(e)
            qMain.put(QueueEvent(SERVER_ERROR, ''))
            exit()
        
# this is a handler class, which we define the handle method
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    def __init__(self, qMain, qThread, *args, **keys):
        self.qMain = qMain      # queue for sending messages to main thread
        self.qThread = qThread  # queue for recieving messages from main 
                                # thread
        socketserver.BaseRequestHandler.__init__(self, *args, **keys)
        
        print("this worked!")
    """

    # this handles incoming TCP packets
    def handle(self):
        cur_thread = threading.current_thread()
        main_thread = threading.main_thread()
        clientAddr = f'{self.client_address[0]}:{self.client_address[1]}'
        qMain = self.server.qMain
        device = 'Unknown'
        
        # set timeout
        self.request.settimeout(20)
        
        print(f"server: New device connected @ {clientAddr}")
        
        while True:
            # get properties portion of packet
            pdata = ''
            try:
                raw = self.request.recv(13)
                pdata = str(raw, 'utf-8')
                    
            except TimeoutError:
                # may add a queue event here if necessary
                #qMain.put('WAITING')
                continue
            except ConnectionResetError:
                print(f"server: connection with {clientAddr} terminated without a proper goodbye :(")
                if device != 'Unknown':
                    qMain.put(QueueEvent(DEVICE_DISCONNECTED, device))
                exit()
                    
            # check if socket is still connected
            if pdata == '' and is_socket_closed(self.request):
                print(f"server: connection with {clientAddr} terminated without a proper goodbye :(")
                if device != 'Unknown':
                    qMain.put(QueueEvent(DEVICE_DISCONNECTED, device))
                exit()
                
            # allow client to end server here. If a bug in the code below
            # results in an unhandled exception, this will allow a client
            # to connect to the server and shut it down and restart it with
            # changes to code
            if pdata.upper().startswith("/CLOSE"):
                print(f'server: client {clientAddr} closed server')
                # build packet and send reponse
                dataOut = bytes(f'Server closed down', 'utf-8')
                qMain.put(QueueEvent(SERVER_END, ''))
                return
            
            ## These two commands are for testing, the normal devices should
            ## be determined when they send their first packet
            
            # send socket to main queue if /app command is passed (to set
            # this socket as the 'APP'
            if pdata.upper().startswith("/APP"):
                print(f'server: setting client {clientAddr} as APP')
                device = 'APP'
                qMain.put(QueueEvent(DEVICE_CONNECTED, device, socket = self.request))
                self.server.appSocket = self.request
                
                # ignore the rest of the data
                continue
                
            # send socket to main queue if /bot command is passed (to set
            # this socket as the 'BOT'
            if pdata.upper().startswith("/BOT") or pdata.upper().startswith("/RPI"):
                print(f'server: setting client {clientAddr} as RPI')
                device = 'RPI'
                qMain.put(QueueEvent(DEVICE_CONNECTED, device, socket = self.request))
                self.server.botSocket = self.request
                
                # ignore the rest of the data
                continue
                
            # get length of data from packet
            length = int.from_bytes(raw[9:13], 'big')
            
            if is_valid_properties(pdata):
                try:
                    # request rest of packet
                    data = ''
                    try:
                        data = str(self.request.recv(length + 5), 'utf-8')
                    except TimeoutError:
                        # add a queue event here if needed
                        #qMain.put('INCOMPLETE PACKET')
                        print(f"server: got incomplete packet from {clientAddr}")
                        continue
                    except ConnectionResetError:
                        print(f"server: connection with {clientAddr} terminated without a proper goodbye :(")
                        if device != 'Unknown':
                            qMain.put(QueueEvent(DEVICE_DISCONNECTED, device))
                        exit()
                
                    # construct Packet object
                    packet = PacketMessage(self.client_address[0], pdata + data)
                    
                    # let qMain know that a connection has initiated and pass the 
                    # socket and device name to the queue
                    if device == 'Unknown':
                        device = packet.src
                        qMain.put(QueueEvent(DEVICE_CONNECTED, device,
                            socket = self.request))
                        if device == 'APP':
                            self.server.appSocket = self.request
                        elif device == 'RPI':
                            self.server.botSocket = self.request
                            
                    # print data recieved to terminal
                    if packet.mtype == 'MSG':
                        print(f"server: Recv MSG:'{packet.data}' from {packet.src}")
                        
                        # these messages are commands handled by the server
                        qMain.put(QueueEvent(NET_MSG, device, msg = packet.data))
                        self.message_handler(packet)
                        
                    else:
                        print(f"server: Recv {packet.mtype}({packet.length} bytes) from {packet.src}")

                    # send packet object to main thread
                    if packet.mtype.upper() == 'DAT':
                        qMain.put(QueueEvent(NET_DAT, device, data = packet.data))
                    else:
                        qMain.put(QueueEvent(NET_IMG, device, data = packet.data))
                    
                except TimeoutError as e:
                    print(f'server: connection time out for {clientAddr}')
                    return
            else:
                # normal test message
                
                #readWaiting, _, _ = select([self.request],[],[])
                
                #if self.request in readWaiting:
                #if not pdata.endswith('/n'):
                #    print(ord(pdata[-1]))
                #    raw = self.request.recv(4096)
                #    pdata += str(raw, 'ascii')
                
                # set timeout to 0.01 to get rest of data without blocking
                self.request.settimeout(0.01)
                try:
                    raw = self.request.recv(4096)
                    pdata += str(raw, 'utf-8')
                except TimeoutError:
                    pass
                    
                # add to chat log
                qMain.put(QueueEvent(NET_MSG, device, msg = pdata))
                    
                # reset timeout
                self.request.settimeout(20)
                
                # echo whole message back to client
                print(f"server: echo '{pdata.rstrip()}' to {clientAddr}")
                self.request.sendall(bytes(pdata, 'utf-8'))
                qMain.put(QueueEvent(NET_RESPONSE, device, msg = pdata))
                
            """
            # get response from main thread
            resp = ""
            try:
                resp = qThread.get(timeout=20)
            except QueueEmpty:
                # after 20 seconds, we time out, and terminate the
                # connection
                print("Server: main thread no response, terminating \
                connection")
                self.end_connection(True)
                return
            
            # send ERROR response and terminate connection if main thread
            # sends empty response
            if resp == "":
               resp = "ERROR"
               self.end_connection(True)
               return
               
            print("Server: Sending '{}'".format(resp))
            dataOut = bytes("{}".format(resp), 'ascii')
            self.request.sendall(dataOut)
            """
            
    # this handles how the server responds to incoming 'MSG' type messages
    def message_handler(self, packet):
        if packet.data == 'EXIT':
            qMain.put(QueueEvent(DEVICE_DISCONNECTED, packet.src))
            print(f"server: ending connection with {self.client_address[0]}")
            return
            
        elif packet.data[:5] == 'SETUP':
            # let qMain know that a connection has initiated
            #qMain.put(f"{packet.src}@{self.client_address[0]}")
            
            # get attributes of device
            version = packet.data[5:37].strip()
            OS = packet.data[37:69].strip()
            width  = int.from_bytes(packet.data[69:71], 'big')
            height = int.from_bytes(packet.data[71:73], 'big')
            
            # print device properties to console
            print(f"i: Device connected @ {self.client_address[0]} is {packet.src}")
            print(f'i: version: {version}')
            print(f'i: OS: {OS}')
            print(f'i: Screen Dimensions: {width}x{height}')
            
            # send device properties to queue
            qMain.put(QueueEvent(DEVICE_GOT_CONFIG, packet.src,
                version = version, OS = OS, width = width, height = height))
            
            # send a packet back to confirm setup of server
            version = '0.1a' # TODO get from main ui?
            os = 'Windows'
            
            # build setup string with padding up to 32 bytes
            configStr = f'SETUP{version:{' '}<32}{os:{' '}<32}'
            
            # build packet and send reponse
            dataOut = construct_packet('SPC', packet.src,
                'MSG', configStr)
            print(f"server: sending device properties to {self.client_address[0]}")
            self.request.sendall(dataOut)
            qMain.put(QueueEvent(NET_RESPONSE, device, msg = configStr))
    
    '''
    # obsolete function, was used in the original to handle the device
    # disconnecting, this done inside the packet_handler method instead
    def end_connection(self, error = False):
        # tell main thread that client connection is ending
        #qMain.put("CONN_END")
        
        # send error signal, if connecting is ending due to an error
        if error:
            dataOut = bytes("ERROR", 'ascii')
            self.request.sendall(dataOut)
            
        # send exit signal to client
        dataOut = bytes("EXIT", 'ascii')
        self.request.sendall(dataOut)
    '''
    
if __name__ == "__main__":
    # create two queues, one for the server thread and one for the main thread
    qMain = Queue()
    qThread = Queue()

    # Port 0 means to select an arbitrary unused port
    # set port to 1991 for convience
    HOST, PORT = "localhost", 1991#0
   
    # init threaded server
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    
    with server:
        # get server IP address and port number
        ip, port = server.server_address
        print(f'main: establishing server @ {ip}:{port}')
        
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
        
        running = True
        while running:
            msg = ""
            resp = ""
            
            # get a message from the queue
            try:
                msg = qMain.get(timeout=25)
                print(f"main: [{msg}]")
            except QueueEmpty as e:
                if not server_thread.is_alive():
                    print('main: server thread crashed')
                    running = False
            
            if msg == "EXIT":
                print("main: Got EXIT signal")
                running = False
            
        print("main: exiting program")
        server.shutdown()
        exit()