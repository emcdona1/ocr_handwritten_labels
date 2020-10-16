
from tkinter import filedialog, simpledialog

from imageTagExtractor import *
from interactiveWords import markWordsInImage
from outputArea import createOutputFrameToDisplayInfo, updateOutput
from scrollableImage import ScrollableImage
from statusBar import *
from wordCategories import initializeCategories


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
        smFile.add_command(label="Process Tag (As is)", command=lambda: openImage())
        smFile.add_command(label="Extract and Process Image with Tag", command=lambda: extractFromImagePath())
        smFile.add_command(label="Extract and Process Image url",command=lambda: extractFromImageUrl())

        #ExtractTag
        smExtractTag = Menu(root.menuBar)
        root.menuBar.add_cascade(label="Batch Processing", menu=smExtractTag)
        smExtractTag.add_command(label="Process Tags from Folder",command=lambda: extractFromFolder())
        smExtractTag.add_command(label="Process Tags from Text file containing urls", command=lambda: extractFromTxtFileUrls())

        #Tools
        smTools=Menu(root.menuBar)
        root.menuBar.add_cascade(label="Tools",menu=smTools)
        smTools.add_command(label="Extract Tags To Destination: " + root.destinationFolder, command=lambda: changeDestination(0, smTools))

        # Image canvas area Row#0 both column
        root.imageCanvasFrame = Frame(root)
        root.imageCanvasFrame.grid(row=0, column=0, sticky='nsew')
        # status bar and user input Row#1 two columns
        root.hoverStatusFrame = Frame(root)
        root.hoverStatusFrame.grid(row=1, column=0, sticky='nsew')
        createStatusBar(root)
        setStatus(root, "\n\t\t\t  Open image file to begin !")

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
                processImagesInTheFolder(imageSourceFolder, root.destinationFolder, root.minimumConfidence)
            pass

        def extractFromTxtFileUrls():
            txtFileContainingUrls = filedialog.askopenfilename(
                filetypes=(("TXT", "*.txt"), ("text", "*.txt"))
            )
            if len(txtFileContainingUrls)>0:
                processImagesFromTheUrlsInTheTextFile(txtFileContainingUrls, root.destinationFolder, root.minimumConfidence)
            pass

        def extractFromImagePath():
            singleImagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            if len(singleImagePath)>1:
                imagePath,df=extractAndProcessTagFromImagePath(singleImagePath,root.destinationFolder, root.minimumConfidence)
                displayClassificationEditor(root,imagePath,df)
            pass


        def extractFromImageUrl():
            imageUrl = simpledialog.askstring("Input", "Enter the image URL: ",parent=root)
            imagePath,df=extractAndProcessTagFromImagePath(imageUrl,root.destinationFolder, root.minimumConfidence)
            displayClassificationEditor(root,imagePath,df)
            pass

        #will not save to database
        def openImage():
            imagePath = filedialog.askopenfilename(
                filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
            )
            #df=processTagImage(imagePath,  root.minimumConfidence)
            df=processTagImage(imagePath,  root.minimumConfidence)
            displayClassificationEditor(root,imagePath,df)

        def displayClassificationEditor(root,imagePath,df):
            removeOldData(root)
            root.imagePath=imagePath
            root.df=df
            root.scrollableImage = ScrollableImage(root.imageCanvasFrame, root=root, scrollbarwidth=6, width=root.imageWidth,
                                                   height=root.imageHeight)
            markWordsInImage(root)
            updateOutput(root)

        def removeOldData(root):
            clearWordStatus(root)

        root.mainloop()