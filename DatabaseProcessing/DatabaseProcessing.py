from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateWord, Call_SP_GetTagDetail, \
    Call_SP_GetTagList, Call_SP_DeleteTag
from Helper.AlgorithmicMethods import GetTempFilePath

def SaveTagtoDatabase(imagePath,processingTime,imageContent, df):
    wordsInfoAsXML = DFToWordsXml(df)
    tagId=Call_SP_AddTag(
        originalImagePath=imagePath,
        processingTime=processingTime,
        img=imageContent,
        wordsInfoAsXML=wordsInfoAsXML)
    return tagId

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
    imgBlob,imagePath,processingTime,df=Call_SP_GetTagDetail(tagId)
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)

    tempFile = GetTempFilePath()
    with open(tempFile, "wb") as fh:
        fh.write(imgBlob)

    return tempFile,[d],imagePath,processingTime

def GetImportedTagTuples(importedDate=''):
    return Call_SP_GetTagList(importedDate)

def DeleteTag(tagId):
    Call_SP_DeleteTag(tagId)


