import requests, json, logging
from internet.internet import internetAccess,getInternet

_logger = logging.getLogger(__name__)

class Gate:

  def __init__(self,dirPath):
    self.dirPath = dirPath
    self.thingsGateFilePath = self.dirPath+'/data/thingsGate.json'
    self.setParams()
    _logger.debug("Gate Class Initialized")

  def setParams(self):
    _logger.debug("Params file is %s " % self.thingsGateFilePath)
    thingsGateFile = open(self.thingsGateFilePath)
    self.thingsGateDict = json.load(thingsGateFile)["thingsGate"]
    thingsGateFile.close()
    self.gateRegistered = True if (
      self.thingsGateDict["registered"]=="yes") else False
    print("gate registered: %s" % self.gateRegistered)
    
    # self.db = self.thingsGateDict["db"][0]
    # self.user = self.thingsGateDict["user_name"][0]
    # self.pswd = self.thingsGateDict["user_password"][0]
    # self.host = self.thingsGateDict["odoo_host"][0]
    # self.port = self.thingsGateDict["odoo_port"][0]

    # self.adm = self.thingsGateDict["admin_id"][0]
    # self.tz = self.thingsGateDict["timezone"][0]

    # os.environ["TZ"] = tz_dic.tz_dic[self.tz]
    # time.tzset()

    # if "https" not in self.thingsGateDict:
    #     self.https_on = False
    # else:
    #     self.https_on = True

    # if self.https_on:
    #     if self.port:
    #         self.url_template = "https://%s:%s" % (self.host, self.port)
    #     else:
    #         self.url_template = "https://%s" % self.host
    # else:
    #     if self.port:
    #         self.url_template = "http://%s:%s" % (self.host, self.port)
    #     else:
    #         self.url_template = "http://%s" % self.host

    # self.uid = self._get_user_id()

  def internetSetup(self):
    while not internetAccess():
      getInternet()
    return True
  
  def odooSetup(self):
    return True

  def gateSetup(self):
    self.internetSetup()
    self.odooSetup()
    return True



def gateInit(dirPath):

  print("gate init -has begun ")
  G = Gate(dirPath)
  if not G.gateRegistered:
    G.gateSetup()
  print("gate init- has ended ") 
