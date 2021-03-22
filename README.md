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
2. Download your Google Cloud Service Account Key. Save the file in this main directory, e.g. `service_account_token.json`. (See [Google Cloud help center](https://cloud.google.com/docs/authentication/production#cloud-console) for more guidance.)
3. Copy the `Configuration-plain.cfg` file as `Configuration.cfg`.
    2. Edit the file to add the name of your service account token (in the `GOOGLE_CLOUD_VISION_API` section, under `serviceAccountTokenPath={name-of-your-service-account-token}`.
    3. Update any other settings if desired.
4. (under development) Set up your Amazon Web Services account and store your credentials in the proper location 
   ([documentation link](https://docs.aws.amazon.com/textract/latest/dg/setup-awscli-sdk.html)).

___
## Workflow/Scripts
*under development, 10 March 2021*

### get_image_urls_from_fern_portal.py
- Given an occurrence CSV downloaded from the [Fern Portal](https://pteridoportal.org/),
 this programs the image file URL for each row.
    - If no image is available (likely due to a specimen having protected status), the img_url column will show `None`. 
- The results are saved as `[original_filename]-updated.csv`; this file is the same as the input file (columns `id` through `reference`, 
 but with one additional column. 

**Example usage**: `python get_image_urls_from_fern_portal.py occur_download.csv`

**Example output**, saved as *occur_download-updated.csv*:
  
| id  | ... | references                                                                      | img_url                                                         |
|-----|-----|---------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 939 | ... | https://www.pteridoportal.org/portal/collections/individual/index.php?occid=939 | http://fm-digital-assets.fieldmuseum.org/1112/912/C0611042F.jpg |
| 952 | ... | https://www.pteridoportal.org/portal/collections/individual/index.php?occid=952 | None                                                            |

---
### nameresolution/taxonomic_name.py
- Given a txt file of generated genus/species names (e.g. generated by OCR), use fuzzy matching ratio to find 
 the closest match based on [World Flora Online](http://www.worldfloraonline.org/downloadData).
- The input text file should be given as the first command line argument, e.g.
`python fuzzy_binomial_match.py list_of_names_to_match.txt`
- The results are saved as a CSV file, `[original_filename]-name_match_results.csv`.
 The columns of the CSV are: the name from the input file, a list of the best matches (multiple if a tie), and 
 the ratio achieved by those matches (0-100). 

**Example usage**: `python nameresolution/taxonomic_name.py file_of_OCR_names.txt`

**Example output**, saved as *file_of_OCR_names-name_match_results.csv*:
     
| search_query            | best_matches               | best_match_ratio |
|-------------------------|----------------------------|------------------|
| Adiantum pedatum        | ['adiantum pedatum']       | 100              |
| Polypodium virginiangan | ['polypodium virginianum'] | 89               |

___

## Credits
This project is being developed for the Grainger Bioinformatics Center at the Field Museum.
Code by Beth McDonald ([@emcdona1](https://github.com/emcdona1)), 
developed under the guidance of Dr. Rick Ree and Dr. Matt von Konrat.
Original codebase for a GUI system with local database developed by 
Keshab Panthi ([@kpanthi](https://github.com/kpanthi)), Northeastern Illinois University.