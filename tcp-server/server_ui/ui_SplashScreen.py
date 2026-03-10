# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SplashScreen.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QMainWindow,
    QProgressBar, QPushButton, QSizePolicy, QWidget)
import server_ui.rc_images

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(814, 533)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(-1, -1, 821, 601))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet(u"QFrame{\n"
"	background:white;\n"
"	color:white;\n"
"}")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.progressBar = QProgressBar(self.frame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(7, 500, 801, 23))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"	background-color: #00A86B;\n"
"	color: white;\n"
"	border-style: outset;\n"
"	border-width: 1px;\n"
"	border-color: blue;\n"
"	border-radius: 10%;\n"
"	text-align: center; \n"
"}\n"
"QProgressBar::chunk {\n"
"	background-color: #af00ff;\n"
"	border-radius:10%;\n"
"}")
        self.progressBar.setValue(55)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 461, 191, 20))
        self.label.setStyleSheet(u"QLabel{\n"
"	color: rgb(0, 0, 0);\n"
"	font-size:16px;\n"
"	font-family:calibri;\n"
"}")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 480, 241, 16))
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.status = QLabel(self.frame)
        self.status.setObjectName(u"status")
        self.status.setGeometry(QRect(680, 480, 121, 16))
        self.status.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.Quit = QPushButton(self.frame)
        self.Quit.setObjectName(u"Quit")
        self.Quit.setGeometry(QRect(782, 0, 31, 28))
        self.Quit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.Quit.setStyleSheet(u"QPushButton{\n"
"	font: 14pt \"Segoe UI\";\n"
"	background:white;\n"
"	border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 10px;\n"
"    border-color: red;\n"
"	color:white;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: rgb(224, 0, 0);\n"
"    border-style: inset;\n"
"}")
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(310, 260, 201, 16))
        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(0, 0, 811, 481))
        self.label_5.setFrameShape(QFrame.Shape.NoFrame)
        self.label_5.setPixmap(QPixmap(u":/splash.png"))
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 120, 201, 31))
        self.label_3.setStyleSheet(u"QLabel{\n"
"	color: rgb(0, 0, 0);\n"
"	font-size:28px;\n"
"	font-family:calibri;\n"
"}")
        self.label_5.raise_()
        self.progressBar.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.status.raise_()
        self.Quit.raise_()
        self.label_4.raise_()
        self.label_3.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.Quit.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Developed by Jade Cawley", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u00a9 2026 Jade Cawley. All Rights Reserved.", None))
        self.status.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.Quit.setText(QCoreApplication.translate("MainWindow", u"\u274c", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"An operating system for everyone.", None))
        self.label_5.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Version: 0.3.1", None))
    # retranslateUi

