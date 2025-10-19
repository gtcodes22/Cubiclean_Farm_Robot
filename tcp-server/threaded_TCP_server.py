import socket
import threading
import socketserver
import time 
from queue import Queue
from queue import Empty as QueueEmpty

# create two queues, one for the server thread and one for the main thread
qMain = Queue()
qThread = Queue()

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
        
        # let qMain know that a connection has initiated
        qMain.put("CONN_INIT")
        
        while True:
            # get data as ascii string
            data = str(self.request.recv(1024), 'ascii')
            
            # print data recieved to terminal
            print("Server: Recieved '{}'".format(data))
            
            # if we get sent EXIT, terminate the connection
            if data == "EXIT":
                print("Server: exit signal recieved, terminating \
                connection")
                self.end_connection(False)
                return
            
            # send data to main thread
            qMain.put(data)
            
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
            
    def end_connection(self, error = False):
        # tell main thread that client connection is ending
        qMain.put("CONN_END")
        
        if error:
            # send exit signal to client
            dataOut = bytes("ERROR", 'ascii')
            self.request.sendall(dataOut)
            
        # send exit signal to client
        dataOut = bytes("EXIT", 'ascii')
        self.request.sendall(dataOut)
           


# class which inherits methods from ThreadingMixIn and TCPServer
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def start(self,qMain,qThread):
        self.qMain = qMain      # queue for sending messages to main thread
        self.qThread = qThread  # queue for recieving messages from main
                                # thread
        
        # run the server until it is shutdown
        self.serve_forever()
    
    # are these methods called?
    def put(self, msg):
        print("TEST: THIS FUNCTION WAS CALLED")
        self.qThread.put(msg)
        
    # used by server thread to communicate with main thread
    def out(self, msg):
        print("TEST: THIS FUNCTION WAS CALLED")
        self.qMain.put(msg)


# a test client method which opens a socket, sends a message to the TCP
# server and gets a response as dictated by the main thread
def client(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        connectionActive = True
        state = 0
        msg = ""
        
        while connectionActive:
            match state:
                case 0:
                    msg = "HI"
                case 7:
                    msg = "EXIT"
                case _:
                    msg = "GET"
            
            print("Client: sending '[{}]{}'".format(state, msg))
            
            sock.sendall(bytes(msg, 'ascii'))
            response = str(sock.recv(1024), 'ascii')
            print("Client: Received: {}".format(response))
            
            if response == "" or response == "EXIT" or state > 10:
                connectionActive = False
                print("Client: Exiting...")
                
            state += 1
            time.sleep(1)

# this is called by the main thread. The message is what is recieved from
# the server and the response is what is sent in return
def message_handler(message, sensors):
    resp = ""
    
    if message == "HI":
        resp = "ACK"
    elif message == "GET":
        resp = sensors
    elif message == "EXIT":
        # client is ending, end program
        resp == "EXIT"
    else:
        # just send message back
        resp = message
                
    return resp
                
if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0
   
    # init threaded server
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    
    #server.RequestHandlerClass.set_queues(None, qMain, qThread)
    
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        #        threading.Thread.__init__(self, args=(), kwargs=None)
        #server_thread = threading.Thread(target=server.serve_forever, 
        #                                 args=(), kwargs=None)
        
        server_thread = threading.Thread(target=server.start,
            args=(qMain,qThread,), kwargs=None)
        
       # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        # if the server thread isn't created sucessfully, end the program
        if not server_thread.is_alive():
            print("Main: server thread crashed")
            exit()
            
        print("Main: Server loop running in thread:", server_thread.name)

        #client(ip, port)
        #client(ip, port)
        
        client_thread = threading.Thread( target=client, args=(ip, port),
                                            daemon=True)
        
        client_thread.start()
        running = True
        while running:
            
            msg = ""
            resp = ""
            try:
                msg = qMain.get(timeout=5)
                #with print_lock:
            except QueueEmpty:
                print("Main: server didn't respond to put")
                running = False
            
            print("Main: [{}]".format(msg))
            
            if msg == "EXIT":
                print("Main: Got EXIT signal")
                running = False
            else:
                # handle message from client
                resp = message_handler(msg, "15 N")
                
                # put response onto qThread if program is still running
                qThread.put(resp)
            
        print("Main: exiting program")
        server.shutdown()
        exit()