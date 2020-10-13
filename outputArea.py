from tkinter import *
from tkinter.scrolledtext import ScrolledText

from getWordsInformation import getDescriptionFromDataFrame


def createOutputFrameToDisplayInfo(root, outputFrame):
    outputFrame.configure(padx=10,pady=10)
    root.outputField = ScrolledText(outputFrame,height=15, width=75)

    root.outputField.configure(font=("Courier", 16),padx=10,pady=10)
    root.outputField.pack(anchor="nw",expand=1)
    #textfield.grid(row=0,column=0,sticky="nsew")


def updateOutput(root,**kw):
    clearOutput(root)
    type=kw.pop('type',"corrected")
    useHint=kw.pop('useHint',0)
    data="######### Data #########\n"+ \
                getDescriptionFromDataFrame(type, root.df, useHint)
    classifiedData= "\n\n######### Classified Information #########\n" + \
                 getDescriptionFromDataFrame('classified', root.df, 1,root.categories)
    appendToOutputArea(root, data)
    appendToOutputArea(root, classifiedData)

def appendToOutputArea(root, value):
    root.outputField.insert('insert', value)

def clearOutput(root):
    root.outputField.delete('1.0', END)


