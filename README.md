# Handwriting Transcription for Herbarium Sheet Labels 

This project is designed to research possibilities for automated or semiautomated transcription of herbarium sheet labels (and all text), both handwritten and typed.
___
## Environment Setup
1. Create a Python 3.8 virtual environment. For example, in Anaconda Terminal:
    - `conda create -n <envname> python=3.8 pip`
    - `conda activate <envname>`
    - `pip install -r requirements.txt`
    - Install the needed nltk corpora by running the `requirements-nltk.py` script. For example, in the same Anaconda window, execute:
        - `python requirements-nltk.py`
2. Set up Google Cloud Vision credentials.
    - Download your Google Cloud Service Account Key. Save the file in this main directory, e.g. `service_account_token.json`. (See [Google Cloud help center](https://cloud.google.com/docs/authentication/production#cloud-console) for more guidance.)
    - Copy the `Configuration-plain.cfg` file as `Configuration.cfg`.
        - Edit the file to add the name of your service account token (in the `GOOGLE_CLOUD_VISION_API` section, under `serviceAccountTokenPath={name-of-your-service-account-token}`.
        - Update any other settings if desired.
3. Set up Amazon Web Services credentials.
    - Set up your Amazon Web Services account and store your credentials in the proper location
      (this location is OS-dependent, please consult the 
      [AWS documentation](https://docs.aws.amazon.com/textract/latest/dg/setup-awscli-sdk.html))
      for full instructions).

___
## Suggested Workflows

#### Creating a comparison between OCR platforms
*Currently available: Google Cloud Vision, Amazon Web Services Textract)*

1. Prepare the images and ground truth information.
    1. Download an occurrence file from the [Fern Portal](https://pteridoportal.org/) which 
       already contains human-created transcriptions of the label text.
       1. As an authenticated user, click the "Crowdsource", and 
           click the pencil icon next to the desired dataset.
       1. Click the "Exporter" tab. Create a search query (e.g. 
           *Collector/Observer CONTAINS Steyermark*). 
       1. For "Processing Status" select "Reviewed."
       1. For "Structure," select "Darwin Core."
       1. For "Data Extensions," deselect "include Determination History"
          and select "include Image Records."
       1. (Compression should already be checked, and "CSV" selected for file format.)
       1. For "Character Set" select "ISO-8859-1 (western)."
       1. Click "Download Records" button.
    1. Place the downloaded ZIP file in your working directory, and run the script 
       `utilities\join_occurrence_file_with_image_urls.py`, pointing to the ZIP file.
    1. 
    


---
## Scripts

### compare_ocr_cloud_platforms.py
Use this program to process each image file with multiple cloud-based OCR platforms, to directly compare results.
Currently, this program compares Google Cloud Vision and Amazon Web Services Textract.

**Input**:
- A single image file on the local computer
- OR
- A folder of image files on the local computer

**Outputs**:
- If a response object has not already been generated for this image, the request is sent to the 
  cloud service and then saved (as a `pickle`) in the `ocr_responses` folder for later use.
  (One sub-folder is created for each cloud service, with the naming convention `<barcode>.pickle`).
    - *Note*: For the response search to work properly, the first part of an image filename should be
      the image barcode (or some other unique, non-overlapping ID).
      Images downloaded from the Fern Portal (Pteridoportal) already follow this naming convention.
- The complete text output is saved to a CSV file with one row per image. 
   Each line/paragraph (AWS/GCV, respectively) is followed by a line break (`\n`) character.
   (Note that both of these OCR platforms use extended character sets, e.g. latin letters with diacritics.)
- One copy of each image per cloud platform, with annotations based on the OCR. Currently, the program
   is configured to draw:
   - a thin black box around each line/paragraph
   - a green line at the start of each detected word
   - a red line at the end of each detected word

**Example usage**:

`python compare_ocr_cloud_platforms.py oneimage-label.jpg`

**Example output**:
All are saved in the folder `./test_results/cloud_compare-<datestamp/`.
1. Image saved as `oneimage-annotated<datestamp>.jpg` in sub-folder `aws`.
2. Image saved as `oneimage-annotated<datestamp>.jpg` in sub-folder `gcv`.
3. CSV file `comparison.csv` :

| gcv_response                       | aws_response                       |
| -----------------------------------|----------------------------------- |
| 31160 PLANTS OF GUATEMALA ...(etc) | 31160 PLANTS OF GUATEMALA ...(etc) |
| ...                                | ...                                |

---
### utilities/join_occurrence_file_with_image_urls.py
Using the downloaded occurrence information (as a ZIP file), this program joins
the full occurrence record with the URL of the high resolution image for each row.

**Input**:
- A ZIP file exported from the [Fern Portal](https://pteridoportal.org/). See workflows above for detailed information.

**Output**:
- The results are saved as a new file in the same directory, with the file name
  `occurrence_file_with_images-[timestamp].csv`. 
  This file is the same as the `occurrences.csv` file, with one additional 
  column, `image_url`, taken from the `images.csv` file. 

**Example usage**:


`python utilities/join_occurrence_file_with_image_urls resources/occur_download.zip`


**Example output**:

Saved in `resources/` as `occurrence_file_with_images-2021_04_14-10_58_13.csv` :
  
| id  | ... | reference                                                                       | image_url                                                         |
|-----|-----|---------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 939 | ... | https://www.pteridoportal.org/portal/collections/individual/index.php?occid=939 | http://fm-digital-assets.fieldmuseum.org/1112/912/C0611042F.jpg |
| 952 | ... | https://www.pteridoportal.org/portal/collections/individual/index.php?occid=952 | http://fm-digital-assets.fieldmuseum.org/1105/971/C0604755F.jpg |

---
### taxon_binomial_name_matching.py
This program uses fuzzy match ratio to find the closest name match based on
[World Flora Online](http://www.worldfloraonline.org/downloadData).
 
**Input**:
- A text file of generated binomial names (genus and species), e.g. as generated by OCR,
  with one name per line.

**Output**:
- The results are saved as with the name `[original_filename]-name_match_results.csv` in the
  current working directory. 
- This file has 3 columns:
    1. The original text string from the input file
    1. A list showing the highest ratio match (or multiple options, if tied)
    1. The highest ratio achieved by those matches (an integer value 0-100, representing %)

**Example usage**:

`python nameresolution/taxonomic_name.py file_of_OCR_names_to_match.txt`


**Example output**:

Saved as *file_of_OCR_names_to_match-name_match_results.csv* :
     
| search_query            | best_matches               | best_match_ratio |
|-------------------------|----------------------------|------------------|
| Adiantum pedatum        | ['adiantum pedatum']       | 100              |
| Polypodium virginiangan | ['polypodium virginianum'] | 89               |

___

## Credits
This project is being developed for the
[Grainger Bioinformatics Center](https://sites.google.com/fieldmuseum.org/bioinformatics/home) at
the [Field Museum](https://www.fieldmuseum.org/) by Beth McDonald ([@emcdona1](https://github.com/emcdona1)),
under the guidance of Dr. Rick Ree and Dr. Matt von Konrat.

Original codebase for a GUI system with a local database developed by 
Keshab Panthi ([@kpanthi](https://github.com/kpanthi)), Northeastern Illinois University.