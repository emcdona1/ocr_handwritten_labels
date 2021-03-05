import nltk
from enchant.checker import SpellChecker
from imageprocessor.get_words_information import get_uncategorized_ocr_data

engSpellCheck = SpellChecker('en_US')


def get_persons_list(text):
    persons_list = []
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'PERSON':
                persons_list.insert(0, (chunk.leaves()[0][0]))
    return list(set(persons_list))


class WordCategories(object):
    plantDict = ''
    Unknown = 'Unknown'
    ScientificName = 'Scientific Name'
    Date = 'Date'
    Title = 'Title'
    RegistrationNumber = 'Registration Number'
    Label = 'Label(ignore)'
    Collector = 'Collector'
    Location = 'Location'


categories = WordCategories()


def detect_wrong_words(sdb, min_confidence) -> None:
    """ Updates images_processor.sdb list"""
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


def apply_suggestions(w, suggestions):
    if len(suggestions) > 0:
        w['isIncorrectWord'] = (not w['description'].lower() == suggestions[0].lower())
        if w['isIncorrectWord']:
            w['color'] = 'red'
            w['replacement'] = suggestions[0]
            w['suggestedDescription'] = list(set(suggestions))
    else:
        w['replacement'] = w['description']


def apply_category_to_word_block(word_block, category, label_index=-1):
    for w in word_block:
        if w['index'] == label_index:
            w['category'] = WordCategories.Label
        else:
            w['category'] = category
