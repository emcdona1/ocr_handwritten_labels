


'''
there are cases where big chunk of image is processed first and smaller chunk later
causing words to be appear out of index
to fix the situation evaluate the centroid of each word, and cluster them by y index
and each cluster should represent a row, serialize each cluster afterward based upon x index
'''
import math


def getSerealizedData(df):
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append((w['sp'],w))

    if len(d) < 3:
        return df
    # step #1 short vertically
    d.sort(key=sortBySpY, reverse=False)
    # step #2 create list of rows based upon the vertical gap ratio
    rows = []
    row = []
    i = 0
    for i in range(len(d)):
        if i == 0:
            row.append(d[i])
        else:
            c = d[i][1]  # current
            p = d[i - 1][1]  # previous (centroid, word), w2[0]=(xval,yval), w2[1]=word
            if areWordsInDifferentLines(c, p):
                row.sort(key=sortBySpX, reverse=False)  # order current row by x
                rows.append(row)
                row = []
            row.append(d[i])
    if (len(row)>0): # final row might not have written
        row.sort(key=sortBySpX, reverse=False)  # order current row by x
        rows.append(row)
    # step #3 serialize the indexes
    i = 1

    for r in rows:
        for w in r:
            w[1]['index'] = i
            i = i + 1
    # step #4 sort the data frame by index
    return df.sort_values(by=['index'])

##########################sub methods#########################


def determinant(a, b):
    return a[0] * b[1] - a[1] * b[0]

def getPolygonAreaByTouples (t):
    sum=0
    for i in range(len(t)-1):
        sum+=determinant(t[i],t[i+1])
    sum+=determinant(t[i+1],t[0])
    return abs(sum/2)

#one liner  sorted(range(len(a)), key=lambda i: a[i], reverse=True)[:2]

def sortBySpY(s):
    return s[0][1] #y value of the touple (x,y)

def sortBySpX(s):
    return s[0][0] #x value of the touple (x,y)


def getWordsByLinesAndBlocks(dfs):
    blocks=[]
    block=[]
    oldW=""
    oldW = None
    for index, w in dfs.iterrows():
        if w['index'] > 0:
            if w['index'] > 1:
                if areWordsInDifferentLines(w, oldW):
                    blocks.append(block)
                    block=[]
            oldW = w
            block.append(oldW)
    blocks.append(block)
    return blocks

# for the words to be in same line all the slopes must be almost equal
def areWordsInDifferentLines(w1, w2):
    print(w1['description']+" vs "+w2['description'])
    tuples=[]
    tuples.append(w1['sp'])
    tuples.append(w1['ep'])
    tuples.append(w2['sp'])
    tuples.append(w2['ep'])
    a=getPolygonAreaByTouples(tuples)
    d=wordDistance(w1,w2)
    print(a)
    print(d)
    #s1=getSlope(w1['sp'],w1['ep'])
    #s2=getSlope(w2['sp'],w2['ep'])



    #print( min(s1, s2, s3, s4, s5))

    return a>400 or d>50


def wordDistance(w1, w2):
    d1=getPointDistance(w1['ep'],w2['sp'])
    d2=getPointDistance(w2['ep'],w1['sp'])
    return min(d1,d2)

def getPointDistance(p1,p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

def getSlope(p1,p2):
    if (p2[0]-p1[0]==0):
        return (p2[1]-p1[1])*100 #infinite
    return (p2[1]-p1[1])/(p2[0]-p1[0])
