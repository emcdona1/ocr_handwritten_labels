
from SuggestEngine.Get_SuggestEngine import GetLocalSuggestEngine
from Helper.WordAssignment import ApplySuggestions
from Helper.WordCategories import WordCategories
suggestEngine=None
MONTH_FILEPATH='InputResources/Months.txt'

def DetectAndSuggestDates(sdb,filePath=MONTH_FILEPATH):
    #global suggestEngine
    #if suggestEngine is None:
    suggestEngine=GetLocalSuggestEngine(filePath, 'TRIE')
    found=DetectAndSuggestDateByBlocks(suggestEngine, sdb[-3:])
    return found

def DetectAndSuggestDateByBlocks(suggestEngine, sdb):
    for db in sdb:#check on first four block
        if(db[0]['category']==WordCategories.Unknown):
            data=" ".join([w['description']for w in db])
            monthPart = (''.join((filter(lambda i: i.isalpha(), data)))).lower()
            if (2<len(monthPart)<10 and len(monthPart)>2):
                suggestions = suggestEngine.suggest(monthPart)
                if (not(suggestions is None)) and len(suggestions)>0:#month is found
                    for w in db:#loop again to find exact month word
                        masked= "".join(['M' if c.isalpha() else c for c in w['description']])
                        while 'MM' in masked:
                            masked=masked.replace('MM','M')
                        w['category'] = WordCategories.Date
                        suggestions=[masked.replace('M',s) for s in suggestions]
                        ApplySuggestions(w, suggestions)
                    return True
    return False







#suggestEngine=GetLocalSuggestEngine("../InputResources/Months.txt", 'TRIE')
#print(suggestEngine.suggest("jun",0))
