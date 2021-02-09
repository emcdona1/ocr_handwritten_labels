import tkinter
import webbrowser
from tkinter import *
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox
from ClassificationApp_GUI.ProcessTag import OpenTagId, DisplayClassificationEditor, RemoveRootData
from ClassificationApp_GUI.StatusBar import SetStatusForWord
from DatabaseProcessing.DatabaseProcessing import DeleteTag, GetImportDates, GetImportedTagTuples, UpdateBarCode
import re

from ImageProcessor.InitializeBarCodeInfoTable import initialize_barcode_info_for_a_key

gRoot = None


def CreateLayout(root):
    global gRoot
    gRoot = root

    ###############sizes#############
    windowHeight = 600
    leftPanelWidthForTagList_width = 180
    rightPanelForImageStatusAndOutput_width = 600
    ddlBoxHeight = 30
    tagListControllerHeight = 30
    imageCanvasAreaHeight = 350
    statusAreaHeight = 60
    root.tagListBoxHeight = windowHeight - ddlBoxHeight
    root.canvasHeight = imageCanvasAreaHeight
    root.canvasWidth = rightPanelForImageStatusAndOutput_width

    ###############Panels#####################

    windowWidth = leftPanelWidthForTagList_width + rightPanelForImageStatusAndOutput_width
    # main window
    root.geometry = str(windowWidth) + "x" + str(windowHeight)
    root.wm_geometry(root.geometry)
    root.resizable(0, 0)
    root.config(background="white")
    # Left Panel for the tag list
    leftPanelFrame = Frame(root, width=leftPanelWidthForTagList_width, background="gray")
    leftPanelFrame.pack(anchor=NW, expand=True, side=LEFT)
    # Left Panel DDL select date
    selectDateFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width, background="gray34")
    selectDateFrame.pack(anchor=NW, expand=True, side=TOP)
    root.selectDateCBox = Combobox(selectDateFrame, values=[], font=("Courier", 14), state="readonly")
    root.selectDateCBox.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshFilteredList(event, x))
    root.selectDateCBox.pack()
    # TagFrame
    tagFrame = Frame(leftPanelFrame, width=leftPanelWidthForTagList_width, background="gray90")
    tagFrame.pack(anchor=SW, expand=True, side=BOTTOM)

    # Left Panel Tag List frame
    selectTagFrame = Frame(tagFrame, width=leftPanelWidthForTagList_width, background="gray90")
    selectTagFrame.pack(anchor=NE, expand=True, side=TOP)
    root.selectTagListBox = Listbox(selectTagFrame, font=("Courier", 15), height=32, bd=0, background="gray90")

    root.selectTagListBox.pack(side=LEFT, fill=BOTH, padx=0, pady=1, expand=True)
    root.selectTagListBox.bind('<<ListboxSelect>>', lambda event, x=root: TagSelected(event, x))
    root.selectTagListBox.bind('<Button-2>', lambda event, x=root: TagRequestDelete(event, x))
    root.selectTagListBox.rclick = RightClick(root.selectTagListBox)

    # Left Panel Tag List Controller
    root.tagListControllerFrame = Frame(tagFrame, width=leftPanelWidthForTagList_width,
                                        background="gray80", height=tagListControllerHeight)
    root.tagListControllerFrame.pack(side=BOTTOM, fill=BOTH, padx=0, pady=1, expand=True)

    root.previousPage = Button(root.tagListControllerFrame, text="|<", command=GetPreviousPage, background="gray90")
    root.previousPage.grid(row=0, column=0)
    root.pageDDL = Combobox(root.tagListControllerFrame, values=[], font=("Courier", 15), justify='center',
                            state="readonly", width=13, background="gray90")
    root.pageDDL.bind('<<ComboboxSelected>>', lambda event, x=root: RefreshTagListPage(event, x))
    root.pageDDL.grid(row=0, column=1)

    root.nextPage = Button(root.tagListControllerFrame, text=">|", command=GetNextPage, background="gray90")
    root.nextPage.grid(row=0, column=2)

    scrollbar = Scrollbar(selectTagFrame, bd=0, width=5)
    root.selectTagListBox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=root.selectTagListBox.yview)
    scrollbar.pack(side=RIGHT, fill=BOTH, expand=True)

    # Right Panel for the image Area, status, and output area
    rightPanelFrame = Frame(root, height=windowHeight, background="yellow")
    rightPanelFrame.pack(anchor=NE, expand=TRUE, fill=BOTH, side=RIGHT)
    # Right Panel canvas frame
    root.imageCanvasFrame = Frame(rightPanelFrame, height=imageCanvasAreaHeight,
                                  background="gray")
    root.imageCanvasFrame.pack(anchor=NE, expand=True, fill=BOTH, side=TOP)
    # status bar
    statusBarFrame = Frame(rightPanelFrame, height=statusAreaHeight, background="gray94")
    statusBarFrame.pack(anchor=NW, expand=True, fill=BOTH, side=TOP)
    wordStatusFrame = Frame(statusBarFrame, height=50, bd=1, background="gray95")
    wordStatusFrame.pack(anchor=NW, expand=False, fill=BOTH, side=TOP)

    root.wordStatusLabel = Label(wordStatusFrame, text="Please import or open image file to continue!",
                                 background="gray90", justify="left", bd=1, anchor="nw",
                                 font=("Courier", 14))
    root.wordStatusLabel.pack(expand=True, fill=BOTH, side=LEFT)

    importDetailsFrame = Frame(statusBarFrame, height=18, bd=0, background="gray80")
    importDetailsFrame.pack(anchor=SW, expand=TRUE, fill=BOTH, side=BOTTOM)

    root.importDetails = Label(importDetailsFrame, text="",
                               justify="left", bd=1, anchor="nw",
                               font=("Courier", 12), foreground="brown4")
    root.importDetails.pack(expand=True, fill=BOTH, side=LEFT)

    # output area
    outputAreaFrame = Frame(rightPanelFrame, height=(windowHeight - imageCanvasAreaHeight - statusAreaHeight),
                            background="white")
    outputAreaFrame.pack(anchor=SW, expand=True, fill=BOTH, side=BOTTOM)

    root.outputField = ScrolledText(outputAreaFrame, font=("Courier", 16), bd=0, highlightthickness=0)
    root.outputField.pack(padx=0, pady=2, fill=BOTH, expand=True)
    ConfigureOutputField(root)


