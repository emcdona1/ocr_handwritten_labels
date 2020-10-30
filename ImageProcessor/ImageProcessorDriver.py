import multiprocessing
import os

from joblib import Parallel

from DatabaseProcessing.DatabaseCalls import Call_SP_GetTagDetail
from ImageProcessor.ImageProcessor import ImageProcessor

ParallelProcessingSizeDefault = 4


def ProcessImagesInTheFolder(suggestEngine, imageFolder, minimumConfidence,extractTag):
    filePaths = []
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            filePaths.append(os.path.join(imageFolder, filename))
    try:
        ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag)
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
        ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag)
    except:
        pass
    pass


def ExtractAndProcessSingleImage(suggestEngine, imagePath, minimumConfidence,extractTag):
    imgProcessorObj = ImageProcessor(suggestEngine, imagePath, minimumConfidence,extractTag)
    return imgProcessorObj.processImage()


def ProcessListOfImagePaths_Sequential(suggestEngine, filePaths, minimumConfidence,extractTag):

    for filePath in filePaths:
        imgProcessorObj = ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag)
        imgProcessorObj.processImage()
    pass


def ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, minimumConfidence,extractTag):
    num_cores = multiprocessing.cpu_count()
    imgObjListToprocess = [ImageProcessor(suggestEngine, filePath, minimumConfidence,extractTag) for filePath in
                           filePaths]
    executor = Parallel(n_jobs=num_cores, backend='multiprocessing')
    tasks = (ExecuteProcessImage(imgObj) for imgObj in imgObjListToprocess)
    executor(tasks)


def ExecuteProcessImage(obj):
    try:
        return obj.processImage()
    except:
        print("Unknown Error when processing image!")
    return None
