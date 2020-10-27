from DetectCorrectAndClassify.DetectAndClassifyCollector import DetectCollector
from DetectCorrectAndClassify.DetectAndClassifyDates import DetectAndSuggestDates
from DetectCorrectAndClassify.DetectAndClassifyRegistrationNumber import DetectRegistrationNumber
from DetectCorrectAndClassify.DetectAndClassifyScienteficNames import DetectAndSuggestScienteficWords
from DetectCorrectAndClassify.DetectAndClassifyTitle import DetectTitle
from DetectCorrectAndClassify.DetectWrongWords import DetectWrongWords


def DetectAndClassify(suggestEngine, sdb, minimumConfidence):
    if not DetectTitle(sdb[:3]):
        print("Could not detect Title!")

    if not DetectCollector(sdb):
        print("Could not detect Collector!")

    if not DetectAndSuggestDates(sdb):
        print("Could not detect Dates!")

    if not DetectRegistrationNumber(sdb):
        print("Could not detect Registration Number!")

    if not DetectAndSuggestScienteficWords(suggestEngine, sdb):
        print("Could not suggest any scientific words!")

    DetectWrongWords(sdb,minimumConfidence)

