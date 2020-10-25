from wordCategories import categories


def detectAndSuggestScienteficWords(suggestEngine, sdb):
    found=detectSuggestScienteficWordsByBlock(suggestEngine,sdb)
    if not found:
       found= detectSuggestScienteficWordsByFirstWordInBlock(suggestEngine,sdb)
    if not found:
        found=detectSuggestScienteficWordsByRandomWordsCombination(suggestEngine,sdb)#hopefully it does not come to this level (WIP)
    #implement more algorithm to detect scientefic word based upon their position.
    return found

def detectSuggestScienteficWordsByBlock(suggestEngine,sdb):
    for db in sdb[:4]:#check on first four block
        data=" ".join([w['description']for w in db[:2]])
        suggestions = suggestEngine.suggest(data)
        if (not(suggestions is None)) and len(suggestions)>0:
            applySuggestionToWordBlocks(suggestions,db[:2])
            return True
    return False

def detectSuggestScienteficWordsByFirstWordInBlock(suggestEngine,sdb):
    for db in sdb[:4]:#check on first four block
        suggestions = suggestEngine.suggest(db[0]['description'])
        if (not(suggestions is None)) and len(suggestions)>0:
            applySuggestionToWordBlocks(suggestions,[db[0]])
            return True
    return False

def detectSuggestScienteficWordsByRandomWordsCombination(suggestEngine, sdb):
    wordList=[w for w in [ db for db in sdb[:4]]]

    for w1 in wordList:
        for w2 in wordList:
            if(w1[0]['index']!=w2[0]['index']) and min(len(w1[0]['description']),len(w2[0]['description']))>2:
                suggestions = suggestEngine.suggest(w1[0]['description'] +" "+w2[0]['description'])
                if (not (suggestions is None)) and len(suggestions) > 0:
                    applySuggestionToWordBlocks(suggestions, [w1[0],w2[0]])
                    return True
    return False



def applySuggestionToWordBlocks(suggestions,words):
    if(len(words)==2):
        gData = [s.split(" ")[0] for s in suggestions]
        sData = [s.split(" ")[1] for s in suggestions]
        setSuggestedDescriptionCategory(words[0], gData, categories.ScientificName)
        setSuggestedDescriptionCategory(words[1], sData, categories.ScientificName)
    if(len(words)==1):
        setSuggestedDescriptionCategory(words[0], suggestions, categories.ScientificName)

def setSuggestedDescriptionCategory(w,sd,c):
    w['replacement'] = sd[0]
    w['suggestedDescription'] = list(set(sd))
    w['category'] = c
    w['isIncorrectWord']= (not w['replacement']==w['description'])
    if w['isIncorrectWord']:
        w['color']="red"






