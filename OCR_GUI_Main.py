import os
from tkinter import filedialog
from google.cloud import vision
from CreateOutputFrameToDisplayInfo import CreateOutputFrameToDisplayInfo
from DetectWrongWords import DetectWrongWords
from ScrollableImage import ScrollableImage
from applyCorrection import ApplyCorrection
from globalCalls import updateOutput
from initializeDataFromImage import InitializeDataFromImage
from interactiveWords import MarkWordsInImage
from statusBar import *
from tesseractCalls import printTessaractOutputForImage

root =Tk()

#################################################################
root.windowWidth = 794
root.windowHeight = 794
root.imageWidth = 788
root.imageHeight = 400
root.wordHovered = ""
root.geometry = str(root.windowWidth) + "x" + str(root.windowHeight)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountToken.json'
root.client = vision.ImageAnnotatorClient()
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
subMenu = Menu(root.menuBar)
root.menuBar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open Image", command=lambda: openImage())

# Image canvas area Row#0 both column
root.imageCanvasFrame = Frame(root)
root.imageCanvasFrame.grid(row=0, column=0, sticky='nsew')
# status bar and user input Row#1 two columns
root.hoverStatusFrame = Frame(root)
root.hoverStatusFrame.grid(row=1, column=0, sticky='nsew')
CreateStatusBar(root)
SetStatus(root,"\n\t\t\t  Open image file to begin !")
#
root.outputFrame = Frame(root)
root.outputFrame.grid(row=2, column=0, sticky='nsew')
CreateOutputFrameToDisplayInfo(root,root.outputFrame)

#################################################################

def openImage():
    root.imagePath = filedialog.askopenfilename(
        filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
    )
    processNewImage(root)

def processNewImage(root):
    removeOldData(root)
    printTessaractOutputForImage(root.imagePath)
    InitializeDataFromImage(root,vision)
    print("After google OCR:")
    print(root.df['description'][0])
    #RemoveDuplicates(df)
    #print("Correction skipped")
    # df = GetSerealizedData2(df)
    DetectWrongWords(root.df,root.minimumConfidence)
    try:
        ApplyCorrection(dfs=root.df)
    except:
        print("Could not apply the correction from bert")

    root.scrollableImage = ScrollableImage(root.imageCanvasFrame, root=root, scrollbarwidth=6, width=root.imageWidth,
                                      height=root.imageHeight)
    MarkWordsInImage(root)
    updateOutput(root)


def removeOldData(root):
    ClearWordStatus(root)

root.mainloop()
