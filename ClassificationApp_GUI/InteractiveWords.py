from ClassificationApp_GUI.PopUpInputBox import PopupWindow
from ClassificationApp_GUI.StatusBar import *
from ClassificationApp_GUI.WordOutline import UpdateWordOutline


def CreateButtonsFromTheWords(root):
    for db in root.sdb:
        for w in db:
            if w['index'] > 0:
                DrawBoxesInImage(root, root.scrollableImage.cnvs, w)


def DrawBoxesInImage(root, canvas, word):
    word['canvas'] = canvas
    word['polygon'] = canvas.create_polygon(word['tupleVertices'])
    # Horizontal line accross the word
    # canvas.create_line(word['sp'][0],word['sp'][1], word['ep'][0],word['ep'][1],dash=(4, 2))
    UpdateWordOutline(word)
    canvas.tag_bind(word.polygon, "<Button-1>", lambda x: word_button1(root, word))
    canvas.tag_bind(word.polygon, "<Enter>", lambda x: polygon_enter(root, word))
    canvas.tag_bind(word.polygon, "<Leave>", lambda x: polygon_leave(root))

    def word_button1(root, word):
        SetActiveWord(root, word)
        ProcessActiveWord(root, word)

    def polygon_enter(root, word):
        if root.activeWord['index'] == 0:
            SetWordStatus(root, word)

    def polygon_leave(root):
        if root.activeWord['index'] == 0:
            ClearWordStatus(root)

    if word['color'] != "green":
        canvas.itemconfigure(word['polygon'], fill='', outline=word['color'], width=1)


def SetActiveWord(root, w):
    root.oldWord = root.activeWord
    root.activeWord = w

    if root.activeWord['index'] > 0:
        root.activeWord['canvas'].itemconfigure(root.activeWord['polygon'], fill='',
                                                outline='#00BFFF', width=2, activewidth=3, activeoutline='#00BFFF')
    if root.oldWord['index'] > 0:
        UpdateWordOutline(root.oldWord)

    if root.oldWord['index'] == root.activeWord['index']:
        root.oldWord = root.activeWord = {'index': 0}


def ProcessActiveWord(root, word):
    if root.activeWord['index'] > 0 and word['index'] == root.activeWord['index']:
        SetWordStatus(root, root.activeWord)
        GetUserUpdatesForTheActiveWord(root, root.activeWord)


def GetUserUpdatesForTheActiveWord(root, activeWord):
    root.popUp = PopupWindow(root.master, root, activeWord)
    root.wait_window(root.popUp.top)
    if root.popUp.top:
        root.popUp.top.destroy()
    SetActiveWord(root, activeWord)
    SetWordStatus(root, activeWord)
