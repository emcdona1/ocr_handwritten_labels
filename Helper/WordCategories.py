class WordCategories(object):
    plantDict = ""
    Unknown = "Unknown"
    ScientificName = "Scientific Name"
    Date = "Date"
    Title = "Title"
    RegistrationNumber = "Registration Number"
    Label = "Label(ignore)"
    Collector = "Collector"
    Location = "Location"


categories = WordCategories()


def GetWordCategories():
    wc = []
    # the order of the items will be used when displaying the classified data
    wc.append(WordCategories.Title)
    wc.append(WordCategories.ScientificName)
    wc.append(WordCategories.RegistrationNumber)
    wc.append(WordCategories.Date)
    wc.append(WordCategories.Collector)
    wc.append(WordCategories.Label)
    wc.append(WordCategories.Unknown)
    wc.append(WordCategories.Location)
    return wc
