from ClassificationApp_GUI.LayoutGUI import CreateLayout,InitializeImportedListCBox
from ClassificationApp_GUI.MenuAndSubMenuAndFunctional import AddMenuAndSubMenu
from ClassificationApp_GUI.ScrollableImage import Tk
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


        #create layout
        root.title("Classify Specimen")
        CreateLayout(root)
        AddMenuAndSubMenu(root)
        InitializeImportedListCBox(root)
        root.mainloop()