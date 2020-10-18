from popUpInputBox import popupWindow
from statusBar import *
from wordOutline import updateWordOutline


def markWordsInImage(root):
    for db in root.sdb:
        for w in db:
            if w['index'] > 0:
                drawBoxesInImage(root,root.scrollableImage.cnvs,w)

def drawBoxesInImage(root,canvas, word):
    word['canvas']=canvas
    word['polygon']=canvas.create_polygon(word['tupleVertices'])
    canvas.create_line(word['sp'][0],word['sp'][1], word['ep'][0],word['ep'][1],dash=(4, 2))
    updateWordOutline(word)
    canvas.tag_bind(word.polygon, "<Button-1>", lambda x: word_button1(root,word))
    canvas.tag_bind(word.polygon, "<Enter>", lambda x: polygon_enter(root,word))
    canvas.tag_bind(word.polygon, "<Leave>", lambda x: polygon_leave(root))

    def word_button1(root,word):
        setActiveWord(root, word)
        processActiveWord(root, word)

    def polygon_enter(root,word):
        if root.activeWord['index']==0:
            setWordStatus(root, word)

    def polygon_leave(root):
        if root.activeWord['index']==0:
            clearWordStatus(root)

    if word['color']!="green":
        canvas.itemconfigure(word['polygon'], fill='',outline=word['color'], width=1)



def setActiveWord(root, w):
    root.oldWord=root.activeWord
    root.activeWord=w

    if root.activeWord['index']>0:
        root.activeWord['canvas'].itemconfigure(root.activeWord['polygon'],fill='',
                                       outline='#00BFFF', width=2, activewidth=3, activeoutline='#00BFFF')
    if root.oldWord['index'] > 0:
        updateWordOutline(root.oldWord)

    if root.oldWord['index']==root.activeWord['index']:
        root.oldWord = root.activeWord = {'index': 0}

def processActiveWord(root, word):
        if root.activeWord['index'] >0 and word['index']==root.activeWord['index']:
             setWordStatus(root, root.activeWord)
             getUserUpdatesForTheActiveWord(root, root.activeWord)

def getUserUpdatesForTheActiveWord(root, activeWord):
    root.popUp = popupWindow(root.master,root,activeWord,root.popUpWidth,root.popUpHeight)
    root.wait_window(root.popUp.top)
    if root.popUp.top:
        root.popUp.top.destroy()
    setActiveWord(root, activeWord)
    setWordStatus(root, activeWord)









