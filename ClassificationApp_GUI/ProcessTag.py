from ClassificationApp_GUI.InteractiveWords import CreateButtonsFromTheWords

from ClassificationApp_GUI.OutputArea import UpdateOutput
from ClassificationApp_GUI.ScrollableImage import AddElementImageCanvas, END
from ClassificationApp_GUI.StatusBar import ClearWordStatus
from DatabaseProcessing.DatabaseProcessing import GetImgAndSDBFromTagId, GetTagClassification, GetBarCodeClassification


def ClearOldImage(root):
    for widget in root.imageCanvasFrame.winfo_children():
        widget.destroy()
    pass

def OpenTagId(root, tagId):
    if tagId>0:
        try:
            ClearOldImage(root)
            RemoveRootData(root)
            root.tagId=tagId
            root.tagPath, root.sdb,root.imagePath,root.processingTime,root.importDate,root.barCode= GetImgAndSDBFromTagId(root.tagId)
            root.classifiedData=GetTagClassification(root.tagId)
            root.classifiedDataForBarCode=GetBarCodeClassification(root.barCode) if len(root.barCode)>0 else []
            DisplayClassificationEditor(root)
        except Exception as error:
            print(f"{error} (Error Code:CAG_001)")
    pass


def DisplayClassificationEditor(root):
    AddElementImageCanvas(root)
    CreateButtonsFromTheWords(root)
    UpdateOutput(root)
    pass

def RemoveRootData(root):
    root.tagPath=root.sdb=root.imagePath=root.processingTime=root.importDate=root.barCode=root.irn=root.taxonomy=root.collector=root.details=None
    ClearWordStatus(root)
    root.outputField.delete('1.0', END)
    root.importDetails['text']=''


pass