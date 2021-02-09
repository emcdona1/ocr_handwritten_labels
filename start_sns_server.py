""" would initialize Trie suggest engine, and would call snsEngine to get the services
standalone server.
"""
import pickle
import socket
from datetime import datetime
from configparser import ConfigParser

from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine


def start_sns_server():
    se = GetLocalSuggestEngine(genus_species_file_path, 'TRIE')
    s = socket.socket()
    s.bind((host_name_server, port_no))
    s.listen(queue_size)
    print(datetime.now().strftime("%H:%M:%S") + " Scientific Name Server(SNS) is now up and listening!")

    while True:
        c, addr = s.accept()  # Establish connection with client.
        print(datetime.now().strftime("%H:%M:%S") + " Connection established ", addr)

        while True:
            try:
                data = c.recv(buffer_size).decode()
                print(datetime.now().strftime("%H:%M:%S") + " Get suggestions for: ", data)
                suggestions = se.suggest(data)
                dumpData = pickle.dumps(suggestions)
                c.send(dumpData)
                print(datetime.now().strftime("%H:%M:%S"), "suggestions:", suggestions, "are sent")
                break
            except Exception as error:
                print(f"{error} (Error Code:SSS_001)")
                print(datetime.now().strftime("%H:%M:%S") + " Unknown Error at server side ")
                break
        c.close()


def parse_configuration_file():
    config_parser = ConfigParser()
    config_file_path = r'Configuration.cfg'
    config_parser.read(config_file_path)
    genus_species_file_path = config_parser.get('SNS_SERVER', 'genus_species_file_path')
    host_name_server = config_parser.get('SNS_SERVER', 'host')
    port_no = int(config_parser.get('SNS_SERVER', 'port_no'))
    queue_size = int(config_parser.get('SNS_SERVER', 'queue_size'))
    buffer_size = int(config_parser.get('SNS_SERVER', 'buffer_size'))
    return genus_species_file_path, host_name_server, port_no, queue_size, buffer_size


if __name__ == '__main__':
    genus_species_file_path, host_name_server, port_no, queue_size, buffer_size = parse_configuration_file()
    start_sns_server()
