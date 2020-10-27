from Helper.WordAssignment import ApplyCategoryToWordBlock
from Helper.WordCategories import WordCategories

def DetectTitle(sdb):
    found=False
    for db in sdb:#check on first four block
        if(db[0]['category']==WordCategories.Unknown):
            data=("".join([w['description']for w in db]))[0:7]
            if (data.isupper()):
                ApplyCategoryToWordBlock(db, WordCategories.Title)
                found=True
    return found

'''last block with all capital or having collector on it should be collector information'''