import socket
import sleep

# a test client method which opens a socket, sends a message to the TCP
# server and gets a response as dictated by the main thread
def client(ip, port, src):
    # set test attributes for this client
    version = '0.1'
    os = 'android' if src == 'APP' else 'ROS2'
    width = int(1920).to_bytes(2,'big')
    height = int(1080).to_bytes(2,'big')
    
    # create config string to send to server
    configStr = f'SETUP{version:{ }<32}{os:{ }<32}{width}{height}'
    
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # connect to server
        sock.connect((ip, port))
        connectionActive = True
        state = 0
        msg = ""
        
        # whilst the connection is still active, test all the server
        # commands in sequence
        while connectionActive:
            match state:
                case 0:
                    msg = configStr
                case 1:
                    msg = "connected"
                case 2:
                    msg = "set.graphsize 640 480"   # turtlebot could expect error for this response
                case 3:
                    msg = "get.graphsize"
                case 4:
                    msg = "get.bed[4]"
                case 5:
                    msg = "get.position"
                case 6:
                    msg = "get.map"
                case 7:
                    msg = "update.map 0.5"
                case 8:
                    msg = "stop.update.map"
                case 9:
                    msg = "jibberish" # test response to invalid command
                    
                case _:
                    msg = "EXIT"
            
            print(f"{src}: sending '[{state}]{msg}'"
            
            # send command to server
            sock.sendall(construct_packet(src, 'SPC', 'MSG', msg))
            
            # wait for response
            response = str(sock.recv(1024), 'ascii')
            print(f"{src}: Received: {response}")
            
            # if we recieve an empty response, or EXIT, or go beyond state 10
            if response == "" or response == "EXIT" or state > 10:
                connectionActive = False
                print(f"{src}: Exiting...")
                
            state += 1
            time.sleep(3)