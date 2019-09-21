from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QImage

from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QCheckBox, QWidget, QPushButton, QLabel, \
    QMessageBox, QDesktopWidget, QFileDialog, QErrorMessage

class Example(QDialog):
    def __init__(self):
        super(Example, self).__init__()
        self.setGeometry(300, 300, 250, 150)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            print("Q")

        if event.key() == QtCore.Qt.Key_Enter:
            print("Call Enter Key")
            self.proceed()

    def proceed(self):
        print("Call Enter Key")

def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()