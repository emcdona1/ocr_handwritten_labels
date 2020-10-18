
import math

def addWordInProperLine(lines,w):
        for line in reversed(lines):
            for lWord in reversed(line):
                if areWordsInAcceptableDistance(lWord,w):
                    if areWordsInAcceptableAngle(w,lWord):
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

def areWordsInAcceptableDistance(w1, w2):
    maxDist=100
    d = wordDistance(w1, w2)
    return  d<maxDist

def areWordsInAcceptableAngle(x, y):
    a1 = getThreePointAngle(x['sp'], x['ep'], y['sp'])
    a2 = getThreePointAngle(x['sp'], x['ep'], y['ep'])
    a3 = getThreePointAngle(x['ep'], x['sp'], y['sp'])
    a4 = getThreePointAngle(x['ep'], x['sp'], y['ep'])
    a5 = getThreePointAngle(y['sp'], y['ep'], x['sp'])
    a6 = getThreePointAngle(y['sp'], y['ep'], x['ep'])
    a7 = getThreePointAngle(y['ep'], y['sp'], x['sp'])
    a8 = getThreePointAngle(y['ep'], y['sp'], x['ep'])
    a=min(a1,a2,a3,a4,a5,a6,a7,a8)
    angleFactor=3
    if 0<=a<=angleFactor:
        return True
    if (180-angleFactor)<=a<=(180+angleFactor):
        return True
    if (360-angleFactor)<=a<=360:
        return True
    return False

def wordDistance(w1, w2):
    d1=getPointDistance(w1['ep'],w2['sp'])
    d2=getPointDistance(w2['ep'],w1['sp'])
    return min(d1,d2)

def getPointDistance(p1,p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

def getThreePointAngle(a, b, c):
    ang = abs(math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])))
    return ang