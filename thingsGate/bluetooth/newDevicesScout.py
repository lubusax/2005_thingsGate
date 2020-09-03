from common.device import Device
from log.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

import time

from messaging.messaging import Requester

def newDevicesScoutThread():
  portReplierDevicesManager    = "5555"
  newDevicesAnnouncer  = Requester(portReplierDevicesManager)

  while True:
    newDeviceAddress = "12:34:AB:CD"
    replyFromDevicesManager = newDevicesAnnouncer.send(newDeviceAddress)

    loggerINFO(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"replyFromDevicesManager: {replyFromDevicesManager} ")
    time.sleep(2)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()