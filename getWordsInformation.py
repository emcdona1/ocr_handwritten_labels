
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import re
def getDescriptionFromDataFrame(type, dfs, hint=0):
    text = ""
    if type=="raw":
        text= dfs['description'][0]
    if type=="corrected":
        oldW=None
        for index, w in dfs.iterrows():
            if w['index'] > 0:
                if w['index']>1:
                    if isCurrentWordInNextLine(currentWord=w,previousWord=oldW):
                        text+="\n"
                oldW=w
                if w['isIncorrectWord']:
                    if (hint==1):
                        text+="["+w['description']+"]->"
                    text += w['replacement']+" "
                else:
                    text += w['description'] + " "

    if type=="OCR":
        for index, w in dfs.iterrows():
            if w['index'] > 0:
                text += w['description'] + " "

    if type=="MASKED":
        for index, w in dfs.iterrows():
            if w['isIncorrectWord']:
                text += "[MASK] "
            else:
                text += w['description'] + " "

    if type=="classified":
        classifiedData = getClassifiedDataTuples(dfs)
        categories=[c[0] for c in classifiedData]
        categories = list(set(categories))
        for c in sorted(categories):
            if not c=="Unknown" and "ignore" not in c:
                text+=c+": "
                for cd in classifiedData:
                    if(cd[0]==c):
                        text+=str(cd[1])+" "
                text+="\n"
    return replaceExtraSpace(text)

def getClassifiedDataTuples(dfs):
    classifiedData = []
    for index, w in dfs.iterrows():
        if w['index'] > 0:
            classifiedData.append((w['category'], w['replacement']))
    return classifiedData

def debugDF(df):
    for index, w in df.iterrows():
        print(str(w['index']) + ":" + w['description'])

# current word's centroid is bigger then previous word's y values
# current word's y values are bigger then previous words' centroid
def isCurrentWordInNextLine(currentWord,previousWord):
    return currentWord['centroid'][1] >= max(previousWord['y_list']) or \
            min(currentWord['y_list']) >= previousWord['centroid'][1]

def getWordByPolygon(dfs, polygon):
    for index, w in dfs.iterrows():
        if index > 0:
            if w['polygon']==polygon:
                return w
    return w

def getWordByXY(dfs, x, y):
    point = (x,y)
    point = Point(x, y)
    for index, w in dfs.iterrows():
        if index > 0:
            polygon = Polygon(w['tupleVertices'])
            if polygon.contains(point):
                return w
    return None

def replaceExtraSpace(text):
    rep = {' \'': '\'',
           ' .':'.',
           ' ,':',',
           ' ?':'?',
           ' !':'!'}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text







