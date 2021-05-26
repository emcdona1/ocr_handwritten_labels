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
    if not os.path.exists(pickle_folder):
        os.mkdir(pickle_folder)
    if not os.path.exists(image_folder_zooniverse):
        os.mkdir(image_folder_zooniverse)
    if not os.path.exists(image_folder_nn):
        os.mkdir(image_folder_nn)

    gcv_processor = GCVProcessor()
    list_of_images: list = load_list_of_images()

    for one_image in list_of_images:
        image_barcode: str = extract_barcode_from_image_name(one_image)
        print('%s loaded.' % one_image, sep='\t | \t')
        gcv_processor.load_image_from_file(one_image)

        list_of_words = gcv_processor.get_list_of_words()
        for word in list_of_words:
            gcv_processor.annotator.draw_polygon(word['bounding_box'], box_drawing_color)
            save_image_to_file(gcv_processor.annotator.current_image_to_annotate, image_folder_zooniverse,
                               'wordbox', image_barcode, word['b_idx'], word['p_idx'], word['w_idx'])
            gcv_processor.annotator.reset_current_image()
        # page = gcv_response.full_text_annotation.pages[0]  # there's only one page in an image file
        # for b_idx, block in enumerate(page.blocks):
        #     for p_idx, paragraph in enumerate(block.paragraphs):
        #         for w_idx, word in enumerate(paragraph.words):
        #             word_filename = ''
        #             for s_idx, symbol in enumerate(word.symbols):
        #                 generate_neural_net_symbol_images(image_to_draw_on, image_barcode, symbol,
        #                                                   b_idx, p_idx, w_idx, s_idx)
        #                 word_filename = generate_symbol_zooniverse_images(image_to_draw_on, image_barcode, symbol,
        #                                                                   b_idx, p_idx, w_idx, s_idx,
        #                                                                   '' if s_idx == 0 else word_filename)
        print('Processing complete for %s.' % one_image)
    clean_and_save_manifests()


def load_list_of_images() -> list:
    if os.path.isdir(folder_or_image_file):
        list_of_images = os.listdir(folder_or_image_file)
        list_of_images = [folder_or_image_file + os.path.sep + filename for filename in list_of_images]
        list_of_images = [item for item in list_of_images if not os.path.isdir(item)]  # remove subdirectories
    elif os.path.isfile(folder_or_image_file):
        list_of_images = [folder_or_image_file]
    else:
        raise FileNotFoundError('%s is neither a directory nor a file.' % folder_or_image_file)
    return list_of_images


def extract_barcode_from_image_name(one_image) -> str:
    image_name_without_extension = os.path.basename(one_image).split('.')[0]
    image_barcode = image_name_without_extension.split('_')[0]
    return image_barcode


def analyze_image_in_google_cloud(image_uri: str, image_processor: GCVProcessor) -> \
        vision.types.AnnotateImageResponse:
    image = vision.types.Image()
    if 'http' in image_uri:
        image.source.image_uri = image_uri
    else:
        with io.open(image_uri, 'rb') as image_file:
            image_content = image_file.read()
        image.content = image_content
        # image_contents = cv2.imread(image_uri)

    response = image_processor.client.document_text_detection(image=image)
    if response.error.message == '':
        return response
    else:
        print(response.error.message)
        exit(0)


def pickle_an_object(save_directory: str, base_image_name: str, obj_to_pickle) -> None:
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    filename = base_image_name + '.pickle'
    with open(os.path.join(save_directory, filename), 'wb') as file:
        pickle.dump(obj_to_pickle, file)


def load_gcv_response_from_pickle(directory: str, file_name: str) -> vision.types.AnnotateImageResponse:
    with open(os.path.join(directory, file_name), 'rb') as file:
        response_object = pickle.load(file)
    return response_object


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


def generate_zooniverse_images(image, image_barcode, word, symbol, b_idx, p_idx, w_idx, s_idx,
                               word_filename: str) -> str:
    """ **updated v2** Creates copy of provided image, saves full image of label (w/ one boxed symbol) to disk,
    and adds a row to the manifest."""
    whole_image = copy.deepcopy(image)
    image_with_one_symbol_boxed = draw_box(whole_image, symbol.bounding_box, box_drawing_color)
    image_filename = save_image_to_file(image_with_one_symbol_boxed,
                                        image_folder_zooniverse, 'symbox', image_barcode,
                                        b_idx, p_idx, w_idx, s_idx)

    new_manifest_row = {'image_of_boxed_letter': image_filename,
                        'barcode': image_barcode,
                        'block_no': b_idx,
                        'paragraph_no': p_idx,
                        'word_no': w_idx,
                        'symbol_no': s_idx,
                        '#GCV_identification': symbol.text
                        }
    global zooniverse_manifest
    zooniverse_manifest = zooniverse_manifest.append(new_manifest_row, ignore_index=True)
    return word_filename


def open_image_in_cv2(one_image) -> np.ndarray:
    if 'http' in one_image:
        resp = urlopen(one_image)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image_to_draw_on = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        image_to_draw_on = cv2.imread(one_image)
    return image_to_draw_on


def draw_box(image: np.ndarray, bounding_box: vision.types.BoundingPoly, color: tuple) -> np.ndarray:
    """Create a deep copy of the image, draw a square using the bounding box and color (1 px width),
    and return the new image."""
    image_to_draw = copy.deepcopy(image)
    cv2.line(image_to_draw, (bounding_box.vertices[0].x, bounding_box.vertices[0].y),
             (bounding_box.vertices[1].x, bounding_box.vertices[1].y), color, 1)
    cv2.line(image_to_draw, (bounding_box.vertices[1].x, bounding_box.vertices[1].y),
             (bounding_box.vertices[2].x, bounding_box.vertices[2].y), color, 1)
    cv2.line(image_to_draw, (bounding_box.vertices[2].x, bounding_box.vertices[2].y),
             (bounding_box.vertices[3].x, bounding_box.vertices[3].y), color, 1)
    cv2.line(image_to_draw, (bounding_box.vertices[3].x, bounding_box.vertices[3].y),
             (bounding_box.vertices[0].x, bounding_box.vertices[0].y), color, 1)
    return image_to_draw


def crop_image(image_to_crop: np.ndarray, bounding_box: vision.types.BoundingPoly) -> np.ndarray:
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
    zooniverse_manifest['symbol_no'] = zooniverse_manifest['symbol_no'].astype(int)
    zooniverse_manifest.reindex(columns=['image_of_boxed_letter', 'barcode',
                                         'block_no', 'paragraph_no', 'word_no', 'symbol_no',
                                         '#GCV_identification']) \
        .to_csv(os.path.join(image_folder_zooniverse, 'zooniverse_manifest.csv'), index=False, encoding='UTF-8')

    letter_metadata['block_no'] = letter_metadata['block_no'].astype(int)
    letter_metadata['paragraph_no'] = letter_metadata['paragraph_no'].astype(int)
    letter_metadata['word_no'] = letter_metadata['word_no'].astype(int)
    letter_metadata['symbol_no'] = letter_metadata['symbol_no'].astype(int)
    letter_metadata.reindex(columns=['image_of_symbol', 'gcv_symbol_classification', 'barcode',
                                     'block_no', 'paragraph_no', 'word_no', 'symbol_no']) \
        .to_csv(os.path.join(image_folder_nn, 'symbol_metadata.csv'), index=False, encoding='UTF-8')


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]
    pickle_folder = 'gcv_responses'
    image_folder_zooniverse = 'processed_images_zooniverse'
    image_folder_nn = 'processed_images_nn'
    box_drawing_color = (240, 17, 17)  # blue

    main()
