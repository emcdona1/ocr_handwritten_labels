from pathlib import Path

import pandas as pd

from DatabaseProcessing.DatabaseProcessing import GetDataForCSV, GetDataForCSVForImportDate
exportToDestinationFolder=""
def SetExportFolder(destination):
    global exportToDestinationFolder
    exportToDestinationFolder=destination


def SaveDataFramesToMultipleTabsInExcelFile(dfs,destination="test.xlsx"):
    writer = pd.ExcelWriter(destination, engine='xlsxwriter')
    i=0
    for df in dfs:
        df.to_excel(writer, sheet_name=f'Sheet{i}')
        i+=1
    writer.close()
    print(f"Successfully exported: {destination}");

def ExportSingleTagToCSV(tagId,tagName):
    dest=CreateFolderAndGetPath(f'SingleTag_{tagName.replace(".","_")[0]}')
    dfs=GetDataForCSV(tagId)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def ExportAllTagsToCSV():
    dest=CreateFolderAndGetPath('ExportedAllTags')
    dfs=GetDataForCSV(0)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def ExportTagsWithImportDatesToCSV(importDateFilter):
    dest=CreateFolderAndGetPath(f'ExportedForFilter_{importDateFilter}')
    dfs=GetDataForCSVForImportDate(importDateFilter)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def CreateFolderAndGetPath(fileName):
    Path(exportToDestinationFolder).mkdir(parents=True, exist_ok=True)
    destPath= exportToDestinationFolder+"/"+fileName+".xlsx"
    return destPath.replace("//","/")

