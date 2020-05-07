import time

def ensureInternet( semaphoreInternet,
                    semaphoreEndInternet):
  print("ensure Internet module - has begun ")

  # while loop until the End Signal (Semaphore)
  # is set.
  while semaphoreEndInternet.acquire(False):
    #do some stuff
    semaphoreEndInternet.release()
    time.sleep(0.1)

  print("ensure Internet module - has ended ")



if __name__ == '__main__':
 
  ensureInternet()
  
