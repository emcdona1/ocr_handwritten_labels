import os
from datetime import datetime

from SuggestEngine.SuggestEngine_Client import SuggestEngineClient
from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine
from Helper.GetWordsInformation import GetDescriptionFromDataBlocks
from ImageProcessor.TagProcessorReadDetectCorrectClassifySave import processTagImage

def CreateOrGetExpectedOutputForFileName(filePath, ActualOutput):
    result=""
    try:
        file = open(filePath, 'r')
        return file.read()
    except IOError:
        file = open(filePath, 'w')
        file.write(ActualOutput)
        file.close()
        return ActualOutput

def CompareActualAndExpected(ActualOutput, ExpectedOutput, filename):
    if not ActualOutput==ExpectedOutput:
        print("\nUnitTest:("+filename+")")
        print("======Expected:=====\n"+ExpectedOutput)
        print("======Actual:=====\n"+ActualOutput)
        return False
    return True

def StartUnitTesting(imageFolder="UnitTesting/Images/", resultFolder="UnitTesting/ExpectedResults/"):
    SuggestEngineTest("UnitTesting/Resources/test.txt")
    suggestEngine = GetLocalSuggestEngine("InputResources/genusspecies_data.txt", "TRIE")
    MONTH_FILEPATH = 'InputResources/Months.txt'
    monthSuggestEngine = GetLocalSuggestEngine(MONTH_FILEPATH, 'TRIE')
    totalFails=0
    if 1==1:
        for filename in sorted(os.listdir(imageFolder)):
            if filename.endswith(".jpg"):
               sdb=processTagImage(suggestEngine,os.path.join(imageFolder, filename), .99)
               ActualOutput=GetDescriptionFromDataBlocks("OCR", sdb)
               ExpectedOutput=CreateOrGetExpectedOutputForFileName(resultFolder + filename + ".txt", ActualOutput)
            if not CompareActualAndExpected(ActualOutput, ExpectedOutput, filename):
                totalFails+=1

def SuggestEngineTest(filePath):
    se1= GetLocalSuggestEngine(filePath, 'FUZZY')
    se2= GetLocalSuggestEngine(filePath, 'ENCHANT')
    se3 = GetLocalSuggestEngine(filePath, 'TRIE')
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






