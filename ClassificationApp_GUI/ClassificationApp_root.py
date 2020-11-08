import os

from ClassificationApp_GUI.LayoutGUI import CreateLayout, InitializeImportedListAndOpenTheTagId
from ClassificationApp_GUI.MenuAndSubMenuAndFunctional import AddMenuAndSubMenu
from ClassificationApp_GUI.ScrollableImage import Tk
from Helper.WordCategories import GetWordCategories
from ImageProcessor.ImageProcessorDriver import setRoot, ExtractAndProcessSingleImage
from ImageProcessor.InitializeDataFromImage import SetGoogleCloudVisionClient, SetBarCodeRegx
from SuggestEngine.Get_SuggestEngine import GetRunningServerEngineOrCreateLocalForSuggestion

from configparser import ConfigParser

class ClassificationApp():
    def __init__(self, **kw):
        root = Tk(className='ToolTip-demo')
        global gRoot
        gRoot = root
        #initialize data
        InitializeConfiguration(root)
        SetGoogleCloudVisionClient(root.serviceAccountTokenPath)
        SetBarCodeRegx(root.barCodeRegx)
        root.minimumConfidence = 1
        root.processed=0
        root.total=0
        root.totalTimeTaken=0
        root.stopThread = False
        root.selectedFilter="Filter: None"
        root.suggestEngine = GetRunningServerEngineOrCreateLocalForSuggestion(root, "TRIE")
        root.WordCategories = GetWordCategories()

        #create layout
        root.title("Classify Specimen")
        CreateLayout(root)
        AddMenuAndSubMenu(root)
        InitializeImportedListAndOpenTheTagId()

        #initialize root links to multiple places if needed
        setRoot(root)
        root.mainloop()


def InitializeConfiguration(root):
    root.configParser = ConfigParser()
    root.configParser.read(r'Configuration.cfg')
    root.plantDictionaryPath = root.configParser.get('SNS_SERVER', 'genusSpeciesFilePath')
    root.serviceAccountTokenPath=root.configParser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
    root.barCodeRegx=root.configParser.get('BARCODE', 'barCodeRegx')

    root.parallelProcess= True if root.configParser.get('IMAGE_PROCESSOR', 'parallelProcess').lower() in ['t','y','true','yes','1'] else False
    root.parallelProcessThreadCount=int(root.configParser.get('IMAGE_PROCESSOR', 'parallelProcessThreadCount'))


