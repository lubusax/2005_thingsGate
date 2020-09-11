from enum import Enum, auto, unique

@unique
class bluezEvents(Enum):
  SerialNumberRead                          = auto()
  ServicesResolved                          = auto()
  SerialNumberCharacteristicInterfaceAdded  = auto()
  GateSetupServiceInterfaceAdded            = auto()

@unique
class deviceManagerEvents(Enum):
  deviceConnected                           = auto()
