# OCRProject

#Execution
 from terminal navigate to main.py and execute following command
 python3 main.py
 it will open GUI window, than open the image file that you want
 
 
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

Part #4 Manual-Correction of the OCR data
Just click on any word shown, and update the value as needed.

Part #5 Classification
Automatic classification is  in progress
User is now able to manually classify the detected words. below is sample output
######### Classified Information #########
Address: Ranken Cave 8 miles St. Valley Park, St. Louis 
Collector: JULIAN A. STEYERMARK 
Date: June 13, 1986 
Registration Number: 1620 
Scientific Name: Asplenium platyneuron 




Color code
(will be updated as needed)
Red: OCR detected a word that is not present in the dictionary
Green: OCR value and replacement are same
Yellow: User manually updated the value.

#sample Execution
1. command line: python3 main.py

2. Open the file from menu (it will autocorrect data and classify)

3. By clicking on any word you can manually correct the data and it's classification
