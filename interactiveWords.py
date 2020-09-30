from PopUpInputBox import popupWindow
from globalCalls import setToDefaultWord
from statusBar import *
oldWord=activeWord={'index':0}


def MarkWordsInImage(root,scrollableImage,dfs):
    for index, w in dfs.iterrows():
        if w['index'] > 0:
            drawBoxesInImage(root,scrollableImage.cnvs,w)

def drawBoxesInImage(root,canvas, word):
    word['canvas']=canvas
    word['polygon']=canvas.create_polygon(word['tupleVertices'], fill='',outline='',width=1, activeoutline=word['color'],activewidth=2)
    canvas.tag_bind(word.polygon, "<Button-1>", lambda x: word_button1(root,word))
    canvas.tag_bind(word.polygon, "<Enter>", lambda x: polygon_enter(word))
    canvas.tag_bind(word.polygon, "<Leave>", lambda x: polygon_leave(word))

    def word_button1(self,word):
        SetActiveWord(word)
        ProcessActiveWord(self,word)

    def polygon_enter(word):
        global activeWord
        global oldWord
        if activeWord['index']==0:
            SetWordStatus(word)

    def polygon_leave(word):
        global activeWord
        global oldWord
        if activeWord['index']==0:
            ClearWordStatus()

    if word['color']!="green":
        canvas.itemconfigure(word['polygon'], fill='',outline=word['color'], width=1)


def GetActiveWord():
    return activeWord

def SetActiveWord(w):
    global activeWord
    global oldWord
    oldWord=activeWord
    activeWord=w

    if activeWord['index']>0:
        activeWord['canvas'].itemconfigure(activeWord['polygon'],fill='',
                                       outline='#00BFFF', width=2, activewidth=3, activeoutline='#00BFFF')


    if oldWord['index'] > 0:
        setToDefaultWord(oldWord)

    if oldWord['index']==activeWord['index']:
        oldWord = activeWord = {'index': 0}

def ProcessActiveWord(self,word):
        if activeWord['index'] >0 and word['index']==activeWord['index']:
             SetWordStatus(activeWord)
             getUserUpdatesForTheWord(self,activeWord)


def getUserUpdatesForTheWord(self,activeWord):
    self.w = popupWindow(self.master,activeWord,320,150)
    self.wait_window(self.w.top)
    if self.w.top:
        self.w.top.destroy()
    SetActiveWord(activeWord)
    SetWordStatus(activeWord)




