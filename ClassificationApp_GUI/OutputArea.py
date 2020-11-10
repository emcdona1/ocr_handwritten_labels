from tkinter import *
from Helper.GetWordsInformation import GetDescriptionFromDataBlocks, GetClassifiedDataTuples, \
    GetClassifiedCategoriesInOrder


def AppendToOutputArea(root, value):
    root.outputField.insert('insert', value)

def UpdateOutput(root,**kw):
    root.outputField.delete('1.0', END)
    classifiedCategories = [c[0] for c in root.classifiedData]
    classifiedCategories = list(set(classifiedCategories))
    categories = GetClassifiedCategoriesInOrder(root.WordCategories, classifiedCategories)
    root.outputField.insert('end',GetLineText("Classifier Data"), 'line')
    root.outputField.tag_config('label', foreground="green",font=("Courier", 14))
    root.outputField.tag_config('data', foreground="black",font=("Courier", 14))
    root.outputField.tag_config('line', foreground="gray50",font=("Courier", 14))
    root.outputField.insert('end','{0: <19}: '.format('Bar Code'),'label')
    root.outputField.insert('end',root.barCode+'\n','data')
    for c in categories:
        root.outputField.insert('end','{0: <19}: '.format(c),'label')
        for cd in root.classifiedData:
            if (cd[0] == c):
                root.outputField.insert('end', cd[1] + " ", 'data')
        root.outputField.insert('end',"\n", 'data')
    pass
    if len(str(root.barCode))>0:
        root.outputField.insert('end',GetLineText("Barcode Info"), 'line')
        for cb in root.classifiedDataForBarCode:
            root.outputField.insert('end', '{0: <19}: '.format(cb[0]),'label')
            root.outputField.insert('end', cb[1] + "\n", 'data')

    root.outputField.insert('end',GetLineText("Import Details"), 'line')
    root.outputField.insert('end', '{0: <19}: '.format("Imported From "), 'label')
    root.outputField.insert('end',root.imagePath+"\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Processing Time "), 'label')
    root.outputField.insert('end', str(root.processingTime)+" Seconds.\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Imported Date "), 'label')
    root.outputField.insert('end', str(root.importDate) + "\n", 'data')

def GetLineText(text,spacer=" * ",length=50):
    return (f"{text:^{length}}").replace('   ',spacer).replace('  ',' ')+"\n"


