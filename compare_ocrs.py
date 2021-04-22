import sys
import os
import numpy as np
import prep_comparison_data
import calculate_changes


def main(occurrence_filepath: str, ocr_text_filepath: str, image_folder: str):
    analysis = prep_comparison_data.main(occurrence_filepath, ocr_text_filepath)
    calculate_changes.main(analysis, 150)


if __name__ == '__main__':
    assert len(sys.argv) == 4, 'Provide 3 arguments: filepath for 1 occurrence' + \
                              ' (can be occurrence_with_images file), ' + \
                              'filepath for 1 CSV file with the headers "barcode", "aws", and "gcv" to compare,' +\
                              'and filepath of the folder of images.'
    occur_file = sys.argv[1]
    ocr_texts = sys.argv[2]
    images_folder = sys.argv[3]
    # if len(sys.argv) == 4:

    main(occur_file, ocr_texts, images_folder)
