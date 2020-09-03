from common.device import Device
from log.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import time

from messaging.messaging import Replier

# device= 
# device = Device()

def devicesManagerThread():
  portReplierDevicesManager   = "5555"
  newDevicesReceiverAndReplier = Replier(portReplierDevicesManager)
  #time.sleep(2)

  while True:
    newDeviceAddress = newDevicesReceiverAndReplier.receive()

    loggerINFO(f"devices Manager - NEW DEVICE --- newDeviceAddress: {newDeviceAddress}")
    newDevicesReceiverAndReplier.reply("OK")

      
def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
