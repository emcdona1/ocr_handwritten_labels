class categories(object):
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
    root.categories.append(categories.Unknown)
    root.categories.append(categories.Location)
    root.categories.append(categories.ScientificName)
    root.categories.append(categories.Date)
    root.categories.append(categories.Description)
    root.categories.append(categories.RegistrationNumber)
    root.categories.append(categories.Label)
    root.categories.append(categories.Collector)



from getWordsInformation import getWordsByLinesAndBlocks

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
                break;
    pass

def detectCollector(wordBlock,classified):
    for w in wordBlock:
        description = (''.join((filter(lambda i: i not in bad_chars, w['description'])))).lower()
        if w['category'] == categories.Unknown:
            if (description == "collector"):
                applyCategoryToWordBlock(wordBlock, categories.Collector)
                classified.append(categories.Collector)
                break;
    pass


def detectDate(wordBlock,classified):
    for w in wordBlock:
        description=(''.join((filter(lambda i: i not in bad_chars, w['description'])))).lower()
        description = description.translate(remove_digits)

        if w['category']==categories.Unknown:
            if(description in months):
                applyCategoryToWordBlock(wordBlock,categories.Date)
                classified.append(categories.Date)
                break;


def detectRegistrationNumber(wordBlock, classified):
    for w in wordBlock:
        description = (''.join((filter(lambda i: i not in bad_chars, w['description'])))).lower()
        description = description.translate(remove_digits)
        if w['category'] == categories.Unknown:
            if (description == "no"):
                applyCategoryToWordBlock(wordBlock, categories.RegistrationNumber)
                classified.append(categories.RegistrationNumber)
                break;
    pass


def detectScienteficName(wordBlock,classified):
    print("To Do:\n1. Load latin words data \n2.run 1 gram model to find if given words are latin")
    text=""
    for w in wordBlock:
        if w['category'] != categories.Unknown:
            break;
        description = (''.join((filter(lambda i: i not in bad_chars, w['description'])))).lower()
        text += description + " ";

    if isItScientificName(text) and len(text)>0:
       applyCategoryToWordBlock(wordBlock, categories.ScientificName)
       classified.append(categories.ScientificName)

def detectLocation(wordBlock):
    pass

def applyCategoryToWordBlock(wordBlock, category, labelIndex=-1):
   for w in wordBlock:
        if w['index']==labelIndex:
            w['category']=categories.Label
        else:
            w['category'] = category


def classifyRemainingWordsAsLocation(blocks):
    for wordBlock in blocks:
        for w in wordBlock:
            if w['category']==categories.Unknown:
                w['category'] = categories.Location
    pass


def autoClassifyWords(dfs):
    print("wip: autoClassifyWords in wordCategories.py")
    blocks=getWordsByLinesAndBlocks(dfs)
    classified=[]
    for block in blocks:
        if categories.Description not in classified:
            detectDescription(block,classified)
        if categories.Collector not in classified:
            detectCollector(block,classified)
        if categories.Date not in classified:
            detectDate(block,classified)
        if categories.RegistrationNumber not in classified:
            detectRegistrationNumber(block,classified)

    for block in blocks:
        if categories.ScientificName not in classified:
            detectScienteficName(block,classified)
    #if only location is remained to validate, classify all remaining items as location
    if set([categories.Description,categories.Collector,categories.Date,categories.RegistrationNumber,categories.ScientificName]).issubset( classified ):
        classifyRemainingWordsAsLocation(blocks)

def isItScientificName(text):
    return True
    pass
