import ImageProcessor.image_processor_driver as ipd
import pandas as pd
from configparser import ConfigParser
import os
from google.cloud import vision
import re
import ImageProcessor.image_processor as ip


def main():
    config = Configurator()
    image_list_filename = 'image_list.txt'
    one_image = 'https://pteridoportal.org/imglib/fern/F/C0611/C0611253F_1591198805_web.jpg'
    image_processor = ip.ImageProcessor(config.google_vision_client)
    transcription_results = process_one_image(one_image, image_processor)
    # transcription_results: pd.DataFrame = process_list_of_images(image_list_filename, config.google_vision_client)

    transcription_results = split_gcv_text_at_barcode(transcription_results)

    save_dataframe_to_csv(transcription_results, 'output-test-barcode.csv')


class Configurator:
    def __init__(self):
        config_parser = ConfigParser()
        config_parser.read(r'Configuration.cfg')
        service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
        self.google_vision_client = vision.ImageAnnotatorClient()


def process_one_image(filename: str, image_processor) -> pd.DataFrame:
    list_of_images = [filename]

    # TODO : expected error w/in here -- updating things
    transcription_results = ipd.process_one_image(filename, 1, False, image_processor.client)
    return transcription_results


def process_list_of_images(filename_of_list: str, image_processor) -> pd.DataFrame:
    list_of_images = ipd.process_file_of_urls_into_a_list(filename_of_list)
    df = pd.DataFrame([], columns=['filename', 'gcv_results', 'correction_results'])
    gcv, corrected = image_processor.process_image()
    new_row = pd.DataFrame([[one_path, gcv, corrected]], columns=df.columns)
    df = df.append(new_row)
    transcription_results = ipd.process_images_from_text_file_with_urls(filename_of_list, 1, False,
                                                                        image_processor)
    return transcription_results


def split_gcv_text_at_barcode(df: pd.DataFrame) -> pd.DataFrame:
    barcode = re.compile('[ ]+[Cc][O]?[0-9]+[FH]?[ ]+')

    def extract_barcode(row: pd.Series) -> str:
        matches_list = barcode.findall(row.gcv_results)
        if len(matches_list) == 0:
            return '[no barcode found]'
        else:
            match = matches_list[0]
            return match if type(match) is str else match[0]

    def find_label_based_on_barcode(row: pd.Series) -> str:
        splits = re.split(row.barcode, row.gcv_results, maxsplit=1)
        if len(splits) == 2:
            return splits[1]
        else:
            return splits[0]

    df['barcode'] = df.apply(extract_barcode, axis=1)
    df['label'] = df.apply(find_label_based_on_barcode, axis=1)
    return df


def import_dataframe_from_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df


def save_dataframe_to_csv(transcription_results: pd.DataFrame, filename: str):
    print(transcription_results.head())
    transcription_results.to_csv(filename)


if __name__ == '__main__':
    main()
