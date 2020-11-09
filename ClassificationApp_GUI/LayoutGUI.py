import tkinter
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox


from ClassificationApp_GUI.ProcessTag import OpenTagId, DisplayClassificationEditor, RemoveRootData
from ClassificationApp_GUI.StatusBar import SetStatusForWord
from DatabaseProcessing.DatabaseProcessing import DeleteTag, GetImportDates, GetImportedTagTuples

gRoot=None


def CreateLayout(root):
    global gRoot
    gRoot=root

    ###############sizes#############
    windowHeight = 600
    leftPanelWidthForTagList_width = 180
    rightPanelForImageStatusAndOutput_width = 600
    ddlBoxHeight=30
    tagListControllerHeight=30
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
    #TagFrame
    tagFrame=Frame(leftPanelFrame, width=leftPanelWidthForTagList_width,background="gray90")
    tagFrame.pack(anchor=SW, expand=True, side=BOTTOM)

    # Left Panel Tag List frame
    selectTagFrame = Frame(tagFrame, width=leftPanelWidthForTagList_width,background="gray90")
    selectTagFrame.pack(anchor=NE, expand=True, side=TOP)
    root.selectTagListBox = Listbox(selectTagFrame, font=("Courier", 15), height=32, bd=0, background=None)
    root.selectTagListBox.pack(side=LEFT, fill=BOTH, padx=0, pady=1, expand=True)
    root.selectTagListBox.bind('<<ListboxSelect>>', lambda event, x=root: TagSelected(event, x))
    root.selectTagListBox.bind('<Button-2>', lambda event, x=root: TagRequestDelete(event, x))
    root.selectTagListBox.rclick = RightClick(root.selectTagListBox)

    # Left Panel Tag List Controller
    root.tagListControllerFrame=Frame(tagFrame, width=leftPanelWidthForTagList_width,
                                 background="gray80",height=tagListControllerHeight)
    root.tagListControllerFrame.pack(side=BOTTOM,fill=BOTH,padx=0,pady=1, expand=True)

    root.previousPage=Button(root.tagListControllerFrame, text ="|<", command = GetPreviousPage)
    root.previousPage.grid(row=0,column=0)
    root.pageDDL = Combobox(root.tagListControllerFrame, values=[], font=("Courier", 15), justify='center',state="readonly",width=13)
    root.pageDDL.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshTagListPage(event, x))
    root.pageDDL.grid(row=0,column=1)

    root.nextPage=Button(root.tagListControllerFrame, text =">|", command = GetNextPage)
    root.nextPage.grid(row=0,column=2)

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
                                 background="gray90", justify="left", bd=1, anchor="nw",
                                 font=("Courier", 14))
    root.wordStatusLabel.pack(expand=True, fill=BOTH, side=LEFT)



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

    except Exception as error:
        #print(f"{error} (Error Code:LG_001)")
        pass
    pass

def TagRequestDelete(evt,root):
    root.selectTagListBox.selection_clear(0, END)
    root.selectTagListBox.selection_set(root.selectTagListBox.nearest(evt.y))
    root.selectTagListBox.activate(root.selectTagListBox.nearest(evt.y))
    TagSelected(evt,root,True)
    pass

def RefreshTagListPage(event,root):
    GetTagListAndDisplay(gRoot.selectDateCBox.get(),int(root.pageDDL.get().split(":")[1])-1)
    pass

def GetPreviousPage():
    text=gRoot.pageDDL.get().split(":")[0]
    currentPage=int(gRoot.pageDDL.get().split(":")[1])
    if currentPage>1:
        gRoot.pageDDL.set(f"{text}:{currentPage-1}")
        GetTagListAndDisplay(gRoot.selectDateCBox.get(),currentPage-2)
    pass

def GetNextPage():
    text=gRoot.pageDDL.get().split(":")[0]
    currentPage=int(gRoot.pageDDL.get().split(":")[1])
    if currentPage*gRoot.noOfItemsInAPage<int(gRoot.selectDateCBox.get().split(">")[1]):
        gRoot.pageDDL.set(f"{text}:{currentPage+1}")
        GetTagListAndDisplay(gRoot.selectDateCBox.get(),currentPage)
    pass

def RefreshFilteredList(event,root):
    root.selectedFilter=root.selectDateCBox.get()
    GetTagListAndDisplay(root.selectedFilter,0)
    pass

def GetImportedDates(root):
    dates=[x[1] for x in root.importedTags]
    dates.append("Filter: None")
    return sorted(list(set(dates)))
    pass

def RefreshImportedDatesAndSelect(selectedFilter='Filter: None'):
    gRoot.selectDateCBoxOptions=[]
    if len(gRoot.currentImportList)>0:
        gRoot.selectDateCBoxOptions.append(f'Current Import >{len(gRoot.currentImportList)}')
    gRoot.selectDateCBoxOptions.extend(GetImportDates())
    gRoot.selectDateCBox['values']=gRoot.selectDateCBoxOptions
    if selectedFilter=='Filter: None':
        gRoot.selectedFilter=gRoot.selectDateCBoxOptions[0]
    else:
        gRoot.selectedFilter=selectedFilter
    SetTagListPageDropDown(gRoot.selectedFilter.split(">")[1])
    gRoot.selectDateCBox.set(gRoot.selectedFilter)
    GetTagListAndDisplay(gRoot.selectedFilter)

