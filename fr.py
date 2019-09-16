import sys 
from PyQt5.uic import loadUi

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QCheckBox, QWidget, QPushButton, QLabel, QPlainTextEdit, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QFile, QTextStream
from imutils import face_utils
import numpy as np
from collections import deque
import cv2
import dlib
# Used to insert keys
import win32com.client as comclt
import os
import pygame
#import psutil
import time
import tkinter
from tkinter import filedialog

import json # for saving/loading settings

class App(QDialog):
	def __init__(self):
		super(App, self).__init__()
		self.title = 'Face Switch 2.0'
		self.closeEvent = self.closeEvent
		#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setWindowIcon(QtGui.QIcon('interface\icon.png'))
		
		self.captureFacePositions = True
		self.capturedPositions = False
		self.faceShapePredictorActivated = False
		
		self.count = 0
		self.webcamActive = True
		
		# gives an error without CAP_DSHOW
		
		self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		
		pygame.init()
		
		self.initUI()
		
		self.smileActivated = False
		self.openMouthActivated = False
		self.raiseEyebrowsActivated = False
		self.snarlActivated = False
		self.blinkActivated = False
		
		# Open keytyper
		
		self.wsh = comclt.Dispatch("WScript.Shell")

		self.center()
		self.oldPos = self.pos()
		self.landmarks()
		
		self.openMouthVar = 0
		self.raiseEyebrowsVar = 0
		self.smileVar = 0
		self.snarlVar = 0
		self.blinkVar = 0

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
		# p = our pre-treined model directory, on my case, it's on the same script's directory.
		p = "resources\shape_predictor_68_face_landmarks.dat"
		
		detector = dlib.get_frontal_face_detector()
		predictor = dlib.shape_predictor(p)

		gesture_arr = deque(maxlen=15)
		gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
		
		while self.webcamActive == True:
			# Getting out image by webcam 
			_, frame = self.cap.read()
			# Converting the image to gray scale
			if(frame is not None):
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				# Get faces into webcam's image
				rects = detector(gray, 0)
			else:
				print("Error connecting to webcam! Exiting...")
				sys.exit()
			#start_time = time.time() # start time of the loop
			
			# Activated
			if (self.faceShapePredictorActivated == True):
				for (i, rect) in enumerate(rects):
				
					start_time = time.time() # start time of the loop
					
					# Make the prediction and transfom it to numpy array
					shape = predictor(gray, rect)
					shape = face_utils.shape_to_np(shape)
					
					# Green
					for (x, y) in shape:
						cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
					# Recognise gestures
					
					# Baseline
					base_line = ((shape[16][0]) - (shape[0][0]))
					
					# Open mouth
					if (self.openMouthActivated == True):
						mouth_top = ((shape[61][1]) + (shape[62][1]) + (shape[63][1]))/3
						mouth_bottom = ((shape[65][1]) + (shape[66][1]) + (shape[67][1]))/3
						mouth_height = mouth_bottom - mouth_top
						try:
							if(mouth_height/base_line > float(self.openMouthVar)):
								gesture_arr.append(0)
						except:
							pass
					# Raise Eyebrow
					if (self.raiseEyebrowsActivated == True):
						eye_top = ((shape[18][1]) + (shape[19][1]) + (shape[20][1]) + (shape[23][1]) + (shape[24][1]) + (shape[25][1]))/6
						eye_bottom = ((shape[27][1]) + (shape[28][1]))/2
						eye_height = eye_bottom - eye_top
						try:
							if(eye_height/base_line > float(self.raiseEyebrowsVar)):
								gesture_arr.append(1)
						except:
							pass
					# Blink
					if (self.blinkActivated == True):
						eyelid_top = ((shape[37][1]) + (shape[38][1]) + (shape[43][1]) + (shape[44][1]))/4
						eyelid_bottom = ((shape[40][1]) + (shape[41][1]) + (shape[46][1]) + (shape[47][1]))/4
						eyelid_height = eyelid_bottom - eyelid_top
						try:
							if(eyelid_height/base_line < float(self.blinkVar)):
								gesture_arr.append(2)
						except:
							pass
					# Smile
					if (self.smileActivated == True):
						mouth_left = ((shape[48][0]) + (shape[49][0]) + (shape[59][0]) + (shape[60][0]))/4
						mouth_right = ((shape[53][0]) + (shape[54][0]) + (shape[55][0]) + (shape[64][0]))/4
						mouth_width = mouth_right - mouth_left
						try:
							if(mouth_width/base_line > float(self.smileVar)):
								gesture_arr.append(3)
						except:
							pass
					# Scrunch nose
					if (self.snarlActivated == True):
						nose_top = ((shape[21][1]) + (shape[22][1]))/2
						nose_bottom = ((shape[31][1]) + (shape[35][1]))/2
						nose_height = nose_bottom - nose_top
						try:
							if(nose_height/base_line < float(self.snarlVar)):
								gesture_arr.append(4)
						except:
							pass
					
					gesture_output = -1 # Set the default value to -1 (no gesture)
					# Get the most common number (gesture) from the array and set it to be the registered gesture (eliminates noise)
					if(-1 not in gesture_arr): # Only if the array is full of gesture recognitions (i.e. no default values)
						gesture_output = max(set(gesture_arr), key=gesture_arr.count)
					
					if(gesture_output == 0):
						print("Mouth opened! - ",(mouth_height/base_line))
						self.wsh.SendKeys(self.txtOpenMouth.toPlainText())
						for i in range(60, 68, 1):
							cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
						
					elif(gesture_output == 1):
						print("Eyebrows raised! - ",(eye_height/base_line))
						self.wsh.SendKeys(self.txtRaiseEyebrows.toPlainText())
						for i in range(17, 27, 1):
							cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
						
					elif(gesture_output == 2):
						print("Eye close detected! - ",(eyelid_height/base_line))
						self.wsh.SendKeys(self.txtBlink.toPlainText())
						for i in range(36, 48, 1):
							cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
						
					elif(gesture_output == 3):
						print("Smile detected! - ",(mouth_width/base_line))
						self.wsh.SendKeys(self.txtSmile.toPlainText())
						for i in range(54, 60, 1):
							cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
						cv2.circle(frame, (shape[48][0], shape[48][1]), 2, (255, 0, 0), -1)
						
					elif(gesture_output == 4):
						print("Anger detected! - ",(nose_height/base_line))
						self.wsh.SendKeys(self.txtSnarl.toPlainText())
						for i in range(27, 36, 1):
							cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
				
					if(gesture_output == 0 or gesture_output == 1 or gesture_output == 2 or gesture_output == 3 or gesture_output == 4):
						gesture_arr = deque(maxlen=15)
						gesture_arr.extend([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
						print(gesture_output)
						
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
		
	def wait_for_key(self):
		e = pygame.event.wait()
		while e.type != pygame.KEYDOWN:
			e = pygame.event.wait()
			if e.type == pygame.QUIT:
				return pygame.K_ESCAPE
		return e.key
		
	def initUI(self):
		loadUi('interface/fr.ui',self)
		
		# self.openMouthVar = round(float(self.sliderOpenMouth.value()) / 277, 2)
		# self.raiseEyebrowsVar = round(float(self.sliderRaiseEyebrows.value()) / 251, 2)
		# self.smileVar = round(float(self.sliderSmile.value()) / 166, 2)
		# self.snarlVar = round(float(self.sliderSnarl.value()) / 141, 3)
		# self.blinkVar = round(float(self.sliderBlink.value()) / 1070, 3)
		
		self.value_changed()
		
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

		self.cboxOpenMouth.stateChanged.connect(lambda:self.btnState(self.cboxOpenMouth))
		self.cboxRaiseEyebrows.stateChanged.connect(lambda:self.btnState(self.cboxRaiseEyebrows))
		self.cboxSmile.stateChanged.connect(lambda:self.btnState(self.cboxSmile))
		self.cboxSnarl.stateChanged.connect(lambda:self.btnState(self.cboxSnarl))	
		self.cboxBlink.stateChanged.connect(lambda:self.btnState(self.cboxBlink))
		
		# Buttons
		self.btnInitialize.setToolTip('Toggle Gesture Detection ON/OFF')
		self.btnInitialize.clicked.connect(self.on_click_initialize)
		self.btnSave.setToolTip('Save Settings')		
		self.btnSave.clicked.connect(lambda:self.btn_save_settings(self.txtOpenMouth.toPlainText(), self.txtRaiseEyebrows.toPlainText(), self.txtSmile.toPlainText(), self.txtSnarl.toPlainText(), self.txtBlink.toPlainText(), self.openMouthVar, self.raiseEyebrowsVar, self.smileVar, self.snarlVar, self.blinkVar))
		self.btnLoad.setToolTip('Load Settings')
		self.btnLoad.clicked.connect(lambda:self.btn_load_settings())
		
		# Sliders
		self.sliderOpenMouth.valueChanged.connect(lambda:self.value_changed())
		self.sliderRaiseEyebrows.valueChanged.connect(lambda:self.value_changed())
		self.sliderSmile.valueChanged.connect(lambda:self.value_changed())
		self.sliderSnarl.valueChanged.connect(lambda:self.value_changed())
		self.sliderBlink.valueChanged.connect(lambda:self.value_changed())
		
		# qbtn = QPushButton('X', self)
		# qbtn.clicked.connect(self.close)
		# qbtn.resize(qbtn.sizeHint())
		# qbtn.resize(30,20)
		# qbtn.move(855, 10)
		
		# Webcam
		self.webcam.setText("Webcam")
		#self.webcam.move(10, 10)
		#self.webcam.resize(640, 480)
		self.show()

	def value_changed(self):
		self.openMouthVar = round(float(self.sliderOpenMouth.value()) / 277, 2)
		self.raiseEyebrowsVar = round(float(self.sliderRaiseEyebrows.value()) / 250, 2)
		self.smileVar = round(float(self.sliderSmile.value()) / 166, 2)
		self.snarlVar = round(float(self.sliderSnarl.value()) / 141, 3)
		self.blinkVar = round(float(self.sliderBlink.value()) / 1000, 3)

		self.lblOpenMouthT.setText(str(self.openMouthVar))
		self.lblRaiseEyebrowsT.setText(str(self.raiseEyebrowsVar))
		self.lblSmileT.setText(str(self.smileVar))
		self.lblSnarlT.setText(str(self.snarlVar))
		self.lblBlinkT.setText(str(self.blinkVar))
	
	def save_settings(self, path, fileName, data):
		filePathNameWExt = path + '/' + fileName + '.json'
		with open(filePathNameWExt, 'w') as f:
			json.dump(data, f)
		
	def btn_save_settings(self, openMouthTxt, raiseEyebrowsTxt, smileTxt, snarlTxt, blinkTxt, openMouthVar, raiseEyebrowsVar, smileVar, snarlVar, blinkVar):
		openMouthKey = openMouthTxt
		raiseEyebrowsKey = raiseEyebrowsTxt
		smileKey = smileTxt
		snarlKey = snarlTxt
		blinkKey = blinkTxt
		openMouth = openMouthVar
		raiseEyebrows = raiseEyebrowsVar
		smile = smileVar
		snarl = snarlVar
		blink = blinkVar
		data_to_save = { 'openMouthKey' : openMouthKey, 'raiseEyebrowsKey' : raiseEyebrowsKey, 'smileKey' : smileKey, 'snarlKey' : snarlKey, 'blinkKey' : blinkKey, 'openMouthVar' : openMouth, 'raiseEyebrowsVar' : raiseEyebrows, 'smileVar' : smile, 'snarlVar' : snarl, 'blinkVar' : blink }
		#print(data_to_save)
		cwd = os.getcwd()
		name, ok = QInputDialog.getText(self, 'Save Settings', 'Enter your name:')
		
		if ok and name != '':
			self.save_settings(cwd, name, data_to_save)
	
	def load_settings(self, fileName):
		data = {}
		cwd = os.getcwd()
		name = fileName
		#filePathNameWExt = cwd + '/' + name + '.json'
		filePathNameWExt = name
		try:
			with open(filePathNameWExt, 'r') as f:
				data = json.load(f)
				self.txtOpenMouth.setPlainText(str(data['openMouthKey']))
				self.txtRaiseEyebrows.setPlainText(str(data['raiseEyebrowsKey']))
				self.txtSmile.setPlainText(str(data['smileKey']))
				self.txtSnarl.setPlainText(str(data['snarlKey']))
				self.txtBlink.setPlainText(str(data['blinkKey']))
				self.sliderOpenMouth.setValue(int(data['openMouthVar']*277))
				self.sliderRaiseEyebrows.setValue(int(data['raiseEyebrowsVar']*250))
				self.sliderSmile.setValue(int(data['smileVar']*166))
				self.sliderSnarl.setValue(int(data['snarlVar']*141))
				self.sliderBlink.setValue(int(data['blinkVar']*1000))
				self.value_changed()
		except:
			print("Settings file: '" + filePathNameWExt + "' not found!")
	
	def btn_load_settings(self):
		# load tkinter
		root = tkinter.Tk()
		root.withdraw()
		
		# prepare file dialog box
		ftypes=[('json file',"*.json")]
		ttl = "Title"
		cwd = os.getcwd()
		
		# Open file dialog box
		root.fileName = filedialog.askopenfilename(filetypes=ftypes, initialdir=cwd, title=ttl)
		
		if root.fileName != '':
			self.load_settings(root.fileName)
	
	def btnState(self, state):
		# checkBox activations
		# open mouth checkbox
		if state.objectName() == "cboxOpenMouth":
			if state.isChecked() == True:
				if (self.openMouthActivated == False):
					print("Open Mouth detection activated")
					self.openMouthActivated = True
			else:
				self.openMouthActivated = False
				print("Open Mouth detection deactivated")
		# raise eyebrow checkbox
		if state.objectName() == "cboxRaiseEyebrows":
			if state.isChecked() == True:
				if (self.raiseEyebrowsActivated == False):
					print("Raise Eyebrows detection activated")
					self.raiseEyebrowsActivated = True
			else:
				self.raiseEyebrowsActivated = False
				print("Raise Eyebrows detection deactivated")
	    # smile checkbox
		if state.objectName() == "cboxSmile":
			if state.isChecked() == True:
				if (self.smileActivated == False):
					print("Smile detection activated")
					self.smileActivated = True
			else:
				self.smileActivated = False
				print("Smile detection deactivated")	
				
		# snarl checkbox
		if state.objectName() == "cboxSnarl":
			if state.isChecked() == True:
				if (self.snarlActivated == False):
					print("Snarl detection activated")
					self.snarlActivated = True
			else:
				self.snarlActivated = False
				print("Snarl detection deactivated")
		# blink checkbox
		if state.objectName() == "cboxBlink":
			if state.isChecked() == True:
				if (self.blinkActivated == False):
					print("Blink detection activated")
					self.blinkActivated = True
			else:
				self.blinkActivated = False
				print("Blink detection deactivated")
				
	@pyqtSlot()
	def on_click_initialize(self):
		if self.faceShapePredictorActivated == True:
			self.faceShapePredictorActivated = False
			self.btnInitialize.setText("Activate")
			
		elif self.faceShapePredictorActivated == False:
			self.faceShapePredictorActivated = True
			self.btnInitialize.setText("Deactivate")

	def closeEvent(self, event):
		#print("event")
		reply = QMessageBox.question(self, 'Message',
			"Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)

		if reply == QMessageBox.Yes:
			self.webcamActive = False
			event.accept()

		else:
			event.ignore()
	
app = QApplication(sys.argv)
widget = App()
widget.show()
pygame.quit()
print("Now exiting")
sys.exit()