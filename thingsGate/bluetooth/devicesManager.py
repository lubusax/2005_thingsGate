from common.device import Device
from log.logger import logger
import time

from messaging.messaging import zmqLazyPirateServer

# device= 
# device = Device()

def devicesManagerThread():
  portServerEndpoint    = "5555"
  newDevicesReceiverAndReplier = zmqLazyPirateServer(portServerEndpoint)
  #time.sleep(2)

  while True:
    newDeviceAddress = newDevicesReceiverAndReplier.receive()

    logger(f"devices Manager - NEW DEVICE --- newDeviceAddress: {newDeviceAddress}")
    newDevicesReceiverAndReplier.reply("1")

      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
