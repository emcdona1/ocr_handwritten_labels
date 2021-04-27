import sys
import os
from utilities.dataloader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from utilities.dataprocessor import convert_relative_to_absolute_coordinates
from imageprocessor.image_processor import ImageProcessor, GCVProcessor, AWSProcessor
import pandas as pd


def main(folder_or_image_path: str, generate_annotated_images=False) -> pd.DataFrame:
    list_of_images = load_file_list_from_filesystem(folder_or_image_path)
    processors = [GCVProcessor(), AWSProcessor()]
    text_comparison = pd.DataFrame(columns=['barcode', 'gcv', 'aws'])

    save_folder_path = os.path.join('test_results', 'cloud_ocr-' + get_timestamp_for_file_saving())
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)

    for one_image_location in list_of_images:
        new_row_of_ocr_texts = dict()
        for processor in processors:
            try:
                processor.load_image_from_file(one_image_location)
                new_row_of_ocr_texts['barcode'] = processor.current_image_barcode
                new_row_of_ocr_texts[processor.name] = processor.get_full_text()
                successful_ocr_query = True
            except Exception as e:
                new_row_of_ocr_texts[processor.name] = 'Error during OCR: %s' % str(e)
                successful_ocr_query = False
            if generate_annotated_images and successful_ocr_query:
                draw_comparison_image(processor, save_folder_path)

        print('OCR gathered for %s' % one_image_location)
        text_comparison = text_comparison.append(new_row_of_ocr_texts, ignore_index=True)

    save_location = save_dataframe_as_csv(save_folder_path, 'ocr_texts', text_comparison, timestamp=False)
    print('Saved to %s' % save_location)
    return text_comparison


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
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).' +\
                              'To generate annotated images, add a flag "True" or "Yes".'
    folder_or_image_file = sys.argv[1]
    generate_images_flag = False
    if len(sys.argv) == 3:
        flag_text = sys.argv[2]
        if not flag_text == 'false' or 'False':
            generate_images_flag = True
    results = main(folder_or_image_file, generate_annotated_images=generate_images_flag)
