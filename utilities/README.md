## Handwriting Transcription
### `utilities` directory


##### Files:
- **data_loader.py**
  - Set of functions to load/save files on the local file system.
      - Load string list from a text file (one line = one item)
      - Load list of files within a directory
      - Pickling/depickling items
      - Open/save cv2 images
      - Download an image from a URL
      - Export a `pd.DataFrame` as a CSV
      - Generate a timestamp
- **data_processor.py**
  - Function to parse a FMNH barcode from within a longer string
  - Function to arrange Cartesian coordinates in a standardized way 
    (clockwise from top left).
- **detect_languages.py**
  - After occurrence files are joined and images are downloaded language detection can be run 
  - This returns a cvs file with the language data
- **language_validation.py**
  - After language detection is run and the labels have been reviewed, you can match the true language to the detected language 
  - Passing in the ground truth occurrence file and the detected language csv will return a csv file with the results of the comparison 
  - This program assumes that the ground truth labels does not exactly match the predicted language labels. If both files are the same length with the same labels in the same order, the function will make unnecessary comparisons (can be fixed later)  
- **join_occurrence_file_with_image_urls.py**
  - After downloading occurrence data from a portal website (in Darwin Core formatting and 
    ISO-8859-1 encoding), this script combines occurrence.csv and images.csv into one file. 
- **download_images_from_csv.py**
  - After running `join_occurrence_file_with_image_urls.py`, this script download the images 
    from URLs to your local computer.
- **quick_crop_labels.py**
  - Script to quickly and roughly crop labels from herbarium specimens (always crops 
    right 1/2 and bottom 1/3 of the image).
- **timer.py**
  - Simple helper script to time and output execution of programs.
- **zooniverse_tools\load_zooniverse_letter_results.py**
  - Use with Zooniverse project "Herbarium Handwriting Transcription" version 1 (transcribing 
    individual letters).  Program uses the classifications export file and cleans/parses the 
    information into a usable format for CNN machine learning use.
- **zooniverse_tools\load_zooniverse_word_results.py**
  - Use with Zooniverse project "Herbarium Handwriting Transcription" version 2 (transcribing 
    whole words).  Program uses the classifications export file and cleans/parses the 
    information into a usable format for CNN+RNN+CTC machine learning use.