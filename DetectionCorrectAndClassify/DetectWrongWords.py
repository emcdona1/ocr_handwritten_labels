from enchant.checker import SpellChecker

from DetectionCorrectAndClassify.ApplyCorrection import get_personslist
from Helper.GetWordsInformation import GetDescriptionFromDataBlocks
from Helper.WordAssignment import ApplySuggestions
from Helper.WordCategories import WordCategories

engSpellCheck = SpellChecker("en_US")

def DetectWrongWords(sdb,minimumConfidence):
    rawText2 = GetDescriptionFromDataBlocks("OCR", sdb, 0)
    personslist = get_personslist(rawText2)
    ignorewords = personslist + ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for db in sdb:
        for w in db:
            if (w['category'] == WordCategories.Unknown):  # known WordCategories are already detected.
                if (w['index'] > 0 and w['description'] not in ignorewords and not w['description'].isnumeric() and w[
                    'confidence'] < minimumConfidence):
                    ApplySuggestions(w, engSpellCheck.suggest(w['description']))
