from ClassificationApp_GUI.LayoutGUI import CreateLayout, GetImportedDates, \
    InitializeTagListBox, InitializeImportedListAndOpenTheTagId
from ClassificationApp_GUI.MenuAndSubMenuAndFunctional import AddMenuAndSubMenu
from ClassificationApp_GUI.ProcessTag import OpenTagId
from ClassificationApp_GUI.ScrollableImage import Tk
from DatabaseProcessing.DatabaseProcessing import GetImportedTagTuples
from Helper.WordCategories import GetWordCategories
from ImageProcessor.ImageProcessorDriver import setRoot
from SuggestEngine.Get_SuggestEngine import GetRunningServerEngineOrCreateLocalForSuggestion

class ClassificationApp():
    def __init__(self, **kw):
        root = Tk(className='ToolTip-demo')
        global gRoot
        gRoot = root
        #initialize data
        root.minimumConfidence = 1
        root.processed=0
        root.total=0
        root.totalTimeTaken=0
        root.stopThread = False
        root.selectedFilter="Filter: None"
        root.plantDictionaryPath = "InputResources/genusspecies_data.txt"
        root.suggestEngine = GetRunningServerEngineOrCreateLocalForSuggestion(root.plantDictionaryPath, "TRIE")
        root.WordCategories = GetWordCategories()


        #create layout
        root.title("Classify Specimen")
        CreateLayout(root)
        AddMenuAndSubMenu(root)
        InitializeImportedListAndOpenTheTagId()

        #initialize root links to multiple places if needed
        setRoot(root)
        root.mainloop()

