from difflib import SequenceMatcher

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#usage to find the area of a polygon
from globalCalls import debugDF, isCurrentWordInNextLine

'''
There are cases, where subset of word is being recognized as seperate word, 
to fix this situations, loop by larger area to smaller area
if smaller area's centroid falls in larger area 
'''
def RemoveDuplicates(df):
    d=[]

    for index, w in df.iterrows():
        if(w['index']>0):
            d.append((w['area'], w))

    d.sort(key=sortByArea, reverse=True)
    for i in range(len(d)-1):
        for j in range(i+1,len(d),1):
                if Polygon(d[i][1]['tupleVertices']).contains(Point(d[j][1]['centroid'][0],d[j][1]['centroid'][1]))\
                        and d[j][1]['description'].lower() in d[i][1]['description'].lower():
                    d[j][1]['index']=-1 # having index=-1 will make sure that it will be ignored in future.
    #debugDF(df)
    pass

'''
there are cases where big chunk of image is processed first and smaller chunk later
causing words to be appear out of index
to fix the situation evaluate the centroid of each word, and cluster them by y index
and each cluster should represent a row, serialize each cluster afterward based upon x index
'''
def GetSerealizedData2(df,GapRatio):
    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append((w['centroid'],w))

    if len(d) < 3:
        return df
    # step #1 short vertically
    d.sort(key=sortByCentroidY, reverse=False)
    # step #2 create list of rows based upon the vertical gap ratio
    rows = []
    row = []
    i = 0

    for i in range(len(d)):
        if i == 0:
            row.append(d[i])
        else:
            c = d[i][1]  # current
            p = d[i - 1][1]  # previous (centroid, word), p[0]=(xval,yval), p[1]=word
            if isCurrentWordInNextLine(currentWord=c,previousWord=p):
                row.sort(key=sortByCentroidX, reverse=False)  # order current row by x
                rows.append(row)
                row = []
            row.append(d[i])
    if (len(row)>0): # final row might not have written
        row.sort(key=sortByCentroidX, reverse=False)  # order current row by x
        rows.append(row)
    # step #3 serialize the indexes
    i = 1
    for r in rows:
        for w in r:
            w[1]['index'] = i
            i = i + 1
    # step #4 sort the data frame by index
    return df.sort_values(by=['index'])
    return df



def GetSerealizedData(df, GapRatio):

    d = []
    for index, w in df.iterrows():
        if (w['index'] > 0):
            d.append((w['centroid'], w))

    if len(d)<3:
        return df
    #step #1 short vertically
    d.sort(key=sortByCentroidY, reverse=False)
    #step #2 create list of rows based upon the vertical gap ratio
    rows=[]
    row=[]
    i=0

    for i in range(len(d)-1):
        if i==0:
            row.append(d[i])
        else:
            G1=(d[i][0][1]-d[i-1][0][1])+1 # vertical gap between current word and previous word
            G2=(d[i+1][0][1]-d[i][0][1])+1 # vertical gap between next word and current word
            if (G1/G2>GapRatio): # we are in a new line
                row.sort(key=sortByCentroidX, reverse=False)#order current row by x
                rows.append(row)
                row=[]
            row.append(d[i])
        if i==(len(d)-2):#last iteration
             if(G2/G1>GapRatio) and len(row)>0:
                 row.sort(key=sortByCentroidX, reverse=False)  # order current row by x
                 rows.append(row)
                 row = []
                 row.append(d[i+1])
                 rows.append(row)
                 row = []
             else:
                 row.append(d[i+1])
                 row.sort(key=sortByCentroidX, reverse=False)  # order current row by x
                 rows.append(row)
                 row = []

    #step #3 serialize the indexes
    i=1
    for r in rows:
        for w in r:
            w[1]['index']=i
            i=i+1
    #step #4 sort the data frame by index
    return df.sort_values(by=['index'])

'''return top suggestions which has higher probability of chances to meet with charsAboveMinimumConfidance'''
def getFilteredSuggestionList(charsAboveMinimumConfidance,suggestions):
    count=5
    print("Enhance this method: getFilteredSuggestionList")
    if(len(suggestions)<count):
        return suggestions
    # return suggestions
    ratioSuggestion=[]
    for s in suggestions:
        ratioSuggestion.append((SequenceMatcher(None,s,charsAboveMinimumConfidance).ratio(),s))
    ratioSuggestion.sort(key=sortBySugestionRatio, reverse=True)
    return [t[1] for t in ratioSuggestion[:count]] #return top 'count' list of tuple (ratio, suggestion)



##########################sub methods#########################


def determinant(a, b):
    return a[0] * b[1] - a[1] * b[0]

def getPolygonAreaByTouples (t):
    sum=0
    for i in range(len(t)-1):
        sum+=determinant(t[i],t[i+1])
    sum+=determinant(t[i+1],t[0])
    return sum/2

#one liner  sorted(range(len(a)), key=lambda i: a[i], reverse=True)[:2]

def sortByArea(s):
    return s[0] #area

def sortByCentroidY(s):
    return s[0][1] #y value of the touple (x,y)

def sortByCentroidX(s):
    return s[0][0] #x value of the touple (x,y)

def sortBySugestionRatio(r):
    return r[0]# valupe of ration in the touple (ratio, suggestion)