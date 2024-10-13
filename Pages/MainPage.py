from main import *


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0,0,781,574)
        self.itemsPageButton = QPushButton("البضاعة",self)
        self.itemsPageButton.setGeometry(640,30,121,121)
        self.dailySalesButton = QPushButton("بيع يومي",self)
        self.dailySalesButton.setGeometry(520,250,241,121)
        self.saleBillButton = QPushButton("فاتورة بيع",self)
        self.saleBillButton.setGeometry(640,380,121,121)

    def openPage(self,tabWidget,page,title):
        tabWidget.addTab(page,title)
        tabWidget.setCurrentIndex(tabWidget.indexOf(page))



