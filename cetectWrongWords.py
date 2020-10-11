from enchant.checker import SpellChecker

from algorithmicMethods import getFilteredSuggestionList
from applyCorrection import get_personslist
from getWordsInformation import GetDescriptionFromDataFrame

def DetectWrongWords(dfs,minimumConfidence):
    rawText2 = GetDescriptionFromDataFrame("OCR", dfs, 0)
    personslist = get_personslist(rawText2)
    ignorewords = personslist + ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    # using enchant.checker.SpellChecker, identify incorrect words
    d = SpellChecker("en_US")
    maskedTextStream = ""
    for index, w in dfs.iterrows():
        if (w['index'] > 0 and not d.check(w['description'])
                and w['description'] not in ignorewords
                and not w['description'].isnumeric()
                and w['confidence'] < minimumConfidence
        ):
            w['suggestedDescription'] = getFilteredSuggestionList(w['charsAboveMinimumConfidence'],
                                                                  d.suggest(w['description']))
            w['isIncorrectWord'] = True
            w['color'] = "red"
        if w['index'] > 0:
            w['replacement'] = w['description']  # default value would be replaced later if needed
