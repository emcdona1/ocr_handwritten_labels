import os
from tkinter import filedialog, simpledialog
from google.cloud import vision

from algorithmicMethods import removeDuplicates, getSerealizedData
from getSectionOfImage import getTagsFromTagUrlFile, getTagsFromImageFolder, getTagByEdgeDetection, initializeTemplates
from wordCategories import autoClassifyWords
from outputArea import createOutputFrameToDisplayInfo, updateOutput
from cetectWrongWords import detectWrongWords
from scrollableImage import ScrollableImage
from wordCategories import initializeCategories
from applyCorrection import applyCorrection
from initializeDataFromImage import initializeDataFromImage
from interactiveWords import markWordsInImage
from statusBar import *

class ClassificationApp():
    def __init__(self, **kw):
        root =Tk()
        #################################################################
        root.windowWidth = 794
        root.windowHeight = 794
        root.imageWidth = 788
        root.imageHeight = 400
        root.popUpWidth=350
        root.popUpHeight=200
        root.wordHovered = ""
        root.destinationFolder=os.path.expanduser("~/Desktop/")+"Tags/"
        root.geometry = str(root.windowWidth) + "x" + str(root.windowHeight)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountToken.json'
        root.client = vision.ImageAnnotatorClient()
        initializeCategories(root)
        initializeTemplates() #initialize templates
        # conf=1 even if the confidence is 100% check the word if it is actual word or not
        # conf=0.90 ignore the words that have confidance more than 0.75%
        root.minimumConfidence = .99

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
        #file
        smFile = Menu(root.menuBar)
        root.menuBar.add_cascade(label="File", menu=smFile)
        smFile.add_command(label="Open Image", command=lambda: openImage())

        #ExtractTag
        smExtractTag = Menu(root.menuBar)
        root.menuBar.add_cascade(label="ExtractTag", menu=smExtractTag)
        smExtractTag.add_command(label="Change Destination: "+ root.destinationFolder, command=lambda: changeDestination(0,smExtractTag))
        smExtractTag.add_command(label="Extract Tags from Folder",command=lambda: extractFromFolder())
        smExtractTag.add_command(label="Extract Tag from Single Image", command=lambda: extractFromImagePath())
        smExtractTag.add_command(label="Extract Tags from Text file containing urls", command=lambda: extractFromTxtFileUrls())
        smExtractTag.add_command(label="Extract Tags from Image url",command=lambda: extractFromImageUrl(root))

        # Image canvas area Row#0 both column
        root.imageCanvasFrame = Frame(root)
        root.imageCanvasFrame.grid(row=0, column=0, sticky='nsew')
        # status bar and user input Row#1 two columns
        root.hoverStatusFrame = Frame(root)
        root.hoverStatusFrame.grid(row=1, column=0, sticky='nsew')
        createStatusBar(root)
        setStatus(root, "\n\t\t\t  Open image file to begin !")
        #
        root.outputFrame = Frame(root)
        root.outputFrame.grid(row=2, column=0, sticky='nsew')
        createOutputFrameToDisplayInfo(root, root.outputFrame)

        #################################################################
        def changeDestination(index,menuItem):
            root.destinationFolder = filedialog.askdirectory()+"/"
            menuItem.entryconfigure(index,label="Change Destination: "+ root.destinationFolder)
            pass
        def extractFromFolder():
            imageSourceFolder = filedialog.askdirectory() + "/"
            if len(imageSourceFolder)>2:
                getTagsFromImageFolder(imageSourceFolder, root.destinationFolder, False)
            pass
        def extractFromImagePath():
            singleImagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            if len(singleImagePath)>1:
                filename=singleImagePath.split('/')[-1]
                getTagByEdgeDetection(singleImagePath, os.path.join(root.destinationFolder, filename),False)

            pass
        def extractFromTxtFileUrls():
            txtFileContainingUrls = filedialog.askopenfilename(
                filetypes=(("TXT", "*.txt"), ("text", "*.txt"))
            )
            if len(txtFileContainingUrls)>0:
                getTagsFromTagUrlFile(txtFileContainingUrls, root.destinationFolder, False)
            pass

        def extractFromImageUrl(root):
            imageUrl = simpledialog.askstring("Input", "Enter the image URL: ",parent=root)
            filename = imageUrl.split('/')[-1]
            getTagByEdgeDetection(imageUrl, os.path.join(root.destinationFolder, filename), False)
            pass

        def openImage():
            root.imagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            processNewImage(root)

        def processNewImage(root):
            removeOldData(root)
            #printTessaractOutputForImage(root.imagePath)
            initializeDataFromImage(root, vision)
            #print("After google OCR:")
            #print(root.df['description'][0])
            #RemoveDuplicates(root.df)
            #print("Correction skipped")
            root.df = getSerealizedData(root.df)
            detectWrongWords(root.df, root.minimumConfidence)
            try:
                applyCorrection(dfs=root.df)
            except:
                print("Could not apply the correction from bert")
                print (sys.exc_info())

            autoClassifyWords(root.df)

            root.scrollableImage = ScrollableImage(root.imageCanvasFrame, root=root, scrollbarwidth=6, width=root.imageWidth,
                                                   height=root.imageHeight)

            markWordsInImage(root)
            updateOutput(root)


        def removeOldData(root):
            clearWordStatus(root)

        root.mainloop()