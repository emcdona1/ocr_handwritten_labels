
import math

def algorithm1(x,y):
    return areWordsInAcceptableOffsetDistance(x,y)


def areWordsInSameBlock(x,y):
    return algorithm1(x,y)

def addWordInProperLine(lines,w):
        for line in reversed(lines):
            for lWord in reversed(line):
                if areWordsInSameBlock(lWord,w):
                    line.append(w)
                    return
        lines.append([w])

def sortBySp(line):
  def sortKey(w):
    return int(w['sp'][0])
  return sorted(line, key=sortKey)

def sortByFirstY(blocks):
    def sortKey(line):
        return int(line[0]['sp'][1])
    return sorted(blocks, key=sortKey)

def getSequentialBlocks(lines):
    blocks=[]
    for line in lines:
        blocks.append(sortBySp(line))
    return sortByFirstY(blocks)

def getSequencialDataList(d):
    lines=[]
    for w in d:
        addWordInProperLine(lines,w)
    return getSequentialBlocks(lines)


def getSequentialDataBlocks(df):
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)
    return getSequencialDataList(d)

##########################sub methods#########################

def meetHorizontalAlignment(x, y, maxGap=80):
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

def areWordsInAcceptableAngle(x,y):
    return True
    #x...y (perfect line 180 degrees)
    a = getThreePointAngle(x['sp'], x['ep'], y['sp'])
    print(x['description'] + "vs" + y['description'] +" : "+ str(a))
    angleFactor=45
    return 180-angleFactor<=a<=180+angleFactor

def wordDistance(w1, w2):
    d1=getPointDistance(w1['ep'],w2['sp'])
    d2=getPointDistance(w2['ep'],w1['sp'])
    return min(d1,d2)

def getPointDistance(p1,p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

def getThreePointAngle(a, b, c):
    ang = abs(math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])))
    return ang