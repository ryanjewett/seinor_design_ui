
import sys
import os
import json
import glob
import time
import datetime
import requests
import numpy as np
from PySide6 import  QtWidgets
from PySide6.QtGui import QFont, QPixmap 
from PySide6.QtCore import QObject, Qt, QDate, QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication,QLineEdit,QWidget,QFormLayout,QVBoxLayout,QSpacerItem,QSizePolicy,QMessageBox,QPushButton,QLabel,QDateEdit,QHBoxLayout
from backgroundfunction import loginCredValidation, registerNewUser,connectToServer, retriveDataChunk
from blenderhandler import startingUpBlendThread, startSimThread, stopBlendSim


class ConnectThread(QThread):
    connection_result = Signal(bool) 
    def run(self):
        connectvalidation = connectToServer()
        self.connection_result.emit(connectvalidation)  

class runSim(QThread):
    def __init__(self, source,status):
        super().__init__()
        self.source = source
        self.irt = 0
        self.status = status
        self.base_url = "http://127.0.0.1:5000"

    def updateData(self):
        try:
            now = datetime.datetime.now()
            current_date = now.date()
            current_time = now.strftime("%H:%M:%S")
            time.sleep(1)
            data = None

            if self.source == 'real_time':
                try:
                    #response = requests.get(f"{self.base_url}/ret/real_data/2024-10-10/10:10:10/")
                    response = requests.get(f"{self.base_url}/ret/real_data/2024-10-10/10:10:10/")
                    response.raise_for_status()
                    data = response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    return False
            elif self.source == 'saved_data':
                try:
                    with open('tempfile.json', 'r') as f:
                        saved_data = json.load(f)
                        if self.irt < len(saved_data):
                            data = saved_data[self.irt]
                        else:
                            return False
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"File error: {e}")
                    return False

            if data is not None:
                try:
                    with open('tempdata.json', 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    print(f"Failed to write data: {e}")
                    return False

            return True
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}")
            return False

    def run(self):
        self.irt = 0
        while self.status:
            if not self.updateData():
                break
            self.irt += 1
            time.sleep(1)
    
class connectServerWindow(QtWidgets.QTabWidget):

    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.conntingText = QtWidgets.QLabel("Connecting...")
        self.failedText = QtWidgets.QLabel("Failed To Connect To Server :(")

        self.retrybutton = QtWidgets.QPushButton("Retry")
        self.retrybutton.setMaximumSize(200,100)
        self.retrybutton.clicked.connect(self.retryConnect)
        self.conntingText.setVisible(True)
        self.retrybutton.setVisible(False)
        self.failedText.setVisible(False)

        flo = QFormLayout()
        flo.addRow(self.conntingText)
        flo.addRow(self.failedText)
        flo.addRow(self.retrybutton)

        centerbox = QVBoxLayout()
        centerbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        centerbox.addLayout(flo)
        centerbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        centerbox.setAlignment(flo, Qt.AlignCenter)
        self.setLayout(centerbox)

        self.connectThread = ConnectThread()
        self.connectThread.connection_result.connect(self.onConnectionResult)
        self.connectThread.start()  

    def retryConnect(self):
        self.connectingVisablity()
        self.connectThread.start()  

    def connectingVisablity(self):
        self.conntingText.setVisible(True)
        self.failedText.setVisible(False)
        self.retrybutton.setVisible(False)

    def retryConnectVisablitly(self):
        self.failedText.setVisible(True)
        self.retrybutton.setVisible(True)
        self.conntingText.setVisible(False)

    def onConnectionResult(self, connectvalidation):
        if connectvalidation:
            self.mainWindow.showLoginWindow()
        else:
            self.retryConnectVisablitly()

