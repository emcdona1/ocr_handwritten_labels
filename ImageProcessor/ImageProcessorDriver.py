
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

def ProcessImagesInTheFolder(suggestEngine, imageFolder, minimumConfidence,extractTag):
    filePaths = []
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            filePaths.append(os.path.join(imageFolder, filename))
    try:
        ProcessMultipleImages(suggestEngine, filePaths, minimumConfidence,extractTag)
    except Exception as error:
        print(f"{error} (Error Code:IPD_001)")
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
    except Exception as error:
        print(f"{error} (Error Code:IPD_002)")
        pass
    pass


def ExtractAndProcessSingleImage(suggestEngine, imagePath, minimumConfidence,extractTag):
    #imgProcessorObj = ImageProcessor(suggestEngine, imagePath, minimumConfidence,extractTag)
    #imgProcessorObj.processImage()
    ProcessMultipleImages(suggestEngine,[imagePath],minimumConfidence,extractTag,True)

def ProcessMultipleImages(suggestEngine, filePaths,minimumConfidence,extractTag,displayAfterProcessing=False):
    UpdateProcessingCount(len(filePaths))
    args=(suggestEngine, filePaths,minimumConfidence,extractTag,displayAfterProcessing)
    if root.parallelProcess:
        Thread(target=ProcessListOfImagePaths_Parallel,args=args).start()
    else:
        Thread(target=ProcessListOfImagePaths_Sequential,args=args).start()


def ProcessListOfImagePaths_Sequential(suggestEngine, filePaths, minimumConfidence,extractTag,displayAfterProcessing=False):
    i=0;
    for filePath in filePaths:
        if not root.stopThread:
            i+=1
            imgProcessorObj = ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag,displayAfterProcessing)
            imgProcessorObj.processImage()
        else:
            break

    if root.stopThread:
        UpdateProcessingCount(-(len(filePaths) - i), 0.01)
        SetStatusForWord(root, f"User interrupted the process! {i}/{len(filePaths)} files are processed!", "red")
        root.stopThread=False



def ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag,displayAfterProcessing=False):
    num_cores = root.parallelProcessThreadCount
    queue = Queue()
    for x in range(num_cores):
        infoExtractor = ImageThreadProcessor(queue)
        infoExtractor.daemon = True
        infoExtractor.start()

    for filePath in filePaths:
        imgProcessorObj = ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag,displayAfterProcessing)
        queue.put(imgProcessorObj)
    queue.join()


class ImageThreadProcessor(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            imageProcessorObj = self.queue.get()
            try:
                imageProcessorObj.processImage()
            finally:
                self.queue.task_done()
                print(imageProcessorObj.imagePath,": done")
