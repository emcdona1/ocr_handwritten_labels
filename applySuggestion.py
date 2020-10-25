def applySuggestion(w,suggestions):
    w['isIncorrectWord'] = (not w['description'].lower() == suggestions[0].lower())
    if w['isIncorrectWord']:
        w['color'] = "red"
        w['replacement'] = suggestions[0]
        w['suggestedDescription'] = suggestions

