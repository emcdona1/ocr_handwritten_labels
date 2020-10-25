import enchant
import aspell
from enchant.checker import SpellChecker

from ScienteficNameService.DetectAndSuggestScienteficNames import detectAndSuggestScienteficWords
from applyCorrection import get_personslist
from getWordsInformation import getDescriptionFromDataBlocks

#plantDict = enchant.PyPWL("InputResources/genusspecies_data.txt")
#plantDict=enchant.request_pwl_dict("InputResources/genusspecies_data.txt")
from wordCategories import categories

engSpellCheck = SpellChecker("en_US")
'''
def checkAndSuggestScienteficName(w):
    if plantDict.check(w['description']):
        w['category']='ScientificName'
        w['suggestedDescription']=[w['description']]
    else:
        w['suggestedDescription'] = plantDict.suggest(w['description'])
    pass
'''
def checkAndSuggestEngWord(w):
    if not engSpellCheck.check(w['description']):
        w['suggestedDescription'] = engSpellCheck.suggest(w['description'])
    pass




def detectWrongWords(suggestEngine,sdb, minimumConfidence):
    if not detectAndSuggestScienteficWords(suggestEngine, sdb):
        print("Could not suggest any scientific words!")

    rawText2 = getDescriptionFromDataBlocks("OCR", sdb, 0)
    personslist = get_personslist(rawText2)
    ignorewords =personslist+ ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for db in sdb:
        for w in db:
            if (w['category']==categories.Unknown):#known categories are already detected.
                if(w['description'].isupper()):
                    ignorewords.append(w['description'])
                    w['category']=categories.Description
                if (w['index'] > 0  and w['description'] not in ignorewords and not w['description'].isnumeric() and w['confidence'] < minimumConfidence):
                    if(len(w['suggestedDescription'])==0):
                        checkAndSuggestEngWord(w)
                    if(len(w['suggestedDescription'])>0):
                        w['isIncorrectWord'] = True
                        w['color'] = "red"