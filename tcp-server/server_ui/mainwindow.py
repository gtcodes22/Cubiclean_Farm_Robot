# This Python file uses the following encoding: utf-8
import sys
import struct

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject, QThread#, pyqtSignal
#from PySide6 import QtUiTools

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from server_ui.ui_form import Ui_MainWindow

def clickTest():
    print("click!")

def returnTest():
    print("tap!")

def appDebug(msg):
    print(f'Debug log {msg}')
    ui = Ui_MainWindow()
    
    ui.scrollAreaWidgetContents_appDebug
    
def sendMessage(ui, isPi = False):
    # add src and destination to message
    src = 'SPC'
    des = 'APP'
    if isPi:
        des = 'RPI'
    
    # type (category) is always message
    cat = 'MSG'
    
    # end is always 00A86B
    end = '\x00\xA8\x6B'
    
    # string to hold message
    msg = ''
    
    if isPi:
        msg = str(ui.lineEdit_rpi.text())
        ui.lineEdit_rpi.clear()
    else:
        msg = str(ui.lineEdit_app.text())
        ui.lineEdit_app.clear()
        
    # get length of message and convert it into 4 bytes, big endian
    length = struct.pack('>i', len(msg))
    
    print(f'ui: sending {src}{des}{cat}{length}{msg}{end}')

def addToChatLog(self, ui, message, isPi = False):
    ui.scrollArea_app
    
class MainWindow(QMainWindow):
    def __init__(self, server, qMain, qThread, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = server
        self.qMain = qMain
        self.qThread = qThread
        
        # set up a qThread to watch the queues
        #self.thread = Worker()
        
        # load widgets from UI file so we can manipulate them in the
        # program
        #loader = QtUiTools.QUiLoader()
        #ui = loader.load('form.ui', parent)
        
        # get the lineEdit widget for the app messenger
        #self.phoneAppLineEdit = self.ui.lineEdit_app
        self.connectWidgets()
    
    def connectWidgets(self):
        self.ui.lineEdit_app.returnPressed.connect(self.sendMessageApp)
        self.ui.lineEdit_rpi.returnPressed.connect(self.sendMessageRPi)
        self.ui.pushButton_connect_rpi.clicked.connect(clickTest)

    def sendMessageApp(self):
        # send a message to the phone app
        msg = sendMessage(self.ui, False)
        server.appSocket.sendall(bytes(msg, 'ascii'))
        
    def sendMessageRPi(self):
        # send a message to the turtlebot
        msg = sendMessage(self.ui, True)
        server.botSocket.sendall(bytes(msg, 'ascii'))

def qMain(server, qMain, qThread):
    app = QApplication(sys.argv)
    widget = MainWindow(server, qMain, qThread)
    widget.show()
    #sys.exit(app.exec())
    app.exec()

if __name__ == "__main__":
    qMain()
