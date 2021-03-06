import os
import cv2
import numpy as np
from typing import List, Tuple


def extract_barcode_from_image_name(image_name: str) -> str:
    image_name_without_extension = os.path.basename(image_name).split('.')[0]
    image_barcode_split = image_name_without_extension.split('_')
    if len(image_barcode_split) == 1:
        image_barcode_split = image_name_without_extension.split('-')
    return image_barcode_split[0]


def crop_an_image_to_coordinates(image: np.ndarray, coordinates: List[Tuple[int, int]]) -> np.ndarray:
    sorted_coordinates, x_min, x_max, y_min, y_max = arrange_coordinates(coordinates)
    sorted_coordinates = np.array([sorted_coordinates])

    mask = np.zeros(image.shape[0:2], dtype=np.uint8)
    cv2.fillPoly(mask, sorted_coordinates, 255)

    masked_image = cv2.bitwise_and(image, image, mask=mask)
    cropped_image = masked_image[y_min:y_max, x_min:x_max]

    return cropped_image


def arrange_coordinates(coordinates: List[Tuple[int, int]]) -> (List[Tuple[int, int]], int, int, int, int):
    """ Sorts the provided list of x-y coordinates and returns the same coordinates in this order:
    (upper left, upper right, lower right, lower left). """
    sorted_x_values = sorted([item[0] for item in coordinates])
    sorted_y_values = sorted([item[1] for item in coordinates])
    left_side = [point for point in coordinates if point[0] in sorted_x_values[0:2]]
    right_side = [point for point in coordinates if point[0] in sorted_x_values[2:]]

    if left_side[0][1] > left_side[1][1]:
        left_side = [left_side[1], left_side[0]]
    if right_side[0][1] > right_side[1][1]:
        right_side = [right_side[1], right_side[0]]
    sorted_coordinates = [left_side[0], right_side[0], right_side[1], left_side[1]]
    return sorted_coordinates, sorted_x_values[0], sorted_x_values[-1], sorted_y_values[0], sorted_y_values[-1]


def crop_an_image_to_box(image: np.ndarray, x_min, x_max, y_min, y_max) -> np.ndarray:
    """ Provide either 4 int values (for absolute cropping) or float values [0,1] (for cropping relative to
    image size).  Returns the cropped image. """
    if type(x_min) is float:
        height = image.shape[0]
        width = image.shape[1]
        x_min = int(height * x_min)
        x_max = int(height * x_max)
        y_min = int(width * y_min)
        y_max = int(width * y_max)
    cropped_image = image[x_min:x_max + 1, y_min:y_max + 1]
    return cropped_image


def convert_relative_to_absolute_coordinates(vertex: Tuple[float, float], height: int, width: int) -> Tuple[int, int]:
    new_x = int(width * vertex[0])
    new_y = int(height * vertex[1])
    return new_x, new_y


def convert_list_of_relative_coordinates(vertex_list: List[Tuple[float, float]], height: int, width: int) -> \
        List[Tuple[int, int]]:
    new_vertex_list = list()
    for point in vertex_list:
        new_point = convert_relative_to_absolute_coordinates(point, height, width)
        new_vertex_list.append(new_point)
    return new_vertex_list
