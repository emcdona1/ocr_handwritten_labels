from tkinter import END


def SetStatusForWord(root, val,fgColor="black"):
    root.wordStatusLabel['text'] = val
    root.wordStatusLabel['foreground']=fgColor


def SetWordStatus(root, word):
    SetWordStatusByValue(root, word['description'], word['replacement'], word['category'])


def ClearWordStatus(root):
    root.oldWord = root.activeWord = {'index': 0}
    root.imagePath=""
    SetWordStatusByValue(root, '', '', '')


def SetWordStatusByValue(root, w, r, cat):
    if (root.total - root.processed) == 0:
        SetStatusForWord(root, (" word       : {w}\n"
                     " replacement: {r}\n"
                     " category   : {cat}").format(w=w, r=r, cat=cat))


