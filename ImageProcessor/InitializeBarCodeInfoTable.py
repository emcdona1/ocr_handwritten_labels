import multiprocessing
from threading import Thread
import requests
from lxml import html
from DatabaseProcessing.DatabaseProcessing import AddBarCodeInfo

xPathIRN=None
xPathTaxonomy = None
xPathCollector=None
xPathDetails=None
searchurl = None

def SetBarCodeInfoDetails(irnPath,taxonomyPath,collectorPath,detailsPath,url):
    global xPathIRN
    global xPathTaxonomy
    global xPathCollector
    global xPathDetails
    global searchurl
    xPathIRN=irnPath
    xPathTaxonomy=taxonomyPath
    xPathCollector=collectorPath
    xPathDetails=detailsPath
    searchurl=url



def GetFirstValueIfExists(doc,xPath,default):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath)[0])
    else:
        return default

def GetDetails(doc,xPath,default):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath))
    else:
        return "[]"

def GetBarCodeInformationTupleFromResponse(response):
    tuples=[]
    doc = html.fromstring(response.content)
    irn=GetFirstValueIfExists(doc,xPathIRN,"0")
    if int(irn)>0:
        tuples.append(("IRN",irn))
        tuples.append(("Taxonomy",GetFirstValueIfExists(doc,xPathTaxonomy,"")))
        possibleCollector=GetFirstValueIfExists(doc,xPathCollector,"")
        if len(possibleCollector)>0 and (not ':' in possibleCollector):
            tuples.append(("Collector",possibleCollector))

        details=GetDetails(doc,xPathDetails,"")
        if len(details)>0:
            tuples.extend(getTupleFromDetails(details))
    return tuples

def getTupleFromDetails(details):
    details=details.replace(':','')
    details=details.replace('  ',' ')
    details=details.replace('[\'','')
    details=details.replace('\']','')
    details=details.replace('\', \'','||')
    details=details.replace('[\"','')
    details=details.replace('\"]','')
    details=details.replace('\", \"','||')
    details=details.replace('\', \"','||')
    details=details.replace('\", \'','||')
    details=details.replace(' ||','||')
    details=details.replace('|| ','')
    details=details.split('||')
    tuples=[(i,k)for i,k in zip(details[0::2], details[1::2])]
    return tuples


#InitializeBarCodeInfoTable(55029,1068760)
def InitializeBarCodeInfoTable(startNo,maxVal):
        for i in range (startNo,maxVal):
            searchKey=f"C{i:0>7}F"
            InitializeBarCodeInfoForAKey(searchKey)

def InitializeBarCodeInfoForAKey(searchKey):
    print(f"Populating BarCodeInfo for the barcode:{searchKey}\n")
    response = requests.get(f"{searchurl}{searchKey}")
    ExtractDataFromResponseAndSaveToDatabase(searchKey,response)

def ExtractDataFromResponseAndSaveToDatabase(barCode,response):
    classificationTuples=GetBarCodeInformationTupleFromResponse(response)
    if len(classificationTuples)>0:
        AddBarCodeInfo(barCode,classificationTuples)

def InitializeBarCodeInfoForAKey_InAThread(searchKey):
    args = (searchKey,)
    Thread(target=InitializeBarCodeInfoForAKey, args=args).start()




