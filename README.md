# OCRProject

Project created by ([@kpanthi](https://github.com/kpanthi)), NEIU.


## Setup
1. Create virtual environment to run the project, using Python 3.8. In Anaconda Terminal:
    - `conda create -n <envname> python=3.8 pip`
    - `conda activate <envname>`
    - `pip install -r requirements.txt`
    - Install the necessary nltk libraries. In Python terminal (type `python`):
        - `import nltk`
        - `nltk.download('punkt')`
        - `nltk.download('averaged_perceptron_tagger')`
        - `nltk.download('maxent_ne_chunker')`
        - `nltk.download('words')`
2. Download your Google Cloud Service Account Key. Save the file in this main directory, e.g. `service_account_token.json`. ([Google Cloud help center](https://cloud.google.com/docs/authentication/production#cloud-console))
3. Copy the `Configuration-plain.cfg` file as `Configuration.cfg`.
    1. Edit the file to add your MySQL database password (in the `[DATABASE]` section, under `password={add-your-MySQL-password-here}`.
    2. Edit the file to add the name of your service account token (in the `GOOGLE_CLOUD_VISION_API` section, under `serviceAccountTokenPath={name-of-your-service-account-token}`.
    3. Update any other settings if desired.
4. From the DatabaseSetupScripts folder, open `CreateDb.sql`, `CreateSPs.sql` and `CreateTables.sql` in mysql and execute them (e.g. in MySQL Workbench) to set up the database.
5. In conda terminal, execute `python BuildPlantDictionary.py` to build the plant dictionary (do not create new, as it takes a lot of time to build).

## Execution
1. In one conda terminal, execute `python Start_SNS_Server.py` (it will start a SNS server which will provide service to suggest plant's scientific names)
2. In a second conda terminal, activate the same environment, and execute `python main.py` (it will launch the application, which will use the server created on above step, if the server is not present/ready, it will create local search engine.)

## Usage Menus 
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
7. Export To Excel File >> Current Tag : Tag Name
    - To export currently displayed tag to the Excel file
8. Export To Excel File >> Tags with import date : date
    - To export the filtered list of tags to excel document
9. Export To Excel File >> Export all Tags  
    - To export all tags in the system to excel document
10. Tools >> Edit Configuration
    - To edit the configuration of the application including the database information.
11. Tools >> Rebuild plant dictionary
    - To rebuild the plant dictionary from the url path specified in the config.
    
## How To 
1. Delete the tag
    - Right click on the tag name on the left panel where the tag list is and click delete. 
2. Update the bar code
    - Right click on the tag name on the left panel where the tag list is and click update barcode. Then provide the barcode and click on update.
3. Update the ocr data and classification of the word.
    - click on the word displayed that you want to update the ocr data, and update

#Excel Exports
- Excel Export will have three tabs with following information
    1. First tab
        a. TagId : system generated tagId in the database.
        b. BarCode : If available barcode of the tag.
        c. Imported Date: The date when the tag got imported.
        
    2. Second tab
        a. TagId : system generated tagId in the database
        b. all other column contain the information detected by OCR and classified by the application.
    
    3. Third tab
        a. BarCode: barcode detected in the image
        b. all other column contain the information found about the barcode from the specified website in the config.
      
    
## Workflow
1. Image will be sent to the Google cloud vision API to extract OCR data
2. Received OCR information will have the location of the words as well.
3. Based upon the location, Registration numbers, Title, Collector, Dates will be classified.
4. Remaining words will be analyzed to check if any of them is Scientific Names, (The words would get compared against the plant dictionary and closest match would replace the word if it is incorrect)
5. All other remaining data will be classified as Location
6. The classified data would be sent to database to store
7. UI will load the image from the database and show the classified information.
8. User will have an option to delete the tag from the left panel with a right click.
9. User will have ability to update any information provided by clicking on the words on the image shown.

## OCR Data correction
1. To correct the regular words, enchant spell checker is used. Any incorrect word is replaced by the suggested word with the least levenshtein distance.
2. To correct the scientific words, Trie plant dictionary is used. Where all words are visited until they exceed the maximum given levenshtein distance. maximum levenshtein distance is dynamically calculated with the following formula
   - maxCost = min((len(word) // 3) + 1, 8)
