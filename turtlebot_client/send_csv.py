import sys
sys.path.insert(0, "../tcp-server")

from packet import *

def send_msg_to_server(sock, StringData):
    # convert string data to bytes
    packet = construct_packet('RPI', 'SPC', 'MSG', StringData)
    
    # send to server
    sock.sendall(packet)

def send_csv_data_to_server(sock, filename):
    StringData = ''
    
    # read input file
    with open(filename, "r", newline="") as f:
        StringData = f.read()
    
    # convert string data to bytes
    packet = construct_packet('RPI', 'SPC', 'DAT', filename + '\x00' + StringData)
    
    # send to server
    sock.sendall(packet)
    
def get_csv_packet(filename):
    StringData = ''
    
    # read input file
    with open(filename, "r", newline="") as f:
        StringData = f.read()
    
    # convert string data to bytes
    return construct_packet('RPI', 'SPC', 'DAT', filename + '\x00' + StringData)
    
# test sending csvs to server
if __name__ == '__main__':
    import socket
    
    ipAddress = 'localhost'
    port = 1991
    
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
    
    # connect to tcp server
    print(f'i: connecting to TCP Server at {ipAddress}:{port}')
    serverSocket = socket.create_connection((ipAddress,port))
    
    # set timeout
    serverSocket.settimeout(20)
        
    print(f"send_csv: test sending csvs to {ipAddress}")
    
    send_msg_to_server(serverSocket, 'test msg 1')
    send_msg_to_server(serverSocket, 'test msg 2')
    send_msg_to_server(serverSocket, 'test msg 3')
    send_msg_to_server(serverSocket, 'test_file.csv')
    send_csv_data_to_server(serverSocket, 'test_file.csv')
    
    raw = serverSocket.recv(1024)
    print(f'send_csv: got "{str(raw, "utf-8")}"')
    serverSocket.close()