import sys

from DetectionCorrectAndClassify.DetectAndClassify import DetectAndClassify
from Helper.AlgorithmicMethods import GetSequentialDataBlocks
from ImageProcessor.InitializeDataFromImage import InitializeDataFromImage


def processTagImage(suggestEngine,imagePath, minimumConfidence):
    print("TagProcessorReadDetectCorrectClassifySave.py- Now processing: "+imagePath)
    dataFrame=InitializeDataFromImage(imagePath)

    sdb = GetSequentialDataBlocks(dataFrame)
    DetectAndClassify(suggestEngine,sdb, minimumConfidence)
    try:
        print("correction skipped for now")
    except:
        print("Could not apply the correction from bert")
        print(sys.exc_info())

    return sdb
    pass


