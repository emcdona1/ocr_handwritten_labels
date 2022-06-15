from pathlib import Path
from typing import List, Tuple, Union


def extract_barcode_from_image_name(image_name: Union[Path, str]) -> str:
    image_name_without_extension = Path(image_name).stem
    image_barcode_split = image_name_without_extension.split('_')
    if len(image_barcode_split) == 1:
        image_barcode_split = image_name_without_extension.split('-')
    return image_barcode_split[0]


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
