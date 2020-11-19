from configparser import ConfigParser
from threading import Thread, Lock
import zmq
import time
import json


class lv(Thread):

    def __init__(self, fileName, port):
        Thread.__init__(self)
        configObj = ConfigParser()
        configObj.read(fileName)

        lvInfo = configObj["LAUNCH_INFO"]
        self.name = lvInfo["name"]
        self.orbit = int(lvInfo["orbit"])
        self.telemetry = {}
        self.telemetry["altitude"] = 0
        self.telemetry["latitude"] = 0
        self.telemetry["longitude"] = 0
        self.telemetryMutex = Lock()
        self.telemetry["temperature"] = 300
        self.telemetry["timeToOrbit"] = self.orbit/3600 + 10
        self.isLaunched = False
        self.isSending = False
        self.latitudeStep = True
        self.isDeployable = False
        self.isDeOrbited = False
        self.port = port
        # print(self.name)
        self.payload = lvInfo["payloadConfig"]
        

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        string = "tcp://localhost:" + str(self.port)
        socket.connect(string)
        while True:
            try:
                message = (socket.recv(flags=zmq.NOBLOCK)).decode("utf-8")
            except zmq.Again as e:
                message = ""
            # print(self.name + ": " + message)
            if(message == "Launch"):
                self.isLaunched = True

            if(message == "StartT"):
                self.isSending = True

            if(message == "StopT"):
                self.isSending = False

            if(message == "DeOrbit"):
                self.isDeOrbited = True
                self.isSending = True

            if self.isSending:
                self.telemetryMutex.acquire()
                try:
                    data = json.dumps(self.telemetry)
                    socket.send_json(data)
                finally:
                    self.telemetryMutex.release()

            self.updateTelemetry()

            if(self.isLaunched and self.telemetry["timeToOrbit"] == 0):
                self.isDeployable = True

            # print(self.name + ": " + str(self.telemetry))
            time.sleep(1)
            if self.isDeOrbited:
                break

    def updateTelemetry(self):
        if self.isLaunched:
            # print(self.name + ": in here")
            self.telemetryMutex.acquire()
            try:
                self.telemetry["altitude"] += 60
                if(self.telemetry["altitude"] > self.orbit):
                    self.telemetry["altitude"] = self.orbit

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


            