import time,socket,fcntl,struct
import shlex,logging
from subprocess import call, PIPE, STDOUT, Popen

def getInternet():
  ''' get internet Access from the User
      WiFi: SSID + Password
  '''
  return True

def getReturnCode(cmd, stderr=STDOUT, timeout=1):
  """Execute a simple shell command
  and return its exit status. Timeout is 1 second"""
  args = shlex.split(cmd)
  childProcess = Popen(args,stdout=PIPE,stderr=stderr)
  try:
    childProcess.communicate(timeout=timeout)
    returnCode = childProcess.returncode
  except:
    returnCode = -99 # timeout or other error
  return returnCode

def internetAccess():
  cmd = "ping -c 1 1.1.1.1"
  return getReturnCode(cmd) == 0

def ensureInternet( semaphoreInternet,
                    semaphoreEndInternet):
  logging.debug(f'ensure Internet module - has begun ')

  # while loop until the End Signal (Semaphore)
  # is set.
  while semaphoreEndInternet.acquire(False):
   
    semaphoreEndInternet.release()
    # release the semaphore inmediately
    # to allow the acquire somewhere else 
    # if this process needs to get a stop signal to end
    if not internetAccess(): 
      logging.debug(f'NOT connected to internet')
    else:
      logging.debug(f'connected to internet')

    time.sleep(0.7) #do some stuff

  # here you can make some arrangements before
  # closing the process
  logging.debug(f'ensure Internet module - has ended ')



if __name__ == '__main__':
 
  ensureInternet( semaphoreInternet,
                  semaphoreEndInternet)
  
