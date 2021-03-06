import time
import zmq
import itertools
import pickle

import log.logger as l
from random import randrange

class SubscriberMultipart():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect(f"tcp://localhost:{port}")
    self.port=port

  def subscribe(self, topic):
    l.loggerDEBUGredDIM(f"SUBSCRIPTION TO TOPIC: {topic}")
    self.socket.setsockopt(zmq.SUBSCRIBE, str(topic).encode('utf-8'))

  def receive(self):
    topic_bytes, message_bytes = self.socket.recv_multipart() # this call is blocking
    topic = topic_bytes.decode('utf-8')
    message = pickle.loads(message_bytes)
    l.loggerTIMESTAMPgreen(f"received TOPIC: {topic}",f"; MESSAGE: {message}")
    return topic, message

class PublisherMultipart():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind(f"tcp://*:{port}")
    self.port=port

  def publish(self, topic, message):
    l.loggerTIMESTAMPcyan(f"published TOPIC: {topic}",f"; MESSAGE: {message}")
    topic_bytes = str(topic).encode('utf-8')
    message_bytes = pickle.dumps(message)
    self.socket.send_multipart([topic_bytes, message_bytes])


def cleanPort(port):
  context = zmq.Context()
  replier = context.socket(zmq.REP)
  l.loggerINFOredDIM(f"Socket on port {port} closed?", f" {replier.closed}")
  if not replier.closed:
    replier.close()
  l.loggerINFOredDIM(f"Socket on port {port} closed?", f" {replier.closed}")

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
    l.loggerDEBUG("Connecting to server…")
    self.requester = self.context.socket(zmq.REQ)
    self.requester.connect(self.replierEndpoint)

  def closeAndRemoveSocket(self):
    self.requester.setsockopt(zmq.LINGER, 0)
    self.requester.close()

  def send(self, message):
    #request = str(message).encode()
    request = message
    for _ in range(self.requestRetries):
      l.loggerDEBUG(f"Sending {request}")
      self.requester.send_pyobj(request)
      if (self.requester.poll(self.requestTimeout) & zmq.POLLIN) != 0:
        reply = self.requester.recv_pyobj()
        if reply == "OK":
          l.loggerDEBUG(f"Replier replied OK: {reply}")
          return "Replier replied OK"
        else:
          l.loggerWARNING(f"Server replied, but it was not an OK:  {reply}")
      l.loggerERROR("No response from replier")
      self.closeAndRemoveSocket()    # Socket is confused. Close and remove it.
      l.loggerDEBUG("Reconnecting to replier…")
      self.connectToReplier()    # Create new connection

    l.loggerERROR("Replier seems to be offline, abandoning")
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
      l.loggerERRORredDIM("ERROR while binding the REPLIER", f": {e}")


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
    self.socket.setsockopt_string(zmq.SUBSCRIBE, str(topic))

  def receive(self):
    string = self.socket.recv_string() # this call is blocking
    topic, message = string.split()
    l.loggerTIMESTAMPgreen(f"TOPIC: {topic}",f"; MESSAGE: {message}")
    return topic, message

class zmqPublisher():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind("tcp://*:"+port)
    self.port=port

  def publish(self, topic, message):
    l.loggerTIMESTAMPcyan(f"TOPIC: {topic}",f"; MESSAGE: {message}")
    string= str(topic)+" "+ message
    self.socket.send_string(string)

class zmqRequester():

  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REQ)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def request(self, topic, message):
    l.loggerTIMESTAMPcyan(f"TOPIC: {topic}",f"; MESSAGE: {message}")
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
    l.loggerTIMESTAMPgreen(f"TOPIC: {topic}",f"; MESSAGE: {message}")
    return topic, message
  
  def reply(self, topic, message):
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
