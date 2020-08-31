from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqReplier

# device= 
# device = Device()

def devicesManagerThread():
  newDevicesReceiverAndReplier = zmqReplier("5560")
  #time.sleep(2)

  while True:
    topic, newDeviceAddress = newDevicesReceiverAndReplier.receive()
    if topic == "newDevice":
      print("NEW DEVICE ---"*10)
      newDevicesReceiverAndReplier.reply("received", newDeviceAddress)
    else:
      newDevicesReceiverAndReplier.reply("notReceived", newDeviceAddress)
      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
