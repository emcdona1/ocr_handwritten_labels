class WordCategories(object):
    plantDict = ""#enchant.PyPWL("InputResources/genusspecies_data.txt")
    Unknown = "Unknown"
    Location = "Location"
    ScientificName = "Scientific Name"
    Date = "Date"
    Title = "Title"
    RegistrationNumber = "Registration Number"
    Label = "Label(ignore)"
    Collector = "Collector"

from string import digits
categories=WordCategories()

def initializeCategories(root):
    root.WordCategories=[]
    #the order of the items will be used when displaying the classified data
    root.WordCategories.append(WordCategories.Title)
    root.WordCategories.append(WordCategories.ScientificName)
    root.WordCategories.append(WordCategories.Location)
    root.WordCategories.append(WordCategories.RegistrationNumber)
    root.WordCategories.append(WordCategories.Date)
    root.WordCategories.append(WordCategories.Collector)
    root.WordCategories.append(WordCategories.Label)
    root.WordCategories.append(WordCategories.Unknown)