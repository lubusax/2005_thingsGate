import time
import zmq
import itertools

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from log.logger import logger
from random import randrange

class zmqLazyPirateRequester():

  def __init__(self, port, timeout=2500, retries=3):
    self.requestTimeout = timeout # in ms
    self.requestRetries = retries
    self.replierEndpoint = "tcp://localhost:"+port
    self.context = zmq.Context()
    self.connectToReplier()

  def connectToReplier(self):
    logger("Connecting to server…")
    self.requester = self.context.socket(zmq.REQ)
    self.requester.connect(self.replierEndpoint)

  def closeAndRemoveSocket(self):
    self.requester.setsockopt(zmq.LINGER, 0)
    self.requester.close()

  def send(self, message):
    #request = str(message).encode()
    request = message
    for _ in range(self.requestRetries):
      logger(f"Sending {request}")
      self.requester.send_pyobj(request)
      if (self.requester.poll(self.requestTimeout) & zmq.POLLIN) != 0:
        reply = self.requester.recv_pyobj()
        if reply == "OK":
          logger(f"Replier replied OK: {reply}")
          return "Replier replied OK"
        else:
          logger(f"Server replied, but it was not an OK:  {reply}")
      logger("No response from replier")
      self.closeAndRemoveSocket()    # Socket is confused. Close and remove it.
      logger("Reconnecting to replier…")
      self.connectToReplier()    # Create new connection

    logger("Replier seems to be offline, abandoning")
    return "Replier seems to be offline"

class zmqLazyPirateReplier():
    def __init__(self, port):
      self.replierEndpoint = "tcp://*:"+port
      self.context = zmq.Context()
      self.replier = self.context.socket(zmq.REP)
      self.replier.bind(self.replierEndpoint)

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
    logger(Fore.GREEN + f"time STAMP: {time.ctime()}; topic:{topic}; message: {message} " + Style.RESET_ALL)
    return topic, message

class zmqPublisher():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind("tcp://*:"+port)
    self.port=port

  def publish(self, topic, message):
    logger(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    string= topic+" "+ message
    self.socket.send_string(string)

class zmqRequester():

  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REQ)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def request(self, topic, message):
    logger(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
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
    logger(Fore.RED + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    return topic, message
  
  def reply(self, topic, message):
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
