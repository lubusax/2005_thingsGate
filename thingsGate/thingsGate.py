import os, sys, time
from crontab.crontabSetup import minuteTrigger
from internet.internet import ensureInternet
from odoo.gate import gateInit
from multiprocessing import Process, Manager


if __name__ == '__main__':
  
  print('main program - running on python version: ', sys.version)

  dirPath = os.path.dirname(os.path.realpath(__file__))

  print('running on directory: ', dirPath)
  
  gateInit(dirPath)

  #minuteTrigger(dirPath) # this function runs only once.
                  # It sets a trigger
                  # to run a program every minute

  manager = Manager()

  processes = []

  semaphoreInternet = manager.Semaphore()
  semaphoreEndInternet = manager.Semaphore()
  # Oversees that there is
  # always an internet connection.
  # The process runs until semaphoreEndInternet
  # is acquired.
  # When the other semaphore, semaphoreInternet is acquired,
  # it means that there is
  # no internet connection
  processEnsureInternet = Process(
          target  = ensureInternet,
          args    = (semaphoreInternet,
                     semaphoreEndInternet),
          name    = "ensure internet connection")
  processes.append(processEnsureInternet)

  semaphoreDisplay = manager.Semaphore()


  for p in processes:
    p.start()
  
  time.sleep(2)
  print("Stop Signal module Internet sent ")
  semaphoreEndInternet.acquire()
  
  for p in processes:
    p.join()
  
  #connectToOdoo()
