# OCRProject

#Setup
1. create virtual environment to run the project, pip3 install -r requirements.txt
    sample: from terminal
        a. pip3 install virtualenv
        b. mkdir "myEnvDir"
        c. cd "myEnvDir"
        d. virtualenv "myEnv"
        e. source myEnv/bin/activate
        f. pip3 install -r requirements.txt (in the download code we should have this file.)
2. Open and edit Configuration.cfg file as needed
3. Open CreateDb.sql, CreateSPs.sql and CreateTables.sql in mysql and execute them to create the database or. Make sure to have correct information.
4. Execute python3 BuildPlantDictionary.py to build the plant dictionary (do not create new, as it takes a lot of time to build)

#Execution
1. python3 Start_SNS_Server.py (it will start a SNS server which will provide service to suggest plant's scientific names)
2. python3 main.py (it will lunch the application, which will use the server created on above step, if the server is not present/ready, it will create local search engine.)

#Usage
1. File >> Process Tag (As is)
   - To process the image file from a local computer without cropping.
2. File >> Extract and Process Image with Tag
   - To crop and process the Tag from given local image.
3. File >> Extract and Process Image url
   - To crop and process the Tag from given image url or image path.
4. Batch Tag Extraction >> Folder Containing Images
    - To crop and process multiple images inside the local folder.
5. Batch Tag Extraction >> Text File With Urls of Images
    - To crop and process multiple images from the urls provided inside the given text file.
6. Batch Tag Extraction >> Stop Batch Processing
    - To break the batch processing, Please note the last file in progress will be processed before the break.
    
    
#Workflow
1. Image will be sent to the Google cloud vision API to extract OCR data
2. Received OCR information will have the location of the words as well.
3. Based upon the location, Registration numbers, Title, Collector, Dates will be classified.
4. Remaining words will be analyzed to check if any of them is Scientific Names, (The words would get compared against the plant dictionary and closest match would replace the word if it is incorrect)
5. All other remaining data will be classified as Location
6. The classified data would be sent to database to store
7. UI will load the image from the database and show the classified information.
8. User will have an option to delete the tag from the left panel with a right click.
9. User will have ability to update any information provided by clicking on the words on the image shown.

#OCR Data correction
1. To correct the regular words, enchant spell checker is used. Any incorrect word is replaced by the suggested word with the least levenshtein distance.
2. To correct the scientific words, Trie plant dictionary is used. Where all words are visited until they exceed the maximum given levenshtein distance. maximum levenshtein distance is dynamically calculated with the following formula
   - maxCost = min((len(word) // 3) + 1, 8)

# WIP
1. order of which words to find first,
2. using natural language processing after enchant to correct the regular words. 
3. modified trie search algorithm to break when exact word is found, or the maximum cost exceeded best match earlier.
4. brew install zbar (to detect barcodes)


  
 
 