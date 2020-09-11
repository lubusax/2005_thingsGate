# connectDeviceWithoutDiscovery needs flag --experimental on the bluetooth service (daemon bluetoothd)
# https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation#enable-bluetooth-low-energy-features
# https://pythonhosted.org/txdbus/dbus_overview.html
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject
from bluetooth.thingsSpecificClasses import Thing
from    common.common import prettyPrint
import time
import threading
import os
import subprocess
import common.events as ev

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from log.logger import loggerINFOredDIM, loggerDEBUGredDIM, loggerTIMESTAMPred, loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL, loggerDEBUGdim, loggerTIMESTAMP, loggerDEBUGredDIM
from common.common import nowInSecondsAndMilliseconds, runShellCommand
from messaging.messaging import zmqSubscriber, zmqPublisher

#########################################################
BLUEZ 															= 'org.bluez'
IFACE_OBJECT_MANAGER_DBUS						= 'org.freedesktop.DBus.ObjectManager'
IFACE_PROPERTIES_DBUS								= "org.freedesktop.DBus.Properties"
IFACE_LE_ADVERTISING_MANAGER 				= 'org.bluez.LEAdvertisingManager1'
IFACE_GATT_MANAGER 									= 'org.bluez.GattManager1'
IFACE_GATT_CHARACTERISTIC 					= 'org.bluez.GattCharacteristic1'
IFACE_GATT_SERVICE                  = 'org.bluez.GattService1'
IFACE_ADAPTER 											= 'org.bluez.Adapter1'
IFACE_DEVICE                        = 'org.bluez.Device1'

PATH_HCI0 													= '/org/bluez/hci0'

UUID_GATESETUP_SERVICE      				= '5468696e-6773-496e-546f-756368000100'
ALIAS_THINGSINTOUCH_BEGINING				= 'ThingsInTouch'
# ThingsInTouch Services        go from 0x001000 to 0x001FFF
# ThingsInTouch Characteristics go from 0x100000 to 0x1FFFFF
UUID_READ_WRITE_TEST_CHARACTERISTIC = '5468696e-6773-496e-546f-756368100000'
UUID_NOTIFY_TEST_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100001'
UUID_SERIAL_NUMBER_CHARACTERISTIC   = '5468696e-6773-496e-546f-756368100002'
UUID_DEVICE_TYPE_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100003'

UUID_BEGIN_THINGSINTOUCH            = '5468696e-6773-496e-546f-756368'

DEVICE_NAME 												= 'ThingsInTouch-Gate-01'
#########################################################

