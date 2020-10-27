import sys

from DetectCorrectAndClassify.ApplyCorrection import ApplyCorrection
from DetectCorrectAndClassify.DetectAndClassify import DetectAndClassify
from Helper.AlgorithmicMethods import GetSequentialDataBlocks
from ImageProcessor.InitializeDataFromImage import InitializeDataFromImage


def processTagImage(suggestEngine,imagePath, minimumConfidence):
    print("Processing: " + imagePath)
    dataFrame=InitializeDataFromImage(imagePath)
    sdb = GetSequentialDataBlocks(dataFrame)
    DetectAndClassify(suggestEngine,sdb, minimumConfidence)
    ApplyCorrection(sdb)
    return sdb
    pass


