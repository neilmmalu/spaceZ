from configparser import ConfigParser
from threading import Thread, Lock
import zmq
import time
import json
from random import seed
from random import randint

import numpy as np



class payload(Thread):
    def __init__(self, fileName, port):
        Thread.__init__(self)
        configObj = ConfigParser()
        configObj.read(fileName)

        #Create payload based on the config file
        lvInfo = configObj["PAYLOAD_INFO"]
        self.name = lvInfo["name"]
        self.type = lvInfo["type"]
        self.time = int(lvInfo["time"])
        self.telemetry = {}

        self.data = {}

        #Set up based on type of payload 
        if(self.type == "Scientific"):
            pass
        elif(self.type == "Comm"):
            pass
        else:
            pass

        self.data["type"] = "Data"

        #Set initial telemetry data
        self.telemetry["type"] = "Tel"
        self.telemetry["altitude"] = 0
        self.telemetry["latitude"] = 0
        self.telemetry["longitude"] = 0
        self.telemetry["temperature"] = 300
        self.telemetry["timeToOrbit"] = 0

        self.telemetryMutex = Lock()
        self.dataMutex = Lock()

        self.isDeployed = False
        self.isSendingTel = False
        self.isSendingData = False
        self.latitudeStep = True
        self.isDecommissioned = False
        self.port = port


    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        string = "tcp://localhost:" + str(self.port)
        socket.connect(string)
        flag = False
        timer = self.time
        while True:
            try:
                #receive signal from DSN
                message = (socket.recv(flags=zmq.NOBLOCK)).decode("utf-8")
            except zmq.Again as e:
                message = ""
            #Deploy payload
            if(message == "Deploy"):
                self.isDeployed = True

            #Start sending telemetry data
            if(message == "StartT"):
                self.isSendingTel = True

            #Start sending payload data
            if(message == "StartD"):
                self.isSendingData = True

            #Stop sending telemetry data
            if(message == "StopT"):
                self.isSendingTel = False

            #Stop sending payload data
            if(message == "StopD"):
                self.isSendingData = False

            #Decommission the satellite
            if(message == "Decommission"):
                self.isDecommissioned = True
                self.isSendingTel = True
                self.isSendingData = True

            #If payload is in telemetry sending mode
            if self.isSendingTel:
                self.telemetryMutex.acquire()
                try:
                    #Send telemetry data to dsn
                    data = json.dumps(self.telemetry)
                    socket.send_json(data)
                finally:
                    self.telemetryMutex.release()

            #Timer for sending data.
            #Only send data when timer is 0. then reset the timer
            if timer == 0 or self.isDecommissioned:
                timer = self.time
                flag = True

            #If payload is in data sending mode
            if self.isSendingData and flag:
                self.dataMutex.acquire()
                try:
                    #Send payload data to dsn
                    data = json.dumps(self.data)
                    socket.send_json(data)
                finally:
                    self.dataMutex.release()
            flag = False

            #Update telemetry and payload data
            self.updateTelemetry()

            self.updateData()

            # print(self.name + ": " + str(self.telemetry))
            time.sleep(1)
            timer -= 1
            if self.isDecommissioned:
                break

    #This function updates telemetry data every second so that it can be sent to dsn
    def updateTelemetry(self):
        self.telemetryMutex.acquire()
        try:
            self.telemetry["altitude"] += 150

            self.telemetry["timeToOrbit"] -= 1
            if(self.telemetry["timeToOrbit"] < 0):
                self.telemetry["timeToOrbit"] = 0

            if(self.latitudeStep == True):
                self.telemetry["latitude"] += 1.5
            else:
                self.telemetry["latitude"] -= 1.5
            if(self.telemetry["latitude"] > 90):
                self.telemetry["latitude"] = 90
                self.latitudeStep = not self.latitudeStep
            if(self.telemetry["latitude"] < -90):
                self.telemetry["latitude"] = -90
                self.latitudeStep = not self.latitudeStep

            self.telemetry["longitude"] += 1.5
            if(self.telemetry["longitude"] >= 180):
                self.telemetry["longitude"] = -180

            if(self.telemetry["altitude"] < 300):
                self.telemetry["temperature"] -= 20
            elif(self.telemetry["altitude"] > 300 and self.telemetry["altitude"] < 1000):
                self.telemetry["temperature"] = (self.telemetry["altitude"] - 300) * 100 / 60
            else:
                self.telemetry["temperature"] -= 50
            
            if(self.telemetry["temperature"] < 5):
                self.telemetry["temperature"] = 5

        finally:
            self.telemetryMutex.release()

    #This function generates random data to send to dsn based on time specified in the config file
    def updateData(self):
        if(self.type == "Scientific"):
            self.data["Rainfall"] = randint(0, 10)
            self.data["Humidity"] = randint(0, 100)
            self.data["Snow"] = randint(0, 10)
        elif(self.type == "Comm"):
            self.data["UpLink"] = randint(0, 100)
            self.data["DownLink"] = randint(0, 1000)
            self.data["ActiveTransponders"] = randint(0, 100)
        else:
            im_out = np.random.randint(0,256,(271,271,3), dtype=np.uint8)
            json_data = json.dumps(np.array(im_out).tolist())
            self.data["Image"] = json_data