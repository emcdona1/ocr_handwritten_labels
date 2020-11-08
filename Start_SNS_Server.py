''' would initialize Trie suggest engine, and would call snsEngine to get the services
standalone server,
'''
import pickle
import socket
from datetime import datetime
from configparser import ConfigParser

from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine


def startSNSServer(genusSpeciesFilePath,hostName_server,portNo_server, queueSize, bufferSize):
    se = GetLocalSuggestEngine(genusSpeciesFilePath, 'TRIE')
    s = socket.socket()
    s.bind((hostName_server, portNo_server))
    s.listen(queueSize)
    print(datetime.now().strftime("%H:%M:%S") + " Scientific Name Server(SNS) is now up and listening!")

    while True:
        c, addr = s.accept()  # Establish connection with client.
        print(datetime.now().strftime("%H:%M:%S") + " Connection established ", addr)

        while True:
            try:
                data = c.recv(bufferSize).decode()
                print(datetime.now().strftime("%H:%M:%S") + " Get suggestions for: ", data)
                suggestions = se.suggest(data)
                dumpData = pickle.dumps(suggestions)
                c.send(dumpData)
                print(datetime.now().strftime("%H:%M:%S"), "suggestions:", suggestions, "are sent")
                break;
            except Exception as error:
                print(error)
                print(datetime.now().strftime("%H:%M:%S") + " Unknown Error at server side ")
                break;
        c.close()


configParser = ConfigParser()
configFilePath = r'Configuration.cfg'
configParser.read(configFilePath)
genusSpeciesFilePath = configParser.get('SNS_SERVER', 'genusSpeciesFilePath')
portNo = configParser.get('SNS_SERVER', 'portNo')
bufferSize = configParser.get('SNS_SERVER', 'bufferSize')
queueSize = configParser.get('SNS_SERVER', 'queueSize')
hostName_server = configParser.get('SNS_SERVER', 'host')

startSNSServer(genusSpeciesFilePath,hostName_server,int(portNo),int(queueSize),int(bufferSize))
