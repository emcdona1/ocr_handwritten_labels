import sys
import os
from utilities.dataloader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from utilities.dataprocessor import convert_relative_to_absolute_coordinates
from imageprocessor.image_processor import ImageProcessor, GCVProcessor, AWSProcessor
import pandas as pd


def main(occurrence_file: str, folder_or_image_path: str, generate_annotated_images=False) -> pd.DataFrame:
    list_of_images = load_file_list_from_filesystem(folder_or_image_path)
    processors = [GCVProcessor(), AWSProcessor()]
    occurrence = pd.read_csv(occurrence_file)

    save_folder_path = os.path.join('test_results', 'cloud_ocr-' + get_timestamp_for_file_saving())
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)

    for one_image_location in list_of_images:
        # new_row_of_ocr_texts = dict()
        for processor in processors:
            processor.load_image_from_file(one_image_location)
            index = occurrence.index[occurrence['catalogNumber'] == processor.current_image_barcode][0]
            occurrence.loc[index, processor.name + 'LabelPoints'] = str(processor.find_label_location())
            occurrence.loc[index, processor.name + 'OcrText'] = processor.get_label_text()
            if generate_annotated_images:
                draw_comparison_image(processor, save_folder_path)
        print('OCR gathered for %s' % one_image_location)

    save_location = save_dataframe_as_csv('test_results', 'occurrence_with_ocr', occurrence)
    print('Saved new occurrence file to %s' % save_location)
    return occurrence


def draw_comparison_image(processor: ImageProcessor, save_folder_path: str) -> None:
    annotator = processor.get_image_annotator()
    annotator.set_save_location(os.path.join(save_folder_path, processor.name))

    lines = processor.get_list_of_lines()
    for line in lines:
        sorted_vertices = annotator.organize_vertices(line)
        height, width, _ = annotator.current_image_to_annotate.shape
        sorted_vertices = [convert_relative_to_absolute_coordinates(pt, height, width) for pt in sorted_vertices]
        box_color = (0, 0, 0)  # black
        annotator.draw_polygon(sorted_vertices, box_color)

    words = processor.get_list_of_words()
    for word in words:
        sorted_vertices = annotator.organize_vertices(word)
        height, width, _ = annotator.current_image_to_annotate.shape
        sorted_vertices = [convert_relative_to_absolute_coordinates(pt, height, width) for pt in sorted_vertices]
        start_color = (0, 200, 0)  # green
        end_color = (0, 0, 230)  # red
        annotator.draw_line(sorted_vertices[0], sorted_vertices[3], start_color, 2)
        annotator.draw_line(sorted_vertices[1], sorted_vertices[2], end_color, 2)

    annotator.save_annotated_image_to_file()


if __name__ == '__main__':
    assert 3 <= len(sys.argv) <= 4, 'Must use 2-3 arguments: 1) either an image file or a directory of images, ' + \
                                    '2) the location of the occurrence_with_image_urls file, ' + \
                                    'And 3) optional - to generate annotated images, add a flag "True" or "Yes".'
    folder_or_image_file = sys.argv[1]
    occur = sys.argv[2]
    generate_images_flag = False
    if len(sys.argv) == 4:
        flag_text = sys.argv[3]
        if not flag_text == ('false' or 'False'):
            generate_images_flag = True
    # todo: the generate_images_flag isn't working
    results = main(occur, folder_or_image_file, generate_images_flag)