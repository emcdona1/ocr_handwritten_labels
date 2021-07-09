import os
from data_loader import load_list_from_txt, open_cv2_image, save_cv2_image
import numpy as np
from typing import Union


def main(barcode_filename: str, image_folder: str):
    barcodes = load_list_from_txt(barcode_filename)
    new_image_folder = image_folder + os.path.sep + 'cropped_labels'
    height_crop = 2/3
    width_crop = 1/2
    if os.path.exists(new_image_folder):
        raise FileExistsError('The folder %s already exists.' % new_image_folder)
    else:
        os.mkdir(new_image_folder)
    for barcode in barcodes:
        image = open_cv2_image(os.path.join(image_folder, barcode + '.jpg'))
        cropped_image = crop_an_image_to_box(image, height_crop, 1, width_crop, 1)
        newest_image_save_location = save_cv2_image(new_image_folder, barcode, cropped_image)
        print('Image saved to %s' % newest_image_save_location)


def crop_an_image_to_box(image: np.ndarray, x_min: Union[int, float], x_max: Union[int, float],
                         y_min: Union[int, float], y_max: Union[int, float]) -> np.ndarray:
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

if __name__ == '__main__':
    main()