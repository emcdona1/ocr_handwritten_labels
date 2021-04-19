import sys
import prep_comparison_data
import calculate_changes


def main(occurrence_filepath: str, ocr_text_filepath: str):
    analysis = prep_comparison_data.main(occurrence_filepath, ocr_text_filepath)
    calculate_changes.main(analysis, 100, 25)


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Provide 2 arguments: filepath for 1 occurrence' + \
                              ' (can be occurrence_with_images file), ' + \
                              'and filepath for 1 CSV file with the headers "barcode", "aws", and "gcv" to compare.'
    occur_file = sys.argv[1]
    ocr_texts = sys.argv[2]
    main(occur_file, ocr_texts)
