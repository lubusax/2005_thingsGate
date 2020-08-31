from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqSubscriber, zmqPublisher

# device= 
# device = Device()

def devicesManagerThread():
  newDevicesSubscriptionPort = "5556"
  newDevicesSubscription = zmqSubscriber(newDevicesSubscriptionPort)
  newDevicesSubscription.subscribe("newDevice")

  while True:
    topic, newDeviceAddress = newDevicesSubscription.receive()
    if topic == "newDevice":
      print("NEW DEVICE ---"*10)

def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
