from tkinter import *

def CreateStatusBar(root):
    root.statusBar = Label(root.hoverStatusFrame, text="", background="light gray", justify="left", bd=1, anchor="nw",
                      width=root.windowWidth-4,
                      height=3,
                      font=("Courier", 16))
    root.statusBar.pack()

def SetStatus(root,val):
    root.statusBar['text']=val

def SetWordStatus(root,word):
    SetWordStatusByValue(root,word['description'],str(word['confidence']),word['replacement'])

def ClearWordStatus(root):
   root.oldWord = root.activeWord = {'index': 0}
   SetWordStatusByValue(root,'','','')

def SetWordStatusByValue(root,w,c,r):
    SetStatus(root,(" word       : {w}\n"
               " confidence : {c} \n"
               " replacement: {r}\n").format(w=w, c=c, r=r))




