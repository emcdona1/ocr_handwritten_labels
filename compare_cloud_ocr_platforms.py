import sys
from utilities.dataloader import load_file_list_from_filesystem


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    print(list_of_images)


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()