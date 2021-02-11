from DetectCorrectAndClassify.DetectAndClassifyCollector import DetectCollector
from DetectCorrectAndClassify.DetectAndClassifyDates import DetectAndSuggestDates
from DetectCorrectAndClassify.DetectAndClassifyLocation import DetectLocation
from DetectCorrectAndClassify.DetectAndClassifyRegistrationNumber import DetectRegistrationNumber
from DetectCorrectAndClassify.DetectAndClassifyScienteficNames import DetectAndSuggestScienteficWords
from DetectCorrectAndClassify.DetectAndClassifyTitle import DetectTitle
from DetectCorrectAndClassify.DetectWrongWords import DetectWrongWords


def DetectAndClassify(suggestEngine, sdb, minimumConfidence):
    """ Updates ImageProcessor.sdb object with word suggestions """
    notDetected = 0
    if not DetectTitle(sdb[:2]):
        notDetected += 1
        print("Could not detect Title!")

    if not DetectCollector(sdb):
        notDetected += 1
        print("Could not detect Collector!")

    if not DetectAndSuggestDates(sdb):
        notDetected += 1
        print("Could not detect Dates!")

    if not DetectRegistrationNumber(sdb):
        notDetected += 1
        print("Could not detect Registration Number!")

    if not DetectAndSuggestScienteficWords(suggestEngine, sdb):
        notDetected += 1
        print("Could not suggest any scientific words!")

    if not DetectLocation(notDetected, sdb):
        notDetected += 1
        print("Could not detect location!")

    DetectWrongWords(sdb, minimumConfidence)
