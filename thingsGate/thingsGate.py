import os, sys, time
from crontab.crontabSetup import minuteTrigger
from rpi.rpiSetup import setHostname
from internet.internet import ensureInternet
from odoo.gate import gateInit
from multiprocessing import Process, Manager
#import logging, logging.config
from launcher import launcher
from log.logger import logger
import importlib

logger(f'running on python version: {sys.version}')

managedProcesses = {
    "devicesManager": "bluetooth.devicesManager",
    "newDevicesScout": "bluetooth.newDevicesScout",
    "zmqLazyPirateServer": "messaging.zmqLazyPirateServer",    
}

greenTempProcesses = managedProcesses

persistentProcesses = greenTempProcesses

running = {}

def defineDirectories():

  dirPath = os.path.dirname(os.path.realpath(__file__))

  logger(f'running on directory: {dirPath}')

  os.environ['PYTHONPATH'] = dirPath

  pythonPath = os.getenv('PYTHONPATH')

  logger(f'PYTHONPATH: {pythonPath}')

def startManagedProcess(name):
  if name in running or name not in managedProcesses: return

  process = managedProcesses[name]

  logger(f"starting python process {process}")

  running[name] = Process(name=name, target=launcher, args=(process,))

  running[name].start()

def killManagedProcess(name):
  logger(f"killing python process {process}")

def preImportMethods():
  for i, p in enumerate(managedProcesses):
    process = managedProcesses[p]
    logger(f"process number {i}, preimporting {process}")
    importlib.import_module(process)

def managerThread():
  logger(f"starting manager thread") 
  # Get thermal status through messaging -- msg = messaging.recv_sock(thermal_sock, wait=True)
  # heavyweight batch processes run only when thermal conditions are favorable

  thermalStatusCritical = False

  logger(f"green Temp Processes {greenTempProcesses}")

  if thermalStatusCritical:
    for p in greenTempProcesses:
      if p in persistentProcesses:
        killManagedProcess(p)
  else:
    for p in greenTempProcesses:
      startManagedProcess(p) 

def main():

  defineDirectories()

  preImportMethods()

  try:
    managerThread()
  except Exception as e:
    #traceback.print_exc() ---- crash.capture_exception()
    logger(f'thingsGate managerThread failed to start with exception {e}')
  finally:
    #cleanupAllProcesses()
    pass

  # if params.get("DoUninstall", encoding='utf8') == "1":  uninstall()


if __name__ == "__main__":

  #logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)

  try:
    main()
  except Exception as e:
    logger(f'thingsGate Manager failed to start with exception {e}')    
    # add_logentries_handler(cloudlog)
    # # Show last 3 lines of traceback ---  error = "Manager failed to start\n \n" + traceback.format_exc(3)
    # with TextWindow(error) as t:
    #   t.wait_for_exit()
    # raise

  # manual exit because we are forked
  # sys.exit(0)