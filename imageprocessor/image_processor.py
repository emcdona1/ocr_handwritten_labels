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


class ImageProcessor(ABC):
    def __init__(self):
        self.client = self.initialize_client()
        self.sdb = None
        self.dataFrame = None
        self.img_rgb = None
        self.imageContent = None

    @abstractmethod
    def initialize_client(self):
        pass

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


class GCVProcessor(ImageProcessor):
    def initialize_client(self):
        config_parser = ConfigParser()
        config_parser.read(r'Configuration.cfg')
        service_account_token_path = config_parser.get('GOOGLE_CLOUD_VISION_API', 'serviceAccountTokenPath')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_token_path
        return vision.ImageAnnotatorClient()


class AWSProcessor(ImageProcessor):
    def initialize_client(self):
        return boto3.client('textract')