class dBusBluezConnection():
  def __init__(self):
    
    loggerTIMESTAMP("__init__ class dBusBluezConnection")

    DBusGMainLoop(set_as_default=True)

    self.systemBus 	                = dbus.SystemBus()

    self.hci0 	                    = self.systemBus.get_object(BLUEZ, PATH_HCI0)
    self.bluez                      = self.systemBus.get_object(BLUEZ , "/")
    self.adapterInterface           = dbus.Interface( self.hci0,   IFACE_ADAPTER)
    self.objectManagerInterface     = dbus.Interface(self.bluez, IFACE_OBJECT_MANAGER_DBUS)

    #self.deviceInterfacesWaitingForServicesResolved = {}

    self.portForBluezEvents   = "5565"
    self.subscriber   = zmqSubscriber(self.portForBluezEvents) 
    self.publisher    = zmqPublisher (self.portForBluezEvents)
    self.subscriber.subscribe(ev.bluezEvents.SerialNumberCharacteristicInterfaceAdded)
    self.subscriber.subscribe(ev.bluezEvents.ServicesResolved)
    self.subscriber.subscribe(ev.bluezEvents.GateSetupServiceInterfaceAdded)

    self.listenToPropertiesChanged()
    self.listenToInterfacesAdded()

    self.exitFlag = threading.Event()
    self.exitFlag.clear()
    self.threadMainLoop = threading.Thread(target=self.enterThreadMainLoopGObject, args=(self.exitFlag,))
    self.threadMainLoop.start()

  def discoverThingsInTouchDevices(self):
    scanFilter = {}
    scanFilter["Transport"] 	= "le" 
    scanFilter['UUIDs'] 			= [UUID_GATESETUP_SERVICE]
    self.adapterInterface.SetDiscoveryFilter(scanFilter)
    self.adapterInterface.StartDiscovery()

  def listenToPropertiesChanged(self):
    self.systemBus.add_signal_receiver(self.propertiesChanged, dbus_interface = IFACE_PROPERTIES_DBUS,
                        signal_name = "PropertiesChanged", arg0 = IFACE_DEVICE, path_keyword = "path")

  def listenToInterfacesAdded(self):
    self.systemBus.add_signal_receiver(self.interfacesAdded, dbus_interface = IFACE_OBJECT_MANAGER_DBUS,
                        signal_name = "InterfacesAdded")

  def interfacesAdded(self, path, interfaces):
    loggerTIMESTAMP("Interfaces Added")
    loggerDEBUGdim(f"An interface was added on path: {path}")
    prettyPrint(interfaces)
    try:
      if dbus.String(IFACE_DEVICE) in interfaces:
        self.connectToDevice(path)
      elif dbus.String(IFACE_GATT_CHARACTERISTIC) in interfaces:
        if str(interfaces[dbus.String(IFACE_GATT_CHARACTERISTIC)][dbus.String('UUID')])== UUID_SERIAL_NUMBER_CHARACTERISTIC:
          loggerTIMESTAMPred("SERIAL NUMBER Characteristic Interface available")
          #devicePath = self.convertServicePathToDevicePath(path)
          self.publisher.publish( ev.bluezEvents.SerialNumberCharacteristicInterfaceAdded, path )
          #loggerTIMESTAMPred(f"acknowledged with reply {reply} ")
      elif dbus.String(IFACE_GATT_SERVICE) in interfaces:
        if str(interfaces[dbus.String(IFACE_GATT_SERVICE)][dbus.String('UUID')])== UUID_GATESETUP_SERVICE :
          loggerTIMESTAMPred("GATE SETUP Service Interface available")
          #devicePath = self.convertServicePathToDevicePath(path)
          self.publisher.publish( ev.bluezEvents.GateSetupServiceInterfaceAdded, path )      
    except Exception as e:
      loggerERROR(f"Exception in  -interfaces added-: {e}")

  def convertServicePathToDevicePath(self, path):
    try:
      pathSplitted = path.split("/service")
      devicePath = pathSplitted[0]
      #loggerDEBUGdim(f"path: {path}; device path {devicePath}")
      return devicePath
    except Exception as e:
      loggerERROR(f"ERROR converting to device path: {e}")

  def convertPathToAddress(self, path):
    try:
      pathSplitted = path.split("/dev_")
      address = pathSplitted[1].replace("_",":")
      #loggerDEBUGredDIM(f"path: {path}; address {address}")
      return address
    except Exception as e:
      loggerERROR(f"ERROR converting to device path: {e}")

  def getDeviceInterface(self, path):
    deviceObject = self.systemBus.get_object( BLUEZ, path)
    return dbus.Interface( deviceObject, IFACE_DEVICE)

  def connectToDevice(self,path):
    try:
      deviceInterface = self.getDeviceInterface(path)
      loggerTIMESTAMPred("ASK TO CONNECT ",f" to device {path}")
      deviceInterface.Connect(path, dbus_interface=IFACE_DEVICE)
      loggerTIMESTAMPred("CONNECTED",f" to device {path}")
    except Exception as e:
      loggerERROR(f"ERROR on method Connect to Device: {e}")

  def propertiesChanged(self, interface, changed, invalidated, path):
    loggerTIMESTAMP(f"Properties Changed on path {path}")
    prettyPrint(changed)
    try:
      for key in changed:
        if str(key) == "Connected":
          loggerTIMESTAMPred("DEVICE CONNECTED", f"on path {path}")
        if str(key) == "ServicesResolved":
          self.publisher.publish(ev.bluezEvents.ServicesResolved, path)
          loggerTIMESTAMPred("SERVICES RESOLVED", f" on path {path}")
    except KeyError:
      loggerERROR(f"DEVICE REMOVED on path {path}")
    except Exception as e:
      loggerERROR(f"ERROR in Properties Changed (callback method): {e}")

  def connectThingsInTouchDevicesStoredLocally(self):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    self.thingsInTouchDevicesStoredLocally = {}
    for path in self.objects:
      if IFACE_DEVICE in self.objects[path]:
        deviceObject = self.systemBus.get_object(BLUEZ , path)
        deviceProperties = deviceObject.GetAll(IFACE_DEVICE, dbus_interface=IFACE_PROPERTIES_DBUS)
        self.thingsInTouchDevicesStoredLocally[str(path)]= {
          "Alias":            self.alias(path),
          "Address":          str(deviceProperties["Address"]),
          "Connected":        bool(deviceProperties["Connected"]),
          "ServicesResolved": False,
          "Services":         None,
          "deviceInterface":  self.getDeviceInterface(path),
          "SerialNumber":     None}
        loggerDEBUG(f"ThingsInTouch device stored locally on path: {path}")
        self.thingsInTouchDevicesStoredLocally[str(path)]["Services"] = self.getServicesOfDevice(path)
        gateServiceAvailable = UUID_GATESETUP_SERVICE in self.thingsInTouchDevicesStoredLocally[str(path)]["Services"]
        loggerDEBUGdim(f"Gate Service Available: {gateServiceAvailable}")
        if  gateServiceAvailable:
          loggerDEBUGredDIM("SERVICES AVAILABLE",f"on path {path}")
          self.connectToDevice(path)
          self.readCharacteristicStringValue( path, UUID_GATESETUP_SERVICE, UUID_SERIAL_NUMBER_CHARACTERISTIC)
          return f"DEVICE sucessfully connected on path {path}"
        else:
          loggerDEBUGredDIM("SERVICES NOT AVAILABLE",f" on path {path}")
          try:
            
            #self.discoverThingsInTouchDevices()
            address = self.convertPathToAddress(path)
            self.waitFor(ev.bluezEvents.GateSetupServiceInterfaceAdded, path)
            self.connectDeviceWithoutDiscovery(address)
            #self.connectToDevice(path)
            self.thingsInTouchDevicesStoredLocally[str(path)]["Services"] = self.getServicesOfDevice(path)
            self.readCharacteristicStringValue( path, UUID_GATESETUP_SERVICE, UUID_SERIAL_NUMBER_CHARACTERISTIC)
            return f"DEVICE sucessfully connected on path {path}"

          except Exception as e:
            return f"unable to connect DEVICE on path {path} with exception {e}"

  def waitFor(self, event, path):
    eventHappened = False
    loggerDEBUGredDIM(f"waiting for event ", f"{event} on path {path}")
    while not eventHappened:
      eventReceived, pathReceived = self.subscriber.receive()
      if eventReceived == str(event) and pathReceived.startswith(path):
        eventHappened = True
        loggerINFOredDIM(f"event {event}", f" happened on path {path}")
        #self.subscriber.reply("OK")

  def alias(self, path):
    return str(self.objects[path][IFACE_DEVICE]["Alias"])

  def deleteDevice(self, devicePath):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    for path in self.objects:
      if IFACE_ADAPTER in self.objects[path]:
        loggerDEBUGdim(f"path (adapter object): {path} -- devicePath (to delete): {devicePath} ")
        adapterObject =  self.systemBus.get_object(BLUEZ , path)
        adapterInterface = dbus.Interface(adapterObject, IFACE_ADAPTER)
        adapterInterface.RemoveDevice(devicePath)

  def readCharacteristicStringValue(self,devicePath, uuidService, uuidCharacteristic):
    characteristicObject = self.thingsInTouchDevicesStoredLocally[str(devicePath)]["Services"][uuidService]["Characteristics"][uuidCharacteristic]["CharacteristicObject"]
    characteristicObject.ReadValue({}, reply_handler= self.showReadStringValue,
        error_handler=self.genericErrorCallback, dbus_interface=IFACE_GATT_CHARACTERISTIC)

  def showReadStringValue(self, value):
    valueString = ''.join([str(v) for v in value])
    loggerTIMESTAMPred("READ CHARACTERISTIC ", f" Value {valueString}")

  def genericErrorCallback(self, error):
    print('D-Bus call failed: ' + str(error))







  def connectDeviceWithoutDiscovery(self,Address, AddressType ="public"):
    connectFilter ={}
    connectFilter["Address"]= str(Address)
    connectFilter["AddressType"]= str(AddressType)
    loggerTIMESTAMPred("just before asking to connect w/o discovery")
    try:
      deviceConnected = self.adapterInterface.ConnectDevice(connectFilter)
      loggerTIMESTAMPred("just after asking to connect w/o discovery")
      #prettyPrint(deviceConnected)
      return deviceConnected
    except Exception as e:
      loggerTIMESTAMPred(f"error while connecting w/o discovery: {e}")


  def enterThreadMainLoopGObject(self, exitFlag):
    self.mainloop = GObject.MainLoop()
    self.mainloop.run()

  def exitThreadMainLoopGobject(self):
    #self.deleteRegisteredDevices()

    self.mainloop.quit()
    self.threadMainLoop.join()

  def deleteRegisteredDevices(self):
    for devicePath in self.registeredDevices:
      self.deleteDevice(devicePath)
    self.updateRegisteredDevices()



    return True

  def updateRegisteredDevices(self):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    self.registeredDevices = {}
    for path in self.objects:
      if IFACE_DEVICE in self.objects[path]:
        deviceObject = self.systemBus.get_object(BLUEZ , path)
        deviceProperties = deviceObject.GetAll(IFACE_DEVICE, dbus_interface=IFACE_PROPERTIES_DBUS)
        connected = bool(deviceProperties["Connected"])
        self.registeredDevices[str(path)]= {
          "Alias":            self.alias(path),
          "Address":          str(deviceProperties["Address"]),
          "Connected":        bool(deviceProperties["Connected"]),
          #"Adapter":          deviceProperties["Adapter"],
          "ServicesResolved": False,
          "Services":         None,
          "deviceInterface":  self.getDeviceInterface(path),
          "SerialNumber":     None}
        print(f"updateRegisteredDevices -  path: {path}, connected: {connected} ")
        if connected:
          self.registeredDevices[str(path)]["Services"] = self.getServicesOfDevice(path)
          if  UUID_GATESETUP_SERVICE not in self.registeredDevices[str(path)]["Services"]:
            print(f"   ---- device not connected")
            self.registeredDevices[str(path)]["Connected"]= False
            # Set Property ["Connected"]= False
          else:
            print(f"   ---- services of connected devices")
            prettyPrint(self.registeredDevices[str(path)]["Services"])
            self.establishBluetoothConnection(path)
    return self.registeredDevices
  
  def isDeviceConnected(self, path):
    return bool(self.objects[path][IFACE_DEVICE]["Connected"])
  
  def alias(self, path):
    return str(self.objects[path][IFACE_DEVICE]["Alias"])

  def isServiceOfThingsInTouch(self, uuid):
    if str(uuid).startswith(UUID_BEGIN_THINGSINTOUCH):
      return True
    else:
      return False
  



  def getServicesOfDevice(self, devicePath):
    servicesOfDevice = {}

    characteristicsOfDevice = self.getCharacteristicsOfDevice(devicePath)

    for path in self.objects:
      if str(path).startswith(str(devicePath)):
        if IFACE_GATT_SERVICE in self.objects[path]:
          serviceObject = self.systemBus.get_object(BLUEZ , path)
          serviceProperties = serviceObject.GetAll(IFACE_GATT_SERVICE, dbus_interface=IFACE_PROPERTIES_DBUS)
          uuid = serviceProperties['UUID']
          if self.isServiceOfThingsInTouch(uuid):
            characteristicsOfService = {}
            for c in characteristicsOfDevice:
              if c.startswith(str(path)):
                characteristicObject = self.systemBus.get_object(BLUEZ , c)
                characteristicProperties = characteristicObject.GetAll(IFACE_GATT_CHARACTERISTIC, dbus_interface=IFACE_PROPERTIES_DBUS)
                characteristicsOfService[str(characteristicProperties['UUID'])]= {
                              "Path":str(c),
                              "Value":characteristicProperties['Value'],
                              "CharacteristicObject": characteristicObject}
            servicesOfDevice[str(uuid)]={"Path":str(path),"ServiceObject": serviceObject,
                                  "Characteristics":characteristicsOfService}

    # print("\n")
    # prettyPrint(servicesOfDevice)
    # print("\n")

    return servicesOfDevice



  def pairToDevice(self,path):
    self.registeredDevices[str(path)]["deviceInterface"].Pair(path, dbus_interface=IFACE_DEVICE)

  def disconnectAllDevices(self):
    for path in self.registeredDevices:
      self.disconnectDevice(path)
  
  def disconnectDevice(self, path):
    self.registeredDevices[str(path)]["deviceInterface"].Disconnect(path, dbus_interface=IFACE_DEVICE)


  def establishBluetoothConnection(self,devicePath):
    self.readCharacteristicStringValue( devicePath, UUID_GATESETUP_SERVICE, UUID_SERIAL_NUMBER_CHARACTERISTIC) # async answer


  def ensureDeviceKnown(self,path):
    # look into a list of known devices , checking the serial number
    # if it is not known, make it known .  Get approval from Odoo for a new device
    # and then make a new entry on the list of local known devices
    # if there is no approval from Odoo, this Method returns False
    return True

  def getCharacteristicsOfDevice(self, devicePath):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    characteristics = []
    for path in self.objects:
      if str(path).startswith(str(devicePath)):
        if IFACE_GATT_CHARACTERISTIC in self.objects[path]:
          characteristics.append(str(path))

    # print("\n")
    # prettyPrint(characteristics)   
    # print("\n")

    return characteristics

  def updateRegisteredServices(self,devicePath):
    self.updateCharacteristics()




  def launchThreadForNewDevice(self,devicePath):
    prettyPrint(self.updateRegisteredDevices())
    self.counterTimeToConnect = time.time()
    print("TIMESTAMP (ms) - asked to connect : ", nowInSecondsAndMilliseconds())
    self.connectToDevice(devicePath)
    #self.flagToExit = True

  def aliasFromThingsInTouch(self, alias):
    if alias.startswith(ALIAS_THINGSINTOUCH_BEGINING):
      return True
    else:
      return False

  def setAdvertisementInterval(self,interval):
    '''
    interval is an int as string
    interval in units of 1,25ms - 
    Advertising packets are sent periodically on each advertising channel.
    The time interval has a fixed interval and a random delay.
    The interval is specified between the set of 3 packets (and 3 channels are almost always used).

    You can set the fixed interval from 20ms to 10.24 seconds, in steps of 0.625ms.
    The random delay is a pseudo-random value from 0ms to 10ms that is automatically added. 
    This randomness helps reduce the possibility of collisions between advertisements of different devices 
    (if they fell in the same rate, they could interfere more easily).
    '''
    os.environ['ADVMININTERVAL'] = interval
    os.environ['ADVMAXINTERVAL'] = interval
    self.runShellCommand("echo $ADVMININTERVAL | sudo tee /sys/kernel/debug/bluetooth/hci0/adv_min_interval > /dev/null")
    self.runShellCommand("echo $ADVMAXINTERVAL | sudo tee /sys/kernel/debug/bluetooth/hci0/adv_max_interval > /dev/null")

  # def runShellCommand(self, command):
  #   try:
  #     completed = subprocess.run(command.split())
  #     loggerDEBUG(f'command {command} - returncode: {completed.returncode}')
  #   except:
  #     loggerERROR(f"error on method run shell command: {command}")       
