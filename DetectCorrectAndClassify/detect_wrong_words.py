import nltk
from enchant.checker import SpellChecker
from Helper.get_words_information import get_uncategorized_ocr_data
from Helper.word_assignment import apply_suggestions
from Helper.word_categories import WordCategories

engSpellCheck = SpellChecker('en_US')


def get_persons_list(text):
    persons_list = []
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'PERSON':
                persons_list.insert(0, (chunk.leaves()[0][0]))
    return list(set(persons_list))


def detect_wrong_words(sdb, min_confidence) -> None:
    """ Updates ImageProcessor.sdb list"""
    raw_text2 = get_uncategorized_ocr_data(sdb, True)
    persons_list = get_persons_list(raw_text2)
    ignore_words = persons_list + ["!", ",", ".", "\"", "?", '(', ')', '*', '\'', '\n']

    for db in sdb:
        if db[0]['category'] == WordCategories.Unknown:
            for w in db:
                if w['index'] > 0 and \
                        w['category'] == WordCategories.Unknown and \
                        w['description'] not in ignore_words and w['description'].isalpha() and \
                        w['confidence'] < min_confidence:
                    apply_suggestions(w, engSpellCheck.suggest(w['description']))
