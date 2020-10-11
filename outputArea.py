from tkinter import *
from tkinter.scrolledtext import ScrolledText

from getWordsInformation import GetDescriptionFromDataFrame


def CreateOutputFrameToDisplayInfo(root,outputFrame):
    outputFrame.configure(padx=10,pady=10)
    root.outputField = ScrolledText(outputFrame,height=15, width=75)

    root.outputField.configure(font=("Courier", 16),padx=10,pady=10)
    root.outputField.pack(anchor="nw",expand=1)
    #textfield.grid(row=0,column=0,sticky="nsew")


def updateOutput(root,**kw):
    type=kw.pop('type',"corrected")
    useHint=kw.pop('useHint',0)
    afterUpdate=GetDescriptionFromDataFrame(type,root.df,useHint)
    displayData=afterUpdate+"\n\n######### Classified Information #########\n\n"+\
                GetDescriptionFromDataFrame('classified', root.df, 1)
    setOutput(root,displayData)

def setOutput(root,value):
    #textfield.configure(state='normal')
    root.outputField.delete('1.0', END)
    root.outputField.insert('insert', value)

    #textfield.configure(state='disabled')


