import sys
import os
from utilities.dataloader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from imageprocessor.image_processor import GCVProcessor, AWSProcessor
import pandas as pd


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    processors = [GCVProcessor(), AWSProcessor()]
    folder_path = os.path.join('test_results', 'cloud_compare-' + get_timestamp_for_file_saving())
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    text_comparison = pd.DataFrame(columns=['barcode', 'gcv', 'aws'])

    for one_image_location in list_of_images:
        new_text_comparison = dict()
        for processor in processors:
            processor.load_processed_ocr_response(one_image_location)
            new_text_comparison[processor.name] = processor.get_full_text()
            new_text_comparison['barcode'] = processor.current_image_barcode

            annotator = processor.get_image_annotator()
            annotator.set_save_location(os.path.join(folder_path, processor.name))
            draw_comparison_image(processor, annotator)
            annotator.save_annotated_image_to_file()

        text_comparison = text_comparison.append(new_text_comparison, ignore_index=True)

    save_dataframe_as_csv(folder_path, 'ocr_texts', text_comparison, timestamp=False)


def draw_comparison_image(processor, annotator) -> None:
    lines = processor.get_list_of_lines()
    for line in lines:
        vertices = annotator.organize_vertices(line)
        box_color = (0, 0, 0)  # black
        annotator.draw_polygon(vertices, box_color)
    words = processor.get_list_of_words()
    for word in words:
        sorted_vertices = annotator.organize_vertices(word)
        start_color = (0, 200, 0)  # green
        end_color = (0, 0, 230)  # red
        annotator.draw_line(sorted_vertices[0], sorted_vertices[3], start_color, 2)
        annotator.draw_line(sorted_vertices[1], sorted_vertices[2], end_color, 2)


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()
