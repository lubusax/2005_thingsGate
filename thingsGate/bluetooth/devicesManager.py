from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqSubscriber

# device= 
# device = Device()

def devicesManagerThread():
  newDevicesSubscriptionPort = "5556"
  newDevicesSubscription = zmqSubscriber(newDevicesSubscriptionPort)
  newDevicesSubscription.subscribe("60437")

  while True:
    newDevicesSubscription.receiveSubscription()
    #logger(f"time STAMP - devices Manager: {time.ctime()}")
    #time.sleep(.2)

def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
