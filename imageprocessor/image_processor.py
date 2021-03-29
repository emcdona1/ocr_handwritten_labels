from configparser import ConfigParser
import io
import os
from google.cloud import vision
from abc import ABC, abstractmethod
import boto3
from utilities.dataloader import load_pickle, pickle_an_object
from utilities.dataprocessor import extract_barcode_from_image_name
from imageprocessor import image_annotator


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

        # phase these out
        self.sdb = None
        self.dataFrame = None
        self.img_rgb = None
        self.imageContent = None

    @abstractmethod
    def initialize_client(self):
        pass

    @abstractmethod
    def initialize_save_directory(self):
        pass

    @abstractmethod
    def load_processed_ocr_response(self, image_path: str) -> None:
        pass

    def check_for_existing_pickle_file(self) -> bool:
        self.current_ocr_response = None
        file_list = os.listdir(self.save_directory)
        matches = [path for path in file_list if (self.current_image_barcode in path and '.pickle' in path)]
        if len(matches) > 0:
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

    def load_processed_ocr_response(self, image_path: str) -> None:
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        found: bool = self.check_for_existing_pickle_file()
        if not found:
            with io.open(image_path, 'rb') as image_file:
                self.image_content = image_file.read()
            image = vision.types.Image(content=self.image_content)
            self.current_ocr_response = self.client.document_text_detection(image=image)
            pickle_an_object(self.save_directory, self.current_image_barcode, self.current_ocr_response)

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
    def initialize_client(self):
        return boto3.client('textract')

    def initialize_save_directory(self):
        self.save_directory = self.save_directory + os.path.sep + 'aws'
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def load_processed_ocr_response(self, image_path: str) -> None:
        self.current_image_location = image_path
        self.current_image_barcode = extract_barcode_from_image_name(self.current_image_location)
        found: bool = self.check_for_existing_pickle_file()
        if not found:
            with open(self.current_image_location, 'rb') as img:
                f = img.read()
                self.image_content = bytes(f)
            self.current_ocr_response = self.client.detect_document_text(
                Document={
                    'Bytes': self.image_content
                })
            pickle_an_object(self.save_directory, self.current_image_barcode, self.current_ocr_response)

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
