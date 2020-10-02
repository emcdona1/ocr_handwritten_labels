'''
Purpose: Extract tag image from bigger image from the bottom right corner
Algorithm: get the tag area by ratio
This is sample file which, please provide correct folder paths and text file when needed.
'''
import os
from urllib.request import urlopen
import numpy as np
import cv2
from pandas import np

def CropImageByRatio(imagePath, destinationFolder, wr=2, hr=1.5):
    print("Processing:"+imagePath)
    fileName=imagePath.split('/')[-1]
    destination = os.path.join(destinationFolder, fileName)
    im=""
    if ":" in imagePath:
        resp = urlopen(imagePath)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        im = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        im = cv2.imread(imagePath)
    h,w,c=im.shape
    hs=int(h//hr)
    ws=int(w//wr)
    imc = im[hs:h,ws:w]
    cv2.imwrite(destination, imc)

def GetTagsFromImageFolder(imageFolder, destinationFolder):
    for filename in os.listdir(imageFolder):
        if filename.endswith(".jpg"):
            CropImageByRatio(os.path.join(imageFolder, filename), destinationFolder,2,1.5)

def GetTagsFromTagUrlFile(textFile,destinationFolder):
    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url=line.replace("\n","")
        CropImageByRatio(url, destinationFolder,2,1.5)



imageFolder="/Users/Keshab/Desktop/ProjectFiles/images/Tags/Steyermark Fern Images/"
destination="/Users/Keshab/Desktop/Tags/"
GetTagsFromImageFolder(imageFolder,destination)
imageFolder="/Users/Keshab/Desktop/ProjectFiles/images/Tags/EugenioLeite Spruce Labels/"
GetTagsFromImageFolder(imageFolder,destination)
textFile="/Users/Keshab/Desktop/ProjectFiles/images/Tags/TagUrls.txt"
GetTagsFromTagUrlFile(textFile,destination)
