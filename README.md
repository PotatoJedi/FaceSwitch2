# fr
Authors: Sione Manulea, Joshua Clarke
- Python version: 3.6.7

This software was created by students at the Otago Polytechnic for our Project 1 & 2 papers in the BIT degree. It is a prototype demo of software that has the potential to allow physically impaired individuals to use a personal computer via facial gestures.

For example they could map a keystroke to the "open mouth" gesture. This would mean that while running the software, they could open their mouth and the keystroke of their choosing would be sent to the computer by the software, rather than by the keyboard.

# Installation instructions

#### You will need to have a physical webcam to use this software.

### 1. Git [ If you have Git software installed, you can skip this section ]
* Download Git for your operating system here: https://git-scm.com/downloads
* Once it's downloaded, you need to open the Git.exe file you downloaded.

#### Here is a step by step guide for how to install git correctly.

1. GNU General Public License -> Click Next 
2. Selection Destination Location -> Nothing to change here, click Next
3. Select Components -> Nothing to change here, click Next
4. Select Start Menu Folder -> Nothing to change here, click Next
5. Choosing the default editor used by Git -> Unless your a professional, click Next
6. Adjusting your PATH environment -> Again, unless you know what you're doing or your a wizard, click Next
7. Choosing HTTPS transport backend -> click Next
8. Configuring the line ending conversions -> click Next
9. Configuring the terminal emulator to use with Git Bash -> click Next
10. Configuring extra options -> click Next
11. Configuring experimental options -> click Next
12. Click Install
13. Completing the Git Setup Wizard -> Make sure "Launch Git Bash" is checked, and then click Finish

### A wild prompt should appear (if it doesn't, then click the start menu, and while the start menu is active type "Git Bash" and click the Git Bash app)

Once the command prompt is open, click anywhere in the black box to type these commands in to:

1. mkdir fr
2. cd fr
3. git clone https://github.com/manulea/MITGUI

If the commands are successful you should beable to see "Cloning into 'MITGUI'" in your command prompt.

You can now close this window. 

### 2. Anaconda Distribution [ If you have anaconda interpreter installed, you can skip this section ]
* Go to the Anaconda website to install the Anaconda Distribution: https://www.anaconda.com/distribution/
* Scroll down a bit until you see Windows, Mac or Linux.
* Choose the operating system that you are installing this software on.
* Under Python 3.7 version, you will need to download the "Graphical installer".

For windows: if you don't know if you're 64 bit or 32 bit here is a guide: https://www.lifewire.com/am-i-running-a-32-bit-or-64-bit-version-of-windows-2624475

* Click Save File

* Run the Anaconda3-2019.07-Windows-x86_64 file that you just saved to your computer. Mine was saved under my Downloads directory.

1. Click Next
2. Read License Agreement, then click I Agree
3. Make sure [Just Me (recommended)] is checked, then click Next 
4. Destionation folder should be: C:\Users\user\Anaconda3, or something similar, click Next
5. Make sure Register Anaconda as my default Python 3.7 is checked, then click Install
6. Click Next on the Installation Complete menu
7. Click Next
8. Uncheck both boxes, unless you are curious.
9. Click Finish.

Congratulations, you should now have Anaconda installed!

### 3. Preparing anaconda

Once anaconda is installed, open Anaconda Prompt by clicking on the start menu, and while the start menu is active, type in 
anaconda prompt, then press enter.

While the anaconda prompt is open, click anywhere in the black box and then follow these instructions:

1. Type: "conda update conda" without the quotation marks, then press the Enter key.
2. Wait until you see "Proceed <[y]/n>?" 
3. Type: "y" without the quotaton marks, then press the Enter key to proceed.

4. Wait until you are back at <base> C:\Users\user>_ 

5. Type: "conda install python=3.6.7" without the quotation marks, then press enter on your keyboard.
6. Wait until you see "Proceed <[y]/n>?" 
7. Type: "y" without the quotaton marks, then press the Enter key to confirm.
9. Your Prompt should now be downloading all the packages.
8. Wait until you are back at <base> C:\Users\user>_ 

You are now ready to run the Face Recognition software.

### 4. Running the software

Using the Anaconda prompt, follow these instructions:

1. Type: "cd fr" without the quotation marks, then press the Enter key on your keyboard.
2. Type: "cd MITGUI" without the quotation marks, then press the Enter key on your keyboard.
3. You should now be in <base> C:\Users\user\fr\MITGUI> 
4. Type "pip install pipenv" without the quotation marks, then press Enter key on your keyboard.
5. Wait until you see Successfully installed pipenv-2018.11.26
6. Run pipenv shell by typing: "pipenv shell" in to the command prompt without the quotation marks, then send the instruction to the computer by pressing the Enter key on your keyboard.
7. You should now be in the virtual environment if you see <MITGUI-*****> <base> C:\Users\user\fr\MITGUI>
8. Type: "pipenv sync" without the quotation marks, then press Enter key on your keyboard.
9. This will take a while.
10. Type: "python fr.py" in to the command prompt without the quotation marks, then press Enter on your keyboard.

### 5. How to use the software
-- Under Construction --


# Download the windows app! #

[Click here to download](https://github.com/manulea/MITGUI/releases/download/v3.0/fr.exe)

![Image0](https://i.imgur.com/blbhQhH.png)

Click Save File

![Image1](https://i.imgur.com/rpf0os7.png)

Find where you saved this file, and double click it!

![Image1.2](https://i.imgur.com/6l91vx4.png)

You may have a security issue.. if this is the case then:

click More info.

![Image1.3](https://i.imgur.com/5kd2qkR.png)

Click Run anyway

#### A windows security prompt should come up, press yes. 

![Image2](https://i.imgur.com/UO40SxR.png)

Choose your destination folder or leave it default.

Click Install

![Image3](https://i.imgur.com/Wpps3uU.png)

Wait for the download to complete.

![Image4](https://i.imgur.com/n74RUUd.png)

Click Close.

![Image5](https://i.imgur.com/CiqcXxO.png)

A new folder is created.

Double click the folder to open the folder.

![Image6](https://i.imgur.com/rYDgYJy.png)

Locate a file named fr.exe and double click it.

![Image7](https://i.imgur.com/wqhjJ5k.png)

A command prompt should start running the scripts.

![Image8](https://i.imgur.com/VuyW4Ap.png)

If everything is successful, the user interface should appear like this on the screen.

# A special thanks to the following creators of these Libraries:
* [PyQt5 5.13.0](https://pypi.org/project/PyQt5/)
* [dlib 19.17.0](https://pypi.org/project/dlib/)
* [opencv-python 4.1.0.25](https://pypi.org/project/opencv-python/)
* [imutils 0.5.2](https://pypi.org/project/imutils/)
* [numpy 1.17.0 ](https://pypi.org/project/numpy/)
* [pywin32 224](https://pypi.org/project/pywin32/)
* [pygame 1.9.6](https://pypi.org/project/pygame/)
