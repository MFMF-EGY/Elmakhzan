import os

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import sys
import mysql.connector as mysql


APP_NAME = "Elmakhzan"
MYSQL_CONNECTION_SETTINGS = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "000600",
    "database" : "mysql",
    "status": "disconnected"
}

from ConfigWindow import ConfigWindow
from ConfigWindow import NewProjectWindow
from Pages.MainPage import MainPage
from Pages.ItemsPage import itemsPage
# mysql_connector = mysql.connect(
#     host=MYSQL_CONNECTION_SETTINGS["host"],
#     port=MYSQL_CONNECTION_SETTINGS["port"],
#     user=MYSQL_CONNECTION_SETTINGS["user"],
#     password=MYSQL_CONNECTION_SETTINGS["password"],
#     database=MYSQL_CONNECTION_SETTINGS["database"]
# )
# mysql_cursor = mysql_connector.cursor()
# mysql_cursor.execute("select * from db;")
# print(mysql_cursor.fetchall())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Widgets Designs/Mainpage.ui", self)

        # self.mainPage.itemsPageButton.clicked.connect(lambda : self.mainPage.openPage(self.tabWidget,self.itemsPage,"البضاعة"))



        # self.tabWidget.addTab(self.mainPage, "الصفحة الرئيسية")
        self.setWindowTitle(APP_NAME)
        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.quit = QAction("Quit")
        self.show()




def main(arg):
    app = QApplication(sys.argv)
    MainWin = MainWindow()
    # ConfigWin = ConfigWindow.ConfigWindow()
    # if len(arg) > 1:
    #    MainWin.loadfile(arg)
    sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)
