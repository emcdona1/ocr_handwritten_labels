from Helper.WordAssignment import ApplyCategoryToWordBlock
from Helper.WordCategories import WordCategories


def DetectCollector(sdb):
    for db in sdb[-2:]:  # check on first four block
        if (db[0]['category'] == WordCategories.Unknown):
            data = " ".join([w['description'] for w in db])
            if (("COLLECTOR" in data.upper()) or data.isupper()) and len(data) > 10:
                ApplyCategoryToWordBlock(db, WordCategories.Collector)
                return True
    return False


'''last block with all capital or having collector on it should be collector information'''
