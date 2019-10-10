import sys

from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QColor, QIcon

class SecondWindow(QDialog):
    def __init__(self, sparetxtvar):
        super(SecondWindow, self).__init__()
        self.closeEvent = self.closeEvent
		
        if sparetxtvar != "":
            self.sparetxtvar = sparetxtvar
        else:
            self.sparetxtvar = ""
        self.changedText = False

    def basicWindow(self):
        loadUi('interfaces/fr2.ui', self)
		
        self.setWindowIcon(QIcon('resources/facial_landmarks_68markup-768x619-transparent.png'))

        self.plainTextEdit.setReadOnly(True)
        self.setWindowTitle("Start typing!")
        # buttons
        self.btnEnter.clicked.connect(self.close)
        self.btnDeleteText.clicked.connect(self.on_click_deleteText)

        self.setWindowFlags(Qt.Window)
       # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.setStyleSheet("background-color: rgb(48, 52, 52);")

        self.plainTextEdit.setPlaceholderText(self.sparetxtvar)
        self.plainTextEdit.setObjectName("myObject")
        self.plainTextEdit.setLineWidth(0)
        self.plainTextEdit.setMidLineWidth(3)
        self.plainTextEdit.setContentsMargins(0, 0, 0, 0)
		
		#Turn blue edge
        #self.setStyleSheet("#myObject { border: 1px solid rgb(42, 130, 218); }")


    def on_click_deleteText(self):
        self.sparetxtvar = ""
        self.plainTextEdit.setPlainText(self.sparetxtvar)

    def keyPressEvent(self, e):
        if not self.changedText:
            #self.plainTextEdit.setPlaceholderText('')
            self.changedText = True

        if self.changedText:
            self.setFocus()
            key = e.key()
            print(key)
            if 49 <= key <= 57:
                self.sparetxtvar += chr(key)
            elif 48 <= key <= 90:
                self.sparetxtvar += str(chr(key)).lower()
            elif key == Qt.Key_Space:
                self.sparetxtvar += " "
            elif key == Qt.Key_Shift:
                self.sparetxtvar += "+"
            elif key == Qt.Key_Control:
                self.sparetxtvar += "^"
            elif key == Qt.Key_Alt:
                self.sparetxtvar += "%"

            elif key == Qt.Key_Left:
                self.sparetxtvar += "{LEFT}"
            elif key == Qt.Key_Right:
                self.sparetxtvar += "{RIGHT}"
            elif key == Qt.Key_Down:
                self.sparetxtvar += "{DOWN}"
            elif key == Qt.Key_Up:
                self.sparetxtvar += "{UP}"

            elif key == Qt.Key_F1:
                self.sparetxtvar += "{F1}"
            elif key == Qt.Key_F2:
                self.sparetxtvar += "{F2}"
            elif key == Qt.Key_F3:
                self.sparetxtvar += "{F3}"
            elif key == Qt.Key_F4:
                self.sparetxtvar += "{F4}"
            elif key == Qt.Key_F5:
                self.sparetxtvar += "{F5}"
            elif key == Qt.Key_F6:
                self.sparetxtvar += "{F6}"
            elif key == Qt.Key_F7:
                self.sparetxtvar += "{F7}"
            elif key == Qt.Key_F8:
                self.sparetxtvar += "{F8}"
            elif key == Qt.Key_F9:
                self.sparetxtvar += "{F9}"
            elif key == Qt.Key_F10:
                self.sparetxtvar += "{F10}"
            elif key == Qt.Key_F11:
                self.sparetxtvar += "{F11}"
            elif key == Qt.Key_F12:
                self.sparetxtvar += "{F12}"
                # Goes all the way to F16 if required.

            elif key == 16777219:
                self.sparetxtvar += "{BACKSPACE}"
            elif key == Qt.Key_CapsLock:
                self.sparetxtvar += "{CAPSLOCK}"
            elif key == Qt.Key_Clear:
                self.sparetxtvar += "{CLEAR}"
            elif key == Qt.Key_Delete:
                self.sparetxtvar += "{DELETE}"
            elif key == Qt.Key_Insert:
                self.sparetxtvar += "{INSERT}"
            elif key == Qt.Key_End:
                self.sparetxtvar += "{END}"
            elif key == 16777220:
                self.sparetxtvar += "{ENTER}"
            elif key == Qt.Key_Escape:
                self.sparetxtvar += "{ESCAPE}"
            elif key == Qt.Key_Help:
                self.sparetxtvar += "{HELP}"
            elif key == Qt.Key_Home:
                self.sparetxtvar += "{HOME}"
            elif key == Qt.Key_NumLock:
                self.sparetxtvar += "{NUMLOCK}"
            elif key == Qt.Key_PageDown:
                self.sparetxtvar += "{PGDN}"
            elif key == Qt.Key_PageUp:
                self.sparetxtvar += "{PGUP}"
            elif key == Qt.Key_ScrollLock:
                self.sparetxtvar += "{SCROLLLOCK}"
            elif key == Qt.Key_Tab:
                self.sparetxtvar += "{TAB}"

            self.plainTextEdit.setPlainText(self.sparetxtvar)
                # {BREAK}
                # {PRTSC} ## Print Screen

    def returnSparetxtVar(self):
        return self.sparetxtvar

    def setSparetxtVar(self, uinput):
        self.sparetxtvar = uinput

    def closeEvent(self, event):
        self.directlyClose = True
        if self.directlyClose:
            self.plainTextEdit.setPlainText("")
            self.plainTextEdit.setPlaceholderText('enter text here')
            self.btnEnter.setFocus()
            event.accept()
