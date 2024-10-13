from PyQt5.QtWidgets import (QWidget, QApplication, QTabWidget, QLabel, QPushButton,
                            QVBoxLayout, QMenuBar, QAction)

class MainWidget(QWidget):
    def __init__(self, textLabel, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        layout     = QVBoxLayout(self)
        self.label = QLabel(textLabel, self)
        self.btn   = QPushButton('Next', self)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        bar = QMenuBar(self)
        menu = bar.addMenu('File')
        action = QAction('Close activ tab', self)
        menu.addAction(action)
        action.triggered.connect(self.closeActivTab)

        self.tabwdg = QTabWidget()
        self.tabwdg.setTabsClosable(True)

        self.tabWidget = MainWidget('this is the first page')
        self.tabwdg.addTab(self.tabWidget, 'first')
        self.tabWidget.btn.clicked.connect(self.numTab)
        self.tabWidget = MainWidget('this is the second page')
        self.tabwdg.addTab(self.tabWidget, 'second')
        self.tabWidget.btn.clicked.connect(self.numTab)
        self.tabWidget = MainWidget('this is the third page')
        self.tabwdg.addTab(self.tabWidget, 'third')
        self.tabWidget.btn.clicked.connect(self.numTab)
        self.tabWidget = MainWidget('this is the fourth page')
        self.tabwdg.addTab(self.tabWidget, 'fourth')
        self.tabWidget.btn.clicked.connect(self.numTab)

        self.tabwdg.tabCloseRequested.connect(self.closeTab)

        box = QVBoxLayout()
        box.addWidget(bar)
        box.addWidget(self.tabwdg)
        self.setLayout(box)

    def numTab(self):
        nextTab = self.tabwdg.currentIndex()+1
        if nextTab == self.tabwdg.count():
            nextTab = 0
        self.tabwdg.setCurrentIndex(nextTab)
        self.tabwdg.setCurrentWidget(self.tabwdg.currentWidget())

    def closeActivTab(self):
        activ_tab_ind = self.tabwdg.currentIndex()
        self.closeTab(activ_tab_ind)

    def closeTab(self, ind):
        self.tabwdg.removeTab(ind)


if __name__ == '__main__':
    import sys
    app = QApplication([''])
    w = Window()
    w.resize(400, 300)
    w.show()
    sys.exit(app.exec_())