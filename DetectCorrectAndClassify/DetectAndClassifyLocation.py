from Helper.WordCategories import WordCategories


def DetectLocation(notDetected, sdb):
    if notDetected > 0:  # if other items are missing we do not want to detect location alone
        return False;
    for db in sdb:
        if (db[0]['category'] == WordCategories.Unknown):
            for w in db:
                if (w['index'] > 0 and w['category'] == WordCategories.Unknown):
                    w['category'] = WordCategories.Location
    return True;
