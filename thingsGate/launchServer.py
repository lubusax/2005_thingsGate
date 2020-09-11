from bluetooth.server import server as server

import log.logger as l

try:
  server()
except Exception as e:
  l.loggerERRORredDIM(f"{e}")