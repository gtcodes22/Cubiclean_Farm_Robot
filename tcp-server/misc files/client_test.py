from threaded_TCP_server import client
import socket
import threading
import socketserver
import time 

if __name__ == "__main__":
    HOST, PORT = "localhost", 1991
    ip = "192.168.137.190"
    port = 1991
    
    client_thread = threading.Thread( target=client, args=(ip, port),
                                                daemon=True)
            
    client_thread.start()
    
    print("running test client")
    
    client_thread.join()