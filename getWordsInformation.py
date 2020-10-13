
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import re

#return the categories in order
def getCalssifiedCategoriesInOrder(mainCategories, classifiedCategories):
    categories=[]
    for c in mainCategories:
        if c in classifiedCategories:
            categories.append(c)
    #add any user added categories at the end
    for c in sorted(classifiedCategories):
        if c not in categories:
            categories.append(c)
    return categories
    pass


def getDescriptionFromDataFrame(type, dfs, hint=0, mainCategories=[]):
    text = ""
    if type=="raw":
        text= dfs['description'][0]
    if type=="corrected":
        oldW=None
        for index, w in dfs.iterrows():
            if w['index'] > 0:
                if w['index']>1:
                    if areWordsInDifferentLines(w, oldW):
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
        classifiedCategories=[c[0] for c in classifiedData]
        classifiedCategories = list(set(classifiedCategories))
        categories=getCalssifiedCategoriesInOrder(mainCategories,classifiedCategories)
        for c in categories:
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
# ignore x by
def areWordsInDifferentLines(w1, w2):
   cymin = min(w1['y_list'])
   ccy = w1['centroid'][1]
   pymin = min(w2['y_list'])
   pcy = w2['centroid'][1]
   centroidGapY = abs(ccy - pcy)

   centroidYRatioCw=abs(centroidGapY/(ccy-cymin))
   centroidYRatioPw=abs(centroidGapY/(pcy-pymin))
   lineGapFactor=min(centroidYRatioCw,centroidYRatioPw)
   return lineGapFactor>0.3 # heat and trial line gap factor to be 0.3

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

def getWordsByLinesAndBlocks(dfs):
    blocks=[]
    block=[]
    oldW=""
    oldW = None
    for index, w in dfs.iterrows():
        if w['index'] > 0:
            if w['index'] > 1:
                if isCurrentWordInNextBlock(currentWord=w, previousWord=oldW):
                    blocks.append(block)
                    block=[]
            oldW = w
            block.append(oldW)
    blocks.append(block)
    return blocks

#next block is defined by the horizontal space between two words
def isCurrentWordInNextBlock(currentWord,previousWord):
    pw_xmin=min(previousWord['x_list'])
    pw_xmax=max(previousWord['x_list'])
    cw_xmin=min(currentWord['x_list'])
    cw_xmax=max(currentWord['x_list'])

    pwSpaceFactor=(pw_xmax-pw_xmin)//(len(previousWord['description']))
    cwSpaceFactor=(cw_xmax - cw_xmin) // (len(currentWord['description']))

    spaceFactor=max(pwSpaceFactor+1,cwSpaceFactor+1)*4
    return abs((cw_xmin-pw_xmax)) > spaceFactor or areWordsInDifferentLines(currentWord, previousWord)








