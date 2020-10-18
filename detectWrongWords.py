
from enchant.checker import SpellChecker

from applyCorrection import get_personslist
from getWordsInformation import getDescriptionFromDataBlocks

#plantCheck = enchant.request_pwl_dict("InputResources/genusspecies_data.txt")


def detectWrongWords(sdb, minimumConfidence):
    engSpellCheck = SpellChecker("en_US")
    rawText2 = getDescriptionFromDataBlocks("OCR", sdb, 0)
    personslist = get_personslist(rawText2)
    ignorewords =personslist+ ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for db in sdb:
        for w in db:
            if (w['index'] > 0  and w['description'] not in ignorewords and not w['description'].isnumeric() and w['confidence'] < minimumConfidence):
               if not engSpellCheck.check(w['description']):
                    w['suggestedDescription'] = engSpellCheck.suggest(w['description'])
                    w['isIncorrectWord'] = True
                    w['color'] = "red"


