from tkinter import *

def createStatusBar(root):
    root.statusBar = Label(root.hoverStatusFrame, text="", background="light gray", justify="left", bd=1, anchor="nw",
                      width=root.windowWidth-4,
                      height=4,
                      font=("Courier", 16))
    root.statusBar.pack()

def setStatus(root, val):
    root.statusBar['text']=val

def setWordStatus(root, word):
    setWordStatusByValue(root, word['description'], str(word['confidence']), word['replacement'], word['category'])

def clearWordStatus(root):
   root.oldWord = root.activeWord = {'index': 0}
   setWordStatusByValue(root, '', '', '', '')

def setWordStatusByValue(root, w, c, r, cat):
    setStatus(root, (" word       : {w}\n"
               " confidence : {c} \n"
               " replacement: {r}\n"
               " category   : {cat}\n").format(w=w, c=c, r=r,cat=cat))




