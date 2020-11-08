from tkinter import *
from Helper.GetWordsInformation import GetDescriptionFromDataBlocks, GetClassifiedDataTuples, \
    GetClassifiedCategoriesInOrder


def AppendToOutputArea(root, value):
    root.outputField.insert('insert', value)


def ClearOutput(root):
    root.outputField.delete('1.0', END)
    root.irn=0

def UpdateOutput(root,**kw):
    ClearOutput(root)
    classifiedData = GetClassifiedDataTuples(root.sdb)
    classifiedCategories = [c[0] for c in classifiedData]
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
        for cd in classifiedData:
            if (cd[0] == c):
                root.outputField.insert('end', cd[1] + " ", 'data')
        root.outputField.insert('end',"\n", 'data')
    pass
    try:
        if len(str(root.barCode))>0 and int(str(root.irn)+"0")>0:
            root.outputField.insert('end',GetLineText("Barcode Info"), 'line')
            root.outputField.insert('end', '{0: <19}: '.format("IRN "), 'label')
            root.outputField.insert('end',root.irn+"\n", 'data')
            root.outputField.insert('end', '{0: <19}: '.format("Taxonomy "), 'label')
            root.outputField.insert('end',root.taxonomy+"\n", 'data')
            root.outputField.insert('end', '{0: <19}: '.format("Collector "), 'label')
            root.outputField.insert('end',root.collector+"\n", 'data')
            for label,data in getTupleDetails(root.details):
                root.outputField.insert('end', '{0: <19}: '.format(label), 'label')
                root.outputField.insert('end',data+"\n", 'data')
    except Exception as error:
        print(f"{error} (Error Code:OA_001)")
        pass

    root.outputField.insert('end',GetLineText("Import Details"), 'line')
    root.outputField.insert('end', '{0: <19}: '.format("Imported From "), 'label')
    root.outputField.insert('end',root.imagePath+"\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Processing Time "), 'label')
    root.outputField.insert('end', str(root.processingTime)+" Seconds.\n", 'data')
    root.outputField.insert('end', '{0: <19}: '.format("Imported Date "), 'label')
    root.outputField.insert('end', str(root.importDate) + "\n", 'data')


def getTupleDetails(details):
    details=details.replace(':','')
    details=details.replace('  ',' ')
    details=details.replace('[\'','')
    details=details.replace('\']','')
    details=details.replace('\', \'','||')
    details=details.replace('[\"','')
    details=details.replace('\"]','')
    details=details.replace('\", \"','||')
    details=details.replace('\', \"','||')
    details=details.replace('\", \'','||')
    details=details.replace(' ||','||')
    details=details.replace('|| ','')
    details=details.split('||')
    tuples=[(i,k)for i,k in zip(details[0::2], details[1::2])]
    return tuples

def GetLineText(text,spacer=" * ",length=50):
    return (f"{text:^{length}}").replace('   ',spacer).replace('  ',' ')+"\n"


