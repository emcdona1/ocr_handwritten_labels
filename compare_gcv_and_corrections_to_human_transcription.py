import ImageProcessor.ImageProcessorDriver as ipd
import pandas as pd
import ImageProcessor.InitializeDataFromImage as idfi
from configparser import ConfigParser
import os
from google.cloud import vision

class Configurator:
    def __init__(self):
        config_parser = ConfigParser()
        config_parser.read(r'Configuration.cfg')
        service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
        self.google_vision_client = vision.ImageAnnotatorClient()


def main():
    config = Configurator()
    image_list_filename = 'image_list.txt'
    one_image = 'https://pteridoportal.org/imglib/fern/F/C0611/C0611253F_1591198805_web.jpg'
    # global transcription_results
    transcription_results = pd.DataFrame([], columns=['filename', 'gcv_results', 'correction_results'])
    transcription_results = process_one_image(one_image, config.google_vision_client, transcription_results)
    # transcription_results = process_list_of_images(image_list_filename, google_vision_client, transcription_results)
    save_dataframe_to_csv(transcription_results, 'output-test.csv')


def process_one_image(filename: str, google_vision_client, transcription_results: pd.DataFrame) -> pd.DataFrame:
    gcv, corrected = ipd.ExtractAndProcessSingleImage(filename, 1, False, google_vision_client)
    transcription_results = transcription_results.append(pd.DataFrame([[filename, gcv, corrected]],
                                                                      columns=transcription_results.columns))
    return transcription_results


def process_list_of_images(list_filename: str, google_vision_client, transcription_results: pd.DataFrame) -> pd.DataFrame:
    # args below:
    ## suggestEngine
    ## txt file name
    ## "minimum confidence" -- using his value of 1
    ## and False=don't search for the label, use the whole image)
    ipd.ProcessImagesFromTheUrlsInTheTextFile(list_filename, 1, False, google_vision_client)
    return transcription_results


def save_dataframe_to_csv(transcription_results: pd.DataFrame, filename: str):
    print(transcription_results.head())
    transcription_results.to_csv(filename)


if __name__ == '__main__':
    main()
