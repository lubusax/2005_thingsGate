from common.device import Device # pylint: disable=import-error
from bluetooth.deviceDiscovery import discoverNewDevices
from log.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

import time

from messaging.messaging import Requester

from bluetooth.dBusBluezConnection import dBusBluezConnection

def newDevicesScoutThread():
  portReplierDevicesManager    = "5555"
  newDevicesAnnouncer  = Requester(portReplierDevicesManager)
  permanentListOfAcceptedDevices = []

  while True:
    newDevice = discoverNewDevices() # blocking call, it returns only when there is a new Device
    #newDeviceAddress = "12:34:AB:CD"
    replyFromDevicesManager = newDevicesAnnouncer.send(newDevice)

    loggerINFO(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"replyFromDevicesManager: {replyFromDevicesManager} ")
    time.sleep(2)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()