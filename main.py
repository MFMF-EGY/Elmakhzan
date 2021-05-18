from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QFileDialog, QMessageBox, QAction
from PyQt5 import QtCore
import sys
import json
import multiprocessing

BUTTON_WIDTH = 64
APP_NAME = "Elmakhzan"
EXTENSION = ".json"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        newfileButton = QPushButton("ملف جديد")
        saveButton = QPushButton("حفظ")
        openButton = QPushButton("افتح")
        self.tableWidget = Grid(5, 5)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        newfileButton.setMaximumWidth(BUTTON_WIDTH)
        newfileButton.clicked.connect(self.newfile)
        saveButton.setMaximumWidth(BUTTON_WIDTH)
        saveButton.clicked.connect(self.savefile)
        openButton.setMaximumWidth(BUTTON_WIDTH)
        openButton.clicked.connect(self.openfile)

        vbox.addLayout(hbox)
        vbox.addWidget(self.tableWidget)
        hbox.addWidget(newfileButton)
        hbox.addWidget(openButton)
        hbox.addWidget(saveButton)
        self.setLayout(vbox)
        self.setWindowTitle(APP_NAME + " - ملف جديد.json")
        self.resize(800, 600)
        self.filepath = ""
        self.isFileSaved = True
        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.quit = QAction("Quit")
        self.quit.triggered.connect(self.closewindow)
        self.show()

    def newfile(self):
        newprocess = multiprocessing.Process(target=main, args=(sys.argv,))
        newprocess.start()

    def savefile(self):
        if self.filepath == "":
            FileDirectory = QFileDialog.getSaveFileName(self, "Save File", "ملف جديد"+EXTENSION,APP_NAME+f" Files (*{EXTENSION})")
        else:
            FileDirectory = [self.filepath]
        if FileDirectory[0] == "": return 0
        Table = {
            "Dimensions": [self.tableWidget.columnCount(), self.tableWidget.rowCount()],
            "Column_Widths": [],
            "Column_Names": [],
            "Data": []
        }
        for ColNum in range(self.tableWidget.columnCount()):
            Table["Column_Widths"].append(self.tableWidget.columnWidth(ColNum))
            Table["Column_Names"].append(self.tableWidget.horizontalHeaderItem(ColNum).text())
            for RawNum in range(self.tableWidget.rowCount()):
                Item = self.tableWidget.item(ColNum, RawNum)
                if Item != None:
                    Table["Data"].append(Item.text())
                else:
                    Table["Data"].append("")
        self.filepath = FileDirectory[0]
        with open(FileDirectory[0], "w") as file:
            json.dump(Table, file)
        self.isFileSaved = True

    def loadfile(self, arg):
        Table = json.load(open(arg[1], "r"))
        for ColNum in range(Table["Dimensions"][0]):
            for RawNum in range(Table["Dimensions"][1]):
                item = QTableWidgetItem(Table["Data"][ColNum * Table["Dimensions"][1] + RawNum])
                self.tableWidget.setItem(ColNum, RawNum, item)
        self.filepath = arg[1]
        self.show()
        self.setWindowTitle(f"{APP_NAME} - " + self.filepath.split("/")[-1])

    def openfile(self):
        FileDirectory = QFileDialog.getOpenFileName(self, 'Open File',"" , APP_NAME+f" Files (*{EXTENSION})")
        if not FileDirectory[0]: return 0
        if self.filepath == "":
            self.loadfile([0, FileDirectory[0]])
            return 0
        if FileDirectory[0] != self.filepath:
            newprocess = multiprocessing.Process(target=main, args=(sys.argv + [FileDirectory[0]],))
            newprocess.start()

    def closewindow(self):
        if not self.isFileSaved:
            save = QMessageBox.question(self, "حفظ الملف", "ستضيع المعلوات إن لم يتم حفظ الملف\n هل تريد حفظ الملف؟",
                                        QMessageBox.Yes | QMessageBox.No)
            if save == QMessageBox.Yes: self.savefile()


class Grid(QTableWidget):
    def __init__(self, rows, columns):
        super(Grid, self).__init__()
        self.setRowCount(rows)
        self.setColumnCount(columns)
        self.doubleClicked.connect(self.editdetection)
        columns = ["اسم المنتج", "عدد الكراتين", "العدد لكل كرتونه", "العدد الكلي", "المقاس"]
        self.setHorizontalHeaderLabels(columns)

    def editdetection(self): self.parent().isFileSaved = 0


def main(arg):
    app = QApplication(sys.argv)
    MainWin = MainWindow()
    if len(arg) > 1:
        MainWin.loadfile(arg)
    sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)
