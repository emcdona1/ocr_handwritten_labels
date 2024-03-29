import sys
import os
from zipfile import ZipFile
import pandas as pd
from io import BytesIO
from copy import deepcopy
from data_loader import save_dataframe_as_csv
import requests


def main(zip_file_path: str):
    occur, images = extract_occur_and_images_from_zip(zip_file_path)
    joined_data = join_occur_and_images_information(occur, images)
    save_directory = os.path.dirname(zip_file_path)
    save_location = save_dataframe_as_csv(save_directory, 'occurrence_file_with_images', joined_data)
    print('New file saved to %s.' % save_location)
    return joined_data


def extract_occur_and_images_from_zip(zip_file_path: str) -> (pd.DataFrame, pd.DataFrame):
    with ZipFile(zip_file_path, 'r') as zipped_file:
        occur_bytes = zipped_file.read('occurrences.csv')
        occur = pd.read_csv(BytesIO(occur_bytes), encoding='UTF-8')
        images_bytes = zipped_file.read('multimedia.csv')
        images = pd.read_csv(BytesIO(images_bytes), encoding='UTF-8')

    return occur, images


def join_occur_and_images_information(occur: pd.DataFrame, images: pd.DataFrame) -> pd.DataFrame:
    joined_information = deepcopy(occur)
    url_df = drop_just_barcodes(images)
    joined_information = joined_information.assign(image_url=url_df['identifier'])
    num_rows = joined_information.shape[0]

    for idx, row in joined_information.iterrows():
        valid_image_url = is_valid_url(row['image_url'])
        if valid_image_url:
            print('Image %i / %i validated.' % (idx + 1, num_rows))
        else:
            print('No image url for %i, barcode: %s.' % (idx + 1, row['catalogNumber']))
    return joined_information


def drop_just_barcodes(images: pd.DataFrame):
    url_df = deepcopy(images)

    for i in range(len(images)):
        url = images.at[i, 'identifier']
        if "_b.jpg" in url or "_B.jpg" in url:
            url_df = url_df.drop([i])
        else:
            pass

    url_df = url_df.reset_index(drop=True)
    return url_df


def is_valid_url(image_url: str) -> bool:
    try:
        result = requests.get(image_url)
        return result.status_code == 200
    except requests.exceptions.MissingSchema as e:
        print(e)
        return False


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Please provide 1 argument: a ZIP file downloaded from the Fern Portal.'
    filepath = sys.argv[1]
    new_df = main(filepath)
