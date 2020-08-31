from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqRequester


def newDevicesScoutThread():

  newDevicesAnnouncer  = zmqRequester("5559")


  while True:
    newDeviceAddress = "12:34:AB:CD"
    topic, message = newDevicesAnnouncer.request("newDevice", newDeviceAddress)
    if topic=="received" and message==newDeviceAddress:
      print("DEVICE REGISTERED -- "*12)

    time.sleep(2)

    #logger(f"time STAMP - newDevicesScout: {time.ctime()}")
    #time.sleep(0.5)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()