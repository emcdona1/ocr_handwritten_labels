from tkinter import *
global statusBar

def CreateStatusBar(statusFrame,windowWidth):
    global statusBar
    statusBar = Label(statusFrame, text="", background="light gray", justify="left", bd=1, anchor="nw",
                      width=windowWidth-4,
                      height=3,
                      font=("Courier", 16))
    statusBar.pack()


def SetStatus(val):
    statusBar['text']=val

def SetWordStatus(word):
    SetWordStatusByValue(word['description'],str(word['confidence']),word['replacement'])

def ClearWordStatus():
   SetWordStatusByValue('','','')

def SetWordStatusByValue(w,c,r):
    SetStatus((" word       : {w}\n"
               " confidence : {c} \n"
               " replacement: {r}\n").format(w=w, c=c, r=r))




