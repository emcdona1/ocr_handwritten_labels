import os
from datetime import datetime

from Helper.get_words_information import get_description_from_data_blocks
from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine
from SuggestEngine.SuggestEngine_Client import SuggestEngineClient


def CreateOrGetExpectedOutputForFileName(filePath, ActualOutput):
    result = ""
    try:
        file = open(filePath, 'r')
        return file.read()
    except IOError:
        file = open(filePath, 'w')
        file.write(ActualOutput)
        file.close()
        return ActualOutput


def CompareActualAndExpected(ActualOutput, ExpectedOutput, filename):
    if not ActualOutput == ExpectedOutput:
        print("\nUnitTest:(" + filename + ")")
        print("======Expected:=====\n" + ExpectedOutput)
        print("======Actual:=====\n" + ActualOutput)
        return False
    return True




def SuggestEngineTest(filePath):
    se1 = GetLocalSuggestEngine(filePath, 'FUZZY')
    se2 = GetLocalSuggestEngine(filePath, 'ENCHANT')
    se3 = GetLocalSuggestEngine(filePath, 'TRIE')
    se4 = SuggestEngineClient()

    word = 'zygopetalum wailesianum'
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(FUZZY) for : " + word)
    print(se1.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(ENCHANT) for : " + word)
    print(se2.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(TRIE) for : " + word)
    print(se3.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions using SNS TCP Server! ")
    print(se4.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " Complete! ")
