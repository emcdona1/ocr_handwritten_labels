'''
Purpose: Extract tag image from bigger image from the bottom right corner
Algorithm: find the color difference and get the tag by the polygon
'''
import os
from array import array
import math
from collections import defaultdict


import cv2
from PIL import Image
from matplotlib.pyplot import gray
from pandas import np

def GetTagFromImage3(imagePath,destination):
    im = Image.open(imagePath)
    w, h = im.size
    imc = im.crop((w // 2, h // 1.3, w, h))
    w,h=imc.size
    image = np.array(imc)

    x,y=0,0#w//5,(h//3)#getXYStart(image,w//2,h//2)
    cv2.rectangle(image, (x, y), (w,h), (36, 255, 12), 3)
    cv2.imwrite(destination, image)


def GetTagFromImage(imagePath,destination):
    im = Image.open(imagePath)
    w, h = im.size
    imc = im.crop((w // 2, h // 1.5, w, h))
    w,h=imc.size
    image = np.array(imc)

    x,y=getXYStart(image,w//2,h//2)
    cv2.rectangle(image, (x, y), (w,h), (36, 255, 12), 3)
    cv2.imwrite(destination, image)

def getXYStart(image,xMax,yMax):
    threshold=40
    print(yMax)
    y=yMax
    sideLength=threshold
    oldVal=getAvgColor(image,sideLength//2,y,sideLength//2)
    x=0
    for x in range(sideLength//2,xMax//2,sideLength//4):
        newVal=getAvgColor(image,x,y,sideLength)
        if(areDifferentColor(oldVal, newVal, threshold)):
            break
    return x,y

'''
return average color between area (x,y) and (x+n,y+n)
'''
def getAvgColor(image,x,y,n):
    if n<2:
        return image[x,y]
    r, g, b = 0, 0, 0
    count = 0
    for i in range(x, x + n):
        for j in range(y, y + n):
            pr, pg, pb = image[i, j]
            r += pr
            g += pg
            b += pb
            count += 1
    return ((r / count), (g / count), (b / count))



def areDifferentColor(rgb1,rgb2,threshold):
   d=math.sqrt((rgb1[0]-rgb2[0])**2 + (rgb1[1]-rgb2[1])**2 +(rgb1[2]-rgb2[2])**2)
   p=d/((rgb1[0]+rgb1[1]+rgb1[2])/3)*100
   return p>threshold

def GetTagFromImage2(imagePath,destination):
    ax=15
    ay=40
    gx=3
    gy=21
    gz=2
    dx=7
    kx=9
    ky=6
    minArea=4000

    im = Image.open(imagePath)
    w, h = im.size
    imc = im.crop((w//2, h//1.5, w, h))
    #cv2.resize(imc, (2//2, h//2))
    image = np.array(imc)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (gx, gy), gz)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, ax, ay)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kx, ky))
    dilate = cv2.dilate(thresh, kernel, iterations=dx)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > minArea:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 3)

    cv2.imwrite(destination,image)


def GetTagsFromImageFolder(imageFolder, destination):
    for filename in os.listdir(imageFolder):
        if filename.endswith(".jpg"):
            GetTagFromImage3(os.path.join(imageFolder, filename),os.path.join(destination, filename))

imageFolder="/Users/Keshab/Desktop/ProjectFiles/images/Tags/Steyermark Fern Images/"
destination="/Users/Keshab/Desktop/Tags/"
GetTagsFromImageFolder(imageFolder,destination)
imageFolder="/Users/Keshab/Desktop/ProjectFiles/images/Tags/EugenioLeite Spruce Labels/"
GetTagsFromImageFolder(imageFolder,destination)

#GetTagFromImage(imagePath)