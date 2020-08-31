from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqPublisher, zmqSubscriber


def newDevicesScoutThread():

  newDevicesPublication     = zmqPublisher("5556")


  while True:
    newDeviceAddress = "12:34:AB:CD"
    newDevicesPublication.publish("newDevice", newDeviceAddress)

    time.sleep(2)

    #logger(f"time STAMP - newDevicesScout: {time.ctime()}")
    #time.sleep(0.5)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()