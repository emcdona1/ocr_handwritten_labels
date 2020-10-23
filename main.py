from ScienteficNameService.sns import initializeDictionary
from classificationGUI import ClassificationApp, processTagImage
from unitTesting import startUnitTesting

if __name__ == '__main__':
    initializeDictionary("ScienteficNameService/test.txt")#genusspecies_data.txt")
    startUnitTesting()

    classificationApp = ClassificationApp()



