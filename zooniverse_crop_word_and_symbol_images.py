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
            # save_image_to_file(gcv_processor.annotator.current_image_to_annotate, image_folder_zooniverse, 'wordbox',
            #                    image_barcode, word['b_idx'], word['p_idx'], word['w_idx'])
            add_word_to_zooniverse_manifest(gcv_processor, word, word_filename)
            gcv_processor.annotator.reset_current_image()

        # list_of_symbols = gcv_processor.get_list_of_symbols()
        # for symbol in list_of_symbols:
        #     gcv_processor.annotator.draw_polygon(symbol['bounding_box'], box_drawing_color)
        #     save_image_to_file(gcv_processor.annotator.current_image_to_annotate, image_folder_zooniverse, 'symbox',
        #                        image_barcode, symbol['b_idx'], symbol['p_idx'], symbol['w_idx'], symbol['s_idx'])
        #     add_symbol_to_zooniverse_manifest(gcv_processor, symbol)
        #     gcv_processor.annotator.reset_current_image()
        #     generate_neural_net_symbol_images(gcv_processor.annotator.current_image_to_annotate, image_barcode,
        #                                       symbol, symbol['b_idx'], symbol['p_idx'], symbol['w_idx'],
        #                                       symbol['s_idx'])
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


def generate_neural_net_symbol_images(image, image_barcode, symbol, b_idx, p_idx, w_idx, s_idx):
    image_of_one_cropped_symbol = crop_image(image, symbol.bounding_box)
    image_filename = save_image_to_file(image_of_one_cropped_symbol, image_folder_nn,
                                        'symbol', image_barcode, b_idx, p_idx, w_idx, s_idx)
    new_letter_row = {'image_of_symbol': image_filename,
                      'gcv_symbol_classification': symbol.text,
                      'barcode': image_barcode,
                      'block_no': b_idx,
                      'paragraph_no': p_idx,
                      'word_no': w_idx,
                      'symbol_no': s_idx
                      }
    global letter_metadata
    letter_metadata = letter_metadata.append(new_letter_row, ignore_index=True)


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


def add_symbol_to_zooniverse_manifest(gcv_processor: GCVProcessor, symbol: dict) -> None:
    """ Add symbol to manifest. """
    new_manifest_row = {'image_of_boxed_letter': gcv_processor.current_image_location,
                        'barcode': gcv_processor.current_image_barcode,
                        'block_no': symbol['b_idx'],
                        'paragraph_no': symbol['p_idx'],
                        'word_no': symbol['w_idx'],
                        '#GCV_identification': symbol['text']
                        }
    global zooniverse_manifest
    zooniverse_manifest = zooniverse_manifest.append(new_manifest_row, ignore_index=True)


def crop_image(image_to_crop: np.ndarray, bounding_box) -> np.ndarray:
    """ Subsets the image based on the bounding box, and returns a deep copy of the crop. """
    x_values = []
    y_values = []
    max_x_value = image_to_crop.shape[1]
    max_y_value = image_to_crop.shape[0]
    for vertex in bounding_box.vertices:
        # GCV has returned some negative X values, e.g. for C0601389F-label.jpg
        x_value_within_valid_range = min(max(0, vertex.x), max_x_value)
        y_value_within_valid_range = min(max(0, vertex.y), max_y_value)
        x_values.append(x_value_within_valid_range)
        y_values.append(y_value_within_valid_range)
    x_min = sorted(x_values)[0]
    x_max = sorted(x_values)[-1]
    y_min = sorted(y_values)[0]
    y_max = sorted(y_values)[-1]
    # ndarray is height x width x color space
    new_cropped_image = copy.deepcopy(image_to_crop[y_min:y_max + 1, x_min:x_max + 1, :])
    return new_cropped_image


def crop_to_label(gcv_processor: GCVProcessor, bounding_box: list) -> np.ndarray:
    x_min = bounding_box[0][0]
    x_max = bounding_box[1][0]
    y_min = bounding_box[1][1]
    y_max = bounding_box[2][1]
    return gcv_processor.annotator.cropped_image(x_min, x_max, y_min, y_max)


def save_image_to_file(image_to_save: np.ndarray, save_folder: str, image_type_prefix: str,
                       image_barcode: str, b_idx: int, p_idx: int, w_idx: int, s_idx=-1) -> str:
    """ Assumes save_folder exists."""
    filename = image_type_prefix + '-' + image_barcode + '-b' + str(b_idx) + 'p' + str(p_idx) \
               + 'w' + str(w_idx) + ('s' + str(s_idx) if s_idx >= 0 else '') + '.jpg'
    file_path = os.path.join(save_folder, filename)
    cv2.imwrite(file_path, image_to_save)
    return filename


def clean_and_save_manifests():
    zooniverse_manifest['block_no'] = zooniverse_manifest['block_no'].astype(int)
    zooniverse_manifest['paragraph_no'] = zooniverse_manifest['paragraph_no'].astype(int)
    zooniverse_manifest['word_no'] = zooniverse_manifest['word_no'].astype(int)
    # zooniverse_manifest['symbol_no'] = zooniverse_manifest['symbol_no'].astype(int)
    zooniverse_manifest.reindex(columns=['image_of_boxed_letter', 'barcode',
                                         'block_no', 'paragraph_no', 'word_no',  # 'symbol_no',
                                         '#GCV_identification']) \
        .to_csv(os.path.join(image_folder_zooniverse, 'zooniverse_manifest.csv'), index=False, encoding='UTF-8')

    # letter_metadata['block_no'] = letter_metadata['block_no'].astype(int)
    # letter_metadata['paragraph_no'] = letter_metadata['paragraph_no'].astype(int)
    # letter_metadata['word_no'] = letter_metadata['word_no'].astype(int)
    # letter_metadata['symbol_no'] = letter_metadata['symbol_no'].astype(int)
    # letter_metadata.reindex(columns=['image_of_symbol', 'gcv_symbol_classification', 'barcode',
    #                                  'block_no', 'paragraph_no', 'word_no', 'symbol_no']) \
    #     .to_csv(os.path.join(image_folder_nn, 'symbol_metadata.csv'), index=False, encoding='UTF-8')


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
