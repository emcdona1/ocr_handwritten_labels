import os
import pickle
import numpy as np
from urllib.request import urlopen
import cv2
from datetime import datetime
import pandas as pd
import requests
from pathlib import Path
from typing import Union, List
from requests.exceptions import MissingSchema


def load_list_from_txt(file_path: str) -> list:
    results = list()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for item in lines:
            item = item.strip()
            results.append(item)
    return results


def load_file_list_from_filesystem(directory_or_file: Union[Path, str]) -> List[Path]:
    directory_or_file = Path(directory_or_file)
    if not os.path.exists(directory_or_file):
        raise FileNotFoundError(f'Not a valid directory or file: {directory_or_file}')

    if os.path.isdir(directory_or_file):
        all_directory_contents = os.listdir(directory_or_file)
        all_directory_contents_with_full_path = [Path(directory_or_file, filename)
                                                 for filename in all_directory_contents]
        results = [item for item in all_directory_contents_with_full_path if not os.path.isdir(item)]
        if isinstance(directory_or_file, Path):
            results = [Path(item) for item in results]
    else:
        results = [directory_or_file]

    return results


def load_pickle(pickle_file_path: Union[Path, str]):
    with open(pickle_file_path, 'rb') as file:
        de_pickled = pickle.load(file)
    return de_pickled


def pickle_an_object(save_directory: Union[Path, str], object_id: str, obj_to_pickle) -> str:
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    filename = object_id + '.pickle'
    file_path = os.path.join(save_directory, filename)
    with open(file_path, 'wb') as file:
        pickle.dump(obj_to_pickle, file)
    return file_path


def open_cv2_image(image_location: Union[Path, str]) -> np.ndarray:
    if 'http' in str(image_location):
        resp = urlopen(str(image_location))
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image_to_draw_on = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        image_to_draw_on = cv2.imread(str(image_location))
    return image_to_draw_on


def save_cv2_image(save_folder: Union[str, Path], image_id: str, image_to_save: np.ndarray, timestamp=True) -> str:
    filename = image_id + (('-annotated_' + get_timestamp_for_file_saving()) if timestamp else '') + '.jpg'
    file_path = os.path.join(save_folder, filename)
    cv2.imwrite(str(file_path), image_to_save)
    return filename


def get_timestamp_for_file_saving() -> str:
    return datetime.strftime(datetime.now(), '%Y_%m_%d-%H_%M_%S')


def save_dataframe_as_csv(save_location: Union[Path, str], file_id: str, df: pd.DataFrame, timestamp=True) -> str:
    filename = file_id + (('-' + get_timestamp_for_file_saving()) if timestamp else '') + '.csv'
    file_location = os.path.join(save_location, filename)
    df.to_csv(file_location, index=False, encoding='UTF-8')
    return file_location


def download_image(image_url: str, save_directory: Union[Path, str], image_id: str) -> str:
    image_save_path = os.path.join(save_directory, str(image_id) + '.jpg')
    if os.path.exists(image_save_path):
        image_save_path = 'EXISTS'
    else:
        try:
            result = requests.get(image_url)
            if result.status_code == 200:
                with open(image_save_path, 'wb') as f:
                    f.write(result.content)
            else:
                image_save_path = ''
        except MissingSchema:
            print(f'No image url: {image_id}')
            image_save_path = ''
    return image_save_path
