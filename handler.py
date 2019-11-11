#CURRENT VERSION
import win32com.client as comclt
self.wsh = comclt.Dispatch("WScript.Shell")

self.wsh.SendKeys(text)

#VERSION 2
from pynput.keyboard import Key, Controller
self.keyboard = Controller()

self.keyboard.press(Key.f12)
self.keyboard.release(Key.f12)