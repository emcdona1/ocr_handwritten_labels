import multiprocessing
from threading import Thread
import requests
from lxml import html
from DatabaseProcessing.DatabaseProcessing import AddBarCodeInfo

xPathIRN = None
xPathTaxonomy = None
xPathCollector = None
xPathDetails = None
search_url = None


def set_barcode_info_details(irnPath, taxonomyPath, collectorPath, detailsPath, url):
    global xPathIRN
    global xPathTaxonomy
    global xPathCollector
    global xPathDetails
    global search_url
    xPathIRN = irnPath
    xPathTaxonomy = taxonomyPath
    xPathCollector = collectorPath
    xPathDetails = detailsPath
    search_url = url


def GetFirstValueIfExists(doc, xPath, default):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath)[0])
    else:
        return default


def GetDetails(doc, xPath, default):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath))
    else:
        return "[]"


def GetBarCodeInformationTupleFromResponse(response):
    tuples = []
    doc = html.fromstring(response.content)
    irn = GetFirstValueIfExists(doc, xPathIRN, "0")
    if int(irn) > 0:
        tuples.append(("IRN", irn))
        tuples.append(("Taxonomy", GetFirstValueIfExists(doc, xPathTaxonomy, "")))
        possibleCollector = GetFirstValueIfExists(doc, xPathCollector, "")
        if len(possibleCollector) > 0 and (not ':' in possibleCollector):
            tuples.append(("Collector", possibleCollector))

        details = GetDetails(doc, xPathDetails, "")
        if len(details) > 0:
            tuples.extend(getTupleFromDetails(details))
    return tuples


def getTupleFromDetails(details):
    details = details.replace(':', '')
    details = details.replace('  ', ' ')
    details = details.replace('[\'', '')
    details = details.replace('\']', '')
    details = details.replace('\', \'', '||')
    details = details.replace('[\"', '')
    details = details.replace('\"]', '')
    details = details.replace('\", \"', '||')
    details = details.replace('\', \"', '||')
    details = details.replace('\", \'', '||')
    details = details.replace(' ||', '||')
    details = details.replace('|| ', '')
    details = details.split('||')
    tuples = [(i, k) for i, k in zip(details[0::2], details[1::2])]
    return tuples


# initialize_barcode_info_table(55029,1068760)
def initialize_barcode_info_table(startNo, maxVal):
    for i in range(startNo, maxVal):
        searchKey = f"C{i:0>7}F"
        initialize_barcode_info_for_a_key(searchKey)


def initialize_barcode_info_for_a_key(searchKey):
    print(f"Populating BarCodeInfo for the barcode:{searchKey}\n")
    response = requests.get(f"{search_url}{searchKey}")
    ExtractDataFromResponseAndSaveToDatabase(searchKey, response)


def ExtractDataFromResponseAndSaveToDatabase(barcode, response):
    classificationTuples = GetBarCodeInformationTupleFromResponse(response)
    if len(classificationTuples) > 0:
        AddBarCodeInfo(barcode, classificationTuples)


def initialize_barcode_info_for_a_key_in_a_thread(searchKey):
    args = (searchKey,)
    Thread(target=initialize_barcode_info_for_a_key, args=args).start()
