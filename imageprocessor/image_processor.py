import io
from urllib.request import urlopen
import cv2
import numpy as np
from imageprocessor.algorithmic_methods import get_normalized_sequential_data_blocks, get_temp_file_path
from imageprocessor.initialize_data_from_image import get_gcv_ocr_as_data_frame_from_image
from imageprocessor.detect_wrong_words import detect_wrong_words

class ImageProcessor:
    def __init__(self, vision_client, image_path=None, min_confidence=None, extract_tag=None,
                 display_after_processing=False):
        self.client = vision_client
        self.tagPath = image_path  # can be overwritten when tag is extracted.
        self.minimumConfidence = min_confidence
        self.sdb = None
        self.extractTag = extract_tag
        self.displayAfterProcessing = display_after_processing
        self.dataFrame = None
        self.img_rgb = None
        self.imageContent = None
        self.temp_image_path = None

    def process_image(self, image_path):
        print('Processing: ' + image_path)
        self.set_image_rgb_and_save_to_temp_location(image_path)
        gcv_response_object = self.initialize_ocr_data()
        self.sdb = get_normalized_sequential_data_blocks(self.dataFrame)

        str_gcv = ''
        for block_of_words in self.sdb:
            for a_word in block_of_words:
                str_gcv += a_word.description + ' '

        detect_wrong_words(self.sdb, self.minimumConfidence)
        str_dc = ''
        for block_of_words in self.sdb:
            for a_word in block_of_words:
                str_dc += a_word.description + ' '

        return gcv_response_object, str_gcv, str_dc

    def initialize_ocr_data(self):
        with io.open(self.temp_image_path, 'rb') as image_file:
            self.imageContent = image_file.read()
        self.dataFrame, gcv_response_object = get_gcv_ocr_as_data_frame_from_image(self.imageContent, self.client)
        return gcv_response_object

    def set_image_rgb_and_save_to_temp_location(self, image_path):
        if 'http' in image_path:
            resp = urlopen(image_path)
            image = np.asarray(bytearray(resp.read()), dtype='uint8')
            img_rgb = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            img_rgb = cv2.imread(image_path)
        self.img_rgb = img_rgb
        self.temp_image_path = get_temp_file_path('_temp_wholeImage.png')
        cv2.imwrite(self.temp_image_path, img_rgb)
