
def SetStatusForWord(root, val):
    root.wordStatusLabel['text'] = val


def SetStatusForFileInfo(root,val):
    root.fileInfoLabel['text'] = val

def SetWordStatus(root, word):
    SetWordStatusByValue(root, word['description'], word['replacement'], word['category'])


def ClearWordStatus(root):
    root.oldWord = root.activeWord = {'index': 0}
    SetWordStatusByValue(root, '', '', '')


def SetWordStatusByValue(root, w, r, cat):
    SetStatusForWord(root, (" word       : {w}\n"
                     " replacement: {r}\n"
                     " category   : {cat}").format(w=w, r=r, cat=cat))

def SetFileInfo(root,importedPath,timeTaken=0.0):
    val=(" {p}").format(p=importedPath)
    if timeTaken>0.0:
        val+=f" ({timeTaken})"
    SetStatusForFileInfo(root,val)



