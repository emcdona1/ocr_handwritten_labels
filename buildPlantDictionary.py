import os
from string import ascii_lowercase

from lxml import html
import requests




def getSearchXpathResult(searchUrlWithKey, xpath):
    response = requests.get(searchUrlWithKey)
    doc = html.fromstring(response.content)
    print(searchUrlWithKey)
    result = []
    try:
        result = doc.xpath(xpath)
    except:
        print(" xpath error :")
    return result


def buildPlantDictionary(destination):
    searchurl="http://www.theplantlist.org/tpl1.1/search?q="
    xpath="//td/a/span[@class='name']/*[@class='genus' or @class='species']/text()"
    f = open(destination, "w")
    for a in ascii_lowercase:
        for b in ascii_lowercase:
            for c in ascii_lowercase:
                searchKey=str(a)+str(b)+str(c)+"*"
                result=getSearchXpathResult(searchurl + searchKey, xpath)
                if (len(result) > 0):
                    for g, s in zip(result[0::2], result[1::2]):
                        f.write(g + " " + s + "\n")
    f.close()

#destinationFolder=os.path.expanduser("~/Desktop/")+"plantDictionary/"
#buildPlantDictionary(destinationFolder)
