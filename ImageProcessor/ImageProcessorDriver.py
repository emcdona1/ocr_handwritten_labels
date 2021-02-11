
import os

from queue import Queue

from ClassificationApp_GUI.LayoutGUI import UpdateProcessingCount
from ClassificationApp_GUI.StatusBar import SetStatusForWord
from ImageProcessor.ImageProcessor import ImageProcessor
from threading import Thread

ParallelProcessingSizeDefault = 4
root=None

def setRoot(r):
    global root
    root=r

def get_root():
    return root

def ProcessImagesInTheFolder(suggestEngine, imageFolder, minimumConfidence,extractTag):
    filePaths = []
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            filePaths.append(os.path.join(imageFolder, filename))
    try:
        ProcessMultipleImages(filePaths, minimumConfidence, extractTag)
    except Exception as error:
        print(f"{error} (Error Code:IPD_001)")
        pass
    pass


def ProcessImagesFromTheUrlsInTheTextFile(textFile, minimumConfidence, extractTag, vision_client):
    print('ProcessImagesFromTheUrlsInTheTextFile')
    filePaths = []
    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url = line.replace('\n', '')
        filePaths.append(url)
    try:
        ProcessMultipleImages(filePaths, minimumConfidence, extractTag, vision_client)
    except Exception as error:
        print(f"{error} (Error Code:IPD_002)")
        pass
    pass


def ExtractAndProcessSingleImage(imagePath, minimumConfidence, extractTag, vision_client):
    #imgProcessorObj = ImageProcessor(suggestEngine, imagePath, minimumConfidence,extractTag)
    #imgProcessorObj.processImage()
    return ProcessMultipleImages([imagePath], minimumConfidence, extractTag, vision_client, True)

def ProcessMultipleImages(filePaths, minimumConfidence, extractTag, vision_client, displayAfterProcessing=False):
    print('ProcessMultipleImages')
    # UpdateProcessingCount(len(filePaths))
    # args=(suggestEngine, filePaths,minimumConfidence,extractTag,displayAfterProcessing)
    # if root.parallelProcess:
    #     Thread(target=ProcessListOfImagePaths_Parallel,args=args).start()
    # else:
    # Thread(target=ProcessListOfImagePaths_Sequential,args=args).start()
    return ProcessListOfImagePaths_Sequential(filePaths, minimumConfidence, extractTag, vision_client, displayAfterProcessing)


def ProcessListOfImagePaths_Sequential(filePaths, minimumConfidence, extractTag, vision_client, displayAfterProcessing=False):
    print('ProcessListOfImagePaths_Sequential')
    i = 0
    for filePath in filePaths:
        # if not root.stopThread:
        #     i += 1
        #     imgProcessorObj = ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag,displayAfterProcessing)
        #     imgProcessorObj.processImage()
        # else:
        #     break
        i += 1
        img_processor_obj = ImageProcessor(filePath, minimumConfidence, extractTag, vision_client, displayAfterProcessing)
        gcv, correct = img_processor_obj.processImage()

    # if root.stopThread:
    #     UpdateProcessingCount(-(len(filePaths) - i), 0.01)
    #     SetStatusForWord(root, f"User interrupted the process! {i}/{len(filePaths)} files are processed!", "red")
    #     root.stopThread=False
    return gcv, correct
