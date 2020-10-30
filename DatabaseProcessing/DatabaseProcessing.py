from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateWord, Call_SP_GetTagDetail
from Helper.AlgorithmicMethods import GetTempFilePath

def SaveTagtoDatabase(imagePath,imageContent, df):
    wordsInfoAsXML = DFToWordsXml(df)
    tagId=Call_SP_AddTag(
        originalImagePath=imagePath,
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
    imgBlob,df=Call_SP_GetTagDetail(tagId)
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)

    tempFile = GetTempFilePath()
    with open(tempFile, "wb") as fh:
        fh.write(imgBlob)

    return tempFile,[d]


