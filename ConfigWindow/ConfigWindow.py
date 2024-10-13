from main import *


class CustomItemWidget(QWidget):
    def __init__(self):
        super(CustomItemWidget,self).__init__()
        self.upperline = QLabel()
        self.lowerline = QLabel()

        self.lowerline.setStyleSheet("color: #ff5555;")

        vbox = QVBoxLayout()
        vbox.setContentsMargins(24,4,24,4)
        vbox.addWidget(self.upperline)
        vbox.addWidget(self.lowerline,0)
        self.setLayout(vbox)

    def setUpperLineText(self,text):
        self.upperline.setText(text)

    def setLowerLineText(self,text):
        self.lowerline.setText(text)


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        file = open("../m.json", "w+")
        if file.read(0) == "":file.write("""{"RecentProject1":{"ProjectName":"","ProjectPath":""}}""")
        file.close()
        file = open("../m.json", "r")
        RecentProjectsFiles = json.load(file)
        RecentProjectsListWidget = QListWidget()
        newProjectButton = QPushButton("مشروع جديد")
        openProjectButton = QPushButton("افتح")
        editProjectButton = QPushButton("تعديل")

        newProjectButton.clicked.connect(self.createNewProjectWindow)
        for ProjectInfo in RecentProjectsFiles:
            ListItem = QListWidgetItem(RecentProjectsListWidget)

            ProjectItem = CustomItemWidget()
            ProjectItem.setUpperLineText(RecentProjectsFiles[ProjectInfo]["ProjectName"])
            ProjectItem.setLowerLineText(RecentProjectsFiles[ProjectInfo]["ProjectPath"])
            ListItem.setSizeHint(ProjectItem.sizeHint())

            RecentProjectsListWidget.addItem(ListItem)
            RecentProjectsListWidget.setItemWidget(ListItem,ProjectItem)
        RecentProjectsListWidget.setStyleSheet("border:0px")
        vbox.setContentsMargins(0,0,0,0)
        self.setLayout(vbox)
        vbox.addWidget(RecentProjectsListWidget)
        vbox.addLayout(hbox)
        hbox.addWidget(newProjectButton)
        hbox.addWidget(openProjectButton)
        hbox.addWidget(editProjectButton)
        self.show()

    def createNewProjectWindow(self):
        self.win = NewProjectWindow.NewProjectWindow()


