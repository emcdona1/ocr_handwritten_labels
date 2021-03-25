""" To run tests, execute in CLI: pytest -p no:warnings imageprocessor\test_image_processor.py """
import pytest
from imageprocessor import image_processor
from google.cloud import vision
import os


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


def test_gcv_client(gcv_processor):
    print(type(gcv_processor.client))
    assert type(gcv_processor.client) is vision.ImageAnnotatorClient


def test_gcv_save_directory(gcv_processor):
    print(gcv_processor.save_directory)
    assert os.path.exists(gcv_processor.save_directory)


def test_aws_save_directory(aws_processor):
    print(aws_processor.save_directory)
    assert os.path.exists(aws_processor.save_directory)


def test_check_for_pickle_with_no_parameters(gcv_processor):
    response = gcv_processor.check_for_existing_pickle_file()
    print(response)
    assert response is None


def test_check_for_pickle_with_valid_search_parameter(gcv_processor):
    print(gcv_processor.save_directory)
    response = gcv_processor.check_for_existing_pickle_file('test_gcv')
    print(type(response))
    assert type(response) is vision.types.AnnotateImageResponse


def test_check_for_pickle_with_invalid_search_parameter(gcv_processor):
    response = gcv_processor.check_for_existing_pickle_file('foo')
    print(response)
    assert response is None


def test_barcode_parser_underscore(gcv_processor):
    filename = 'foo' + os.path.sep + 'C0123456F_label.pickle'
    barcode = image_processor.extract_barcode_from_image_name(filename)
    assert barcode == 'C0123456F'


def test_barcode_parser_hyphen(gcv_processor):
    filename = 'foo' + os.path.sep + 'C0123456F-label.pickle'
    barcode = image_processor.extract_barcode_from_image_name(filename)
    assert barcode == 'C0123456F'