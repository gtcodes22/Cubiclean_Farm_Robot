#
# Main function
#
# This is the main function to be called when running the PC server. It
# will set up a server thread, allow messages to be recieved/sent to either
# rpi or phone app, and process data through matlab and pass that along to
# the app.

# requires PySide6 to be installed for the interface

# python library imports
import sys
import random

# program library imports
from ThreadedTCPServer import *
from server_ui import mainwindow
#from debug_print import *

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError as e:
    print('PySide6 required to run this program, install via pip install' +
    ' pyside6')
    exit()
    
def main():
    # create two queues, one for the server thread and one for the main thread
    qMain = Queue()
    qThread = Queue()

    # Port 0 means to select an arbitrary unused port
    # set port to 1991 for convience
    HOST, PORT = "localhost", 1991#0
   
    # init threaded server
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    
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
        return
    
    print(f"main: Server loop running in thread: {server_thread.name}")
    
    # start running the QT app
    mainwindow.qMain(server, qMain, qThread)
    
    # once the QT closes, shutdown the server and exit
    print("main: exiting program")
    server.shutdown()
    sys.exit()
    
if __name__ == "__main__":
    main()