# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QVBoxLayout, QWidget)

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
        self.formLayout_2 = QFormLayout(self.tab_systemOverview)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.verticalSpacer_13 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout_2.setItem(0, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_13)

        self.progressBar = QProgressBar(self.tab_systemOverview)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(0, 20))
        self.progressBar.setValue(79)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.progressBar)

        self.label_13 = QLabel(self.tab_systemOverview)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_13)

        self.verticalSpacer_6 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout_2.setItem(2, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_6)

        self.progressBar_2 = QProgressBar(self.tab_systemOverview)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setMinimumSize(QSize(0, 20))
        self.progressBar_2.setValue(56)

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.progressBar_2)

        self.label_28 = QLabel(self.tab_systemOverview)
        self.label_28.setObjectName(u"label_28")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_28)

        self.verticalSpacer_29 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout_2.setItem(4, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_29)

        self.progressBar_9 = QProgressBar(self.tab_systemOverview)
        self.progressBar_9.setObjectName(u"progressBar_9")
        self.progressBar_9.setMinimumSize(QSize(0, 20))
        self.progressBar_9.setValue(5)

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.progressBar_9)

        self.label_29 = QLabel(self.tab_systemOverview)
        self.label_29.setObjectName(u"label_29")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label_29)

        self.verticalSpacer_28 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.formLayout_2.setItem(6, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_28)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, -1, 6, 6)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_6)

        self.spinBox = QSpinBox(self.tab_systemOverview)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMaximum(16)
        self.spinBox.setValue(6)

        self.horizontalLayout_13.addWidget(self.spinBox)


        self.formLayout_2.setLayout(7, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_13)

        self.label_32 = QLabel(self.tab_systemOverview)
        self.label_32.setObjectName(u"label_32")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label_32)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout_2.setItem(8, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_11)

        self.tabWidget.addTab(self.tab_systemOverview, "")
        self.tab_rpiStatus = QWidget()
        self.tab_rpiStatus.setObjectName(u"tab_rpiStatus")
        self.label_2 = QLabel(self.tab_rpiStatus)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 20, 81, 16))
        self.label_isConnected_rpi = QLabel(self.tab_rpiStatus)
        self.label_isConnected_rpi.setObjectName(u"label_isConnected_rpi")
        self.label_isConnected_rpi.setGeometry(QRect(100, 20, 131, 16))
        self.label_5 = QLabel(self.tab_rpiStatus)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 40, 81, 16))
        self.label_6 = QLabel(self.tab_rpiStatus)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 60, 81, 16))
        self.pushButton_connect_rpi = QPushButton(self.tab_rpiStatus)
        self.pushButton_connect_rpi.setObjectName(u"pushButton_connect_rpi")
        self.pushButton_connect_rpi.setEnabled(True)
        self.pushButton_connect_rpi.setGeometry(QRect(180, 60, 80, 18))
        self.lineEdit_port_rpi = QLineEdit(self.tab_rpiStatus)
        self.lineEdit_port_rpi.setObjectName(u"lineEdit_port_rpi")
        self.lineEdit_port_rpi.setGeometry(QRect(100, 60, 71, 20))
        self.lineEdit_ipAddress_rpi = QLineEdit(self.tab_rpiStatus)
        self.lineEdit_ipAddress_rpi.setObjectName(u"lineEdit_ipAddress_rpi")
        self.lineEdit_ipAddress_rpi.setGeometry(QRect(100, 40, 113, 20))
        self.tabWidget.addTab(self.tab_rpiStatus, "")
        self.tab_appStatus = QWidget()
        self.tab_appStatus.setObjectName(u"tab_appStatus")
        self.formLayout = QFormLayout(self.tab_appStatus)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.tab_appStatus)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_isConnected_app = QLabel(self.tab_appStatus)
        self.label_isConnected_app.setObjectName(u"label_isConnected_app")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_isConnected_app)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.formLayout.setItem(3, QFormLayout.ItemRole.LabelRole, self.verticalSpacer)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.formLayout.setItem(3, QFormLayout.ItemRole.FieldRole, self.verticalSpacer_2)

        self.label_3 = QLabel(self.tab_appStatus)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.lineEdit_ipAddress_app = QLineEdit(self.tab_appStatus)
        self.lineEdit_ipAddress_app.setObjectName(u"lineEdit_ipAddress_app")
        self.lineEdit_ipAddress_app.setMaximumSize(QSize(140, 16777215))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_ipAddress_app)

        self.label_4 = QLabel(self.tab_appStatus)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_port_app = QLineEdit(self.tab_appStatus)
        self.lineEdit_port_app.setObjectName(u"lineEdit_port_app")
        self.lineEdit_port_app.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout.addWidget(self.lineEdit_port_app)

        self.pushButton_connect_app = QPushButton(self.tab_appStatus)
        self.pushButton_connect_app.setObjectName(u"pushButton_connect_app")
        self.pushButton_connect_app.setEnabled(False)
        self.pushButton_connect_app.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_connect_app)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.tabWidget.addTab(self.tab_appStatus, "")
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
        self.scrollArea_rpi.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 306, 402))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer_4 = QSpacerItem(20, 383, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_4)

        self.scrollArea_rpi.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_rpi.addWidget(self.scrollArea_rpi)

        self.lineEdit_rpi = QLineEdit(self.tab_netChat)
        self.lineEdit_rpi.setObjectName(u"lineEdit_rpi")

        self.verticalLayout_rpi.addWidget(self.lineEdit_rpi)


        self.horizontalLayout_3.addLayout(self.verticalLayout_rpi)

        self.verticalLayout_app = QVBoxLayout()
        self.verticalLayout_app.setObjectName(u"verticalLayout_app")
        self.label_app = QLabel(self.tab_netChat)
        self.label_app.setObjectName(u"label_app")

        self.verticalLayout_app.addWidget(self.label_app)

        self.scrollArea_app = QScrollArea(self.tab_netChat)
        self.scrollArea_app.setObjectName(u"scrollArea_app")
        self.scrollArea_app.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 306, 402))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.scrollArea_app.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_app.addWidget(self.scrollArea_app)

        self.lineEdit_app = QLineEdit(self.tab_netChat)
        self.lineEdit_app.setObjectName(u"lineEdit_app")

        self.verticalLayout_app.addWidget(self.lineEdit_app)


        self.horizontalLayout_3.addLayout(self.verticalLayout_app)

        self.tabWidget.addTab(self.tab_netChat, "")
        self.tab_appDebug = QWidget()
        self.tab_appDebug.setObjectName(u"tab_appDebug")
        self.verticalLayout = QVBoxLayout(self.tab_appDebug)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.tab_appDebug)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 622, 446))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_5 = QSpacerItem(20, 431, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_5)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab_appDebug, "")
        self.tab_settings = QWidget()
        self.tab_settings.setObjectName(u"tab_settings")
        self.gridLayout_2 = QGridLayout(self.tab_settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_sendAsPlainText = QCheckBox(self.tab_settings)
        self.checkBox_sendAsPlainText.setObjectName(u"checkBox_sendAsPlainText")

        self.gridLayout_2.addWidget(self.checkBox_sendAsPlainText, 0, 0, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_7, 1, 0, 1, 1)

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

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Phone Battery", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"TurtleBot Battery", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Bed Scan Progress", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Number of Bed Scan readings to take", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_systemOverview), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Connection Status", None))
        self.label_isConnected_rpi.setText(QCoreApplication.translate("MainWindow", u"disconnected (test)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"IP Address", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.pushButton_connect_rpi.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.lineEdit_port_rpi.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lineEdit_ipAddress_rpi.setText(QCoreApplication.translate("MainWindow", u"0.0.0.0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_rpiStatus), QCoreApplication.translate("MainWindow", u"Raspberry Pi Status", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Connection Status", None))
        self.label_isConnected_app.setText(QCoreApplication.translate("MainWindow", u"disconnected", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"IP Address", None))
        self.lineEdit_ipAddress_app.setText(QCoreApplication.translate("MainWindow", u"0.0.0.0", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.lineEdit_port_app.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.pushButton_connect_app.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_appStatus), QCoreApplication.translate("MainWindow", u"Phone App Status", None))
        self.label_rpi.setText(QCoreApplication.translate("MainWindow", u"Raspberry Pi", None))
        self.label_app.setText(QCoreApplication.translate("MainWindow", u"Phone App", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_netChat), QCoreApplication.translate("MainWindow", u"Network Debug", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_appDebug), QCoreApplication.translate("MainWindow", u"App Debug", None))
        self.checkBox_sendAsPlainText.setText(QCoreApplication.translate("MainWindow", u"Send messages to devices as plain text", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_settings), QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

