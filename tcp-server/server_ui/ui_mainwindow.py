# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(30, 20, 411, 311))
        self.tab_main = QWidget()
        self.tab_main.setObjectName(u"tab_main")
        self.tabWidget.addTab(self.tab_main, "")
        self.tab_rpi = QWidget()
        self.tab_rpi.setObjectName(u"tab_rpi")
        self.label_2 = QLabel(self.tab_rpi)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 20, 81, 16))
        self.label_isConnected_rpi = QLabel(self.tab_rpi)
        self.label_isConnected_rpi.setObjectName(u"label_isConnected_rpi")
        self.label_isConnected_rpi.setGeometry(QRect(100, 20, 131, 16))
        self.label_5 = QLabel(self.tab_rpi)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 40, 81, 16))
        self.label_6 = QLabel(self.tab_rpi)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 60, 81, 16))
        self.pushButton_connect_rpi = QPushButton(self.tab_rpi)
        self.pushButton_connect_rpi.setObjectName(u"pushButton_connect_rpi")
        self.pushButton_connect_rpi.setEnabled(False)
        self.pushButton_connect_rpi.setGeometry(QRect(180, 60, 80, 18))
        self.lineEdit_port_rpi = QLineEdit(self.tab_rpi)
        self.lineEdit_port_rpi.setObjectName(u"lineEdit_port_rpi")
        self.lineEdit_port_rpi.setGeometry(QRect(100, 60, 71, 20))
        self.lineEdit_ipAddress_rpi = QLineEdit(self.tab_rpi)
        self.lineEdit_ipAddress_rpi.setObjectName(u"lineEdit_ipAddress_rpi")
        self.lineEdit_ipAddress_rpi.setGeometry(QRect(100, 40, 113, 20))
        self.tabWidget.addTab(self.tab_rpi, "")
        self.tab_app = QWidget()
        self.tab_app.setObjectName(u"tab_app")
        self.label = QLabel(self.tab_app)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 81, 16))
        self.label_isConnected_app = QLabel(self.tab_app)
        self.label_isConnected_app.setObjectName(u"label_isConnected_app")
        self.label_isConnected_app.setGeometry(QRect(100, 20, 131, 16))
        self.label_3 = QLabel(self.tab_app)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 40, 81, 16))
        self.label_4 = QLabel(self.tab_app)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 60, 81, 16))
        self.lineEdit_port_app = QLineEdit(self.tab_app)
        self.lineEdit_port_app.setObjectName(u"lineEdit_port_app")
        self.lineEdit_port_app.setGeometry(QRect(100, 60, 71, 20))
        self.pushButton_connect_app = QPushButton(self.tab_app)
        self.pushButton_connect_app.setObjectName(u"pushButton_connect_app")
        self.pushButton_connect_app.setEnabled(False)
        self.pushButton_connect_app.setGeometry(QRect(180, 60, 80, 18))
        self.lineEdit_ipAddress_app = QLineEdit(self.tab_app)
        self.lineEdit_ipAddress_app.setObjectName(u"lineEdit_ipAddress_app")
        self.lineEdit_ipAddress_app.setGeometry(QRect(100, 40, 113, 20))
        self.tabWidget.addTab(self.tab_app, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayoutWidget = QWidget(self.tab)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 16, 371, 261))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_rpi = QVBoxLayout()
        self.verticalLayout_rpi.setObjectName(u"verticalLayout_rpi")
        self.label_rpi = QLabel(self.horizontalLayoutWidget)
        self.label_rpi.setObjectName(u"label_rpi")

        self.verticalLayout_rpi.addWidget(self.label_rpi)

        self.scrollArea_rpi = QScrollArea(self.horizontalLayoutWidget)
        self.scrollArea_rpi.setObjectName(u"scrollArea_rpi")
        self.scrollArea_rpi.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 179, 213))
        self.scrollArea_rpi.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_rpi.addWidget(self.scrollArea_rpi)

        self.lineEdit_rpi = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_rpi.setObjectName(u"lineEdit_rpi")

        self.verticalLayout_rpi.addWidget(self.lineEdit_rpi)


        self.horizontalLayout.addLayout(self.verticalLayout_rpi)

        self.verticalLayout_app = QVBoxLayout()
        self.verticalLayout_app.setObjectName(u"verticalLayout_app")
        self.label_app = QLabel(self.horizontalLayoutWidget)
        self.label_app.setObjectName(u"label_app")

        self.verticalLayout_app.addWidget(self.label_app)

        self.scrollArea_app = QScrollArea(self.horizontalLayoutWidget)
        self.scrollArea_app.setObjectName(u"scrollArea_app")
        self.scrollArea_app.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 178, 213))
        self.scrollArea_app.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_app.addWidget(self.scrollArea_app)

        self.lineEdit_app = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_app.setObjectName(u"lineEdit_app")

        self.verticalLayout_app.addWidget(self.lineEdit_app)


        self.horizontalLayout.addLayout(self.verticalLayout_app)

        self.tabWidget.addTab(self.tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 17))
        self.menuTest = QMenu(self.menubar)
        self.menuTest.setObjectName(u"menuTest")
        self.menutest2 = QMenu(self.menubar)
        self.menutest2.setObjectName(u"menutest2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuTest.menuAction())
        self.menubar.addAction(self.menutest2.menuAction())

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_main), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Connection Status", None))
        self.label_isConnected_rpi.setText(QCoreApplication.translate("MainWindow", u"disconnected", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"IP Address", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.pushButton_connect_rpi.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.lineEdit_port_rpi.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ipAddress_rpi.setText(QCoreApplication.translate("MainWindow", u"0.0.0.0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_rpi), QCoreApplication.translate("MainWindow", u"Raspberry Pi Status", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Connection Status", None))
        self.label_isConnected_app.setText(QCoreApplication.translate("MainWindow", u"disconnected", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"IP Address", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.lineEdit_port_app.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.pushButton_connect_app.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.lineEdit_ipAddress_app.setText(QCoreApplication.translate("MainWindow", u"0.0.0.0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_app), QCoreApplication.translate("MainWindow", u"Phone App Status", None))
        self.label_rpi.setText(QCoreApplication.translate("MainWindow", u"Raspberry Pi", None))
        self.label_app.setText(QCoreApplication.translate("MainWindow", u"Phone App", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Network Debug", None))
        self.menuTest.setTitle(QCoreApplication.translate("MainWindow", u"Test", None))
        self.menutest2.setTitle(QCoreApplication.translate("MainWindow", u"test2", None))
    # retranslateUi

