import mysql.connector
from configparser import ConfigParser

configParser = ConfigParser()
configFilePath = r'Configuration.cfg'
configParser.read(configFilePath)
userName = configParser.get('DATABASE', 'userName')
password = configParser.get('DATABASE', 'password')
host = configParser.get('DATABASE', 'host')
databaseName = configParser.get('DATABASE', 'databaseName')
portNo = configParser.get('DATABASE', 'portNo')

def Get_Connection():
    Connected=True
    conn = ""
    try:
        conn = mysql.connector.connect(user=userName, password=password, host=host, database=databaseName,port=portNo)
    except:
        print("Database connection can not made")
        Connected=False
    return conn, Connected,databaseName

def ConnectAndGetDBInfoToCreate():
    conn = ""
    Connected=True
    try:
        conn = mysql.connector.connect(user=userName, password=password, host=host, port=portNo)
    except:
        print("Database connection can not made")
        Connected=False
    return conn, Connected,databaseName,userName,password,host