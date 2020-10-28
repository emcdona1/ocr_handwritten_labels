import multiprocessing
import os

from joblib import Parallel

from ImageProcessor.ImageProcessorObj import ImageProcessor

ParallelProcessingSizeDefault = 4


def ProcessImagesInTheFolder(suggestEngine, imageFolder, destinationFolder, minimumConfidence):
    filePaths = []
    for filename in sorted(os.listdir(imageFolder)):
        if filename.endswith(".jpg"):
            filePaths.append(os.path.join(imageFolder, filename))
    try:
        ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, destinationFolder, minimumConfidence)
    except:
        pass
    pass


# process images from the provided urls inside the text file (ParallelExecution With Thread)
def ProcessImagesFromTheUrlsInTheTextFile(suggestEngine, textFile, destinationFolder, minimumConfidence):
    filePaths = []
    with open(textFile) as f:
        lines = f.readlines()
    for line in lines:
        url = line.replace("\n", "")
        filePaths.append(url)
    try:
        ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, destinationFolder, minimumConfidence)
    except:
        pass
    pass


def ExtractAndProcessSingleImage(suggestEngine, imagePath, destinationFolder, minimumConfidence):
    imgProcessorObj = ImageProcessor(suggestEngine, imagePath, destinationFolder, minimumConfidence)
    return imgProcessorObj.processImage()


def ProcessListOfImagePaths_Sequential(suggestEngine, filePaths, destinationFolder, minimumConfidence):
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)
    for filePath in filePaths:
        imgProcessorObj = ImageProcessor(suggestEngine, filePath, destinationFolder, minimumConfidence)
        imgProcessorObj.processImage()
    pass


def ProcessListOfImagePaths_Parallel(suggestEngine, filePaths, destinationFolder, minimumConfidence):
    num_cores = multiprocessing.cpu_count()
    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)
    imgObjListToprocess = [ImageProcessor(suggestEngine, filePath, destinationFolder, minimumConfidence) for filePath in
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
