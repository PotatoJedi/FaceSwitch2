import keybinder as keybinder
from PyQt5.QtWidgets import QDialog
import main as main

class textBox(QDialog):
    def __init__(self, name):
        super(textBox, self).__init__()

        self.secondWindow = keybinder.SecondWindow()

        self.name = name
        self.sparetxtvar = ""

    def getUserInput(self):
        self.secondWindow.basicWindow()
        retreivedVar = self.secondWindow.returnSparetxtVar()

        if retreivedVar != "":
            self.secondWindow.setSparetxtVar("")

        if not self.secondWindow.exec_():
            retreivedVar = self.secondWindow.returnSparetxtVar()
            self.sparetxtvar = retreivedVar

    def getSpareTxtVar(self):
        return self.sparetxtvar

    def getName(self):
        return name