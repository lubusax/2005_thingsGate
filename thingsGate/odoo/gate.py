import requests,json, logging

_logger = logging.getLogger(__name__)

class Gate:

  def __init__(self,dirPath):
    self.dirPath = dirPath
    self.thingsGateFilePath = self.dirPath+'/data/thingsGate.json'
    _logger.debug("Gate Class Initialized")



  def gateRegistered(self):
    ''' returns true if the Gate has succesfully been registered in Odoo
    in the past. This condition is signaled by a flag 
    in the local file thingsGate.json '''

    thingsGateFile = open(self.thingsGateFilePath,'r')
    thingsGateDict = json.load(thingsGateFile)
    print(thingsGateDict)
    return True

  def registerGate():
    return True



def gateInit(dirPath):

  print("ensure Gate Registered (on Odoo) module - has begun ")
  G = Gate(dirPath)
  if not G.gateRegistered():
    G.registerGate()
  print("ensure Gate Registered (on Odoo) module - has ended ") 
