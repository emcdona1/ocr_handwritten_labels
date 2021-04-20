import os
from dataloader import load_list_from_txt, open_cv2_image, save_cv2_image
from dataprocessor import crop_an_image_to_box


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