class loginWindow(QtWidgets.QTabWidget):

    def __init__(self,mainWindow):

        super().__init__()

        self.setWindowTitle("Login Window")
        self.mainWindow = mainWindow
        
        self.setMaximumSize(800,600)
        self.setMinimumSize(800,600)
        self.resize(800,600)

        self.username = QLineEdit()
        self.username.setMaxLength(12)
        self.username.setFont(QFont("Times New Roman",20))

        self.password = QLineEdit()
        self.password.setMaxLength(12)
        self.password.setEchoMode(QLineEdit.Password)

        self.submitButton = QtWidgets.QPushButton("Login")
        self.submitButton.clicked.connect(self.loginValidation)

        self.registerButton = QtWidgets.QPushButton("Register")
        self.registerButton.clicked.connect(self.registerUser)

        self.failedtext = QtWidgets.QLabel("Failed Login or Register")
        self.failedtext.setVisible(False)

        flo = QFormLayout()
        flo.addWidget(self.failedtext)
        flo.addRow("Username",self.username)
        flo.addRow("Password",self.password)
        flo.addWidget(self.submitButton)
        flo.addWidget(self.registerButton)
        
        self.central_layout = QVBoxLayout()
        self.central_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.central_layout.addLayout(flo)
        self.central_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.central_layout.setAlignment(flo, Qt.AlignCenter)
        self.setLayout(self.central_layout)

    def loginValidation(self):
        usernameTxt = self.username.text()
        passwordTxt = self.password.text()
        validation = loginCredValidation(username=usernameTxt, password=passwordTxt)
        if validation == True:
            self.mainWindow.showUserDash()
        else:
            self.failedLogin()
    
    def registerUser(self):
        usernameTxt = self.username.text()
        passwordTxt = self.password.text()
        validation = registerNewUser(username=usernameTxt,password=passwordTxt)
        if validation == True:
            self.mainWindow.showUserDash()
        else:
            self.failedLogin()
        
    
    def failedLogin(self):
        self.username.clear()
        self.password.clear()

        self.failedtext.setVisible(True)

class userDash(QWidget):

    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        
        self.mainLayout = QHBoxLayout()
        
        self.buttonLayout = QVBoxLayout()

        self.welcomeLabel = QLabel("Welcome to the User Dashboard")
        self.welcomeLabel.setAlignment(Qt.AlignCenter)
        self.buttonLayout.addWidget(self.welcomeLabel)

        self.buttonLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.signOutButton = QPushButton("Sign Out")
        self.signOutButton.setMaximumSize(200,100)
        self.signOutButton.clicked.connect(self.signOut)
        self.buttonLayout.addWidget(self.signOutButton)

        self.retrieveDataButton = QPushButton("Retrieve Past Data")
        self.retrieveDataButton.setMaximumSize(200,100)
        self.retrieveDataButton.clicked.connect(self.retrievePastData)
        self.buttonLayout.addWidget(self.retrieveDataButton)

        self.realTimeButton = QPushButton("See Real-Time Data")
        self.realTimeButton.setMaximumSize(200,100)
        self.realTimeButton.clicked.connect(self.viewRealTimeData)
        self.buttonLayout.addWidget(self.realTimeButton)

        self.manageAlertsButton = QPushButton("Manage Alerts")
        self.manageAlertsButton.setMaximumSize(200,100)
        self.manageAlertsButton.clicked.connect(self.manageAlerts)
        self.buttonLayout.addWidget(self.manageAlertsButton)

        self.calibrateButton = QPushButton("Calibrate")
        self.calibrateButton.setMaximumSize(200,100)
        self.calibrateButton.clicked.connect(self.calibrate)
        self.buttonLayout.addWidget(self.calibrateButton)

        self.downloadDataButton = QPushButton("Download Data")
        self.downloadDataButton.setMaximumSize(200,100)
        self.downloadDataButton.clicked.connect(self.downloadData)
        self.buttonLayout.addWidget(self.downloadDataButton)

        self.buttonLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.mainLayout.addLayout(self.buttonLayout)

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        
        pixmap = QPixmap("/Users/ryanjewett/Documents/CPE4850/background.png")  
        self.imageLabel.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        
        self.mainLayout.addWidget(self.imageLabel)

        self.setLayout(self.mainLayout)

    def signOut(self):
        self.mainWindow.showLoginWindow()

    def retrievePastData(self):
        self.mainWindow.retivePastDataWindow()

    def viewRealTimeData(self):
        self.mainWindow.showBlendWindow()

    def manageAlerts(self):
        self.mainWindow.showManageAlertWindow()

    def calibrate(self):
        self.mainWindow.showCalibrationWindow()

    def downloadData(self):
        self.mainWindow.showDownloadWindow()

