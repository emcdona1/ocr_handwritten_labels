import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Style, Combobox


from ClassificationApp_GUI.ProcessTag import OpenTagId, DisplayClassificationEditor
from ClassificationApp_GUI.StatusBar import SetStatusForWord, SetStatusForFileInfo
from DatabaseProcessing.DatabaseProcessing import GetImportedTagTuples, DeleteTag

gRoot=None


def CreateLayout(root):
    global gRoot
    gRoot=root

    ###############sizes#############
    windowHeight = 600
    leftPanelWidthForTagList_width = 180
    rightPanelForImageStatusAndOutput_width = 600
    ddlBoxHeight=30
    imageCanvasAreaHeight=350
    statusAreaHeight=60
    root.tagListBoxHeight=windowHeight-ddlBoxHeight
    root.canvasHeight=imageCanvasAreaHeight
    root.canvasWidth=rightPanelForImageStatusAndOutput_width

    ###############Panels#####################

    windowWidth = leftPanelWidthForTagList_width + rightPanelForImageStatusAndOutput_width
    #main window
    root.geometry = str(windowWidth) + "x" + str(windowHeight)
    root.wm_geometry(root.geometry)
    root.resizable(0,0)
    root.config(background="white")
    #Left Panel for the tag list
    leftPanelFrame = Frame(root, width=leftPanelWidthForTagList_width,background="gray")
    leftPanelFrame.pack(anchor=NW, expand=True, side=LEFT )
    # Left Panel DDL select date
    selectDateFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width, background="gray34")
    selectDateFrame.pack(anchor=NW, expand=True, side=TOP)
    root.selectDateCBox = Combobox(selectDateFrame, values=[], font=("Courier", 14), state="readonly")
    root.selectDateCBox.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshFilteredList(event, x))
    root.selectDateCBox.pack()

    # Left Panel Tag List frame
    selectTagFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width,
                                background="gray90")
    selectTagFrame.pack(anchor=SW, expand=True, side=BOTTOM)
    root.selectTagListBox = Listbox(selectTagFrame, font=("Courier", 15), height=1000, bd=0, background=None)
    root.selectTagListBox.pack(side=LEFT, fill=BOTH, padx=0, pady=1, expand=True)
    root.selectTagListBox.bind('<<ListboxSelect>>', lambda event, x=root: TagSelected(event, x))
    root.selectTagListBox.bind('<Button-2>', lambda event, x=root: TagRequestDelete(event, x))
    root.selectTagListBox.rclick = RightClick(root.selectTagListBox)



    scrollbar = Scrollbar(selectTagFrame, bd=0, width=5)
    root.selectTagListBox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=root.selectTagListBox.yview)
    scrollbar.pack(side=RIGHT, fill=BOTH, expand=True)

    #Right Panel for the image Area, status, and output area
    rightPanelFrame = Frame(root, height=windowHeight, background="yellow")
    rightPanelFrame.pack(anchor=NE, expand=TRUE,fill=BOTH, side=RIGHT)
    #Right Panel canvas frame
    root.imageCanvasFrame = Frame(rightPanelFrame, height=imageCanvasAreaHeight,
                              background="gray")
    root.imageCanvasFrame.pack(anchor=NE, expand=True, fill=BOTH,side=TOP)
    # status bar
    statusBarFrame = Frame(rightPanelFrame, height=statusAreaHeight,background="gray94")
    statusBarFrame.pack(anchor=NW, expand=True,fill=BOTH, side=TOP)
    wordStatusFrame = Frame(statusBarFrame, height=50, bd=1, background="gray95")
    wordStatusFrame.pack(anchor=NW, expand=False, fill=BOTH, side=TOP)

    root.wordStatusLabel = Label(wordStatusFrame, text="Please import or open image file to continue!",
                                 background="gray95", justify="left", bd=1, anchor="nw",
                                 font=("Courier", 14))
    root.wordStatusLabel.pack(expand=True, fill=BOTH, side=LEFT)

    fileInfoFrame = Frame(statusBarFrame, height=50, bd=1, background="gray88")
    fileInfoFrame.pack(anchor=NW, expand=False, fill=X, side=BOTTOM)
    root.fileInfoLabel = Label(fileInfoFrame, text="", background="gray88", justify="left", bd=1, anchor="nw",
                               font=("Courier", 14))
    root.fileInfoLabel.pack(expand=True, fill=BOTH, side=LEFT)


    # output area
    outputAreaFrame = Frame(rightPanelFrame, height=(windowHeight - imageCanvasAreaHeight-statusAreaHeight),
                                background="white")
    outputAreaFrame.pack(anchor=SW, expand=True,fill=BOTH, side=BOTTOM)

    root.outputField = ScrolledText(outputAreaFrame, font=("Courier", 16), bd=0, highlightthickness=0)
    root.outputField.pack(padx=0, pady=2, fill=BOTH, expand=True)


