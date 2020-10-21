import enchant

from algorithmicMethods import getSequentialDataBlocks


class categories(object):
    plantDict = ""#enchant.PyPWL("InputResources/genusspecies_data.txt")
    Unknown = "Unknown"
    Location = "Location"
    ScientificName = "Scientific Name"
    Date = "Date"
    Description = "Description"
    RegistrationNumber = "Registration Number"
    Label = "Label(ignore)"
    Collector = "Collector"

from string import digits
categories=categories()

def initializeCategories(root):
    root.categories=[]
    #the order of the items will be used when displaying the classified data
    root.categories.append(categories.Description)
    root.categories.append(categories.ScientificName)
    root.categories.append(categories.Location)
    root.categories.append(categories.RegistrationNumber)
    root.categories.append(categories.Date)
    root.categories.append(categories.Collector)
    root.categories.append(categories.Label)
    root.categories.append(categories.Unknown)

months=["jan","january","feb","february","mar","march","apr","april",
            "may","jun","june","jul","july","aug","august","sep","sept","september",
            "october","oct","nov","november","dec","december"]

bad_chars = [';', ':', '!', "*",",","."," "]

remove_digits = str.maketrans('', '', digits)

def detectDescription(wordBlock,classified):
    for w in wordBlock:
        description = (''.join((filter(lambda i: i not in bad_chars, w['description'])))).lower()
        if w['category'] == categories.Unknown:
            if (description == "of"):
                applyCategoryToWordBlock(wordBlock, categories.Description)
                classified.append(categories.Description)
                return True;
    return False

def detectCollector(wordBlock,classified):
    for w in wordBlock:
        replacement = (''.join((filter(lambda i: i not in bad_chars, w['replacement'])))).lower()
        if w['category'] == categories.Unknown:
            if (replacement == "collector"):
                applyCategoryToWordBlock(wordBlock, categories.Collector)
                classified.append(categories.Collector)
                return True;
    return False

def detectDate(wordBlock,classified):
    for w in wordBlock:
        replacement=(''.join((filter(lambda i: i not in bad_chars, w['replacement'])))).lower()
        replacement = replacement.translate(remove_digits)

        if w['category']==categories.Unknown:
            if(replacement in months):
                applyCategoryToWordBlock(wordBlock,categories.Date)
                classified.append(categories.Date)
                return True;
    return False


def detectRegistrationNumber(wordBlock, classified):
    for w in wordBlock:
        replacement = (''.join((filter(lambda i: i not in bad_chars, w['replacement'])))).lower()
        replacement = replacement.translate(remove_digits)
        if w['category'] == categories.Unknown:
            if (replacement == "no"):
                applyCategoryToWordBlock(wordBlock, categories.RegistrationNumber)
                classified.append(categories.RegistrationNumber)
                return True;
    return False


def detectScienteficName(wordBlocks,classified):
    for wordBlock in wordBlocks:
        for w in wordBlock:
            if w['category'] == categories.Unknown:
                replacement = (''.join((filter(lambda i: i not in bad_chars, w['replacement'])))).lower()
                if isItScientificName(replacement):
                   applyCategoryToWordBlock(wordBlock, categories.ScientificName)
                   #joinWordBlock(wordBlock)
                   classified.append(categories.ScientificName)
                   return True;
    return False

def joinWordBlock(wordBlock):
    w=wordBlock[0]
    for n in wordBlock[1:]:
        n['index']=-1;
        w['description']=w['description']+" "+n['description']
        w['tupleVertices'][0]=(min(w['tupleVertices'][0][0],n['tupleVertices'][0][0]),min(w['tupleVertices'][0][1],n['tupleVertices'][0][1]))

        w['tupleVertices'][1] =(max(w['tupleVertices'][1][0],n['tupleVertices'][1][0]),min(w['tupleVertices'][1][1],n['tupleVertices'][1][1]))

        w['tupleVertices'][2] =(max(w['tupleVertices'][2][0],n['tupleVertices'][2][0]),max(w['tupleVertices'][2][1],n['tupleVertices'][2][1]))

        w['tupleVertices'][3] =(min(w['tupleVertices'][3][0],n['tupleVertices'][3][0]),max(w['tupleVertices'][3][1],n['tupleVertices'][3][1]))

        w['sp']=((w['tupleVertices'][0][0]+w['tupleVertices'][3][0])//2,(w['tupleVertices'][0][1]+w['tupleVertices'][3][1])//2)
        w['ep']=((w['tupleVertices'][1][0]+w['tupleVertices'][2][0])//2,(w['tupleVertices'][1][1]+w['tupleVertices'][2][1])//2)

        w['replacement']=w['replacement']+n['replacement']
    suggestScienteficWords(w)
def suggestScienteficWords(w):
    if categories.plantDict.check(w['description']):
        w['suggestedDescription'] = [w['description']]
        w['isIncorrectWord'] = False
        w['color'] = "green"
        return
    else:
        w['suggestedDescription'] = categories.plantDict.suggest(w['description'])
        w['isIncorrectWord'] = True
        w['color'] = "yellow"


def detectLocation(wordBlocks):
    classifyRemainingWordsAsLocation(wordBlocks)
    return True

def applyCategoryToWordBlock(wordBlock, category, labelIndex=-1):
   for w in wordBlock:
        if w['index']==labelIndex:
            w['category']=categories.Label
        else:
            w['category'] = category

def applyCategoryToWord(w,category):
    w['category']=category

def classifyRemainingWordsAsLocation(blocks):
    for wordBlock in blocks:
        for w in wordBlock:
            if w['category']==categories.Unknown:
                w['category'] = categories.Location
    pass


def autoClassifyWords(sdb):
    classified=[]
    for block in sdb:
        detectedCurrentBlock=False
        if not detectedCurrentBlock and categories.Description not in classified:
           detectedCurrentBlock= detectDescription(block,classified)
        if not detectedCurrentBlock and categories.Collector not in classified:
           detectedCurrentBlock=detectCollector(block,classified)
        if not detectedCurrentBlock and categories.Date not in classified:
            detectedCurrentBlock = detectDate(block,classified)
        if not detectedCurrentBlock and categories.RegistrationNumber not in classified:
            detectedCurrentBlock = detectRegistrationNumber(block,classified)

        if not detectedCurrentBlock and categories.ScientificName not in classified:
            detectScienteficName(sdb,classified)
    #location is seperate detection if everyting is detected.
    if set([categories.Description,categories.Collector,categories.Date,categories.RegistrationNumber,categories.ScientificName]).issubset( classified ):
        detectLocation(sdb)

def isItScientificName(text):
    return True
    pass
