import sys
import os
import imageprocessor
from utilities.data_loader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from imageprocessor import ImageProcessor, GCVProcessor
import pandas as pd


def main(occurrence_file: str, folder_or_image_path: str):
    list_of_images = load_file_list_from_filesystem(folder_or_image_path)
    processors = GCVProcessor()
    occurrence = pd.read_csv(occurrence_file, encoding='UTF-8')
    language_dataframe = pd.DataFrame(data=None, index=None, columns=['Barcode', 'Document Language', 'Detected Languages',
                                                          'Confidence of Detection'])

    for im in range(len(list_of_images)):
        processors.load_image_from_file(list_of_images[im])

        document_langugae = str(processors.document_level_language)
        top_languages = str(processors.top_languages)
        top_confidences = str(processors.top_confidence)

        barcodes = str(occurrence['catalogNumber'][im])
        element = [barcodes, document_langugae, top_languages, top_confidences]
        language_dataframe.loc[im] = element

    time = get_timestamp_for_file_saving()
    language_dataframe.to_csv('detect_language_data' + time + '.csv')
    print("saving to " + 'detect_language_data' + time + '.csv' )


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Must use 2-3 arguments: 1) either an image file or a directory of images, ' + \
                                    '2) the location of the occurrence_with_image_urls file, '
    folder_or_image_file = sys.argv[1]
    occur = sys.argv[2]
    main(occur, folder_or_image_file)
