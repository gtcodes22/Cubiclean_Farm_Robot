## from: https://github.com/Yash12007/Splash_Screen/blob/main/SplashScreen.py
## modified by Jade Cawley
# python library imports
import sys

# external python library imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from PySide6.QtCore import *

# program library imports
from server.QueueEvent import *
from server.pyqt.ui_SplashScreen import Ui_MainWindow as ui_splashscreen

UIPath = r".\SplashScreen.ui"

class SplashScreen(QMainWindow):
    def __init__(self, parent, loaderThread):
        super().__init__()
        self.parent = parent
        self.loaderThread = loaderThread
        
        self.ui = ui_splashscreen()
        self.ui.setupUi(self)
        
        '''
        self.progress = self.findChild(QProgressBar, 'progressBar')
        self.quit = self.findChild(QPushButton, 'Quit')
        self.status = self.findChild(QLabel, 'status')
        '''
        self.progress = self.ui.progressBar
        self.Quit = self.ui.Quit
        self.status = self.ui.status
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        self.connectWidgets()

        self.loading_steps = ["Initializing TCP Server", "Initializing Dash Web App Server", "Almost there...", "Finishing up..."]
        self.current_step = 0
        self.ui.progressBar.setValue(0)
        #self.loading_timer = QTimer(self)
        #self.loading_timer.timeout.connect(self.update_loading)
        self.loaderThread.nextLoadStep.connect(self.update_loading)
        #self.loading_timer.start(2000)
        
        # start loader worker
        self.loaderThread.start()
        
        self.show()

    def connectWidgets(self):
        self.Quit.clicked.connect(self.close)
        self.Quit.clicked.connect(self.close_exit)

    def close(self):
        super(SplashScreen, self).close()

    def close_exit(self):
        self.parent.qMain.put(QueueEvent(SERVER_END, ''))

    def update_loading(self, valueUpdate = 25):
        if self.current_step < len(self.loading_steps):
            self.progress.setValue(self.progress.value() + valueUpdate)
            self.status.setText(self.loading_steps[self.current_step])
            self.current_step += 1
        else:
            #self.loading_timer.disconnect()
            self.close()
            self.parent.show()
            self.parent.raise_()
            #uic.loadUi("C:\\Users\\yash3\\OneDrive\\Desktop\\Yash12007\\Projects\\WEBVIEW\\Nexus_OS\\1280x720.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = SplashScreen()
    sys.exit(app.exec())
