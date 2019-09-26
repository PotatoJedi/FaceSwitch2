from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

class SecondWindow(QDialog):
    def __init__(self, parent=None):
        super(SecondWindow, self).__init__()

        self.closeEvent = self.closeEvent

        self.sparetxtvar = ""

        self.basicWindow()

    def basicWindow(self):
        loadUi('interfaces/fr2.ui', self)
        self.plainTextEdit.setReadOnly(True)

    def keyPressEvent(self, e):
        key = e.key()
        #test = QMessageBox.information(self, "hello", "I m here")
        print(key)
        # Numerical
        # Numbers
        if 58 <= key <= 67:
            self.sparetxtvar += chr(key)
            # Characters print out in capitals naturally.
        elif 48 <= key <= 90:
            self.sparetxtvar += str(chr(key)).lower()
        # Space key does not work
        #elif key == Qt.Key_Space:
        #   self.sparetxtvar += " "
        # Modifiers
        elif key == Qt.Key_Shift:
            self.sparetxtvar += "+"
        elif key == Qt.Key_Control:
            self.sparetxtvar += "^"
        elif key == Qt.Key_Alt:
            self.sparetxtvar += "%"

        # Left Right Up Down
        elif key == Qt.Key_Left:
            self.sparetxtvar += "{LEFT}"
        elif key == Qt.Key_Right:
            self.sparetxtvar += "{RIGHT}"
        elif key == Qt.Key_Down:
            self.sparetxtvar += "{DOWN}"
        elif key == Qt.Key_Up:
            self.sparetxtvar += "{UP}"

        # Function keys
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

            # Alternative keys:
            # {BACKSPACE}
        elif key == 16777219:
            self.sparetxtvar += "{BACKSPACE}"
        # {CAPSLOCK}
        elif key == Qt.Key_CapsLock:
            self.sparetxtvar += "{CAPSLOCK}"
        # {CLEAR}
        elif key == Qt.Key_Clear:
            self.sparetxtvar += "{CLEAR}"
        # {DELETE}
        elif key == Qt.Key_Delete:
            self.sparetxtvar += "{DELETE}"
        # {INSERT}
        elif key == Qt.Key_Insert:
            self.sparetxtvar += "{INSERT}"
            # {END}
        elif key == Qt.Key_End:
            self.sparetxtvar += "{END}"

            # {ENTER}
        elif key == 16777220:
            self.sparetxtvar += "{ENTER}"

            # {ESCAPE}
        elif key == Qt.Key_Escape:
            self.sparetxtvar += "{ESCAPE}"
            # {HELP}
        elif key == Qt.Key_Help:
            self.sparetxtvar += "{HELP}"
            # {HOME}
        elif key == Qt.Key_Home:
            self.sparetxtvar += "{HOME}"
            # {NUMLOCK}
        elif key == Qt.Key_NumLock:
            self.sparetxtvar += "{NUMLOCK}"
            # {PGDN} / Page Down
        elif key == Qt.Key_PageDown:
            self.sparetxtvar += "{PGDN}"
            # {PGUP} / Page Up
        elif key == Qt.Key_PageUp:
            self.sparetxtvar += "{PGUP}"
            # {SCROLLLOCK}
        elif key == Qt.Key_ScrollLock:
            self.sparetxtvar += "{SCROLLLOCK}"
            # {TAB}
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
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            self.sparetxtvar = ""
            event.ignore()
