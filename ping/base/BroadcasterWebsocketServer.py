#!/usr/bin/python

from threading import Thread
from time import sleep
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
import Queue

clients = []
debug = False
dataQ=Queue.Queue()

class WebsocketBroadcasterHandler(WebSocket):

    def handleMessage(self):
        dataQ.put(self.data)

        #self.sendMessage(self.data)


    def handleConnected(self):
        if debug:
            print (self.address, 'connected')
        clients.append(self)

    def handleClose(self):
        if debug:
            print (self.address, 'closed')
        clients.remove(self)


class BroadcasterWebsocketServer(Thread):

    def __init__(self, host, port,incomingQ, debugInfo=False):
        Thread.__init__(self)
        self.server = SimpleWebSocketServer(host, port, WebsocketBroadcasterHandler)
        self._isClosed = False
        global debug
        debug = debugInfo
#        incomingQ=dataQ
        self.setDaemon(True)

    def getQ(self):
        return dataQ

    def start(self):
        super(BroadcasterWebsocketServer, self).start()

    def run(self):
        if debug:
            print ('starting server')
        self.server.serveforever()

    def stop(self):
        if debug:
            print ('closing server')
        self.server.close()
        self._isClosed = True

    def waitForIt(self):
        try:
            while self._isClosed is False:
                sleep(0.1)
        except KeyboardInterrupt:
            pass

    def broadcast(self, msg):
        if isinstance(msg, str):
            msg = unicode(msg, "utf-8")
        for client in clients:
            client.sendMessage(msg)
            while client.sendq:
                opcode, payload = client.sendq.popleft()
                remaining = client._sendBuffer(payload)
                if remaining is not None:
                    client.sendq.appendleft((opcode, remaining))
                    break