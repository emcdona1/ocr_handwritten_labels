'''used to process multiple images'''

import os
from urllib.request import urlopen
import numpy as np
import cv2

from DatabaseProcessing.DatabaseProcessing import SaveTagtoDatabase
from ImageProcessor.TagProcessorReadDetectCorrectClassifySave import processTagImage

class ImageProcessor():
    topLeftTemplates=[]
    leftEdgeTemplates=[]
    topEdgeTemplates=[]

    templatesInitialized=False
    @classmethod
    def GetTemplateDataListFromFolder(cls,folderPath):
        template_data = []
        for filename in sorted(os.listdir(folderPath)):
            if filename.endswith(".png"):
                image = cv2.imread(os.path.join(folderPath, filename), 0)
                template_data.append(image)
        return template_data

    @classmethod
    def InitializeTemplates(cls,tlt="./InputResources/EdgeTemplates/topleft/",let="./InputResources/EdgeTemplates/left/",tet="./InputResources/EdgeTemplates/top/"):
        cls.topLeftTemplates = cls.GetTemplateDataListFromFolder(tlt)
        cls.leftEdgeTemplates = cls.GetTemplateDataListFromFolder(let)
        cls.topEdgeTemplates = cls.GetTemplateDataListFromFolder(tet)
        cls.templatesInitialized=True

    def __init__(self, suggestEngine,imagePath,destinationFolder,minimumConfidence):
        self.suggestEngine = suggestEngine
        self.imagePath = imagePath
        self.destinationFolder=destinationFolder
        self.minimumConfidence=minimumConfidence
        self.tagPath=None
        self.sdb=None
        if not ImageProcessor.templatesInitialized:
            ImageProcessor.InitializeTemplates()
    def processImage(self):
            self.tagPath, self.sdb = self.ExtractAndProcessTagFromImagePath()
            SaveTagtoDatabase(self.tagPath, self.sdb)
            return self.tagPath,self.sdb

    def GetCoordinatesOfMatchingTemplateBetweenTwoPoints(self,cv2RgbImg, templates, xStart, yStart, xEnd, yEnd, threshold):
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

    # saves tag image to the destination folder
    def SaveTagImageToTheDestinationFolder(self,image, fileName):
        if not os.path.exists(self.destinationFolder):
            os.makedirs(self.destinationFolder)
        cv2.imwrite(os.path.join(self.destinationFolder, fileName), image)

    # main method to find the tag on image, returns tag image from larger image
    def GetTagImageFromTheLargeImage(self,img_rgb):
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
        x, y = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb,ImageProcessor.topLeftTemplates, xStart, yStart, xEnd, yEnd,
                                                                0.8)
        # if top left corner is not found
        if y == yStart and x == xStart:
            # try to find left edge
            x, yTemp = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, ImageProcessor.leftEdgeTemplates, xStart, yStart,
                                                                        xEnd,
                                                                        yEnd, 0.7)
            # try to find top edge
            xStart = x - int(iw // 50)  # start little left of the left edge
            yEnd = yTemp + int(iw // 50)  # End little down of the yValue value found on the edge
            xTemp, y = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, ImageProcessor.topEdgeTemplates, xStart, yStart, xEnd,
                                                                        yEnd, 0.7)
        # possibly no tag is found then return original image and starting point
        tagArea = int((ih - y) * (iw - x))
        if (iw - x) < (ih - y) or tagArea < tagMinArea:
            print("Looks like the image is a tag")
            return img_rgb
        else:
            return img_rgb[y:ih, x:iw]

    def GetTagImageFromTheImagePath(self,imagePath):
        img_rgb = ""
        if ":" in imagePath:
            resp = urlopen(imagePath)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            img_rgb = cv2.imread(imagePath)
        return self.GetTagImageFromTheLargeImage(img_rgb)

    def ExtractAndProcessTagFromImagePath(self):
        fileName = self.imagePath.split('/')[-1]
        tagImage=self.GetTagImageFromTheImagePath(self.imagePath)
        self.SaveTagImageToTheDestinationFolder(tagImage, fileName)
        tagPath=os.path.join(self.destinationFolder, fileName)
        sdb=processTagImage(self.suggestEngine,tagPath, self.minimumConfidence)
        return tagPath,sdb
