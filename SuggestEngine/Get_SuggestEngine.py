'''would initialize engine of any kind, and would contain method to invoke the respective method'''
from datetime import datetime

from SuggestEngine.SuggestEngine_Client import SuggestEngineClient
from SuggestEngine.SuggestEngine_Enchant import SuggestEngineWithEnchant
from SuggestEngine.SuggestEngine_Fuzzy import SuggestEngineWithFuzzy
from SuggestEngine.SuggestEngine_Trie import WordSearcherWithTrieNode


def GetLocalSuggestEngine(WORDS_FILE_PATH, ENGINE_NAME='TRIE'):
    suggestEngine = None
    print(datetime.now().strftime("%H:%M:%S") + " Initializing Suggest engine(" + ENGINE_NAME + ") for path: " + str(
        WORDS_FILE_PATH))
    if ENGINE_NAME == 'TRIE':
        suggestEngine = WordSearcherWithTrieNode(WORDS_FILE_PATH)
    if ENGINE_NAME == 'FUZZY':
        suggestEngine = SuggestEngineWithFuzzy(WORDS_FILE_PATH)
    if ENGINE_NAME == 'ENCHANT':
        suggestEngine = SuggestEngineWithEnchant(WORDS_FILE_PATH)
    print(datetime.now().strftime("%H:%M:%S") + " Suggest engine(" + ENGINE_NAME + ") initialized!")
    return suggestEngine


monthSuggestEngine = None


def GetMonthSuggestEngine(monthsFilePath='InputResources/Months.txt', ENGINE_NAME='TRIE'):
    global monthSuggestEngine
    if not monthSuggestEngine is None:
        return monthSuggestEngine
    else:
        monthSuggestEngine = GetLocalSuggestEngine(monthsFilePath, ENGINE_NAME)
        return monthSuggestEngine


def GetRunningServerEngineOrCreateLocalForSuggestion(root, engineTypeToUseWhenNotFound):
    se = None
    serverFound = False
    try:
        print("Checking if suggest server for SNS is available!")
        se = SuggestEngineClient(root)
        if (se.suggest('ServerTest') is None):
            print("suggest server (SNS) is not available!")
        else:
            print("SNS server is available, SNS server would be used to suggest Scientific words!")
            serverFound = True
    except:
        print("Unknown error! when using the SNS server!")
    if not serverFound:
        se = GetLocalSuggestEngine(root.plantDictionaryPath, engineTypeToUseWhenNotFound)
    return se
