import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QCheckBox, QWidget, QPushButton, QLabel, \
    QMessageBox, QDesktopWidget, QFileDialog, QErrorMessage, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, Qt, QPoint
from imutils import face_utils
from collections import deque
import cv2
import dlib
import win32com.client as comclt  # Used to insert keys
import os, sys
import json  # for saving/loading settings


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        self.title = 'Face Switch 2.0'
        self.closeEvent = self.closeEvent
        self.setWindowIcon(QtGui.QIcon('interfaces/icon.png'))

        global app_dir  # Allow the variable to be used anywhere
        app_dir = os.environ['USERPROFILE'] + '/.FaceSwitch2'  # Path to application settings

        if not os.path.isdir(app_dir):  # Create the directory if it does not already exist
            try:
                os.mkdir(app_dir)  # Make the .FaceSwitch2 folder
            except OSError:
                print("Creation of the directory %s failed" % app_dir)
            else:
                print("Successfully created the directory %s " % app_dir)

        self.captureFacePositions = True
        self.capturedPositions = False
        self.faceShapePredictorActivated = False

        self.count = 0
        self.webcamActive = True

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # gives an error without CAP_DSHOW
        
        self.neutral_gesture_vars = {}
        self.base_line = 0

        self.sparetxtvar = ""
        self.changesMade = False

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.initUI()

        self.smileActivated = False
        self.openMouthActivated = False
        self.raiseEyebrowsActivated = False
        self.snarlActivated = False
        self.leftWinkActivated = False
        self.rightWinkActivated = False

        self.blinkActivated = False
        self.calibrate = False

        self.wsh = comclt.Dispatch("WScript.Shell")  # Open keytyper

        self.center()
        self.oldPos = self.pos()
        self.landmarks()
        
        self.facial_landmarks = 0
        
        self.neutral_open_mouth = 0
        self.neutral_raise_eyebrows = 0
        self.neutral_smile = 0
        self.neutral_snarl = 0
        self.neutral_left_wink = 0
        self.neutral_right_wink = 0
        
        self.open_mouth_var = 0
        self.raise_eyebrows_var = 0
        self.smile_var = 0
        self.snarl_var = 0
        self.left_wink_var = 0
        self.right_wink_var = 0

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def landmarks(self):
        p = "resources/shape_predictor_68_face_landmarks.dat"  # p = our pre-trained model
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(p)
        
        gesture_arr = deque(maxlen=10)
        gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
        
        while self.webcamActive:
            # Getting out image by webcam 
            _, frame = self.cap.read()
            # Converting the image to gray scale
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Get faces into webcam's image
                rects = detector(gray, 0)
            else:
                print("Error connecting to webcam! Exiting...")
                sys.exit()
            
            # Activated
            if self.faceShapePredictorActivated:
                for (i, rect) in enumerate(rects):
                    # Make the prediction and transform it to numpy array
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    self.facial_landmarks = shape # Set facial_landmarks to contain the data points from shape
                    
                    detection = False # Boolean for determining if a gesture has been detected

                    for (x, y) in shape:
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # (0, 255, 0) = Green
                    
                    # Create a base line variable so that the gesture detection will still work when the user moves towards/away from the camera
                    self.base_line = ((shape[16][0]) - (shape[0][0]))
                    
                    # Recognise gestures
                    # Open mouth
                    if self.openMouthActivated:
                        mouth_height = (shape[66][1]) - (shape[62][1])
                        try:
                            if self.neutral_gesture_vars['0'] + (mouth_height/self.base_line) > float(self.open_mouth_var):
                                gesture_arr.append(0)
                                detection = True
                        except:
                            pass
                    
                    # Raise Eyebrow
                    if self.raiseEyebrowsActivated:
                        eye_height = (shape[27][1]) - (((shape[19][1]) + (shape[24][1]))/2)
                        try:
                            if (eye_height/self.base_line) - self.neutral_gesture_vars['1'] > float(self.raise_eyebrows_var):
                                gesture_arr.append(1)
                                detection = True
                        except:
                            pass
                    
                    # Smile
                    if self.smileActivated:
                        mouth_width = (((shape[54][0]) + (shape[64][0]))/2) - (((shape[48][0]) + (shape[60][0]))/2)
                        try:
                            if (mouth_width/self.base_line) - self.neutral_gesture_vars['2'] > float(self.smile_var):
                                gesture_arr.append(2)
                                detection = True
                        except:
                            pass
                    
                    # Scrunch nose / Snarl
                    if self.snarlActivated:
                        nose_height = (((shape[31][1]) + (shape[35][1]))/2) - (((shape[21][1]) + (shape[22][1]))/2)
                        try:
                            if self.neutral_gesture_vars['3'] - (nose_height/self.base_line) > float(self.snarl_var):
                                gesture_arr.append(3)
                                detection = True
                        except:
                            pass
                    
                    # Left Wink
                    if self.leftWinkActivated:
                        left_eye_top = ((shape[43][1]) + (shape[44][1]))/2
                        left_eye_bottom = ((shape[46][1]) + (shape[47][1]))/2
                        left_eye_height = left_eye_bottom - left_eye_top
                        try:
                            if self.neutral_gesture_vars['4'] - (left_eye_height/self.base_line) > float(self.left_wink_var):
                                gesture_arr.append(4)
                                gesture_arr.append(4)
                                gesture_arr.append(4)
                                detection = True
                        except:
                            pass
                    
                    # Right Wink
                    if self.rightWinkActivated:
                        right_eye_top = ((shape[37][1]) + (shape[38][1]))/2
                        right_eye_bottom = ((shape[40][1]) + (shape[41][1]))/2
                        right_eye_height = right_eye_bottom - right_eye_top
                        try:
                            if self.neutral_gesture_vars['5'] - (right_eye_height/self.base_line) > float(self.right_wink_var):
                                gesture_arr.append(5)
                                gesture_arr.append(5)
                                gesture_arr.append(5)
                                detection = True
                        except:
                            pass
                    
                    # If there was no gesture detected, add a default value to the array
                    # This prevents gesture detections from the previous gesture carrying over to the next
                    if not detection:
                        gesture_arr.append(-1)
                    
                    gesture_output = -1  # Set the default value to -1 (no gesture)
                    #  Get the most common number (gesture) from the array and set it to be the registered gesture
                    #  (eliminates noise)
                    if -1 not in gesture_arr:  #  Only if the array is full of gesture recognitions (i.e no default values)
                        gesture_output = max(set(gesture_arr), key=gesture_arr.count)
                    
                    if gesture_output == 0:
                        print("Mouth opened! - ", self.neutral_gesture_vars['0'] + (mouth_height/self.base_line))
                        self.wsh.SendKeys(self.txtOpenMouth.toPlainText())
                        for t in range(60, 68, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                        
                    elif gesture_output == 1:
                        print("Eyebrows raised! - ", (eye_height/self.base_line) - self.neutral_gesture_vars['1'])
                        self.wsh.SendKeys(self.txtRaiseEyebrows.toPlainText())
                        for t in range(17, 27, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                            
                    elif gesture_output == 2:
                        print("Smile detected! - ", (mouth_width/self.base_line) - self.neutral_gesture_vars['2'])
                        self.wsh.SendKeys(self.txtSmile.toPlainText())
                        for t in range(54, 60, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                        cv2.circle(frame, (shape[48][0], shape[48][1]), 2, (255, 0, 0), -1)
                        
                    elif gesture_output == 3:
                        print("Anger detected! - ", self.neutral_gesture_vars['3'] - (nose_height/self.base_line))
                        self.wsh.SendKeys(self.txtSnarl.toPlainText())
                        for t in range(27, 36, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                            
                    elif gesture_output == 4:
                        print("Left wink detected! - ", self.neutral_gesture_vars['4'] - (left_eye_height/self.base_line))
                        self.wsh.SendKeys(self.txtLeftWink.toPlainText())
                        for t in range(42, 48, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                    
                    elif gesture_output == 5:
                        print("Right wink detected! - ", self.neutral_gesture_vars['5'] - (right_eye_height/self.base_line))
                        self.wsh.SendKeys(self.txtRightWink.toPlainText())
                        for t in range(36, 42, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                    
                    if 0 <= gesture_output <= 5: # If a gesture was output, reset the gesture array to give a small pause
                        gesture_arr = deque(maxlen=10)
                        gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
                        
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(rgb_frame.tobytes(), 
                rgb_frame.shape[1],
                rgb_frame.shape[0],
                QImage.Format_RGB888)
            self.webcam.setPixmap(QPixmap.fromImage(image))
            self.webcam.show()
            
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                self.exit()
            # Press 'q' to break out of loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.exit()
                
        cv2.destroyAllWindows()
        self.cap.release()

    def initUI(self):
        loadUi('interfaces/fr.ui', self)
        
        # Load default settings
        self.value_changed()
        
        # Load previous state settings from file
        print("Checking for state settings...")
        state_settings_path = app_dir + '/state_settings.json'
        self.load_settings(state_settings_path)  # Load the last settings that were last used
        QApplication.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)

        # Text boxes
        # On mouse click
        self.txtOpenMouth.mousePressEvent = self.get_userinput
        self.txtRaiseEyebrows.mousePressEvent = self.get_userinput1
        self.txtSmile.mousePressEvent = self.get_userinput2
        self.txtSnarl.mousePressEvent = self.get_userinput3
        self.txtLeftWink.mousePressEvent = self.get_userinput4
        self.txtRightWink.mousePressEvent = self.get_userinput5

        # Checkboxes
        self.cboxOpenMouth.stateChanged.connect(lambda: self.btn_state(self.cboxOpenMouth))
        self.cboxRaiseEyebrows.stateChanged.connect(lambda: self.btn_state(self.cboxRaiseEyebrows))
        self.cboxSmile.stateChanged.connect(lambda: self.btn_state(self.cboxSmile))
        self.cboxSnarl.stateChanged.connect(lambda: self.btn_state(self.cboxSnarl))
        self.cboxLeftWink.stateChanged.connect(lambda: self.btn_state(self.cboxLeftWink))
        self.cboxRightWink.stateChanged.connect(lambda: self.btn_state(self.cboxRightWink))
        
        # Buttons
        self.btnInitialize.setToolTip('Toggle Gesture Detection ON/OFF')
        self.btnInitialize.clicked.connect(self.on_click_initialize)
        self.btnSave.setToolTip('Save Settings')		
        self.btnSave.clicked.connect(lambda: self.btn_save_settings())
        self.btnLoad.setToolTip('Load Settings')
        self.btnLoad.clicked.connect(lambda: self.btn_load_settings())
        self.btnCalibrate.clicked.connect(lambda: self.btn_calibrate(self.facial_landmarks, self.base_line))

        # sliders
        self.sliderOpenMouth.valueChanged.connect(lambda: self.value_changed())
        self.sliderRaiseEyebrows.valueChanged.connect(lambda: self.value_changed())
        self.sliderSmile.valueChanged.connect(lambda: self.value_changed())
        self.sliderSnarl.valueChanged.connect(lambda: self.value_changed())
        self.sliderLeftWink.valueChanged.connect(lambda: self.value_changed())
        self.sliderRightWink.valueChanged.connect(lambda: self.value_changed())
        
        # webcam
        self.webcam.setText("Webcam")
        self.show()

    def btn_calibrate(self, neutral_landmarks, base_line):
        self.neutral_landmarks = neutral_landmarks
        self.base_line = base_line

        if self.faceShapePredictorActivated:
            # print(self.neutral_landmarks.shape)

            # Calculate facial feture distance ratios for the users neutral face
            # Closed mouth ratio
            self.neutral_open_mouth = self.neutral_landmarks[66][1] - self.neutral_landmarks[62][1]
            self.neutral_open_mouth /= base_line
            print("closed mouth:", self.neutral_open_mouth)
            # Normal eyebrow height ratio
            self.neutral_raise_eyebrows = (self.neutral_landmarks[27][1]) - (
                        ((self.neutral_landmarks[19][1]) + (self.neutral_landmarks[24][1])) / 2)
            self.neutral_raise_eyebrows /= base_line
            print("eyebrows:", self.neutral_raise_eyebrows)
            # Normal mouth width ratio
            self.neutral_smile = (((self.neutral_landmarks[54][0]) + (self.neutral_landmarks[64][0])) / 2) - (
                        ((self.neutral_landmarks[48][0]) + (self.neutral_landmarks[60][0])) / 2)
            self.neutral_smile /= base_line
            print("smile:", self.neutral_smile)
            # Normal non frown/snarl ratio
            self.neutral_snarl = (((self.neutral_landmarks[31][1]) + (self.neutral_landmarks[35][1])) / 2) - (
                        ((self.neutral_landmarks[21][1]) + (self.neutral_landmarks[22][1])) / 2)
            self.neutral_snarl /= base_line
            print("nose:", self.neutral_snarl)
            # Normal left eye height ratio
            left_eye_top = ((self.neutral_landmarks[43][1]) + (self.neutral_landmarks[44][1])) / 2
            left_eye_bottom = ((self.neutral_landmarks[46][1]) + (self.neutral_landmarks[47][1])) / 2
            self.neutral_left_wink = left_eye_bottom - left_eye_top
            self.neutral_left_wink /= base_line
            print("left eye:", self.neutral_left_wink)
            # Normal right eye height ratio
            right_eye_top = ((self.neutral_landmarks[37][1]) + (self.neutral_landmarks[38][1])) / 2
            right_eye_bottom = ((self.neutral_landmarks[40][1]) + (self.neutral_landmarks[41][1])) / 2
            self.neutral_right_wink = right_eye_bottom - right_eye_top
            self.neutral_right_wink /= base_line
            print("right eye:", self.neutral_right_wink)

            # Fill the dictionary with the new calibration
            self.neutral_gesture_vars = {'0': self.neutral_open_mouth,
                                         '1': self.neutral_raise_eyebrows,
                                         '2': self.neutral_smile,
                                         '3': self.neutral_snarl,
                                         '4': self.neutral_left_wink,
                                         '5': self.neutral_right_wink
                                         }

        else:
            pass
            print("Must be activated")

    def get_keybind(self, state):
        self.changesMade = True
        #usrkeybind, ok = QInputDialog.getText(self, 'Enter KeyBind', '>')
        usrkeybind, ok = QInputDialog.getText(self, 'Get Keybind', 'enter your name')
        print(usrkeybind)

        emptyVar = ""

        self.txtOpenMouth.setPlainText(usrkeybind)

    def get_userinput(self, state):
        self.changesMade = not self.changesMade
        self.txtOpenMouth.setReadOnly(True)

        if self.changesMade:
            self.sparetxtvar = ""
            self.txtOpenMouth.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtOpenMouth.setPlainText(self.sparetxtvar)
            self.txtOpenMouth.setReadOnly(False)

    def get_userinput1(self, state):
        self.changesMade = not self.changesMade
        self.txtRaiseEyebrows.setReadOnly(True)

        if self.changesMade:
            self.sparetxtvar = ""
            self.txtRaiseEyebrows.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtRaiseEyebrows.setPlainText(self.sparetxtvar)
            self.txtRaiseEyebrows.setReadOnly(False)

    def get_userinput2(self, state):
        self.changesMade = not self.changesMade
        self.txtSmile.setReadOnly(True)
        if self.changesMade:
            self.sparetxtvar = ""
            self.txtSmile.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtSmile.setPlainText(self.sparetxtvar)
            self.txtSmile.setReadOnly(False)

    def get_userinput3(self, state):
        self.changesMade = not self.changesMade
        self.txtSnarl.setReadOnly(True)
        if self.changesMade:
            self.sparetxtvar = ""
            self.txtSnarl.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtSnarl.setPlainText(self.sparetxtvar)
            self.txtSnarl.setReadOnly(False)

    def get_userinput4(self, state):
        self.changesMade = not self.changesMade
        self.txtLeftWink.setReadOnly(True)
        if self.changesMade:
            self.sparetxtvar = ""
            self.txtLeftWink.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtLeftWink.setPlainText(self.sparetxtvar)
            self.txtLeftWink.setReadOnly(False)

    def get_userinput5(self, state):
        self.changesMade = not self.changesMade
        self.txtRightWink.setReadOnly(True)
        if self.changesMade:
            self.sparetxtvar = ""
            self.txtRightWink.setPlainText("Press some keys")

        elif not self.changesMade:
            self.txtRightWink.setPlainText(self.sparetxtvar)
            self.txtRightWink.setReadOnly(False)

    def keyPressEvent(self, e):

        if self.changesMade:
            key = e.key()
            print(key)
            #test = QMessageBox.information(self, "hello", "I m here")
            # Numerical
            if key == 48:
                self.sparetxtvar += "0"
            elif key == 49:
                self.sparetxtvar += "1"
            elif key == 50:
                self.sparetxtvar += "2"
            elif key == 51:
                self.sparetxtvar += "3"
            elif key == 52:
                self.sparetxtvar += "4"
            elif key == 53:
                self.sparetxtvar += "5"
            elif key == 54:
                self.sparetxtvar += "6"
            elif key == 55:
                self.sparetxtvar += "7"
            elif key == 56:
                self.sparetxtvar += "8"
            elif key == 57:
                self.sparetxtvar += "9"

            # Alphabetical
            elif key == 65:
                self.sparetxtvar += "a"
            elif key == 66:
                self.sparetxtvar += "b"
            elif key == 67:
                self.sparetxtvar += "c"
            elif key == 68:
                self.sparetxtvar += "d"
            elif key == 69:
                self.sparetxtvar += "e"
            elif key == 70:
                self.sparetxtvar += "f"
            elif key == 71:
                self.sparetxtvar += "g"
            elif key == 72:
                self.sparetxtvar += "h"
            elif key == 73:
                self.sparetxtvar += "i"
            elif key == 74:
                self.sparetxtvar += "j"
            elif key == 75:
                self.sparetxtvar += "k"
            elif key == 76:
                self.sparetxtvar += "l"
            elif key == 77:
                self.sparetxtvar += "m"
            elif key == 78:
                self.sparetxtvar += "n"
            elif key == 79:
                self.sparetxtvar += "o"
            elif key == 80:
                self.sparetxtvar += "p"
            elif key == 81:
                self.sparetxtvar += "q"
            elif key == 82:
                self.sparetxtvar += "r"
            elif key == 83:
                self.sparetxtvar += "s"
            elif key == 84:
                self.sparetxtvar += "t"
            elif key == 85:
                self.sparetxtvar += "u"
            elif key == 86:
                self.sparetxtvar += "v"
            elif key == 87:
                self.sparetxtvar += "w"
            elif key == 88:
                self.sparetxtvar += "x"
            elif key == 89:
                self.sparetxtvar += "y"
            elif key == 90:
                self.sparetxtvar += "z"

            elif key == Qt.Key_Space:
                self.sparetxtvar += " "

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
            elif key == Qt.Key_Backspace:
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

            # {BREAK}
            # {PRTSC} ## Print Screen


    def value_changed(self):
        self.open_mouth_var = round(float(self.sliderOpenMouth.value()) / 400, 2)
        self.raise_eyebrows_var = round(float(self.sliderRaiseEyebrows.value()) / 1250, 2)
        self.smile_var = round(float(self.sliderSmile.value()) / 500, 2)
        self.snarl_var = round(float(self.sliderSnarl.value()) / 1000, 3)
        self.left_wink_var = round(float(self.sliderLeftWink.value()) / 1000, 3)
        self.right_wink_var = round(float(self.sliderRightWink.value()) / 1000, 3)
    
        self.lblOpenMouthT.setText(str(self.open_mouth_var))
        self.lblRaiseEyebrowsT.setText(str(self.raise_eyebrows_var))
        self.lblSmileT.setText(str(self.smile_var))
        self.lblSnarlT.setText(str(self.snarl_var))
        self.lblLeftWinkT.setText(str(self.left_wink_var))
        self.lblRightWinkT.setText(str(self.right_wink_var))

    def prep_data_to_save(self):
        data = {'openMouthKey': self.txtOpenMouth.toPlainText(),
                'raiseEyebrowsKey': self.txtRaiseEyebrows.toPlainText(),
                'smileKey': self.txtSmile.toPlainText(),
                'snarlKey': self.txtSnarl.toPlainText(),
                'leftWinkKey': self.txtLeftWink.toPlainText(),
                'rightWinkKey': self.txtRightWink.toPlainText(),
                'open_mouth_var': self.open_mouth_var,
                'raise_eyebrows_var': self.raise_eyebrows_var,
                'smile_var': self.smile_var,
                'snarl_var': self.snarl_var,
                'left_wink_var': self.left_wink_var,
                'right_wink_var': self.right_wink_var
                }
        try:
            calibration = {'0': self.neutral_open_mouth,
                        '1': self.neutral_raise_eyebrows,
                        '2': self.neutral_smile,
                        '3': self.neutral_snarl,
                        '4': self.neutral_left_wink,
                        '5': self.neutral_right_wink
                        }
            data.update(calibration)
        except:
            print("No calibration detected!")
            
        return data

    def save_state(self):
        data = self.prep_data_to_save()
        
        filepathwithextension = app_dir + '/state_settings.json'
        with open(filepathwithextension, 'w') as f:
            json.dump(data, f)

    def save_settings(self, path, file_name, data):
        filepathwithextension = path + '/' + file_name + '.json'
        try:
            with open(filepathwithextension, 'w') as f:
                json.dump(data, f)
            print("Settings file: '" + filepathwithextension + "' saved successfully!")
        except:
            print("An error occurred!")

    def btn_save_settings(self):
        data = self.prep_data_to_save()
        
        name, ok = QInputDialog.getText(self, 'Save Settings', 'Enter your name:')
        
        if ok and name != '':
            self.save_settings(app_dir, name, data)

    def load_settings(self, file_name):
        data = {}
        name = file_name
        try:
            with open(name, 'r') as f:
                data = json.load(f)
                self.txtOpenMouth.setPlainText(str(data['openMouthKey']))
                self.txtRaiseEyebrows.setPlainText(str(data['raiseEyebrowsKey']))
                self.txtSmile.setPlainText(str(data['smileKey']))
                self.txtSnarl.setPlainText(str(data['snarlKey']))
                self.txtLeftWink.setPlainText(str(data['leftWinkKey']))
                self.txtRightWink.setPlainText(str(data['rightWinkKey']))
                self.sliderOpenMouth.setValue(int(data['open_mouth_var']*400))
                self.sliderRaiseEyebrows.setValue(int(data['raise_eyebrows_var']*1250))
                self.sliderSmile.setValue(int(data['smile_var']*500))
                self.sliderSnarl.setValue(int(data['snarl_var']*1000))
                self.sliderLeftWink.setValue(int(data['left_wink_var']*1000))
                self.sliderRightWink.setValue(int(data['right_wink_var']*1000))
                
                print("Initial settings: '" + name + "' loaded successfully!")
        except FileNotFoundError:
            print("Settings file: '" + name + "' not found or corrupt!")
        else:
            try:
                self.neutral_open_mouth = float(data['0'])
                self.neutral_raise_eyebrows = float(data['1'])
                self.neutral_smile = float(data['2'])
                self.neutral_snarl = float(data['3'])
                self.neutral_left_wink = float(data['4'])
                self.neutral_right_wink = float(data['5'])
                self.neutral_gesture_vars = {'0': self.neutral_open_mouth,
                                            '1': self.neutral_raise_eyebrows,
                                            '2': self.neutral_smile,
                                            '3': self.neutral_snarl,
                                            '4': self.neutral_left_wink,
                                            '5': self.neutral_right_wink
                                            }
            except:
                print("Error with calibration data!")
            
        self.value_changed()

    def btn_load_settings(self):
        f, a = QFileDialog.getOpenFileName(self, "title", app_dir, "json files  (*.json)")  # returns two items
        if f != '':
            self.load_settings(f)  # pass the first item

    def btn_state(self, state):
        # checkBox activations
        # open mouth checkbox
        if state.objectName() == "cboxOpenMouth":
            if state.isChecked():
                if not self.openMouthActivated:
                    print("Open Mouth detection activated")
                    self.openMouthActivated = True
            else:
                self.openMouthActivated = False
                print("Open Mouth detection deactivated")
        # raise eyebrow checkbox
        if state.objectName() == "cboxRaiseEyebrows":
            if state.isChecked():
                if not self.raiseEyebrowsActivated:
                    print("Raise Eyebrows detection activated")
                    self.raiseEyebrowsActivated = True
            else:
                self.raiseEyebrowsActivated = False
                print("Raise Eyebrows detection deactivated")
        # smile checkbox
        if state.objectName() == "cboxSmile":
            if state.isChecked():
                if not self.smileActivated:
                    print("Smile detection activated")
                    self.smileActivated = True
            else:
                self.smileActivated = False
                print("Smile detection deactivated")	
                
        # snarl checkbox
        if state.objectName() == "cboxSnarl":
            if state.isChecked():
                if not self.snarlActivated:
                    print("Snarl detection activated")
                    self.snarlActivated = True
            else:
                self.snarlActivated = False
                print("Snarl detection deactivated")
        # left wink checkbox
        if state.objectName() == "cboxLeftWink":
            if state.isChecked():
                if not self.leftWinkActivated:
                    print("Left Wink detection activated")
                    self.leftWinkActivated = True
            else:
                self.leftWinkActivated = False
                print("Left Wink detection deactivated")
                
        # right wink checkbox
        if state.objectName() == "cboxRightWink":
            if state.isChecked():
                if not self.rightWinkActivated:
                    print("Right Wink detection activated")
                    self.rightWinkActivated = True
            else:
                self.rightWinkActivated = False
                print("Right Wink detection deactivated")

    @pyqtSlot()
    def on_click_initialize(self):  # Used to turn the gesture detection ON or OFF
        if self.faceShapePredictorActivated:
            self.faceShapePredictorActivated = False
            print("Gesture detection Deactivated!")
            self.btnInitialize.setText("Activate")

        elif not self.faceShapePredictorActivated:
            self.faceShapePredictorActivated = True
            print("Gesture detection Activated!")
            self.btnInitialize.setText("Deactivate")


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Save the settings before exiting
            print("Saving state settings...")
            self.save_state()
            print("State settings saved successfully!")
            self.webcamActive = False
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    print("Now exiting")
    sys.exit()
