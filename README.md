# OCRProject

#Execution
 from terminal navigate to main.py and execute following command
 python3 main.py
 it will open GUI window, 
 1. File
    > Open Image : to classify any image
 2. ExtractTag
    > Change Destination: to specify the folder to keep extracted tags
    > Extract Tags from folder: extract tags of all images within a folder
    > Extra Tag from Single Image: extract tag of one image
    > Extract Tags from Text file containing Urls: extract tags from each url
    > Extract Tag from Image url: extract tag from single image url
 
 3. Once the image is opened
    > Application would automatically classify the data
    > Click on word to to update the classification information or word data
        
 
 
#Solution approach

Part#1 Extract the tags from images.
Sample images are inside the InputResources/SampleImages. And the urls inside the text file "InputResources/SampleImages/TagUrls.txt"
Execute GetSectionOfImage.py, it will create a Tags folder in the desktop and extract the tags inside that folder.
(this is work in progress.)

Part #2 OCR detection
Execute main.py, from the Menu "file" open the image

Part #3 Auto-Correction of the OCR data
work in progress
(wrong words are marked with red box)
corpus is build using the script on corpusBuilder.py, and the output data is used to detect scientific names

Part #4 Manual-Correction of the OCR data
Just click on any word shown, and update the value as needed.

Part #5 Classification
Automatic classification is  in progress
User is now able to manually classify the detected words. below is sample output
######### Classified Information #########
Description: FLORA OF MISSOURI 
Scientific Name: Camstozora shyhkyllae 
Location: ( L. ) Link. Chere Coeur Lake NO 
Registration Number: No. 1623 
Date: april 10, 1986 
Collector: JULIAN A. STEYERMARK, COLLECTOR 


#Color code(will be updated as needed)
Red: OCR detected a word that is not present in the dictionary
Green: OCR value and replacement are same
Yellow: User manually updated the value.

#Scientific Name Detection
a server is created which would use Trie search algorithm to find the closest match
when application opens, it tires to connect with server (SNS), 
if SNS server is down, it will create local engine to detect scientific words
Local engine can be any one of three,
1. Trie fastest engine when searching
2. Fuzzy fastest when loading the dictionary, but slower when searching
3. Enchant medium when searching.

To avoid the situation, when application can be closed and open multiple times, and do not want to load the dictionary each time, a server can run continuesly
execute the server by running "startSnsServer.py"
if server is used to detect the scientific words, it will show the client-server communication in the console!