class retrievePastDataWindow(QWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow  

        self.mainLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()

        self.retiveSuccessText = QLabel("Data Retrieved Successfully")
        self.retiveSuccessText.setAlignment(Qt.AlignCenter)
        self.retiveSuccessText.setVisible(False)

        self.retiveFailedText = QLabel("Data Retrieval Failed")
        self.retiveFailedText.setAlignment(Qt.AlignCenter)
        self.retiveFailedText.setVisible(False)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.goBack)
        self.topLayout.addWidget(self.backButton)
        self.topLayout.addStretch()

        self.mainLayout.addLayout(self.topLayout)

        self.titleLabel = QLabel("Select Date Range to Retrieve Past Data")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.titleLabel)

        self.startDateLabel = QLabel("Start Date:")
        self.startDateEdit = QDateEdit()
        self.startDateEdit.setCalendarPopup(True)
        self.startDateEdit.setDate(QDate.currentDate())
        self.endDateLabel = QLabel("End Date:")
        self.endDateEdit = QDateEdit()
        self.endDateEdit.setCalendarPopup(True)
        self.endDateEdit.setDate(QDate.currentDate())

        dateLayout = QHBoxLayout()
        dateLayout.addWidget(self.startDateLabel)
        dateLayout.addWidget(self.startDateEdit)
        dateLayout.addWidget(self.endDateLabel)
        dateLayout.addWidget(self.endDateEdit)
        self.mainLayout.addLayout(dateLayout)

        self.submitButton = QPushButton("Retrieve Data")
        self.submitButton.clicked.connect(self.retrieveData)
        self.mainLayout.addWidget(self.submitButton)

        self.mainLayout.addWidget(self.retiveSuccessText)
        self.mainLayout.addWidget(self.retiveFailedText)

        self.mainLayout.addStretch()

        self.setLayout(self.mainLayout)

    def goBack(self):
        if  not (self.retiveFailedText.isVisible() or self.retiveSuccessText.isVisible()):
            self.mainWindow.showUserDash()
        else:
            self.backButton.setVisible(True)
            self.retiveSuccessText.setVisible(False)
            self.retiveFailedText.setVisible(False)
            self.submitButton.setVisible(True)
            self.startDateEdit.setVisible(True)
            self.endDateEdit.setVisible(True)
            self.startDateLabel.setVisible(True)
            self.endDateLabel.setVisible(True)
            self.titleLabel.setVisible(True)

    def retrieveData(self):
        startDate = self.startDateEdit.date()
        endDate = self.endDateEdit.date()

        startDateReForm = startDate.toPython()
        endDateReForm = endDate.toPython()
        print(f"startdate:{startDateReForm},enddate:{endDateReForm} ")

        val = retriveDataChunk(str(startDateReForm), str(endDateReForm))

        if val == True:
            self.successDataRet()
        else:
            self.failedDataRet()

    def successDataRet(self):
        
        self.submitButton.setVisible(False)
        self.startDateEdit.setVisible(False)
        self.endDateEdit.setVisible(False)
        self.startDateLabel.setVisible(False)
        self.endDateLabel.setVisible(False)
        self.titleLabel.setVisible(False)

        self.retiveSuccessText.setVisible(True)

    def failedDataRet(self):
        
        self.submitButton.setVisible(False)
        self.startDateEdit.setVisible(False)
        self.endDateEdit.setVisible(False)
        self.startDateLabel.setVisible(False)
        self.endDateLabel.setVisible(False)
        self.titleLabel.setVisible(False)
        self.backButton.setVisible(False)

        self.retiveFailedText.setVisible(True)

        QTimer.singleShot(3000, self.goBack)

