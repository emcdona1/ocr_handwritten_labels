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
from imageprocessor import image_annotator
from typing import List, Tuple
import math
import numpy as np


class ImageProcessor(ABC):
    def __init__(self, starting_image_path=None):
        self.client = self.initialize_client()
        self.save_directory = 'ocr_responses'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        self.initialize_save_directory()
        self.current_image_location = None
        self.current_image_barcode = None
        self.current_ocr_response = None
        self.current_image_height = None
        self.current_image_width = None
        self.current_label_height = None
        self.current_label_width = None
        self.current_label_location = None
        self.name = 'imageprocessor'
        self.ocr_blocks = None
        if starting_image_path:
            self.load_image_from_file(starting_image_path)

    def search_for_and_load_existing_pickle_file(self) -> bool:
        """ Returns true if a pickled response is found for this file/OCR platform, and loads the pickled response
         into current_ocr_response.  If not found, returns false and sets current_ocr_response to None."""
        base_name_of_image = os.path.basename(self.current_image_location).split('.')[0]
        file_list = os.listdir(self.save_directory)
        matches = [path for path in file_list if (base_name_of_image + '.pickle') in path]
        if len(matches) > 0:
            print('Using previously pickled %s response object for %s' % (self.name, base_name_of_image))
            self.current_ocr_response = load_pickle(os.path.join(self.save_directory, matches[0]))
            return True
        else:
            self.current_ocr_response = None
            return False

    def get_found_word_locations(self) -> List[Tuple]:
        """ Returns a list of (x,y) coordinates (top left is origin),
         where each point is the corner of a word identified by the OCR. """
        word_points = []
        words = self.get_list_of_words()
        annotator = self.get_image_annotator()
        for word in words:
            corners_of_word = annotator.organize_vertices(word)
            for vertex in corners_of_word:
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
            for y in range(int(self.current_image_height / 2), self.current_image_height - self.current_label_height + 1):
                for x in range(int(self.current_image_width / 2), self.current_image_width - self.current_label_width + 1):
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
        return self.current_label_location

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def initialize_save_directory(self):
        pass

    @abstractmethod
    def load_image_from_file(self, image_path: str) -> None:
        pass

    @abstractmethod
    def parse_ocr_blocks(self) -> None:
        pass

    @abstractmethod
    def download_ocr_and_save_response(self) -> None:
        pass

    @abstractmethod
    def get_image_annotator(self):
        pass

    @abstractmethod
    def get_list_of_words(self) -> list:
        pass

    @abstractmethod
    def get_list_of_lines(self) -> list:
        pass

    @abstractmethod
    def get_full_text(self) -> str:
        pass

    @abstractmethod
    def get_label_text(self) -> str:
        pass


