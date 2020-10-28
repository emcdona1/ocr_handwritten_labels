import binascii

import pandas as pd

from DatabaseProcessing.GetConnection import Get_Connection


def Call_SP_AddTag(importReference, tagName, originalImagePath, img, wordsInfoAsXML):
    conn, isConnected = Get_Connection()
    tagId = 0
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_AddTag',
                        [importReference, tagName, originalImagePath, binascii.hexlify(img), wordsInfoAsXML, ])
        result = cursor.stored_results()
        conn.commit()
        tagId = 0
        for r in result:
            for row in r:
                tagId = row[0]
        pass
    return tagId


def Call_SP_UpdateTag(tagIdUpdate, wordsInfoAsXML):
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_UpdateTag', [tagIdUpdate, wordsInfoAsXML, ])
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


def Call_SP_GetTagList(importReferenceIn):
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        tagList = []
        cursor.callproc('SP_GetTagList', [importReferenceIn, ])
        for result in cursor.stored_results():
            for row in result:
                tag = {
                    'TagId': row[0],
                    'ImportReference': row[1],
                    'TagName': row[2],
                    'OriginalImagePath': row[3]
                }
                tagList.append(tag)
        cursor.close()
        return tagList
        pass


def Call_SP_GetTagDetail(tagIdIn):
    dataFrame = pd.DataFrame(columns=['index', 'isIncorrectWord'])
    conn, isConnected = Get_Connection()
    if isConnected:
        cursor = conn.cursor()
        cursor.callproc('SP_GetTagDetail', [tagIdIn, ])
        image = None
        for result in cursor.stored_results():
            for row in result:
                if not image is None:
                    dataFrame = dataFrame.append(
                        dict(
                            index=row[0],
                            description=row[1],
                            replacement=row[2],
                            category=row[5],
                            tupleVertices=row[4],
                            sp=0,
                            ep=0,
                            suggestedDescription=row[3],
                            polygon=None,
                            canvas=None,
                            confidence=0.0,
                            isIncorrectWord=(not row[1] == row[2]),
                            color="green" if not row[1] == row[2] else "red"
                        ),
                        ignore_index=True
                    )
                else:
                    image = row[0]
        cursor.close()
        return image, dataFrame
        pass

# print(Call_SP_GetTagList(''))

# print(Call_SP_GetTagDetail(1))
# print(Call_SP_DeleteTag(3))
# print(Call_SP_GetTagDetail(3))
