import os
from datetime import datetime

from ScienteficNameService.SuggestEngine_Client import SuggestEngineClient
from ScienteficNameService.Get_SuggestEngine import getLocalSuggestEngine
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
    suggestEngineTest("UnitTesting/Resources/test.txt")
    suggestEngine = getLocalSuggestEngine("InputResources/genusspecies_data.txt", "TRIE")
    totalFails=0
    if 1==1:
        for filename in sorted(os.listdir(imageFolder)):
            if filename.endswith(".jpg"):
               sdb=processTagImage(suggestEngine,os.path.join(imageFolder, filename), .99)
               ActualOutput=getDescriptionFromDataBlocks("OCR",sdb)
               ExpectedOutput=createOrGetExpectedOutputForFileName(resultFolder+filename+".txt",ActualOutput)
            if not compareActualAndExpected(ActualOutput,ExpectedOutput,filename):
                totalFails+=1

def suggestEngineTest(filePath):
    se1= getLocalSuggestEngine(filePath,'FUZZY')
    se2= getLocalSuggestEngine(filePath,'ENCHANT')
    se3 = getLocalSuggestEngine(filePath, 'TRIE')
    se4 = SuggestEngineClient()

    word='zygopetalum wailesianum'
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(FUZZY) for : " + word)
    print(se1.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(ENCHANT) for : " + word)
    print(se2.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(TRIE) for : " + word)
    print(se3.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions using SNS TCP Server! ")
    print(se4.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " Complete! ")