def TagSelected(evt,root,showDeleteOption=False):
    try:
        root.tagId=0
        w = evt.widget
        index=int(w.curselection()[0])
        root.tagId,root.imagePath=root.tagIdImagePathHolder[index]
        if root.tagId>0:
            if showDeleteOption:
                root.selectTagListBox.rclick.popup(evt,root.tagId,root.imagePath.split('/')[-1],index)
            OpenTagId(root, root.tagId)

    except:
        pass
    pass

def TagRequestDelete(evt,root):
    root.selectTagListBox.selection_clear(0, END)
    root.selectTagListBox.selection_set(root.selectTagListBox.nearest(evt.y))
    root.selectTagListBox.activate(root.selectTagListBox.nearest(evt.y))
    TagSelected(evt,root,True)
    pass


def InitializeTagListBox(root):
    root.selectTagListBox.delete(0, tkinter.END)
    root.tagIdImagePathHolder=[]
    i=0
    for x in root.importedTags:
        if x[1] == root.selectedFilter or root.selectedFilter == 'Filter: None':
            root.selectTagListBox.insert(i," " + x[2].split('/')[-1])
            root.tagIdImagePathHolder.append((x[0], x[2]))
            i+=1
    pass

def RefreshFilteredList(event,root):
    root.selectedFilter=root.selectDateCBox.get()
    InitializeTagListBox(root)
    pass

def GetImportedDates(root):
    dates=[x[1] for x in root.importedTags]
    dates.append("Filter: None")
    return sorted(list(set(dates)))
    pass

def InitializeImportedListAndOpenTheTagId(tagId=0):
    gRoot.tagId = tagId
    gRoot.importedTags = GetImportedTagTuples()
    gRoot.selectDateCBox['values']=GetImportedDates(gRoot)
    gRoot.selectDateCBox.set(gRoot.selectedFilter)
    InitializeTagListBox(gRoot)
    if(gRoot.tagId>0):
        OpenTagId(gRoot,gRoot.tagId)
    pass

def UpdateProcessingCount(count,processingTime=0):
    global gRoot
    if(count>0):
        gRoot.total += count
    if gRoot.total>0:
        if count<0:
            gRoot.processed -=count
            gRoot.totalTimeTaken+=processingTime

        if(gRoot.total==gRoot.processed):
            gRoot.processed=gRoot.total=gRoot.totalTimeTaken=0
            Config_StateMenu(gRoot, "normal")

        if(gRoot.total-gRoot.processed)>0:

            if gRoot.totalTimeTaken>0:
                remainingTime=(gRoot.totalTimeTaken *(gRoot.total-gRoot.processed))/ gRoot.processed
            else:
                remainingTime=(gRoot.total-gRoot.processed)*14

            remainingMinutes=remainingTime//60
            remainingSeconds=((remainingTime-(remainingMinutes*60))*100)//100
            strRemmsg=f"{remainingMinutes} minutes {remainingSeconds} seconds to complete!"
            SetStatusForWord(gRoot,f"[PROCESSING]: {gRoot.processed}/{gRoot.total} processed! {strRemmsg}")
            Config_StateMenu(gRoot,"disabled")


def Config_StateMenu(root,state="normal"):
            root.menuBar.entryconfig("File", state=state)
            root.menuBar.entryconfig("Batch Tag Extraction", state=state)
            root.menuBar.entryconfig("Tools", state=state)


class RightClick:
    def __init__(self, master):
        self.aMenu = Menu(master, tearoff=0)
        self.aMenu.add_command(label='Delete', command=self.delete)

    def delete(self):
        print(f"Deleting TagId:{self.tagId}")
        gRoot.sdb = ''
        DeleteRecord(gRoot,self.index,self.tagId)
        SetStatusForFileInfo(gRoot, '')


    def popup(self, event,tagId,fileName,index):
        self.fileName=fileName
        self.aMenu.entryconfigure(1, label=f"Delete: {fileName}")
        self.tagId=tagId
        self.index=index
        self.aMenu.post(event.x_root, event.y_root)

def DeleteRecord(root,index,tagId):
    root.selectTagListBox.delete(index)
    del root.tagIdImagePathHolder[index]
    root.importedTags =  [i for i in root.importedTags  if not i[0] == tagId]
    DeleteTag(tagId)


