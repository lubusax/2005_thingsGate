import time
import zmq
import itertools

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from log.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL, loggerINFOredDIM, loggerERRORredDIM
from random import randrange

def cleanPort(port):
  context = zmq.Context()
  replierEndpoint = "tcp://localhost:"+port
  replier = context.socket(zmq.REP)
  requester = context.socket(zmq.REQ)
  loggerINFOredDIM(f"Socket on port {port} closed?", f" {replier.closed}")
  if not replier.closed:
    #replier.unbind(replierEndpoint)
    replier.close()
  loggerINFOredDIM(f"Socket on port {port} closed?", f" {replier.closed}")

class Requester():
  '''
    zmq Lazy Pirate Client (Requester)
  '''
  def __init__(self, port, timeout=2500, retries=3):
    self.requestTimeout = timeout # in ms
    self.requestRetries = retries
    self.replierEndpoint = "tcp://localhost:"+port
    self.context = zmq.Context()
    self.connectToReplier()

  def connectToReplier(self):
    loggerDEBUG("Connecting to server…")
    self.requester = self.context.socket(zmq.REQ)
    self.requester.connect(self.replierEndpoint)

  def closeAndRemoveSocket(self):
    self.requester.setsockopt(zmq.LINGER, 0)
    self.requester.close()

  def send(self, message):
    #request = str(message).encode()
    request = message
    for _ in range(self.requestRetries):
      loggerDEBUG(f"Sending {request}")
      self.requester.send_pyobj(request)
      if (self.requester.poll(self.requestTimeout) & zmq.POLLIN) != 0:
        reply = self.requester.recv_pyobj()
        if reply == "OK":
          loggerDEBUG(f"Replier replied OK: {reply}")
          return "Replier replied OK"
        else:
          loggerWARNING(f"Server replied, but it was not an OK:  {reply}")
      loggerERROR("No response from replier")
      self.closeAndRemoveSocket()    # Socket is confused. Close and remove it.
      loggerDEBUG("Reconnecting to replier…")
      self.connectToReplier()    # Create new connection

    loggerERROR("Replier seems to be offline, abandoning")
    return "Replier seems to be offline"

class Replier():
  '''
    zmq Lazy Pirate Server (Replier)
  '''
  def __init__(self, port):
    self.replierEndpoint = "tcp://*:"+port
    self.context = zmq.Context()
    self.replier = self.context.socket(zmq.REP)
    try:
      self.replier.bind(self.replierEndpoint)
    except Exception as e:
      loggerERRORredDIM("ERROR while binding the REPLIER", f": {e}")


  def receive(self):
    self.requestMessage = self.replier.recv_pyobj()
    return self.requestMessage

  def reply(self,replyMessage):
    self.replier.send_pyobj(replyMessage)

class zmqSubscriber():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def subscribe(self, topic):
    self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

  def receive(self):
    string = self.socket.recv_string() # this call is blocking
    topic, message = string.split()
    loggerDEBUG(Fore.GREEN + f"time STAMP: {time.ctime()}; topic:{topic}; message: {message} " + Style.RESET_ALL)
    return topic, message

class zmqPublisher():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind("tcp://*:"+port)
    self.port=port

  def publish(self, topic, message):
    loggerDEBUG(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    string= topic+" "+ message
    self.socket.send_string(string)

class zmqRequester():

  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REQ)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def request(self, topic, message):
    loggerDEBUG(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
    message = self.socket.recv()
    answerString = str(message, 'utf-8')
    topic, message = answerString.split()
    return topic, message

class zmqReplier():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REP)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def receive(self):
    message = self.socket.recv()
    answerString = str(message, 'utf-8')
    topic, message = answerString.split()
    loggerDEBUG(Fore.RED + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    return topic, message
  
  def reply(self, topic, message):
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
