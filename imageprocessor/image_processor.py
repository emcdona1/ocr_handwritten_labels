from configparser import ConfigParser
import io
import os
from google.cloud import vision
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ConnectionClosedError
from utilities.dataloader import load_pickle, pickle_an_object, open_cv2_image
from utilities.dataprocessor import extract_barcode_from_image_name, convert_relative_to_absolute_coordinates, \
    convert_list_of_relative_coordinates, arrange_coordinates
from imageprocessor.image_annotator import ImageAnnotator
from typing import List, Tuple, Union
import math
import numpy as np


class ImageProcessor(ABC):
    def __init__(self, starting_image_path=None):
        self.client = self._initialize_client()
        self.object_save_directory = 'imageprocessor_objects'
        self.name = self._initialize_name_and_save_directory()
        self._current_ocr_response = None
        self.ocr_blocks = None
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

    def __getstate__(self):
        """ Return a copy of the ImageProcessor, without the client instance attribute, for pickling."""
        state = self.__dict__.copy()
        try:
            del state['client']
        except TypeError:
            # 'client' wasn't in state
            pass
        return state

    def __setstate__(self, state):
        """ Restores ImageProcessor from pickle and initialized the client (which is not pickled). """
        try:
            del state['client']
        except KeyError:
            # 'client' wasn't in state
            pass
        self.__dict__.update(state)
        self.client = self._initialize_client()

    def pickle_current_image_state(self):
        path = pickle_an_object(self.object_save_directory, self.current_image_barcode, self)
        print('%s ImageProcessor saved to %s.' % (self.name, path))

    def get_found_word_locations(self) -> List[Tuple]:
        """ Returns a list of (x,y) coordinates, where each point is the corner of a word identified by the OCR. """
        word_points = []
        words = self.get_list_of_words()
        for word in words:
            for vertex in word.bounding_box:
                word_points.append(vertex)
        return word_points

    def find_label_location(self) -> \
            Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """ Searches bottom quadrant of image for highest concentration of word bounding boxes
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
        self.pickle_current_image_state()
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
        self.annotator.clear_current_image()

    @abstractmethod
    def _initialize_name_and_save_directory(self) -> str:
        pass

    def load_image_from_file(self, image_path: str) -> None:
        self.clear_current_image()
        self.current_image_location = image_path
        self.current_image_basename = os.path.basename(image_path).split('.')[0]
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        self.annotator.load_image_from_file(image_path)

        # 1. check for imageprocessor_object. If Y, load it and done.
        pickled_object_location = self._search_for_pickled_object()
        if pickled_object_location:
            loaded = load_pickle(pickled_object_location)
            self.__setstate__(loaded.__dict__)
        else:
            # 2. If N, send OCR request, pickle the response, and then _parse_ocr_blocks and pickle the IP.
            self._download_ocr()
            self._parse_ocr_blocks()
            self.current_label_height = math.ceil(self.current_image_height * 0.15)
            self.current_label_width = math.ceil(self.current_image_width * 0.365)
            self.pickle_current_image_state()

    def _search_for_pickled_object(self) -> Union[str, None]:
        pickled_search_name = self.current_image_basename + '.pickle'
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

    def get_list_of_words(self) -> list:
        words = [block for block in self.ocr_blocks if block['type'] == 'WORD']
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
        self.object_save_directory = self.object_save_directory + os.path.sep + self.name
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
        for block in self.current_ocr_response.full_text_annotation.pages[0].blocks:
            for paragraph in block.paragraphs:
                line_text = ''
                for word in paragraph.words:
                    word_text = ''
                    for symbol in word.symbols:
                        v = symbol.bounding_box.vertices
                        v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                        vertices, _, _, _, _ = arrange_coordinates(v)
                        self.ocr_blocks.append({'type': 'SYMBOL', 'confidence': symbol.confidence,
                                                'bounding_box': vertices, 'text': symbol.text})
                        word_text += symbol.text
                        line_text += symbol.text
                    v = word.bounding_box.vertices
                    v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                    vertices, _, _, _, _ = arrange_coordinates(v)
                    self.ocr_blocks.append({'type': 'WORD', 'confidence': word.confidence,
                                            'bounding_box': vertices, 'text': word_text})
                v = paragraph.bounding_box.vertices
                v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                vertices, _, _, _, _ = arrange_coordinates(v)
                self.ocr_blocks.append({'type': 'LINE', 'confidence': paragraph.confidence,
                                        'bounding_box': vertices, 'text': line_text})
        block_order = {'LINE': 1, 'WORD': 2, 'SYMBOL': 3}
        self.ocr_blocks = sorted(self.ocr_blocks, key=lambda b: block_order[b['type']])
        self.pickle_current_image_state()


class AWSProcessor(ImageProcessor):
    def _initialize_client(self):
        return boto3.client('textract')

    def _initialize_name_and_save_directory(self) -> str:
        self.name = 'aws'
        self.object_save_directory = self.object_save_directory + os.path.sep + self.name
        if not os.path.exists(self.object_save_directory):
            os.makedirs(self.object_save_directory)
        return self.name

    def _download_ocr(self) -> None:
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
        current_image = open_cv2_image(self.current_image_location)
        self.current_ocr_response['height'] = current_image.shape[0]
        self.current_ocr_response['width'] = current_image.shape[1]

    def _parse_ocr_blocks(self):
        self.current_image_height = self.current_ocr_response['height']
        self.current_image_width = self.current_ocr_response['width']
        self.ocr_blocks = list()
        lines: list = [line for line in self.current_ocr_response['Blocks'] if not line['BlockType'] == 'PAGE']
        for line in lines:
            new_line: dict = {'type': line['BlockType'], 'confidence': line['Confidence'], 'text': line['Text']}
            v: list = line['Geometry']['Polygon']
            v_list = [(v[0]['X'], v[0]['Y']), (v[1]['X'], v[1]['Y']), (v[2]['X'], v[2]['Y']), (v[3]['X'], v[3]['Y'])]
            v_list = convert_list_of_relative_coordinates(v_list, self.current_image_height, self.current_image_width)
            new_line['bounding_box'], _, _, _, _ = arrange_coordinates(v_list)
            self.ocr_blocks.append(new_line)
        self.pickle_current_image_state()
