from configparser import ConfigParser
import io
import os
from google.cloud import vision
from abc import ABC, abstractmethod
import boto3
from utilities.dataloader import load_pickle, pickle_an_object, open_cv2_image
from utilities.dataprocessor import extract_barcode_from_image_name, convert_relative_to_absolute_coordinates
from imageprocessor import image_annotator
from typing import List, Tuple
import math
import numpy as np


class ImageProcessor(ABC):
    def __init__(self):
        self.client = self.initialize_client()
        self.save_directory = 'ocr_responses'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        self.initialize_save_directory()
        self.image_content = None
        self.current_image_location = None
        self.current_image_barcode = None
        self.current_ocr_response = None
        self.current_image_height = None
        self.current_image_width = None
        self.current_label_height = None
        self.current_label_width = None
        self.current_label_location = None
        self.name = 'imageprocessor'

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def initialize_save_directory(self):
        pass

    @abstractmethod
    def load_image_from_file(self, image_path: str) -> None:
        pass

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
        and returns a set of 4 tuples (top-left, top-right, bottom-right, bottom-left). """
        np_of_points = np.array(self.get_found_word_locations())
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


class GCVProcessor(ImageProcessor):
    def __init__(self, starting_image_path=None):
        super().__init__()
        self.name = 'gcv'
        if starting_image_path:
            self.load_image_from_file(starting_image_path)

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

    def download_ocr_and_save_response(self) -> None:
        with io.open(self.current_image_location, 'rb') as image_file:
            self.image_content = image_file.read()
        image = vision.types.Image(content=self.image_content)
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


class AWSProcessor(ImageProcessor):
    def __init__(self, starting_image_path=None):
        super().__init__()
        self.name = 'aws'
        if starting_image_path:
            self.load_image_from_file(starting_image_path)

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

    def download_ocr_and_save_response(self) -> None:
        with open(self.current_image_location, 'rb') as img:
            f = img.read()
            self.image_content = bytes(f)
        self.current_ocr_response = self.client.detect_document_text(
            Document={
                'Bytes': self.image_content
            })
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
                aws_text = aws_text + line['Text'] + '\n'
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
