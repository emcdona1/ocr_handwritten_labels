import os
from string import ascii_lowercase

from lxml import html
import requests


def selectResultAndAppendToFile(xmlDoc,xpath,destinationFile):
    result=[]
    try:
        result = xmlDoc.xpath(xpath)
    except:
        print("error :")
    if(len(result)>0):
        f = open(destinationFile, "a")
        for w in list(set(result)):
            f.write(w+"\n")
        f.close()
    pass


def buildCorpusBySearchingOnUrl(searchUrlWithKey, resultXpathsWithFileName, outputFolder):
    response = requests.get(searchUrlWithKey)
    doc = html.fromstring(response.content)
    print(searchUrlWithKey)
    try:
        for xpathFileName in resultXpathsWithFileName:
            xpath=xpathFileName[0]
            filePath=outputFolder+xpathFileName[1]
            selectResultAndAppendToFile(doc,xpath,filePath)
    except:
        print("error :" + searchUrlWithKey)
    pass

def buildCorpus(destination):
    searchurl="http://www.theplantlist.org/tpl1.1/search?q="
    resultXpathsWithFileName=[]#each xpath will have it's own corpusFile
    resultXpathsWithFileName.append(("//td[@class='name Accepted']/a/span[@class='name']/i[@class='genus']/text()","Accepted_genus.txt"))
    resultXpathsWithFileName.append(("//td[@class='name Accepted']/a/span[@class='name']/i[@class='species']/text()","Accepted_species.txt"))
    resultXpathsWithFileName.append(("//td[@class='name Synonym']/a/span[@class='name']/i[@class='genus']/text()","Synonym_genus.txt"))
    resultXpathsWithFileName.append(("//td[@class='name Synonym']/a/span[@class='name']/i[@class='species']/text()","Synonym_species.txt"))

    if not os.path.exists(destination):
        os.makedirs(destination)

    for a in ascii_lowercase:
        for b in ascii_lowercase:
            for c in ascii_lowercase:
                searchKey=str(a)+str(b)+str(c)+"*"
                try:
                    buildCorpusBySearchingOnUrl(searchurl+searchKey,resultXpathsWithFileName,destination)
                except:
                    print("error")



destinationFolder=os.path.expanduser("~/Desktop/")+"corpus/"
buildCorpus(destinationFolder)
