from DetectionCorrectAndClassify.DetectAndClassifyCollector import DetectCollector
from DetectionCorrectAndClassify.DetectAndClassifyDates import DetectAndSuggestDates
from DetectionCorrectAndClassify.DetectAndClassifyRegistrationNumber import DetectRegistrationNumber
from DetectionCorrectAndClassify.DetectAndClassifyScienteficNames import DetectAndSuggestScienteficWords
from DetectionCorrectAndClassify.DetectAndClassifyTitle import DetectTitle
from DetectionCorrectAndClassify.DetectWrongWords import DetectWrongWords


def DetectAndClassify(suggestEngine, sdb, minimumConfidence):
    if not DetectAndSuggestScienteficWords(suggestEngine, sdb):
        print("Could not suggest any scientific words!")

    if not DetectAndSuggestDates(sdb):
        print("Could not detect Dates!")

    if not DetectCollector(sdb):
        print("Could not detect Collector!")

    if not DetectRegistrationNumber(sdb):
        print("Could not detect Registration Number!")

    if not DetectTitle(sdb):
        print("Could not detect Title!")

    DetectWrongWords(sdb,minimumConfidence)

