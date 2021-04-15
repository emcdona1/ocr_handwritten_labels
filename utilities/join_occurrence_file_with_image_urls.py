import sys
import os
from zipfile import ZipFile
import pandas as pd
from io import BytesIO
from copy import deepcopy
from dataloader import save_dataframe_as_csv
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
        occur = pd.read_csv(BytesIO(occur_bytes), encoding='ISO-8859-1')
        images_bytes = zipped_file.read('images.csv')
        images = pd.read_csv(BytesIO(images_bytes), encoding='ISO-8859-1')
    return occur, images


def join_occur_and_images_information(occur: pd.DataFrame, images: pd.DataFrame) -> pd.DataFrame:
    joined_information = deepcopy(occur)
    joined_information = joined_information.assign(image_url = images['identifier'])
    num_rows = joined_information.shape[0]
    for idx, row in joined_information.iterrows():
        valid_image_url = is_valid_url(row['image_url'])
        if valid_image_url:
            print('Image %i / %i validated.' % (idx + 1, num_rows))
        else:
            web_resolution_image = images.at[idx, 'goodQualityAccessURI']
            valid_image_url = is_valid_url(web_resolution_image)
            if valid_image_url:
                joined_information.at[idx, 'image_url'] = web_resolution_image
                print('Image %i / %i successfully replaced.' % (idx + 1, num_rows))
            else:
                joined_information.at[idx, 'image_url'] = ''
                print('No image url for %i, barcode: %s.' % (idx + 1, row['catalogNumber']))
    return joined_information


def is_valid_url(image_url: str) -> bool:
    result = requests.get(image_url)
    return result.status_code == 200


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Please provide 1 argument: a ZIP file downloaded from the Fern Portal.'
    filepath = sys.argv[1]
    new_df = main(filepath)
