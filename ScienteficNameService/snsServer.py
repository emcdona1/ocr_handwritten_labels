import socket
import pickle
from datetime import datetime

from ScienteficNameService.snsEngine import SuggestEngine

def startSNSServer(wordFilePath, hostName_server=socket.gethostname(), portNo_server=1234, queueSize=3, bufferSize=1024):
    print(datetime.now().strftime("%H:%M:%S") + " Initializing Suggest Engine(TRIE) with for filePath: "+wordFilePath)
    se = SuggestEngine(wordFilePath, 'TRIE')
    print(datetime.now().strftime("%H:%M:%S") + " Suggest Engine Initialized!")

    s = socket.socket()
    s.bind((hostName_server, portNo_server))
    s.listen(queueSize)
    print(datetime.now().strftime("%H:%M:%S") + " Scientific Name Server(SNS) is now up and listening!")

    while True:
         c, addr = s.accept() 		# Establish connection with client.
         print(datetime.now().strftime("%H:%M:%S") + " Connection established ",addr)

         while True:
              try:
                   data=c.recv(bufferSize).decode()
                   print(datetime.now().strftime("%H:%M:%S") + " Get suggestions for: ",data)
                   suggestions=se.suggest(data)
                   dumpData=pickle.dumps(suggestions)
                   c.send(dumpData)
                   print(datetime.now().strftime("%H:%M:%S"), "suggestions:", suggestions, "are sent")
                   break;
              except:
                  print(datetime.now().strftime("%H:%M:%S") + " Unknown Error at server side ")
                  break;
         c.close()

startSNSServer("../InputResources/genusspecies_data.txt")