class GCVProcessor(ImageProcessor):
    def __init__(self, starting_image_path=None):
        super().__init__(starting_image_path)
        self.name = 'gcv'

    def initialize_client(self):
        config_parser = ConfigParser()
        config_parser.read(r'Configuration.cfg')
        service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
        return vision.ImageAnnotatorClient()

    def initialize_save_directory(self):
        self.save_directory = self.save_directory + os.path.sep + 'gcv'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def load_image_from_file(self, image_path: str) -> None:
        self.current_ocr_response = None
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        found: bool = self.search_for_and_load_existing_pickle_file()
        if not found:
            self.download_ocr_and_save_response()
        self.current_image_height = self.current_ocr_response.full_text_annotation.pages[0].height
        self.current_image_width = self.current_ocr_response.full_text_annotation.pages[0].width
        self.current_label_height = math.ceil(self.current_image_height * 0.15)
        self.current_label_width = math.ceil(self.current_image_width * 0.365)
        self.parse_ocr_blocks()

    def parse_ocr_blocks(self):
        self.ocr_blocks = list()
        for block in self.current_ocr_response.full_text_annotation.pages[0].blocks:
            for paragraph in block.paragraphs:
                line_text = ''
                for word in paragraph.words:
                    word_text = ''
                    for symbol in word.symbols:
                        v = symbol.bounding_box.vertices
                        v = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[3].x, v[3].y)]
                        v, _, _, _, _ = arrange_coordinates(v)
                        self.ocr_blocks.append({'type': 'SYMBOL', 'confidence': symbol.confidence,
                                                'bounding_box': v,
                                                'text': symbol.text})
                        word_text += symbol.text
                        line_text += symbol.text
                    v = symbol.bounding_box.vertices
                    self.ocr_blocks.append({'type': 'WORD', 'confidence': word.confidence,
                                            # todo: sort these first
                                            'bounding_box': [(v[0].x, v[0].y), (v[1].x, v[1].y),
                                                             (v[2].x, v[2].y), (v[3].x, v[3].y)],
                                            'text': word_text})
                v = paragraph.bounding_box.vertices
                self.ocr_blocks.append({'type': 'LINE',
                                        'confidence': paragraph.confidence,
                                        # todo: sort these first
                                        'bounding_box': [(v[0].x, v[0].y), (v[1].x, v[1].y),
                                                         (v[2].x, v[2].y), (v[3].x, v[3].y)],
                                        'text': line_text})
        block_order = { 'LINE': 1,
                        'WORD': 2,
                        'SYMBOL': 3}
        self.ocr_blocks = sorted(self.ocr_blocks, key=lambda b: block_order[b['type']])

    def download_ocr_and_save_response(self) -> None:
        with io.open(self.current_image_location, 'rb') as image_file:
            image_content = image_file.read()
        image = vision.types.Image(content=image_content)
        self.current_ocr_response = self.client.document_text_detection(image=image)
        pickle_an_object(self.save_directory,
                         os.path.basename(self.current_image_location).split('.')[0],
                         self.current_ocr_response)

    def get_image_annotator(self):
        return image_annotator.GCVImageAnnotator(self.current_image_location)

    def get_full_text(self) -> str:
        gcv_text = ' '
        if self.current_ocr_response:
            gcv_text = self.current_ocr_response.full_text_annotation.text
        return gcv_text.strip()

    def get_list_of_words(self) -> list:
        all_words = []
        page = self.current_ocr_response.full_text_annotation.pages[0]
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    all_words.append(word)
        return all_words

    def get_list_of_lines(self) -> list:
        all_lines = []
        page = self.current_ocr_response.full_text_annotation.pages[0]
        for block in page.blocks:
            for paragraph in block.paragraphs:
                all_lines.append(paragraph)
        return all_lines

    def get_label_text(self) -> str:
        if self.current_ocr_response is None:
            print('Warning: no image OCR data has been loaded.')
            return ''
        elif self.current_label_location is None:
            print('No label location set; searching now.')
            self.find_label_location()
        label_text = ''
        for block in self.current_ocr_response.full_text_annotation.pages[0].blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        location = symbol.bounding_box.vertices[0]
                        if self.current_label_location[0][0] <= location.x <= self.current_label_location[1][0]:
                            if self.current_label_location[1][1] <= location.y <= self.current_label_location[2][1]:
                                label_text = label_text + symbol.text
                    label_text += ' '
                label_text += '\n'
        return label_text.strip()