class realTimeModelWindow(QWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.runningsim = True

        self.pathToTempFolder= "/Users/ryanjewett/Documents/CPE4850/SAVE_HERE"

        self.newestFile = "/Users/ryanjewett/Documents/CPE4850/exported_jpeg.jpeg"
        self.fallbackImage = "/Users/ryanjewett/Documents/CPE4850/exported_jpeg.jpeg"

        self.mode = 'real_time'
        self.currentMesh = None
        self.mainWindow = mainWindow

        self.simThread = runSim(self.mode,status=True)
        
        self.topLayout = QHBoxLayout()
        self.mainLayout = QVBoxLayout()

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.goBack)
        self.topLayout.addWidget(self.backButton)

        #self.startModel = QPushButton("Start Blender")
        #self.startModel.clicked.connect(self.startBlenderModel)
        #self.topLayout.addWidget(self.startModel)

        self.startSimButton = QPushButton("Start Sim")
        self.startSimButton.clicked.connect(self.startSim)
        self.topLayout.addWidget(self.startSimButton)

        self.stopSimButton = QPushButton("Stop Sim")
        self.stopSimButton.clicked.connect(self.stopSim)
        self.topLayout.addWidget(self.stopSimButton)

        self.realTimeButton = QPushButton("Real-Time Mode")
        self.realTimeButton.clicked.connect(self.realTimeMode)
        self.topLayout.addWidget(self.realTimeButton)

        self.savedDataButton = QPushButton("Saved Data Mode")
        self.savedDataButton.clicked.connect(self.savedDataMode)
        self.topLayout.addWidget(self.savedDataButton)

        self.mainLayout.addLayout(self.topLayout)

        self.imageLabel = QLabel(self)
        self.mainLayout.addWidget(self.imageLabel)

        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.loadJPEG)  

        self.setLayout(self.mainLayout)

    def loadJPEG(self):
        jpeg_files = glob.glob(os.path.join(self.pathToTempFolder, '*.jpg'))
        if jpeg_files:
            self.newestFile = max(jpeg_files, key=os.path.getmtime)
            print("Newest JPEG file:", self.newestFile)
        else:
            print("No JPEG files found.")
            self.newestFile = self.fallbackImage

        pixmap = QPixmap(self.newestFile)  
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)  
        self.imageLabel.adjustSize()

    def goBack(self):
        self.mainWindow.showUserDash()

    def startBlenderModel(self):
        #val = startingUpBlendThread()
        #print(val)
        print("how are you even here")

    def startSim(self):
        #startSimThread(self.mode)
        self.simThread.start()
        self.timer.start(1000)

    def realTimeMode(self):
        self.mode = 'real_time'

    def savedDataMode(self):
        self.mode = 'saved_data'

    def stopSim(self):
        self.runningsim = False
        #stopBlendSim()
        self.simThread.terminate()
        self.timer.stop()

class manageAlertWindow(QWidget):
    def __init__(self,mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

class calibrationWindow(QWidget):
    def __init__(self,mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

class dataDownloadWindow(QWidget):
    def __init__(self,mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.showConnectionWindow()

    def showConnectionWindow(self):
        self.connectwindow = connectServerWindow(self)
        self.setCentralWidget(self.connectwindow)
        self.setWindowTitle("Connection Window")
        self.setFixedSize(800, 600)

    def showLoginWindow(self):
        self.loginwindow = loginWindow(self)
        self.setCentralWidget(self.loginwindow)
        self.setWindowTitle("Login Window")
        self.setFixedSize(800, 600)
        self.loginwindow.update()
    
    def showUserDash(self):
        self.userdash = userDash(self)
        self.setCentralWidget(self.userdash)
        self.setWindowTitle("User Dash")
        self.setFixedSize(800,600)
        self.userdash.update()

    def retivePastDataWindow(self):
        self.retivepastdataselect = retrievePastDataWindow(self)
        self.setCentralWidget(self.retivepastdataselect)
        self.setWindowTitle("Date Select")
        self.setFixedSize(800,600)
        self.retivepastdataselect.update()

    def showBlendWindow(self):
        self.realtimewindow = realTimeModelWindow(self)
        self.setCentralWidget(self.realtimewindow)
        self.setWindowTitle("3D Model")
        self.setFixedSize(800,600)
        self.realtimewindow.update()
    
    def showManageAlertWindow(self):
        self.managealert = manageAlertWindow(self)
        self.setCentralWidget(self.managealert)
        self.setWindowTitle("Manage Alert")
        self.setFixedSize(800,600)
        self.managealert.update()
    
    def showCalibrationWindow(self):
        self.calibrationcontrol = calibrationWindow(self)
        self.setCentralWidget(self.calibrationcontrol)
        self.setWindowTitle("Calibration Control")
        self.setFixedSize(800,600)
        self.calibrationcontrol.update()

    def showDataDownloadWindow(self):
        self.datadownload = dataDownloadWindow(self)
        self.setCentralWidget(self.datadownload)
        self.setWindowTitle("Data Download")
        self.setFixedSize(800,600)
        self.datadownload.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec())
    