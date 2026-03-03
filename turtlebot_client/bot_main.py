# from: https://www.geeksforgeeks.org/python/python-import-module-from-different-directory/
import sys
sys.path.insert(0, "../tcp-server")

import argparse
import socket
from packet import *
from turtlebot import TurtleBot
import threading
from query_handler import *

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
    #
    #
    # load ROS
    #
    #
    print('w: could not load ROS')
    
    #
    #
    # initialise sensors
    #
    #
    print('w: could not initialise sensors')
    
    # connect to tcp server
    print(f'i: connecting to TCP Server at {ipAddress}:{port}')
    serverSocket = socket.create_connection((ipAddress,port))
    
    # create query handler thread
    qh_thread = threading.Thread(
        target=run_query_handler, args=(serverSocket, turtlebot,),
        kwargs=None)
    qh_thread.name = 'Query Handler Thread'
    qh_thread.start()
    
    # ADD AWESOME CODE HERE!
    # Just test code
    for i in range(5):
        send_msg_to_server(serverSocket, f'iteration {i}')
    
    # to test functionality
    qh_thread.join()
    
    # call this when program ends
    serverSocket.close()

def send_msg_to_server(sock, StringData):
    # convert string data to bytes
    packet = construct_packet('RPI', 'SPC', 'MSG', StringData)
    
    # send to server
    sock.sendall(packet)

def send_csv_data_to_server(sock, StringData):
    # 
    # convert string data to bytes
    packet = construct_packet('RPI', 'SPC', 'DAT', StringData)
    
    # send to server
    sock.sendall(packet)

if __name__ == "__main__":
    # set up arguments for script
    parser = argparse.ArgumentParser(description = 'TurtleBot Main Program')
    parser.add_argument('ipaddress', type=str, help='ip_address:port', nargs='?')
    main()