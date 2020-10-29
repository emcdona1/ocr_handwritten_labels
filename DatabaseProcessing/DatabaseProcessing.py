from DatabaseProcessing.DatabaseCalls import Call_SP_AddTag, Call_SP_UpdateWord


def LoadTagFromDatabase():
    print("place holder to load oldTag from the db")
    tagId = df = ""
    return tagId, df
    pass

def SaveTagtoDatabase(imagePath, df):
    imgBlob = GetBlob(imagePath)
    wordsInfoAsXML = DFToWordsXml(df)
    return Call_SP_AddTag(
        originalImagePath=imagePath,
        img=imgBlob,
        wordsInfoAsXML=wordsInfoAsXML)


def UpdateWordInDatabase(tagId,word):
    Call_SP_UpdateWord(tagId,word['index'], word['replacement'],word['suggestedDescription'],word['category'])
    pass


def GetBlob(tagPath):
    with open(tagPath, 'rb') as file:
        binaryData = file.read()
    return binaryData


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
