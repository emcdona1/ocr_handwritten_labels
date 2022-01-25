import json
from configparser import ConfigParser
import io
import os
from google.cloud import vision
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ConnectionClosedError
from utilities.data_loader import load_pickle, pickle_an_object, open_cv2_image, save_cv2_image
from utilities.data_processor import extract_barcode_from_image_name, arrange_coordinates
from imageprocessor.image_annotator import ImageAnnotator
from typing import List, Tuple, Union
import math
import numpy as np


# from google.cloud.vision_v1 import types
# from google.cloud import vision_v1
# from google.protobuf.json_format import MessageToJson, MessageToDict


class ImageProcessor(ABC):
    def __init__(self, starting_image_path=None):
        self.client = self._initialize_client()
        self.object_save_directory = 'imageprocessor_objects'
        self.name = self._initialize_name_and_save_directory()
        self._current_ocr_response = None
        self.ocr_blocks = None
        self.current_image_used_cropped_image_ocr = False
        self.current_image_location = None
        self.current_image_basename = None
        self.current_image_barcode = None
        self.current_image_height = None
        self.current_image_width = None
        self.current_label_height = None
        self.current_label_width = None
        self.current_label_location = None
        self.annotator = ImageAnnotator(self.name)
        if starting_image_path:
            self.load_image_from_file(starting_image_path)
        self.document_level_language = None
        self.top_languages = None
        self.top_confidence = None

    def __getstate__(self):
        """ Return a copy of the ImageProcessor, without the client instance attribute, for pickling."""
        state = self.__dict__.copy()
        try:
            del state['client']
        except TypeError:
            # 'client' wasn't in state
            pass
        try:
            del state['annotator']
        except TypeError:
            # 'annotator' wasn't in state
            pass
        return state

    def __setstate__(self, state):
        """ Restores ImageProcessor from pickle and initialized the client (which is not pickled). """
        try:
            del state['client']
        except KeyError:
            # 'client' wasn't in state
            pass
        try:
            del state['annotator']
        except KeyError:
            # 'annotator' wasn't in state
            pass
        self.__dict__.update(state)
        self.client = self._initialize_client()

    def pickle_current_image_state(self, name: str):
        path = pickle_an_object(self.object_save_directory, self.current_image_basename, self)
        print('%s ImageProcessor saved to %s, called by %s.' % (self.name, path, name))

    def get_found_word_locations(self) -> List[Tuple]:
        """ Returns a list of (x,y) coordinates, where each point is the corner of a symbol identified by the OCR. """
        word_points = []
        words = self.get_list_of_words()
        for word in words:
            for vertex in word['bounding_box']:
                word_points.append(vertex)
        return word_points

    def find_label_location(self) -> \
            Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """ Searches bottom quadrant of image for highest concentration of symbol bounding boxes
        and returns a set of 4 tuples (top-left, top-right, bottom-right, bottom-left).
        If no OCR data is present, it sets the label location to be the bottom right corner. """
        np_of_points = np.array(self.get_found_word_locations())
        if np_of_points.shape[0] == 0:  # no OCR data found
            upper_left = (self.current_image_width - self.current_label_width,
                          self.current_image_height - self.current_label_height)
            upper_right = (self.current_image_width - 1, self.current_image_height - self.current_label_height)
            lower_right = (self.current_image_width - 1, self.current_image_height - 1)
            lower_left = (self.current_image_width - self.current_label_width, self.current_image_height - 1)
        else:
            max_count = 0
            max_loc = (0, 0)
            for y in range(int(self.current_image_height / 2),
                           self.current_image_height - self.current_label_height + 1):
                for x in range(int(self.current_image_width / 2),
                               self.current_image_width - self.current_label_width + 1):
                    x_values = np_of_points[:, 0]
                    idx_of_valid_x = np.intersect1d(np.where(x_values >= x),
                                                    np.where(x_values < x + self.current_label_width))
                    y_possible = np_of_points[idx_of_valid_x, 1]
                    valid_y_count = np.intersect1d(np.where(y_possible >= y),
                                                   np.where(y_possible < y + self.current_label_height))
                    count = valid_y_count.shape[0]
                    if count >= max_count:
                        max_count = count
                        max_loc = (x, y)
            print('Label found at point %s with %.0f words.' % (str(max_loc), max_count / 4))
            upper_left = max_loc
            upper_right = (max_loc[0] + self.current_label_width, max_loc[1])
            lower_right = (max_loc[0] + self.current_label_width, max_loc[1] + self.current_label_height)
            lower_left = (max_loc[0], max_loc[1] + self.current_label_height)
        self.current_label_location = upper_left, upper_right, lower_right, lower_left
        self.pickle_current_image_state('find label')
        return self.current_label_location

    @abstractmethod
    def _initialize_client(self):
        pass

    def clear_current_image(self):
        self._current_ocr_response = None
        self.ocr_blocks = None
        self.current_image_location = None
        self.current_image_basename = None
        self.current_image_barcode = None
        self.current_image_width = None
        self.current_image_height = None
        self.current_label_width = None
        self.current_label_height = None
        self.current_label_location = None
        self.current_image_used_cropped_image_ocr = False
        self.annotator.clear_current_image()
        self.document_level_language = None
        self.top_languages = None
        self.top_confidence = None

    @abstractmethod
    def _initialize_name_and_save_directory(self) -> str:
        pass

    def load_image_from_file(self, image_path: str, is_label: bool = False) -> None:
        self.clear_current_image()
        self.current_image_location = image_path
        self.current_image_basename = os.path.basename(image_path).split('.')[0]
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        self.annotator.load_image_from_file(image_path)

        # 1. check for imageprocessor_object. If Y, load it and done.
        pickled_object_location = self._search_for_pickled_object()
        if pickled_object_location:
            self._load_from_pickle(pickled_object_location)
        else:
            # 2. If N, send OCR request, pickle the response, and then _parse_ocr_blocks and pickle the IP.
            self._download_ocr()
            self._parse_ocr_blocks()
            if is_label:
                self.current_label_height = self.current_image_height
                self.current_label_width = self.current_image_height
            else:
                self.current_label_height = math.ceil(self.current_image_height * 0.15)
                self.current_label_width = math.ceil(self.current_image_width * 0.365)
            self.pickle_current_image_state('new ocr')

    def load_image_by_barcode(self, barcode: str) -> None:
        pickle_name = f'{barcode}.pickle'
        search_directory = os.listdir(self.object_save_directory)
        if pickle_name in search_directory:
            pickle_path = os.path.join(self.object_save_directory, pickle_name)
            self._load_from_pickle(pickle_path)
        self.annotator.load_image_from_file(self.current_image_location)

    def _load_from_pickle(self, pickle_location: str) -> None:
        loaded = load_pickle(pickle_location)
        self.__setstate__(loaded.__dict__)

    def _search_for_pickled_object(self) -> Union[str, None]:
        pickled_search_name = f'{self.current_image_basename}.pickle'
        search_directory = os.listdir(self.object_save_directory)
        if pickled_search_name in search_directory:
            return os.path.join(self.object_save_directory, pickled_search_name)
        else:
            return None

    @abstractmethod
    def _parse_ocr_blocks(self) -> None:
        pass

    @abstractmethod
    def _download_ocr(self) -> None:
        pass

    def get_list_of_words(self, label_only=False) -> list:
        words = [block for block in self.ocr_blocks if block['type'] == 'WORD']
        if label_only:
            x_min = self.current_label_location[0][0]
            x_max = self.current_label_location[1][0]
            y_min = self.current_label_location[1][1]
            y_max = self.current_label_location[2][1]
            label_words = list()
            for word in words:
                curr_x = (word['bounding_box'][0][0] + word['bounding_box'][1][0]) / 2
                curr_y = (word['bounding_box'][1][1] + word['bounding_box'][2][1]) / 2
                if x_min <= curr_x <= x_max and y_min <= curr_y <= y_max:
                    label_words.append(word)
            words = label_words
        return words

    def get_list_of_lines(self) -> list:
        lines = [block for block in self.ocr_blocks if block['type'] == 'LINE']
        return lines

    def get_full_text(self) -> str:
        if self.ocr_blocks is None:
            print('Warning: no image OCR data has been loaded.')
            return ''
        full_text = ''
        if len(self.ocr_blocks) > 0:
            words = [block for block in self.ocr_blocks if block['type'] == 'WORD']
            for word in words:
                full_text += word['text'] + ' '
        return full_text.strip()

    def get_label_text(self) -> str:
        """ Returns a string of words found by the OCR, but only words for which the upper left point of that word is
                within the label area. """
        if self.ocr_blocks is None:
            print('Warning: no image OCR data has been loaded.')
            return ''
        elif self.current_label_location is None:
            print('No label location set; searching now.')
            self.find_label_location()
        label_text = ''
        if len(self.ocr_blocks) > 0:
            words = [block for block in self.ocr_blocks if block['type'] == 'WORD']
            for word in words:
                top_left = word['bounding_box'][0]
                if self.current_label_location[0][0] <= top_left[0] <= self.current_label_location[1][0]:
                    if self.current_label_location[1][1] <= top_left[1] <= self.current_label_location[2][1]:
                        label_text += word['text'] + ' '
        return label_text.strip()


