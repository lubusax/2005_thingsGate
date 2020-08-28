from common.device import Device
import time

# device= 
# device = Device()

def devicesManagerThread():
  while 1:
    print(f"time STAMP - devices Manager: {time.ctime()}")
    time.sleep(10)

def main():
  devicesManagerThread()

if __name__ == "__main__":
  main()
