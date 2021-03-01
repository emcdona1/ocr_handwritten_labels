from DetectCorrectAndClassify.detect_wrong_words import detect_wrong_words


def detect_and_classify(sdb, min_confidence):
    """ Updates ImageProcessor.sdb object with word suggestions """
    # notDetected = 0
    # if not DetectTitle(sdb[:2]):
    #     notDetected += 1
    #     print("Could not detect Title!")
    #
    # if not detect_collector(sdb):
    #     notDetected += 1
    #     print("Could not detect Collector!")
    #
    # if not DetectAndSuggestDates(sdb):
    #     notDetected += 1
    #     print("Could not detect Dates!")
    #
    # if not DetectRegistrationNumber(sdb):
    #     notDetected += 1
    #     print("Could not detect Registration Number!")
    #
    # if not DetectAndSuggestScienteficWords(suggestEngine, sdb):
    #     notDetected += 1
    #     print("Could not suggest any scientific words!")
    #
    # if not DetectLocation(notDetected, sdb):
    #     notDetected += 1
    #     print("Could not detect location!")

    detect_wrong_words(sdb, min_confidence)
