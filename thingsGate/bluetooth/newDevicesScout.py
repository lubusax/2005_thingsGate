from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqPublisher


def newDevicesScoutThread():

  newDevicesPublication = zmqPublisher("5556")

  while True:
    newDevicesPublication.publish()

    #logger(f"time STAMP - newDevicesScout: {time.ctime()}")
    time.sleep(0.5)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()