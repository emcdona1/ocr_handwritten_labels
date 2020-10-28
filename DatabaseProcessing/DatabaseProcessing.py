from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateTag


def LoadTagFromDatabase():
    print("place holder to load oldTag from the db")
    tagId=df=""
    return tagId,df
    pass

def SaveTagtoDatabase(imagePath, df):
    imgBlob=GetBlob(imagePath)
    tagName=imagePath.split("/")[-1]
    wordsInfoAsXML=DFToWordsXml(df)
    return Call_SP_AddTag(
        importReference='codeTest2132',
        tagName=tagName,
        originalImagePath=imagePath,
        img=imgBlob,
        wordsInfoAsXML=wordsInfoAsXML)

def UpdateTagInDatabase(tagId, df):
    Call_SP_UpdateTag(tagId,(DFToWordsXml(df)))
    pass

def GetBlob(tagPath):
    with open(tagPath, 'rb') as file:
        binaryData = file.read()
    return binaryData

def DFToWordsXml(df):
    xml = ['<words>']
    for ws in df:
        for w in ws:
            if w['index']>0:
                xml.append('<word>')
                xml.append('<description>' + str( w['description'] )+ '</description>')
                xml.append('<replacement>' + str(w['replacement'] )+ '</replacement>')
                xml.append('<vertices>' + str(w['tupleVertices'] )+ '</vertices>')
                xml.append('<suggestions>' +str( w['suggestedDescription'] )+ '</suggestions>')
                xml.append('<category>' + str(w['category'] )+ '</category>')
                xml.append('</word>')
    xml.append('</words>')
    return '\n'.join(xml)
