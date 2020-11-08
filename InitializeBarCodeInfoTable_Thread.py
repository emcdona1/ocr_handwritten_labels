import os
from queue import Queue
from threading import Thread
import requests
from lxml import html


class BarCodeInfoExtractor(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            searchKey = self.queue.get()
            try:
                GetInfoForBarCode(searchKey)
            finally:
                self.queue.task_done()



from DatabaseProcessing.DatabaseProcessing import AddBarCodeInfo

xPathIRN="//div[@class='view-content']/div/div[span/text()='IRN: ']/span/a[starts-with(@href, '/catalogue/')]/text()"
xPathTaxonomy = "//div[@class='view-content']/div/div[1]/span/a[starts-with(@href, '/taxonomy/')]/text()"
xPathCollector="//div[@class='view-content']/div/div[2]/span/text()"
xPathDetails="//div[@class='view-content']/div/div[position()>2 and span[not(a) and not(div)][2]]/span/text()"


def GetFirstValueIfExists(doc,xPath,default):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath)[0])
    else:
        return default

def GetDetails(doc,xPath):
    if doc.xpath(xPath):
        return str(doc.xpath(xPath))
    else:
        return "[]"



def GetBarCodeInformationFromResponse(response):
    doc = html.fromstring(response.content)
    irn=GetFirstValueIfExists(doc,xPathIRN,"0")
    taxonomy=GetFirstValueIfExists(doc,xPathTaxonomy,"")
    collector=GetFirstValueIfExists(doc,xPathCollector,"")
    details=GetDetails(doc,xPathDetails)
    return irn,taxonomy,collector,details


searchurl = "https://collections-botany.fieldmuseum.org/list?ss_ObjEcode="

def InitializeBarCodeInfoTable(startNo,maxVal):
        keys=[f"C{i:0>7}F" for i in range (startNo,maxVal)]
        queue = Queue()
        for x in range(8):
            infoExtractor = BarCodeInfoExtractor(queue)
            infoExtractor.daemon = True
            infoExtractor.start()

        for searchKey in keys:
            queue.put(searchKey)
        queue.join()



def GetInfoForBarCode(searchKey):
    print("Processing: ",searchKey)
    response = requests.get(searchurl+searchKey)
    ExtractDataFromResponseAndSaveToDatabase(searchKey,response)

def ExtractDataFromResponseAndSaveToDatabase(barCode,response):
    irn,taxonomy,collector,details=GetBarCodeInformationFromResponse(response)
    if(int(irn+"0")>0):
        AddBarCodeInfo(barCode,str(irn),str(taxonomy),str(collector),str(details))


