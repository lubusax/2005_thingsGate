from common.device import Device
from log.logger import logger
from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

import time

from messaging.messaging import zmqLazyPirateClient

def newDevicesScoutThread():
  port    = "5555"
  timeout = 2500 #ms
  retries = 3
  newDevicesAnnouncer  = zmqLazyPirateClient(port, timeout, retries)

  result = newDevicesAnnouncer.sendRequest()

  logger(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"request result: {result} ")

  # while True:
  #   #newDeviceAddress = "12:34:AB:CD"
  #   result = newDevicesAnnouncer.sendRequest()
    
  #   logger(Fore.RED + "newDEVICES scout"+ Style.RESET_ALL + f"request result: {result} ")

  #   time.sleep(2)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()