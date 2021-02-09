import os
from pathlib import Path
from string import ascii_lowercase

import requests
from lxml import html
from configparser import ConfigParser
from datetime import datetime

from Helper.Confirm import confirm

configParser = ConfigParser()
configFilePath = r'Configuration.cfg'
configParser.read(configFilePath)
genus_species_file_path = configParser.get('SNS_SERVER', 'genus_species_file_path')
search_url = configParser.get('SNS_SERVER', 'searchUrl')
xpath = configParser.get('SNS_SERVER', 'xPathGenusSpecies')


def getSearchXpathResult(searchUrlWithKey, xpath):
    response = requests.get(searchUrlWithKey)
    doc = html.fromstring(response.content)
    print(searchUrlWithKey)
    result = set()
    try:
        rawResult = doc.xpath(xpath)
        for g, s in zip(rawResult[0::2], rawResult[1::2]):
            result.add(g + " " + s)
    except Exception as error:
        print(f"{error} (Error Code:BPD_001)")
        print(" xpath error :")
    return list(result)


def buildPlantDictionary():
    buildFile=True
    filePath=Path(genus_species_file_path)
    if filePath.is_file():
        buildFile= confirm(genus_species_file_path + " already exists! Do you still want to build plant dictionary?")
        if buildFile:
            now = datetime.now()
            date_time = now.strftime("%Y_%d_%m_%H_%M_%S")
            bakFilePath= genus_species_file_path + "." + date_time + ".bak"
            os.rename(genus_species_file_path, bakFilePath)
            print("Old file is backed up at:"+bakFilePath)

    if buildFile:

        f = open(genus_species_file_path, "w")
        for a in ascii_lowercase:
            for b in ascii_lowercase:
                for c in ascii_lowercase:
                    searchKey = str(a) + str(b) + str(c) + "*"
                    result = getSearchXpathResult(search_url + searchKey, xpath)
                    if (len(result) > 0):
                        for r in result:
                            f.write(r + "\n")
        f.close()

