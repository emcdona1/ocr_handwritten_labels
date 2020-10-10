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


def getCoordinatesOfMatchingTemplate(cv2RgbImg, edgeTemplates, hs, ws, he, we):
    img_gray = cv2.cvtColor(cv2RgbImg, cv2.COLOR_BGR2GRAY)
    for filename in sorted(os.listdir(edgeTemplates)):
        if filename.endswith(".png"):
            img_template = cv2.imread(os.path.join(edgeTemplates, filename), 0)
            w, h = img_template.shape[::-1]
            res = cv2.matchTemplate(img_gray, img_template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = np.where(res >= threshold)

            for pt in reversed(list(zip(*loc[::-1]))):
                if pt[0] > ws and pt[1] > hs and pt[0] < we and pt[1] < he:
                    yval = pt[1]+int(h//2)
                    xval = pt[0]+int(w//2)
                    return yval,xval
    return hs,ws

def GetTagByEdgeDetection(imagePath, destination):
    print("Processing: "+imagePath)
    img_rgb = ""
    if ":" in imagePath:
        resp = urlopen(imagePath)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        img_rgb = cv2.imread(imagePath)

    edgeTemplates = "./EdgeTemplates/"

    oh, ow, oc = img_rgb.shape
    hs = int(oh // 1.5)
    ws = int(ow // 2)
    he=int(oh-oh // 15)
    we=int(ow-ow // 15)

    ignore,x= getCoordinatesOfMatchingTemplate(img_rgb, edgeTemplates + "left/", hs, ws, he, we)
    #if above method sends incorrect then following will be worthless
    y,ignore=getCoordinatesOfMatchingTemplate(img_rgb, edgeTemplates + "top/", hs + int(oh // 15), ws, ignore - int(oh // 15), we)

    #cv2.rectangle(img_rgb, (x, y), (ow, oh), (0, 200, 255), 2)
    #cv2.imwrite(destination, img_rgb)

    imc = img_rgb[y:oh, x:ow]
    cv2.imwrite(destination, imc)

def GetTagsFromImageFolder(imageFolder,destinationFolder):
    for filename in os.listdir(imageFolder):
        if filename.endswith(".jpg"):
            GetTagByEdgeDetection(os.path.join(imageFolder, filename), os.path.join(destinationFolder, filename))

def GetTagsFromTagUrlFile(textFile,destinationFolder):
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)

    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url=line.replace("\n","")
        fileName = url.split('/')[-1]
        destination = os.path.join(destinationFolder, fileName)
        GetTagByEdgeDetection(url, os.path.join(destinationFolder, destination))

destination=os.path.expanduser("~/Desktop/")+"Tags/"
GetTagsFromTagUrlFile("./InputResources/TagUrls.txt",destination)
GetTagsFromImageFolder("./InputResources/SampleImages/",destination)


