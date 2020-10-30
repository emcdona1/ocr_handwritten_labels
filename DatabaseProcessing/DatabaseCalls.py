import ast
import binascii

import pandas as pd

from DatabaseProcessing.GetConnection import Get_Connection


def Call_SP_AddTag(originalImagePath, img, wordsInfoAsXML):
    conn, isConnected = Get_Connection()
    tagId = 0
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_AddTag',
                        [originalImagePath, binascii.hexlify(img), wordsInfoAsXML, ])
        result = cursor.stored_results()
        conn.commit()
        tagId = 0
        for r in result:
            for row in r:
                tagId = row[0]
        pass
    return tagId


def Call_SP_UpdateWord(tagId,wordIndexUpdate, replacement,suggestions,category):
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_UpdateWord', [tagId,wordIndexUpdate, replacement, str(suggestions),category,])
        cursor.stored_results()
        conn.commit()
        pass


def Call_SP_DeleteTag(tagIdDelete):
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_DeleteTag', [tagIdDelete, ])
        conn.commit()
        pass


def Call_SP_GetTagList(importDateIn):
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        tagList = []
        cursor.callproc('SP_GetTagList', [importDateIn, ])
        for result in cursor.stored_results():
            for row in result:
                tag = {
                    'TagId': row[0],
                    'ImportDate': row[1],
                    'OriginalImagePath': row[2]
                }
                tagList.append(tag)
        cursor.close()
        return tagList
        pass


def Call_SP_GetTagDetail(tagIdIn):
    dataFrame = pd.DataFrame(columns=['index', 'isIncorrectWord','tupleVertices'])
    conn, isConnected = Get_Connection()
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
        cursor.close()
        return image, dataFrame
        pass
def GetTupleVerticesFromStringTuples(stringTuples):
    return []

# print(Call_SP_GetTagList(''))

# print(Call_SP_GetTagDetail(1))
# print(Call_SP_DeleteTag(3))
# print(Call_SP_GetTagDetail(3))