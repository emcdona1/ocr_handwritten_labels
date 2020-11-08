import ast
import binascii

import pandas as pd

from DatabaseProcessing.GetConnection import Get_Connection


def Call_SP_AddTag(originalImagePath, processingTime,img, wordsInfoAsXML,barCode):
    conn, isConnected,dbName = Get_Connection()
    tagId = 0
    importDate=''
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_AddTag',
                        [originalImagePath, processingTime,binascii.hexlify(img), wordsInfoAsXML,barCode, ])
        result = cursor.stored_results()
        conn.commit()
        cursor.close()
        conn.close()
        tagId = 0
        for r in result:
            for row in r:
                tagId = row[0]
                importDate=row[1]
                hasBarCodeInDb=row[2]
        pass

    return tagId,importDate,hasBarCodeInDb


def Call_SP_UpdateWord(tagId,wordIndexUpdate, replacement,suggestions,category):
    conn, isConnected, dbName= Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_UpdateWord', [tagId,wordIndexUpdate, replacement, str(suggestions),category,])
        cursor.stored_results()
        conn.commit()
        cursor.close()
        conn.close()
        pass


def Call_SP_DeleteTag(tagIdDelete):
    conn, isConnected, dbName= Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_DeleteTag', [tagIdDelete, ])
        conn.commit()
        cursor.close()
        conn.close()
        pass


def Call_SP_GetTagList(importDateIn):
    conn, isConnected,dbName = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        tagList = []
        cursor.callproc('SP_GetTagList', [importDateIn, ])
        for result in cursor.stored_results():
            for row in result:
                tagList.append((row[0],row[1],row[2]))
        cursor.close()
        conn.close()
        return tagList
        pass


def Call_SP_GetTagDetail(tagIdIn):
    dataFrame = pd.DataFrame(columns=['index', 'isIncorrectWord','tupleVertices'])
    conn, isConnected, dbName = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_GetTagDetail', [tagIdIn, ])
        image = None
        for result in cursor.stored_results():
            for row in result:
                if not image is None:
                    isIncorrectWord = (not row[1].lower() == row[2].lower())
                    color = "green" if not isIncorrectWord else "red"
                    suggestions=ast.literal_eval(row[3])
                    tupleVertices=ast.literal_eval(row[4])
                    dataFrame = dataFrame.append(
                        dict(
                            index=row[0],
                            description=row[1],
                            replacement=row[2],
                            category=row[5],
                            tupleVertices=tupleVertices,
                            sp=0,
                            ep=0,
                            suggestedDescription=suggestions,
                            polygon=None,
                            canvas=None,
                            confidence=0.0,
                            isIncorrectWord=isIncorrectWord,
                            color=color
                        ),
                        ignore_index=True
                    )
                else:
                    image = row[0]
                    imagePath=row[1]
                    processingTime=row[2]
                    importDate=row[3]
                    barCode=row[4]
                    irn=str(row[5])
                    taxonomy=row[6]
                    collector=row[7]
                    details=row[8]
        cursor.close()
        conn.close()
        return image,imagePath,processingTime, dataFrame,importDate,barCode,irn,taxonomy,collector,details
        pass

def Call_SP_AddBarCodeInfo(barCode,irn,taxonomy, collector,details):
    conn, isConnected,dbName = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_AddBarCodeInfo',[barCode, irn,taxonomy, collector,details, ])
        cursor.stored_results()
        conn.commit()
        cursor.close()
        conn.close()
    else:
        print("Unable to connect to the database")
