from configparser import ConfigParser
import os
from google.cloud import vision
import ImageProcessor.image_processor as ip
from urllib.request import urlopen
import numpy as np
import cv2
import pickle


def setup() -> ip.ImageProcessor:
    config_parser = ConfigParser()
    config_parser.read(r'Configuration.cfg')
    service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
    google_vision_client = vision.ImageAnnotatorClient()
    image_processor = ip.ImageProcessor(google_vision_client)
    return image_processor


def create_folders_for_images(save_path: str, base_image_name_for_folders: str, symbol_folder: str) -> (str, str):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    folder_for_this_image = os.path.join(save_path, base_image_name_for_folders)
    if not os.path.exists(folder_for_this_image):
        os.mkdir(folder_for_this_image)
    folder_for_these_symbols = os.path.join(folder_for_this_image, symbol_folder)
    if not os.path.exists(folder_for_these_symbols):
        os.mkdir(folder_for_these_symbols)
    return folder_for_this_image, folder_for_these_symbols


def analyze_image(image_uri, image_processor) -> vision.types.AnnotateImageResponse:
    print('Processing: ' + image_uri)
    image = vision.types.Image()
    image.source.image_uri = image_uri
    response = image_processor.client.document_text_detection(image=image)
    return response


def open_image_in_cv2(one_image):
    if 'http' in one_image:
        resp = urlopen(one_image)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image_to_draw_on = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        image_to_draw_on = cv2.imread(one_image)
    return image_to_draw_on


def draw_boxes(image: np.ndarray, bounding_box: vision.types.BoundingPoly, color: tuple) -> None:
    """Draw a border around the image using the hints in the vector list."""
    cv2.line(image, (bounding_box.vertices[0].x, bounding_box.vertices[0].y),
             (bounding_box.vertices[1].x, bounding_box.vertices[1].y), color, 1)
    cv2.line(image, (bounding_box.vertices[1].x, bounding_box.vertices[1].y),
             (bounding_box.vertices[2].x, bounding_box.vertices[2].y), color, 1)
    cv2.line(image, (bounding_box.vertices[2].x, bounding_box.vertices[2].y),
             (bounding_box.vertices[3].x, bounding_box.vertices[3].y), color, 1)
    cv2.line(image, (bounding_box.vertices[3].x, bounding_box.vertices[3].y),
             (bounding_box.vertices[0].x, bounding_box.vertices[0].y), color, 1)


def crop_image(image_to_crop: np.ndarray, bounding_box: vision.types.BoundingPoly) -> np.ndarray:
    x_values = []
    y_values = []
    for vertex in bounding_box.vertices:
        x_values.append(vertex.x)
        y_values.append(vertex.y)
    x_min = sorted(x_values)[0]
    x_max = sorted(x_values)[-1]
    y_min = sorted(y_values)[0]
    y_max = sorted(y_values)[-1]
    # ndarray is height x width x colorspace
    return image_to_crop[y_min:y_max + 1, x_min:x_max + 1, :]


def pickle_an_object(obj_to_pickle, base_image_name_for_folders: str, save_directory: str) -> None:
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    filename = base_image_name_for_folders + '_gcv.pickle'
    with open(os.path.join(save_directory, filename), 'wb') as file:
        pickle.dump(obj_to_pickle, file)


def load_gcv_response_from_pickle(directory: str, file_name: str) -> vision.types.AnnotateImageResponse:
    with open(os.path.join(directory, file_name), 'rb') as file:
        response_object = pickle.load(file)
    return response_object


def save_word_image_to_file(save_folder: str, base_image_name_for_folders: str, image_to_save: np.ndarray,
                            b_idx: int, p_idx: int, w_idx: int) -> None:
    """ Assumes save_folder exists."""
    filename = base_image_name_for_folders + '_boxed-word_block' + str(b_idx) + '_para' + str(p_idx) + \
               '_word' + str(w_idx) + '.jpg'
    file_path = os.path.join(save_folder, filename)
    cv2.imwrite(file_path, image_to_save)


def save_symbol_image_to_file(save_folder: str, base_image_name_for_folders: str, image_to_save: np.ndarray,
                              b_idx: int, p_idx: int, w_idx: int, s_idx: int) -> None:
    """ Assumes save_folder exists."""
    filename = base_image_name_for_folders + '_one-symbol_block' + str(b_idx) + '_para' + str(p_idx) + \
               '_word' + str(w_idx) + '_sym' + str(s_idx) + '.jpg'
    file_path = os.path.join(save_folder, filename)
    cv2.imwrite(file_path, image_to_save)


def main():
    image_processor = setup()
    pickle_folder = 'gcv_responses'
    image_folder = 'processed_images'
    symbol_folder = 'symbols'

    one_image = 'https://pteridoportal.org/imglib/fern/F/C0611/C0611253F_1591198805_web.jpg'
    base_image_name_for_folders = os.path.basename(one_image).split('.')[0]
    base_image_name_for_folders = base_image_name_for_folders.split('_')[0]
    # gcv_response = analyze_image(one_image, image_processor)
    gcv_response = load_gcv_response_from_pickle('gcv_responses', 'C0611253F.pickle')
    # pickle_an_object(gcv_response, base_image_name_for_folders, pickle_folder)

    folder_for_saved_images, folder_for_saved_symbols = \
        create_folders_for_images(image_folder, base_image_name_for_folders, symbol_folder)
    word_color = (240, 17, 17)  # red

    page = gcv_response.full_text_annotation.pages[0]  # there's only one page in an image file
    for b_idx in range(14, 16, 1):  # 20, 1):
        paragraphs = page.blocks[b_idx].paragraphs
        for p_idx, paragraph in enumerate(paragraphs):
            for w_idx, word in enumerate(paragraph.words):
                image_to_draw_on = open_image_in_cv2(one_image)
                draw_boxes(image_to_draw_on, word.bounding_box, word_color)
                save_word_image_to_file(folder_for_saved_images, base_image_name_for_folders,
                                        image_to_draw_on, b_idx, p_idx, w_idx)
                letters = ''
                symbol_images = []
                for s_idx, symbol in enumerate(word.symbols):
                    image_to_extract_letters = open_image_in_cv2(one_image)
                    cropped_symbol_image = crop_image(image_to_extract_letters, symbol.bounding_box)
                    save_symbol_image_to_file(folder_for_saved_symbols, base_image_name_for_folders,
                                              cropped_symbol_image, b_idx, p_idx, w_idx, s_idx)
                    symbol_images.append(cropped_symbol_image)
                    letters = letters + symbol.text
                # todo: create composite image of symbols for Zooniverse?
                # todo: save letters to a metadata CSV -- which can be human read AND used as a manifest for ZV


if __name__ == '__main__':
    main()
