'''
Purpose: Extract tag image from bigger image from the bottom right corner
Algorithm: find left edge, and find top edge, and crop the image by the top left corner found
bottom right corner is taken as end of the picture
'''
import os
from urllib.request import urlopen
import numpy as np
import cv2

from DatabaseProcessing.DatabaseProcessing import SaveTagtoDatabase
from ImageProcessor.TagProcessorReadDetectCorrectClassifySave import processTagImage

topLeftTemplates = []
leftEdgeTemplates = []
topEdgeTemplates = []

def initializeTemplates():
    global topLeftTemplates
    global leftEdgeTemplates
    global topEdgeTemplates
    topLeftTemplates = GetTemplateDataListFromFolder("./InputResources/EdgeTemplates/topleft/")
    leftEdgeTemplates = GetTemplateDataListFromFolder("./InputResources/EdgeTemplates/left/")
    topEdgeTemplates = GetTemplateDataListFromFolder("./InputResources/EdgeTemplates/top/")


def GetTemplateDataListFromFolder(folderPath):
    template_data = []
    for filename in sorted(os.listdir(folderPath)):
        if filename.endswith(".png"):
            image = cv2.imread(os.path.join(folderPath, filename), 0)
            template_data.append(image)
    return template_data


def GetCoordinatesOfMatchingTemplateBetweenTwoPoints(cv2RgbImg, templates, xStart, yStart, xEnd, yEnd, threshold):
    img_gray = cv2.cvtColor(cv2RgbImg, cv2.COLOR_BGR2GRAY)
    for img_template in templates:
        w, h = img_template.shape[::-1]
        res = cv2.matchTemplate(img_gray, img_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        for pt in reversed(list(zip(*loc[::-1]))):
            if xStart <= pt[0] <= xEnd and yStart <= pt[1] <= yEnd:
                xval = pt[0] + int(w // 2)
                yval = pt[1] + int(h // 2)

                return xval, yval
    return xStart, yStart


# main method to find the tag on image, returns tag image from larger image
def GetTagImageFromTheLargeImage(img_rgb):
    tagMaxArea = 50000
    tagMinArea = 10000
    ih, iw, oc = img_rgb.shape
    ih = int(ih)
    iw = int(iw)
    # if the image is already a tag return that image.
    if ih < iw or ih * iw < tagMaxArea:
        return img_rgb

    xStart = int(iw // 2)
    xEnd = int(iw - iw // 10)
    yStart = int(ih // 1.5)
    yEnd = int(ih - ih // 10)
    # try to find the top left corner edge
    x, y = GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, topLeftTemplates, xStart, yStart, xEnd, yEnd, 0.8)
    # if top left corner is not found
    if y == yStart and x == xStart:
        # try to find left edge
        x, yTemp = GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, leftEdgeTemplates, xStart, yStart, xEnd,
                                                                    yEnd, 0.7)
        # try to find top edge
        xStart = x - int(iw // 50)  # start little left of the left edge
        yEnd = yTemp + int(iw // 50)  # End little down of the yValue value found on the edge
        xTemp, y = GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, topEdgeTemplates, xStart, yStart, xEnd,
                                                                    yEnd, 0.7)
    # possibly no tag is found then return original image and starting point
    tagArea=int((ih - y) * (iw - x))
    if  (iw - x)<(ih - y) or tagArea < tagMinArea:
        print("Looks like the image is a tag")
        return img_rgb
    else:
        return img_rgb[y:ih, x:iw]


# returns tag image by the image path
def GetTagImageFromTheImagePath(imagePath):
    print("Processing: " + imagePath)
    img_rgb = ""
    if ":" in imagePath:
        resp = urlopen(imagePath)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        img_rgb = cv2.imread(imagePath)
    return GetTagImageFromTheLargeImage(img_rgb)


# saves tag image to the destination folder
def SaveTagImageToTheDestinationFolder(image, destinationFolder, fileName):
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)
    cv2.imwrite(os.path.join(destinationFolder, fileName), image)

# extract tag from larger image and save to destination and return destinaitonPath
def ExtractAndProcessTagFromImagePath(suggestEngine, imagePath, destinationFolder, minimumConfidence):
    fileName = imagePath.split('/')[-1]
    tagImage=GetTagImageFromTheImagePath(imagePath)
    SaveTagImageToTheDestinationFolder(tagImage, destinationFolder, fileName)
    tagPath=os.path.join(destinationFolder, fileName)
    sdb=processTagImage(suggestEngine,tagPath, minimumConfidence)
    return tagPath,sdb


# process images inside the folder
def ProcessImagesInTheFolder(suggestEngine, imageFolder, destinationFolder, minimumConfidence):
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
           ProcessImageAndSaveToDatabase(suggestEngine, os.path.join(imageFolder, filename), destinationFolder, minimumConfidence)


# process images from the provided urls inside the text file
def ProcessImagesFromTheUrlsInTheTextFile(suggestEngine, textFile, destinationFolder, minimumConfidence):
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)

    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url = line.replace("\n", "")
        ProcessImageAndSaveToDatabase(suggestEngine, url, destinationFolder, minimumConfidence)

def ProcessImageAndSaveToDatabase(suggestEngine, imagePath, destinationFolder, minimumConfidence):
    tagPath, sdb = ExtractAndProcessTagFromImagePath(suggestEngine, imagePath, destinationFolder, minimumConfidence)
    SaveTagtoDatabase(tagPath, sdb)