def TagSelected(evt, root, showDeleteOption=False):
    try:
        root.tagId = 0
        root.barcode = ""
        w = evt.widget
        index = int(w.curselection()[0])
        root.tagId, root.imagePath = root.tagIdImagePathHolder[index]
        if root.tagId > 0:
            OpenTagId(root, root.tagId)
            if showDeleteOption:
                root.selectTagListBox.rclick.popup(evt, root, root.tagId, root.barcode, root.imagePath.split('/')[-1],
                                                   index)
        UpdateExportTagLabel(root)

    except Exception as error:
        # print(f"{error} (Error Code:LG_001)")
        pass
    pass


def TagRequestDelete(evt, root):
    root.selectTagListBox.selection_clear(0, END)
    root.selectTagListBox.selection_set(root.selectTagListBox.nearest(evt.y))
    root.selectTagListBox.activate(root.selectTagListBox.nearest(evt.y))
    TagSelected(evt, root, True)
    pass


def RefreshTagListPage(event, root):
    GetTagListAndDisplay(gRoot.selectDateCBox.get(), int(root.pageDDL.get().split(":")[1]) - 1)
    pass


def GetPreviousPage():
    text = gRoot.pageDDL.get().split(":")[0]
    currentPage = int(gRoot.pageDDL.get().split(":")[1])
    if currentPage > 1:
        gRoot.pageDDL.set(f"{text}:{currentPage - 1}")
        GetTagListAndDisplay(gRoot.selectDateCBox.get(), currentPage - 2)
    pass


def GetNextPage():
    text = gRoot.pageDDL.get().split(":")[0]
    currentPage = int(gRoot.pageDDL.get().split(":")[1])
    if currentPage * gRoot.noOfItemsInAPage < int(gRoot.selectDateCBox.get().split(">")[1]):
        gRoot.pageDDL.set(f"{text}:{currentPage + 1}")
        GetTagListAndDisplay(gRoot.selectDateCBox.get(), currentPage)
    pass


def RefreshFilteredList(event, root):
    root.selectedFilter = root.selectDateCBox.get()
    GetTagListAndDisplay(root.selectedFilter, 0)
    UpdateExportImportDatelabel(root)
    pass


def GetImportedDates(root):
    dates = [x[1] for x in root.importedTags]
    dates.append("Filter: None")
    return sorted(list(set(dates)))
    pass


def RefreshImportedDatesAndSelect(selectedFilter='Filter: None'):
    gRoot.selectDateCBoxOptions = []
    if len(gRoot.currentImportList) > 0:
        gRoot.selectDateCBoxOptions.append(f'Current Import >{len(gRoot.currentImportList)}')
    try:
        gRoot.selectDateCBoxOptions.extend(GetImportDates())
    except Exception as e:
        print(f"Database connection error:{e}")
        gRoot.selectDateCBoxOptions.extend(['Database Error>0'])

    gRoot.selectDateCBox['values'] = gRoot.selectDateCBoxOptions
    if selectedFilter == 'Filter: None':
        gRoot.selectedFilter = gRoot.selectDateCBoxOptions[0]
    else:
        gRoot.selectedFilter = selectedFilter
    SetTagListPageDropDown(gRoot.selectedFilter.split(">")[1])
    gRoot.selectDateCBox.set(gRoot.selectedFilter)
    GetTagListAndDisplay(gRoot.selectedFilter)


