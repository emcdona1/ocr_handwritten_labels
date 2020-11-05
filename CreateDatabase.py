import os
from pathlib import Path

from DatabaseProcessing.GetConnection import Get_Connection, ConnectAndGetDBInfoToCreate
from Helper.Confirm import confirm
from subprocess import Popen, PIPE, STDOUT


def CreateDatabase():
    createDatabase = True
    try:
        print("Connection attempt to check if database exists!")
        conn, isConnected, databaseName = Get_Connection()
        if isConnected:
            createDatabase = confirm(
                f"The database:{databaseName} already exists in the system. Do you want to overwrite?")
            conn.close()
    except Exception as error:
        createDatabase = True

    if createDatabase:
        isConnected2 = False
        try:
            print(f"Connection attempt to create a new database:{databaseName}!")
            conn, isConnected2, databaseName, userName, password,host = ConnectAndGetDBInfoToCreate()
            conn.close()
            if isConnected2:
                print(f"Connection successful, now creating database: {databaseName} on the server: {host}")
                if DropOldAndCreateNewDatabase(conn, databaseName, userName, host):
                    print("Database created!")
                    CreateTablesAndStoredProcedures(databaseName,userName,password,host)
                else:
                    print(f"Could not create the database:{databaseName} on the server: {host}")

        except Exception as error:
            print(error)

        if not isConnected2:
            print("Database can not connected! Please modify the information in Configuration.cfg and try again!")
    else:
        print("Nothing has been modified!")


def DropOldAndCreateNewDatabase(conn, databaseName, userName, host):
    DatabaseCreated=False
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {databaseName};"
                       f"CREATE DATABASE {databaseName};"
                       f"GRANT ALL PRIVILEGES ON {databaseName}.* TO '{userName}'@'{host}';"
                       "FLUSH PRIVILEGES;", multi=True)
        cursor.close()
        conn.close()
        # As now database is created, connect to database and create tables and SPS
        DatabaseCreated=True
    except Exception as error:
        print("Some error happen when creating the database.")
        print(error)
        cursor.close()
        conn.close()
    return DatabaseCreated

def CreateTablesAndStoredProcedures(db,user,passwd,host):
    try:

        createTablesSQL=Path('DatabaseSetupScripts/CreateTables.sql')
        createSPSQL=Path('DatabaseSetupScripts/CreateSPs.sql')
        executeSqlScript( createTablesSQL,db,user,passwd,host)
        executeSqlScript( createSPSQL,db,user,passwd,host)

    except Exception as error:
        print("Could not create the tables and stored procedures")
        print(error)

def executeSqlScript( scriptPath,dbName,userName,password,host ,ignoreErrors=False ) :
    scriptDirPath = os.path.dirname( os.path.realpath( scriptPath ) )
    sourceCmd = "SOURCE %s" % (scriptPath,)
    cmdList = [ "mysql","--database", dbName,"-u",userName,"-p",password, "-h",host,"--unbuffered" ]
    if ignoreErrors :
        cmdList.append( "--force" )
    else:
        cmdList.extend( ["--execute", sourceCmd ] )
    process = Popen( cmdList
                     , cwd=scriptDirPath
                     , stdout=PIPE
                     , stderr=(STDOUT if ignoreErrors else PIPE)
                     , stdin=(PIPE if ignoreErrors else None) )
    stdOut, stdErr = process.communicate( sourceCmd if ignoreErrors else None )
    if stdErr is not None and len(stdErr) > 0 :
        print(stdErr)
    return stdOut


CreateDatabase()
