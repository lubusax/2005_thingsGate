from enum import Enum, auto, unique

@unique
class port(Enum):
  bluez             = "5565"
  deviceManager     = "5566"