def SetTagListPageDropDown(totalItems):
    i = 1
    items = [f"Page:{i}"]
    while i * int(gRoot.noOfItemsInAPage) < int(totalItems):
        i += 1
        items.append(f"Page:{i}")

    gRoot.pageDDLOptions = items
    gRoot.pageDDL['values'] = items
    gRoot.pageDDL.set(items[0])


def GetTagListAndDisplay(filter, tagPageIndex=0):
    gRoot.tagPageIndex = tagPageIndex
    f = filter.split(" >")[0]
    if f == 'Current Import':
        InitializeTagListBox(gRoot.currentImportList)
    else:
        tagList = GetImportedTagTuples(f, gRoot.sortItemsByBarCode, tagPageIndex * gRoot.noOfItemsInAPage,
                                       gRoot.noOfItemsInAPage)
        InitializeTagListBox(tagList)


def AddNewTagOnTheTagList(tagId, importDate, imagePath, barcode):
    # tagId,BarCode,ImportDate,OriginalImagePath
    data = [(tagId, barcode, 'Current Import', imagePath)]
    data.extend(gRoot.currentImportList)
    gRoot.currentImportList = data
    currentImportOption = f'Current Import >{len(gRoot.currentImportList)}'
    gRoot.selectDateCBoxOptions = [currentImportOption]
    gRoot.selectDateCBoxOptions.extend(GetImportDates())
    gRoot.selectDateCBox['values'] = gRoot.selectDateCBoxOptions
    gRoot.selectedFilter = currentImportOption
    gRoot.selectDateCBox.set(gRoot.selectedFilter)
    InitializeTagListBox(gRoot.currentImportList)


def InitializeTagListBox(lst):
    gRoot.tagListDisplay = lst
    gRoot.selectTagListBox.delete(0, tkinter.END)
    gRoot.tagIdImagePathHolder = []
    i = 0

    if gRoot.tagListDisplay:
        for x in gRoot.tagListDisplay:
            # tagId,BarCode,ImportDate,OriginalImagePath
            gRoot.selectTagListBox.insert(i, str(x[1]) + "_" + str(x[3].split('/')[-1]))
            if i % 2 == 0:
                gRoot.selectTagListBox.itemconfigure(i, background="gainsboro", selectbackground="gray80",
                                                     selectforeground="sea green")
            else:
                gRoot.selectTagListBox.itemconfigure(i, selectbackground="gray80", selectforeground="sea green")

            gRoot.tagIdImagePathHolder.append((x[0], x[3]))
            i += 1


def DeleteRecord(root, index, tagId):
    root.selectTagListBox.delete(index)
    del root.tagIdImagePathHolder[index]
    del root.tagListDisplay[index]
    DeleteTag(tagId)
    OpenTagId(root, root.tagId)


