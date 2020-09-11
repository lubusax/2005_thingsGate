import time
from common.device import Device
import log.logger as l

import messaging.messaging as m

def devicesManagerThread():
  listOfDevicesStoredLocally = getListOfDevicesStoredLocally()
  for device in listOfDevicesStoredLocally:
    launchDeviceManager(device)

  while True:
    eventReceived, pathReceived = subscriber.receive()
    l.loggerINFOredDIM(f"DEVICES MANAGER event received: {eventReceived}", f"on path: {pathReceived}")
      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
