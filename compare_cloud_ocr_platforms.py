import sys
from utilities.dataloader import load_file_list_from_filesystem
from imageprocessor.image_processor import GCVProcessor, AWSProcessor


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    image_processors = [GCVProcessor(), AWSProcessor()]
    for one_image_location in list_of_images:
        for processor in image_processors:
            processor.load_processed_ocr_response(one_image_location)
            annotator = processor.get_image_annotator()
            # todo: drawing time
    pass


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()
