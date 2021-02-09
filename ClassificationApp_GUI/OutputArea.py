import webbrowser
from tkinter import *


def UpdateOutput(root, **kw):
    root.imagePathToOpen = root.imagePath
    root.outputField.delete('1.0', END)
    root.importDetails['text']=f"Imported On: {root.importDate}\tProcessing Time: {root.processingTime} seconds."
    root.outputField.insert('end', '{0: <19}: '.format("Imported From "), 'label')
    root.outputField.insert('end', root.imagePath, 'filePath')
    root.outputField.insert('end', '\n')
    if len(root.barcode) > 0:
        root.outputField.insert('end', '{0: <19}: '.format('Bar Code'), 'label')
        root.outputField.insert('end', root.barcode, 'barcode')
        root.outputField.insert('end', '\n')
        for cb in root.classifiedDataForBarCode:
            if not ('barcode' in cb[0].lower()):
                root.outputField.insert('end', '{0: <19}: '.format(cb[0]), 'label')
                root.outputField.insert('end', cb[1], 'data')
                root.outputField.insert('end', '\n')

    root.outputField.insert('end', "______________________________________________________________________\n\n", 'line')
    for cd in root.classifiedData:
        root.outputField.insert('end', '{0: <19}: '.format(cd[0]), 'label')
        root.outputField.insert('end', cd[1], 'data')
        root.outputField.insert('end', '\n')
