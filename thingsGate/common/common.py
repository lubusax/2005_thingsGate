from    pprint import PrettyPrinter
pPrint = PrettyPrinter(indent=1).pprint

import time
import subprocess

def prettyPrint(message):
  pPrint(message)

def nowInSecondsAndMilliseconds():
  t = time.time()
  return (str(int((t - int(t/100)*100)))+ "s " + str(int((t - int(t)) *1000))+ "ms")

def runShellCommand(command):
  try:
    completed = subprocess.run(command.split())
    loggerDEBUG(f'command {command} - returncode: {completed.returncode}')
  except:
    loggerERROR(f"error on method run shell command: {command}")