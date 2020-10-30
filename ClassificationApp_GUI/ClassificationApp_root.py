from tkinter import filedialog, simpledialog

from ClassificationApp_GUI.InteractiveWords import MarkWordsInImage
from ClassificationApp_GUI.OutputArea import CreateOutputFrameToDisplayInfo, UpdateOutput
from ClassificationApp_GUI.ScrollableImage import ScrollableImage
from ClassificationApp_GUI.StatusBar import *
from DatabaseProcessing.DatabaseCalls import Call_SP_GetTagList
from DatabaseProcessing.DatabaseProcessing import GetImgAndSDBFromTagId
from Helper.BuildPlantDictionary import buildPlantDictionary
from Helper.WordCategories import initializeCategories
from ImageProcessor.ImageTagExtractor import *
from SuggestEngine.Get_SuggestEngine import GetRunningServerEngineOrCreateLocalForSuggestion


class ClassificationApp():
    def __init__(self, **kw):
        root = Tk()
        #################################################################
        root.windowWidth = 794
        root.windowHeight = 794
        root.imageWidth = 788
        root.imageHeight = 400
        root.popUpWidth = 350
        root.popUpHeight = 200
        root.wordHovered = ""
        root.destinationFolder = os.path.expanduser("~/Desktop/") + "Tags/"
        root.geometry = str(root.windowWidth) + "x" + str(root.windowHeight)
        initializeCategories(root)
        # conf=1 even if the confidence is 100% check the word if it is actual word or not
        # conf=0.90 ignore the words that have confidance more than 0.75%
        root.minimumConfidence = 1
        # suggestEnginesInitializations
        root.plantDictionaryPath = "InputResources/genusspecies_data.txt"
        root.suggestEngine = GetRunningServerEngineOrCreateLocalForSuggestion(root.plantDictionaryPath, "TRIE")
        #################################################################

        root.wm_geometry(root.geometry)
        root.resizable(0, 0)
        root.title("Classify Specimen")
        root.config(background="white")
        root.image_window = ""

        # menu bar
        root.menuBar = Menu(root)
        root.config(menu=root.menuBar)
        # sub Menu
        # file
        smFile = Menu(root.menuBar)
        root.menuBar.add_cascade(label="File", menu=smFile)
        smFile.add_command(label="Process Tag (As is)", command=lambda: OpenImage())
        smFile.add_command(label="Extract and Process Image with Tag", command=lambda: ExtractFromImagePath())
        smFile.add_command(label="Extract and Process Image url", command=lambda: ExtractFromImageUrl())

        # ExtractTag
        smExtractTag = Menu(root.menuBar)
        root.menuBar.add_cascade(label="Batch Tag Extraction", menu=smExtractTag)
        smExtractTag.add_command(label="Folder Containing Images", command=lambda: ExtractFromFolder())
        smExtractTag.add_command(label="Text File With Urls of Images", command=lambda: ExtractFromTxtFileUrls())

        # Tools
        smTools = Menu(root.menuBar)
        root.menuBar.add_cascade(label="Tools", menu=smTools)
        smTools.add_command(label="Extract Tags To Destination: " + root.destinationFolder,
                            command=lambda: ChangeDestination(0, smTools))
        smTools.add_command(label="Build Plant Dictionary: " + root.plantDictionaryPath,
                            command=lambda: buildPlantDictionary(root.plantDictionaryPath))

        # Image canvas area Row#0 both column
        root.imageCanvasFrame = Frame(root)
        root.imageCanvasFrame.grid(row=0, column=0, sticky='nsew')
        # status bar and user input Row#1 two columns
        root.hoverStatusFrame = Frame(root)
        root.hoverStatusFrame.grid(row=1, column=0, sticky='nsew')
        CreateStatusBar(root)
        SetStatus(root, "\n\t\t\t  Open image file to begin !")

        root.outputFrame = Frame(root)
        root.outputFrame.grid(row=2, column=0, sticky='nsew')
        CreateOutputFrameToDisplayInfo(root, root.outputFrame)

        #################################################################
        def ChangeDestination(index, menuItem):
            val = filedialog.askdirectory() + "/"
            if (len(val) > 1):
                root.destinationFolder
                menuItem.entryconfigure(index, label="Extract Tags To Destination: " + root.destinationFolder)
            pass

        def ExtractFromFolder():
            imageSourceFolder = filedialog.askdirectory() + "/"
            if len(imageSourceFolder) > 2:
                ProcessImagesInTheFolder(root.suggestEngine, imageSourceFolder, root.destinationFolder,
                                         root.minimumConfidence)
            pass

        def ExtractFromTxtFileUrls():
            txtFileContainingUrls = filedialog.askopenfilename(
                filetypes=(("TXT", "*.txt"), ("text", "*.txt"))
            )
            if len(txtFileContainingUrls) > 0:
                ProcessImagesFromTheUrlsInTheTextFile(root.suggestEngine, txtFileContainingUrls, root.destinationFolder,
                                                      root.minimumConfidence)
            pass

        def ExtractFromImagePath():
            singleImagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            if len(singleImagePath) > 1:
                imagePath, sdb, tagId = ExtractAndProcessSingleImage(root.suggestEngine, singleImagePath,
                                                                     root.destinationFolder, root.minimumConfidence)
                root.tagId = tagId
                DisplayClassificationEditor(root, imagePath, sdb)
            pass

        def ExtractFromImageUrl():
            imageUrl = simpledialog.askstring("Input", "Enter the image URL: ", parent=root)
            imagePath, sdb, tagId = ExtractAndProcessSingleImage(root.suggestEngine, imageUrl, root.destinationFolder,
                                                                 root.minimumConfidence)
            root.tagId = tagId
            DisplayClassificationEditor(root, imagePath, sdb)
            pass

        # will not save to database
        def OpenImage():
            imagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            if len(imagePath) > 1:
                imagePath, sdb, tagId = ExtractAndProcessSingleImage(root.suggestEngine, imagePath,
                                                                     root.destinationFolder, root.minimumConfidence)
                root.tagId = tagId
                DisplayClassificationEditor(root, imagePath, sdb)

        def DisplayClassificationEditor(root, imagePath, sdb):
            RemoveOldData(root)
            root.tagList=Call_SP_GetTagList('')
            root.imagePath = imagePath
            #root.sdb = sdb
            img,root.sdb=GetImgAndSDBFromTagId(root.tagId) #test only
            root.scrollableImage = ScrollableImage(root.imageCanvasFrame, root=root, scrollbarwidth=6,
                                                   width=root.imageWidth,
                                                   height=root.imageHeight)
            MarkWordsInImage(root)
            UpdateOutput(root)

        def RemoveOldData(root):
            ClearWordStatus(root)

        root.mainloop()
