from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def addToLastLineOrNewLine(lines, w):
    if(len(lines)>0):
        lWord=lines[-1][-1]
        if areWordsInAcceptableOffsetDistance(lWord,w):
            lines[-1].append(w)
        else:
            lines.append([w])
    else:
        lines.append([w])

def sortBySp(line):
  def sortKey(w):
    return int(w['sp'][0])
  return sorted(line, key=sortKey)

def sortByFirstY(blocks):
    def sortKey(line):
        return int(line[0]['sp'][1])
    return sorted(blocks, key=sortKey)

def sortByLastX(blocks):
    def sortKey(line):
        return int(line[-1]['sp'][0])
    return sorted(blocks, key=sortKey)

def getSequentialBlocks(lines):
    blocks=[]
    for line in lines:
        blocks.append(sortBySp(line))
    return sortByFirstY(blocks)

def getSequencialDataList(d):
    lines=[]
    for w in d:
        addToLastLineOrNewLine(lines, w)
    return getSequentialBlocks(lines)

def getSequentialDataBlocks(df):
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)
    return getSequencialDataList(d)


def detectAndRemoveSmallRepeatedWordArea(x, y):
    polygonY = Polygon(y['tupleVertices'])
    c=Point((x['sp'][0]+x['ep'][0])//2,(x['sp'][1]+x['ep'][1])//2)
    if polygonY.contains(c):
       x['index']=-1

##########################sub methods#########################

def meetHorizontalAlignment(x, y, maxGap=70):
    if(y['sp'][0]<x['sp'][0]):
        t=x
        x=y
        y=t
    l1= x['ep'][0] - x['sp'][0]
    l2=y['ep'][0]-y['sp'][0]
    tl=y['ep'][0]-x['sp'][0]
    g = y['sp'][0] - x['ep'][0]
    ldiff=abs(tl-l1-l2-g)

    return ldiff==0 and g<=maxGap

def meetVerticalAlignment(w1,w2, verticleOffset=15):
    v = w2['sp'][1] - w1['ep'][1]
    return abs(v)<=verticleOffset

def areWordsInAcceptableOffsetDistance(w1, w2):
    return meetHorizontalAlignment(w1, w2) and meetVerticalAlignment(w1,w2)
