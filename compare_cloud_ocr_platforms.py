import sys
import os
from utilities.dataloader import load_file_list_from_filesystem, get_timestamp_for_file_saving, save_dataframe_as_csv
from imageprocessor.image_processor import GCVProcessor, AWSProcessor
import pandas as pd


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    gcv_processor = GCVProcessor()
    aws_processor = AWSProcessor()
    folder_path = os.path.join('test_results', 'cloud_compare-' + get_timestamp_for_file_saving())
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    text_comparison = pd.DataFrame(columns=['gcv', 'aws'])

    for one_image_location in list_of_images:
        gcv_processor.load_processed_ocr_response(one_image_location)
        gcv_annotator = gcv_processor.get_image_annotator()
        gcv_annotator.set_save_location(os.path.join(folder_path, 'gcv'))
        draw_comparison_images(gcv_processor, gcv_annotator)

        text_comparison = text_comparison.append(new_text_comparison, ignore_index=True)

    save_dataframe_as_csv(folder_path, 'comparison', text_comparison)

def draw_comparison_images(processor, annotator) -> None:
    lines = processor.get_list_of_lines()
    for line in lines:
        draw_box_around_lines(annotator, line)
    words = processor.get_list_of_words()
    for word in words:
        draw_word_start_and_end_lines(annotator, word)
    annotator.save_annotated_image_to_file()


def draw_box_around_lines(annotator: ImageAnnotator, word_box) -> None:
    vertices = annotator.organize_vertices(word_box)
    box_color = (0, 0, 0)  # black
    annotator.draw_polygon(vertices, box_color)


def draw_word_start_and_end_lines(annotator: ImageAnnotator, word_box) -> None:
    sorted_vertices = annotator.organize_vertices(word_box)
    start_color = (0, 200, 0)  # green
    end_color = (0, 0, 230)  # red
    annotator.draw_line(sorted_vertices[0], sorted_vertices[3], start_color, 2)
    annotator.draw_line(sorted_vertices[1], sorted_vertices[2], end_color, 2)


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Include one command line argument (either an image file or a directory of images).'
    folder_or_image_file = sys.argv[1]

    main()
