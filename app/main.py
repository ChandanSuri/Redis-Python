import socket
import os
import time
from threading import *
from enum import Enum
from argparse import ArgumentParser

class ServerRole(str, Enum):
    MASTER = "master"
    SLAVE = "slave"

class Command(str, Enum):
    PING = "ping"
    ECHO = "echo"
    SET = "set"
    GET = "get"
    INFO = "info"

class Database:
    def __init__(self):
        self.data = {}
        self.expiryTimes = {}

    def add(self, key, value):
        self.data[key] = value

    def get(self, key):
        if key not in self.data:
            return -1
        
        return self.data[key]
    
    def updateExpiryTime(self, key, expiryTime):
        self.expiryTimes[key] = expiryTime

    def getDataExpiry(self, key):
        if key not in self.expiryTimes:
            return -1
        
        return self.expiryTimes[key]
    
    def deleteDataExpiry(self, key):
        if key in self.expiryTimes:
            del self.expiryTimes[key]
    
class Connection(Thread):
    def __init__(self, socket, address):
        super().__init__()
        self.socket = socket
        self.address = address
        self.database = Database()
        self.start()

    def run(self):
        while True:
            request = self.socket.recv(1024)
            if not request:
                break
            
            parsedReq = self.parseReq(request)
            self.parseCommandAndSendRequest(parsedReq)

        self.socket.close()

    def parseReq(self, request):
        requestParams = request.decode().split("\r\n")
        return requestParams

    def parseCommandAndSendRequest(self, request):
        requestCommand = request[2].lower()

        if requestCommand == Command.PING:
            dataToSend = "+PONG\r\n"
        elif requestCommand == Command.ECHO:
            dataToSend = f"+{request[-2]}\r\n"
        elif requestCommand == Command.SET:
            key, value = request[4], request[6]
            self.database.add(key, value)

            if len(request) > 8 and request[8].upper() == "PX":
                self.database.updateExpiryTime(key, time.time() + float(request[10]) / 1000)
            else:
                self.database.deleteDataExpiry(key)

            dataToSend = "+OK\r\n"
        elif requestCommand == Command.GET:
            key = request[4]
            dataExpiryTime = self.database.getDataExpiry(key)
            if dataExpiryTime != -1 and time.time() > dataExpiryTime:
                dataToSend = f"$-1\r\n"
            else:
                value = self.database.get(key)
                dataToSend = f"+{value}\r\n"
        elif requestCommand == Command.INFO:
            subCommand = request[4].lower()
            if subCommand == "replication":
                if role == ServerRole.MASTER:
                    payload = "role:master\n" + \
                        "master_replid:8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb\n" + \
                        "master_repl_offset:0"
                    dataToSend = f"${len(payload)}\r\n{payload}\r\n"
                else:
                    dataToSend = f"$10\r\nrole:slave\r\n"
            else:
                dataToSend = f"$-1\r\n"
        else:
            return
        
        self.socket.send(dataToSend.encode())
    
def main():
    serverSocket = socket.create_server(("localhost", args.port), reuse_port=True)

    while True:
        # Wait for client
        clientSocket, clientAddress = serverSocket.accept() 
        print("Received a connection from client: {clientAddress}")
        Connection(clientSocket, clientAddress)


if __name__ == "__main__":
    parser = ArgumentParser("Redis Server Using Python!!!")
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--replicaof", type=str)
    args = parser.parse_args()

    role = ServerRole.SLAVE if args.replicaof else ServerRole.MASTER

    main()
