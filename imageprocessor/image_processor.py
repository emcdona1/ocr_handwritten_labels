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
        self.name = 'imageprocessor'

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def initialize_save_directory(self):
        pass

    @abstractmethod
    def load_processed_ocr_response(self, image_path: str) -> None:
        pass

    def check_for_existing_pickle_file(self, filename: str) -> bool:
        self.current_ocr_response = None
        file_list = os.listdir(self.save_directory)
        matches = [path for path in file_list if (filename + '.pickle') in path]
        if len(matches) > 0:
            print('Using previously pickled response object for %s' % filename)
            self.current_ocr_response = load_pickle(os.path.join(self.save_directory, matches[0]))
            return True
        return False

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
        top_left_points = []
        words = self.get_list_of_words()
        annotator = self.get_image_annotator()
        for word in words:
            one_top_left_point, _, _, _ = annotator.organize_vertices(word)
            top_left_points.append(one_top_left_point)
        return top_left_points


class GCVProcessor(ImageProcessor):
    def __init__(self):
        super().__init__()
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

    def load_processed_ocr_response(self, image_path: str) -> None:
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        base_name_of_image = os.path.basename(self.current_image_location).split('.')[0]
        found: bool = self.check_for_existing_pickle_file(base_name_of_image)
        if not found:
            with io.open(image_path, 'rb') as image_file:
                self.image_content = image_file.read()
            image = vision.types.Image(content=self.image_content)
            self.current_ocr_response = self.client.document_text_detection(image=image)
            pickle_an_object(self.save_directory, base_name_of_image, self.current_ocr_response)
        self.current_image_height = self.current_ocr_response.full_text_annotation.pages[0].height
        self.current_image_width = self.current_ocr_response.full_text_annotation.pages[0].width

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
    def __init__(self):
        super().__init__()
        self.name = 'aws'

    def initialize_client(self):
        return boto3.client('textract')

    def initialize_save_directory(self):
        self.save_directory = self.save_directory + os.path.sep + 'aws'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def load_processed_ocr_response(self, image_path: str) -> None:
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        base_name_of_image = os.path.basename(self.current_image_location).split('.')[0]
        found: bool = self.check_for_existing_pickle_file(base_name_of_image)
        if not found:
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
            pickle_an_object(self.save_directory, base_name_of_image, self.current_ocr_response)
        self.current_image_height = self.current_ocr_response['height']
        self.current_image_width = self.current_ocr_response['width']

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
