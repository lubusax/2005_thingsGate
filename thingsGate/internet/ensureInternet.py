import time

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

    time.sleep(0.1) #do some stuff

  # here you can make some arrangements before
  # closing the process
  print("ensure Internet module - has ended ")



if __name__ == '__main__':
 
  ensureInternet( semaphoreInternet,
                  semaphoreEndInternet)
  
