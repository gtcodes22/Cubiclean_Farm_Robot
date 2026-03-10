# from: https://www.geeksforgeeks.org/python/python-import-module-from-different-directory/
import sys
sys.path.insert(0, "../tcp-server")

import argparse
import socket
from packet import *
from turtlebot import TurtleBot
import threading
from query_handler import *
import time
import sys
from send_csv import *
from is_socket_closed import *

def main():
    args = parser.parse_args()
    ipAddress = None
    port = 1991
    turtlebot = TurtleBot()
    
    # connect to server
    if args.ipaddress == '?' or not args.ipaddress:
        
        # set up udp socket listening on 0.0.0.0 i.e. all net interfaces
        # from: https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python#27893987
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(('', 1995))
        client_socket.settimeout(2.0)
        
        # attempt 5 times to find the server
        # in future, this could displayed in an window
        for attempts in range(5):
            print(f'i: listening for server broadcast, attempt {attempts + 1}/5')
            
            # try getting data from socket
            try:
                data, server = client_socket.recvfrom(1024)
                print(f'Got message: \'{data}\' from {server}')
                ipAddress = server[0]
                break
            except socket.timeout:
                print('i: request timed out')
        
        # close the socket
        client_socket.close()
        
        if ipAddress == None:
            print('ERROR: Could not find server!')
            sys.exit()
    else:
        # get ip address and port number from command line argument
        ipAddress = args.ipaddress.split(':')[0]
        port = args.ipaddress.split(':')[1]
    
    # set up socket for listening from data script
    # from: https://coderivers.org/blog/interprocess-communication-python/#shared-memory
    localSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    localSocket.bind(('127.0.0.1',1993))
    
    # connect to tcp server
    print(f'i: connecting to TCP Server at {ipAddress}:{port}')
    serverSocket = socket.create_connection((ipAddress,port))
    
    # create query handler thread
    qh_thread = threading.Thread(
        target=run_query_handler, args=((ipAddress,port,),serverSocket, turtlebot,),
        kwargs=None)
    qh_thread.name = 'Query Handler Thread'
    qh_thread.daemon = True
    qh_thread.start()
    
    # start listening on socket
    localSocket.listen(1)
    isRunning = True
    
    turtlebot.closing = False
    
    # send initial message to server
    send_msg_to_server(serverSocket, 'Hi TCP Server!')
    
    # Loop: whenever we recieve a filename on the local socket, send
    # that file to the server
    while isRunning:
        # new connection
        conn, addr = None, None
        try:
            conn, addr = localSocket.accept()
            isConnected = True
        except Exception as e:
            print(f"bot_main: connection with server raised {e} :(")
            isRunning = False
            turtlebot.closing = True
            continue
            
        print('bot_main: local connection made')
        
        while isConnected:
            # attempt to get data
            try:
                raw = conn.recv(1024)
                msg = str(raw, 'utf-8')
                print(f'bot_main: Got: "{msg}"')
            except TimeoutError:
                continue
            except ConnectionResetError:
                print(f"bot_main: local socket terminated without a proper goodbye :(")
                isConnected = False
        
            # check if socket is still connected
            if msg == '' and is_socket_closed(conn):
                print('local socket closed')
                isConnected = False

            if msg.upper().startswith('/EXIT'):
                isConnected = False
                isRunning = False
                localSocket.close()
                continue
            elif msg.upper().endswith('.CSV'):
                for filename in msg.split(','):
                    # last minute edit to convert filepaths from linux to
                    # windows
                    filename.replace('/','\\')
                    
                    print(f'sending {filename} to TCP Server')
                    send_csv_data_to_server(serverSocket, filename)
                
                
        # check to see if the bot is closing
        isRunning = not turtlebot.closing
    
    # ADD AWESOME CODE HERE!
    # Just test code
    #for i in range(5):
    #    send_msg_to_server(serverSocket, f'iteration {i}')
    
    # read and send a file to the TCP Server
    #send_csv_data_to_server(serverSocket, 'test,1,2')
    
    # wait for qh_thread to end
    print('waiting for qh_thread to end')
    qh_thread.join()
    
    # call this when program ends
    serverSocket.close()
    sys.exit()


if __name__ == "__main__":
    # set up arguments for script
    parser = argparse.ArgumentParser(description = 'TurtleBot Main Program')
    parser.add_argument('ipaddress', type=str, help='ip_address:port', nargs='?')
    main()