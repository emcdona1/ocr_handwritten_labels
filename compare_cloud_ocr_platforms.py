import sys
from utilities.dataloader import load_file_list_from_filesystem
from imageprocessor.image_processor import GCVProcessor, AWSProcessor


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    gcv_processor = GCVProcessor()
    aws_processor = AWSProcessor()
    for one_image in list_of_images:
        pass
    pass


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()