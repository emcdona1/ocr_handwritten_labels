from dataloader import download_image
import pandas as pd
import sys
import os


def main(occ_filepath: str, save_directory: str):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    occurrences = pd.read_csv(occ_filepath, encoding='ISO-8859-1')
    num_rows = occurrences.shape[0]
    for idx, row in occurrences.iterrows():
        image_url = row['image_url']
        barcode = row['catalogNumber']
        saved_image_location = download_image(image_url, save_directory, barcode)
        if saved_image_location == '':
            print('Error saving image for barcode %s.' % barcode)
        else:
            print('Image %i / %i saved.' % (idx+1, num_rows))


if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Provide 2 arguments: an occurrence file with the added "image_url" column ' + \
        '(via join_occurrence_file_with_image_urls.py script), and the directory in which to save images ' + \
                              '(will be created if needed).'
    occur_path = sys.argv[1]
    save_dir = sys.argv[2]
    main(occur_path, save_dir)