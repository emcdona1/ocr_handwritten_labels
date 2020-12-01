from pathlib import Path

import pandas as pd

from DatabaseProcessing.DatabaseProcessing import GetDataForCSV, GetDataForCSVForImportDate


def SaveDataFramesToMultipleTabsInExcelFile(dfs,destination="test.xlsx"):
    writer = pd.ExcelWriter(destination, engine='xlsxwriter')
    i=0
    for df in dfs:
        df.to_excel(writer, sheet_name=f'Sheet{i}')
        i+=1
    writer.close()
    print(f"Successfully exported: {destination}");

def ExportSingleTagToCSV(destination,tagId,tagName):
    dest=CreateFolderAndGetPath(destination,f'Exported_{tagName.replace(".","_")}')
    dfs=GetDataForCSV(tagId)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def ExportAllTagsToCSV(destination):
    dest=CreateFolderAndGetPath(destination,'ExportedAllTags')
    dfs=GetDataForCSV(0)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def ExportTagsWithImportDatesToCSV(destination,importDateFilter):
    dest=CreateFolderAndGetPath(destination,f'ExportedForFilter_{importDateFilter}')
    dfs=GetDataForCSVForImportDate(importDateFilter)
    SaveDataFramesToMultipleTabsInExcelFile(dfs,dest)

def CreateFolderAndGetPath(exportToDestinationFolder,fileName):
    Path(exportToDestinationFolder).mkdir(parents=True, exist_ok=True)
    destPath= exportToDestinationFolder+"/"+fileName+".xlsx"
    return destPath.replace("//","/")

