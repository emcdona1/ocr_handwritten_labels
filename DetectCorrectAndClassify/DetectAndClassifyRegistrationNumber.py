from Helper.WordAssignment import ApplyCategoryToWordBlock
from Helper.WordCategories import WordCategories


def DetectRegistrationNumber(sdb):
    for db in sdb[-3:]:  # check on first four block
        if (db[0]['category'] == WordCategories.Unknown):
            data=" ".join([w['description']for w in db])
            label = (''.join((filter(lambda i: i.isalpha(), data)))).lower()
            digits="0"+(''.join((filter(lambda i: i.isdigit(), data))))
            if(label=="no" and int(digits)>0):
                ApplyCategoryToWordBlock(db, WordCategories.RegistrationNumber)
                return True

    for db in sdb[:3]:  # check on first four block
        if (db[0]['category'] == WordCategories.Unknown and len(db)<3):
            data=" ".join([w['description']for w in db])
            label = (''.join((filter(lambda i: i.isalpha(), data)))).lower()
            digits="0"+(''.join((filter(lambda i: i.isdigit(), data))))
            if(label=="no" or int(digits)>0):
                ApplyCategoryToWordBlock(db, WordCategories.RegistrationNumber)
                return True

    for db in sdb[3:-3]:
        if (db[0]['category'] == WordCategories.Unknown and len(db) < 3):
            data = " ".join([w['description'] for w in db])
            label = (''.join((filter(lambda i: i.isalpha(), data)))).lower()
            digits = "0" + (''.join((filter(lambda i: i.isdigit(), data))))
            if (label == "no" and int(digits) > 0):
                ApplyCategoryToWordBlock(db, WordCategories.RegistrationNumber)
                return True
    return False






