'''would make connection to the server and send and receive the suggested word details'''
''' max cost is determined at server side'''
import socket
import pickle
from datetime import datetime
SERVER_PORT_DEFAULT=1234
CLIENT_PORT_DEFAULT=1235

class WordSearcherWithTrieServer:
    bufferSize=None
    queueSize=None
    portNo_client=None
    portNo_server = None
    hostName_client=None
    hostName_server=None
    s=None
    def __init__(self, hostName=socket.gethostname(), portNo_client=CLIENT_PORT_DEFAULT,hostName_server=socket.gethostname(),portNo_server=SERVER_PORT_DEFAULT, queueSize=3, bufferSize=1024):
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
            return None