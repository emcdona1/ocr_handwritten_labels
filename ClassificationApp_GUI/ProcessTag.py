from ClassificationApp_GUI.InteractiveWords import CreateButtonsFromTheWords

from ClassificationApp_GUI.OutputArea import UpdateOutput, ClearOutput
from ClassificationApp_GUI.ScrollableImage import ScrollableImage, AddElementImageCanvas
from ClassificationApp_GUI.StatusBar import ClearWordStatus, SetFileInfo
from DatabaseProcessing.DatabaseProcessing import GetImgAndSDBFromTagId

def ClearOldImage(root):
    RemoveOldData(root)
    root.scrollableImage.RemoveImage(root)
    root.tagId=0
    ClearOutput(root)
    pass

def OpenTagId(root, tagId):
    root.tagId = tagId
    if root.tagId>0:
        try:
            root.tagPath, root.sdb,root.imagePath,root.processingTime = GetImgAndSDBFromTagId(root.tagId)
            DisplayClassificationEditor(root)
        except:
            ClearOldImage(root)
    else:
        ClearOldImage(root)
    pass


def DisplayClassificationEditor(root):
    RemoveOldData(root)
    AddElementImageCanvas(root)
    SetFileInfo(root,root.imagePath,root.processingTime)
    CreateButtonsFromTheWords(root)
    UpdateOutput(root)
    pass




def RemoveOldData(root):
    ClearWordStatus(root)


pass