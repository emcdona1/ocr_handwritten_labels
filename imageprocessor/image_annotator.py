import os
import numpy as np
from utilities.data_loader import open_cv2_image, save_cv2_image
from utilities.data_processor import extract_barcode_from_image_name
import cv2
from typing import Union
from pathlib import Path
import copy


class ImageAnnotator:
    def __init__(self, name: Union[str, Path], starting_image_location=None):
        self.save_location = os.path.join('annotated_images', name)
        self.current_image_location = None
        self.current_image_barcode = None
        self.current_image_basename = None
        self.current_image_to_annotate = None
        if starting_image_location:
            self.load_image_from_file(starting_image_location)

    def set_save_location(self, name: str):
        self.save_location = name

    def load_image_from_file(self, image_path: str):
        self.clear_current_image()
        self.current_image_location: str = image_path
        self.current_image_to_annotate: np.ndarray = open_cv2_image(self.current_image_location)
        self.current_image_barcode: str = extract_barcode_from_image_name(self.current_image_location)
        self.current_image_basename: str = os.path.basename(self.current_image_location)

    def draw_line(self, point1, point2, color=(0, 0, 0), width=1):
        cv2.line(self.current_image_to_annotate, point1, point2, color, width)

    def draw_polygon(self, points: list, color):
        for idx in range(len(points) - 1):
            self.draw_line(points[idx], points[idx + 1], color)
        self.draw_line(points[-1], points[0], color)

    def save_annotated_image_to_file(self) -> str:
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)
        return save_cv2_image(self.save_location, self.current_image_basename, self.current_image_to_annotate)

    def clear_current_image(self):
        self.current_image_location = None
        self.current_image_barcode = None
        self.current_image_to_annotate = None

    def reset_current_image(self):
        self.current_image_to_annotate = open_cv2_image(self.current_image_location)

    def cropped_copy_of_image(self, x_min: int, x_max: int, y_min: int, y_max: int) -> np.ndarray:
        """ Returns a subset of the current image, cropped to the desired absolute values. """
        return copy.deepcopy(self.current_image_to_annotate[y_min:y_max + 1, x_min:x_max + 1])

    def cropped_image_to_ratio(self, x_min: float, x_max: float, y_min: float, y_max: float) -> np.ndarray:
        """ Returns a subset of the current image, cropped to the desired ratio. """
        height = self.current_image_to_annotate.shape[0]
        width = self.current_image_to_annotate.shape[1]
        x_min = int(height * x_min)
        x_max = int(height * x_max)
        y_min = int(width * y_min)
        y_max = int(width * y_max)
        return self.cropped_copy_of_image(x_min, x_max, y_min, y_max)

    def cropped_to_box(self, list_of_four_sorted_points: list) -> np.ndarray:
        """ Returns a subset of the current image, cropped to the desired absolute values. """
        x_min = list_of_four_sorted_points[0][0]
        x_max = list_of_four_sorted_points[1][0]
        y_min = list_of_four_sorted_points[1][1]
        y_max = list_of_four_sorted_points[2][1]
        return self.cropped_copy_of_image(x_min, x_max, y_min, y_max)