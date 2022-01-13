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
    list_of_images: list = load_list_of_images()

    for one_image in list_of_images:
        gcv_processor.load_image_from_file(one_image)
        image_barcode = gcv_processor.current_image_barcode
        print('%s loaded.' % one_image, sep='\t | \t')

        list_of_words = gcv_processor.get_list_of_words(label_only=True)
        for word in list_of_words:
            gcv_processor.annotator.draw_polygon(word['bounding_box'], box_drawing_color)
            cropped_image = crop_to_label(gcv_processor, gcv_processor.current_label_location)
            word_filename = save_image_to_file(cropped_image, image_folder_zooniverse, 'wordbox',
                                               image_barcode, word['b_idx'], word['p_idx'], word['w_idx'])
            add_word_to_zooniverse_manifest(gcv_processor, word, word_filename)
            gcv_processor.annotator.reset_current_image()

        print('%s completed.' % one_image)
    clean_and_save_manifests()


def load_list_of_images() -> list:
    if os.path.isdir(folder_or_image_file):
        list_of_images = os.listdir(folder_or_image_file)
        list_of_images = [os.path.join(folder_or_image_file, filename) for filename in list_of_images]
        list_of_images = [item for item in list_of_images if not os.path.isdir(item)]  # remove subdirectories
    elif os.path.isfile(folder_or_image_file):
        list_of_images = [folder_or_image_file]
    else:
        raise FileNotFoundError('%s is neither a directory nor a file.' % folder_or_image_file)
    return list_of_images


def add_word_to_zooniverse_manifest(gcv_processor: GCVProcessor, word: dict, word_filename: str) -> None:
    """ Add word to manifest. """
    new_manifest_row = {'image_of_boxed_letter': word_filename,
                        'barcode': gcv_processor.current_image_barcode,
                        'block_no': word['b_idx'],
                        'paragraph_no': word['p_idx'],
                        'word_no': word['w_idx'],
                        '#GCV_identification': word['text']
                        }
    global zooniverse_manifest
    zooniverse_manifest = zooniverse_manifest.append(new_manifest_row, ignore_index=True)


def save_image_to_file(image_to_save: np.ndarray, save_folder: str, image_type_prefix: str,
                       image_barcode: str, b_idx: int, p_idx: int, w_idx: int) -> str:
    """ Assumes save_folder exists."""
    filename = image_type_prefix + '-' + image_barcode + '-b' + str(b_idx) + 'p' + str(p_idx) \
               + 'w' + str(w_idx) + '.jpg'
    file_path = os.path.join(save_folder, filename)
    cv2.imwrite(file_path, image_to_save)
    return filename


def clean_and_save_manifests():
    zooniverse_manifest['block_no'] = zooniverse_manifest['block_no'].astype(int)
    zooniverse_manifest['paragraph_no'] = zooniverse_manifest['paragraph_no'].astype(int)
    zooniverse_manifest['word_no'] = zooniverse_manifest['word_no'].astype(int)
    zooniverse_manifest.reindex(columns=['image_of_boxed_word', 'barcode',
                                         'block_no', 'paragraph_no', 'word_no',
                                         '#GCV_identification']) \
        .to_csv(os.path.join(image_folder_zooniverse, 'zooniverse_manifest.csv'), index=False, encoding='UTF-8')


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    image_folder_zooniverse = 'processed_images_zooniverse'
    # image_folder_nn = 'processed_images_nn'
    if not os.path.exists(image_folder_zooniverse):
        os.mkdir(image_folder_zooniverse)
    # if not os.path.exists(image_folder_nn):
    #     os.mkdir(image_folder_nn)

    box_drawing_color = (240, 17, 17)  # blue
    main()
