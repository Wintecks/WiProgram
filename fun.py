import os

base_path = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/"
base_path2 = "C:/Users/winte/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/"

def OBS():
    os.startfile(base_path+"OBS Studio")

def Driver():
    os.startfile("D:/")

def Chrome():
    os.startfile(base_path+"Google Chrome")

def PaintNET():
    os.startfile(base_path+"PaintNET")

def IriunWebcam():
    os.startfile(base_path+"Iriun Webcam/Iriun Webcam")

def PrismLauncher():
    os.startfile(base_path2+"Prism Launcher")
    
def YouTubeMusic():
    os.startfile(base_path2+"Додатки Chrome/YouTube Music")

def VSCode():
    os.startfile(base_path2+"Visual Studio Code/Visual Studio Code")