import sys
from algorithmicMethods import getSequentialDataBlocks
from applyCorrection import applyCorrection, applyCorrection2
from detectWrongWords import detectWrongWords
from initializeDataFromImage import initializeDataFromImage
from wordCategories import autoClassifyWords

def processTagImage(root,imagePath, minimumConfidence):
    print("tagProcessor.py- Now processing: "+imagePath)
    dataFrame=initializeDataFromImage(imagePath)

    sdb = getSequentialDataBlocks(dataFrame)
    detectWrongWords(root,sdb, minimumConfidence)
    try:
        #applyCorrection2(sdb)
        print("correction skipped for now")
    except:
        print("Could not apply the correction from bert")
        print(sys.exc_info())
    autoClassifyWords(sdb)
    return sdb
    pass


