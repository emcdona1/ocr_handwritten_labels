import re

from Detection_ScienteficName.Get_SuggestEngine import getLocalSuggestEngine
from applySuggestion import applySuggestion
from wordCategories import categories
suggestEngine=None
MONTH_FILEPATH="InputResources/Months.txt"

def DetectAndSuggestDates(sdb):
    global suggestEngine
    if suggestEngine is None:
        suggestEngine=getLocalSuggestEngine(MONTH_FILEPATH,'TRIE')
    found=detectAndSuggestDateByBlocks(suggestEngine, sdb)
    return found

def detectAndSuggestDateByBlocks(suggestEngine, sdb):
    for db in sdb[-3:]:#check on first four block
        if(db[0]['category']==categories.Unknown):
            data=" ".join([w['description']for w in db])

            monthPart = (''.join((filter(lambda i: i.isalpha(), data)))).lower()
            if (2<len(monthPart)<10):
                suggestions = suggestEngine.suggest(monthPart)
                if (not(suggestions is None)) and len(suggestions)>0:#month is found
                    for w in db:#loop again to find exact month word
                        masked= "".join(['M' if c.isalpha() else c for c in w['description']])
                        while 'MM' in masked:
                            masked=masked.replace('MM','M')
                        w['category'] = categories.Date
                        suggestions=[masked.replace('M',s) for s in suggestions]
                        applySuggestion(w,suggestions)
                    return True
    return False






