import sys
import os
from utilities.dataloader import load_file_list_from_filesystem, get_timestamp_for_file_saving
from imageprocessor.image_processor import GCVProcessor, AWSProcessor
from imageprocessor.image_annotator import ImageAnnotator
import csv


def main():
    list_of_images = load_file_list_from_filesystem(folder_or_image_file)
    gcv_processor = GCVProcessor()
    aws_processor = AWSProcessor()
    csv_filename = os.path.join('test_results', 'aws_gcv_comparison-' + get_timestamp_for_file_saving() + '.csv')
    if not os.path.exists('test_results'):
        os.mkdir('test_results')
    csv_file = open(csv_filename, 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['gcv_response', 'aws_response'])
    for one_image_location in list_of_images:
        gcv_processor.load_processed_ocr_response(one_image_location)
        gcv_annotator = gcv_processor.get_image_annotator()
        draw_comparison_images(gcv_processor, gcv_annotator)

        aws_processor.load_processed_ocr_response(one_image_location)
        aws_annotator = aws_processor.get_image_annotator()
        draw_comparison_images(aws_processor, aws_annotator)
        csv_writer.writerow([gcv_processor.get_full_text(), aws_processor.get_full_text()])
    csv_file.close()


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
