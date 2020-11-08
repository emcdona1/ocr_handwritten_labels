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
    root.irn=0
    ClearOutput(root)
    pass

def OpenTagId(root, tagId):
    root.tagId = tagId
    if root.tagId>0:
        try:
            RemoveOldData(root)
            root.tagPath, root.sdb,root.imagePath,root.processingTime,root.importDate, \
            root.barCode,root.irn,root.taxonomy,root.collector,root.details= GetImgAndSDBFromTagId(root.tagId)
            DisplayClassificationEditor(root)
        except Exception as error:
            #print(f"{error} (Error Code:CAG_001)")
            ClearOldImage(root)
    else:
        ClearOldImage(root)
    pass


def DisplayClassificationEditor(root):
    AddElementImageCanvas(root)
    CreateButtonsFromTheWords(root)
    UpdateOutput(root)
    pass




def RemoveOldData(root):
    ClearWordStatus(root)


pass