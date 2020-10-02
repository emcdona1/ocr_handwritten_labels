from PopUpInputBox import popupWindow
from globalCalls import setToDefaultWord
from statusBar import *


def MarkWordsInImage(root):
    for index, w in root.df.iterrows():
        if w['index'] > 0:
            drawBoxesInImage(root,root.scrollableImage.cnvs,w)

def drawBoxesInImage(root,canvas, word):
    word['canvas']=canvas
    word['polygon']=canvas.create_polygon(word['tupleVertices'], fill='',outline='',width=1, activeoutline=word['color'],activewidth=2)
    canvas.tag_bind(word.polygon, "<Button-1>", lambda x: word_button1(root,word))
    canvas.tag_bind(word.polygon, "<Enter>", lambda x: polygon_enter(root,word))
    canvas.tag_bind(word.polygon, "<Leave>", lambda x: polygon_leave(root))

    def word_button1(root,word):
        SetActiveWord(root,word)
        ProcessActiveWord(root,word)

    def polygon_enter(root,word):
        if root.activeWord['index']==0:
            SetWordStatus(root,word)

    def polygon_leave(root):
        if root.activeWord['index']==0:
            ClearWordStatus(root)

    if word['color']!="green":
        canvas.itemconfigure(word['polygon'], fill='',outline=word['color'], width=1)


def SetActiveWord(root,w):
    root.oldWord=root.activeWord
    root.activeWord=w

    if root.activeWord['index']>0:
        root.activeWord['canvas'].itemconfigure(root.activeWord['polygon'],fill='',
                                       outline='#00BFFF', width=2, activewidth=3, activeoutline='#00BFFF')
    if root.oldWord['index'] > 0:
        setToDefaultWord(root.oldWord)

    if root.oldWord['index']==root.activeWord['index']:
        root.oldWord = root.activeWord = {'index': 0}

def ProcessActiveWord(root,word):
        if root.activeWord['index'] >0 and word['index']==root.activeWord['index']:
             SetWordStatus(root,root.activeWord)
             getUserUpdatesForTheActiveWord(root, root.activeWord)


def getUserUpdatesForTheActiveWord(root, activeWord):
    root.popUp = popupWindow(root.master,root,activeWord,320,150)
    root.wait_window(root.popUp.top)
    if root.popUp.top:
        root.popUp.top.destroy()
    SetActiveWord(root,activeWord)
    SetWordStatus(root,activeWord)




