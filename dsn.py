from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from lv import lv
from payload import payload
from threading import Thread, Lock, RLock
from configparser import ConfigParser
from PIL import Image
from PIL.ImageQt import ImageQt

import time
import zmq
import json
import base64
import numpy as np

context = zmq.Context()


vehicles = []

launches = {}
#[0]: lv obj
#[1]: lv socket
#[2]: lv tel data
#[3]: payload obj
#[4]: payload socket
#[5]: payload tel data
#[6]: payload data

launchMutex = RLock()

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        #GUI Stuff
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 558)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.lvDetails = QtWidgets.QTextEdit(self.centralwidget)
        self.lvDetails.setGeometry(QtCore.QRect(230, 10, 271, 301))
        self.lvDetails.setObjectName("lvDetails")
        self.lvDetails.setReadOnly(True)

        self.payloadDetails = QtWidgets.QTextEdit(self.centralwidget)
        self.payloadDetails.setGeometry(QtCore.QRect(510, 10, 271, 301))
        self.payloadDetails.setObjectName("payloadDetails")
        self.payloadDetails.setReadOnly(True)

        self.imgBox = QtWidgets.QLabel(self.centralwidget)
        self.imgBox.setGeometry(QtCore.QRect(510, 220, 271, 0))
        self.imgBox.setObjectName("imgBox")
        self.imgBox.setFrameShape(QtWidgets.QFrame.Box)

        self.addNewLaunchButton = QtWidgets.QPushButton(self.centralwidget)
        self.addNewLaunchButton.setGeometry(QtCore.QRect(10, 480, 113, 32))
        self.addNewLaunchButton.setObjectName("addNewLaunchButton")
        self.addNewLaunchButton.clicked.connect(self.addNewLaunch)

        self.deleteLaunchButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteLaunchButton.setGeometry(QtCore.QRect(110, 480, 113, 32))
        self.deleteLaunchButton.setObjectName("deleteLaunchButton")
        self.deleteLaunchButton.clicked.connect(self.deleteLaunch)

        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(230, 320, 271, 181))
        self.groupBox.setObjectName("groupBox")

        self.lvLaunchButton = QtWidgets.QPushButton(self.groupBox)
        self.lvLaunchButton.setGeometry(QtCore.QRect(70, 20, 131, 32))
        self.lvLaunchButton.setObjectName("lvLaunchButton")
        self.lvLaunchButton.clicked.connect(self.launchVehicle)

        self.lvStartTButton = QtWidgets.QPushButton(self.groupBox)
        self.lvStartTButton.setGeometry(QtCore.QRect(70, 50, 131, 32))
        self.lvStartTButton.setObjectName("lvStartTButton")
        self.lvStartTButton.clicked.connect(self.startTel)

        self.lvStopTButton = QtWidgets.QPushButton(self.groupBox)
        self.lvStopTButton.setGeometry(QtCore.QRect(70, 80, 131, 32))
        self.lvStopTButton.setObjectName("lvStopTButton")
        self.lvStopTButton.setEnabled(False)
        self.lvStopTButton.clicked.connect(self.stopTel)

        self.deployButton = QtWidgets.QPushButton(self.groupBox)
        self.deployButton.setGeometry(QtCore.QRect(70, 110, 131, 32))
        self.deployButton.setObjectName("deployButton")
        self.deployButton.setEnabled(False)
        self.deployButton.clicked.connect(self.deployPayload)

        self.deOrbitButton = QtWidgets.QPushButton(self.groupBox)
        self.deOrbitButton.setGeometry(QtCore.QRect(70, 140, 131, 32))
        self.deOrbitButton.setObjectName("deOrbitButton")
        self.deOrbitButton.clicked.connect(self.deOrbit)

        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(520, 319, 261, 181))
        self.groupBox_2.setObjectName("groupBox_2")

        self.payloadStartTButton = QtWidgets.QPushButton(self.groupBox_2)
        self.payloadStartTButton.setGeometry(QtCore.QRect(60, 110, 131, 32))
        self.payloadStartTButton.setObjectName("payloadStartTButton")
        self.payloadStartTButton.clicked.connect(self.startPayloadTel)

        self.payloadStopTButton = QtWidgets.QPushButton(self.groupBox_2)
        self.payloadStopTButton.setGeometry(QtCore.QRect(60, 140, 131, 32))
        self.payloadStopTButton.setObjectName("payloadStopTButton")
        self.payloadStopTButton.clicked.connect(self.stopPayloadTel)
        self.payloadStopTButton.setEnabled(False)

        self.payloadStartDButton = QtWidgets.QPushButton(self.groupBox_2)
        self.payloadStartDButton.setGeometry(QtCore.QRect(60, 20, 131, 32))
        self.payloadStartDButton.setObjectName("payloadStartDButton")
        self.payloadStartDButton.clicked.connect(self.startPayloadData)

        self.payloadStopDButton = QtWidgets.QPushButton(self.groupBox_2)
        self.payloadStopDButton.setGeometry(QtCore.QRect(60, 50, 131, 32))
        self.payloadStopDButton.setObjectName("payloadStopDButton")
        self.payloadStopDButton.clicked.connect(self.stopPayloadData)
        self.payloadStopDButton.setEnabled(False)

        self.decommissionButton = QtWidgets.QPushButton(self.groupBox_2)
        self.decommissionButton.setGeometry(QtCore.QRect(60, 80, 131, 32))
        self.decommissionButton.setObjectName("decommissionButton")
        self.decommissionButton.clicked.connect(self.decommission)
        self.decommissionButton.setEnabled(False)

        self.launchList = QtWidgets.QListWidget(self.centralwidget)
        self.launchList.setGeometry(QtCore.QRect(10, 10, 211, 471))
        self.launchList.setObjectName("launchList")
        self.launchList.currentItemChanged.connect(self.reset)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.dsn = dsn()
        self.dsn.start()
        # self.dsn.sig.connect(self.updateDetails)

        self.timer = QTimer() 
        self.timer.timeout.connect(self.updateDetails)
        self.timer.start(100)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addNewLaunchButton.setText(_translate("MainWindow", "New Launch"))
        self.deleteLaunchButton.setText(_translate("MainWindow", "Delete Launch"))
        self.groupBox.setTitle(_translate("MainWindow", "Launch Vehicle Commands"))
        self.lvLaunchButton.setText(_translate("MainWindow", "Launch"))
        self.lvStartTButton.setText(_translate("MainWindow", "Start Telemetry"))
        self.lvStopTButton.setText(_translate("MainWindow", "Stop Telemetry"))
        self.deployButton.setText(_translate("MainWindow", "Deploy Payload"))
        self.deOrbitButton.setText(_translate("MainWindow", "DeOrbit"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Payload Commands"))
        self.payloadStartTButton.setText(_translate("MainWindow", "Start Telemetry"))
        self.payloadStopTButton.setText(_translate("MainWindow", "Stop Telemetry"))
        self.payloadStartDButton.setText(_translate("MainWindow", "Start Data"))
        self.payloadStopDButton.setText(_translate("MainWindow", "Stop Data"))
        self.decommissionButton.setText(_translate("MainWindow", "Decommission"))


    #Clicking add launch button.
    #Spawns new vehicle with new thread and new socket
    #New vehicle also attached to new payload with its own socket
    def addNewLaunch(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Config File", "", "Config files (*.ini)")
        if fileName:

            socket1 = context.socket(zmq.PAIR)
            port1 = socket1.bind_to_random_port("tcp://*")

            configObj = ConfigParser()
            configObj.read(fileName)

            if not "LAUNCH_INFO" in configObj:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Invalid File')
                error_dialog.exec_()
                return

            launch = lv(fileName, port1)

            with launchMutex:
                if launch.name in launches:
                    error_dialog = QtWidgets.QErrorMessage()
                    error_dialog.showMessage('File already selected')
                    error_dialog.exec_()
                    return
            
            launch.daemon = True
            launch.start()
            
            socket2 = context.socket(zmq.PAIR)
            port2 = socket2.bind_to_random_port("tcp://*")
            p = payload(launch.payload, port2)
            p.daemon = True
            p.start()
            obj = [launch, socket1, "", p, socket2, "", ""]

            launchMutex.acquire()
            try:
                launches[launch.name] = obj
            finally:
                launchMutex.release()
            item = QListWidgetItem(launch.name)
            self.launchList.addItem(item)
            self.launchList.setCurrentItem(item)
            vehicles.append(lv)


    #Delete button should remove launch, payload and name from the list
    def deleteLaunch(self):
        if self.launchList.currentItem() != None:
            with launchMutex:
                lv = launches[self.launchList.currentItem().text()][0]
                payload = launches[self.launchList.currentItem().text()][3]
                launches.pop(self.launchList.currentItem().text())
            self.launchList.takeItem(self.launchList.currentRow())
            del lv
            del payload
            self.updateDetails()

    #Reset function is called when the item in the list is changed.
    #Reset the buttons to their original state
    def reset(self):
        if self.launchList.currentItem() != None:
            lv = launches[self.launchList.currentItem().text()][0]
            payload = launches[self.launchList.currentItem().text()][3]

            if lv.isLaunched:
                self.lvLaunchButton.setEnabled(False)
            else:
                self.lvLaunchButton.setEnabled(True)


            if lv.isSending and lv.isDeOrbited == False:
                self.lvStopTButton.setEnabled(True)

            if lv.isSending == False and lv.isDeOrbited == False:
                self.lvStartTButton.setEnabled(True)

            if lv.isDeOrbited:
                self.lvLaunchButton.setEnabled(False)
                self.lvStartTButton.setEnabled(False)
                self.lvStopTButton.setEnabled(False)
                self.deployButton.setEnabled(False)
                self.deOrbitButton.setEnabled(False)
            else:
                self.deOrbitButton.setEnabled(True)

            if lv.isDeployable and payload.isDecommissioned == False:
                self.deployButton.setEnabled(True)
            else:
                self.deployButton.setEnabled(False)

            if payload.isSendingTel and payload.isDecommissioned == False:
                self.payloadStopTButton.setEnabled(True)

            if payload.isSendingTel == False and payload.isDecommissioned == False:
                self.payloadStartTButton.setEnabled(True)

            if payload.isSendingData and payload.isDecommissioned == False:
                self.payloadStopDButton.setEnabled(True)

            if payload.isSendingData == False and payload.isDecommissioned == False:
                self.payloadStartDButton.setEnabled(True)


            if payload.isDecommissioned:
                self.payloadStartDButton.setEnabled(False)
                self.payloadStartTButton.setEnabled(False)
                self.payloadStopDButton.setEnabled(False)
                self.payloadStopTButton.setEnabled(False)
                self.decommissionButton.setEnabled(False)
                self.deployButton.setEnabled(False)
            else:
                self.decommissionButton.setEnabled(True)
                if lv.isDeployable:
                    self.deployButton.setEnabled(True)

            if payload.isDeployed:
                self.deployButton.setEnabled(False)
            

            self.updateDetails()


    #Update details is called every 0.5s
    #It updates the GUI dashboard and buttons based on the item selected
    def updateDetails(self):
        if self.launchList.currentItem() != None:

            with launchMutex:

                #Add details to the launch vehicle dashboard

                lv = launches[self.launchList.currentItem().text()][0]
                lvDetails = ""
                if not lv.isLaunched:
                    lvDetails += "Waiting to be launched....\n"
                else:
                    lvDetails += "Vehicle launched!\n"

                lvDetails += "Name: " + lv.name + "\n"
                lvDetails += "Orbit: " + str(lv.orbit) + "\n"
                lvDetails += "\n"
                
                if lv.isDeOrbited:
                    self.deployButton.setEnabled(False)
                    self.lvStartTButton.setEnabled(False)
                    self.lvStopTButton.setEnabled(False)
                elif lv.isDeployable:
                    self.deployButton.setEnabled(True)

                #Add telemetry data if its being sent
                if not lv.isSending:
                    lis = launches[self.launchList.currentItem().text()]
                    lis[2] = {}
                    launches[self.launchList.currentItem().text()] = lis
                    lvDetails += ""
                else:
                    telemetryData = launches[self.launchList.currentItem().text()][2]
                    lvDetails += "Telemetry Data:\n\n"
                    for key, value in telemetryData.items():
                        lvDetails += key + ": " + str(value) + "\n"


                #Get details of the payload and display on the dashboard

                payload = launches[self.launchList.currentItem().text()][3]
                payloadDetails = ""
                if not payload.isDeployed:
                    payloadDetails += "Waiting to be deployed....\n"
                else:
                    payloadDetails += "Payload Deployed\n"

                payloadDetails += "Name: " + payload.name + "\n"
                payloadDetails += "\n"

                if payload.isDeployed:
                    self.deployButton.setEnabled(False)
                    self.decommissionButton.setEnabled(True)

                if payload.isDecommissioned:
                    self.decommissionButton.setEnabled(False)
                
                #Get payload telemetry data if it is sending it
                if not payload.isSendingTel:
                    lis = launches[self.launchList.currentItem().text()]
                    lis[5] = {}
                    launches[self.launchList.currentItem().text()] = lis
                    payloadDetails += ""
                else:
                    payloadTelData = launches[self.launchList.currentItem().text()][5]
                        
                    payloadDetails += "Telemetry Data:\n\n"

                    for key, value in payloadTelData.items():
                        payloadDetails += key + ": " + str(value) + "\n"

                payloadDetails += "\n"

                #Get payload data if it is sending it
                if not payload.isSendingData:
                    lis = launches[self.launchList.currentItem().text()]
                    lis[6] = {}
                    launches[self.launchList.currentItem().text()] = lis
                    payloadDetails += ""
                    self.payloadDetails.setGeometry(QtCore.QRect(510, 10, 271, 301))
                    self.imgBox.setGeometry(QtCore.QRect(510, 220, 271, 0))

                else:
                    if payload.type == "Scientific":
                        payloadDetails += "Weather Data: \n"
                    elif payload.type == "Comm":
                        payloadDetails += "Comm Data: \n"
                    else:
                        payloadDetails += "Image Data: \n"


                #Based on type of payload, process the data it will send and display
                payloadData = launches[self.launchList.currentItem().text()][6]
                for key, value in payloadData.items():
                    if key == "Image":
                        self.payloadDetails.setGeometry(QtCore.QRect(510, 10, 271, 201))
                        self.imgBox.setGeometry(QtCore.QRect(510, 220, 271, 90))
                        img = Image.fromarray(np.array(json.loads(value), dtype='uint8'))
                        qimg = ImageQt(img).copy()
                        pixmap = QtGui.QPixmap.fromImage(qimg)
                        self.imgBox.setPixmap(pixmap)
                        
                    else:
                        self.payloadDetails.setGeometry(QtCore.QRect(510, 10, 271, 301))
                        self.imgBox.setGeometry(QtCore.QRect(510, 220, 271, 0))
                        payloadDetails += key + ": " + str(value)
                    if payload.type == "Scientific":
                        if key == "Rainfall":
                            payloadDetails += "mm\n"
                        elif key == "Humidity":
                            payloadDetails += "%\n"
                        else:
                            payloadDetails += "in\n"
                    elif payload.type == "Comm":
                        if key == "UpLink" or key == "DownLink":
                            payloadDetails += "Mbps\n" 

            
            self.lvDetails.clear()
            self.lvDetails.setText(lvDetails)
            self.payloadDetails.clear()
            self.payloadDetails.setText(payloadDetails)
        else:
            self.lvDetails.clear()
            self.payloadDetails.clear()



    #Initiates launch of the vehicle, that begins the timeToOrbit countdown
    #Send the launch signal to the launch vehicle through the socket
    def launchVehicle(self):
        if self.launchList.currentItem() != None:
            lv = launches[self.launchList.currentItem().text()][0]
            if lv.isDeOrbited:
                return
            socket = launches[self.launchList.currentItem().text()][1]

            socket.send(b"Launch")
            self.lvLaunchButton.setEnabled(False)

    #Send the Start Telemetry signal to the launch vehicle
    def startTel(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][1]
            lv = launches[self.launchList.currentItem().text()][0]
            if lv.isDeOrbited or lv.isSending:
                return

            socket.send(b"StartT")
            self.lvStartTButton.setEnabled(False)
            self.lvStopTButton.setEnabled(True)

    #Send the Stop Telemetry signal to the launch vehicle
    def stopTel(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][1]
            lv = launches[self.launchList.currentItem().text()][0]
            if lv.isDeOrbited or lv.isSending == False:
                return
            socket.send(b"StopT")
            self.lvStopTButton.setEnabled(False)
            self.lvStartTButton.setEnabled(True)

    #Send the Deorbit signal to the launch vehicle
    def deOrbit(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][1]
            lv = launches[self.launchList.currentItem().text()][0]
            payload = launches[self.launchList.currentItem().text()][3]
            if lv.isDeOrbited or payload.isDeployed == False:
                return
            socket.send(b"DeOrbit")
            self.deOrbitButton.setEnabled(False)
            self.lvStopTButton.setEnabled(False)
            self.lvStartTButton.setEnabled(False)

    #Send the deploy signal to the launch vehicle if the payload is deployable
    #Is only activated after t seconds
    def deployPayload(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            lv = launches[self.launchList.currentItem().text()][0]
            payload = launches[self.launchList.currentItem().text()][3]
            if lv.isDeOrbited or payload.isDecommissioned:
                return
            socket.send(b"Deploy")
            self.deployButton.setEnabled(False)
            self.deOrbitButton.setEnabled(True)

    #Send the Start Telemetry signal to the payload
    def startPayloadTel(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            payload = launches[self.launchList.currentItem().text()][3]
            if payload.isDecommissioned or payload.isSendingTel:
                return
            socket.send(b"StartT")
            self.payloadStartTButton.setEnabled(False)
            self.payloadStopTButton.setEnabled(True)

    #Send the Stop Telemetry signal to the payload
    def stopPayloadTel(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            payload = launches[self.launchList.currentItem().text()][3]
            if payload.isDecommissioned or payload.isSendingTel == False:
                return
            socket.send(b"StopT")
            self.payloadStopTButton.setEnabled(False)
            self.payloadStartTButton.setEnabled(True)

    #Send the Start Data signal to the payload
    def startPayloadData(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            payload = launches[self.launchList.currentItem().text()][3]
            if payload.isDecommissioned or payload.isSendingData:
                return
            socket.send(b"StartD")
            self.payloadStartDButton.setEnabled(False)
            self.payloadStopDButton.setEnabled(True)

    #Send the Stop Data signal to the payload
    def stopPayloadData(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            payload = launches[self.launchList.currentItem().text()][3]
            if payload.isDecommissioned or payload.isSendingData == False:
                return
            socket.send(b"StopD")
            self.payloadStopDButton.setEnabled(False)
            self.payloadStartDButton.setEnabled(True)

    #Send the Decommission signal to the payload
    def decommission(self):
        if self.launchList.currentItem() != None:
            socket = launches[self.launchList.currentItem().text()][4]
            payload = launches[self.launchList.currentItem().text()][3]
            if payload.isDecommissioned or payload.isDeployed == False:
                return
            socket.send(b"Decommission")
            self.decommissionButton.setEnabled(False)
            self.payloadStopDButton.setEnabled(False)
            self.payloadStartDButton.setEnabled(False)
            self.payloadStartTButton.setEnabled(False)
            self.payloadStopTButton.setEnabled(False)


#This is the thread that controls the DSN socket. 
#Waits, receives and sends messages to launch vehicles
class dsn(QtCore.QThread):
    
    sig = pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        while True:
            with launchMutex:
                #For each socket, keep checking if messages have arrived
                for key, value in launches.items():
                    socket1 = value[1]
                    socket2 = value[4]
                    message = None
                    payloadMessage = None
                    #This is the launch vehicle transmission block
                    try:
                        #Save the received message into the buffer so that it can be processed 
                        lvMessage = socket1.recv_json(flags=zmq.NOBLOCK)
                        value[2] = json.loads(lvMessage)
                        # self.sig.emit(message)
                    except zmq.Again as e:
                        pass
                    #This is the payload transmission block
                    try:
                        #Save the received message into the buffer so that it can be processed 
                        #Also save the message based on the type
                        payloadMessage = socket2.recv_json(flags=zmq.NOBLOCK)
                        temp = json.loads(payloadMessage)
                        if(temp["type"] == "Tel"):
                            temp.pop("type")
                            value[5] = temp
                        elif(temp["type"] == "Data"):
                            temp.pop("type")
                            value[6] = temp
                    except zmq.Again as e:
                        pass
                    launches[key] = value
            
            


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
    dsn.join()

    for v in vehicles:
        v.join()
