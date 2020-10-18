
import math

def addWordInProperLine(lines,w):
        for line in reversed(lines):
            for lWord in reversed(line):
                if areWordsInAcceptableAngle(w,lWord):
                    line.append(w)
                    return
        lines.append([w])

def sortBySp(line):
  def sortKey(w):
    return int(w['sp'][0])
  return sorted(line, key=sortKey)

def addBlocksBrokenByDist(blocks, line):
    newLine=[]
    for w in line:
        if(len(newLine)==0):
            newLine.append(w)
        else:
            if areWordsInAcceptableDistance(newLine[-1],w):
                newLine.append(w)
            else:
                blocks.append(newLine)
                newLine=[w]
    if(len(newLine)>0):
        blocks.append(newLine)

def getSequentialBlocks(lines):
    blocks=[]
    for line in lines:
        line=sortBySp(line)
        addBlocksBrokenByDist(blocks, line)
    return blocks

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
    a=getThreePointAngle(x['sp'], x['ep'], y['sp'])
    angleFactor=10
    if 0<=a<=angleFactor:
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