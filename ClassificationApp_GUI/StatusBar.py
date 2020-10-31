
def SetStatus(root, val):
    root.statusBar['text'] = val

def SetWordStatus(root, word):
    SetWordStatusByValue(root, word['description'], word['replacement'], word['category'])


def ClearWordStatus(root):
    root.oldWord = root.activeWord = {'index': 0}
    SetWordStatusByValue(root, '', '', '')


def SetWordStatusByValue(root, w, r, cat):
    SetStatus(root, (" word       : {w}\n"
                     " replacement: {r}\n"
                     " category   : {cat}\n").format(w=w, r=r, cat=cat))
