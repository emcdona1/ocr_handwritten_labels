import re
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from Helper.word_categories import WordCategories


def get_classified_categories_in_order(main_categories, classified_categories):
    categories = []
    for c in main_categories:
        if c in classified_categories:
            categories.append(c)
    # add any user added WordCategories at the end
    for c in sorted(classified_categories):
        if c not in categories:
            categories.append(c)
    return categories
    pass


def get_description_from_data_blocks(type, sdb, hint=0, main_categories=None):
    if main_categories is None:
        main_categories = []
    text = ''
    if type == 'corrected':
        for db in sdb:
            for w in db:
                if w['index'] > 0:
                    if w['isIncorrectWord']:
                        if hint == 1:
                            text += "[" + w['description'] + ']->'
                        text += w['replacement'] + ' '
                    else:
                        text += w['description'] + ' '
            text += '\n'

    if type == 'OCR':
        for db in sdb:
            for w in db:
                if w['index'] > 0:
                    text += w['description'] + ' '
            text += '\n'
    if type == 'classified':
        classified_data = get_classified_data_tuples(sdb)
        classified_categories = [c[0] for c in classified_data]
        classified_categories = list(set(classified_categories))
        categories = get_classified_categories_in_order(main_categories, classified_categories)
        for c in categories:
            if not c == 'Unknown' and 'ignore' not in c:
                text += c + ": "
                for cd in classified_data:
                    if cd[0] == c:
                        text += str(cd[1]) + ' '
                text += '\n'
    return replace_extra_space(text)


def get_uncategorized_ocr_data(sdb, masked_incorrect=True):
    stream_data = ""
    for db in sdb:
        for w in db:
            if w['index'] > 0 and w['category'] == WordCategories.Unknown:
                if not w['isIncorrectWord']:
                    stream_data += w['description'] + ' '
                else:
                    if masked_incorrect:
                        if len(w['suggestedDescription']) > 0:
                            stream_data += w['suggestedDescription'][0] + ' '
                        else:
                            stream_data += '[MASK] '
                    else:
                        stream_data += w['replacement'] + ' '
    return replace_extra_space(stream_data)


def get_classified_data_tuples(sdb):
    classified_data = []
    categories = []
    for db in sdb:
        for w in db:
            if w['index'] > 0:
                categories.append(w['category'])

    categories = list(set(categories))
    for c in categories:
        info = ''
        for db in sdb:
            for w in db:
                if w['index'] > 0 and w['category'] == c:
                    info = info + ' ' + w['replacement']
        classified_data.append((c, info))

    return classified_data


def replace_extra_space(text):
    rep = {' \'': '\'',
           ' .': '.',
           ' ,': ',',
           ' ?': '?',
           ' !': '!'}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text
