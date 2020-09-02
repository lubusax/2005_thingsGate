from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqLazyPirateReplier

# device= 
# device = Device()

def devicesManagerThread():
  portReplierDevicesManager   = "5555"
  newDevicesReceiverAndReplier = zmqLazyPirateReplier(portReplierDevicesManager)
  #time.sleep(2)

  while True:
    newDeviceAddress = newDevicesReceiverAndReplier.receive()

    logger(f"devices Manager - NEW DEVICE --- newDeviceAddress: {newDeviceAddress}")
    newDevicesReceiverAndReplier.reply("OK")

      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
