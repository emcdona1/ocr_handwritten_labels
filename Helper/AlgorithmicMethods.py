import tempfile

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def add_to_last_line_or_new_line(lines, w):
    if len(lines) > 0:
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


def sort_by_first_y(blocks):
    def sort_key(line):
        return int(line[0]['sp'][1])
    return sorted(blocks, key=sort_key)


def sort_by_last_x(blocks):
    def sort_key(line):
        return int(line[-1]['sp'][0])
    return sorted(blocks, key=sort_key)


def get_sequential_blocks(lines):
    blocks = []
    for line in lines:
        blocks.append(SortBySp(line))
    return sort_by_first_y(blocks)


def get_sequential_data_list(d):
    lines = []
    for w in d:
        add_to_last_line_or_new_line(lines, w)
    return get_sequential_blocks(lines)


def get_normalized_sequential_data_blocks(start_x, start_y, df):
    """ Converts ImageProcessor.dataFrame into a list -- unsure why it gives it a certain shape.
    StartX and start_y refer to attempting to detect a label. These are both 0 if a label ('tag') image is used. """
    d = []
    if start_x == 0 and start_y == 0:  # processing whole image
        for index, w in df.iterrows():
            if w['index'] > 0:
                d.append(w)
    else:  # processing part of image
        for index, w in df.iterrows():
            if w['index'] > 0:
                if normalize_position(start_x, start_y, w):
                    d.append(w)
    return get_sequential_data_list(d)


def normalize_position(start_x, start_y, w):
    w['tupleVertices'] = [(x - start_x, y - start_y) for x, y in w['tupleVertices']]
    return w['tupleVertices'][0][0] >= 0 and w['tupleVertices'][0][1] >= 0


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


def GetTempFilePath(ending):
    tf = tempfile.NamedTemporaryFile()
    return tf.name + ending
    pass
