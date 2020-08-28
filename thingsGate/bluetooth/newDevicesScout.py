from common.device import Device
from log.logger import logger
import time

def newDevicesScoutThread():
  while 1:
    logger(f"time STAMP - newDevicesScout: {time.ctime()}")
    time.sleep(10)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()