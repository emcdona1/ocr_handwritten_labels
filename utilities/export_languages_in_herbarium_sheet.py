import sys
import os
from pathlib import Path
import pandas as pd
from data_loader import save_dataframe_as_csv
from timer import Timer
sys.path.append(os.path.abspath('.'))
from imageprocessor.image_processor import GCVProcessor


def main(folder: Path):
    t = Timer('gather languages')
    list_of_images = [Path(folder, str(i)) for i in os.listdir(folder)]
    ip = GCVProcessor()
    results = pd.DataFrame(columns=('image_location', 'barcode',
                                    'document_language', 'document_language_by_word',
                                    'languages_found', 'languages_found_in_label'))
    for img in list_of_images:
        ip.load_image_from_file(img)
        new_row = pd.Series({'image_location': img,
                             'barcode': img.stem,
                             'document_language': ip.document_level_language,
                             'document_language_by_word': ip.main_language,
                             'languages_found': ip.languages_found,
                             'languages_found_in_label': ip.languages_found_in_label})
        results = results.append(new_row, ignore_index=True)

    t.stop()

    save_folder = Path('test_results')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_dataframe_as_csv(save_folder, 'languages_found', results, True)


if __name__ == '__main__':
    print(os.path.abspath('.'))
    assert len(sys.argv) == 2, 'Provide one folder of images to be processed.'
    image_folder = Path(sys.argv[1])
    assert image_folder.exists() and image_folder.is_dir(), f'{image_folder} is not a valid directory path.'
    main(image_folder)
