from Helper.word_categories import WordCategories


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