def UpdateProcessingCount(count, processingTime=0, tagId=0, sdb='', tagPath='', imagePath='', importDate='', barcode='',
                          classifiedData='', display=False):
    global gRoot
    if (count > 0):
        gRoot.total += count
    if gRoot.total > 0:
        if count < 0:
            gRoot.processed -= count
            gRoot.totalTimeTaken += processingTime

        if (gRoot.total == gRoot.processed):
            gRoot.processed = gRoot.total = gRoot.totalTimeTaken = 0
            Config_StateMenu(gRoot, "normal")

        if (gRoot.total - gRoot.processed) > 0:
            if gRoot.totalTimeTaken > 0:
                remainingTime = (gRoot.totalTimeTaken * (gRoot.total - gRoot.processed)) / gRoot.processed
            else:
                remainingTime = (gRoot.total - gRoot.processed) * 14

            remainingMinutes = int(remainingTime // 60)
            remainingSeconds = int(((remainingTime - (remainingMinutes * 60)) * 100) // 100)
            strRemmsg = f"{remainingMinutes} minutes {remainingSeconds} seconds to complete!"
            SetStatusForWord(gRoot, f"[PROCESSING]: {gRoot.processed}/{gRoot.total} processed! {strRemmsg}", "brown4")
            Config_StateMenu(gRoot, "disabled")

    if tagId > 0:
        AddNewTagOnTheTagList(tagId, importDate, imagePath, barcode)
    if display:
        RemoveRootData(gRoot)
        gRoot.tagId = tagId
        gRoot.sdb = sdb
        gRoot.tagPath = tagPath
        gRoot.imagePath = imagePath
        gRoot.processingTime = processingTime
        gRoot.importDate = importDate
        gRoot.barCode = barcode
        gRoot.classifiedData = classifiedData
        DisplayClassificationEditor(gRoot)


def Config_StateMenu(root, state="normal"):
    root.menuBar.entryconfig("File", state=state)
    root.smExtractTag.entryconfig("Folder Containing Images", state=state)
    root.smExtractTag.entryconfig("Text File With Urls of Images", state=state)
    if state == "normal":
        root.smExtractTag.entryconfig("Stop Batch Processing", state="disabled")
    else:
        root.smExtractTag.entryconfig("Stop Batch Processing", state="normal")


def UpdateExportTagLabel(root):
    root.smExportTag.entryconfigure(0, label=f"Current Tag: ", state="disabled")
    if len(root.imagePath.split('/')[-1]) > 0:
        root.smExportTag.entryconfigure(0, label=f"Current Tag: {root.imagePath.split('/')[-1]}", state="normal")


def UpdateExportImportDatelabel(root):
    root.smExportTag.entryconfigure(1, label=f"Tags with import date: ", state="disabled")
    filter = (root.selectedFilter.split(" >")[0])
    nosymboltxt = re.sub(r'[^\w]', ' ', filter)
    nosymboltxt = nosymboltxt.replace(" ", "")
    if nosymboltxt.isdigit():
        root.smExportTag.entryconfigure(1, label=f"Tags with import date: {filter}", state="normal")


class RightClick:
    def __init__(self, master):
        self.aMenu = Menu(master, tearoff=0)
        self.aMenu.add_command(label='Delete', command=self.delete)
        self.aMenu.add_command(label='Update barcode', command=self.update_barcode)

    def delete(self):
        print(f"Deleting TagId:{self.tagId}")
        gRoot.sdb = ''
        DeleteRecord(gRoot, self.index, self.tagId)

    def update_barcode(self):
        barcode = simpledialog.askstring(title="Update Barcode", prompt="What is the barcode?",
                                         initialvalue=self.barcode)
        if not barcode == None:
            alreadyExists = UpdateBarCode(self.tagId, barcode)
            if not alreadyExists and len(barcode) > 2:
                initialize_barcode_info_for_a_key(barcode)
            OpenTagId(self.root, self.tagId)

    def popup(self, event, root, tagId, barcode, fileName, index):
        self.root = root
        self.fileName = fileName
        self.aMenu.entryconfigure(0, label=f"Delete: {fileName}")
        self.tagId = tagId
        self.barcode = barcode
        self.index = index
        self.aMenu.post(event.x_root, event.y_root)


def ConfigureOutputField(root):
    def enterTheTag(e, x):
        root.outputField.tag_config(x, foreground="blue", underline=1)
        root.outputField.config(cursor="hand2")

    def leaveTheTag(e, x):
        root.outputField.tag_config(x, foreground="blue", underline=0)
        root.outputField.config(cursor='')

    root.outputField.tag_config('label', foreground="green", font=("Courier", 14))
    root.outputField.tag_config('data', foreground="black", font=("Courier", 14))
    root.outputField.tag_config('line', foreground="gray50", font=("Courier", 14))
    root.outputField.tag_config("filePath", foreground="blue", underline=0, font=("Courier", 12))
    root.outputField.tag_config("barcode", foreground="blue", underline=0, font=("Courier", 14))
    root.outputField.tag_bind("filePath", "<Enter>", lambda e, x="filePath": enterTheTag(e, x))
    root.outputField.tag_bind("filePath", "<Leave>", lambda e, x="filePath": leaveTheTag(e, x))
    root.outputField.tag_bind("barcode", "<Enter>", lambda e, x="barcode": enterTheTag(e, x))
    root.outputField.tag_bind("barcode", "<Leave>", lambda e, x="barcode": leaveTheTag(e, x))
    root.outputField.tag_bind("filePath", "<Button-1>", openImageFromPath)
    root.outputField.tag_bind("barcode", "<Button-1>", openBarCodeInfo)


def openImageFromPath(event):
    path = gRoot.imagePathToOpen
    if len(path) > 0:
        if 'http' in path:
            webbrowser.open_new(path)
        else:
            webbrowser.open_new("file:///" + path)
    pass


def openBarCodeInfo(event):
    if len(gRoot.barCode) > 0:
        webbrowser.open_new(f'{gRoot.barcode_search_url}{gRoot.barCode}')
