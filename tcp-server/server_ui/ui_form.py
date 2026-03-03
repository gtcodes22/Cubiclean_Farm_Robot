# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(652, 535)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(640, 480))
        self.tab_systemOverview = QWidget()
        self.tab_systemOverview.setObjectName(u"tab_systemOverview")
        self.gridLayout = QGridLayout(self.tab_systemOverview)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_28 = QLabel(self.tab_systemOverview)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_7.addWidget(self.label_28)

        self.progressBar_2 = QProgressBar(self.tab_systemOverview)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setMinimumSize(QSize(80, 20))
        self.progressBar_2.setValue(56)

        self.horizontalLayout_7.addWidget(self.progressBar_2)


        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 0, 1, 1)

        self.label_10 = QLabel(self.tab_systemOverview)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 1, 1, 1, 1)

        self.label_9 = QLabel(self.tab_systemOverview)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 1, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_30 = QLabel(self.tab_systemOverview)
        self.label_30.setObjectName(u"label_30")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.label_30)

        self.progressBar_10 = QProgressBar(self.tab_systemOverview)
        self.progressBar_10.setObjectName(u"progressBar_10")
        self.progressBar_10.setMinimumSize(QSize(0, 20))
        self.progressBar_10.setValue(5)

        self.horizontalLayout_9.addWidget(self.progressBar_10)


        self.gridLayout.addLayout(self.horizontalLayout_9, 4, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_29 = QLabel(self.tab_systemOverview)
        self.label_29.setObjectName(u"label_29")

        self.horizontalLayout_8.addWidget(self.label_29)

        self.progressBar_9 = QProgressBar(self.tab_systemOverview)
        self.progressBar_9.setObjectName(u"progressBar_9")
        self.progressBar_9.setMinimumSize(QSize(0, 20))
        self.progressBar_9.setValue(5)

        self.horizontalLayout_8.addWidget(self.progressBar_9)


        self.gridLayout.addLayout(self.horizontalLayout_8, 3, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(202, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 0, 2, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_13 = QLabel(self.tab_systemOverview)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_5.addWidget(self.label_13)

        self.progressBar = QProgressBar(self.tab_systemOverview)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(0, 20))
        self.progressBar.setValue(79)

        self.horizontalLayout_5.addWidget(self.progressBar)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 5, 0, 1, 1)

        self.label = QLabel(self.tab_systemOverview)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font: 16pt \"Segoe UI\";")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.tab_systemOverview)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAutoFillBackground(False)
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font: 16pt \"Segoe UI\";")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.tabWidget.addTab(self.tab_systemOverview, "")
        self.tab_netChat = QWidget()
        self.tab_netChat.setObjectName(u"tab_netChat")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_netChat)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_rpi = QVBoxLayout()
        self.verticalLayout_rpi.setObjectName(u"verticalLayout_rpi")
        self.label_rpi = QLabel(self.tab_netChat)
        self.label_rpi.setObjectName(u"label_rpi")

        self.verticalLayout_rpi.addWidget(self.label_rpi)

        self.scrollArea_rpi = QScrollArea(self.tab_netChat)
        self.scrollArea_rpi.setObjectName(u"scrollArea_rpi")
        self.scrollArea_rpi.setEnabled(True)
        self.scrollArea_rpi.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 302, 378))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer_4 = QSpacerItem(20, 383, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_4)

        self.scrollArea_rpi.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_rpi.addWidget(self.scrollArea_rpi)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 0)
        self.label_BotConnectStatus = QLabel(self.tab_netChat)
        self.label_BotConnectStatus.setObjectName(u"label_BotConnectStatus")
        self.label_BotConnectStatus.setMinimumSize(QSize(0, 18))

        self.horizontalLayout_4.addWidget(self.label_BotConnectStatus)


        self.verticalLayout_rpi.addLayout(self.horizontalLayout_4)

        self.lineEdit_rpi = QLineEdit(self.tab_netChat)
        self.lineEdit_rpi.setObjectName(u"lineEdit_rpi")
        self.lineEdit_rpi.setEnabled(False)

        self.verticalLayout_rpi.addWidget(self.lineEdit_rpi)


        self.horizontalLayout_3.addLayout(self.verticalLayout_rpi)

        self.verticalLayout_app = QVBoxLayout()
        self.verticalLayout_app.setObjectName(u"verticalLayout_app")
        self.label_app = QLabel(self.tab_netChat)
        self.label_app.setObjectName(u"label_app")

        self.verticalLayout_app.addWidget(self.label_app)

        self.scrollArea_app = QScrollArea(self.tab_netChat)
        self.scrollArea_app.setObjectName(u"scrollArea_app")
        self.scrollArea_app.setEnabled(True)
        self.scrollArea_app.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 310, 376))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.scrollArea_app.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_app.addWidget(self.scrollArea_app)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout_6.setContentsMargins(-1, -1, -1, 0)
        self.label_AppConnectStatus = QLabel(self.tab_netChat)
        self.label_AppConnectStatus.setObjectName(u"label_AppConnectStatus")

        self.horizontalLayout_6.addWidget(self.label_AppConnectStatus)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.pushButton_app_sendImg = QPushButton(self.tab_netChat)
        self.pushButton_app_sendImg.setObjectName(u"pushButton_app_sendImg")
        self.pushButton_app_sendImg.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.pushButton_app_sendImg)

        self.pushButton_app_sendDat = QPushButton(self.tab_netChat)
        self.pushButton_app_sendDat.setObjectName(u"pushButton_app_sendDat")
        self.pushButton_app_sendDat.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.pushButton_app_sendDat)


        self.verticalLayout_app.addLayout(self.horizontalLayout_6)

        self.lineEdit_app = QLineEdit(self.tab_netChat)
        self.lineEdit_app.setObjectName(u"lineEdit_app")
        self.lineEdit_app.setEnabled(False)

        self.verticalLayout_app.addWidget(self.lineEdit_app)


        self.horizontalLayout_3.addLayout(self.verticalLayout_app)

        self.tabWidget.addTab(self.tab_netChat, "")
        self.tab_appDebug = QWidget()
        self.tab_appDebug.setObjectName(u"tab_appDebug")
        self.verticalLayout = QVBoxLayout(self.tab_appDebug)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textEdit_SystemLog = QTextEdit(self.tab_appDebug)
        self.textEdit_SystemLog.setObjectName(u"textEdit_SystemLog")

        self.verticalLayout.addWidget(self.textEdit_SystemLog)

        self.tabWidget.addTab(self.tab_appDebug, "")
        self.tab_settings = QWidget()
        self.tab_settings.setObjectName(u"tab_settings")
        self.verticalLayout_2 = QVBoxLayout(self.tab_settings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox_sendAsPlainText = QCheckBox(self.tab_settings)
        self.checkBox_sendAsPlainText.setObjectName(u"checkBox_sendAsPlainText")

        self.verticalLayout_2.addWidget(self.checkBox_sendAsPlainText)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, -1, 6, 6)
        self.label_32 = QLabel(self.tab_settings)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_13.addWidget(self.label_32)

        self.spinBox_BedScanReadings = QSpinBox(self.tab_settings)
        self.spinBox_BedScanReadings.setObjectName(u"spinBox_BedScanReadings")
        self.spinBox_BedScanReadings.setMaximumSize(QSize(30, 16777215))
        self.spinBox_BedScanReadings.setMaximum(16)
        self.spinBox_BedScanReadings.setValue(6)

        self.horizontalLayout_13.addWidget(self.spinBox_BedScanReadings)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_13)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_7)

        self.tabWidget.addTab(self.tab_settings, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 652, 17))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cubiclean Robot Server 0.2.2", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Battery", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Current Bed Progress", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Total Progress", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Battery", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Turtlebot", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Data Viewer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_systemOverview), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.label_rpi.setText(QCoreApplication.translate("MainWindow", u"Raspberry Pi", None))
        self.label_BotConnectStatus.setText(QCoreApplication.translate("MainWindow", u"\u274c Device Disconnected", None))
        self.label_app.setText(QCoreApplication.translate("MainWindow", u"Phone App", None))
        self.label_AppConnectStatus.setText(QCoreApplication.translate("MainWindow", u"\u274c Device Disconnected", None))
        self.pushButton_app_sendImg.setText(QCoreApplication.translate("MainWindow", u"Send Image...", None))
        self.pushButton_app_sendDat.setText(QCoreApplication.translate("MainWindow", u"Send Data...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_netChat), QCoreApplication.translate("MainWindow", u"Network Debug", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_appDebug), QCoreApplication.translate("MainWindow", u"System Log", None))
        self.checkBox_sendAsPlainText.setText(QCoreApplication.translate("MainWindow", u"Send messages to devices as plain text", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Number of Bed Scan readings to take", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_settings), QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

