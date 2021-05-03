# Handwriting Transcription for Herbarium Sheet Labels 

This project is designed to research possibilities for automated or semi-automated 
transcription of herbarium sheet text, both handwritten and typed.
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
## Example Workflows

#### Comparing OCR platforms on analyzing herbarium sheet labels
*Currently available: Google Cloud Vision and Amazon Web Services Textract*

1. **Download the ground truth information for your dataset, plus URLs of the images**.
    1. In a web browser, log into the [Fern Portal](https://pteridoportal.org/) 
       and download an occurrence file, which should contain human-created transcriptions 
       of the herbarium sheet text:
   1. As an authenticated user, click the "Crowdsource", and click the pencil icon 
      next to the desired dataset.
   1. Click the "Exporter" tab. Create a search query (e.g. 
      *Collector/Observer CONTAINS Steyermark*).
       1. For "Processing Status" select "Reviewed." (This ensures that you have ground truth
          data, i.e. transcribed by humans and reviewed by staff, to compare to the OCR.)
       1. For "Structure," select "Darwin Core."
       1. For "Data Extensions," deselect "include Determination History"
          and select "include Image Records."
       1. (Compression should already be checked, and "CSV" selected for file format.)
       1. For "Character Set" select "UTF-8 (unicode)."
       1. Click "Download Records" button.
   1. Place this downloaded ZIP file in your working directory.
1. **Download your image set**.
    1. Run the script `utilities\join_occurrence_file_with_image_urls.py`, pointing to 
       the ZIP file you just downloaded.  A new CSV file 
       (e.g. "occurrence_file_with_images.csv") is created in the same directory. 
    1. Run the script `utilities\download_images_from_csv.py`, pointing to (1) the
       "occurrence_file_with_images.csv" file, and (2) the desired directory for the 
       downloaded image set.
1. **Retrieve and save OCR data for your image set**.
    1. Run the script `gather_ocr_data_from_cloud_platforms.py` pointing to the folder of 
       images downloaded in the previous step.
    1. (To cut down on cloud usage, the program attempts to find already existing
       ocr response objects, and any OCR responses generated will be saved in the 
       `ocr_responses` folder, with one subfolder for each cloud platform.)
    1. The file "occurrence_with_ocr-<yyyy_mm_dd-hh_mm_ss>.csv" will be saved in the folder
       `test_results`.
    1. To generate annotated images for each image and cloud platform, e.g. if you want
       to visualize and manually compare, add a flag 'True' to the script.
       These images are saved within a new subfolder called `cloud_ocr-[yyyy_mm_dd-hh_mm_ss]`.
       (e.g. `python gather_ocr_data_from_cloud_platforms.py images True`)
1. **Compare OCR data to ground truth data**.
    1. Run the script `prep_comparison_data.py` with the "occurrences_with_ocr" file
       generated in the previous step. This script saves 2 new files to the
       `test_results` folder:
        1. The occurrence file with 3 added columns,saved as 
           "occurrence_with_ocr_and_scores-<yyyy_mm_dd-hh-mm-ss>.csv":
            - `labelText` - ground truth data (compiled from the human-created transcriptions
              in the occurrence file) 
            - `awsMatchingScore` - The total "score" for the AWS Textract platform's OCR text
              found in this image. (Roughly, this score gives 1 pt for an exact match, 
              0.5 pt for a 60-99% match, and no points for any match <60%)
            - `gcvMatchingScore` - The total "score" for the GCV platform's OCR text
              found in this image.
        1. A file called "compare_word_by_word-<yyyy_mm_dd-hh_mm_ss>.csv" which shows
           the best OCR match (fuzzy match ratio) for each word in the ground truth text
           (taken from the occurrence file).
    1. (Note: because of the label-finding feature, this script takes roughly 23-30 seconds 
    per image on an average personal computer.)
    


---
## Scripts

### gather_ocr_data_from_cloud_platforms.py
Use this program to send each image file to all available cloud-based platforms, 
for OCR processing.

**Input**:
- A single image file on the local computer
- OR
- A folder of image files on the local computer


**N.B. about file naming and cloud server usage**: To reduce cloud computing costs, 
the program always searches the `ocr_responses` folder for an existing response object before 
sending a query to the cloud service. Queries are stored in the folder with the base of the 
image file name as the name. e.g. The OCR response for `cat-and-dog.jpg` is saved as 
`cat-and-dog.pickle`. If `cat-and-dog.jpg` is run through this script again, it will import the 
pickle (and print a message to the console, *Using previously pickled response object for 
cat-and-dog*).


**Outputs**:
- The response for any new cloud queries are saved in the folder `ocr_responses`, with one
  sub-folder for each cloud service, e.g. `aws` and `gcv`.
- The other outputs are all saved to the `test_results` folder, in a new subfolder called
  `cloud_ocr-[timestamp]`.
- The complete text output is saved as `ocr_texts.csv`, with one row per image. 
  For AWS and GCV respectively, a line break (`\n`) character separates each "line"
  or "paragraph" of OCR data. (Both AWS and GCV will generate extended character sets and 
  non-latin characters, such as latin letters with diacritics, Korean, Arabic, etc.)
- Unless flagged false (see example usage), one copy of each image is generated per cloud 
  platform, with annotations indicating the "words" found by all platforms.
  The program is configured to draw (1) a thin black box around each line/paragraph, (2) 
  a green line at the start of each detected word, and (3) a red line at the end of each 
  detected word.  (This can be adjusted in the `draw_comparison_image` function.)

**Example usage**:

`python gather_ocr_data_from_cloud_platforms.py oneimage.jpg`

`python gather_ocr_data_from_cloud_platforms.py image_folder`

`python gather_ocr_data_from_cloud_platforms.py image_folder True` (Same functionality as the
previous example)

`python gather_ocr_data_from_cloud_platforms.py image_folder false` (Optional second argument
to skip the creation of the annotated images. Case-insensitive, will detect "false", "no", 
or "n".)



**Example output** for `python gather_ocr_data_from_cloud_platforms.py oneimage.jpg`:

Saved in the folder `./test_results/cloud_ocr-<yyyy-mm-dd_hh-mm-ss>/`:
1. Image saved as `oneimage-annotated<datestamp>.jpg` in sub-folder `aws`.
2. Image saved as `oneimage-annotated<datestamp>.jpg` in sub-folder `gcv`.
3. CSV file `ocr_texts.csv` :

| barcode    | gcv                                | aws                                |
| ---------- | -----------------------------------|----------------------------------- |
| C12345678F | 31160 PLANTS OF GUATEMALA ...(etc) | 31160 PLANTS OF GUATEMALA ...(etc) |
| ...        | ...                                | ...                                |

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