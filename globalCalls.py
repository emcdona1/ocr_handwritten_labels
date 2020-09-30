from CreateOutputFrameToDisplayInfo import setOutput

df=""

def setDF(d):
    global  df
    df=d
    updateOutput()



def GetDescriptionFromDataFrame(type,dfs, hint):
    correctedText = ""
    if type=="raw":
        correctedText= dfs['description'][0]
    if type=="corrected":
        oldW=None
        for index, w in dfs.iterrows():
            if w['index'] > 0:
                if w['index']>1:
                    if isCurrentWordInNextLine(currentWord=w,previousWord=oldW):
                        correctedText+="\n"
                oldW=w
                if w['isIncorrectWord']:
                    if (hint==1):
                        correctedText+="["+w['description']+"]->"
                    correctedText += w['replacement']+" "
                else:
                    correctedText += w['description'] + " "

    if type=="OCR":
        for index, w in dfs.iterrows():
            if w['index'] > 0:
                correctedText += w['description'] + " "
    return correctedText

def setToDefaultWord(word):
    if word['index']>0:
       if(word['color']=='green'):
            word['canvas'].itemconfigure(word['polygon'], outline='', width=1,
                                           fill='',    activeoutline=word['color'],activewidth=2)
       else:
           word['canvas'].itemconfigure(word['polygon'], outline=word['color'], width=1,
                                          fill='',    activeoutline=word['color'], activewidth=2)

def updateOutput(**kw):
    type=kw.pop('type',"corrected")
    useHint=kw.pop('useHint',0)
    global df
    afterUpdate=GetDescriptionFromDataFrame(type,df,useHint)
    setOutput(afterUpdate)

def debugDF(df):
    for index, w in df.iterrows():
        print(str(w['index']) + ":" + w['description'])

# current word's centroid is bigger then previous word's y values
# current word's y values are bigger then previous words' centroid
def isCurrentWordInNextLine(currentWord,previousWord):
    return currentWord['centroid'][1] >= max(previousWord['y_list']) or \
            min(currentWord['y_list']) >= previousWord['centroid'][1]


from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def GetWordByPolygon(dfs, polygon):
    for index, w in dfs.iterrows():
        if index > 0:
            if w['polygon']==polygon:

                return w
    return w

def GetWordByXY(dfs, x, y):
    point = (x,y)
    point = Point(x, y)
    for index, w in dfs.iterrows():
        if index > 0:
            polygon = Polygon(w['tupleVertices'])
            if polygon.contains(point):
                return w
    return None