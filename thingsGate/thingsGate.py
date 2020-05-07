import os, sys, time
from crontab.crontabSetup import setupCrontab
from internet.ensureInternet import ensureInternet
from multiprocessing import Process, Manager

def minuteTrigger(): # triggers a programm every minute
  print('minute trigger - has begun')
  dirPath = os.path.dirname(os.path.realpath(__file__))
  #setupCrontab(dirPath)
  print('minute trigger - has ended')
  

def connectToInternet(): # oversees that there is
                      # always an internet connection
  print('connect to internet - has begun')
  ensureInternet()
  print('connect to internet - has ended')                   


if __name__ == '__main__':
  print('main program - python version: ', sys.version)

  minuteTrigger() # this function runs only once.
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
  
  time.sleep(10)
  print("Stop Signal module Internet sent ")
  semaphoreEndInternet.acquire()
  
  for p in processes:
    p.join()
  
  #connectToOdoo()
