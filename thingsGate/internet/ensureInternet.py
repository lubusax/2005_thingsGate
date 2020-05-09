import time,socket,fcntl,struct

def check_connection():
  ifaces = ['eth0','wlan0']
  connected = []

  i = 0
  for ifname in ifaces:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
        )[20:24])
      connected.append(ifname)
      print ("%s is connected" % ifname)
    except:
      print ("%s is not connected" % ifname)
  i += 1

  return connected



def isAnyInterfaceConnected():
  result=False
  connected_ifaces = check_connection()
  if len(connected_ifaces) == 0:
      print ('not connected to any network')
  else:
      result= True
      print ('connected to a network using the following interface(s):')
      for x in connected_ifaces:
          print ('\t%s' % x)
  return result

def ensureInternet( semaphoreInternet,
                    semaphoreEndInternet):
  print("ensure Internet module - has begun ")

  # while loop until the End Signal (Semaphore)
  # is set.
  while semaphoreEndInternet.acquire(False):
   
    semaphoreEndInternet.release()
    # release the semaphore inmediately
    # to allow the acquire somewhere else 
    # if this process needs to get a stop signal to end
    if not isAnyInterfaceConnected(): 
      print ('not connected to any network')
    else:
      print ('there is at least one network connection active')

    time.sleep(0.7) #do some stuff

  # here you can make some arrangements before
  # closing the process
  print("ensure Internet module - has ended ")



if __name__ == '__main__':
 
  ensureInternet( semaphoreInternet,
                  semaphoreEndInternet)
  
