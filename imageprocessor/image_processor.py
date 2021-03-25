from configparser import ConfigParser
import io
import os
from urllib.request import urlopen
import cv2
import numpy as np
from imageprocessor.algorithmic_methods import get_normalized_sequential_data_blocks
from imageprocessor.initialize_data_from_image import get_gcv_ocr_as_data_frame_from_image
from google.cloud import vision
from abc import ABC, abstractmethod
import boto3
from utilities.dataloader import load_pickle


class ImageProcessor(ABC):
    def __init__(self):
        self.client = self.initialize_client()
        self.sdb = None
        self.dataFrame = None
        self.img_rgb = None
        self.imageContent = self.image_content = None
        self.save_directory = 'ocr_responses'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        self.initialize_save_directory()

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def initialize_save_directory(self):
        pass

    @abstractmethod
    def perform_ocr(self, image_path: str):
        pass

    def check_for_existing_pickle_file(self, image_id=None):
        response = None
        if image_id:
            file_list = os.listdir(self.save_directory)
            matches = [path for path in file_list if (image_id in path and '.pickle' in path)]
            response = None
            if len(matches) > 0:
                response = load_pickle(os.path.join(self.save_directory, matches[0]))
        return response

    def process_image(self, image_path: str):
        print('Processing: ' + image_path)
        self.set_image_rgb(image_path)
        gcv_response_object = self.initialize_ocr_data(image_path)
        self.sdb = get_normalized_sequential_data_blocks(self.dataFrame)

        str_gcv = ''
        for block_of_words in self.sdb:
            for a_word in block_of_words:
                str_gcv += a_word.description + ' '

        str_dc = ''
        for block_of_words in self.sdb:
            for a_word in block_of_words:
                str_dc += a_word.description + ' '

        return gcv_response_object, str_gcv, str_dc

    def initialize_ocr_data(self, image_path: str):
        with io.open(image_path, 'rb') as image_file:
            self.imageContent = image_file.read()
        self.dataFrame, gcv_response_object = get_gcv_ocr_as_data_frame_from_image(self.imageContent, self.client)
        return gcv_response_object

    def set_image_rgb(self, image_path):
        if 'http' in image_path:
            resp = urlopen(image_path)
            image = np.asarray(bytearray(resp.read()), dtype='uint8')
            img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            img_rgb = cv2.imread(image_path)
        self.img_rgb = img_rgb


def extract_barcode_from_image_name(image_path: str) -> str:
    image_name_without_extension = os.path.basename(image_path).split('.')[0]
    image_barcode_split = image_name_without_extension.split('_')
    if len(image_barcode_split) == 1:
        image_barcode_split = image_name_without_extension.split('-')
    image_barcode = image_barcode_split[0]
    return image_barcode


class GCVProcessor(ImageProcessor):
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

    def perform_ocr(self, image_path: str, image_id=None):
        response = self.check_for_existing_pickle_file(image_id)
        if not response:
            if not image_id:
                image_id = extract_barcode_from_image_name(image_path)
            with io.open(image_path, 'rb') as image_file:
                self.image_content = image_file.read()
            image = vision.types.Image(content=self.image_content)
            response = self.client.document_text_detection(image=image)
        return response


class AWSProcessor(ImageProcessor):
    def initialize_client(self):
        return boto3.client('textract')

    def initialize_save_directory(self):
        self.save_directory = self.save_directory + os.path.sep + 'aws'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def perform_ocr(self, image_path: str, image_id=None):
        response = self.check_for_existing_pickle_file(image_id)
        if not response:
            if not image_id:
                image_id = extract_barcode_from_image_name(image_path)
            with open(image_path, 'rb') as img:
                f = img.read()
                image_binary = bytes(f)
            response = self.client.detect_document_text(
                Document={
                    'Bytes': image_binary
                })
        return response