import pickle
import socket
from datetime import datetime


class SuggestEngineClient:
    s = None

    def __init__(self, root):
        self.genus_species_file_path = root.configParser.get('SNS_SERVER', 'genus_species_file_path')
        self.hostName_server = root.configParser.get('SNS_SERVER', 'host')
        self.port_no = int(root.configParser.get('SNS_SERVER', 'port_no'))
        self.buffer_size = int(root.configParser.get('SNS_SERVER', 'buffer_size'))
        self.queue_size = int(root.configParser.get('SNS_SERVER', 'queue_size'))
        pass

    def suggest(self, word):
        try:
            self.s = socket.socket()
            self.s.connect((self.hostName_server, self.port_no))
            self.s.send(word.encode())
            result = pickle.loads(self.s.recv(self.port_no))
            self.s.close()
            return result
        except Exception as error:
            print(f"{error} (Error Code:SEC_001)")
            print(datetime.now().strftime("%H:%M:%S") + " Unknown Error when getting suggestion from SNS server!")
            return None
