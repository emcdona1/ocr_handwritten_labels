import mysql.connector
from configparser import ConfigParser


def Initialize_DB_Properties():
    config_parser = ConfigParser()
    config_file_path = r'Configuration.cfg'
    config_parser.read(config_file_path)
    global userName
    global password
    global host
    global databaseName
    global database_port_no
    userName = config_parser.get('DATABASE', 'userName')
    password = config_parser.get('DATABASE', 'password')
    host = config_parser.get('DATABASE', 'host')
    databaseName = config_parser.get('DATABASE', 'databaseName')
    database_port_no = config_parser.get('DATABASE', 'portNo')


def Get_Connection():
    Connected = True
    conn = ""
    try:
        conn = mysql.connector.connect(user=userName, password=password, host=host, database=databaseName,
                                       port=database_port_no)
    except Exception as error:
        print("Database connection can not made")
        print(f"{error} (Error Code:GC_001)")
        Connected = False
    return conn, Connected, databaseName


def ConnectAndGetDBInfoToCreate():
    conn = ""
    Connected = True
    try:
        conn = mysql.connector.connect(user=userName, password=password, host=host, port=database_port_no)
    except Exception as error:
        print("Database connection can not made")
        print(f"{error} (Error Code:GC_002)")
        Connected = False
    return conn, Connected, databaseName, userName, password, host
