from ClassificationApp_GUI.InteractiveWords import CreateButtonsFromTheWords

from ClassificationApp_GUI.OutputArea import UpdateOutput
from ClassificationApp_GUI.ScrollableImage import ScrollableImage, AddElementImageCanvas
from ClassificationApp_GUI.StatusBar import ClearWordStatus
from DatabaseProcessing.DatabaseProcessing import GetImgAndSDBFromTagId


def OpenTagId(root, tagId):
    root.tagId = tagId
    root.tagPath, root.sdb = GetImgAndSDBFromTagId(root.tagId)
    DisplayClassificationEditor(root)
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