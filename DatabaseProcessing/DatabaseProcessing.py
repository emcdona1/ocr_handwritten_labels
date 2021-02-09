from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateWord, Call_SP_GetTagDetail, \
    Call_SP_GetTagList, Call_SP_DeleteTag, Call_SP_AddBarCodeInfo, CALL_SP_GetImportDates, CALL_SP_GetTagClassification, \
    Call_SP_AddUpdateTagClassification, CALL_SP_GetBarCodeInfo, CALL_SP_GetDataForCSV, \
    CALL_SP_GetDataForCSVForImportDate, Call_SP_UpdateBarCode
from Helper.AlgorithmicMethods import GetTempFilePath
from Helper.GetWordsInformation import GetClassifiedDataTuples


def SaveTagtoDatabase(imagePath, processingTime, imageContent, df, barcode):
    wordsInfoAsXML = DFToWordsXml(df)
    tagId, importDate, hasBarCodeInDB = Call_SP_AddTag(
        originalImagePath=imagePath,
        processingTime=processingTime,
        img=imageContent,
        wordsInfoAsXML=wordsInfoAsXML,
        barcode=barcode)
    return tagId, importDate, hasBarCodeInDB


def UpdateWordInDatabase(root, word):
    tagId = root.tagId
    root.classifiedData = GetClassifiedDataTuples(root.sdb)
    if (tagId > 0):
        Call_SP_UpdateWord(tagId, word['index'], word['replacement'], word['suggestedDescription'], word['category'])
        AddUpdateTagClassification(tagId, root.classifiedData)
    else:
        print(f'Invalid tagId:{tagId}')
    pass


def DFToWordsXml(df):
    xml = ['<words>']
    for ws in df:
        for w in ws:
            if w['index'] > 0:
                xml.append('<word>')
                xml.append('<wordIndex>' + str(w['index']) + '</wordIndex>')
                xml.append('<description>' + str(w['description']) + '</description>')
                xml.append('<replacement>' + str(w['replacement']) + '</replacement>')
                xml.append('<vertices>' + str(w['tupleVertices']) + '</vertices>')
                xml.append('<suggestions>' + str(w['suggestedDescription']) + '</suggestions>')
                xml.append('<category>' + str(w['category']) + '</category>')
                xml.append('</word>')
    xml.append('</words>')
    return '\n'.join(xml)


def GetImgAndSDBFromTagId(tagId):
    imgBlob, imagePath, processingTime, df, importDate, barcode = Call_SP_GetTagDetail(tagId)
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)

    tempFile = GetTempFilePath("DB_Load_Tag.png")
    with open(tempFile, "wb") as fh:
        fh.write(imgBlob)

    return tempFile, [d], imagePath, processingTime, importDate, barcode


def GetImportedTagTuples(importedDate, sortItemsByBarCode, startIndex, Count):
    return Call_SP_GetTagList(importedDate, sortItemsByBarCode, startIndex, Count)


def GetImportDates():
    return CALL_SP_GetImportDates()


def DeleteTag(tagId):
    Call_SP_DeleteTag(tagId)


def AddBarCodeInfo(barcode, classificationTuples):
    data = GetXMLClassificationInfoFromTuples(classificationTuples)
    Call_SP_AddBarCodeInfo(barcode, data)


def GetTagClassification(TagId):
    return CALL_SP_GetTagClassification(TagId)


def GetBarCodeClassification(barcode):
    return CALL_SP_GetBarCodeInfo(barcode)


def AddUpdateTagClassification(TagId, classificationTuples):
    data = GetXMLClassificationInfoFromTuples(classificationTuples)
    Call_SP_AddUpdateTagClassification(TagId, data)


def GetXMLClassificationInfoFromTuples(classificationTuples):
    xml = ['<classifications>']
    for c in classificationTuples:
        xml.append('<classification>')
        xml.append(f'<Category>{c[0]}</Category>')
        xml.append(f'<Information>{c[1]}</Information>')
        xml.append('</classification>')
    xml.append('</classifications>')
    data = '\n'.join(xml)
    return data


def GetDataForCSV(TagId):
    return CALL_SP_GetDataForCSV(TagId)


def UpdateBarCode(TagId, BarCode):
    return Call_SP_UpdateBarCode(TagId, BarCode)


def GetDataForCSVForImportDate(ImportDate):
    return CALL_SP_GetDataForCSVForImportDate(ImportDate)
