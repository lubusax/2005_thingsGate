from common.device import Device
from log.logger import logger
import time

# device= 
# device = Device()

def devicesManagerThread():
  while 1:
    logger(f"time STAMP - devices Manager: {time.ctime()}")
    time.sleep(9)

def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
