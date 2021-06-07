import sys
import dbus 
from gi.repository import GLib, GObject
from bluetooth.genericClassesBLE import Application, Advertisement, Service, Characteristic
from pprint import PrettyPrinter
import time
from dbus.mainloop.glib import DBusGMainLoop

prettyPrint = PrettyPrinter(indent=1).pprint

BLUEZ =                        'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
ADAPTER_IFACE =                'org.Bluez.Adapter1'

PATH_HCI0 =                    '/org/bluez/hci0'

UUID_GATESETUP_SERVICE      = '5468696e-6773-496e-546f-756368000100'
# ThingsInTouch Services        go from 0x001000 to 0x001FFF
# ThingsInTouch Characteristics go from 0x100000 to 0x1FFFFF

UUID_READ_WRITE_TEST_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100000'
UUID_NOTIFY_TEST_CHARACTERISTIC         = '5468696e-6773-496e-546f-756368100001'
UUID_SERIAL_NUMBER_CHARACTERISTIC       = '5468696e-6773-496e-546f-756368100002'
UUID_DEVICE_TYPE_CHARACTERISTIC         = '5468696e-6773-496e-546f-756368100003'

DEVICE_NAME = 'ThingsInTouch-RAS'

class SerialNumberCharacteristic(Characteristic):
    """
    S/N
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_SERIAL_NUMBER_CHARACTERISTIC 
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.serialNumber = "20200818.000.000.001"
        self.value = self.serialNumber.encode()
        self.notifying = False

    def ReadValue(self, options):
        print("Serial Number Read: {}".format(self.value))
        return self.value

class DeviceTypeCharacteristic(Characteristic):
    """
    DeviceType
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_DEVICE_TYPE_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.deviceType = "001.000.000.000.000" # Test Device
        self.value = self.deviceType.encode()
        self.notifying = False

    def ReadValue(self, options):
        print("Device Type Read: {}".format(self.value))
        return self.value

class ReadAndWriteTestCharacteristic(Characteristic):
    """
    Dummy test characteristic. Gives "now" while read. And can be written to
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_READ_WRITE_TEST_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read','write'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.value = []
        self.notifying = False

    def ReadValue(self, options):
        now = time.asctime()
        print("TestCharacteristic Read: {}".format(now))
        self.value = now.encode()
        #print(type(self.value))
        return self.value

    def WriteValue(self, value, options):
        valueString =""
        for i in range(0,len(value)):
            valueString+= str(value[i])
        print('TestCharacteristic on index {} was written : {}'.format(self.index, valueString))      
        self.value = value
        self.valueString = valueString

class NotifyTestCharacteristic(Characteristic):
    """
    Fake Battery Level characteristic. The battery level is drained by 2 points
    every "self.period" milliseconds.

    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_NOTIFY_TEST_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__( self, self.bus, self.index, self.uuid, ['read', 'notify'], service)
        self.notifying = False
        self.battery_lvl = 100
        self.period = 1000 # in ms
        GObject.timeout_add(self.period, self.drain_battery)

    def notify_battery_level(self):
        if not self.notifying: return
        self.PropertiesChanged( GATT_CHRC_IFACE, { 'Value': [dbus.Byte(self.battery_lvl)] }, [])

    def drain_battery(self):
        if self.battery_lvl > 0:    self.battery_lvl -= 2
        else:                       self.battery_lvl = 100
        print('Battery Level drained: ' + repr(self.battery_lvl))
        if self.notifying:          self.notify_battery_level()
        return True

    def ReadValue(self, options):
        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
        else:
            self.notifying = True
            self.notify_battery_level()

    def StopNotify(self):
        if self.notifying:
            self.notifying = False
        else:
            print('Not notifying, nothing to do')

class GateSetupService(Service):
    """
    Service that exposes Gate Device Information and allows for the Setup
    """
    def __init__(self, bus):
        Service.__init__(self, bus, UUID_GATESETUP_SERVICE)
        self.add_characteristic(ReadAndWriteTestCharacteristic(self))
        self.add_characteristic(NotifyTestCharacteristic(self))
        self.add_characteristic(SerialNumberCharacteristic(self))
        self.add_characteristic(DeviceTypeCharacteristic(self))

class GateSetupApplication(Application):
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        Application.__init__(self, bus)
        self.add_service(GateSetupService(bus))

class GateSetupAdvertisement(Advertisement):
    def __init__(self):
        bus = dbus.SystemBus()
        index = 0
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid( UUID_GATESETUP_SERVICE) 
        self.add_local_name( DEVICE_NAME)
        self.add_alias( DEVICE_NAME)
        self.include_tx_power = True
        self.setAdvertisementInterval("90")

