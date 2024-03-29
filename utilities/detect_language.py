import sys
from utilities.data_loader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from imageprocessor import GCVProcessor
import pandas as pd


def main(occurrence_file: str, folder_or_image_path: str):
    list_of_images = load_file_list_from_filesystem(folder_or_image_path)
    print("Running language detection on", len(list_of_images), "labels...")
    processors = GCVProcessor()
    occurrence = pd.read_csv(occurrence_file, encoding='UTF-8')
    language_dataframe = pd.DataFrame(data=None, index=None, columns=['Barcode', 'Document Language',
                                                                      'Detected Languages', 'Confidence of Detection'])

    for i, image in enumerate(list_of_images):
        processors.load_image_from_file(image)
        document_language = str(processors.document_level_language)
        top_languages = str(processors.languages_found)

        barcodes = str(occurrence['catalogNumber'][i])
        element = [barcodes, document_language, top_languages]
        language_dataframe.loc[i] = element

    time = get_timestamp_for_file_saving()
    language_dataframe.to_csv('detect_language_data' + time + '.csv')
    print("Finished: saving to " + 'detect_language_data' + time + '.csv')


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Must use 2 arguments: 1) either an image file or a directory of images, ' + \
                                    '2) the location of the occurrence_with_image_urls file, '
    folder_or_image_file = sys.argv[1]
    occur = sys.argv[2]
    main(occur, folder_or_image_file)
