import os

from ScienteficNameService.sns import getSuggestions
from getWordsInformation import getDescriptionFromDataBlocks
from tagProcessor import processTagImage

def createOrGetExpectedOutputForFileName(filePath,ActualOutput):
    result=""
    try:
        file = open(filePath, 'r')
        return file.read()
    except IOError:
        file = open(filePath, 'w')
        file.write(ActualOutput)
        file.close()
        return ActualOutput

def compareActualAndExpected(ActualOutput,ExpectedOutput,filename):
    if not ActualOutput==ExpectedOutput:
        print("\nUnitTest:("+filename+")")
        print("======Expected:=====\n"+ExpectedOutput)
        print("======Actual:=====\n"+ActualOutput)
        return False
    return True

def startUnitTesting(imageFolder="UnitTesting/Images/",resultFolder="UnitTesting/ExpectedResults/"):
    totalFails=0
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
           sdb=processTagImage(os.path.join(imageFolder, filename), .99)
           ActualOutput=getDescriptionFromDataBlocks("OCR",sdb)
           ExpectedOutput=createOrGetExpectedOutputForFileName(resultFolder+filename+".txt",ActualOutput)
        if not compareActualAndExpected(ActualOutput,ExpectedOutput,filename):
            totalFails+=1

    if not getSuggestions("Aalius brevipe")[0]=='Aalius brevipes':
        totalFails+=1
        print("Suggestion failed!")
    print("Total Fails: "+str(totalFails))
