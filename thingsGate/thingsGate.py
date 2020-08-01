import os, sys, time
from crontab.crontabSetup import minuteTrigger
from rpi.rpiSetup import setHostname
from internet.internet import ensureInternet
from odoo.gate import gateInit
from multiprocessing import Process, Manager
import logging, logging.config

def main():
  logging.debug(('running on python version: {v}').format(v=sys.version))

  dirPath = os.path.dirname(os.path.realpath(__file__))

  logging.debug(('running on directory: {d}').format(d=dirPath))

  setHostname('02')
  
  # #gateInit(dirPath)

  # #minuteTrigger(dirPath) # this function runs only once.
  #                 # It sets a trigger
  #                 # to run a program every minute

  # manager = Manager()

  # processes = []

  # semaphoreInternet = manager.Semaphore()
  # semaphoreEndInternet = manager.Semaphore()
  # # Oversees that there is
  # # always an internet connection.
  # # The process runs until semaphoreEndInternet
  # # is acquired.
  # # When the other semaphore, semaphoreInternet is acquired,
  # # it means that there is
  # # no internet connection
  # processEnsureInternet = Process(
  #         target  = ensureInternet,
  #         args    = (semaphoreInternet,
  #                    semaphoreEndInternet),
  #         name    = "ensure internet connection")
  # processes.append(processEnsureInternet)

  # semaphoreDisplay = manager.Semaphore()


  # for p in processes:
  #   p.start()
  
  # time.sleep(2)
  # logging.debug(f'Stop Signal module Internet sent')
  # semaphoreEndInternet.acquire()
  
  # for p in processes:
  #   p.join()
  
  # #connectToOdoo()

if __name__ == '__main__':
  logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)
  main()
