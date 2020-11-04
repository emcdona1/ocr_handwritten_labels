from ClassificationApp_GUI.InteractiveWords import CreateButtonsFromTheWords

from ClassificationApp_GUI.OutputArea import UpdateOutput, ClearOutput
from ClassificationApp_GUI.ScrollableImage import  AddElementImageCanvas
from ClassificationApp_GUI.StatusBar import ClearWordStatus
from DatabaseProcessing.DatabaseProcessing import GetImgAndSDBFromTagId

def ClearOldImage(root):
    RemoveOldData(root)
    for widget in root.imageCanvasFrame.winfo_children():
        widget.destroy()
    root.tagId=0
    ClearOutput(root)
    pass

def OpenTagId(root, tagId):
    root.tagId = tagId
    if root.tagId>0:
        try:
            root.tagPath, root.sdb,root.imagePath,root.processingTime,root.importDate = GetImgAndSDBFromTagId(root.tagId)
            DisplayClassificationEditor(root)
        except:
            ClearOldImage(root)
    else:
        ClearOldImage(root)
    pass


def DisplayClassificationEditor(root):
    RemoveOldData(root)
    AddElementImageCanvas(root)
    CreateButtonsFromTheWords(root)
    UpdateOutput(root)
    pass




def RemoveOldData(root):
    ClearWordStatus(root)


pass