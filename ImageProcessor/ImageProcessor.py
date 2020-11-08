'''used to process multiple images'''
import io
import os
import tempfile
from threading import Thread
from urllib.request import urlopen

import cv2
import numpy as np
from datetime import datetime

from ClassificationApp_GUI.LayoutGUI import UpdateProcessingCount
from DatabaseProcessing.DatabaseProcessing import SaveTagtoDatabase

from DetectCorrectAndClassify.ApplyCorrection import ApplyCorrection
from DetectCorrectAndClassify.DetectAndClassify import DetectAndClassify
from Helper.AlgorithmicMethods import GetNormalizedSequentialDataBlocks, GetTempFilePath
from ImageProcessor.InitializeBarCodeInfoTable import InitializeBarCodeInfoForAKey_InAThread
from ImageProcessor.InitializeDataFromImage import GetInformationAsDataFrameFromImage, GetBarCodeFromOCRData



class ImageProcessor():
    topLeftTemplates = []
    leftEdgeTemplates = []
    topEdgeTemplates = []

    templatesInitialized = False

    @classmethod
    def GetTemplateDataListFromFolder(cls, folderPath):
        template_data = []
        for filename in sorted(os.listdir(folderPath)):
            if filename.endswith(".png"):
                image = cv2.imread(os.path.join(folderPath, filename), 0)
                template_data.append(image)
        return template_data

    @classmethod
    def InitializeTemplates(cls, tlt="./InputResources/EdgeTemplates/topleft/",
                            let="./InputResources/EdgeTemplates/left/", tet="./InputResources/EdgeTemplates/top/"):
        cls.topLeftTemplates = cls.GetTemplateDataListFromFolder(tlt)
        cls.leftEdgeTemplates = cls.GetTemplateDataListFromFolder(let)
        cls.topEdgeTemplates = cls.GetTemplateDataListFromFolder(tet)
        cls.templatesInitialized = True

    def __init__(self, suggestEngine, imagePath, minimumConfidence, extractTag):
        self.suggestEngine = suggestEngine
        self.imagePath = imagePath
        self.tagPath=imagePath #can be overwritten when tag is extracted.
        self.minimumConfidence = minimumConfidence
        self.sdb = None
        self.extractTag=extractTag
        if not ImageProcessor.templatesInitialized:
            ImageProcessor.InitializeTemplates()

    def processImage(self):
        print("Processing: " + self.imagePath)
        self.startTime = datetime.now()
        self.SetImageRGBAndSaveToTempLocation()
        self.ocrThread= Thread(target=self.InitializeOCRData)
        self.ocrThread.start()
        self.ExtractTagContentFromImageAndSetTempTagPath()
        self.ocrThread.join()
        self.barCode=GetBarCodeFromOCRData(self.dataFrame['description'][0])
        self.sdb = GetNormalizedSequentialDataBlocks(self.startX, self.startY, self.dataFrame)
        DetectAndClassify(self.suggestEngine, self.sdb, self.minimumConfidence)
        ApplyCorrection(self.sdb)
        self.endTime = datetime.now()
        self.processingTime=(self.endTime - self.startTime).total_seconds()
        self.tagId,self.importDate,self.hasBarCodeInDB = SaveTagtoDatabase(self.imagePath, self.processingTime, self.tagContent, self.sdb,self.barCode)
        UpdateProcessingCount(-1,self.processingTime,self.tagId,self.sdb,self.tagPath,self.imagePath,self.importDate,self.barCode)
        if len(self.barCode)>0 and self.hasBarCodeInDB==0:
            InitializeBarCodeInfoForAKey_InAThread(self.barCode)


    def InitializeOCRData(self):
        with io.open(self.tempImagePath, 'rb') as image_file:
            self.imageContent = image_file.read()
        self.dataFrame = GetInformationAsDataFrameFromImage(self.imageContent)
        pass

    def GetCoordinatesOfMatchingTemplateBetweenTwoPoints(self, cv2RgbImg, templates, xStart, yStart, xEnd, yEnd,
                                                         threshold):
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
    def ExtractTagRGBFromTheLargeImageRGB(self, img_rgb):
        tagMaxArea = 50000
        tagMinArea = 10000
        ih, iw, oc = img_rgb.shape
        ih = int(ih)
        iw = int(iw)
        # if the image is already a tag return that image.
        if ih < iw or ih * iw < tagMaxArea:
            return 0,0,img_rgb

        xStart = int(iw // 2)
        xEnd = int(iw - iw // 10)
        yStart = int(ih // 1.5)
        yEnd = int(ih - ih // 10)
        # try to find the top left corner edge
        x, y = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, ImageProcessor.topLeftTemplates, xStart,
                                                                     yStart, xEnd, yEnd,
                                                                     0.8)
        # if top left corner is not found
        if y == yStart and x == xStart:
            # try to find left edge
            x, yTemp = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, ImageProcessor.leftEdgeTemplates,
                                                                             xStart, yStart,
                                                                             xEnd,
                                                                             yEnd, 0.7)
            # try to find top edge
            xStart = x - int(iw // 50)  # start little left of the left edge
            yEnd = yTemp + int(iw // 50)  # End little down of the yValue value found on the edge
            xTemp, y = self.GetCoordinatesOfMatchingTemplateBetweenTwoPoints(img_rgb, ImageProcessor.topEdgeTemplates,
                                                                             xStart, yStart, xEnd,
                                                                             yEnd, 0.7)
        # possibly no tag is found then return original image and starting point
        tagArea = int((ih - y) * (iw - x))
        if (iw - x) < (ih - y) or tagArea < tagMinArea:
            print("Looks like the image is a tag")
            return 0,0,img_rgb
        else:
            return x,y,img_rgb[y:ih, x:iw]

    def SetImageRGBAndSaveToTempLocation(self):
        if ":" in self.imagePath:
            resp = urlopen(self.imagePath)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            img_rgb = cv2.imread(self.imagePath)
        self.img_rgb=img_rgb
        self.tempImagePath=GetTempFilePath("_temp_wholeImage.png")
        cv2.imwrite(self.tempImagePath,img_rgb)
        pass

    def ExtractTagContentFromImageAndSetTempTagPath(self):
        if (self.extractTag):
            self.startX,self.startY,tag_rgb=self.ExtractTagRGBFromTheLargeImageRGB(self.img_rgb)
            tempTagPath=GetTempFilePath("_temp_tagPath.png")
            cv2.imwrite(tempTagPath, tag_rgb)
            self.tagPath=tempTagPath
        else:
            self.startX=0
            self.startY=0
            self.tagPath=self.tempImagePath

        with io.open(self.tagPath, 'rb') as image_file:
            self.tagContent = image_file.read()
