import sys
from utilities.dataloader import load_file_list_from_filesystem
from imageprocessor.image_processor import GCVProcessor, AWSProcessor, extract_barcode_from_image_name


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    gcv_processor = GCVProcessor()
    aws_processor = AWSProcessor()
    for one_image_location in list_of_images:
        one_image_barcode = extract_barcode_from_image_name(one_image_location)
        gcv_response = gcv_processor.load_processed_ocr_response(one_image_location, one_image_barcode)
        aws_response = aws_processor.load_processed_ocr_response(one_image_location, one_image_barcode)
        # todo: drawing time
    pass


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()