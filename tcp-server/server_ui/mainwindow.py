# This Python file uses the following encoding: utf-8
import sys
import struct

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PySide6.QtCore import QObject, QThread, Signal, Slot#, pyqtSignal
#from PySide6 import QtUiTools

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from server_ui.ui_form import Ui_MainWindow
from server_ui.QueueWatcher import QueueWatcher
from packet import construct_packet
from QueueEvent import *

def clickTest():
    print("click!")

def returnTest():
    print("tap!")

def appDebug(msg):
    print(f'Debug log {msg}')
    ui = Ui_MainWindow()
    
    #ui.scrollAreaWidgetContents_appDebug
    
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
    
    addToChatLog(ui, msg, src, isPi = False)
    #packet = f'{src}{des}{cat}{length}{msg}{end}'
    packet = bytes(f'{msg}\r\n', 'utf-8')
    
    if ui.checkBox_sendAsPlainText.isChecked() == False:
        packet = construct_packet(src, des, cat, msg)
    
    print(f'ui: sending {packet}')
    return packet

def addToChatLog(ui, message, src, isPi = False):
    # from https://stackoverflow.com/questions/22255994/pyqt-adding-widgets-to-scrollarea-during-the-runtime
    label = QLabel(f'{src}: {message.rstrip()}')
    label.setStyleSheet("background-color: darkgreen")
    if src == 'SPC':
        label.setStyleSheet("background-color: darkblue")
        
    widget = ui.scrollAreaWidgetContents_2
    layout = widget.layout()
    layout.insertWidget(layout.count()-1, label)
    
class MainWindow(QMainWindow):
    def __init__(self, server, qMain, qThread, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = server
        self.qMain = qMain
        self.qThread = qThread
        
        # set up a qThread to watch the queues
        """
        self.thread = QThread()
        self.QueueWatcher = QueueWatcher()
        self.QueueWatcher.setQueue(self.qMain)
        self.QueueWatcher.moveToThread(self.thread)
        self.thread.start()
        """
        self.qwThread = QueueWatcher()
        self.qwThread.setQueue(self.qMain)
        self.qwThread.start()
        
        # connect QueueWatcher signals
        #self.qwThread.newNetMessage.connect()
        
        # load widgets from UI file so we can manipulate them in the
        # program
        #loader = QtUiTools.QUiLoader()
        #ui = loader.load('form.ui', parent)
        
        # get the lineEdit widget for the app messenger
        #self.phoneAppLineEdit = self.ui.lineEdit_app
        self.connectWidgets()
    
    @Slot(str)
    def recieveMessageApp(self, arg):
        print(f'slot mechanism activated with {arg}')
        addToChatLog(self.ui, arg, 'APP')
        
    def connectWidgets(self):
        self.ui.lineEdit_app.returnPressed.connect(self.sendMessageApp)
        self.ui.lineEdit_rpi.returnPressed.connect(self.sendMessageRPi)
        self.ui.pushButton_connect_rpi.clicked.connect(clickTest)
        
        # Queue Watcher signals
        self.qwThread.newNetMessage.connect(self.recieveMessageApp)
        self.qwThread.serverEND.connect(self.close_server)

    # from: https://www.w3resource.com/python-exercises/pyqt/python-pyqt-connecting-signals-to-slots-exercise-11.php
    def closeEvent(self, event):
        # Ask for confirmation before closing
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to close the application?", QMessageBox.Yes | QMessageBox.No)

        if confirmation == QMessageBox.Yes:
            # end the queue watcher thread with a server end queue event
            self.qMain.put(QueueEvent(SERVER_END, ''))
            
            event.accept()  # Close the app
        else:
            event.ignore()  # Don't close the app
        
    @Slot()
    def close_server(self):
        QApplication.quit()

    def sendMessageApp(self):
        # send a message to the phone app
        packet = sendMessage(self.ui, False)
        self.server.appSocket.sendall(packet)
        
    def sendMessageRPi(self):
        # send a message to the turtlebot
        packet = sendMessage(self.ui, True)
        self.server.botSocket.sendall(packet)

def qMain(server, qMain, qThread):
    app = QApplication(sys.argv)
    widget = MainWindow(server, qMain, qThread)
    widget.show()
    #sys.exit(app.exec())
    app.exec()

if __name__ == "__main__":
    qMain()