class GCVProcessor(ImageProcessor):
    def _initialize_client(self):
        config_parser = ConfigParser()
        config_parser.read(r'Configuration.cfg')
        service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
        return vision.ImageAnnotatorClient()

    def _initialize_name_and_save_directory(self) -> str:
        self.name = 'gcv'
        self.object_save_directory = os.path.join(self.object_save_directory, self.name)
        if not os.path.exists(self.object_save_directory):
            os.makedirs(self.object_save_directory)
        return self.name

    def _download_ocr(self) -> None:
        with io.open(self.current_image_location, 'rb') as image_file:
            image_content = image_file.read()
        image = vision.types.Image(content=image_content)
        self.current_ocr_response = self.client.document_text_detection(image=image)

    def _parse_ocr_blocks(self):
        self.current_image_height = self.current_ocr_response.full_text_annotation.pages[0].height
        self.current_image_width = self.current_ocr_response.full_text_annotation.pages[0].width
        self.ocr_blocks = list()
        for b_idx, block in enumerate(self.current_ocr_response.full_text_annotation.pages[0].blocks):
            for p_idx, paragraph in enumerate(block.paragraphs):
                line_text = ''
                for w_idx, word in enumerate(paragraph.words):
                    word_text = ''
                    for s_idx, symbol in enumerate(word.symbols):
                        v = symbol.bounding_box.vertices
                        v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                        vertices, _, _, _, _ = arrange_coordinates(v)
                        self.ocr_blocks.append({'type': 'SYMBOL', 'confidence': symbol.confidence,
                                                'bounding_box': vertices, 'text': symbol.text,
                                                'b_idx': b_idx, 'p_idx': p_idx, 'w_idx': w_idx, 's_idx': s_idx})
                        word_text += symbol.text
                        line_text += symbol.text
                    v = word.bounding_box.vertices
                    v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                    vertices, _, _, _, _ = arrange_coordinates(v)
                    self.ocr_blocks.append({'type': 'WORD', 'confidence': word.confidence,
                                            'bounding_box': vertices, 'text': word_text,
                                            'b_idx': b_idx, 'p_idx': p_idx, 'w_idx': w_idx, 's_idx': None})
                v = paragraph.bounding_box.vertices
                v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                vertices, _, _, _, _ = arrange_coordinates(v)
                self.ocr_blocks.append({'type': 'LINE', 'confidence': paragraph.confidence,
                                        'bounding_box': vertices, 'text': line_text,
                                        'b_idx': b_idx, 'p_idx': p_idx, 'w_idx': None, 's_idx': None})
        block_order = {'LINE': 1, 'WORD': 2, 'SYMBOL': 3}
        self.ocr_blocks = sorted(self.ocr_blocks, key=lambda b: block_order[b['type']])
        self.pickle_current_image_state('parsed GCV ocr')

        response = self.current_ocr_response
        page = response.full_text_annotation

        page_string = str(response.full_text_annotation)
        page_string_split = page_string.split('\n')
        # every 4th line if it contains 'language code'
        # every 5th line if it contains 'confidence'

        language_code = 'language_code: '
        confidence = 'confidence: '
        language_code_list = []
        confidence_list = []
        stop = 'blocks'

        for line in page_string_split:
            if stop in line:
                break
            else:
                if language_code in line:
                    language_code_list.append(line)
                else:
                    pass
                if confidence in line:
                    confidence_list.append(line)
                else:
                    pass

        just_language_code_values_list = []
        for items in language_code_list:
            items = items.replace('language_code: "', "")
            items = items.replace(' ', "")
            items = items.replace('"', "")
            items = items.replace(",", "")
            items = items.replace("'", "")
            just_language_code_values_list.append(items)

        just_confidence_values_list = []
        for items in confidence_list:
            items = items.replace('confidence: ', "")
            items = items.replace(" ", "")
            items = items.replace(",", "")
            items = items.replace("'", "")
            con_num = float(items)
            just_confidence_values_list.append(con_num)

        # take out low confidence values
        # for i in range(len(just_confidence_values_list)):
        #     if just_confidence_values_list[i] < .1:
        #         just_confidence_values_list.remove(just_confidence_values_list[i])
        #         just_language_code_values_list.remove(just_language_code_values_list[i])

        top_languages = []
        top_confidence = []
        if len(just_language_code_values_list) >= 3:
            for i in range(0, 3):
                top_languages.append(just_language_code_values_list[i])
                top_confidence.append(just_confidence_values_list[i])
        else:
            top_languages = just_language_code_values_list.copy()
            top_confidence = just_confidence_values_list.copy()

        contains_locale = str(response)
        contains_locale_split = contains_locale.split('\n')
        locale_string = str(contains_locale_split[1])
        locale = locale_string.replace('locale: ', '')
        locale = locale.replace('"', '')
        locale = locale.replace(' ', '')

        self.document_level_language = locale
        self.top_languages = top_languages
        self.top_confidence = top_confidence

        # print('Document Level Language: ', locale)
        # print('Detected Languages: ', top_languages)
        # print('Language Confidence: ', top_confidence)
        print(word_text)
        print(line_text)

        # return locale, top_languages, top_confidence

    # def get_language_data(self):
    #     response = self.current_ocr_response
    #     page = response.full_text_annotation
    #
    #     page_string = str(page)
    #     page_string_split = page_string.split('\n')
    #
    #     language_code = 'language_code: '
    #     confidence = 'confidence: '
    #     language_code_list = []
    #     confidence_list = []
    #     stop = 'blocks'
    #
    #     for line in page_string_split:
    #         if stop in line:
    #             break
    #         else:
    #             if language_code in line:
    #                 language_code_list.append(line)
    #             else:
    #                 pass
    #             if confidence in line:
    #                 confidence_list.append(line)
    #             else:
    #                 pass
    #
    #     just_language_code_values_list = []
    #     for items in language_code_list:
    #         items = items.replace('language_code: "', "")
    #         items = items.replace(' ', "")
    #         items = items.replace('"', "")
    #         items = items.replace(",", "")
    #         items = items.replace("'", "")
    #         just_language_code_values_list.append(items)
    #
    #     just_confidence_values_list = []
    #     for items in confidence_list:
    #         items = items.replace('confidence: ', "")
    #         items = items.replace(" ", "")
    #         items = items.replace(",", "")
    #         items = items.replace("'", "")
    #         con_num = float(items)
    #         just_confidence_values_list.append(con_num)
    #
    #     top_languages = []
    #     top_confidence = []
    #     for i in range(0, 3):
    #         top_languages.append(just_language_code_values_list[i])
    #         top_confidence.append(just_confidence_values_list[i])
    #
    #     contains_locale = str(response)
    #     contains_locale_split = contains_locale.split('\n')
    #     locale_string = str(contains_locale_split[1])
    #     locale = locale_string.replace('locale: ', '')
    #     locale = locale.replace('"', '')
    #     locale = locale.replace(' ', '')
    #
    #     print('Document Level Language: ', locale)
    #     print('Detected Languages: ', top_languages)
    #     print('Language Confidence: ', top_confidence)
    #
    #     return locale, top_languages, top_confidence

    def get_list_of_symbols(self, label_only=False) -> list:
        symbols = [block for block in self.ocr_blocks if block['type'] == 'SYMBOL']
        if label_only:
            x_min = self.current_label_location[0][0]
            x_max = self.current_label_location[1][0]
            y_min = self.current_label_location[1][1]
            y_max = self.current_label_location[2][1]
            label_words = list()
            for symbol in symbols:
                curr_x = (symbol['bounding_box'][0][0] + symbol['bounding_box'][1][0]) / 2
                curr_y = (symbol['bounding_box'][1][1] + symbol['bounding_box'][2][1]) / 2
                if x_min <= curr_x <= x_max and y_min <= curr_y <= y_max:
                    label_words.append(symbol)
            words = label_words
        return symbols


