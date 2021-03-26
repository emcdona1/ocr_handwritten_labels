import os


def extract_barcode_from_image_name(image_name: str) -> str:
    image_name_without_extension = os.path.basename(image_name).split('.')[0]
    image_barcode_split = image_name_without_extension.split('_')
    if len(image_barcode_split) == 1:
        image_barcode_split = image_name_without_extension.split('-')
    return image_barcode_split[0]
