import sys

from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QColor, QIcon


class SecondWindow(QDialog):
    def __init__(self, spare_text_variable):
        super(SecondWindow, self).__init__()
        self.closeEvent = self.closeEvent

        self.form_width = 341
        self.form_height = 139

        if spare_text_variable != "":
            self.spare_text_variable = spare_text_variable
        else:
            self.spare_text_variable = "press some keys"
        self.changedText = False

    def basicWindow(self):
        loadUi('interfaces/keybind_window.ui', self)

        self.setWindowIcon(QIcon('resources/face_switch_2_icon_black.ico'))

        self.plainTextEdit.setReadOnly(True)
        self.setWindowTitle("Keybinder 2.0")
        
        # Buttons
        self.btnConfirm.clicked.connect(self.close)
        self.btnDeleteText.clicked.connect(self.on_click_deleteText)

        self.setFixedSize(self.form_width, self.form_height)
        self.setStyleSheet("background-color: rgb(48, 52, 52);")

        self.plainTextEdit.setPlaceholderText(self.spare_text_variable)
        self.plainTextEdit.setObjectName("myObject")
        self.plainTextEdit.setLineWidth(0)
        self.plainTextEdit.setMidLineWidth(3)
        self.plainTextEdit.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.mousePressEvent = self.refocusitself

        self.btnRightClick.clicked.connect(lambda: self.right_click())
        self.btnLeftClick.clicked.connect(lambda: self.left_click())

        self.setFocus()

    def refocusitself(self, state):
        self.setFocus()

    def right_click(self):
        print("Right click")
        self.spare_text_variable += "{RIGHTCLICK}"
        self.plainTextEdit.setPlainText(self.spare_text_variable)
        self.setFocus()

    def left_click(self):
        print("Left click")
        self.spare_text_variable += "{LEFTCLICK}"
        self.plainTextEdit.setPlainText(self.spare_text_variable)
        self.setFocus()

    def on_click_deleteText(self):
        self.spare_text_variable = ""
        self.plainTextEdit.setPlainText(self.spare_text_variable)
        self.setFocus()


    def keyPressEvent(self, e):
        if not self.changedText:
            self.changedText = True

        if self.changedText:
            self.setFocus()
            key = e.key()
            print(key)
            if 49 <= key <= 57:
                self.spare_text_variable += chr(key)
            elif 48 <= key <= 90:
                self.spare_text_variable += str(chr(key)).lower()

            elif key == Qt.Key_Backslash:
                self.spare_text_variable += "\\"
            elif key == Qt.Key_Slash:
                self.spare_text_variable += "/"
            elif key == Qt.Key_Asterisk:
                self.spare_text_variable += "*"

            elif key == Qt.Key_Space:
                self.spare_text_variable += " "
            elif key == Qt.Key_Shift:
                self.spare_text_variable += "+"
            elif key == Qt.Key_Control:
                self.spare_text_variable += "^"
            elif key == Qt.Key_Alt:
                self.spare_text_variable += "%"

            elif key == Qt.Key_Left:
                self.spare_text_variable += "{LEFT}"
            elif key == Qt.Key_Right:
                self.spare_text_variable += "{RIGHT}"
            elif key == Qt.Key_Down:
                self.spare_text_variable += "{DOWN}"
            elif key == Qt.Key_Up:
                self.spare_text_variable += "{UP}"

            elif key == Qt.Key_F1:
                self.spare_text_variable += "{F1}"
            elif key == Qt.Key_F2:
                self.spare_text_variable += "{F2}"
            elif key == Qt.Key_F3:
                self.spare_text_variable += "{F3}"
            elif key == Qt.Key_F4:
                self.spare_text_variable += "{F4}"
            elif key == Qt.Key_F5:
                self.spare_text_variable += "{F5}"
            elif key == Qt.Key_F6:
                self.spare_text_variable += "{F6}"
            elif key == Qt.Key_F7:
                self.spare_text_variable += "{F7}"
            elif key == Qt.Key_F8:
                self.spare_text_variable += "{F8}"
            elif key == Qt.Key_F9:
                self.spare_text_variable += "{F9}"
            elif key == Qt.Key_F10:
                self.spare_text_variable += "{F10}"
            elif key == Qt.Key_F11:
                self.spare_text_variable += "{F11}"
            elif key == Qt.Key_F12:
                self.spare_text_variable += "{F12}"
            # Goes all the way to F16 if required.

            elif key == 16777219:
                self.spare_text_variable += "{BACKSPACE}"
            elif key == Qt.Key_CapsLock:
                self.spare_text_variable += "{CAPSLOCK}"
            elif key == Qt.Key_Clear:
                self.spare_text_variable += "{CLEAR}"
            elif key == Qt.Key_Delete:
                self.spare_text_variable += "{DELETE}"
            elif key == Qt.Key_Insert:
                self.spare_text_variable += "{INSERT}"
            elif key == Qt.Key_End:
                self.spare_text_variable += "{END}"
            elif key == 16777220:
                self.spare_text_variable += "{ENTER}"
            elif key == Qt.Key_Escape:
                self.spare_text_variable += "{ESCAPE}"
            elif key == Qt.Key_Help:
                self.spare_text_variable += "{HELP}"
            elif key == Qt.Key_Home:
                self.spare_text_variable += "{HOME}"
            elif key == Qt.Key_NumLock:
                self.spare_text_variable += "{NUMLOCK}"
            elif key == Qt.Key_PageDown:
                self.spare_text_variable += "{PGDN}"
            elif key == Qt.Key_PageUp:
                self.spare_text_variable += "{PGUP}"
            elif key == Qt.Key_ScrollLock:
                self.spare_text_variable += "{SCROLLLOCK}"
            elif key == Qt.Key_Tab:
                self.spare_text_variable += "{TAB}"

            self.plainTextEdit.setPlainText(self.spare_text_variable)

    def returnspare_text_variable(self):
        return self.spare_text_variable

    def setspare_text_variable(self, uinput):
        self.spare_text_variable = uinput

    def closeEvent(self, event):
        self.directlyClose = True
        if self.directlyClose:
            self.plainTextEdit.setPlainText("")
            self.plainTextEdit.setPlaceholderText('enter text here')
            event.accept()
