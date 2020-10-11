'''
Purpose: Extract tag image from bigger image from the bottom right corner
Algorithm: find left edge, and find top edge, and crop the image by the top left corner found
bottom right cornor is taken as end of the picture
'''
import os
from urllib.request import urlopen
import numpy as np
import cv2
from pandas import np


def getCoordinatesOfMatchingTemplateBetweenTwoPoints(cv2RgbImg, edgeTemplates,xStart, yStart, xEnd,yEnd, threshold):
    img_gray = cv2.cvtColor(cv2RgbImg, cv2.COLOR_BGR2GRAY)
    for filename in sorted(os.listdir(edgeTemplates)):
        if filename.endswith(".png"):
            img_template = cv2.imread(os.path.join(edgeTemplates, filename), 0)
            w, h = img_template.shape[::-1]
            res = cv2.matchTemplate(img_gray, img_template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            for pt in reversed(list(zip(*loc[::-1]))):
                if xStart<=pt[0]<=xEnd and yStart<=pt[1]<=yEnd:
                    xval = pt[0] + int(w // 2)
                    yval = pt[1]+int(h//2)

                    return xval,yval
    return xStart, yStart

def GetTagByEdgeDetection(imagePath, destination, justMarkTag):
    print("Processing: "+imagePath)
    img_rgb = ""
    if ":" in imagePath:
        resp = urlopen(imagePath)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        img_rgb = cv2.imread(imagePath)

    edgeTemplates = "./EdgeTemplates/"

    ih, iw, oc = img_rgb.shape
    xStart = int(iw // 2)
    xEnd = int(iw - iw // 10)
    yStart = int(ih // 1.5)
    yEnd = int(ih - ih // 10)


    x,y=getCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, edgeTemplates + "topleft/", xStart,yStart, xEnd, yEnd, 0.8)
    if not x==xStart and justMarkTag:
        cv2.rectangle(img_rgb, (x-10, y-10), (x + 10, y + 10), (255, 0, 255), 4)
    if y==yStart and x==xStart:
        x,yTemp= getCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, edgeTemplates + "left/",xStart, yStart, xEnd, yEnd, 0.7)

        xStart=x-int(iw//50) # start little left of the left edge
        yEnd=yTemp+int(iw//50) # End little down of the yValue value found on the edge

        xTemp,y=getCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, edgeTemplates + "top/", xStart, yStart, xEnd, yEnd, 0.7)
        if justMarkTag:
            cv2.rectangle(img_rgb, (xTemp, y), (xTemp + 10, y + 10), (255, 0, 255), 4)
            cv2.rectangle(img_rgb, (x, yTemp), (x + 10, yTemp + 10), (255, 0, 255), 4)

    if justMarkTag:
        cv2.rectangle(img_rgb, (x, y), (iw, ih), (0, 200, 255), 2)
        cv2.imwrite(destination, img_rgb)
    else:
        imc = img_rgb[y:ih, x:iw]
        cv2.imwrite(destination, imc)

def GetTagsFromImageFolder(imageFolder,destinationFolder,justMarkTag):
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            GetTagByEdgeDetection(os.path.join(imageFolder, filename), os.path.join(destinationFolder, filename),justMarkTag)

def GetTagsFromTagUrlFile(textFile,destinationFolder,justMarkTag):
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)

    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url=line.replace("\n","")
        fileName = url.split('/')[-1]
        destination = os.path.join(destinationFolder, fileName)
        GetTagByEdgeDetection(url, os.path.join(destinationFolder, destination),justMarkTag)

destination=os.path.expanduser("~/Desktop/")+"Tags/"
SourceFolder=os.path.expanduser("~/Desktop/")+"AllImages/"
#justMarkTag with value false will crop the tag
justMarkTag=False
GetTagsFromImageFolder(SourceFolder, destination, justMarkTag)
#GetTagsFromTagUrlFile("./InputResources/TagUrls.txt",destination,justMarkTag)
#GetTagsFromImageFolder("./InputResources/SampleImages/",destination,justMarkTag)