def SetTagListPageDropDown(totalItems):
    i=1
    items=[f"Page:{i}"]
    while i*int(gRoot.noOfItemsInAPage)<int(totalItems):
        i+=1
        items.append(f"Page:{i}")

    gRoot.pageDDLOptions=items
    gRoot.pageDDL['values']=items
    gRoot.pageDDL.set(items[0])


def GetTagListAndDisplay(filter,tagPageIndex=0):
    gRoot.tagPageIndex=tagPageIndex
    f=filter.split(" >")[0]
    if f=='Current Import':
        InitializeTagListBox(gRoot.currentImportList)
    else:
        tagList=GetImportedTagTuples(f,gRoot.sortItemsByBarCode,tagPageIndex*gRoot.noOfItemsInAPage,gRoot.noOfItemsInAPage)
        InitializeTagListBox(tagList)

def AddNewTagOnTheTagList(tagId,importDate,imagePath,barCode):
    #tagId,BarCode,ImportDate,OriginalImagePath
    data=[(tagId,barCode,'Current Import',imagePath)]
    data.extend(gRoot.currentImportList)
    gRoot.currentImportList=data
    currentImportOption=f'Current Import >{len(gRoot.currentImportList)}'
    gRoot.selectDateCBoxOptions=[currentImportOption]
    gRoot.selectDateCBoxOptions.extend(GetImportDates())
    gRoot.selectDateCBox['values']=gRoot.selectDateCBoxOptions
    gRoot.selectedFilter=currentImportOption
    gRoot.selectDateCBox.set(gRoot.selectedFilter)
    InitializeTagListBox(gRoot.currentImportList)

def InitializeTagListBox(lst):
    gRoot.tagListDisplay=lst
    gRoot.selectTagListBox.delete(0, tkinter.END)
    gRoot.tagIdImagePathHolder=[]
    i=0
    for x in gRoot.tagListDisplay:
        #tagId,BarCode,ImportDate,OriginalImagePath
        gRoot.selectTagListBox.insert(i,str(x[1])+"_" + str(x[3].split('/')[-1]))
        gRoot.tagIdImagePathHolder.append((x[0], x[3]))
        i+=1

def DeleteRecord(root,index,tagId):
    root.selectTagListBox.delete(index)
    del root.tagIdImagePathHolder[index]
    del root.tagListDisplay[index]
    DeleteTag(tagId)


def UpdateProcessingCount(count,processingTime=0,tagId=0,sdb='',tagPath='',imagePath='',importDate='',barCode='',classifiedData='',display=False):
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

            remainingMinutes=int(remainingTime//60)
            remainingSeconds=int(((remainingTime-(remainingMinutes*60))*100)//100)
            strRemmsg=f"{remainingMinutes} minutes {remainingSeconds} seconds to complete!"
            SetStatusForWord(gRoot,f"[PROCESSING]: {gRoot.processed}/{gRoot.total} processed! {strRemmsg}","brown4")
            Config_StateMenu(gRoot,"disabled")

    if tagId>0:
        AddNewTagOnTheTagList(tagId,importDate,imagePath,barCode)
    if display:
        RemoveRootData(gRoot)
        gRoot.tagId=tagId
        gRoot.sdb=sdb
        gRoot.tagPath=tagPath
        gRoot.imagePath=imagePath
        gRoot.processingTime=processingTime
        gRoot.importDate=importDate
        gRoot.barCode=barCode
        gRoot.classifiedData=classifiedData
        DisplayClassificationEditor(gRoot)

def Config_StateMenu(root,state="normal"):
    root.menuBar.entryconfig("File", state=state)
    root.smExtractTag.entryconfig("Folder Containing Images", state=state)
    root.smExtractTag.entryconfig("Text File With Urls of Images", state=state)
    if state=="normal":
        root.smExtractTag.entryconfig("Stop Batch Processing", state="disabled")
    else:
        root.smExtractTag.entryconfig("Stop Batch Processing", state="normal")


class RightClick:
    def __init__(self, master):
        self.aMenu = Menu(master, tearoff=0)
        self.aMenu.add_command(label='Delete', command=self.delete)

    def delete(self):
        print(f"Deleting TagId:{self.tagId}")
        gRoot.sdb = ''
        DeleteRecord(gRoot,self.index,self.tagId)


    def popup(self, event,tagId,fileName,index):
        self.fileName=fileName
        self.aMenu.entryconfigure(1, label=f"Delete: {fileName}")
        self.tagId=tagId
        self.index=index
        self.aMenu.post(event.x_root, event.y_root)







