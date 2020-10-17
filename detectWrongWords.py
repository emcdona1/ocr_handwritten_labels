
from enchant.checker import SpellChecker

from applyCorrection import get_personslist
from getWordsInformation import getDescriptionFromDataFrame

#plantCheck = enchant.request_pwl_dict("InputResources/genusspecies_data.txt")


def detectWrongWords(dfs, minimumConfidence):
    engSpellCheck = SpellChecker("en_US")
    rawText2 = getDescriptionFromDataFrame("OCR", dfs, 0)
    personslist = get_personslist(rawText2)
    ignorewords =personslist+ ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for index, w in dfs.iterrows():
        if (w['index'] > 0  and w['description'] not in ignorewords and not w['description'].isnumeric() and w['confidence'] < minimumConfidence):
           if not engSpellCheck.check(w['description']):
                w['suggestedDescription'] = engSpellCheck.suggest(w['description'])
                w['isIncorrectWord'] = True
                w['color'] = "red"


