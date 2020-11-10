from tkinter import Menu, filedialog, simpledialog
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
    root.menuBar.add_cascade(label="Export",menu=root.smExportTag)
    root.smExportTag.add_command(label="Export current Tag Information", command=lambda: ExportTag(root.tagId))
    root.smExportTag.add_command(label="Export all Tags", command=lambda: ExportAllTags())

    def ExportTag(tagId):
        if tagId:
            print("Export: "+str(tagId))
            pass

    def ExportAllTags():
        print("Export all tags")
        pass



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
            ProcessImagesFromTheUrlsInTheTextFile(root.suggestEngine, txtFileContainingUrls,root.minimumConfidence, extractTag)
        pass

    def ExtractFromImagePath(extractTag):
        singleImagePath = filedialog.askopenfilename(
            filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
        )
        if len(singleImagePath) > 1:
            root.imagePath = singleImagePath
            ExtractAndProcessSingleImage(root.suggestEngine, root.imagePath,root.minimumConfidence, extractTag)
        pass



    def ExtractFromImageUrl(extractTag):
        imageUrl = simpledialog.askstring("Input", "Enter the image URL: ", parent=root)
        if len(imageUrl) > 1:
            root.imagePath = imageUrl
            ExtractAndProcessSingleImage(root.suggestEngine, root.imagePath,root.minimumConfidence, extractTag)
        pass

    def StopBatchProcessing(root):
        if (root.total - root.processed) > 0 and not root.stopThread:
            root.stopThread = True




