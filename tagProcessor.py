import sys
from algorithmicMethods import getSerealizedData
from applyCorrection import applyCorrection
from detectWrongWords import detectWrongWords
from initializeDataFromImage import initializeDataFromImage
from wordCategories import autoClassifyWords

def processTagImage(imagePath, minimumConfidence):
    df=initializeDataFromImage(imagePath)
    df = getSerealizedData(df)
    detectWrongWords(df, minimumConfidence)
    try:
        applyCorrection(dfs=df)
    except:
        print("Could not apply the correction from bert")
        print(sys.exc_info())
    autoClassifyWords(df)
    return df
    pass


