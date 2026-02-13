import argparse
import socket
from packet import *

def main():
    args = parser.parse_args()
    print(f'Test: {args.ipaddress}')
    
    # get ip address and port number from command line argument
    ipAddress = args.ipaddress.split(':')[0]
    port = args.ipaddress.split(':')[1]
    
    # connect to tcp server
    serverSocket = socket.create_connection((ipAddress,port))
    
    
    # ADD AWESOME CODE HERE!
    # Just test code
    for i in range(5):
        send_msg_to_server(serverSocket, f'iteration {i}')
    
    

    
    # call this when program ends
    serverSocket.close()

def send_msg_to_server(sock, StringData):
    # convert string data to bytes
    packet = construct_packet('RPI', 'SPC', 'MSG', StringData)
    
    # send to server
    sock.sendall(packet)

def send_csv_data_to_server():
    pass

if __name__ == "__main__":
    # set up arguments for script
    parser = argparse.ArgumentParser(description = 'TurtleBot Main Program')
    parser.add_argument('ipaddress', type=str, help='ip_address:port')
    main()