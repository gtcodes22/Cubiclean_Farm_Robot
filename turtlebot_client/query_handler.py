# from: https://www.geeksforgeeks.org/python/python-import-module-from-different-directory/
import sys
sys.path.insert(0, "../tcp-server")

import argparse
import socket
from packet import *
from is_socket_closed import *
from query_handler import *

def run_query_handler(ipport, socket, turtlebot):
    serverAddr = ipport[0]
    serverPort = ipport[1]
    
    # set timeout
    socket.settimeout(20)
        
    print(f"query handler: listening to queries from {serverAddr}")
    
    while True:
        # get properties portion of packet
        pdata = ''
        try:
            raw = socket.recv(13)
            pdata = str(raw, 'utf-8')
            print(f'query_handler: got packet [{pdata}][{len(pdata)}]')
                
        except TimeoutError:
            continue
        except ConnectionResetError:
            print(f"query handler: connection with {serverAddr} terminated without a proper goodbye :(")
            exit()
                    
        # check if socket is still connected
        if pdata == '' and is_socket_closed(socket):
            print(f"query handler: connection with {serverAddr} terminated without a proper goodbye :(")
            exit()
            
        # allow server to end client here. If a bug in the code below
        # results in an unhandled exception, this will allow the server
        # to shut the client down and restart it with changes to code
        if pdata.upper().startswith("/CLOSE"):
            print(f'query handler: server {serverAddr} closed client')
            # build packet and send reponse
            dataOut = bytes(f'client closed down', 'utf-8')
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
                packet = PacketMessage(serverAddr, pdata + data)
                
                # print data recieved to terminal
                if packet.mtype == 'MSG':
                    print(f"query handler: Recv MSG:'{packet.data}' from {packet.src}")
                    
                    # these messages are commands handled by the server
                    socket.sendall(message_handler(packet, turtlebot))
                    
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
            
            # echo whole message back to client
            print(f"query handler: echo '{pdata.rstrip()}' to {serverAddr}")
            socket.sendall(bytes(pdata, 'utf-8'))
                
def message_handler(packet, turtlebot):
    response = ''
    description = ''
    
    if packet.data.upper().startswith('/EXIT'):
        print(f"query handler: ending connection with {packet.src}")
        exit()
        
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
        
        # send device properties to queue
        qMain.put(QueueEvent(DEVICE_GOT_CONFIG, packet.src,
            version = version, OS = OS, width = width, height = height))
        
        # send a packet back to confirm setup of server
        version = '0.2.2' # TODO get from main ui?
        os = 'Ubuntu' # TODO get from operating system
        
        # build setup string with padding up to 32 bytes
        response = f'SETUP{version:{' '}<32}{os:{' '}<32}'
        
    elif packet.data.upper().startswith('/BATTERY'):
        description = 'device battery life'
        response = f'{turtlebot.get_battery_life()}%'
    elif packet.data.upper().startswith('/SPEEDCM'):
        description = 'device speed (in cm/s)'
        response = f'{turtlebot.get_speed_cm_ps()}'
    elif packet.data.upper().startswith('/PROGRESS'):
        description = 'device scan progress'
        response = f'{turtlebot.get_progress()}%'
        
    dataOut = construct_packet('SPC', packet.src, 'MSG', response)
    print(f"query handler: sending {description} to TCP Server")
    return dataOut
    