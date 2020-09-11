import time
from common.device import Device
import log.logger as l

import messaging.messaging as m

def getListOfDevicesStoredLocally():
  listOfDevicesStoredLocally = []
  return listOfDevicesStoredLocally

def launchDeviceManager():
  pass

def devicesManagerThread():
  listOfDevicesStoredLocally = getListOfDevicesStoredLocally()

  for device in listOfDevicesStoredLocally:
    launchDeviceManager(device)

  while True:
    eventReceived, pathReceived = subscriber.receive()
    l.loggerINFOredDIM(f"DEVICES MANAGER event received: {eventReceived}", f"on path: {pathReceived}")
    #To Do: If DEVICE Does not Respond - TIMEOUT -Inform Odoo and Relaunch
      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
