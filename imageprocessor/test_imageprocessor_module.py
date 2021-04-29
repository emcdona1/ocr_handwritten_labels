""" To run tests, execute in CLI: pytest -p no:warnings imageprocessor\test_imageprocessor_module.py """
import pytest

from imageprocessor import image_processor
from google.cloud import vision
import os
from utilities import dataloader, dataprocessor


@pytest.fixture
def test_image():
    return 'test_label_image.jpg'


@pytest.fixture
def test_directory():
    return 'label_images'


@pytest.fixture
def gcv_processor():
    return image_processor.GCVProcessor()


@pytest.fixture
def aws_processor():
    return image_processor.AWSProcessor()


@pytest.fixture
def aws_response():
    return dataloader.load_pickle(os.path.join('imageprocessor', 'test_aws_response.pickle'))


@pytest.fixture
def gcv_response():
    return dataloader.load_pickle(os.path.join('imageprocessor', 'test_gcv_response.pickle'))


def test_gcv_client(gcv_processor):
    print(type(gcv_processor.client))
    assert type(gcv_processor.client) is vision.ImageAnnotatorClient


def test_gcv_save_directory(gcv_processor):
    print(gcv_processor.ocr_save_directory)
    assert os.path.exists(gcv_processor.ocr_save_directory)


def test_aws_save_directory(aws_processor):
    print(aws_processor.ocr_save_directory)
    assert os.path.exists(aws_processor.ocr_save_directory)


def test_barcode_parser_underscore(gcv_processor):
    filename = 'foo' + os.path.sep + 'C0123456F_label.pickle'
    barcode = dataprocessor.extract_barcode_from_image_name(filename)
    assert barcode == 'C0123456F'


def test_barcode_parser_hyphen(gcv_processor):
    filename = 'foo' + os.path.sep + 'C0123456F-label.pickle'
    barcode = dataprocessor.extract_barcode_from_image_name(filename)
    assert barcode == 'C0123456F'
