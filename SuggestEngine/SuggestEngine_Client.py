import pickle
import socket
from datetime import datetime

class SuggestEngineClient:
    s = None
    def __init__(self,root):
        self.genusSpeciesFilePath = root.configParser.get('SNS_SERVER', 'genusSpeciesFilePath')
        self.hostName_server = root.configParser.get('SNS_SERVER', 'host')
        self.portNo_server = int(root.configParser.get('SNS_SERVER', 'portNo'))
        self.bufferSize = int(root.configParser.get('SNS_SERVER', 'bufferSize'))
        self.queueSize = int(root.configParser.get('SNS_SERVER', 'queueSize'))
        pass

    def suggest(self, word):
        try:
            self.s = socket.socket()
            self.s.connect((self.hostName_server, self.portNo_server))
            self.s.send(word.encode())
            result = pickle.loads(self.s.recv(self.portNo_server))
            self.s.close()
            return result
        except Exception as error:
            print(f"{error} (Error Code:SEC_001)")
            print(datetime.now().strftime("%H:%M:%S") + " Unknown Error when getting suggestion from SNS server!")
            return None
