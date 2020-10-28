import mysql.connector


def Get_Connection():
    conn = ""
    try:
        conn = mysql.connector.connect(user='root', password='orange#5',
                                       host='localhost',
                                       database='PlantClassificationDB')
    except:
        print("Database connection can not made")
        return "", False
    return conn, True
