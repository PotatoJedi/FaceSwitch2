import sys 
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QCheckBox, QWidget, QPushButton, QLabel, \
    QMessageBox, QDesktopWidget, QFileDialog, QErrorMessage
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, Qt, QPoint
from imutils import face_utils
from collections import deque
import cv2
import dlib
import win32com.client as comclt  # Used to insert keys
import os

import json  # for saving/loading settings


class App(QDialog):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Face Switch 2.0'
        self.closeEvent = self.closeEvent
        self.setWindowIcon(QtGui.QIcon('interface/icon.png'))
        
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
        
        self.webcamActive = True
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # gives an error without CAP_DSHOW
        
        self.neutral_gesture_vars = {}
        self.base_line = 0

        self.initUI()
        
        self.smileActivated = False
        self.openMouthActivated = False
        self.raiseEyebrowsActivated = False
        self.snarlActivated = False
        self.blinkActivated = False
        
        self.wsh = comclt.Dispatch("WScript.Shell")  # Open keytyper
        
        self.center()
        self.oldPos = self.pos()
        self.landmarks()
        
        #self.facial_landmarks = numpy.zeroes((68, 2))
        self.facial_landmarks = 0
        
        self.neutral_open_mouth = 0
        self.neutral_raise_eyebrows = 0
        self.neutral_smile = 0
        self.neutral_snarl = 0
        self.neutral_blink = 0
        
        self.open_mouth_var = 0
        self.raise_eyebrows_var = 0
        self.smile_var = 0
        self.snarl_var = 0
        self.blink_var = 0

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

        gesture_arr = deque(maxlen=15)
        gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
        
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
                    """
                    # Open mouth
                    if self.openMouthActivated:
                        mouth_top = ((shape[61][1]) + (shape[62][1]) + (shape[63][1]))/3
                        mouth_bottom = ((shape[65][1]) + (shape[66][1]) + (shape[67][1]))/3
                        mouth_height = mouth_bottom - mouth_top
                        try:
                            if mouth_height/self.base_line > float(self.open_mouth_var):
                                gesture_arr.append(0)
                        except:
                            pass
                    # Raise Eyebrow
                    if self.raiseEyebrowsActivated:
                        eye_top = ((shape[18][1]) + (shape[19][1]) + (shape[20][1]) + (shape[23][1])
                                   + (shape[24][1]) + (shape[25][1]))/6
                        eye_bottom = ((shape[27][1]) + (shape[28][1]))/2
                        eye_height = eye_bottom - eye_top
                        try:
                            if eye_height/self.base_line > float(self.raise_eyebrows_var):
                                gesture_arr.append(1)
                        except:
                            pass
                    # Smile
                    if self.smileActivated:
                        mouth_left = ((shape[48][0]) + (shape[49][0]) + (shape[59][0]) + (shape[60][0]))/4
                        mouth_right = ((shape[53][0]) + (shape[54][0]) + (shape[55][0]) + (shape[64][0]))/4
                        mouth_width = mouth_right - mouth_left
                        try:
                            if mouth_width/self.base_line > float(self.smile_var):
                                gesture_arr.append(2)
                        except:
                            pass
                    # Scrunch nose / Snarl
                    if self.snarlActivated:
                        nose_top = ((shape[21][1]) + (shape[22][1]))/2
                        nose_bottom = ((shape[31][1]) + (shape[35][1]))/2
                        nose_height = nose_bottom - nose_top
                        try:
                            if nose_height/self.base_line < float(self.snarl_var):
                                gesture_arr.append(3)
                        except:
                            pass
                    # Blink
                    if self.blinkActivated:
                        eyelid_top = ((shape[37][1]) + (shape[38][1]) + (shape[43][1]) + (shape[44][1]))/4
                        eyelid_bottom = ((shape[40][1]) + (shape[41][1]) + (shape[46][1]) + (shape[47][1]))/4
                        eyelid_height = eyelid_bottom - eyelid_top
                        try:
                            if eyelid_height/self.base_line < float(self.blink_var):
                                gesture_arr.append(4)
                        except:
                            pass
                            
                    """
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
                    
                    # Blink
                    if self.blinkActivated:
                        eyelid_top = ((shape[37][1]) + (shape[38][1]) + (shape[43][1]) + (shape[44][1]))/4
                        eyelid_bottom = ((shape[40][1]) + (shape[41][1]) + (shape[46][1]) + (shape[47][1]))/4
                        eyelid_height = eyelid_bottom - eyelid_top
                        try:
                            if eyelid_height/self.base_line < float(self.blink_var):
                                gesture_arr.append(4)
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
                        print("Eye close detected! - ", (eyelid_height/self.base_line))
                        self.wsh.SendKeys(self.txtBlink.toPlainText())
                        for t in range(36, 48, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                    
                    if 0 <= gesture_output <= 4: # If a gesture was output, reset the gesture array to give a small pause
                        gesture_arr = deque(maxlen=15)
                        gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
                    
                    
                    
                    """
                    if gesture_output == 0:
                        print("Mouth opened! - ", (mouth_height/self.base_line))
                        self.wsh.SendKeys(self.txtOpenMouth.toPlainText())
                        for t in range(60, 68, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                        
                    elif gesture_output == 1:
                        print("Eyebrows raised! - ", (eye_height/self.base_line))
                        self.wsh.SendKeys(self.txtRaiseEyebrows.toPlainText())
                        for t in range(17, 27, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                            
                    elif gesture_output == 2:
                        print("Smile detected! - ", (mouth_width/self.base_line))
                        self.wsh.SendKeys(self.txtSmile.toPlainText())
                        for t in range(54, 60, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                        cv2.circle(frame, (shape[48][0], shape[48][1]), 2, (255, 0, 0), -1)
                        
                    elif gesture_output == 3:
                        print("Anger detected! - ", (nose_height/self.base_line))
                        self.wsh.SendKeys(self.txtSnarl.toPlainText())
                        for t in range(27, 36, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                            
                    elif gesture_output == 4:
                        print("Eye close detected! - ", (eyelid_height/self.base_line))
                        self.wsh.SendKeys(self.txtBlink.toPlainText())
                        for t in range(36, 48, 1):
                            cv2.circle(frame, (shape[t][0], shape[t][1]), 2, (255, 0, 0), -1)
                
                    if 0 <= gesture_output <= 4:
                        gesture_arr = deque(maxlen=15)
                        gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
                        print(gesture_output)
                        
                    """
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
        loadUi('interface/fr.ui', self)
        
        # Load default settings
        self.value_changed()
        
        # Load previous state settings from file
        print("Checking for state settings...")
        state_settings_path = app_dir + '/state_settings.json'
        self.load_settings(state_settings_path)  # Load the last settings that were used
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

        # Checkboxes
        self.cboxOpenMouth.stateChanged.connect(lambda: self.btn_state(self.cboxOpenMouth))
        self.cboxRaiseEyebrows.stateChanged.connect(lambda: self.btn_state(self.cboxRaiseEyebrows))
        self.cboxSmile.stateChanged.connect(lambda: self.btn_state(self.cboxSmile))
        self.cboxSnarl.stateChanged.connect(lambda: self.btn_state(self.cboxSnarl))
        self.cboxBlink.stateChanged.connect(lambda: self.btn_state(self.cboxBlink))
        
        # Buttons
        self.btnInitialize.setToolTip('Toggle Gesture Detection ON/OFF')
        self.btnInitialize.clicked.connect(self.on_click_initialize)
        self.btnSave.setToolTip('Save Settings')		
        self.btnSave.clicked.connect(lambda: self.btn_save_settings(self.txtOpenMouth.toPlainText(),
                                                                    self.txtRaiseEyebrows.toPlainText(),
                                                                    self.txtSmile.toPlainText(),
                                                                    self.txtSnarl.toPlainText(),
                                                                    self.txtBlink.toPlainText(),
                                                                    self.open_mouth_var,
                                                                    self.raise_eyebrows_var,
                                                                    self.smile_var,
                                                                    self.snarl_var,
                                                                    self.blink_var))
        self.btnLoad.setToolTip('Load Settings')
        self.btnLoad.clicked.connect(lambda: self.btn_load_settings())
        self.btnCalibrate.clicked.connect(lambda: self.btn_calibrate(self.facial_landmarks, self.base_line))

        # sliders
        self.sliderOpenMouth.valueChanged.connect(lambda: self.value_changed())
        self.sliderRaiseEyebrows.valueChanged.connect(lambda: self.value_changed())
        self.sliderSmile.valueChanged.connect(lambda: self.value_changed())
        self.sliderSnarl.valueChanged.connect(lambda: self.value_changed())
        self.sliderBlink.valueChanged.connect(lambda: self.value_changed())
        
        # webcam
        self.webcam.setText("Webcam")
        self.show()

    def btn_calibrate(self, neutral_landmarks, base_line):
        self.neutral_landmarks = neutral_landmarks
        self.base_line = base_line
        
        if self.faceShapePredictorActivated:
            #print(self.neutral_landmarks.shape)
            
            # Calculate facial feture distance ratios for the users neutral face
            # Closed mouth ratio
            self.neutral_open_mouth = self.neutral_landmarks[66][1] - self.neutral_landmarks[62][1]
            self.neutral_open_mouth /= base_line
            print("closed mouth:", self.neutral_open_mouth)
            # Normal eyebrow height ratio
            self.neutral_raise_eyebrows = (self.neutral_landmarks[27][1]) - (((self.neutral_landmarks[19][1]) + (self.neutral_landmarks[24][1]))/2)
            self.neutral_raise_eyebrows /= base_line
            print("eyebrows:", self.neutral_raise_eyebrows)
            # Normal mouth width ratio
            self.neutral_smile = (((self.neutral_landmarks[54][0]) + (self.neutral_landmarks[64][0]))/2) - (((self.neutral_landmarks[48][0]) + (self.neutral_landmarks[60][0]))/2)
            self.neutral_smile /= base_line
            # Normal non frown/snarl ratio
            self.neutral_snarl = (((self.neutral_landmarks[31][1]) + (self.neutral_landmarks[35][1]))/2) - (((self.neutral_landmarks[21][1]) + (self.neutral_landmarks[22][1]))/2)
            self.neutral_snarl /= base_line
            # Normal eye height ratio
            eyelid_top = ((self.neutral_landmarks[37][1]) + (self.neutral_landmarks[38][1]) + (self.neutral_landmarks[43][1]) + (self.neutral_landmarks[44][1]))/4
            eyelid_bottom = ((self.neutral_landmarks[40][1]) + (self.neutral_landmarks[41][1]) + (self.neutral_landmarks[46][1]) + (self.neutral_landmarks[47][1]))/4
            self.neutral_blink = eyelid_bottom - eyelid_top
            self.neutral_blink /= base_line
            
            # Fill the dictionary with the new calibration
            self.neutral_gesture_vars = {'0': self.neutral_open_mouth,
                                    '1': self.neutral_raise_eyebrows,
                                    '2': self.neutral_smile,
                                    '3': self.neutral_snarl,
                                    '4': self.neutral_blink,
                                    }
            
        else:
            print("Must be activated")

    def value_changed(self):
        self.open_mouth_var = round(float(self.sliderOpenMouth.value()) / 277, 2)
        self.raise_eyebrows_var = round(float(self.sliderRaiseEyebrows.value()) / 250, 2)
        self.smile_var = round(float(self.sliderSmile.value()) / 166, 2)
        self.snarl_var = round(float(self.sliderSnarl.value()) / 141, 3)
        self.blink_var = round(float(self.sliderBlink.value()) / 1000, 3)
    
        self.lblOpenMouthT.setText(str(self.open_mouth_var))
        self.lblRaiseEyebrowsT.setText(str(self.raise_eyebrows_var))
        self.lblSmileT.setText(str(self.smile_var))
        self.lblSnarlT.setText(str(self.snarl_var))
        self.lblBlinkT.setText(str(self.blink_var))
    
    def save_state(self, openMouthTxt, raiseEyebrowsTxt, smileTxt, snarlTxt, blinkTxt, open_mouth_var, raise_eyebrows_var, smile_var, snarl_var, blink_var):
        openMouthKey = openMouthTxt
        raiseEyebrowsKey = raiseEyebrowsTxt
        smileKey = smileTxt
        snarlKey = snarlTxt
        blinkKey = blinkTxt
        openMouth = open_mouth_var
        raiseEyebrows = raise_eyebrows_var
        smile = smile_var
        snarl = snarl_var
        blink = blink_var
        data = {'openMouthKey': openMouthKey,
                'raiseEyebrowsKey': raiseEyebrowsKey,
                'smileKey': smileKey,
                'snarlKey': snarlKey,
                'blinkKey': blinkKey,
                'open_mouth_var': openMouth,
                'raise_eyebrows_var': raiseEyebrows,
                'smile_var': smile,
                'snarl_var': snarl,
                'blink_var': blink
                }
        
        filepathwithextension = app_dir + '/state_settings.json'
        with open(filepathwithextension, 'w') as f:
            json.dump(data, f)
    
    def save_settings(self, path, fileName, data):
        filepathwithextension = path + '/' + fileName + '.json'
        with open(filepathwithextension, 'w') as f:
            json.dump(data, f)
        print("Settings file: '" + filepathwithextension + "' saved successfully!")
        
    def btn_save_settings(self, openMouthTxt, raiseEyebrowsTxt, smileTxt, snarlTxt, blinkTxt, open_mouth_var, raise_eyebrows_var, smile_var, snarl_var, blink_var):
        openMouthKey = openMouthTxt
        raiseEyebrowsKey = raiseEyebrowsTxt
        smileKey = smileTxt
        snarlKey = snarlTxt
        blinkKey = blinkTxt
        openMouth = open_mouth_var
        raiseEyebrows = raise_eyebrows_var
        smile = smile_var
        snarl = snarl_var
        blink = blink_var
        data_to_save = {'openMouthKey': openMouthKey, 'raiseEyebrowsKey': raiseEyebrowsKey, 'smileKey': smileKey,
                        'snarlKey': snarlKey, 'blinkKey': blinkKey, 'open_mouth_var': openMouth,
                        'raise_eyebrows_var': raiseEyebrows, 'smile_var': smile, 'snarl_var': snarl, 'blink_var': blink
                        }
        name, ok = QInputDialog.getText(self, 'Save Settings', 'Enter your name:')
        
        if ok and name != '':
            self.save_settings(app_dir, name, data_to_save)
    
    def load_settings(self, fileName):
        data = {}
        name = fileName
        try:
            with open(name, 'r') as f:
                data = json.load(f)
                self.txtOpenMouth.setPlainText(str(data['openMouthKey']))
                self.txtRaiseEyebrows.setPlainText(str(data['raiseEyebrowsKey']))
                self.txtSmile.setPlainText(str(data['smileKey']))
                self.txtSnarl.setPlainText(str(data['snarlKey']))
                self.txtBlink.setPlainText(str(data['blinkKey']))
                self.sliderOpenMouth.setValue(int(data['open_mouth_var']*277))
                self.sliderRaiseEyebrows.setValue(int(data['raise_eyebrows_var']*250))
                self.sliderSmile.setValue(int(data['smile_var']*166))
                self.sliderSnarl.setValue(int(data['snarl_var']*141))
                self.sliderBlink.setValue(int(data['blink_var']*1000))
                self.value_changed()
                print("Settings file: '" + name + "' loaded successfully!")
        except:
            print("Settings file: '" + name + "' not found!")
    
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
        # blink checkbox
        if state.objectName() == "cboxBlink":
            if state.isChecked():
                if not self.blinkActivated:
                    print("Blink detection activated")
                    self.blinkActivated = True
            else:
                self.blinkActivated = False
                print("Blink detection deactivated")

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

    def warningbox(self):
        pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Save the settings before exiting
            print("Saving state settings...")
            self.save_state(self.txtOpenMouth.toPlainText(), self.txtRaiseEyebrows.toPlainText(),
                            self.txtSmile.toPlainText(), self.txtSnarl.toPlainText(),
                            self.txtBlink.toPlainText(), self.open_mouth_var, self.raise_eyebrows_var,
                            self.smile_var, self.snarl_var, self.blink_var)
            print("State settings saved successfully!")
            self.webcamActive = False
            event.accept()
        else:
            event.ignore()


app = QApplication(sys.argv)
widget = App()
widget.show()
print("Now exiting")
sys.exit()
