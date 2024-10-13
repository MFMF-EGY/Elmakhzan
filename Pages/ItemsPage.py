from main import *

class itemsPage(QWidget):
    def __init__(self):
        super().__init__()
        # mysql_cursor.execute("select * from items")
        #itemsData = mysql_cursor.fetchall()
        hbox = QHBoxLayout()
        self.itemsTableWidget = QTableWidget()
        self.itemsTableWidget.setRowCount(1)
        self.itemsTableWidget.setColumnCount(4)
        columns = ["اسم المنتج", "الكمية", "الوحدة",]
        self.itemsTableWidget.setHorizontalHeaderLabels(columns)

        buttonsLayout = QVBoxLayout()
        self.addItemButton = QPushButton("اضافة")
        self.addItemButton.setMaximumHeight(40)
        self.deleteItemButton = QPushButton("حذف")
        self.deleteItemButton.setMaximumHeight(40)

        hbox.addWidget(self.itemsTableWidget)
        hbox.addLayout(buttonsLayout)
        hbox.setContentsMargins(0,0,0,0)
        buttonsLayout.addWidget(self.addItemButton)
        buttonsLayout.addWidget(self.deleteItemButton)
        self.setLayout(hbox)
