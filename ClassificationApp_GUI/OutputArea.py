from tkinter import *
from Helper.GetWordsInformation import GetDescriptionFromDataBlocks, GetClassifiedDataTuples, \
    GetClassifiedCategoriesInOrder


def UpdateOutput_old(root, **kw):
    ClearOutput(root)
    type = kw.pop('type', "corrected")
    useHint = kw.pop('useHint', 0)
    data = "######### Data #########\n" + \
           GetDescriptionFromDataBlocks(type, root.sdb, useHint)
    classifiedData = "\n\n######### Classified Information #########\n" + \
                     GetDescriptionFromDataBlocks('classified', root.sdb, 1, root.WordCategories)
    AppendToOutputArea(root, data)
    AppendToOutputArea(root, classifiedData)


def AppendToOutputArea(root, value):
    root.outputField.insert('insert', value)


def ClearOutput(root):
    root.outputField.delete('1.0', END)

def UpdateOutput(root,**kw):
    ClearOutput(root)
    classifiedData = GetClassifiedDataTuples(root.sdb)
    classifiedCategories = [c[0] for c in classifiedData]
    classifiedCategories = list(set(classifiedCategories))
    categories = GetClassifiedCategoriesInOrder(root.WordCategories, classifiedCategories)
    root.outputField.tag_config('label', foreground="green",font=("Courier", 14))
    root.outputField.tag_config('data', foreground="black",font=("Courier", 14))

    for c in categories:
        root.outputField.insert('end','{0: <19}: '.format(c),'label')
        for cd in classifiedData:
            if (cd[0] == c):
                root.outputField.insert('end', cd[1] + " ", 'data')
        root.outputField.insert('end',"\n", 'data')
    pass
    root.outputField.insert('end',"\n---------------------------------------------------------------\n", 'label')
    root.outputField.insert('end', '{0: <19}: '.format("Imported From: "), 'label')
    root.outputField.insert('end',root.imagePath+"\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Processing Time: "), 'label')
    root.outputField.insert('end', str(root.processingTime)+" Seconds.\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Imported Date: "), 'label')
    root.outputField.insert('end', str(root.importDate) + "\n", 'data')
