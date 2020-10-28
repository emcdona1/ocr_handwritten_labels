''' would initialize Trie suggest engine, and would call snsEngine to get the services
standalone server,
'''
import pickle
import socket
from datetime import datetime

from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine

GENUS_SPECIES_FILE = "InputResources/genusspecies_data.txt"
SERVER_PORT_DEFAULT = 1234


def startSNSServer(wordFilePath=GENUS_SPECIES_FILE, hostName_server=socket.gethostname(),
                   portNo_server=SERVER_PORT_DEFAULT, queueSize=10, bufferSize=1024):
    se = GetLocalSuggestEngine(wordFilePath, 'TRIE')
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
            except:
                print(datetime.now().strftime("%H:%M:%S") + " Unknown Error at server side ")
                break;
        c.close()


startSNSServer()
