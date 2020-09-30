from tkinter import *
from tkinter.scrolledtext import ScrolledText

label=""
textfield=""


def CreateOutputFrameToDisplayInfo(outputFrame,windowWidth):
    global textfield
    outputFrame.configure(padx=10,pady=10)
    textfield = ScrolledText(outputFrame,height=15, width=75)

    textfield.configure(font=("Courier", 16),padx=10,pady=10)
    textfield.pack(anchor="nw",expand=1)
    #textfield.grid(row=0,column=0,sticky="nsew")

def setOutput(value):
    global textfield
    #textfield.configure(state='normal')
    textfield.delete('1.0', END)
    textfield.insert('insert', value)
    #textfield.configure(state='disabled')


