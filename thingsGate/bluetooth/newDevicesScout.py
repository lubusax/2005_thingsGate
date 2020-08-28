from common.device import Device
import time

# device= 
# device = Device()

def newDevicesScoutThread():
  while 1:
    print(f"time STAMP - newDevicesScout: {time.gmtime()}")
    time.sleep(10)

def main():
  newDevicesScoutThread()

if __name__ == "__main__":
  main()