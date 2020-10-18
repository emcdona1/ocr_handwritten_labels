import sys
from algorithmicMethods import getSequentialDataBlocks
from applyCorrection import applyCorrection
from detectWrongWords import detectWrongWords
from initializeDataFromImage import initializeDataFromImage
from wordCategories import autoClassifyWords

def processTagImage(imagePath, minimumConfidence):
    print("tagProcessor.py- Now processing: "+imagePath)
    dataFrame=initializeDataFromImage(imagePath)
    sdb = getSequentialDataBlocks(dataFrame)
    detectWrongWords(sdb, minimumConfidence)
    try:
        applyCorrection(sdb)
    except:
        print("Could not apply the correction from bert")
        print(sys.exc_info())
    autoClassifyWords(sdb)
    return sdb
    pass


