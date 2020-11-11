import webbrowser
from tkinter import *


def UpdateOutput(root, **kw):
    root.imagePathToOpen = root.imagePath
    root.outputField.delete('1.0', END)
    root.outputField.insert('end', '{0: <19}: '.format("Imported From "), 'label')
    root.outputField.insert('end', root.imagePath, 'filePath')
    root.outputField.insert('end', '\n')
    if len(root.barCode) > 0:
        root.outputField.insert('end', '{0: <19}: '.format('Bar Code'), 'label')
        root.outputField.insert('end', root.barCode, 'barCode')
        root.outputField.insert('end', '\n')
        for cb in root.classifiedDataForBarCode:
            if not ('barcode' in cb[0].lower()):
                root.outputField.insert('end', '{0: <19}: '.format(cb[0]), 'label')
                root.outputField.insert('end', cb[1], 'data')
                root.outputField.insert('end', '\n')

    root.outputField.insert('end', "______________________________________________________________________\n\n", 'line')
    root.outputField.insert('end', '{0: <19}: '.format("Imported Date "), 'label')
    root.outputField.insert('end', str(root.importDate), 'data')
    root.outputField.insert('end', '\n')
    root.outputField.insert('end', '{0: <19}: '.format("Processing Time "), 'label')
    root.outputField.insert('end', str(root.processingTime) + " Seconds.", 'data')
    root.outputField.insert('end', '\n')

    root.outputField.insert('end', "______________________________________________________________________\n\n", 'line')
    for cd in root.classifiedData:
        root.outputField.insert('end', '{0: <19}: '.format(cd[0]), 'label')
        root.outputField.insert('end', cd[1], 'data')
        root.outputField.insert('end', '\n')
