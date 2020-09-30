import os
from tkinter import filedialog

from google.cloud import vision

from AlgorithmicMethods import RemoveDuplicates, GetSerealizedData2
from CreateOutputFrameToDisplayInfo import CreateOutputFrameToDisplayInfo
from ScrollableImage import ScrollableImage
from applyCorrection import ApplyCorrection
from globalCalls import *
from initializeDataFromImage import InitializeDataFromImage
from interactiveWords import MarkWordsInImage
from statusBar import *

#################################################################
from tesseractCalls import printTessaractOutputForImage

windowWidth = 794
windowHeight = 794
imageWidth = 788
imageHeight = 400
totalColumns = 3
wordHovered = ""
geometry = str(windowWidth) + "x" + str(windowHeight)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountToken.json'
client = vision.ImageAnnotatorClient()
# conf=1 even if the confidence is 100% check the word if it is actual word or not
# conf=0.90 ignore the words that have confidance more than 0.75%
minimumConfidence = .99

#################################################################
root = Tk()
root.wm_geometry(geometry)
root.resizable(0, 0)
root.title("Classify Specimen")
root.config(background="white")
root.image_window = ""

textInPath = StringVar()
userInputVal = StringVar()

# menu bar
menuBar = Menu(root)
root.config(menu=menuBar)
# sub Menu
subMenu = Menu(menuBar)
menuBar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open Image", command=lambda: openImage())

# Image canvas area Row#0 both column
imageCanvasFrame = Frame(root)
imageCanvasFrame.grid(row=0, column=0, sticky='nsew')
# status bar and user input Row#1 two columns
hoverStatusFrame = Frame(root)
hoverStatusFrame.grid(row=1, column=0, sticky='nsew')
CreateStatusBar(hoverStatusFrame, windowWidth)
SetStatus("\n\t\t\t  Open image file to begin !")
#
outputFrame = Frame(root)
outputFrame.grid(row=2, column=0, sticky='nsew')
CreateOutputFrameToDisplayInfo(outputFrame, windowWidth)

#################################################################

def openImage():
    imagePath = filedialog.askopenfilename(
        filetypes=(("PNG", "*.png"), ("PNG", "*.png"))
    )
    processNewImage(imagePath)

def processNewImage(imagePath):
    removeOldData()
    printTessaractOutputForImage(imagePath)
    df = InitializeDataFromImage(imagePath, client, vision, minimumConfidence)
    print("After google OCR:")
    print(df['description'][0])
    RemoveDuplicates(df)
    df = GetSerealizedData2(df)

    ApplyCorrection(dfs=df, minimumConfidence=minimumConfidence)

    root.image = PhotoImage(file=imagePath)

    scrollableImage = ScrollableImage(imageCanvasFrame, root=root, scrollbarwidth=6, width=imageWidth,
                                      height=imageHeight)
    MarkWordsInImage(root, scrollableImage, df)
    setDF(d=df)

def removeOldData():
    ClearWordStatus()



root.mainloop()
