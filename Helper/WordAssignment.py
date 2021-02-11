from Helper.WordCategories import WordCategories


def ApplySuggestions(w, suggestions):
    if len(suggestions) > 0:
        w['isIncorrectWord'] = (not w['description'].lower() == suggestions[0].lower())
        if w['isIncorrectWord']:
            w['color'] = 'red'
            w['replacement'] = suggestions[0]
            w['suggestedDescription'] = list(set(suggestions))
    else:
        w['replacement'] = w['description']


def ApplyCategoryToWordBlock(wordBlock, category, labelIndex=-1):
    for w in wordBlock:
        if w['index'] == labelIndex:
            w['category'] = WordCategories.Label
        else:
            w['category'] = category
