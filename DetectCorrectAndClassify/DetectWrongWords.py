import nltk
from enchant.checker import SpellChecker

from Helper.GetWordsInformation import GetNotCategorizedOCRData
from Helper.WordAssignment import ApplySuggestions
from Helper.WordCategories import WordCategories

engSpellCheck = SpellChecker("en_US")
def get_personslist(text):
    personslist = []
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'PERSON':
                personslist.insert(0, (chunk.leaves()[0][0]))
    return list(set(personslist))


def DetectWrongWords(sdb,minimumConfidence):
    rawText2 = GetNotCategorizedOCRData(sdb, True)
    personslist = get_personslist(rawText2)
    ignorewords = personslist + ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for db in sdb:
        if(db[0]['category']==WordCategories.Unknown):
            for w in db:
                if (w['index'] > 0 and w['category'] == WordCategories.Unknown and w['description'] not in ignorewords and w['description'].isalpha() and w[
                        'confidence'] < minimumConfidence):
                        ApplySuggestions(w, engSpellCheck.suggest(w['description']))
