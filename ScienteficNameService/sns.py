from datetime import datetime
import enchant

plantDict = None
snFilePath = "ScienteficNameService/test.txt"


def initializeDictionary(filePath=snFilePath):
    global plantDict
    print(datetime.now().strftime("%H:%M:%S") + " Initializing dictionary from path: " + filePath)
    plantDict = enchant.PyPWL(filePath)
    print(datetime.now().strftime("%H:%M:%S") + " Dictionary initialized!")


def getSuggestions(data):
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions for : " + data)
    suggestions = getSuggestionsFromDictionary(data,plantDict)
    print(datetime.now().strftime("%H:%M:%S") + " suggestions : " +str(suggestions))
    return suggestions

def getSuggestionsFromDictionary(data,dict=plantDict):
    return dict.suggest(data)



def startLocalTest():
    initializeDictionary("test.txt")
    for i in range(100):
        getSuggestions("Aalius assimillis")

#startLocalTest()



