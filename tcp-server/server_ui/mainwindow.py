# This Python file uses the following encoding: utf-8
import sys
import struct

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QLabel
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot, QSize, QTimer#, pyqtSignal
from PySide6.QtGui import QPixmap, QIcon, QImage, QGuiApplication
#from PySide6 import QtUiTools

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from server_ui.ui_form import Ui_MainWindow
from server_ui.QueueWatcher import QueueWatcher
from server_ui.LoadWorker import LoadWorker
from server_ui.ui_SplashScreen import Ui_MainWindow as ui_splashscreen
from server_ui.SplashScreen import SplashScreen
from packet import construct_packet
from QueueEvent import *
import time
import socket

def clickTest():
    print("click!")

def returnTest():
    print("tap!")
    
def sendMessage(ui, qMain, isPi = False, message = ''):
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
    msg = message
    
    if isPi:
        if msg == '':
            msg = str(ui.lineEdit_rpi.text())
        ui.lineEdit_rpi.clear()
        qMain.put(QueueEvent(NET_RESPONSE, 'RPI', msg = msg))
    else:
        if msg == '':
            msg = str(ui.lineEdit_app.text())
        ui.lineEdit_app.clear()
        qMain.put(QueueEvent(NET_RESPONSE, 'APP', msg = msg))
        
    # get length of message and convert it into 4 bytes, big endian
    length = struct.pack('>i', len(msg))
    
    #addToChatLog(ui, msg, src, des)
    #packet = f'{src}{des}{cat}{length}{msg}{end}'
    packet = bytes(f'{msg}\r\n', 'utf-8')
    
    if ui.checkBox_sendAsPlainText.isChecked() == False:
        packet = construct_packet(src, des, cat, msg)
    
    
    print(f'ui: sending {packet}')
    return packet

