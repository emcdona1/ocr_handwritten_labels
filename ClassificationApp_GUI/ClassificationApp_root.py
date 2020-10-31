from ClassificationApp_GUI.LayoutGUI import CreateLayout, AddElementSelectDate, AddElementSelectTag, \
    InitializeImportedListCBox, InitializeTagListBox, AddElementStatusBar
from ClassificationApp_GUI.MenuAndSubMenuAndFunctional import AddMenuAndSubMenu
from ClassificationApp_GUI.OutputArea import CreateOutputFrameToDisplayInfo
from ClassificationApp_GUI.ScrollableImage import AddElementImageCanvas, Tk
from ClassificationApp_GUI.StatusBar import *
from DatabaseProcessing.DatabaseProcessing import GetImportedTagTuples
from Helper.WordCategories import GetWordCategories
from SuggestEngine.Get_SuggestEngine import GetRunningServerEngineOrCreateLocalForSuggestion


class ClassificationApp():
    def __init__(self, **kw):
        root = Tk(className='ToolTip-demo')
        #initialize data
        root.minimumConfidence = 1
        root.plantDictionaryPath = "InputResources/genusspecies_data.txt"
        root.suggestEngine = GetRunningServerEngineOrCreateLocalForSuggestion(root.plantDictionaryPath, "TRIE")
        root.WordCategories = GetWordCategories()
        root.importedTags = GetImportedTagTuples()

        #create layout
        root.title("Classify Specimen")
        CreateLayout(root)
        AddMenuAndSubMenu(root)
        AddElementSelectDate(root)
        InitializeImportedListCBox(root)

        AddElementSelectTag(root)
        InitializeTagListBox(root)

        AddElementStatusBar(root)

        root.mainloop()

        # status bar and user input Row#1 two columns

        SetStatus(root, "\n\t\t\t  Open image file to begin !")
        # output Area
        root.outputFrame = Frame(root)
        root.outputFrame.grid(row=2, column=1, sticky='nsew')
        CreateOutputFrameToDisplayInfo(root, root.outputFrame)

        #################################################################







