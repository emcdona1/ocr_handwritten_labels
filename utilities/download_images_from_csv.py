from data_loader import download_image, open_cv2_image, save_cv2_image
import pandas as pd
import sys
import os
import cv2
from pathlib import Path


def main(occ_filepath: str, save_directory: str):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    occurrences = pd.read_csv(occ_filepath, encoding='UTF-8')
    num_rows = occurrences.shape[0]
    for idx, row in occurrences.iterrows():
        image_url = row['image_url']
        barcode = row['catalogNumber']
        saved_image_location = download_image(image_url, save_directory, barcode)
        if saved_image_location == '':
            print('Error saving image for barcode %s.' % barcode)
        elif saved_image_location == 'EXISTS':
            print('Image already exists for barcode %s.' % barcode)
        else:
            image = cv2.imread(saved_image_location)
            # print(f'{image.shape[0]} vs. {image.shape[1]}')
            if image.shape[0] < image.shape[1]:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                save_cv2_image(Path(saved_image_location).parent, Path(saved_image_location).stem, image, False)
                print(f'Image {idx + 1} / {num_rows} rotated & saved.')
            print(f'Image { idx + 1 } / { num_rows } saved.')


if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Provide 2 arguments: an occurrence file with the added "image_url" column ' + \
        '(via join_occurrence_file_with_image_urls.py script), and the directory in which to save images ' + \
                              '(will be created if needed).'
    occur_path = sys.argv[1]
    save_dir = sys.argv[2]
    main(occur_path, save_dir)
