from DetectCorrectAndClassify.DetectAndClassifyCollector import DetectCollector
from DetectCorrectAndClassify.DetectAndClassifyDates import DetectAndSuggestDates
from DetectCorrectAndClassify.DetectAndClassifyLocation import DetectLocation
from DetectCorrectAndClassify.DetectAndClassifyRegistrationNumber import DetectRegistrationNumber
from DetectCorrectAndClassify.DetectAndClassifyScienteficNames import DetectAndSuggestScienteficWords
from DetectCorrectAndClassify.DetectAndClassifyTitle import DetectTitle
from DetectCorrectAndClassify.DetectWrongWords import DetectWrongWords


def DetectAndClassify(suggestEngine, sdb, minimumConfidence):
    notDetected = 0
    if not DetectTitle(sdb[:2]):
        ++notDetected
        print("Could not detect Title!")

    if not DetectCollector(sdb):
        ++notDetected
        print("Could not detect Collector!")

    if not DetectAndSuggestDates(sdb):
        ++notDetected
        print("Could not detect Dates!")

    if not DetectRegistrationNumber(sdb):
        ++notDetected
        print("Could not detect Registration Number!")

    if not DetectAndSuggestScienteficWords(suggestEngine, sdb):
        ++notDetected
        print("Could not suggest any scientific words!")

    DetectWrongWords(sdb, minimumConfidence)

    if not DetectLocation(notDetected, sdb):
        ++notDetected
        print("Could not detect location!")
