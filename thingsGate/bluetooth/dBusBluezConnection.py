# connectDeviceWithoutDiscovery needs flag --experimental on the bluetooth service (daemon bluetoothd)
# https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation#enable-bluetooth-low-energy-features
# https://pythonhosted.org/txdbus/dbus_overview.html


import  time
import  threading
import  os
import  subprocess

import  dbus
from    dbus.mainloop.glib              import  DBusGMainLoop
from    gi.repository                   import  GObject

import  common.enumsEvents              as      ev
import  log.logger                      as      l
  
from    bluetooth.thingsSpecificClasses import  Thing
from    common.common                   import  prettyPrint
from    common.enumsPorts               import  port
from    common.enumsDbusBluez           import  orgBluezEnums         as bluezEnum
from    common.enumsDbusBluez           import  thingsInTouchEnums    as thingsEnum
from    common.common                   import  nowInSecondsAndMilliseconds, runShellCommand
from    messaging.messaging             import  zmqSubscriber, zmqPublisher


class dBusBluezConnection():
  def __init__(self):
    
    l.loggerTIMESTAMP("__init__ class dBusBluezConnection")

    DBusGMainLoop(set_as_default=True)

    self.systemBus 	                = dbus.SystemBus()

    self.hci0 	                    = self.systemBus.get_object(bluezEnum.BLUEZ.value, bluezEnum.PATH_HCI0.value)
    self.bluez                      = self.systemBus.get_object(bluezEnum.BLUEZ.value , "/")
    self.adapterInterface           = dbus.Interface( self.hci0,   bluezEnum.IFACE_ADAPTER.value)
    self.objectManagerInterface     = dbus.Interface(self.bluez, bluezEnum.IFACE_OBJECT_MANAGER_DBUS.value)

    self.portForBluezEvents   = port.bluez.value
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
    scanFilter['UUIDs'] 			= [thingsEnum.UUID_GATESETUP_SERVICE.value]
    self.adapterInterface.SetDiscoveryFilter(scanFilter)
    self.adapterInterface.StartDiscovery()

  def listenToPropertiesChanged(self):
    self.systemBus.add_signal_receiver(self.propertiesChanged, dbus_interface = bluezEnum.IFACE_PROPERTIES_DBUS.value,
                        signal_name = "PropertiesChanged", arg0 = bluezEnum.IFACE_DEVICE.value, path_keyword = "path")

  def listenToInterfacesAdded(self):
    self.systemBus.add_signal_receiver(self.interfacesAdded, dbus_interface = bluezEnum.IFACE_OBJECT_MANAGER_DBUS.value,
                        signal_name = "InterfacesAdded")

  def interfacesAdded(self, path, interfaces):
    l.loggerTIMESTAMP("Interfaces Added")
    l.loggerDEBUGdim(f"An interface was added on path: {path}")
    prettyPrint(interfaces)
    try:
      if dbus.String(bluezEnum.IFACE_DEVICE.value) in interfaces:
        self.connectToDevice(path)
      elif dbus.String(bluezEnum.IFACE_GATT_CHARACTERISTIC.value) in interfaces:
        if str(interfaces[dbus.String(bluezEnum.IFACE_GATT_CHARACTERISTIC.value)][dbus.String('UUID')])== thingsEnum.UUID_SERIAL_NUMBER_CHARACTERISTIC.value:
          l.loggerTIMESTAMPred("SERIAL NUMBER Characteristic Interface available")
          self.publisher.publish( ev.bluezEvents.SerialNumberCharacteristicInterfaceAdded, path )
      elif dbus.String(bluezEnum.IFACE_GATT_SERVICE.value) in interfaces:
        if str(interfaces[dbus.String(bluezEnum.IFACE_GATT_SERVICE.value)][dbus.String('UUID')])== thingsEnum.UUID_GATESETUP_SERVICE.value :
          l.loggerTIMESTAMPred("GATE SETUP Service Interface available")
          self.publisher.publish( ev.bluezEvents.GateSetupServiceInterfaceAdded, path )      
    except Exception as e:
      l.loggerERROR(f"Exception in  -interfaces added-: {e}")

  def convertServicePathToDevicePath(self, path):
    try:
      pathSplitted = path.split("/service")
      devicePath = pathSplitted[0]
      #l.loggerDEBUGdim(f"path: {path}; device path {devicePath}")
      return devicePath
    except Exception as e:
      l.loggerERROR(f"ERROR converting to device path: {e}")

  def convertPathToAddress(self, path):
    try:
      pathSplitted = path.split("/dev_")
      address = pathSplitted[1].replace("_",":")
      #l.loggerDEBUGredDIM(f"path: {path}; address {address}")
      return address
    except Exception as e:
      l.loggerERROR(f"ERROR converting to device path: {e}")

  def getDeviceInterface(self, path):
    deviceObject = self.systemBus.get_object( bluezEnum.BLUEZ.value, path)
    return dbus.Interface( deviceObject, bluezEnum.IFACE_DEVICE.value)

  def connectToDevice(self,path):
    try:
      deviceInterface = self.getDeviceInterface(path)
      l.loggerTIMESTAMPred("ASK TO CONNECT ",f" to device {path}")
      deviceInterface.Connect(path, dbus_interface=bluezEnum.IFACE_DEVICE.value)
      l.loggerTIMESTAMPred("CONNECTED",f" to device {path}")
    except Exception as e:
      l.loggerERROR(f"ERROR on method Connect to Device: {e}")

  def propertiesChanged(self, interface, changed, invalidated, path):
    l.loggerTIMESTAMP(f"Properties Changed on path {path}")
    prettyPrint(changed)
    try:
      for key in changed:
        if str(key) == "Connected":
          l.loggerTIMESTAMPred("DEVICE CONNECTED", f"on path {path}")
        if str(key) == "ServicesResolved":
          self.publisher.publish(ev.bluezEvents.ServicesResolved, path)
          l.loggerTIMESTAMPred("SERVICES RESOLVED", f" on path {path}")
    except KeyError:
      l.loggerERROR(f"DEVICE REMOVED on path {path}")
    except Exception as e:
      l.loggerERROR(f"ERROR in Properties Changed (callback method): {e}")

  def connectThingsInTouchDevicesStoredLocally(self):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    self.thingsInTouchDevicesStoredLocally = {}
    for path in self.objects:
      if bluezEnum.IFACE_DEVICE.value in self.objects[path]:
        deviceObject = self.systemBus.get_object(bluezEnum.BLUEZ.value , path)
        deviceProperties = deviceObject.GetAll(bluezEnum.IFACE_DEVICE.value, dbus_interface=bluezEnum.IFACE_PROPERTIES_DBUS.value)
        self.thingsInTouchDevicesStoredLocally[str(path)]= {
          "Alias":            self.alias(path),
          "Address":          str(deviceProperties["Address"]),
          "Connected":        bool(deviceProperties["Connected"]),
          "ServicesResolved": False,
          "Services":         None,
          "deviceInterface":  self.getDeviceInterface(path),
          "SerialNumber":     None}
        l.loggerDEBUG(f"ThingsInTouch device stored locally on path: {path}")
        self.thingsInTouchDevicesStoredLocally[str(path)]["Services"] = self.getServicesOfDevice(path)
        gateServiceAvailable = thingsEnum.UUID_GATESETUP_SERVICE.value in self.thingsInTouchDevicesStoredLocally[str(path)]["Services"]
        l.loggerDEBUGdim(f"Gate Service Available: {gateServiceAvailable}")
        if  gateServiceAvailable:
          l.loggerDEBUGredDIM("SERVICES AVAILABLE",f"on path {path}")
          self.connectToDevice(path)
          self.readCharacteristicStringValue( path, thingsEnum.UUID_GATESETUP_SERVICE.value, thingsEnum.UUID_SERIAL_NUMBER_CHARACTERISTIC.value)
          return f"DEVICE sucessfully connected on path {path}"
        else:
          l.loggerDEBUGredDIM("SERVICES NOT AVAILABLE",f" on path {path}")
          try:
            
            #self.discoverThingsInTouchDevices()
            address = self.convertPathToAddress(path)
            self.waitFor(ev.bluezEvents.GateSetupServiceInterfaceAdded, path)
            self.connectDeviceWithoutDiscovery(address)
            #self.connectToDevice(path)
            self.thingsInTouchDevicesStoredLocally[str(path)]["Services"] = self.getServicesOfDevice(path)
            self.readCharacteristicStringValue( path, thingsEnum.UUID_GATESETUP_SERVICE.value, thingsEnum.UUID_SERIAL_NUMBER_CHARACTERISTIC.value)
            return f"DEVICE sucessfully connected on path {path}"

          except Exception as e:
            return f"unable to connect DEVICE on path {path} with exception {e}"

  def waitFor(self, event, path):
    eventHappened = False
    l.loggerDEBUGredDIM(f"waiting for event ", f"{event} on path {path}")
    while not eventHappened:
      eventReceived, pathReceived = self.subscriber.receive()
      if eventReceived == str(event) and pathReceived.startswith(path):
        eventHappened = True
        l.loggerINFOredDIM(f"event {event}", f" happened on path {path}")
        #self.subscriber.reply("OK")

  def alias(self, path):
    return str(self.objects[path][bluezEnum.IFACE_DEVICE.value]["Alias"])

  def deleteDevice(self, devicePath):
    self.objects = self.objectManagerInterface.GetManagedObjects()
    for path in self.objects:
      if bluezEnum.IFACE_ADAPTER.value in self.objects[path]:
        l.loggerDEBUGdim(f"path (adapter object): {path} -- devicePath (to delete): {devicePath} ")
        adapterObject =  self.systemBus.get_object(bluezEnum.BLUEZ.value , path)
        adapterInterface = dbus.Interface(adapterObject, bluezEnum.IFACE_ADAPTER.value)
        adapterInterface.RemoveDevice(devicePath)

  def readCharacteristicStringValue(self,devicePath, uuidService, uuidCharacteristic):
    characteristicObject = self.thingsInTouchDevicesStoredLocally[str(devicePath)]["Services"][uuidService]["Characteristics"][uuidCharacteristic]["CharacteristicObject"]
    characteristicObject.ReadValue({}, reply_handler= self.showReadStringValue,
        error_handler=self.genericErrorCallback, dbus_interface=bluezEnum.IFACE_GATT_CHARACTERISTIC.value)

  def showReadStringValue(self, value):
    valueString = ''.join([str(v) for v in value])
    l.loggerTIMESTAMPred("READ CHARACTERISTIC ", f" Value {valueString}")

  def genericErrorCallback(self, error):
    print('D-Bus call failed: ' + str(error))







  def connectDeviceWithoutDiscovery(self,Address, AddressType ="public"):
    connectFilter ={}
    connectFilter["Address"]= str(Address)
    connectFilter["AddressType"]= str(AddressType)
    l.loggerTIMESTAMPred("just before asking to connect w/o discovery")
    try:
      deviceConnected = self.adapterInterface.ConnectDevice(connectFilter)
      l.loggerTIMESTAMPred("just after asking to connect w/o discovery")
      #prettyPrint(deviceConnected)
      return deviceConnected
    except Exception as e:
      l.loggerTIMESTAMPred(f"error while connecting w/o discovery: {e}")


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
      if bluezEnum.IFACE_DEVICE.value in self.objects[path]:
        deviceObject = self.systemBus.get_object(bluezEnum.BLUEZ.value , path)
        deviceProperties = deviceObject.GetAll(bluezEnum.IFACE_DEVICE.value, dbus_interface=bluezEnum.IFACE_PROPERTIES_DBUS.value)
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
          if  thingsEnum.UUID_GATESETUP_SERVICE.value not in self.registeredDevices[str(path)]["Services"]:
            print(f"   ---- device not connected")
            self.registeredDevices[str(path)]["Connected"]= False
            # Set Property ["Connected"]= False
          else:
            print(f"   ---- services of connected devices")
            prettyPrint(self.registeredDevices[str(path)]["Services"])
            self.establishBluetoothConnection(path)
    return self.registeredDevices
  
  def isDeviceConnected(self, path):
    return bool(self.objects[path][bluezEnum.IFACE_DEVICE.value]["Connected"])
  
  def alias(self, path):
    return str(self.objects[path][bluezEnum.IFACE_DEVICE.value]["Alias"])

  def isServiceOfThingsInTouch(self, uuid):
    if str(uuid).startswith(thingsEnum.UUID_BEGIN_THINGSINTOUCH.value):
      return True
    else:
      return False
  



  def getServicesOfDevice(self, devicePath):
    servicesOfDevice = {}

    characteristicsOfDevice = self.getCharacteristicsOfDevice(devicePath)

    for path in self.objects:
      if str(path).startswith(str(devicePath)):
        if bluezEnum.IFACE_GATT_SERVICE.value in self.objects[path]:
          serviceObject = self.systemBus.get_object(bluezEnum.BLUEZ.value , path)
          serviceProperties = serviceObject.GetAll(bluezEnum.IFACE_GATT_SERVICE.value, dbus_interface=bluezEnum.IFACE_PROPERTIES_DBUS.value)
          uuid = serviceProperties['UUID']
          if self.isServiceOfThingsInTouch(uuid):
            characteristicsOfService = {}
            for c in characteristicsOfDevice:
              if c.startswith(str(path)):
                characteristicObject = self.systemBus.get_object(bluezEnum.BLUEZ.value , c)
                characteristicProperties = characteristicObject.GetAll(bluezEnum.IFACE_GATT_CHARACTERISTIC.value, dbus_interface=bluezEnum.IFACE_PROPERTIES_DBUS.value)
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
    self.registeredDevices[str(path)]["deviceInterface"].Pair(path, dbus_interface=bluezEnum.IFACE_DEVICE.value)

  def disconnectAllDevices(self):
    for path in self.registeredDevices:
      self.disconnectDevice(path)
  
  def disconnectDevice(self, path):
    self.registeredDevices[str(path)]["deviceInterface"].Disconnect(path, dbus_interface=bluezEnum.IFACE_DEVICE.value)


  def establishBluetoothConnection(self,devicePath):
    self.readCharacteristicStringValue( devicePath, thingsEnum.UUID_GATESETUP_SERVICE.value, thingsEnum.UUID_SERIAL_NUMBER_CHARACTERISTIC.value) # async answer


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
        if bluezEnum.IFACE_GATT_CHARACTERISTIC.value in self.objects[path]:
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
    if alias.startswith(thingsEnum.ALIAS_THINGSINTOUCH_BEGINING.value):
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
  #     l.loggerDEBUG(f'command {command} - returncode: {completed.returncode}')
  #   except:
  #     l.loggerERROR(f"error on method run shell command: {command}")       
