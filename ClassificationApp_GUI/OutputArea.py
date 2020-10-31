from tkinter import *
from tkinter.scrolledtext import ScrolledText

from Helper.GetWordsInformation import GetDescriptionFromDataBlocks





def UpdateOutput(root, **kw):
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
