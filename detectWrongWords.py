import enchant
import aspell
from enchant.checker import SpellChecker

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

def setSuggestedDescriptionCategory(w,sd,c):
    w['replacement'] = sd[0]
    w['suggestedDescription'] = list(set(sd))
    w['category'] = c
    w['isIncorrectWord']= (not w['replacement']==w['description'])
    if w['isIncorrectWord']:
        w['color']="red"


def detectWrongWords(root,sdb, minimumConfidence):

    rawText2 = getDescriptionFromDataBlocks("OCR", sdb, 0)
    personslist = get_personslist(rawText2)
    ignorewords =personslist+ ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    foundScientefic=False
    lastWord={'index': -1}
    for db in sdb:
        for w in db:
            if not foundScientefic:
                if lastWord['index']>0:
                    suggestions=root.suggestEngine.suggest(lastWord['description']+" "+w['description'])
                    if len(suggestions)>0:
                        gData=[s.split(" ")[0] for s in suggestions]
                        sData = [s.split(" ")[1] for s in suggestions]
                        setSuggestedDescriptionCategory(lastWord,gData,categories.ScientificName)
                        setSuggestedDescriptionCategory(w, sData, categories.ScientificName)
                        foundScientefic = True
                        continue;
                if not foundScientefic:
                    suggestions=root.suggestEngine.suggest(w['description'])
                    if len(suggestions)>0:
                        w['suggestedDescription']=suggestions
                        w['replacement']=suggestions[0]
                        foundScientefic=True
                        continue;
                lastWord=w

            if(w['description'].isupper()):
                ignorewords.append(w['description'])
                w['category']=categories.Description
            if (w['index'] > 0  and w['description'] not in ignorewords and not w['description'].isnumeric() and w['confidence'] < minimumConfidence):
                #checkAndSuggestScienteficName2(w)
                if(len(w['suggestedDescription'])==0):
                    checkAndSuggestEngWord(w)
                if(len(w['suggestedDescription'])>0):
                    w['isIncorrectWord'] = True
                    w['color'] = "red"