from enum import Enum, auto, unique

@unique
class orgBluezEnums(Enum):
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


@unique
class thingsInTouchEnums(Enum):
  # ThingsInTouch Services        go from 0x001000 to 0x001FFF
  # ThingsInTouch Characteristics go from 0x100000 to 0x1FFFFF
  UUID_GATESETUP_SERVICE      				= '5468696e-6773-496e-546f-756368000100'
  ALIAS_THINGSINTOUCH_BEGINING				= 'ThingsInTouch'

  UUID_READ_WRITE_TEST_CHARACTERISTIC = '5468696e-6773-496e-546f-756368100000'
  UUID_NOTIFY_TEST_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100001'
  UUID_SERIAL_NUMBER_CHARACTERISTIC   = '5468696e-6773-496e-546f-756368100002'
  UUID_DEVICE_TYPE_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100003'

  UUID_BEGIN_THINGSINTOUCH            = '5468696e-6773-496e-546f-756368'

  DEVICE_NAME 												= 'ThingsInTouch-Gate-01'