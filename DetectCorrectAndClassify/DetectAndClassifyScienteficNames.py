from Helper.WordAssignment import ApplySuggestions
from Helper.WordCategories import WordCategories


def DetectAndSuggestScienteficWords(suggestEngine, sdb):
    found = DetectSuggestScienteficWordsByBlock(suggestEngine, sdb)
    if not found:
        found = DetectSuggestScienteficWordsByFirstWordInBlock(suggestEngine, sdb)
    if not found:
        found = DetectSuggestScienteficWordsByRandomWordsCombination(suggestEngine,
                                                                     sdb)  # hopefully it does not come to this level (WIP)
    # implement more algorithm to detect scientefic word based upon their position.
    return found


def DetectSuggestScienteficWordsByBlock(suggestEngine, sdb):
    for db in sdb[:4]:  # check on first four block
        if (db[0]['category'] == WordCategories.Unknown):
            data = " ".join([w['description'] for w in db[:2]])
            suggestions = suggestEngine.suggest(data)
            if (not (suggestions is None)) and len(suggestions) > 0:
                ApplySuggestionToWordBlocks(suggestions, db[:2])
                return True
    return False


def DetectSuggestScienteficWordsByFirstWordInBlock(suggestEngine, sdb):
    for db in sdb[:4]:  # check on first four block
        if (db[0]['category'] == WordCategories.Unknown):
            suggestions = suggestEngine.suggest(db[0]['description'])
            if (not (suggestions is None)) and len(suggestions) > 0:
                ApplySuggestionToWordBlocks(suggestions, [db[0]])
                return True
    return False


def DetectSuggestScienteficWordsByRandomWordsCombination(suggestEngine, sdb):
    wordList = [w for w in [db for db in sdb[:4]]]

    for w1 in wordList:
        for w2 in wordList:
            if (w1[0]['index'] != w2[0]['index']) and min(len(w1[0]['description']), len(w2[0]['description'])) > 2 \
                    and (w1[0]['description'] == WordCategories.Unknown) and (
                    w1[0]['description'] == WordCategories.Unknown):
                suggestions = suggestEngine.suggest(w1[0]['description'] + " " + w2[0]['description'])
                if (not (suggestions is None)) and len(suggestions) > 0:
                    ApplySuggestionToWordBlocks(suggestions, [w1[0], w2[0]])
                    return True
    return False


def ApplySuggestionToWordBlocks(suggestions, words):
    if (len(words) == 2):
        gData = [s.split(" ")[0] for s in suggestions]
        sData = [s.split(" ")[1] for s in suggestions]
        AddSuggestedDescriptionAndCategory(words[0], gData, WordCategories.ScientificName)
        AddSuggestedDescriptionAndCategory(words[1], sData, WordCategories.ScientificName)
    if (len(words) == 1):
        AddSuggestedDescriptionAndCategory(words[0], suggestions, WordCategories.ScientificName)


def AddSuggestedDescriptionAndCategory(w, sd, c):
    w['category'] = c
    ApplySuggestions(w, sd)
