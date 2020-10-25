'''would initialize engine of any kind, and would contain method to invoke the respective method'''
from datetime import datetime

from ScienteficNameService.similarityUsingEnchant import WordSearcherWithEnchant
from ScienteficNameService.similarityUsingTrieNode import WordSearcherWithTrieNode
from ScienteficNameService.similarityUsingFuzzy import WordSearcherWithFuzzy
from ScienteficNameService.similarityUsingTrieServer import WordSearcherWithTrieServer

"""
SNS: Scientefic Name Service
"""
class SuggestEngine:
    suggestEngine = None
    def __init__(self,WORDS_FILE_PATH,ENGINE_NAME='TRIE'):
        print(datetime.now().strftime("%H:%M:%S") + " Initializing Suggest engine("+ENGINE_NAME+") for path: " + WORDS_FILE_PATH)
        if ENGINE_NAME=='TRIE':
            self.suggestEngine = WordSearcherWithTrieNode(WORDS_FILE_PATH)

        if ENGINE_NAME=='FUZZY':
            self.suggestEngine = WordSearcherWithFuzzy(WORDS_FILE_PATH)

        if ENGINE_NAME=='ENCHANT':
            self.suggestEngine = WordSearcherWithEnchant(WORDS_FILE_PATH)

        if ENGINE_NAME=='TRIE_SERVER':
            self.suggestEngine=WordSearcherWithTrieServer()

        print(datetime.now().strftime("%H:%M:%S") + " Suggest engine("+ENGINE_NAME+") initialized!")

    def suggest(self, word):
        return self.suggestEngine.suggest(word)

def getSuggestions(data,suggestEngine):
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions for : " + data)
    suggestions = suggestEngine.suggest(data)
    print(datetime.now().strftime("%H:%M:%S") + " suggestions : " +str(suggestions))
    return suggestions

def startLocalTest():
    filePath= "../InputResources/genusspecies_data.txt"
    se1= SuggestEngine(filePath,'FUZZY')
    se2= SuggestEngine(filePath,'ENCHANT')
    se3 = SuggestEngine(filePath, 'TRIE')
    se4=  SuggestEngine(filePath,'TRIE_SERVER')

    word='zygopetalum wailesianum'
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(FUZZY) for : " + word)
    print(se1.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(ENCHANT) for : " + word)
    print(se2.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(TRIE) for : " + word)
    print(se3.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " Complete! ")
    print(se3.suggest(word))
    print(datetime.now().strftime("%H:%M:%S") + " Complete! ")

def getRunningServerEngineOrCreateLocalForSuggestion(plantDictionaryPath,engineTypeToUseWhenNotFound):
    se=SuggestEngine("",'TRIE_SERVER')
    try:
        print("Checking if suggest server for SNS is available!")
        if(se.suggest('') is None):
            print("suggest server (SNS) is not available!")
            print("Creating new SNS engine with the Engine Type of:",engineTypeToUseWhenNotFound)
            se=SuggestEngine(plantDictionaryPath,engineTypeToUseWhenNotFound)
    except:
        print("Unknown error! when creating suggest engine for Scientific Names! creating new  with the Engine Type of:",engineTypeToUseWhenNotFound)
        se = SuggestEngine(plantDictionaryPath, engineTypeToUseWhenNotFound)

    return se



#startLocalTest()



