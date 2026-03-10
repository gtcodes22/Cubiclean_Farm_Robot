# from: https://www.geeksforgeeks.org/python/python-import-module-from-different-directory/
import sys
sys.path.insert(0, "../tcp-server")

import os
import argparse
import socket as Socket
from packet import *
from is_socket_closed import *
from query_handler import *
from send_csv import *

def run_query_handler(ipport, socket, turtlebot):
    serverAddr = ipport[0]
    serverPort = ipport[1]
    
    # set timeout
    socket.settimeout(5)
        
    print(f"query handler: listening to queries from {serverAddr}")
    
    while True:
        # get properties portion of packet
        pdata = ''
        try:
            raw = socket.recv(13)
            # bug fix here, need to handle length seperately as it is
            # not utf-8 compliant
            pdata = str(raw[:9], 'utf-8') + ' ' * 4
            print(f'query_handler: got packet [{pdata}][{len(pdata)}]')
                
        except TimeoutError:
            print('query handler: waiting...')
            continue
        except ConnectionResetError:
            print(f"query handler: connection with {serverAddr} terminated without a proper goodbye :(")
            exit()
                    
        # check if socket is still connected
        if pdata == '' and is_socket_closed(socket):
            print(f"query handler: connection with {serverAddr} terminated without a proper goodbye :(")
            
            # send signal to bot_main.py thread through local socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1',1993))
                s.sendall(f'/EXIT'.encode('utf-8'))
            
            turtlebot.closing = True
            
            sys.exit()
            
        # allow server to end client here. If a bug in the code below
        # results in an unhandled exception, this will allow the server
        # to shut the client down and restart it with changes to code
        if pdata.upper().startswith("/CLOSE"):
            print(f'query handler: server {serverAddr} closed client')
            # build packet and send reponse
            dataOut = bytes(f'client closed down', 'utf-8')
            turtlebot.closing = True
            return
        
        # get length of data from packet
        length = int.from_bytes(raw[9:13], 'big')
        print(f'query_handler: length of data: {length}')
        if is_valid_properties(pdata):
            print('valid packet')
            try:
                # request rest of packet
                data = ''
                try:
                    data = str(socket.recv(length + 5), 'utf-8')
                except TimeoutError:
                    print(f"query handler: got incomplete packet from {serverAddr}")
                    continue
                except ConnectionResetError:
                    print(f"query handler: connection with {serverAddr} terminated without a proper goodbye :(")
                    exit()
            
                # construct Packet object
                packet = PacketMessage(serverAddr, pdata + data, length)
                
                # print data recieved to terminal
                if packet.mtype == 'MSG':
                    print(f"query handler: Recv MSG:'{packet.data}' from {packet.src}")
                    
                    # these messages are commands handled by the server
                    socket.sendall(message_handler(packet, turtlebot))
                    
                    if turtlebot.closing == True:
                        # close this thread and signal to main thread to close
                        with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as s:
                            s.connect(('127.0.0.1',1993))
                            s.sendall('/EXIT'.encode('utf-8'))
                        
                        socket.close()
                        exit()
                    
                else:
                    print(f"query handler: Recv {packet.mtype}({packet.length} bytes) from {packet.src}")
      
            except TimeoutError as e:
                print(f'query handler: connection time out for {serverAddr}')
                return
        else:
            # set timeout to 0.01 to get rest of data without blocking
            socket.settimeout(0.01)
            try:
                raw = socket.recv(4096)
                pdata += str(raw, 'utf-8')
            except TimeoutError:
                pass
                
            # reset timeout
            socket.settimeout(20)
            
            # don't echo
            # echo whole message back to client
            #print(f"query handler: echo '{pdata.rstrip()}' to {serverAddr}")
            #socket.sendall(bytes(pdata, 'utf-8'))
                
def message_handler(packet, turtlebot):
    response = ''
    description = ''
    
    if packet.data.upper().startswith('/EXIT'):
        print(f"query handler: ending connection with {packet.src}")
        description = 'bot client exiting signal'
        response = f'EXIT'
        turtlebot.closing = True
        
    elif packet.data.upper().startswith('/GET_MISSING_CSV'):
        OUT_DIR = os.path.join('.', 'OUT')
        OUTTEST_DIR = os.path.join('.', 'OUT_TEST')
        
        # get start of file names
        fnIndex = packet.data.index(':') + 1
        
        # get list of server files (remove the trailing 'comma')
        server_files = [x for x in packet.data[fnIndex:-1].split(',')]
        
        print(f'server files {server_files}')
        
        # if folders don't exist, create them
        if not os.path.isdir(OUT_DIR):
            os.makedirs(OUT_DIR)
        if not os.path.isdir(OUTTEST_DIR):
            os.makedirs(OUTTEST_DIR)
        
        # build list of files in each folder
        bot_files = [os.path.join(OUT_DIR, x) for x in os.listdir(OUT_DIR)]
        bot_files += [os.path.join(OUTTEST_DIR, x) for x in os.listdir(OUTTEST_DIR)]

        print(f'bot files {bot_files}')
        
        megaPacket = b''
        numFiles = 0
        
        for filename in bot_files:
            if filename.lower().endswith('.csv') or filename.lower().endswith('.log'):
                if filename not in server_files:
                    numFiles += 1
                    print(f'sending {filename} to TCP Server')
                    megaPacket += get_csv_packet(filename)
        
        print(f"query handler: sending megapacket containing {numFiles} files to TCP Server")
        
        return megaPacket
        
    elif packet.data.upper().startswith('/SETUP'):
        description = 'device properties'
        
        # get attributes of device
        version = packet.data[5:37].strip()
        OS = packet.data[37:69].strip()
        width  = int.from_bytes(packet.data[69:71], 'big')
        height = int.from_bytes(packet.data[71:73], 'big')
        
        # print device properties to console
        print(f'i: version: {version}')
        print(f'i: OS: {OS}')
        print(f'i: Screen Dimensions: {width}x{height}')
        
        # send a packet back to confirm setup of server
        version = '0.3.1' # TODO get from main ui?
        OS = 'Ubuntu' # TODO get from operating system
        
        # build setup string with padding up to 32 bytes
        response = f'SETUP{version:{' '}<32}{OS:{' '}<32}'
        
    elif packet.data.upper().startswith('/BATTERY'):
        description = 'device battery life'
        response = f'/BATTERY:{turtlebot.get_battery_life()}'
    elif packet.data.upper().startswith('/SPEEDCM'):
        description = 'device speed (in cm/s)'
        response = f'/SPEEDCM:{turtlebot.get_speed_cm_ps()}'
    elif packet.data.upper().startswith('/PROGRESS'):
        description = 'device scan progress'
        response = f'/PROGRESS:{turtlebot.get_progress()}'
        
    dataOut = construct_packet('RPI', packet.src, 'MSG', response)
    print(f"query handler: sending {description} to TCP Server")
    return dataOut
    