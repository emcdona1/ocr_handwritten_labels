import os
import webbrowser
from tkinter import Menu, filedialog, simpledialog

from BuildPlantDictionary import buildPlantDictionary
from ClassificationApp_GUI.PopupWindowEditConfig import PopupWindowEditConfig
from Helper.SaveDataFramesToExcelFile import ExportSingleTagToCSV, ExportAllTagsToCSV, ExportTagsWithImportDatesToCSV
from ImageProcessor.ImageProcessorDriver import ProcessImagesInTheFolder, ProcessImagesFromTheUrlsInTheTextFile, \
    ExtractAndProcessSingleImage

def AddMenuAndSubMenu(root):
    # menu bar
    root.menuBar = Menu(root)
    root.config(menu=root.menuBar)
    # sub Menu
    # file
    smFile = Menu(root.menuBar)
    root.menuBar.add_cascade(label="File", menu=smFile)
    smFile.add_command(label="Process Tag (As is)", command=lambda: ExtractFromImagePath(False))
    smFile.add_command(label="Extract and Process Image with Tag", command=lambda: ExtractFromImagePath(True))
    smFile.add_command(label="Extract and Process Image url", command=lambda: ExtractFromImageUrl(True))


    # ExtractTag
    root.smExtractTag = Menu(root.menuBar)
    root.menuBar.add_cascade(label="Batch Tag Extraction", menu=root.smExtractTag)
    root.smExtractTag.add_command(label="Folder Containing Images", command=lambda: ExtractFromFolder(True))
    root.smExtractTag.add_command(label="Text File With Urls of Images", command=lambda: ExtractFromTxtFileUrls(True))
    root.smExtractTag.add_command(label="Stop Batch Processing", command=lambda: StopBatchProcessing(root), state="disabled")

    # Export to File
    root.smExportTag=Menu(root.menuBar)
    root.menuBar.add_cascade(label="Export To Excel File",menu=root.smExportTag)
    root.smExportTag.add_command(label="Current Tag:", command=lambda: ExportSingleTagToCSV(GetDestination(),root.tagId,root.imagePath.split("/")[-1]),state="disabled")
    root.smExportTag.add_command(label="Tags with import date:", command=lambda: ExportTagsWithImportDatesToCSV(GetDestination(),root.selectedFilter.split(" >")[0]),state="disabled")
    root.smExportTag.add_command(label="Export all Tags", command=lambda: ExportAllTagsToCSV(GetDestination()),state="normal")

    # Tools
    root.smTools=Menu(root.menuBar)
    root.menuBar.add_cascade(label="Tools",menu=root.smTools)
    root.smTools.add_command(label="Edit Configurations", command=lambda: EditConfiguration())
    root.smTools.add_command(label="Rebuild plant dictionary", command=lambda:buildPlantDictionary())

    def EditConfiguration():
        root.popUpEditConfig = PopupWindowEditConfig(root.master, root, r'Configuration.cfg')
        root.wait_window(root.popUpEditConfig.top)
        if root.popUpEditConfig.top:
            try:
                root.popUpEditConfig.top.destroy()
            except Exception as e:
                print("Restart application due to configuration update!")
                #raise Exception('Restart', 'Restart application due to configuration update!')

    def GetDestination():
        dirname = filedialog.askdirectory()+"/"
        if len(dirname)<2:
            dirname=root.defaultExportFolderPath;
        return dirname;

    def ExtractFromFolder(extractTag):
        imageSourceFolder = filedialog.askdirectory() + "/"
        if len(imageSourceFolder) > 2:
            ProcessImagesInTheFolder(root.suggestEngine, imageSourceFolder,
                                     root.minimumConfidence, extractTag)
        pass

    def ExtractFromTxtFileUrls(extractTag):
        txtFileContainingUrls = filedialog.askopenfilename(
            filetypes=(("TXT", "*.txt"), ("text", "*.txt"))
        )
        if len(txtFileContainingUrls) > 0:
            ProcessImagesFromTheUrlsInTheTextFile(txtFileContainingUrls, root.minimumConfidence, extractTag)
        pass

    def ExtractFromImagePath(extractTag):
        singleImagePath = filedialog.askopenfilename(
            filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
        )
        if len(singleImagePath) > 1:
            root.imagePath = singleImagePath
            ExtractAndProcessSingleImage(root.imagePath, root.minimumConfidence, extractTag)
        pass


    def ExtractFromImageUrl(extractTag):
        imageUrl = simpledialog.askstring("Input", "Enter the image URL: ", parent=root)
        if len(imageUrl) > 1:
            root.imagePath = imageUrl
            ExtractAndProcessSingleImage(root.imagePath, root.minimumConfidence, extractTag)
        pass

    def StopBatchProcessing(root):
        if (root.total - root.processed) > 0 and not root.stopThread:
            root.stopThread = True

