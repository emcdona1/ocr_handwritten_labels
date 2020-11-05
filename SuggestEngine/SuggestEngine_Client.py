import pickle
import socket
from datetime import datetime
from configparser import ConfigParser

configParser = ConfigParser()
configFilePath = r'Configuration.cfg'
configParser.read(configFilePath)
genusSpeciesFilePath = configParser.get('SNS_SERVER', 'genusSpeciesFilePath')
hostName_server = configParser.get('SNS_SERVER', 'host')
portNo_server = int(configParser.get('SNS_SERVER', 'portNo'))
bufferSize = int(configParser.get('SNS_SERVER', 'bufferSize'))
queueSize = int(configParser.get('SNS_SERVER', 'queueSize'))


class SuggestEngineClient:
    s = None
    def __init__(self):
        pass

    def suggest(self, word):
        try:
            self.s = socket.socket()
            self.s.connect((hostName_server, portNo_server))
            self.s.send(word.encode())
            result = pickle.loads(self.s.recv(portNo_server))
            self.s.close()
            return result
        except:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown Error when getting suggestion from SNS server!")
            return None
