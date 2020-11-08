from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateWord, Call_SP_GetTagDetail, \
    Call_SP_GetTagList, Call_SP_DeleteTag, Call_SP_AddBarCodeInfo
from Helper.AlgorithmicMethods import GetTempFilePath

def SaveTagtoDatabase(imagePath,processingTime,imageContent, df,barCode):
    wordsInfoAsXML = DFToWordsXml(df)
    tagId,importDate,hasBarCodeInDB=Call_SP_AddTag(
        originalImagePath=imagePath,
        processingTime=processingTime,
        img=imageContent,
        wordsInfoAsXML=wordsInfoAsXML,
        barCode=barCode)
    return tagId,importDate,hasBarCodeInDB

def UpdateWordInDatabase(tagId,word):
    Call_SP_UpdateWord(tagId,word['index'], word['replacement'],word['suggestedDescription'],word['category'])
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
    imgBlob,imagePath,processingTime,df,importDate,barCode,irn,taxonomy,collector,details=Call_SP_GetTagDetail(tagId)
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)

    tempFile = GetTempFilePath("DB_Load_Tag.png")
    with open(tempFile, "wb") as fh:
        fh.write(imgBlob)

    return tempFile,[d],imagePath,processingTime,importDate,barCode,irn,taxonomy,collector,details

def GetImportedTagTuples(importedDate=''):
    return Call_SP_GetTagList(importedDate)

def DeleteTag(tagId):
    Call_SP_DeleteTag(tagId)

def AddBarCodeInfo(barCode,irn,taxonomy, collector,details):
    Call_SP_AddBarCodeInfo(barCode,irn,taxonomy, collector,details)


