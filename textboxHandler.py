import keybinder as keybinder
from PyQt5.QtWidgets import QDialog
import main as main

class textBox(QDialog):
    def __init__(self, name):
        super(textBox, self).__init__()
        
        self.name = name
        self.spare_text_variable = ""

    def getUserInput(self):
        self.secondWindow = keybinder.SecondWindow(self.spare_text_variable)

        self.secondWindow.basicWindow()
        retreivedVar = self.secondWindow.returnspare_text_variable()

        if retreivedVar != "":
            self.secondWindow.setspare_text_variable("")

        if not self.secondWindow.exec_():
            retreivedVar = self.secondWindow.returnspare_text_variable()
            self.spare_text_variable = retreivedVar

    def getspare_text_variable(self):
        return self.spare_text_variable

    def getName(self):
        return name