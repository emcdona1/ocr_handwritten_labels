import os
from abc import ABC, abstractmethod
from utilities.dataloader import open_cv2_image, save_cv2_image
from utilities.dataprocessor import extract_barcode_from_image_name
import cv2


class ImageAnnotator(ABC):
    def __init__(self, starting_image_location=None):
        self.save_location = 'annotated_images'
        if not os.path.exists(self.save_location):
            os.mkdir(self.save_location)
        self.set_save_location()
        self.current_image_location = None
        self.current_image_id = None
        self.current_image_to_annotate = None
        if starting_image_location:
            self.load_image(starting_image_location)

    @abstractmethod
    def set_save_location(self) -> None:
        pass

    def load_image(self, image_path: str):
        self.current_image_location = image_path
        self.current_image_to_annotate = open_cv2_image(self.current_image_location)
        self.current_image_id = extract_barcode_from_image_name(self.current_image_location)

    @abstractmethod
    def organize_vertices(self, points_object) -> ((int, int), (int, int), (int, int), (int, int)):
        pass

    def draw_line(self, point1, point2, color=(0, 0, 0), width=1):
        cv2.line(self.current_image_to_annotate, point1, point2, color, width)

    def draw_polygon(self, points: list, color):
        for idx in range(len(points) - 1):
            self.draw_line(points[idx], points[idx + 1], color)
        self.draw_line(points[-1], points[0], color)

    def save_annotated_image_to_file(self):
        save_cv2_image(self.save_location, self.current_image_id, self.current_image_to_annotate)


class GCVImageAnnotator(ImageAnnotator):
    def set_save_location(self):
        self.save_location = self.save_location + os.path.sep + 'gcv'
        if not os.path.exists(self.save_location):
            os.mkdir(self.save_location)

    def organize_vertices(self, points_object) -> ((int, int), (int, int), (int, int), (int, int)):
        """ Given a response object with a bounding_box, returns a 4-tuple with x-y coordinates organized in the following way:
        (top_left, top_right, bottom_right, bottom_left). """
        vertices = points_object.bounding_box.vertices
        sorted_x_values = sorted([vertex.x for vertex in vertices])
        left_side = tuple([(vertex.x, vertex.y) for vertex in vertices
                           if vertex.x == sorted_x_values[0] or vertex.x == sorted_x_values[1]])
        right_side = tuple([(vertex.x, vertex.y) for vertex in vertices
                            if vertex.x == sorted_x_values[2] or vertex.x == sorted_x_values[3]])
        if left_side[0][1] > left_side[1][1]:
            left_side = (left_side[1], left_side[0])
        if right_side[0][1] > left_side[1][1]:
            right_side = (right_side[1], right_side[0])
        return left_side[0], right_side[0], right_side[1], left_side[1]


class AWSImageAnnotator(ImageAnnotator):
    def set_save_location(self):
        self.save_location = self.save_location + os.path.sep + 'aws'
        if not os.path.exists(self.save_location):
            os.mkdir(self.save_location)

    def organize_vertices(self, points_object) -> ((int, int), (int, int), (int, int), (int, int)):
        """ Given a block, returns a 4-tuple with x-y coordinates organized in the following way:
        (top_left, top_right, bottom_right, bottom_left). """
        height, width, _ = self.current_image_to_annotate.shape
        vertices = []
        for block in points_object['Geometry']['Polygon']:
            vertices.append((int(width * block['X']), int(height * block['Y'])))
        return tuple(vertices)
