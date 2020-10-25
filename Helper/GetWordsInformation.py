import math

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import re



def GetClassifiedCategoriesInOrder(mainCategories, classifiedCategories):
    categories=[]
    for c in mainCategories:
        if c in classifiedCategories:
            categories.append(c)
    #add any user added WordCategories at the end
    for c in sorted(classifiedCategories):
        if c not in categories:
            categories.append(c)
    return categories
    pass


def GetDescriptionFromDataBlocks(type, sdb, hint=0, mainCategories=[]):
    text = ""
    if type=="corrected":
        for db in sdb:
            for w in db:
                if w['index'] > 0:
                    if w['isIncorrectWord']:
                        if (hint==1):
                            text+="["+w['description']+"]->"
                        text += w['replacement']+" "
                    else:
                        text += w['description'] + " "
            text+="\n"

    if type=="OCR":
        for db in sdb:
            for w in db:
                if w['index'] > 0:
                    text += w['description'] + " "
            text+="\n"

    if type=="MASKED":
        for db in sdb:
            for w in db:
                if w['isIncorrectWord']:
                    text += "[MASK] "
                else:
                    text += w['description'] + " "

    if type=="classified":
        classifiedData = GetClassifiedDataTuples(sdb)
        classifiedCategories=[c[0] for c in classifiedData]
        classifiedCategories = list(set(classifiedCategories))
        categories=GetClassifiedCategoriesInOrder(mainCategories, classifiedCategories)
        for c in categories:
            if not c=="Unknown" and "ignore" not in c:
                text+=c+": "
                for cd in classifiedData:
                    if(cd[0]==c):
                        text+=str(cd[1])+" "
                text+="\n"
    return ReplaceExtraSpace(text)

def GetClassifiedDataTuples(sdb):
    classifiedData = []
    for db in sdb:
        for w in db:
            if w['index'] > 0:
                classifiedData.append((w['category'], w['replacement']))
    return classifiedData


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

def ReplaceExtraSpace(text):
    rep = {' \'': '\'',
           ' .':'.',
           ' ,':',',
           ' ?':'?',
           ' !':'!'}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text












