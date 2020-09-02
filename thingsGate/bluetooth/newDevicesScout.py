from common.device import Device
from log.logger import logger
from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

import time

from messaging.messaging import zmqLazyPirateRequester

def newDevicesScoutThread():
  portReplierDevicesManager    = "5555"
  newDevicesAnnouncer  = zmqLazyPirateRequester(portReplierDevicesManager)

  while True:
    newDeviceAddress = "12:34:AB:CD"
    replyFromDevicesManager = newDevicesAnnouncer.send(newDeviceAddress)

    logger(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"replyFromDevicesManager: {replyFromDevicesManager} ")
    time.sleep(2)


  # 
  #   #newDeviceAddress = "12:34:AB:CD"
  #   result = newDevicesAnnouncer.sendRequest()
    
  #   logger(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"request result: {result} ")

  #   

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()