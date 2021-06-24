# todo: move all of this to other repo, what a mess
import sys
import os
import copy
import pandas as pd
import numpy as np
import cv2
from imageprocessor import GCVProcessor

zooniverse_manifest = pd.DataFrame()
letter_metadata = pd.DataFrame()


def main():
    gcv_processor = GCVProcessor()
    if not os.path.isdir(words_save_folder):
        os.makedirs(words_save_folder)
    # load_and_parse_zooniverse_results()
    # condense_zooniverse_results()
    # clean_zooniverse_results()
    # for row in cleaned_zooniverse_results:
    #     image_id = parse_image_id_from_row()
    #     load_processor_using_image_id()
    #     crop_image_of_word()
    #     save_image_of_word(words_save_folder)
    pass


if __name__ == '__main__':
    folder_of_images = os.path.join('images', )
    zooniverse_results = os.path.join('file_resources', '2021_06_14-herbarium_handwriting_transcription_classifications-words.csv')
    words_save_folder = 'labeled_word_images'
    main()