class AWSProcessor(ImageProcessor):
    def __init__(self, starting_image_path=None):
        super().__init__(starting_image_path)
        self.name = 'aws'

    def initialize_client(self):
        return boto3.client('textract')

    def initialize_save_directory(self):
        self.save_directory = self.save_directory + os.path.sep + 'aws'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def load_image_from_file(self, image_path: str) -> None:
        self.current_ocr_response = None
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        found: bool = self.search_for_and_load_existing_pickle_file()
        if not found:
            self.download_ocr_and_save_response()
        self.current_image_height = self.current_ocr_response['height']
        self.current_image_width = self.current_ocr_response['width']
        self.current_label_height = math.ceil(self.current_image_height * 0.15)
        self.current_label_width = math.ceil(self.current_image_width * 0.365)
        self.parse_ocr_blocks()

    def parse_ocr_blocks(self):
        self.ocr_blocks = list()
        lines = [line for line in self.current_ocr_response['Blocks'] if not line['BlockType'] == 'PAGE']
        for line in lines:
            new_line = {'type': line['BlockType'], 'confidence': line['Confidence'], 'text': line['Text']}
            v = line['Geometry']['Polygon']
            v_list = [(v[0]['X'], v[0]['Y']), (v[1]['X'], v[1]['Y']), (v[2]['X'], v[2]['Y']), (v[3]['X'], v[3]['Y'])]
            v_list = convert_list_of_relative_coordinates(v_list, self.current_image_height, self.current_image_width)
            new_line['bounding_box'], _, _, _, _ = arrange_coordinates(v_list)
            self.ocr_blocks.append(new_line)

    def download_ocr_and_save_response(self) -> None:
        with open(self.current_image_location, 'rb') as img:
            f = img.read()
            image_content = bytes(f)
        try:
            self.current_ocr_response = self.client.detect_document_text(
                Document={
                    'Bytes': image_content
                })
            pickle_an_object(self.save_directory,
                             os.path.basename(self.current_image_location).split('.')[0],
                             self.current_ocr_response)
        except ConnectionClosedError:
            print('Unable to get %s connection for image %s.' % (self.name, self.current_image_barcode))
            self.current_ocr_response = dict()
            self.current_ocr_response['Blocks'] = [{'BlockType': 'PAGE'}]
        current_image = open_cv2_image(self.current_image_location)
        self.current_ocr_response['height'] = current_image.shape[0]
        self.current_ocr_response['width'] = current_image.shape[1]
        pickle_an_object(self.save_directory,
                         os.path.basename(self.current_image_location).split('.')[0],
                         self.current_ocr_response)

    def get_image_annotator(self):
        return image_annotator.AWSImageAnnotator(self.current_image_location)

    def get_full_text(self) -> str:
        aws_text = ' '
        if self.current_ocr_response:
            blocks = self.current_ocr_response['Blocks']
            lines = [block for block in blocks if block['BlockType'] == 'LINE']
            for line in lines:
                aws_text += line['Text'] + '\n'
        return aws_text.strip()

    def get_list_of_words(self) -> list:
        words = [block for block in self.current_ocr_response['Blocks'] if block['BlockType'] == 'WORD']
        return words

    def get_list_of_lines(self) -> list:
        lines = [block for block in self.current_ocr_response['Blocks'] if block['BlockType'] == 'LINE']
        return lines

    def get_found_word_locations(self) -> List[Tuple[int, int]]:
        relative_word_locations = super(AWSProcessor, self).get_found_word_locations()
        absolute_word_locations = [convert_relative_to_absolute_coordinates(relative,
                                                                            self.current_image_height,
                                                                            self.current_image_width)
                                   for relative in relative_word_locations]
        return absolute_word_locations

    def get_label_text(self) -> str:
        """ Returns a string of words found by the OCR, but only words for which the upper left point of that word is
        within the label area. """
        if self.current_ocr_response is None:
            print('Warning: no image OCR data has been loaded.')
            return ''

        if self.current_label_location is None:
            print('No label location set; searching now.')
            self.find_label_location()
        label_text = ''
        words = [block for block in self.current_ocr_response['Blocks'] if block['BlockType'] == 'WORD']
        for word in words:
            location = word['Geometry']['Polygon'][0]
            location = convert_relative_to_absolute_coordinates((location['X'], location['Y']),
                                                                self.current_image_height, self.current_image_width)
            if self.current_label_location[0][0] <= location[0] <= self.current_label_location[1][0]:
                if self.current_label_location[1][1] <= location[1] <= self.current_label_location[2][1]:
                    label_text += word['Text'] + ' '
        return label_text
