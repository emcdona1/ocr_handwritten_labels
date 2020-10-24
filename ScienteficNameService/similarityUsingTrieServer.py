import socket
import pickle
from datetime import datetime


class WordSearcherWithTrieServer:
    bufferSize=1024
    queueSize=3
    portNo_client=1235
    portNo_server = 1234
    hostName_client=None
    hostName_server=None
    s=None
    def __init__(self, hostName=socket.gethostname(), portNo_client=1235,hostName_server=socket.gethostname(),portNo_server=1234, queueSize=3, bufferSize=1024):
        self.bufferSize=bufferSize
        self.queueSize=queueSize
        self.portNo_client=portNo_client
        self.hostName_client=hostName
        self.hostName_server=hostName_server
        self.portNo_server=portNo_server

    def suggest(self, word):
        try:
            self.s = socket.socket()
            self.s.connect((self.hostName_server, self.portNo_server))
            print(datetime.now().strftime("%H:%M:%S") + " Sending :'"+word+"' to SNS server to get suggestions!")
            self.s.send(word.encode())
            result = pickle.loads(self.s.recv(self.portNo_client))
            print(datetime.now().strftime("%H:%M:%S") + " Suggestions: "+str(result))
            self.s.close()
            return result
        except:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown Error at client side ")