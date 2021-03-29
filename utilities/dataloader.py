import os
import pickle
import numpy as np
from urllib.request import urlopen
import cv2


def load_list_from_txt(file_path: str) -> list:
    results = list()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for item in lines:
            item = item.strip()
            results.append(item)
    return results


def load_file_list_from_filesystem(directory_or_file: str) -> list:
    results = list()
    if os.path.isdir(directory_or_file):
        results = os.listdir(directory_or_file)
        results = [directory_or_file + os.path.sep + filename for filename in results]
        results = [item for item in results if not os.path.isdir(item)]  # remove subdirectories
    elif os.path.isfile(directory_or_file):
        results = [directory_or_file]
    else:
        raise FileNotFoundError('Not a valid directory or file: %s' % directory_or_file)

    return results


def load_pickle(pickle_file_path: str):
    with open(pickle_file_path, 'rb') as file:
        de_pickled = pickle.load(file)
    return de_pickled


def pickle_an_object(save_directory: str, object_id: str, obj_to_pickle) -> None:
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    filename = object_id + '.pickle'
    with open(os.path.join(save_directory, filename), 'wb') as file:
        pickle.dump(obj_to_pickle, file)


def open_cv2_image(image_location: str) -> np.ndarray:
    if 'http' in image_location:
        resp = urlopen(image_location)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image_to_draw_on = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        image_to_draw_on = cv2.imread(image_location)
    return image_to_draw_on


def save_cv2_image(save_location: str, image_id: str, image_to_save: np.ndarray) -> str:
    filename = image_id + '-annotated.jpg'
    file_path = os.path.join(save_location, filename)
    cv2.imwrite(file_path, image_to_save)
    return filename
