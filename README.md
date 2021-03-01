# Handwriting Transcription for Herbarium Sheet Labels 

Project codebase developed for the Grainger Bioinformatics Center at the Field Museum.  Original project groundwork developed by Keshab Panthi ([@kpanthi](https://github.com/kpanthi)), NEIU.


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
    2. Edit the file to add the name of your service account token (in the `GOOGLE_CLOUD_VISION_API` section, under `serviceAccountTokenPath={name-of-your-service-account-token}`.
    3. Update any other settings if desired.

## Execution
*under development, 1 March 2021*
