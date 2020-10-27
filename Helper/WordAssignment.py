from Helper.WordCategories import WordCategories


def ApplySuggestions(w, suggestions):
    w['isIncorrectWord'] = (not w['description'].lower() == suggestions[0].lower())
    if w['isIncorrectWord']:
        w['color'] = "red"
        w['replacement'] = suggestions[0]
        w['suggestedDescription'] = list(set(suggestions))

def ApplyCategoryToWordBlock(wordBlock, category, labelIndex=-1):
   for w in wordBlock:
        if w['index']==labelIndex:
            w['category']=WordCategories.Label
        else:
            w['category'] = category