import tempfile

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def AddToLastLineOrNewLine(lines, w):
    if (len(lines) > 0):
        lWord = lines[-1][-1]
        if AreWordsInAcceptableOffsetDistance(lWord, w):
            lines[-1].append(w)
        else:
            lines.append([w])
    else:
        lines.append([w])


def SortBySp(line):
    def sortKey(w):
        return int(w['sp'][0])

    return sorted(line, key=sortKey)


def SortByFirstY(blocks):
    def sortKey(line):
        return int(line[0]['sp'][1])

    return sorted(blocks, key=sortKey)


def SortByLastX(blocks):
    def sortKey(line):
        return int(line[-1]['sp'][0])

    return sorted(blocks, key=sortKey)


def GetSequentialBlocks(lines):
    blocks = []
    for line in lines:
        blocks.append(SortBySp(line))
    return SortByFirstY(blocks)


def GetSequencialDataList(d):
    lines = []
    for w in d:
        AddToLastLineOrNewLine(lines, w)
    return GetSequentialBlocks(lines)


def GetSequentialDataBlocks(df):
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append(w)
    return GetSequencialDataList(d)


def DetectAndRemoveSmallRepeatedWordArea(x, y):
    polygonY = Polygon(y['tupleVertices'])
    c = Point((x['sp'][0] + x['ep'][0]) // 2, (x['sp'][1] + x['ep'][1]) // 2)
    if polygonY.contains(c):
        x['index'] = -1


##########################sub methods#########################

def MeetHorizontalAlignment(x, y, maxGap=70):
    if (y['sp'][0] < x['sp'][0]):
        t = x
        x = y
        y = t
    l1 = x['ep'][0] - x['sp'][0]
    l2 = y['ep'][0] - y['sp'][0]
    tl = y['ep'][0] - x['sp'][0]
    g = y['sp'][0] - x['ep'][0]
    ldiff = abs(tl - l1 - l2 - g)

    return ldiff == 0 and g <= maxGap


def MeetVerticalAlignment(w1, w2, verticleOffset=15):
    v = w2['sp'][1] - w1['ep'][1]
    return abs(v) <= verticleOffset


def AreWordsInAcceptableOffsetDistance(w1, w2):
    return MeetHorizontalAlignment(w1, w2) and MeetVerticalAlignment(w1, w2)

def GetTempFilePath():
    tf = tempfile.NamedTemporaryFile()
    return tf.name + "_temp.png"
    pass

