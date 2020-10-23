
from datetime import datetime

from ScienteficNameService.similarityUsingEnchant import WordSearcherWithEnchant
from ScienteficNameService.similarityUsingTrieNode import WordSearcherWithTrieNode
from ScienteficNameService.similarityUsingFuzzy import WordSearcherWithFuzzy
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

        print(datetime.now().strftime("%H:%M:%S") + " Suggest engine("+ENGINE_NAME+") initialized!")

    def suggest(self, word):
        return self.suggestEngine.suggest(word)

def getSuggestions(data,suggestEngine):
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions for : " + data)
    suggestions = suggestEngine.suggest(data)
    print(datetime.now().strftime("%H:%M:%S") + " suggestions : " +str(suggestions))
    return suggestions



def startLocalTest():
    filePath="genusspecies_data.txt"
    se1= SuggestEngine(filePath,'FUZZY')
    se2= SuggestEngine(filePath,'ENCHANT')
    se3 = SuggestEngine(filePath, 'TRIE')

    word='zygopetalum wailesianum'
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(FUZZY) for : " + word)
    se1.suggest(word)
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(ENCHANT) for : " + word)
    se2.suggest(word)
    print(datetime.now().strftime("%H:%M:%S") + " getting suggestions(TRIE) for : " + word)
    se3.suggest(word)
    print(datetime.now().strftime("%H:%M:%S") + " Complete! ")

#startLocalTest()