def addToChatLog(ui, message, src, des, mType = 'MSG', lPixmap = None):
    print(f'adding {mType} of len:{len(message)} from {src} to {des} to chat log')
    # from https://stackoverflow.com/questions/22255994/pyqt-adding-widgets-to-scrollarea-during-the-runtime
    label = QLabel()
    if mType == 'IMG':
        label.setText(f'{src}: IMAGE')
        label.setPixmap(lPixmap)
    elif mType == 'MSG' and src == 'APP':
        label.setText(f'{src}: {message.rstrip()}')
        label.setStyleSheet("color: white;background-color: rgb(139, 195, 74);")
    elif mType == 'MSG' and src == 'RPI':
        label.setText(f'{src}: {message.rstrip()}')
        label.setStyleSheet("color: white;background-color: rgb(244, 67, 54);")
    elif mType == 'MSG' and src == 'SPC':
        label.setText(f'{src}: {message.rstrip()}')
        label.setStyleSheet("color: white;background-color: rgb(3, 169, 244);")
    
    widget = ui.scrollAreaWidgetContents_2
    if src == 'RPI' or des == 'RPI':
        widget = ui.scrollAreaWidgetContents
        
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
        self.pixmap = []
        
        # Window icon
        self.setWindowIcon(QIcon('cow.png'))
        self.ver = '0.2.2'
        # need to incorporate being able to change the ports in the interface
        self.port = 1991    
        self.broadcastPort = 1995
        self.broadcastIP = None
        
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
        
        # get broadcast server ip
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        allips = [ip[-1][0] for ip in interfaces]

        # only broadcast on local area network
        for ip in allips:
            if ip.split('.')[2] in ('0', '1'):
                self.broadcastIP = ip
        
        if self.broadcastIP:
            self.appDebug(f'broadcasting on {self.broadcastIP}')
            
            # broadcast server ip timer
            self.broadcast_timer = QTimer(self)
            self.broadcast_timer.timeout.connect(self.server_broadcast)
            self.broadcast_timer.start(2000)
        else:
            self.appDebug(f'w: could not get broadcast IP')
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.ping_for_update)
        #self.update_timer.start(5000)
        
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
    def recieveMessageApp(self, msg, src, des):
        addToChatLog(self.ui, msg, src, des)
        
    def connectWidgets(self):
        # Network Debug Chat page related signals
        self.ui.lineEdit_app.returnPressed.connect(self.sendMessageApp)
        self.ui.lineEdit_rpi.returnPressed.connect(self.sendMessageRPi)
        #self.ui.pushButton_connect_rpi.clicked.connect(clickTest)
        
        self.ui.pushButton_app_sendImg.clicked.connect(self.get_image)
        self.ui.pushButton_app_sendDat.clicked.connect(self.get_dat_file)
        
        # Queue Watcher signals
        self.qwThread.newNetMessage.connect(self.recieveMessageApp)
        self.qwThread.serverEND.connect(self.close_server)
        self.qwThread.deviceConnected.connect(self.device_connected)
        self.qwThread.deviceDisconnected.connect(self.device_disconnected)
        self.qwThread.logQueueEvent.connect(self.ui.textEdit_SystemLog.append)

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

    @Slot(bool)
    def device_connected(self, arg):
        self.ping_for_update()
        ui = self.ui
        if arg:
            ui.lineEdit_rpi.setEnabled(True)
            ui.label_BotConnectStatus.setText('✅ Device Connected') 
        else:
            ui.pushButton_app_sendImg.setEnabled(True)
            ui.pushButton_app_sendDat.setEnabled(True)
            ui.lineEdit_app.setEnabled(True)
            ui.label_AppConnectStatus.setText('✅ Device Connected')

    @Slot(bool)
    def device_disconnected(self, arg):
        self.ping_for_update()
        ui = self.ui
        if arg:
            ui.lineEdit_rpi.setEnabled(False)
            ui.label_BotConnectStatus.setText('❌ Device Disconnected') 
        else:
            ui.pushButton_app_sendImg.setEnabled(False)
            ui.pushButton_app_sendDat.setEnabled(False)
            ui.lineEdit_app.setEnabled(False)
            ui.label_AppConnectStatus.setText('❌ Device Disconnected')
        
    @Slot()
    def close_server(self):
        QApplication.quit()
        
    def sendMessageApp(self):
        # send a message to the phone app
        packet = sendMessage(self.ui, self.qMain, False)
        self.server.appSocket.sendall(packet)
        
    def sendMessageRPi(self):
        # send a message to the turtlebot
        packet = sendMessage(self.ui, self.qMain, True)
        self.server.botSocket.sendall(packet)
    
    def sendImage(self, img):
        with open(img, 'rb') as imgfile:
            content = imgfile.read()
            src = 'SPC'
            des = 'APP'
            packet = construct_packet(src, des, 'IMG', content)
            self.server.appSocket.sendall(packet)
            self.qMain.put(QueueEvent(NET_IMG, 'APP', data = 'Image File'))
        
    def get_image(self):
        # get image filename
        img = self.get_file(False)
        
        # create a pixmap of the image to add to the GUI
        pixmap = QPixmap(str(img))
        
        # resize it to be 128 pixels tall (no more than 256 pixels wide)
        pixmap = pixmap.scaled(QSize(256,128), aspectMode=Qt.KeepAspectRatio, mode = Qt.SmoothTransformation)
        
        # add pixmap to list of pixmaps
        self.pixmap.append(pixmap)
        
        # add image to chat log
        addToChatLog(self.ui, '', 'SPC', 'APP', mType = 'IMG', lPixmap = pixmap)
        
        # send image to app
        if self.ui.checkBox_sendAsPlainText.isChecked():
            # just send image filename as plain text
            self.server.appSocket.sendall(bytes(f'image: {img}\r\n', 'utf-8'))
        else:
            self.sendImage(img)
        
    def get_dat_file(self):
        # get data filename
        data = self.get_file(True)
        
        # add image representation of a data file to chat log (?)
        
    def get_file(self, isDat):
        """
        # set up dialog
        dialog = QFileDialog(self)
        
        # only allows selecting existing files
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        
        # set dialog file type filters
        dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        
        # set dialog view to list view
        dialog.setViewMode(QFileDialog.List)
        """
        
        caption = "Open Image..."
        filter = "Image Files (*.png *.jpg *.bmp)"
        
        if isDat:
            caption = "Open Data File..."
            filter = "All Files (*.*)"
        
        # open file open dialog
        fileName = QFileDialog.getOpenFileName(self, caption = caption, filter = filter)
        
        print(f'{fileName[0]}')
        return fileName[0]
    
    # adapted from Source - https://stackoverflow.com/a/64067297
    # Posted by Mario Camilleri, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-03-02, License - CC BY-SA 4.0
    def server_broadcast(self):
        msg = bytes(f'TCP Server {self.ver}', 'utf-8')
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((self.broadcastIP,0))
        sock.sendto(msg, ("255.255.255.255", self.broadcastPort))
        sock.close()
        
    def ping_for_update(self):
        # if the app is connected
        if self.server.appSocket:
            sendMessage(self.ui, self.qMain, message = '/BATTERY')
        
        # if the turtlebot is connected
        if self.server.botSocket:
            sendMessage(self.ui, self.qMain, True, message='/BATTERY')
            sendMessage(self.ui, self.qMain, True, message='/SPEEDCM')
            sendMessage(self.ui, self.qMain, True, message='/PROGRESS')

    def appDebug(self, msg):
        print(msg)
        self.ui.textEdit_SystemLog.append(msg)
        
def start_ui(server, serverThread, qMain, qThread):
    # start QApplication
    app = QApplication(sys.argv)
    
    # force light mode
    QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
        
    # set up worker thread to start TCP Server and Dartly HTTP server
    loaderThread = LoadWorker(qMain, server, serverThread)
    
    # main program widget
    widget = MainWindow(server, qMain, qThread)
    
    # splash screen widget
    splash = SplashScreen(widget, loaderThread)
    
    # show splash screen
    splash.show()
    splash.raise_()

    # start executing QApp
    app.exec()
    
    #sys.exit(app.exec())
    #app.exec()

if __name__ == "__main__":
    start_ui()