class AWSProcessor(ImageProcessor):
    def _initialize_client(self):
        return boto3.client('textract')

    def _initialize_name_and_save_directory(self) -> str:
        self.name = 'aws'
        self.object_save_directory = os.path.join(self.object_save_directory, self.name)
        if not os.path.exists(self.object_save_directory):
            os.makedirs(self.object_save_directory)
        return self.name

    def _download_ocr(self, special_image_location=None) -> None:
        """ Use the optional parameter special_image_location to run the OCR on a temporary image (e.g. when running
        a cropped image through, if the original image didn't generate much OCR text).  Otherwise,
        self.current_image_location is used for the OCR. """
        if special_image_location:
            with open(special_image_location, 'rb') as img:
                f = img.read()
                image_content = bytes(f)
        else:
            with open(self.current_image_location, 'rb') as img:
                f = img.read()
                image_content = bytes(f)

        try:
            self.current_ocr_response = self.client.detect_document_text(
                Document={
                    'Bytes': image_content
                })
        except ConnectionClosedError:
            print('Unable to get %s connection for image %s.' % (self.name, self.current_image_barcode))
            self.current_ocr_response = dict()
            self.current_ocr_response['Blocks'] = [{'BlockType': 'PAGE'}]

    def _parse_ocr_blocks(self):
        self.ocr_blocks = list()
        current_image = open_cv2_image(self.current_image_location)
        self.current_image_height = current_image.shape[0]
        self.current_image_width = current_image.shape[1]

        found_text = [block['Text'] for block in self.current_ocr_response['Blocks'] if block['BlockType'] == 'WORD']
        if len(' '.join(found_text)) < 200:
            self._rerun_ocr_with_cropping()
            self.current_image_used_cropped_image_ocr = True
            print('Bad image %s, reran OCR.' % self.current_image_barcode)

        lines: list = [line for line in self.current_ocr_response['Blocks'] if not line['BlockType'] == 'PAGE']
        for line in lines:
            new_line: dict = {'type': line['BlockType'], 'confidence': line['Confidence'], 'text': line['Text']}
            v: list = line['Geometry']['Polygon']
            v_list = [(v[0]['X'], v[0]['Y']), (v[1]['X'], v[1]['Y']), (v[2]['X'], v[2]['Y']), (v[3]['X'], v[3]['Y'])]
            v_list = self.convert_list_of_relative_coordinates(v_list)
            new_line['bounding_box'], _, _, _, _ = arrange_coordinates(v_list)
            self.ocr_blocks.append(new_line)

        self.pickle_current_image_state('parsed AWS ocr')

    def convert_list_of_relative_coordinates(self, vertex_list: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
        new_vertex_list = list()
        for point in vertex_list:
            new_x = int(self.current_image_width * point[0])
            new_y = int(self.current_image_height * point[1])
            new_vertex_list.append((new_x, new_y))
        return new_vertex_list

    def _rerun_ocr_with_cropping(self):
        temp_folder = 'tmp'
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        # create cropped image of lower right quadrant
        cropped_image = self.annotator.cropped_image_to_ratio(0.5, 1.0, 0.5, 1.0)
        cropped_filepath = save_cv2_image(temp_folder, self.current_image_barcode, cropped_image)
        cropped_filepath = os.path.join(temp_folder, cropped_filepath)
        print(cropped_filepath)
        # rerun OCR with the temp image
        self._download_ocr(cropped_filepath)
        # correct the vertex values = 0.5x + 0.5
        for block in self.current_ocr_response['Blocks']:
            block['Geometry']['Polygon'] = [{'X': 0.5 * p['X'] + 0.5, 'Y': 0.5 * p['Y'] + 0.5} for p
                                            in block['Geometry']['Polygon']]
        # delete temp image
        os.remove(cropped_filepath)
