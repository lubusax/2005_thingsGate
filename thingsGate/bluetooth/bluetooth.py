import  time
from    bluetooth.dBusBluezConnection import dBusBluezConnection
from    common.common import prettyPrint
from log.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

def bluetoothConnectionThread():
  myBluezConnection = dBusBluezConnection()

  # listen to Interfaces Added - get Feedback if there is a device added

  myBluezConnection.connectThingsInTouchDevicesStoredLocally()

  myBluezConnection.discoverThingsInTouchDevices()

  #while not myBluezConnection.flagToExit: time.sleep(0.5)

  time.sleep(10)

  print("client Gate Things exit")

  myBluezConnection.exitThreadMainLoopGobject()

def main():
  bluetoothConnectionThread()

if __name__ == "__main__":
  main()
