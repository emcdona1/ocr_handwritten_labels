from enchant.checker import SpellChecker

from algorithmicMethods import getFilteredSuggestionList
from applyCorrection import get_personslist
from getWordsInformation import getDescriptionFromDataFrame

def detectWrongWords(dfs, minimumConfidence):
    rawText2 = getDescriptionFromDataFrame("OCR", dfs, 0)
    personslist = get_personslist(rawText2)
    ignorewords = personslist + ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    # using enchant.checker.SpellChecker, identify incorrect words
    engSpellCheck = SpellChecker("en_US")
    maskedTextStream = ""
    for index, w in dfs.iterrows():
        if (w['index'] > 0  and w['description'] not in ignorewords and not w['description'].isnumeric() and w['confidence'] < minimumConfidence):
            if not engSpellCheck.check(w['description']):
                w['suggestedDescription'] = getFilteredSuggestionList(w['charsAboveMinimumConfidence'],
                                                                      engSpellCheck.suggest(w['description']))
                w['isIncorrectWord'] = True
                w['color'] = "red"