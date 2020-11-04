import multiprocessing
import os

from joblib import Parallel

from ClassificationApp_GUI.LayoutGUI import UpdateProcessingCount, Config_StateMenu
from ClassificationApp_GUI.StatusBar import SetStatusForWord
from ImageProcessor.ImageProcessor import ImageProcessor
from threading import Thread

ParallelProcessingSizeDefault = 4
root=None
def setRoot(r):
    global root
    root=r

def ProcessImagesInTheFolder(suggestEngine, imageFolder, minimumConfidence,extractTag):
    filePaths = []
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            filePaths.append(os.path.join(imageFolder, filename))
    try:
        ProcessMultipleImages(suggestEngine, filePaths, minimumConfidence,extractTag)
    except:
        pass
    pass


def ProcessImagesFromTheUrlsInTheTextFile(suggestEngine, textFile, minimumConfidence,extractTag):
    filePaths = []
    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url = line.replace("\n", "")
        filePaths.append(url)
    try:
        ProcessMultipleImages(suggestEngine, filePaths, minimumConfidence, extractTag)
    except:
        pass
    pass


def ExtractAndProcessSingleImage(suggestEngine, imagePath, minimumConfidence,extractTag):
    #imgProcessorObj = ImageProcessor(suggestEngine, imagePath, minimumConfidence,extractTag)
    #imgProcessorObj.processImage()
    ProcessMultipleImages(suggestEngine,[imagePath],minimumConfidence,extractTag)

def ProcessMultipleImages(suggestEngine, filePaths,minimumConfidence,extractTag):
    UpdateProcessingCount(len(filePaths))
    # ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag)
    #ProcessListOfImagePaths_Sequential(suggestEngine, filePaths, minimumConfidence, extractTag)
    ProcessMultipleImages_Thread(suggestEngine, filePaths, minimumConfidence, extractTag)
    #ProcessListOfImagePaths_ThreadToThread(suggestEngine, filePaths, minimumConfidence, extractTag)

def ProcessMultipleImages_Thread(suggestEngine, filePaths,minimumConfidence,extractTag):

    args=(suggestEngine, filePaths,minimumConfidence,extractTag)
    Thread(target=ProcessListOfImagePaths_Sequential,args=args).start()



def ProcessListOfImagePaths_ThreadToThread(suggestEngine, filePaths, minimumConfidence,extractTag):
    num_cores = multiprocessing.cpu_count()
    imgObjListToprocess = [ImageProcessor(suggestEngine, filePath, minimumConfidence, extractTag) for filePath in
                           filePaths]
    for obj in imgObjListToprocess:
        args=(obj)
        Thread(target=obj.processImage).start()



def ProcessListOfImagePaths_Sequential(suggestEngine, filePaths, minimumConfidence,extractTag):
    i=0;
    for filePath in filePaths:
        if not root.stopThread:
            i+=1
            imgProcessorObj = ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag)
            imgProcessorObj.processImage()
        else:
            break

    if root.stopThread:
        UpdateProcessingCount(-(len(filePaths) - i), 0.01)
        SetStatusForWord(root, f"User interrupted the process! {i}/{len(filePaths)} files are processed!", "red")
        root.stopThread=False

def ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag):
    num_cores = multiprocessing.cpu_count()
    imgObjListToprocess = [ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag) for filePath in
                           filePaths]
    executor = Parallel(n_jobs=num_cores, backend='multiprocessing')
    tasks = (ExecuteProcessImage(imgObj) for imgObj in imgObjListToprocess)
    executor(tasks)


def ExecuteProcessImage(obj):
    try:
        obj.processImage()
    except:
        print("Unknown Error when processing image!")
    return None
